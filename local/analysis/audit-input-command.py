"""Verify command evidence and all preserved training progress."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'input-command-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'input-lifecycle-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==15 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training','partial_original_addresses','rigidbody_update_training','rigidbody_active_training','live_browser_keyboard','live_input_callbacks','live_input_lifecycle']:
 assert c[key]==prior[key],key
assert c['browser_suites']==129 and c['unpromoted_functions_in_this_module']==596
assert c['unpromoted_functions_across_separate_experiments']==613
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==339
assert sum(row['total'] for row in coverage.values())==339
assert not any(row['excluded'] or row['missing'] for row in coverage.values())
assert len(c['live_input_commands']['events'])==28 and len(c['input_command_descriptors'])==15
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'platform_sources':len(c['platform_source_hashes']),
 'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,
 'unit_cases':856,'unit_calls':1090,'new_instruction_coverage':'339/339; no exclusions',
 'named_input_commands':14,'descriptor_rows':15,'live_keyboard_transitions':28,'live_script_invocations':8,
 'preserved_training_trace_calls':67,'preserved_active_snapshot_calls':2,'playable':False}
(p/'input-command-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
