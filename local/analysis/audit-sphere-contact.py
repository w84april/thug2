"""Rehash full swept sphere contacts and preserve coverage/playability limits."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'sphere-contact-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'sphere-sweep-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==4 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training']:
 assert c[key]==prior[key],key
assert c['browser_suites']==117 and c['unpromoted_functions_in_this_module']==526
assert c['unpromoted_functions_across_separate_experiments']==543
coverage=c['instruction_coverage'];assert sum(row['covered'] for row in coverage.values())==1576
assert sum(row['total'] for row in coverage.values())==1593
assert sum(len(row['missing']) for row in coverage.values())==17
assert all(not row['excluded'] for row in coverage.values())
assert coverage['0x40ec90']['covered']==coverage['0x40ec90']['total']==992
t=c['sphere_contact_training'];assert t['cases']==2244 and t['calls']==11220 and len(t['selected_triangles'])==561
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':7370,'unit_calls':7370,'new_instruction_coverage':'1576/1593; 17 unexercised, no exclusions',
 'training_triangle_cases':2244,'training_triangle_calls':11220,'actual_training_triangles':561,
 'preserved_scene_trace_calls':63,'playable':False}
(p/'sphere-contact-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
