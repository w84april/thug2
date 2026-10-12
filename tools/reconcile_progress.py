"""Reconcile private behavioral evidence into a public, address-deduplicated ledger.

Requires the preserved discovery index and original comparisons. Never executes
the specimen, rewrites checkpoints, or publishes fixture contents.
"""
import collections
import csv
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'local/analysis'


def read(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def fixture_functions(path):
    # Fixtures can be hundreds of MB. Only read their leading function map.
    with (ROOT / path).open() as stream:
        data = ''
        while len(data) < 4_000_000:
            chunk = stream.read(65536)
            if not chunk:
                break
            data += chunk
            match = re.search(r'"functions"\s*:', data)
            if match:
                try:
                    return json.JSONDecoder().raw_decode(data[match.end():].lstrip())[0]
                except json.JSONDecodeError:
                    pass
    return {}


def observations(report, name, address):
    """Only positive original execution observations, with their exact field."""
    for field, values in report.items():
        if not isinstance(values, dict):
            continue
        if field == 'counts' or field.endswith('_counts'):
            value = values.get(name, 0)
            if type(value) is int and value > 0:
                yield f'{field}/{name}', value
        if field == 'callee_coverage' or field.endswith('_callee_coverage'):
            for key, value in values.items():
                if key.startswith('0x') and int(key, 16) == address and type(value) is int and value > 0:
                    yield f'{field}/{key}', value
        if field == 'instruction_coverage':
            for key, value in values.items():
                if key.startswith('0x') and int(key, 16) == address and isinstance(value, dict) and value.get('covered', 0) > 0:
                    yield f'{field}/{key}/covered', value['covered']


def main():
    checkpoint_path = 'local/analysis/walk-component-checkpoint.json'
    checkpoint = read(checkpoint_path)
    specimen = (ROOT / 'local/discs/cd3/Crack/THUG2.exe').read_bytes()
    assert hashlib.sha256(specimen).hexdigest() == checkpoint['specimen_sha256']
    pe = struct.unpack_from('<I', specimen, 0x3c)[0]
    assert specimen[pe:pe + 4] == b'PE\0\0'
    section_count = struct.unpack_from('<H', specimen, pe + 6)[0]
    optional_size = struct.unpack_from('<H', specimen, pe + 20)[0]
    image_base = struct.unpack_from('<I', specimen, pe + 24 + 28)[0]
    executable_sections = []
    for i in range(section_count):
        at = pe + 24 + optional_size + i * 40
        if struct.unpack_from('<I', specimen, at + 36)[0] & 0x20000000:
            size, rva = struct.unpack_from('<II', specimen, at + 8)
            executable_sections.append((specimen[at:at + 8].rstrip(b'\0').decode(), image_base + rva, size))
    assert executable_sections == [('.text', 0x401000, 2375378)], 'Review code denominator for a different specimen'
    discovery = read('local/analysis/recovery-ledger-discovery.json')
    experimental_path = 'local/analysis/walk-component-browser.json'
    maintained_path = 'local/validation/collision-browser.json'
    experimental = read(experimental_path)['observed']['suites']
    maintained = read(maintained_path)
    sources = discovery['sources']
    pinned = {**checkpoint['artifact_hashes'], **checkpoint['source_hashes'], **checkpoint['harness_hashes']}
    pinned[checkpoint_path] = digest(checkpoint_path)
    assert digest(maintained_path) == pinned[maintained_path]
    for path, value in maintained['artifact_hashes'].items():
        assert path not in pinned or pinned[path] == value
        pinned[path] = value
    for suite, value in maintained['oracle_reports'].items():
        path = f'local/validation/{suite.replace("_", "-")}.json'
        assert path not in pinned or pinned[path] == value['report_sha256']
        pinned[path] = value['report_sha256']
    # The native-only early reports predate the browser checkpoint. Accept their
    # preserved source identity, then pin their metadata for this reconciliation.
    for suite in ('checksums', 'bounds', 'lzss'):
        path = f'local/validation/{suite}.json'
        report = read(path)
        assert report['result'] == 'pass' and report['specimen_sha256'] == checkpoint['specimen_sha256']
        for source_path, value in report['source_hashes'].items():
            assert value == checkpoint['source_hashes'][source_path] == digest(source_path)
        pinned[path] = digest(path)
    checked = set()

    def pin(path):
        if path not in checked:
            assert path in pinned, f'Unpinned evidence: {path}'
            assert digest(path) == pinned[path], f'Changed pinned evidence: {path}'
            checked.add(path)
        return {'path': path, 'sha256': pinned[path]}

    inventory = {}
    range_paths = ['local/analysis/progress-function-ranges.tsv', 'local/analysis/progress-extra-ranges-complete.tsv']
    if (LOCAL / 'progress-reconciled-extra-ranges.tsv').exists():
        range_paths.append('local/analysis/progress-reconciled-extra-ranges.tsv')
    for path in range_paths:
        for row in csv.DictReader((ROOT / path).open(), delimiter='\t'):
            address = int(row['address'], 16)
            assert address not in inventory, f'Duplicate inventory entry: {address:x}'
            ranges = [tuple(int(x, 16) for x in pair.split(':')) for pair in row['ranges'].split(';')]
            size = int(row['body_bytes'])
            assert size == sum(end - start + 1 for start, end in ranges)
            inventory[address] = {'address': f'0x{address:08x}', 'size': size, 'ranges': ranges}

    candidates = collections.defaultdict(list)
    for key, rows in discovery['records'].items():
        candidates[int(key, 16)].extend(rows)

    # Aggregate decal suites use several fixture maps, rather than one named
    # after the suite. The original exporter missed all of these maps.
    for suite, fixtures in {
        'decal_prerequisites': ['decal-storage', 'decal-grid', 'decal-geometry', 'decal-lifetime', 'decal-lighting'],
        'decal_resources': ['decal-math', 'decal-resources'],
        'decal_projection': ['mesh-lifecycle', 'decal-projection'],
    }.items():
        for fixture in fixtures:
            path = f'local/validation/collision/{fixture}-fixtures.json'
            for key, function in fixture_functions(path).items():
                name = function['name']
                if name in sources and maintained[suite].get('counts', {}).get(name, 0) > 0:
                    candidates[int(key, 16)].append({'name': name, 'source': sources[name], 'suite': suite, 'group': 'maintained', 'fixture': path})

    # Checkpoint claims reached indirectly, absent from direct-export counters.
    for address, name, suite in (
        (0x43d5c0, 'thug_vibration_bind_device_draft', 'input_lifecycle'),
        (0x45e450, 'thug_composite_checksum_draft', 'prop_command'),
        (0x4608f0, 'thug_object_checksum_draft', 'prop_command'),
        (0x4c6270, 'thug_model_scene_finalize_draft', 'scene_finalize'),
    ):
        assert discovery['claims'][hex(address)]
        candidates[address].append({'name': name, 'source': sources[name], 'suite': suite, 'group': 'experimental', 'fixture': f'local/analysis/{suite.replace("_", "-")}-fixtures.json'})

    # Maintained indirect helpers: explicit leading address comments plus actual
    # original callee observations. Names without an unambiguous address stay out.
    all_names = {r['name'] for rows in candidates.values() for r in rows}
    for name, source in sources.items():
        if name in all_names or not source['path'].startswith('src/') or '/platform/' in source['path'] or source['path'].endswith('.h'):
            continue
        text = (ROOT / source['path']).read_text()
        pattern = r'/\*\s*(?:0x)?(00[4-6][0-9a-f]{5})\b[^*]*(?:\*(?!/)[^*]*)*\*/\s*[^;{}]*\b' + re.escape(name) + r'\s*\('
        match = re.search(pattern, text)
        if not match:
            continue
        address = int(match[1], 16)
        for suite, summary in maintained.items():
            if not isinstance(summary, dict) or summary.get('result') != 'pass':
                continue
            original_path = f'local/validation/{suite.replace("_", "-")}.json'
            if not (ROOT / original_path).exists():
                continue
            report = read(original_path)
            if list(observations(report, name, address)):
                candidates[address].append({'name': name, 'source': source, 'suite': suite, 'group': 'maintained'})

    # These two older suites record aggregate counts instead of per-export names.
    for address, name, suite, field in (
        (0x45f270, 'thug_component_register_factory', 'factory_registration', 'instruction_coverage/covered'),
        (0x46fbd0, 'thug_script_random_value', 'script_ranges', 'cases'),
    ):
        row = candidates[address][0]
        assert row['name'] == name and row['suite'] == suite
        row['reviewed_observation'] = field
        row['mapping_harness'] = f'tools/verify_{suite}.py'

    # Earlier direct comparison mappings, reviewed against the original harness.
    # Checksums, bounds and decoding use native comparisons; no browser claim.
    early = [
        (0x401aa0, 'thug_crc32_buffer', 'checksums', 'comparisons/buffer'),
        (0x401af0, 'thug_crc32_extend_buffer', 'checksums', 'comparisons/extend_buffer'),
        (0x401b30, 'thug_crc32_normalized_buffer', 'checksums', 'comparisons/normalized_buffer'),
        (0x401b90, 'thug_crc32_string', 'checksums', 'comparisons/string'),
        (0x401be0, 'thug_crc32_extend_string', 'checksums', 'comparisons/extend_string'),
        (0x4033e0, 'thug_bounds_reset', 'bounds', 'counts/reset'),
        (0x403450, 'thug_bounds_expand', 'bounds', 'counts/expand'),
        (0x4034d0, 'thug_bounds_count_containing_axes', 'bounds', 'counts/count_containing_axes'),
        (0x4014f0, 'thug_lzss_decode_unchecked', 'lzss', 'counts/oracle_comparisons'),
        (0x40b230, 'thug_collision_vertex', 'geometry', 'counts/vertex'),
        (0x414d80, 'thug_collision_face_normal', 'geometry', 'counts/face_normal'),
        (0x40b420, 'thug_collision_triangle', 'triangles', 'count'),
        (0x49cbb0, 'thug_collision_load', 'loading', 'counts/files'),
        (0x4169c0, 'thug_collision_bind', 'collision', 'counts/object_relocations'),
        (0x416320, 'thug_collision_query', 'collision', 'counts/queries'),
        (0x48c980, 'thug_collision_select_scenes', 'scene', 'counts/scenes'),
        (0x4188c0, 'thug_collision_grid_query', 'scene', 'counts/grid'),
        (0x4106c0, 'thug_collision_scene_segment', 'scene', 'counts/scene'),
        (0x410930, 'thug_collision_scene_segment_farthest', 'scene', 'counts/farthest'),
        (0x4172f0, 'thug_collision_probe_query', 'probes', 'counts/probe'),
    ]
    for address, name, suite, field in early:
        source = sources[name]
        harness = 'tools/verify_' + ('collision' if suite == 'collision' else suite) + '.py'
        assert f'0x{address:08x}' in (ROOT / source['path']).read_text(), name
        assert re.search(r'0x0*' + f'{address:x}' + r'\b', (ROOT / harness).read_text()), name
        candidates[address].append({'name': name, 'source': source, 'suite': suite, 'group': 'maintained', 'reviewed_observation': field, 'mapping_harness': harness, 'native_only': suite in ('checksums', 'bounds', 'lzss')})

    accepted = []
    excluded = []
    reports = {}
    partials = {int(a, 16) for a in checkpoint['partial_original_addresses']}
    missing = sorted(set(candidates) - set(inventory) - partials)
    if missing:
        (LOCAL / 'progress-reconciliation-extra-entries.txt').write_text(''.join(f'{address:08x}\n' for address in missing))
        raise AssertionError(f'Missing function extents: {[hex(address) for address in missing]}')
    for address, rows in sorted(candidates.items()):
        if address in partials:
            excluded.append({'address': f'0x{address:08x}', 'reason': 'Incomplete routine in current checkpoint'})
            continue
        assert address in inventory, f'Missing function extent: {address:x}'
        evidence = []
        for row in rows:
            name, source, suite = row['name'], row['source'], row['suite']
            if name.endswith('_prefix_draft') and address != 0x512cc0:
                continue
            # The Gap dispatcher retained its old name after all routes passed.
            if address == 0x512cc0:
                complete = read('local/analysis/gap-end-checkpoint.json')['partial_command_dispatch']
                assert complete['counted_as_complete'] and not complete['incomplete_routes']
            original_path = f'local/validation/{suite.replace("_", "-")}.json' if row['group'] == 'maintained' else f'local/analysis/{suite.replace("_", "-")}-original.json'
            if original_path not in reports:
                reports[original_path] = read(original_path)
            report = reports[original_path]
            assert report['specimen_sha256'] == checkpoint['specimen_sha256']
            original_checkpoint = None
            if address == 0x526e00 and suite == 'walk_air_wallplant' and 'result' not in report:
                # This preserved oracle predates a result field. Its complete
                # routine claim and passing replays are recorded in the pinned
                # enclosing checkpoint, rather than invented from the counters.
                path = 'local/analysis/walk-air-transitions-checkpoint.json'
                parent = read(path)
                assert hex(address) in parent['original_addresses']
                assert parent['result'] == 'original comparisons, Node and actual Chromium pass; unpromoted'
                assert parent['specimen_sha256'] == checkpoint['specimen_sha256']
                original_checkpoint = pin(path)
            # Earlier integration reports sometimes stop at an unfinished parent.
            # Prefer a separate passing complete-routine comparison for credit.
            if not original_checkpoint and not report.get('result', '').startswith(('pass', 'original pass')):
                continue
            observed = list(observations(report, name, address))
            if row.get('reviewed_observation'):
                value = report
                for part in row['reviewed_observation'].split('/'):
                    value = value[part]
                assert type(value) is int and value > 0
                observed.append((row['reviewed_observation'], value))
            if not observed:
                continue
            pin(source['path'])
            assert source['sha256'] == pinned[source['path']]
            # Macro-produced definitions retain the macro invocation's source
            # line. The preserved preprocessor index supplies their full name.
            assert source['line'] > 0 and source['line'] <= len((ROOT / source['path']).read_text().splitlines()), name
            proof = {'original': {**pin(original_path), 'field': observed[0][0], 'value': observed[0][1]}, 'scope': report.get('scope', '')}
            if original_checkpoint:
                proof['original_checkpoint'] = original_checkpoint
                proof['scope'] = parent['scope']
            if row.get('native_only'):
                proof['runtime'] = 'Native recovered-C comparison; no browser validation claimed'
            else:
                browser_path = maintained_path if row['group'] == 'maintained' else experimental_path
                summary = maintained if suite == 'collision' else (maintained if row['group'] == 'maintained' else experimental)[suite]
                assert summary['result'] == 'pass'
                proof['browser'] = {**pin(browser_path), 'suite': suite, 'result': 'pass'}
                # Original comparison reports include the Node replay, or that
                # replay is separately preserved in the checkpoint result set.
                node_paths = [f'local/validation/{suite.replace("_", "-")}-wasm.json'] if row['group'] == 'maintained' else [f'local/analysis/walk-component-checkpoint-{suite.replace("_", "-")}-result.json', f'local/analysis/{suite.replace("_", "-")}-unit.json']
                for path in node_paths:
                    if path in pinned:
                        node = read(path)
                        assert node['result'] == 'pass', path
                        proof['node'] = pin(path)
                        break
                if 'fixture' in row:
                    proof['fixture'] = pin(row['fixture'])
            if row.get('mapping_harness'):
                proof['mapping_harness'] = pin(row['mapping_harness'])
            evidence.append({'name': name, 'source': source, **proof})
        if not evidence:
            excluded.append({'address': f'0x{address:08x}', 'names': sorted({r['name'] for r in rows}), 'reason': 'No linked positive original execution observation'})
            continue
        # Prefer maintained source and one strongest proof; aliases are recorded
        # separately and never add another function or another copy of its bytes.
        evidence.sort(key=lambda r: (not r['source']['path'].startswith('src/'), 'node' not in r, r['source']['path'], r['name']))
        entry = {**inventory[address], **evidence[0], 'aliases': sorted({r['name'] for r in evidence}), 'checkpoint_claims': discovery['claims'].get(hex(address), [])}
        sizes = sorted({m['bytes'] for m in discovery['routines'].get(hex(address), []) if 'bytes' in m})
        if sizes and entry['size'] not in sizes:
            entry['linear_extent_bytes'] = sizes
            entry['size_note'] = 'Ghidra body union excludes gaps/alignment within the separately verified linear extent; body bytes only receive credit.'
            assert max(sizes) >= entry['size']
        accepted.append(entry)

    all_ranges = sorted((start, end, address) for address, row in inventory.items() for start, end in row['ranges'])
    last_end = 0
    for start, end, address in all_ranges:
        assert 0x401000 <= start <= end < 0x401000 + 2375378
        assert start > last_end, f'Overlapping original bodies at {address:x}'
        last_end = end
    output = ROOT / 'progress'
    output.mkdir(exist_ok=True)
    inventory_path = output / 'function-inventory.tsv'
    with inventory_path.open('w') as stream:
        stream.write('address\tbody_bytes\tranges\n')
        for address, row in sorted(inventory.items()):
            stream.write(f'{address:08x}\t{row["size"]}\t' + ';'.join(f'{start:08x}:{end:08x}' for start, end in row['ranges']) + '\n')
    ledger = {'version': 1, 'specimen_sha256': checkpoint['specimen_sha256'], 'specimen_provenance': 'User-supplied modified/unpacked PC build; not pristine retail', 'checkpoint': pin(checkpoint_path), 'inventory': {'path': 'progress/function-inventory.tsv', 'sha256': digest('progress/function-inventory.tsv'), 'functions': len(inventory), 'body_bytes': sum(r['size'] for r in inventory.values()), 'source_exports': [{'path': path, 'sha256': digest(path)} for path in range_paths]}, 'code_section': {'name': '.text', 'address': 0x401000, 'virtual_size': 2375378, 'denominator_policy': 'All original .text virtual bytes, including unidentified code, jump tables and padding; excludes raw file alignment. No data or asset completion claimed.'}, 'partial_addresses': checkpoint['partial_original_addresses'], 'records': accepted, 'excluded': excluded, 'limitations': ['Scoped behavioral verification, not exhaustive equivalence or binary matching.', 'Original game, private fixtures and Wasm are required to replay the local comparisons; CI validates metadata only.', 'Historical separate physics experiment is not in this active-build ledger; no credit without reconciliation.']}
    accepted_names = {name for row in accepted for name in row['aliases']}
    ledger['uncredited_source_definitions'] = [
        {'name': name, 'source': source, 'reason': 'No accepted one-to-one original address and full-routine behavioral proof; includes adapters, partial entries and untested helpers'}
        for name, source in sorted(sources.items()) if name not in accepted_names
    ]
    ledger['reconciliation'] = {
        'provisional_addresses': len(discovery['records']),
        'accepted_addresses': len(accepted),
        'uncredited_source_definitions': len(ledger['uncredited_source_definitions']),
        'duplicate_alias_addresses': sum(len(row['aliases']) > 1 for row in accepted),
        'linear_extent_differences': sum('linear_extent_bytes' in row for row in accepted),
        'historical_routine_estimate': {'numerator': 2026, 'denominator': 11637, 'used_for_report': False},
        'new_behavioral_recovery': False,
    }
    (output / 'ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
    print(json.dumps({'accepted_functions': len(accepted), 'complete_body_bytes': sum(r['size'] for r in accepted), 'known_functions': len(inventory), 'unassigned_text_bytes': ledger['code_section']['virtual_size'] - ledger['inventory']['body_bytes'], 'excluded': excluded}, indent=2))


if __name__ == '__main__':
    main()
