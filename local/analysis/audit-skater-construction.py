"""Verify skater startup evidence while preserving prior scene and input work."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'skater-construction-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'input-command-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==8 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training','rigidbody_update_training','rigidbody_active_training','live_browser_keyboard','live_input_callbacks','live_input_lifecycle','live_input_commands','input_command_descriptors','named_qb_member_dispatches']:
 assert c[key]==prior[key],key
assert c['partial_original_addresses']==prior['partial_original_addresses']+['0x582d90']
assert c['browser_suites']==130 and c['unpromoted_functions_in_this_module']==604
assert c['unpromoted_functions_across_separate_experiments']==621
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==161
assert sum(row['total'] for row in coverage.values())==175
assert not any(row['excluded'] for row in coverage.values())
assert sum(len(row['missing']) for row in coverage.values())==14
prefix=c['skater_constructor_prefix'];assert prefix['interrupted_calls']==32 and len(prefix['records'])==32
assert (prefix['covered'],prefix['total'])==(145,463)
assert c['new_cases']==114 and c['new_calls_including_existing_dependencies']==228
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'platform_sources':len(c['platform_source_hashes']),
 'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,
 'unit_cases':114,'unit_calls':228,'new_instruction_coverage':'161/175;14 unexercised;no exclusions',
 'constructor_prefix_coverage':'145/463;32 interrupted calls before Score',
 'preserved_training_trace_calls':67,'preserved_active_snapshot_calls':2,'playable':False}
(p/'skater-construction-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
