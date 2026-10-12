"""Audit ledge/contact evidence while preserving all preceding checkpoint bytes."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'walk-ledge-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'walk-transition-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-transition-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(2,150,784,801)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(503,680,9)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(1241,1244)
assert not any(x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
e=c['walk_ledge_evidence'];assert e['completed_calls']==671 and e['interrupted_calls']==9
assert len(e['callback_records'])==14 and len(e['contact_transition_records'])==6
assert (e['ground_prefix_coverage']['covered'],e['ground_prefix_coverage']['total'])==(63,134)
assert len(e['ground_prefix_records'])==15 and sum(x['interrupted'] for x in e['ground_prefix_records'])==9
assert e['undefined_source_offsets']=={'0xa8':784,'0x70':36} and e['undefined_word_comparisons']==820
assert e['checker_corruptions_rejected']==6 and e['undefined_word_mutation_accepted']
previous=json.loads((p/'walk-transition-browser.json').read_text())['observed']['suites']
observed=json.loads((p/'walk-ledge-browser.json').read_text())['observed']['suites'];assert len(observed)==150
for name,value in previous.items():assert observed[name]==value,name
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':503,'unit_calls':680,'completed_calls':671,'interrupted_calls':9,
 'new_instruction_coverage':'1241/1244; three unexercised alignment instructions without exclusions; not exhaustive inputs or branches',
 'undefined_word_comparisons':820,'undefined_source_offsets':e['undefined_source_offsets'],'undefined_field_provenance_checked':True,'checker_corruptions_rejected':6,
 'new_float_comparison_allowances':0,'browser_suites':150,'preserved_browser_suites':149,
 'constructor_prefix':'277/463 unchanged; local path stops before7cd3e6d5','walk_frame_prefix':'51/142 unchanged; stops before state handlers or common tail',
 'walk_ground_prefix':'63/134, previously18/134; stops before floor handler52b370 with genuine state/control exits preserved','playable':False}
(p/'walk-ledge-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
