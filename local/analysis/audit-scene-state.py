import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
pin=json.loads((p/'scene-state-checkpoint.json').read_text());prior=json.loads((p/'training-mode-checkpoint.json').read_text())
groups=['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']
for group in groups:
 for n,h in pin[group].items():assert sha(r/n)==h,(group,n)
for n,h in prior['artifact_hashes'].items():assert pin['artifact_hashes'][n]==h,n
assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
assert sha(p/'scene-state-draft.wasm')==pin['wasm_sha256']
report={'result':'pass','checkpoint_sha256':sha(p/'scene-state-checkpoint.json'),
 'checked':{g:len(pin[g]) for g in groups},'preserved_prior_artifacts':len(prior['artifact_hashes']),
 'main_unchanged':True,'playable':False}
(p/'scene-state-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
