"""Generate objdiff v2 accounting metadata; never award binary-match credit."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

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
    if local_evidence:
        verify_ref(root, ledger['checkpoint'])
        for update in ledger.get('verified_recovery_updates', []):
            verify_ref(root, update['checkpoint'])
            verify_ref(root, update['audit'])
            audit = json.loads((root / update['audit']['path']).read_text())
            assert audit['result'] == 'pass' and audit['checkpoint_sha256'] == update['checkpoint']['sha256']
        for ref in ledger['inventory']['source_exports']:
            verify_ref(root, ref)

    def measures(code, functions, complete, units, complete_units):
        return {'total_code': str(code), 'complete_code': str(complete), 'complete_code_percent': complete / code * 100 if code else 0, 'total_functions': functions, 'total_units': units, 'complete_units': complete_units, 'matched_code': '0', 'matched_data': '0', 'matched_functions': 0, 'matched_code_percent': 0, 'matched_data_percent': 0, 'matched_functions_percent': 0, 'fuzzy_match_percent': 0, 'total_data': '0', 'complete_data': '0', 'complete_data_percent': 0}

    units = []
    for complete in (True, False):
        addresses = [a for a in sorted(inventory) if (a in recovered) == complete]
        code = sum(inventory[a][0] for a in addresses)
        functions = [{'name': recovered[a]['name'] if complete else f'original_{a:08x}', 'size': str(inventory[a][0]), 'address': str(a - start), 'fuzzy_match_percent': 0, 'metadata': {'virtual_address': str(a)}} for a in addresses]
        units.append({'name': 'Verified behavioral recovery' if complete else 'Known unrecovered original functions', 'measures': measures(code, len(addresses), code if complete else 0, 1, int(complete)), 'functions': functions, 'metadata': {'complete': complete, 'auto_generated': True}})
    unassigned = total - body_bytes
    units.append({'name': 'Unassigned original .text bytes (includes padding and jump tables)', 'measures': measures(unassigned, 0, 0, 1, 0), 'sections': [{'name': '.text unassigned', 'size': str(unassigned), 'fuzzy_match_percent': 0}], 'metadata': {'complete': False, 'auto_generated': True}})
    complete_bytes = sum(r['size'] for r in recovered.values())
    return {'version': 2, 'measures': measures(total, len(inventory), complete_bytes, len(units), 1), 'units': units}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, default=ROOT / 'progress/ledger.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'progress/report.json')
    parser.add_argument('--check', action='store_true', help='Require the saved report to exactly match regeneration')
    parser.add_argument('--local-evidence', action='store_true', help='Also inspect private original and runtime evidence')
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text())
    report = generate(ledger, local_evidence=args.local_evidence)
    data = json.dumps(report, indent=2) + '\n'
    if args.check:
        assert args.output.read_text() == data, 'Saved report differs from regeneration'
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    m = report['measures']
    print(f'{len(ledger["records"])} verified addresses; {m["complete_code"]}/{m["total_code"]} original .text bytes ({m["complete_code_percent"]:.2f}%); zero verified binary matches')


if __name__ == '__main__':
    main()
