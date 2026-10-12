"""Verify Trigger and construction evidence while preserving the prior checkpoint."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'trigger-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'gap-end-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope','prior_skater_constructor_prefix','skater_constructor_prefix'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'gap-end-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(8,144,726,743)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(307,513,32)
assert (sum(x['covered'] for x in c['instruction_coverage'].values()),sum(x['total'] for x in c['instruction_coverage'].values()))==(293,294)
assert not any(x['excluded'] for x in c['instruction_coverage'].values()) and not c['playable']
assert c['prior_skater_constructor_prefix']==prior['skater_constructor_prefix']
assert (c['skater_constructor_prefix']['covered'],c['skater_constructor_prefix']['total'])==(249,463)
assert c['trigger_evidence']['native_qb_callbacks']==35 and c['trigger_evidence']['completed_calls']==481
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':307,'unit_calls':513,'completed_calls':481,'interrupted_calls':32,
 'new_instruction_coverage':'293/294; one skipped alignment instruction unexercised; no exclusions',
 'native_qb_callbacks':35,'new_uninitialized_byte_allowances':0,'browser_suites':144,'preserved_browser_suites':143,
 'constructor_prefix':'249/463; local path creates Trigger then stops before SkaterFinalizePhysics','playable':False}
(p/'trigger-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
