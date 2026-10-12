"""Conservative Ghidra body accounting and original-entry deduplication."""
import csv,hashlib,json
from pathlib import Path
r=Path.cwd();p=r/'local/analysis';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();groups={n:json.loads((p/(n+'-routines.json')).read_text()) for n in ['skater-tag-texture','skater-final-startup','skater-full-startup']}
rows={}
for name in ['progress-function-ranges.tsv','skater-tag-pc-extra-ranges.tsv']:
 rows.update({int(x['address'],16):x for x in csv.DictReader((p/name).open(),delimiter='\t')})
ledger=json.loads((r/'progress/ledger.json').read_text());credited={int(x['address'],16) for x in ledger['records']};inventory={int(x['address'],16) for x in csv.DictReader((r/'progress/function-inventory.tsv').open(),delimiter='\t')};maps={a:v for g in groups.values() for a,v in g.items()};assert len(maps)==sum(map(len,groups.values()))==22
new={a:v for a,v in maps.items() if int(a,16) not in credited};shared={a:v for a,v in maps.items() if int(a,16) in credited};assert len(new)==21 and set(shared)=={'0x49f3b0'}
assert sum(v['body_bytes'] for v in new.values())==4093
for a,v in maps.items():
 row=rows[int(a,16)];assert v['body_bytes']==int(row['body_bytes']);assert v['ranges']==row['ranges'];assert v['body_bytes']<=v['bytes']
 for span in row['ranges'].split(';'):
  x,y=(int(s,16) for s in span.split(':'));assert int(a,16)<=x<=y<int(a,16)+v['bytes']
# Preserve the read-only export; additional inventory contains only absent entries.
extra=[row for a,row in rows.items() if a in {int(x,16) for x in maps} and a not in inventory];assert len(extra)==3
out=p/'skater-tag-texture-extra-ranges.tsv';out.write_text('address\tbody_bytes\tranges\n'+''.join(f"{row['address']}\t{row['body_bytes']}\t{row['ranges']}\n" for row in extra));assert sum(int(row['body_bytes']) for row in extra)==85
report={'result':'pass','baseline_report_sha256':sha(r/'progress/report.json'),'baseline_ledger_sha256':sha(r/'progress/ledger.json'),'routines_sha256':{n:sha(p/(n+'-routines.json')) for n in groups},'selected_mappings':22,'new_unique_addresses':21,'shared_addresses':['0x49f3b0'],'new_complete_body_bytes':4093,'selected_body_bytes':4101,'selected_linear_bytes':sum(v['bytes'] for v in maps.values()),'inventory_additions':3,'inventory_added_body_bytes':85,'body_linear_differences':{'0x4e06a0':{'body_bytes':73,'linear_bytes':82,'unreachable_alignment_bytes':9,'reason':'4e06c5 unconditionally branches to4e06d0; excluded4e06c7..4e06cf are never entered'}},'contract_exclusions':'Initialized allocator/GPU and valid bounded storage; no cold-process equivalence or unchecked allocation-fault recovery claimed','playable':False}
(p/'skater-full-startup-extents.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
