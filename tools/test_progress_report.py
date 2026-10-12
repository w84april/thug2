"""Small corruption controls for the public report generator."""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from generate_progress_report import ROOT, generate


def main():
    ledger = json.loads((ROOT / 'progress/ledger.json').read_text())
    report = generate(ledger)
    m = report['measures']
    assert int(m['complete_code']) == sum(r['size'] for r in ledger['records'])
    assert int(m['total_code']) == ledger['code_section']['virtual_size']
    assert m['matched_code'] == '0' and m['matched_functions'] == 0
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
    if len(sys.argv) > 1:
        parser = str(Path(sys.argv[1]).resolve())
        bad_reports = []
        aggregate = copy.deepcopy(report)
        aggregate['measures']['matched_data'] = '1'
        bad_reports.append(aggregate)
        unit = copy.deepcopy(report)
        unit['units'][0]['measures']['matched_code_percent'] = 1
        bad_reports.append(unit)
        item = copy.deepcopy(report)
        item['units'][0]['functions'][0]['fuzzy_match_percent'] = 1
        bad_reports.append(item)
        arithmetic = copy.deepcopy(report)
        arithmetic['measures']['total_code'] = str(int(m['total_code']) + 1)
        bad_reports.append(arithmetic)
        with tempfile.TemporaryDirectory(prefix='thug2-report-controls-') as directory:
            path = Path(directory) / 'bad-report.json'
            for bad in bad_reports:
                path.write_text(json.dumps(bad))
                result = subprocess.run([parser, str(path)], capture_output=True)
                assert result.returncode != 0, 'Objdiff validator accepted corrupt matching/arithmetic'
        print('Actual objdiff parser rejects four matching/arithmetic corruptions')


if __name__ == '__main__':
    main()
