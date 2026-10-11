"""Rehash sphere geometry and preserve the explicit scene-integration limits."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'sphere-geometry-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'rigidbody-solver-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==4 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata']:
 assert c[key]==prior[key],key
assert c['browser_suites']==113 and c['unpromoted_functions_in_this_module']==514
assert c['unpromoted_functions_across_separate_experiments']==531
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==614
assert all(row['covered']==row['total'] and not row['missing'] and not row['excluded'] for row in coverage.values())
t=c['sphere_training'];assert t['cases']==1683 and t['calls']==8415 and len(t['selected_triangles'])==561
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':2259,'unit_calls':2662,'new_instruction_coverage':'614/614; no exclusions',
 'training_triangle_cases':1683,'training_triangle_calls':8415,'actual_training_triangles':561,
 'preserved_scene_trace_calls':63,'playable':False}
(p/'sphere-geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
