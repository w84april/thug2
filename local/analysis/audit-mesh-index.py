import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
report_path=p/'mesh-index-audit.json';assert not report_path.exists()
pin=json.loads((p/'mesh-index-checkpoint.json').read_text());prior=json.loads((p/'scene-construction-checkpoint.json').read_text())
groups=['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']
for group in groups:
 for name,digest in pin[group].items():assert sha(r/name)==digest,(group,name)
 for name,digest in prior[group].items():assert pin[group][name]==digest,(group,name)
assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
assert sha(p/'mesh-index-draft.wasm')==pin['wasm_sha256']
report={'result':'pass','checkpoint_sha256':sha(p/'mesh-index-checkpoint.json'),'checked':{g:len(pin[g]) for g in groups},
 'preserved_prior_artifacts':len(prior['artifact_hashes']),'main_unchanged':True,'playable':False}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
