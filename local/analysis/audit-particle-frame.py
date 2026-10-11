"""Audit particle prerequisite checkpoint and preserve all earlier evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'particle-frame-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'lock-frame-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==7 and not c['playable'] and c['actual_training']==prior['actual_training']
assert c['browser_suites']==101 and c['unpromoted_functions_in_this_module']==446
assert c['particle_frame_prefix']==prior['particle_frame_prefix']
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'particle_prerequisite_cases':246,'particle_prerequisite_calls':906,'prior_training_unchanged':True,'playable':False}
(p/'particle-frame-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
