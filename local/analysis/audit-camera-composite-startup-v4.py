"""Audit the immutable metadata correction and unchanged complete v3 proofs."""
import hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
f=p/'camera-composite-startup-v4-checkpoint.json';c=read(f);old=read(r/c['metadata_correction']['preserved_checkpoint']);assert sha(r/c['metadata_correction']['preserved_checkpoint'])==c['metadata_correction']['preserved_checkpoint_sha256']
for group in ['artifact_hashes','source_hashes','draft_source_hashes','harness_hashes','platform_source_hashes','checker_dependency_hashes']:
 for n,h in c[group].items():assert sha(r/n)==h,(group,n)
 for n,h in old[group].items():assert c[group][n]==h,(group,n)
for k,v in old.items():
 if k not in ['artifact_hashes','harness_hashes']:assert c[k]==v,k
assert c['verified_scoped_addresses_from_prior']=={} and c['new_functions']==1 and c['new_complete_body_bytes']==24
a=read(p/'camera-composite-startup-v3-audit.json');a['checkpoint_sha256']=sha(f);a['artifacts']=len(c['artifact_hashes']);a['preserved_metadata_checkpoint_sha256']=c['metadata_correction']['preserved_checkpoint_sha256'];a['metadata_only_correction']=True
target=p/'camera-composite-startup-v4-audit.json';assert not target.exists();target.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
