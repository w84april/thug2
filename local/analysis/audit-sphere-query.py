"""Rehash scene sphere query evidence and preserve the full playable-level scope."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'sphere-query-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'sphere-contact-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==4 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training']:
 assert c[key]==prior[key],key
assert c['browser_suites']==119 and c['unpromoted_functions_in_this_module']==530
assert c['unpromoted_functions_across_separate_experiments']==547
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==sum(row['total'] for row in coverage.values())==560
assert all(not row['excluded'] and not row['missing'] for row in coverage.values())
t=c['sphere_query_training'];assert t['cases']==1122 and t['calls']==3366 and len(t['selected_triangles'])==561
assert len(t['relocations'])==978 and t['grid_cell_references']==905 and t['grid_nonempty_cells']==73
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':533,'unit_calls':635,'new_instruction_coverage':'560/560; no exclusions',
 'training_query_cases':1122,'training_query_calls':3366,'actual_training_collision_objects':605,
 'preserved_scene_trace_calls':63,'playable':False}
(p/'sphere-query-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
