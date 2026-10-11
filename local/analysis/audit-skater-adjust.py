"""Verify new evidence and all inherited checkpoint hashes without changing them."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'skater-adjust-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'skater-gap-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==8 and not c['playable']
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','main_wasm_sha256','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','prior_skater_constructor_prefix','skater_constructor_prefix','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_skater_constructor_prefix']==prior['skater_constructor_prefix']
assert (c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(137,660,677)
coverage=c['instruction_coverage'];assert (sum(row['covered'] for row in coverage.values()),sum(row['total'] for row in coverage.values()))==(355,376)
assert not any(row['excluded'] for row in coverage.values())
assert len(coverage['0x4f80e0']['missing'])==7 and len(coverage['0x427700']['missing'])==14
prefix=c['skater_constructor_prefix'];assert prefix['interrupted_calls']==len(prefix['records'])==32 and (prefix['covered'],prefix['total'])==(241,463)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'])==(313,565)
assert len(c['skater_adjust_shared_startup'])==2
assert c['moving_escape_evidence']['escape_first_call_outcomes']=={'restore previous':48,'surface plus one':13,'velocity candidate':11}
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'platform_sources':len(c['platform_source_hashes']),
 'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,
 'unit_cases':313,'unit_calls':565,'new_instruction_coverage':'355/376;seven factory-failure and fourteen probe-cleanup instructions unexercised;no exclusions',
 'constructor_prefix_coverage':'241/463;32 interrupted calls;local path creates SkaterAdjustPhysics',
 'preserved_training_trace_calls':67,'preserved_active_snapshot_calls':2,'playable':False}
(p/'skater-adjust-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
