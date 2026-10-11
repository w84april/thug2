"""Read-only audit of frozen combined startup evidence."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
f=p/'level-object-startup-checkpoint.json';c=read(f);prior=read(p/'geometry-clone-checkpoint.json')
for group in ['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']:
 for n,h in c[group].items():assert sha(r/n)==h,(group,n)
for n,h in prior['artifact_hashes'].items():assert c['artifact_hashes'][n]==h
assert c['main_wasm_sha256']==sha(r/'local/build/thug-core.wasm')==prior['main_wasm_sha256']
assert c['new_functions']==0 and c['browser_suites']==75 and c['new_interrupted_calls']==1 and not c['playable']
assert c['actual_training']['completed_objects']==0 and c['actual_training']['boundary']=='0x41c920'
report={'result':'pass','checkpoint_sha256':sha(f),'preserved_prior_artifacts':len(prior['artifact_hashes']),'artifacts':len(c['artifact_hashes']),'maintained_sources':len(c['source_hashes']),'harnesses':len(c['harness_hashes']),'checker_dependencies':len(c['checker_dependency_hashes']),'browser_suites':75,'completed_prefix_calls':10,'interrupted_calls':1,'completed_level_objects':0,'next_boundary':'Collision factory41c920','main_unchanged':True,'playable':False}
(p/'level-object-startup-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
