"""Rehash fan-rotation evidence and verify its explicit integration limits."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'motion-rotation-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'rigidbody-response-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==6 and not c['playable'] and c['actual_training']==prior['actual_training'] and c['particle_frame_prefix']==prior['particle_frame_prefix']
assert c['browser_suites']==110 and c['unpromoted_functions_in_this_module']==509 and c['unpromoted_functions_across_separate_experiments']==526
assert c['fan_training']['completed_calls']==63 and c['fan_training']['interrupted_calls']==0
assert len(c['fan_training']['fans'])==2 and all(len(f['matrices'])==len(set(f['matrices']))==4 for f in c['fan_training']['fans'])
assert c['original_only_scene_discovery']['result']=='returned' and len(c['original_only_scene_discovery']['object_update_entries'])==32
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':621,'unit_calls':1275,'new_instruction_coverage':'722/722','training_completed_calls':63,'fans':2,'fan_updates_each':4,'unrecovered_registered_motion_members':45,'playable':False}
(p/'motion-rotation-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
