"""Small corruption controls for the public report generator."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from generate_progress_report import ROOT, generate
from verify_matching_proof import verify_proof


def main():
    ledger = json.loads((ROOT / 'progress/ledger.json').read_text())
    report = generate(ledger)
    m = report['measures']
    assert int(m['complete_code']) == sum(r['size'] for r in ledger['records'])
    assert int(m['total_code']) == ledger['code_section']['virtual_size']
    selection = json.loads((ROOT / 'matching/selection.json').read_text())
    proof = json.loads((ROOT / selection['proof']['path']).read_text())
    manifest = json.loads((ROOT / selection['manifest']['path']).read_text())
    assert int(m['matched_code']) == proof['credited_bytes'] and m['matched_functions'] == len(selection['accepted_addresses'])
    bad_ledgers = []
    duplicate = copy.deepcopy(ledger)
    duplicate['records'].append(copy.deepcopy(duplicate['records'][0]))
    bad_ledgers.append(duplicate)
    size = copy.deepcopy(ledger)
    size['records'][0]['size'] += 1
    bad_ledgers.append(size)
    partial = copy.deepcopy(ledger)
    partial['partial_addresses'].append(partial['records'][0]['address'])
    bad_ledgers.append(partial)
    evidence = copy.deepcopy(ledger)
    evidence['records'][0]['original']['value'] = 0
    bad_ledgers.append(evidence)
    changed = copy.deepcopy(ledger)
    changed['records'][0]['source']['sha256'] = '0' * 64
    bad_ledgers.append(changed)
    if ledger.get('resolved_partials'):
        missing_resolution = copy.deepcopy(ledger)
        missing_resolution['resolved_partials'] = []
        bad_ledgers.append(missing_resolution)
        no_return = copy.deepcopy(ledger)
        no_return['resolved_partials'][0]['verification']['returned_this'] = False
        bad_ledgers.append(no_return)
        no_calls = copy.deepcopy(ledger)
        no_calls['resolved_partials'][0]['verification']['completed_calls'] = 0
        bad_ledgers.append(no_calls)
    for bad in bad_ledgers:
        try:
            generate(bad)
        except AssertionError:
            continue
        raise AssertionError('Corrupt ledger was accepted')
    print(f'Report arithmetic and {len(bad_ledgers)} corruption controls pass')
    inventory = {int(r['address'], 16): (r['size'], [tuple(x) for x in r['ranges']]) for r in ledger['records']}
    bad_proofs = []
    for change in ('duplicate', 'short', 'hash', 'raw_hash', 'unequal', 'wrong_target', 'overlap', 'source', 'total', 'specimen', 'inventory', 'compiler'):
        bad = copy.deepcopy(proof)
        if change == 'duplicate': bad['functions'][1] = copy.deepcopy(bad['functions'][0])
        elif change == 'short': bad['functions'][0]['size'] -= 1
        elif change == 'hash': bad['functions'][0]['relocated_sha256'] = '0' * 64
        elif change == 'raw_hash': bad['functions'][-1]['raw_object_sha256'] = '0' * 64
        elif change == 'unequal': bad['functions'][3]['credited_bytes'] = bad['functions'][3]['size']
        elif change == 'wrong_target': bad['functions'][0]['relocations'][0]['target'] = '0067c249'
        elif change == 'overlap': bad['functions'][0]['relocations'].append(copy.deepcopy(bad['functions'][0]['relocations'][0]))
        elif change == 'source': bad['source_sha256'] = '0' * 64
        elif change == 'total': bad['credited_bytes'] += 1
        elif change == 'specimen': bad['reference_sha256'] = '0' * 64
        elif change == 'inventory': bad['inventory_sha256'] = '0' * 64
        elif change == 'compiler': bad['compiler']['files_sha256'] = {}
        bad_proofs.append(bad)
    for bad in bad_proofs:
        try: verify_proof(ledger, inventory, selection, bad, manifest, ROOT)
        except AssertionError: continue
        raise AssertionError('Corrupt native proof accepted')
    duplicate_selection = copy.deepcopy(selection)
    duplicate_selection['accepted_addresses'].append(selection['accepted_addresses'][0])
    try: verify_proof(ledger, inventory, duplicate_selection, proof, manifest, ROOT)
    except AssertionError: pass
    else: raise AssertionError('Duplicate native selection accepted')
    print(f'Native proof and {len(bad_proofs) + 1} corruption controls pass')
    if len(sys.argv) > 1:
        parser = str(Path(sys.argv[1]).resolve())
        bad_reports = []
        aggregate = copy.deepcopy(report)
        aggregate['measures']['matched_data'] = '1'
        bad_reports.append(aggregate)
        unit = copy.deepcopy(report)
        unit['units'][0]['measures']['matched_code_percent'] += 1
        bad_reports.append(unit)
        item = copy.deepcopy(report)
        item['units'][0]['functions'][0]['fuzzy_match_percent'] = 1
        bad_reports.append(item)
        arithmetic = copy.deepcopy(report)
        arithmetic['measures']['total_code'] = str(int(m['total_code']) + 1)
        bad_reports.append(arithmetic)
        moved = copy.deepcopy(report)
        items = moved['units'][0]['functions']
        matched = next(f for f in items if f['fuzzy_match_percent'] == 100)
        unproved = next(f for f in items if f['fuzzy_match_percent'] == 0 and f['size'] == matched['size'])
        matched['fuzzy_match_percent'], unproved['fuzzy_match_percent'] = 0, 100
        bad_reports.append(moved)  # Totals remain valid; selected proof must reject it.
        category = copy.deepcopy(report)
        category['categories'] = [{'id': 'invented', 'name': 'Unproved category', 'measures': copy.deepcopy(m)}]
        category['categories'][0]['measures']['matched_data'] = '1'
        bad_reports.append(category)
        missing_credit = copy.deepcopy(report)
        for target in (missing_credit['measures'], missing_credit['units'][0]['measures']):
            for key in ('matched_code_percent', 'matched_functions_percent', 'fuzzy_match_percent', 'matched_functions'):
                target[key] = 0
            target['matched_code'] = '0'
        for f in missing_credit['units'][0]['functions']: f['fuzzy_match_percent'] = 0
        bad_reports.append(missing_credit)
        with tempfile.TemporaryDirectory(prefix='thug2-report-controls-') as directory:
            path = Path(directory) / 'bad-report.json'
            for bad in bad_reports:
                path.write_text(json.dumps(bad))
                result = subprocess.run([parser, str(path)], capture_output=True)
                assert result.returncode != 0, 'Objdiff validator accepted corrupt matching/arithmetic'
        print(f'Actual objdiff parser rejects {len(bad_reports)} matching/arithmetic/provenance corruptions')


if __name__ == '__main__':
    main()
