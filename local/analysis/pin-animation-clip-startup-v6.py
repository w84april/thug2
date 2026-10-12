"""Preserve the scoped proof and pin its one additional discovery extent."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();read=lambda f:json.loads(f.read_text())
old=p/'animation-clip-startup-v4-checkpoint.json';audit=p/'animation-clip-startup-v4-audit.json';extra=p/'animation-clip-startup-v6-selected-ranges.tsv'
assert sha(old)=='3d572b67c03bbc98ca52dc81d1a4789895cd131ee091578af3633ef2f604d39c'
c=read(old);a=read(audit);assert a['result']=='pass' and a['checkpoint_sha256']==sha(old)
for group in ['artifact_hashes','source_hashes','draft_source_hashes','harness_hashes','platform_source_hashes','checker_dependency_hashes']:
 for n,h in c[group].items():assert sha(r/n)==h,(group,n)
rows=list(csv.DictReader(extra.open(),delimiter='\t'));assert rows==[{'address':'004823c0','body_bytes':'1442','ranges':'004823c0:00482961'}]
assert rows[0] in list(csv.DictReader((p/'animation-clip-startup-v1-ranges.tsv').open(),delimiter='\t'))
assert set(c['original_addresses'])=={'0x4616f0','0x4823c0'} and c['new_complete_body_bytes']==1467
c['discovery_extension']={'preserved_checkpoint':str(old.relative_to(r)),'preserved_checkpoint_sha256':sha(old),'selected_export':str(extra.relative_to(r)),'selected_export_sha256':sha(extra),'reason':'4823c0 was absent from the prior inventory;4616f0 was already known. Select only the independently exported1442-byte extent to avoid duplicate inventory rows. No behavioral proof, module, addresses, sizes or scoped exclusions change.'}
for f in [old,audit,extra,p/'pin-animation-clip-startup-v6.py',p/'audit-animation-clip-startup-v6.py']:
 c['artifact_hashes'][str(f.relative_to(r))]=sha(f)
 if f.suffix=='.py':c['harness_hashes'][str(f.relative_to(r))]=sha(f)
c['artifact_hashes']=dict(sorted(c['artifact_hashes'].items()));c['harness_hashes']=dict(sorted(c['harness_hashes'].items()))
target=p/'animation-clip-startup-v6-checkpoint.json';assert not target.exists();target.write_text(json.dumps(c,indent=2)+'\n');print('Pinned discovery-compatible checkpoint',len(c['artifact_hashes']),'artifacts;',sha(target))
