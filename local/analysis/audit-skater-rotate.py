"""Check complete SkaterRotate evidence and the complete preserved artifact chain."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'skater-rotate-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'skater-trick-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','platform_source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==11 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training','rigidbody_update_training','rigidbody_active_training','live_browser_keyboard','live_input_callbacks','live_input_lifecycle','live_input_commands','input_command_descriptors','named_qb_member_dispatches','partial_original_addresses','score_asset_initialization','matrix_fcos_infinity_specification','trick_control_shared_startup']:
 assert c[key]==prior[key],key
assert c['prior_skater_constructor_prefix']==prior['skater_constructor_prefix']
assert c['browser_suites']==135 and c['unpromoted_functions_in_this_module']==641
assert c['unpromoted_functions_across_separate_experiments']==658
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==679
assert sum(row['total'] for row in coverage.values())==685
assert not any(row['excluded'] for row in coverage.values())
assert sum(len(row['missing']) for row in coverage.values())==6
prefix=c['skater_constructor_prefix'];assert prefix['interrupted_calls']==32 and len(prefix['records'])==32
assert (prefix['covered'],prefix['total'])==(221,463)
assert c['new_cases']==809 and c['new_calls_including_existing_dependencies']==1646
assert c['score_asset_initialization']['cases']==4 and c['score_asset_initialization']['calls']==12
assert len(c['matrix_fcos_infinity_specification']['cases'])==2
assert len(c['skater_rotate_shared_startup'])==2
assert c['rotate_double_returns']=={'bit_checks':366,'nan_payloads':2}
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'platform_sources':len(c['platform_source_hashes']),
 'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),
 'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,
 'unit_cases':809,'unit_calls':1646,'double_returns_checked_exactly':366,'nan_double_returns_checked_exactly':2,'fcos_infinity_cases':2,'fcos_infinity_emulator_differences':1,
 'new_instruction_coverage':'679/685;six allocation-failure instructions unexercised;no exclusions',
 'constructor_prefix_coverage':'221/463;32 interrupted calls;local path advances through SkaterRotate',
 'preserved_training_trace_calls':67,'preserved_active_snapshot_calls':2,'playable':False}
(p/'skater-rotate-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
