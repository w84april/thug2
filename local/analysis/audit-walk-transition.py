"""Verify Walk transitions and preserve the ground-helper checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'walk-transition-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'walk-ground-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'walk-ground-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(11,149,782,799)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(825,1399,0)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(1011,1014)
assert sum(len(x['excluded']) for x in c['instruction_coverage'].values())==3 and not c['playable']
e=c['walk_transition_evidence'];assert e['completed_calls']==1399 and e['interrupted_calls']==0
assert len(e['rail_sequence_records'])==12 and all(row['final_state']==3 for row in e['rail_sequence_records'])
assert c['skater_constructor_prefix']==prior['skater_constructor_prefix'] and c['walk_evidence']==prior['walk_evidence'] and c['walk_ground_evidence']==prior['walk_ground_evidence']
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':825,'unit_calls':1399,'completed_calls':1399,'interrupted_calls':0,
 'new_instruction_coverage':'1011/1014; three documented unreachable-path exclusions after a false collision query; not exhaustive inputs or branches',
 'new_uninitialized_byte_allowances':0,'new_float_comparison_allowances':0,'browser_suites':149,'preserved_browser_suites':148,
 'constructor_prefix':'277/463 unchanged; local path stops before7cd3e6d5','walk_frame_prefix':'51/142 unchanged; stops before state handlers or common tail',
 'walk_ground_prefix':'18/134 unchanged; stops before transition52c2c0','rail_selection_to_callback_target_sequences':12,'playable':False}
(p/'walk-transition-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
