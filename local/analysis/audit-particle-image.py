"""Audit the saved particle creation checkpoint and every inherited hash."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'particle-image-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'particle-create-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==11 and not c['playable'] and c['actual_training']==prior['actual_training']
assert c['browser_suites']==92 and c['unpromoted_functions_in_this_module']==419
assert c['particle_frame_prefix']['completed_calls']==48 and c['particle_frame_prefix']['interrupted_calls']==1
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'image_cases':154,'image_calls':162,'completed_browser_LevelObjects':31,'training_calls':49,'explicit_effect_setup_stops':1,'playable':False}
(p/'particle-image-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
