"""Validate exact complete extents, inline ID targets and body-only accounting."""
import csv,hashlib,json,struct
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(exe)=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));base=pe.OPTIONAL_HEADER.ImageBase;dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True
path=p/'skater-startup-tail-routines.json';routines=json.loads(path.read_text());checked={}
for address,row in routines.items():
 start=int(address,16);end=start+row['bytes'];code=list(dis.disasm(pe.get_data(start-base,row['bytes']),start));boundaries={i.address for i in code}
 assert len(code)==row['instructions'] and code[-1].address+code[-1].size==end and code[-1].mnemonic=='ret',address
 for i in code:
  if i.group(capstone.CS_GRP_JUMP):
   if i.operands[0].type==capstone.x86.X86_OP_IMM:assert i.operands[0].imm in boundaries,(address,hex(i.address),i.op_str)
   else:
    assert address=='0x511780' and i.address==0x51178b and i.op_str=='dword ptr [eax*4 + 0x5117e4]'
    targets=struct.unpack('<8I',pe.get_data(0x5117e4-base,32));assert all(a in boundaries for a in targets)
 checked[address]={'instructions':len(code),'end':hex(end),'terminator':code[-1].mnemonic}
padding=next(i for i in dis.disasm(pe.get_data(0x51acb0-base,118),0x51acb0) if i.address==0x51accd)
assert padding.mnemonic=='lea' and padding.op_str=='ecx, [ecx]' and padding.size==3
prior=list(csv.DictReader(Path('progress/function-inventory.tsv').open(),delimiter='\t'));known={int(x['address'],16) for x in prior};rows={}
for name in ['skater-1859f772-extra-ranges.tsv','skater-final-components-extra-ranges.tsv']:
 for row in csv.DictReader((p/name).open(),delimiter='\t'):
  a=int(row['address'],16)
  if a not in known:
   if a in rows:assert rows[a]==row
   rows[a]=row
target=p/'skater-startup-tail-extra-ranges.tsv'
with target.open('w') as f:
 w=csv.DictWriter(f,fieldnames=['address','body_bytes','ranges'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows[a] for a in sorted(rows))
inventory={int(x['address'],16):x for x in prior};inventory.update(rows)
sizes={a:int(inventory[int(a,16)]['body_bytes']) for a in routines};assert sizes['0x511780']==21 and routines['0x511780']['bytes']==98
report={'result':'pass','routines_sha256':sha(path),'checked':checked,'unreachable_alignment':{'address':'0x51accd','bytes':3,'instruction':'lea ecx, [ecx]','proof':'Unconditionally bypassed by51accb jump to51acd0; no branch or observable behavior omitted.'},'conservative_inline_ID_extent':{'address':'0x511780','verified_linear_bytes':98,'credited_Ghidra_body_bytes':21,'case_table_address':'0x5117e4','targets':[hex(x) for x in struct.unpack('<8I',pe.get_data(0x5117e4-base,32))]},'new_discovery_entries':len(rows),'new_complete_functions':len(routines),'new_complete_body_bytes':sum(sizes.values()),'new_verified_linear_bytes':sum(x['bytes'] for x in routines.values())}
(p/'skater-startup-tail-extents.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checked'}))
