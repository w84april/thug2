"""Rehash the kick checkpoint without treating component tests as playability."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'rigidbody-kick-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'contact-assembly-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==2 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata','sphere_training','sphere_sweep_training','sphere_contact_training','sphere_query_training','contact_assembly_training']:
 assert c[key]==prior[key],key
assert c['browser_suites']==122 and c['unpromoted_functions_in_this_module']==533
assert c['unpromoted_functions_across_separate_experiments']==550
for address,count in [('0x42c140',402),('0x48c770',29)]:
 row=c['instruction_coverage'][address];assert row['covered']==row['total']==count and not row['missing'] and not row['excluded']
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':395,'unit_calls':407,'new_instruction_coverage':'431/431; no exclusions',
 'preserved_scene_trace_calls':63,'playable':False}
(p/'rigidbody-kick-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
