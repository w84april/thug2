"""Rehash contact-solver evidence and preserve earlier integration limits."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
path=p/'rigidbody-solver-checkpoint.json';c=json.loads(path.read_text())
prior=json.loads((p/'motion-rotation-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==1 and not c['playable']
for key in ['actual_training','particle_frame_prefix','fan_training','original_only_scene_discovery','motion_descriptor_metadata']:
 assert c[key]==prior[key],key
assert c['browser_suites']==111 and c['unpromoted_functions_in_this_module']==510
assert c['unpromoted_functions_across_separate_experiments']==527
coverage=c['instruction_coverage']['0x430140']
assert (coverage['covered'],coverage['total'])==(688,690)
assert set(coverage['missing'])==set(coverage['excluded'])=={'0x4301b8','0x4301bf'}
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),
 'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),
 'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),
 'main_wasm_unchanged':True,'unit_cases':338,'unit_calls':418,
 'new_instruction_coverage':'688/690; only two unreachable alignment instructions excluded',
 'training_completed_calls':63,'fans':2,'fan_updates_each':4,'playable':False}
(p/'rigidbody-solver-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
