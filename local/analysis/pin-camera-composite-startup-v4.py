"""Add the reconciler's explicit empty duplicate map without altering proof v3."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
old=p/'camera-composite-startup-v3-checkpoint.json';audit=p/'camera-composite-startup-v3-audit.json'
assert sha(old)=='40fe1004554632f2399fe1c1890cbeda2196167a7a3ad45fdd845004328604cd'
c=read(old);a=read(audit);assert a['result']=='pass' and a['checkpoint_sha256']==sha(old)
for group in ['artifact_hashes','source_hashes','draft_source_hashes','harness_hashes','platform_source_hashes','checker_dependency_hashes']:
 for n,h in c[group].items():assert sha(r/n)==h,(group,n)
assert set(c['original_addresses'])=={'0x41b7f0'} and c['new_functions']==1 and c['new_complete_body_bytes']==24
c['verified_scoped_addresses_from_prior']={}
c['metadata_correction']={'preserved_checkpoint':str(old.relative_to(r)),'preserved_checkpoint_sha256':sha(old),'reason':'The central reconciler requires an explicit duplicate-map field even when empty. The v3 proof omitted that field. No evidence, addresses, counts, source, module or result changes.'}
for f in [old,audit,p/'pin-camera-composite-startup-v4.py',p/'audit-camera-composite-startup-v4.py']:
 c['artifact_hashes'][str(f.relative_to(r))]=sha(f)
 if f.suffix=='.py':c['harness_hashes'][str(f.relative_to(r))]=sha(f)
c['artifact_hashes']=dict(sorted(c['artifact_hashes'].items()));c['harness_hashes']=dict(sorted(c['harness_hashes'].items()))
target=p/'camera-composite-startup-v4-checkpoint.json';assert not target.exists();target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned metadata-compatible checkpoint',len(c['artifact_hashes']),'artifacts;',sha(target))
