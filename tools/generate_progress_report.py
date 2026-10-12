"""Generate objdiff matching/link fields and a separate scoped behavioral record."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from verify_matching_proof import verified_matches

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_ref(root, ref):
    path = (root / ref['path']).resolve()
    assert path.is_relative_to(root.resolve()), 'Reference escapes the repository'
    assert path.is_file() and sha(path) == ref['sha256'], f'Changed/missing evidence: {ref["path"]}'


def generate(ledger, root=ROOT, local_evidence=False):
    assert ledger['version'] == 1
    verify_ref(root, ledger['inventory'])
    section = ledger['code_section']
    start, total = section['address'], section['virtual_size']
    assert start > 0 and total > 0
    inventory = {}
    all_ranges = []
    for row in csv.DictReader((root / ledger['inventory']['path']).open(), delimiter='\t'):
        address = int(row['address'], 16)
        assert address not in inventory, 'Duplicate function address'
        size = int(row['body_bytes'])
        ranges = [tuple(int(x, 16) for x in pair.split(':')) for pair in row['ranges'].split(';')]
        assert size > 0 and size == sum(end - begin + 1 for begin, end in ranges)
        assert any(begin <= address <= end for begin, end in ranges), 'Entry outside function body'
        for begin, end in ranges:
            assert start <= begin <= end < start + total, 'Body outside original code section'
            all_ranges.append((begin, end))
        inventory[address] = (size, ranges)
    last = start - 1
    for begin, end in sorted(all_ranges):
        assert begin > last, 'Overlapping function bodies would count bytes twice'
        last = end
    body_bytes = sum(size for size, _ in inventory.values())
    assert len(inventory) == ledger['inventory']['functions']
    assert body_bytes == ledger['inventory']['body_bytes'] <= total
    recovered = {}
    partials = {int(a, 16) for a in ledger['partial_addresses']}
    resolutions = {int(row['address'], 16): row for row in ledger.get('resolved_partials', [])}
    assert len(resolutions) == len(ledger.get('resolved_partials', [])), 'Duplicate partial resolution'
    historical = {int(a, 16) for a in ledger.get('historical_partial_addresses', ledger['partial_addresses'])}
    assert historical == partials | resolutions.keys() and not partials & resolutions.keys(), 'Missing/invalid partial resolution'
    for row in ledger['records']:
        address = int(row['address'], 16)
        assert address not in recovered, 'Duplicate recovered address'
        assert address not in partials, 'Incomplete routine receives completion credit'
        assert address in inventory and (row['size'], [tuple(x) for x in row['ranges']]) == inventory[address], 'Incorrect original function size/ranges'
        assert row['original']['value'] > 0 and row['original']['field'], 'No original execution evidence'
        assert row['name'] in row['aliases']
        assert row.get('browser', {}).get('result') == 'pass' or 'Native recovered-C comparison' in row.get('runtime', ''), 'No verified runtime'
        verify_ref(root, row['source'])
        assert 0 < row['source']['line'] <= len((root / row['source']['path']).read_text().splitlines())
        if local_evidence:
            for field in ('original', 'original_checkpoint', 'fixture', 'browser', 'node', 'mapping_harness'):
                if field in row:
                    verify_ref(root, row[field])
            report = json.loads((root / row['original']['path']).read_text())
            assert report['specimen_sha256'] == ledger['specimen_sha256']
            if 'original_checkpoint' in row:
                parent = json.loads((root / row['original_checkpoint']['path']).read_text())
                assert hex(address) in parent['original_addresses']
                assert parent['specimen_sha256'] == ledger['specimen_sha256']
                assert parent['result'] == 'original comparisons, Node and actual Chromium pass; unpromoted'
            else:
                assert report['result'].startswith(('pass', 'original pass'))
            value = report
            for part in row['original']['field'].split('/'):
                value = value[part]
            assert value == row['original']['value']
            if 'browser' in row:
                browser = json.loads((root / row['browser']['path']).read_text())
                suites = browser.get('observed', {}).get('suites', browser)
                summary = browser if row['browser']['suite'] == 'collision' else suites[row['browser']['suite']]
                assert summary['result'] == 'pass'
        recovered[address] = row
    for address, resolution in resolutions.items():
        assert address in recovered, 'Resolved partial lacks completed routine evidence'
        proof = resolution['verification']
        assert proof['completed_calls'] > 0 and proof['expected_traps'] == 0
        assert proof['returned_this'] and proof['temporary_cleanup_verified'], 'Incomplete constructor resolution'
        assert any(resolution['checkpoint'] == u['checkpoint'] and resolution['audit'] == u['audit']
                   for u in ledger['verified_recovery_updates']), 'Unaudited partial resolution'
        if local_evidence:
            verify_ref(root, resolution['checkpoint'])
            verify_ref(root, resolution['audit'])
            parent = json.loads((root / resolution['checkpoint']['path']).read_text())
            audit = json.loads((root / resolution['audit']['path']).read_text())
            assert proof == parent['partial_resolutions'][hex(address)]
            assert hex(address) in audit['resolved_partial_addresses']
            row = recovered[address]
            original = json.loads((root / row['original']['path']).read_text())['complete_constructor']
            fixture = json.loads((root / row['fixture']['path']).read_text())
            steps = [s for c in fixture['cases'] for s in c['steps'] if int(s['fn'], 16) == address]
            assert len(steps) == original['returned_calls'] == proof['completed_calls']
            assert all(not s.get('expected_trap') and s['result'] == s['this'] for s in steps)
            assert all(r['returned_this'] and r['temporary_scope_restored'] and r['texture_copies_equal'] for r in original['records'])
    if local_evidence:
        verify_ref(root, ledger['checkpoint'])
        for update in ledger.get('verified_recovery_updates', []):
            verify_ref(root, update['checkpoint'])
            verify_ref(root, update['audit'])
            audit = json.loads((root / update['audit']['path']).read_text())
            assert audit['result'] == 'pass' and audit['checkpoint_sha256'] == update['checkpoint']['sha256']
        for ref in ledger['inventory']['source_exports']:
            verify_ref(root, ref)

    matched = verified_matches(ledger, inventory, root, local_evidence)

    def measures(code, functions, complete, units, complete_units, matched_code=0, matched_functions=0):
        percent = matched_code / code * 100 if code else 0
        return {'total_code': str(code), 'complete_code': str(complete), 'complete_code_percent': complete / code * 100 if code else 0, 'total_functions': functions, 'total_units': units, 'complete_units': complete_units, 'matched_code': str(matched_code), 'matched_data': '0', 'matched_functions': matched_functions, 'matched_code_percent': percent, 'matched_data_percent': 0, 'matched_functions_percent': matched_functions / functions * 100 if functions else 0, 'fuzzy_match_percent': percent, 'total_data': '0', 'complete_data': '0', 'complete_data_percent': 0}

    units = []
    for behavioral in (True, False):
        addresses = [a for a in sorted(inventory) if (a in recovered) == behavioral]
        code = sum(inventory[a][0] for a in addresses)
        functions = [{'name': recovered[a]['name'] if behavioral else f'original_{a:08x}', 'size': str(inventory[a][0]), 'address': str(a - start), 'fuzzy_match_percent': 100 if a in matched else 0, 'metadata': {'virtual_address': str(a)}} for a in addresses]
        matches = [a for a in addresses if a in matched]
        # Synthetic address groups are not proven original-target linked units.
        # Exact individual object matches do not establish that link evidence.
        units.append({'name': 'Scoped behavioral recovery (original-target link unverified)' if behavioral else 'Known unrecovered original functions', 'measures': measures(code, len(addresses), 0, 1, 0, sum(inventory[a][0] for a in matches), len(matches)), 'functions': functions, 'metadata': {'complete': False, 'auto_generated': True}})
    unassigned = total - body_bytes
    units.append({'name': 'Unassigned original .text bytes (includes padding and jump tables)', 'measures': measures(unassigned, 0, 0, 1, 0), 'sections': [{'name': '.text unassigned', 'size': str(unassigned), 'fuzzy_match_percent': 0}], 'metadata': {'complete': False, 'auto_generated': True}})
    return {'version': 2, 'measures': measures(total, len(inventory), 0, len(units), 0, sum(f['size'] for f in matched.values()), len(matched)), 'units': units}


def behavioral_summary(ledger, report, ledger_path=ROOT / 'progress/ledger.json'):
    """Keep behavioral coverage outside objdiff's original-target linked fields."""
    m = report['measures']
    assert int(m['complete_code']) == m['complete_units'] == 0
    verified_bytes = sum(row['size'] for row in ledger['records'])
    total = ledger['code_section']['virtual_size']
    return {'version': 1, 'metric': 'Scoped behavioral recovery of original function bodies',
            'specimen_sha256': ledger['specimen_sha256'], 'ledger_sha256': sha(ledger_path),
            'verified_addresses': len(ledger['records']), 'verified_function_body_bytes': verified_bytes,
            'original_text_virtual_bytes': total, 'verified_body_percent': verified_bytes / total * 100,
            'known_inventory_functions': ledger['inventory']['functions'],
            'known_function_body_bytes': ledger['inventory']['body_bytes'],
            'unassigned_text_bytes': total - ledger['inventory']['body_bytes'],
            'native_matching': {'functions': m['matched_functions'], 'bytes': int(m['matched_code']), 'percent': m['matched_code_percent']},
            'original_target_link': {'verified_code_bytes': 0, 'verified_units': 0, 'status': 'unverified', 'evidence': []},
            'scope': 'Complete routine implementations under their recorded behavioral test scopes; not exhaustive equivalence, original-target build/link completion, asset completion or playability.',
            'playable': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, default=ROOT / 'progress/ledger.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'progress/report.json')
    parser.add_argument('--behavioral-output', type=Path, default=ROOT / 'progress/behavioral-recovery.json')
    parser.add_argument('--check', action='store_true', help='Require the saved report to exactly match regeneration')
    parser.add_argument('--local-evidence', action='store_true', help='Also inspect private original and runtime evidence')
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    report = generate(ledger, local_evidence=args.local_evidence)
    data = json.dumps(report, indent=2) + '\n'
    behavioral = behavioral_summary(ledger, report, args.ledger)
    behavioral_data = json.dumps(behavioral, indent=2) + '\n'
    if args.check:
        assert args.output.read_text() == data, 'Saved report differs from regeneration'
        assert args.behavioral_output.read_text() == behavioral_data, 'Saved behavioral record differs from regeneration'
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
        args.behavioral_output.parent.mkdir(parents=True, exist_ok=True)
        args.behavioral_output.write_text(behavioral_data)
    m = report['measures']
    print(f'{behavioral["verified_addresses"]} behaviorally verified addresses; {behavioral["verified_function_body_bytes"]}/{m["total_code"]} original .text bytes ({behavioral["verified_body_percent"]:.2f}%); {m["complete_code"]} verified original-target linked bytes; {m["matched_code"]} verified native matching bytes ({m["matched_code_percent"]:.5f}%)')


if __name__ == '__main__':
    main()
