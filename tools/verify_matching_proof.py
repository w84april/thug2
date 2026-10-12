"""Validate selected native proof metadata; optionally replay private bytes."""
import hashlib
import json
import re
import struct
from pathlib import Path

POLICY = 'Apply only declared COFF DIR32/REL32 targets; compare every resulting byte.'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_ref(root, ref):
    path = (root / ref['path']).resolve()
    assert path.is_relative_to(root.resolve()) and path.is_file(), 'Missing/escaped matching reference'
    assert digest(path.read_bytes()) == ref['sha256'], 'Changed matching reference'
    return path


def verify_proof(ledger, inventory, selection, proof, manifest, root):
    assert selection['version'] == 1
    assert proof['reference_sha256'] == ledger['specimen_sha256']
    # Later engine discoveries may extend the inventory. Preserve the trial's
    # immutable digest and require every complete trial body to equal today's
    # inventory below; no byte/range difference is tolerated.
    assert proof['inventory_sha256'] == selection['trial_inventory_sha256']
    assert proof['manifest_sha256'] == selection['manifest']['sha256']
    check_ref(root, {'path': proof['source'], 'sha256': proof['source_sha256']})
    for group in ('tools_sha256', 'recovered_sources_sha256'):
        assert proof[group], 'Missing source/comparator provenance'
        for path, sha in proof[group].items():
            check_ref(root, {'path': path, 'sha256': sha})
    assert proof['relocation_policy'] == POLICY
    compiler = proof['compiler']
    assert compiler['object_record'] == {'tool_id': 96, 'build': 3077}
    assert compiler['options'] == ['/nologo', '/c', '/O2', '/Gy']
    assert set(compiler['files_sha256']) == {'cl.exe', 'c1.dll', 'c1xx.dll', 'c2.dll', 'msvcr71.dll'}
    for sha in [proof['object_sha256'], *compiler['files_sha256'].values()]:
        assert re.fullmatch('[0-9a-f]{64}', sha), 'Missing compiler/object identity'
    targets = {}
    for target in selection['data_targets']:
        assert target['symbol'] not in targets, 'Duplicate relocation target'
        source = check_ref(root, target['source'])
        values = [int(v, 16) for v in re.findall(r'0x([0-9a-fA-F]{8})u', source.read_text())]
        assert len(values) == 256 and target['size'] == 1024
        assert digest(struct.pack('<256I', *values)) == target['bytes_sha256']
        targets[target['symbol']] = target['address']
    assert targets == manifest['symbols'], 'Unverified relocation target'
    assert len(proof['functions']) == len(manifest['functions']) > 0
    recovered = {int(r['address'], 16): r for r in ledger['records']}
    seen, symbols, matches = set(), set(), {}
    for f, declared in zip(proof['functions'], manifest['functions']):
        assert {k: f[k] for k in ('symbol', 'address', 'size')} == declared
        address, size = int(f['address'], 16), f['size']
        assert address not in seen and f['symbol'] not in symbols, 'Duplicate native claim'
        seen.add(address); symbols.add(f['symbol'])
        assert inventory.get(address) == (size, [(address, address + size - 1)]), 'Native claim must cover complete original body'
        assert type(f['compiled_size']) is int and f['compiled_size'] > 0
        for key in ('reference_sha256', 'raw_object_sha256', 'relocated_sha256'):
            assert re.fullmatch('[0-9a-f]{64}', f[key])
        raw_equal = f['compiled_size'] == size and f['raw_object_sha256'] == f['reference_sha256']
        equal = f['compiled_size'] == size and f['relocated_sha256'] == f['reference_sha256']
        assert type(f['raw_object_equal']) is bool and f['raw_object_equal'] == raw_equal
        assert type(f['relocated_equal']) is bool and f['relocated_equal'] == equal
        assert f['credited_bytes'] == (size if equal else 0), 'Unequal body credited'
        if equal:
            assert f['first_difference'] is None
            assert address in recovered and recovered[address]['size'] == size, 'Match lacks behavioral completion evidence'
            matches[address] = f
        else:
            assert type(f['first_difference']) is int and 0 <= f['first_difference'] <= min(size, f['compiled_size'])
        occupied = set()
        for relocation in f['relocations']:
            offset = relocation['offset']
            assert relocation['type'] in ('DIR32', 'REL32')
            assert relocation['target'] == targets[relocation['symbol']]
            assert type(offset) is int and 0 <= offset <= f['compiled_size'] - 4
            span = set(range(offset, offset + 4))
            assert not occupied & span, 'Overlapping relocations'
            occupied.update(span)
            assert type(relocation['addend']) is int and 0 <= relocation['addend'] <= 0xffffffff
        if not f['relocations']:
            assert f['raw_object_sha256'] == f['relocated_sha256']
    accepted = selection['accepted_addresses']
    assert len(accepted) == len(set(accepted)) and set(accepted) == {f['address'] for f in matches.values()}, 'Selected matches differ from proof'
    assert proof['credited_bytes'] == sum(f['size'] for f in matches.values())
    assert proof['raw_equal_bytes'] == sum(f['size'] for f in proof['functions'] if f['raw_object_equal'])
    return matches


def verified_matches(ledger, inventory, root, local_evidence=False):
    path = root / 'matching/selection.json'
    assert path.is_file(), 'Missing native matching selection'
    selection = json.loads(path.read_text())
    proof = json.loads(check_ref(root, selection['proof']).read_text())
    manifest = json.loads(check_ref(root, selection['manifest']).read_text())
    matches = verify_proof(ledger, inventory, selection, proof, manifest, root)
    if local_evidence:
        review = json.loads(check_ref(root, selection['local_review']).read_text())
        assert review['result'] == 'pass' and review['full_comparator_replay']
        assert review['public_proof_sha256'] == selection['proof']['sha256']
        assert review['real_opcode_and_target_corruptions_rejected'] and review['shortened_and_duplicate_claims_rejected']
        from native_match import compare
        actual = compare(root / 'local/discs/cd3/Crack/THUG2.exe', Path(review['private_object']), manifest)
        assert actual['inventory_sha256'] == ledger['inventory']['sha256']
        assert all(proof[key] == value for key, value in actual.items() if key != 'inventory_sha256'), 'Private matching replay differs'
    return matches
