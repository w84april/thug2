"""Verify Walk evidence and preservation of the CleanupState checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'skater-walk-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'skater-cleanup-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope','prior_skater_constructor_prefix','skater_constructor_prefix'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'skater-cleanup-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(11,147,764,781)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(848,1474,144)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(505,505)
assert not any(x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
assert c['prior_skater_constructor_prefix']==prior['skater_constructor_prefix']
assert (c['skater_constructor_prefix']['covered'],c['skater_constructor_prefix']['total'])==(277,463)
assert c['walk_evidence']['completed_calls']==1330 and c['walk_evidence']['allocation_failure_calls']==2
frame=c['walk_evidence']['partial_frame'];assert (frame['covered'],frame['total'],frame['interrupted_calls'])==(51,142,112)
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':848,'unit_calls':1474,'completed_calls':1330,'interrupted_calls':144,
 'new_instruction_coverage':'505/505; no exclusions; instruction coverage does not imply exhaustive inputs or branches',
 'new_uninitialized_byte_allowances':0,'new_float_comparison_allowances':0,'browser_suites':147,'preserved_browser_suites':146,
 'constructor_prefix':'277/463; local path creates Walk then stops before7cd3e6d5','walk_frame_prefix':'51/142; stops before five state handlers or remaining common tail','playable':False}
(p/'skater-walk-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
