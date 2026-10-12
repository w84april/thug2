"""Audit hanging/rail evidence while preserving every prior checkpoint byte."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'walk-floor-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'walk-ledge-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-ledge-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(12,151,796,813)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(559,811,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(1145,1145)
assert not any(x['missing'] or x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_floor_evidence'];assert (e['completed_calls'],e['new_routine_calls'],e['existing_probe_initializations'],e['interrupted_calls'])==(811,751,60,0)
assert e['new_comparison_allowances']==0 and not e['new_unreachable_exclusions']
assert len(e['callback_records'])==12 and sum(x['callbacks'] for x in e['callback_records'])==4
assert len(e['upper_rail_callback_records'])==2 and len(e['ledge_continuation_records'])==72
assert len(e['vertical_clearance_records'])==40 and len(e['coincident_records'])==96
previous=json.loads((p/'walk-ledge-browser.json').read_text())['observed']['suites']
observed=json.loads((p/'walk-floor-browser.json').read_text())['observed']['suites'];assert len(observed)==151
for name,value in previous.items():assert observed[name]==value,name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':559,'unit_calls':811,'completed_calls':811,'interrupted_calls':0,
 'new_instruction_coverage':'1145/1145; no exclusions; not exhaustive inputs or branches',
 'new_float_comparison_allowances':0,'new_indeterminate_field_allowances':0,'browser_suites':151,'preserved_browser_suites':150,
 'constructor_prefix':'277/463 unchanged; local path stops before7cd3e6d5','walk_frame_prefix':'51/142 unchanged; stops before state handlers or common tail',
 'walk_ground_prefix':'63/134 unchanged; stops before floor handler52b370 with genuine state/control exits preserved','playable':False}
(p/'walk-floor-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
