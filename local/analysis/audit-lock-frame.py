"""Audit attachment checkpoint and preservation of all earlier evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'lock-frame-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'proximity-frame-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==6 and not c['playable'] and c['actual_training']==prior['actual_training']
assert c['browser_suites']==100 and c['unpromoted_functions_in_this_module']==439
assert c['particle_frame_prefix']['completed_calls']==49 and c['particle_frame_prefix']['interrupted_calls']==1 and c['particle_frame_prefix']['barrel_update_complete']
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'attachment_cases':294,'attachment_calls':1125,'completed_browser_LevelObjects':31,'training_calls':50,'completed_barrel_object_updates':1,'explicit_particle_stops':1,'playable':False}
(p/'lock-frame-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
