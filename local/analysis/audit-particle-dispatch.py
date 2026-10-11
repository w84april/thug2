"""Audit the complete particle component/training checkpoint without rewriting it."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'particle-dispatch-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'particle-update-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==13 and not c['playable'] and c['actual_training']==prior['actual_training']
assert c['browser_suites']==107 and c['unpromoted_functions_in_this_module']==494 and c['unpromoted_functions_across_separate_experiments']==511
assert c['prior_particle_frame_prefix']==prior['particle_frame_prefix']
t=c['particle_frame_prefix'];assert t['completed_calls']==52 and t['interrupted_calls']==0 and t['particle_count']==2 and t['setup_script_after']==0
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'unit_cases':132,'unit_calls':283,'training_completed_calls':52,'training_interrupted_calls':0,'actual_training_fire_particles':2,'playable':False}
(p/'particle-dispatch-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
