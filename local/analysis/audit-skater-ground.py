"""Recheck the complete checkpoint and preserve every prior boundary."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'skater-ground-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'skater-adjust-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
changed={'result','prior_checkpoint_sha256','new_functions','original_addresses','unpromoted_functions_in_this_module','unpromoted_functions_across_separate_experiments','wasm_sha256','wasm_bytes','main_wasm_sha256','browser_suites','new_cases','new_calls_including_existing_dependencies','new_interrupted_calls','instruction_coverage','unrecovered_lifecycle','coverage_limit','artifact_hashes','harness_hashes','browser_dom_fingerprint','playable','scope'}
for key in set(prior)-changed:assert c[key]==prior[key],key
assert c['prior_checkpoint_sha256']==sha(p/'skater-adjust-checkpoint.json')
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert (c['new_functions'],c['browser_suites'],c['unpromoted_functions_in_this_module'],c['unpromoted_functions_across_separate_experiments'])==(14,138,674,691)
assert (c['new_cases'],c['new_calls_including_existing_dependencies'],c['new_interrupted_calls'])==(478,1032,0)
coverage=c['instruction_coverage'];assert (sum(x['covered'] for x in coverage.values()),sum(x['total'] for x in coverage.values()))==(955,960)
assert not any(x['excluded'] for x in coverage.values())
assert c['skater_constructor_prefix']==prior['skater_constructor_prefix'] and not c['playable']
e=c['skater_ground_evidence'];assert len(e['owner_virtual_frames'])==8 and e['original_collision_queries']==842 and e['original_event_emissions']==65
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),
 'platform_sources':len(c['platform_source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':478,'unit_calls':1032,
 'new_instruction_coverage':'955/960;two skipped alignment and three secondary-probe cleanup instructions unexercised;no exclusions',
 'owner_dispatch_frames':24,'original_collision_queries':842,'original_event_emissions':65,
 'constructor_prefix_unchanged':'241/463;local path stops before Trigger','preserved_training_trace_calls':67,'preserved_active_snapshot_calls':2,'playable':False}
(p/'skater-ground-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
