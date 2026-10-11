import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
pin=json.loads((p/'prop-sound-checkpoint.json').read_text());prior=json.loads((p/'prop-lifecycle-checkpoint.json').read_text())
groups=['artifact_hashes','source_hashes','harness_hashes','checker_dependency_hashes']
for group in groups:
 for n,h in pin[group].items():assert sha(r/n)==h,(group,n)
for group in groups:
 for n,h in prior[group].items():assert pin[group][n]==h,(group,n)
assert sha(r/'local/build/thug-core.wasm')==pin['main_wasm_sha256']
assert sha(p/'prop-sound-draft.wasm')==pin['wasm_sha256']
report={'result':'pass','checkpoint_sha256':sha(p/'prop-sound-checkpoint.json'),
 'checked':{g:len(pin[g]) for g in groups},'preserved_prior_artifacts':len(prior['artifact_hashes']),'main_unchanged':True,'playable':False}
(p/'prop-sound-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
