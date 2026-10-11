"""Rehash complete prop/manager updates without claiming playability."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'rigidbody-update-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'rigidbody-kick-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==3 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training','partial_original_addresses']:
 assert c[key]==prior[key],key
assert c['browser_suites']==125 and c['unpromoted_functions_in_this_module']==536
assert c['unpromoted_functions_across_separate_experiments']==553
coverage=c['instruction_coverage']
assert sum(row['covered'] for row in coverage.values())==585
assert sum(row['total'] for row in coverage.values())==594
assert sum(len(row['missing']) for row in coverage.values())==9
assert all(not row['excluded'] for row in coverage.values())
normal=c['rigidbody_update_training'];active=c['rigidbody_active_training']
assert normal['completed_calls']==67 and normal['interrupted_calls']==0 and normal['full_manager_updates']==4
assert active['completed_calls']==2 and active['interrupted_calls']==0 and active['full_manager_updates']==2
assert len(active['wake_input'])==19 and active['dependency_calls']['0x430140']==17
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':455,'unit_calls':871,'new_instruction_coverage':'585/594; nine unexercised, no exclusions',
 'training_trace_calls':67,'active_snapshot_trace_calls':2,'complete_manager_updates':6,'playable':False}
(p/'rigidbody-update-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
