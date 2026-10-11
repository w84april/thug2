"""Read-only artifact audit, with a new report path for this checkpoint only."""
import hashlib,json,subprocess,sys
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();path=p/'level-collision-load-checkpoint.json';c=json.loads(path.read_text());prior=json.loads((p/'level-object-startup-checkpoint.json').read_text())
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for name,digest in c[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert c[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==c['main_wasm_sha256']==prior['main_wasm_sha256']
assert c['new_functions']==4 and not c['playable'] and c['actual_training']['completed_objects']==0
assert c['actual_training']['collision']['count']==605 and c['actual_training']['collision']['sectors']==881
subprocess.run([sys.executable,'-B',str(p/'check-level-collision-load-graph.py')],check=True)
report={'result':'pass','checkpoint_sha256':sha(path),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'preserved_previous_artifacts':len(prior['artifact_hashes']),'main_wasm_unchanged':True,'completed_LevelObjects':0,'first_unrecovered_factory':'0x41c920','playable':False}
(p/'level-collision-load-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
