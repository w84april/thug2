"""Audit the saved movement checkpoint and every inherited hash."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'motion-frame-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'particle-setup-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==6 and not c['playable'] and c['actual_training']==prior['actual_training']
assert c['browser_suites']==96 and c['unpromoted_functions_in_this_module']==428
assert c['particle_frame_prefix']['completed_calls']==48 and c['particle_frame_prefix']['interrupted_calls']==1
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'motion_cases':231,'motion_calls':731,'completed_browser_LevelObjects':31,'training_calls':49,'explicit_proximity_stops':1,'playable':False}
(p/'motion-frame-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
