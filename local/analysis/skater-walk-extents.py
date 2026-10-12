"""Check exact Walk code spans and local jump targets against the specimen."""
import hashlib,json
from pathlib import Path
from specimen import load
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
p=Path('local/analysis');path=p/'skater-walk-routines.json';specs=json.loads(path.read_text());pe=load();checked={}
for at,row in specs.items():
 a=int(at,16);n=row['bytes'];code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a))
 assert sum(i.size for i in code)==n and len(code)==row['instructions'] and code[-1].mnemonic in ['ret','jmp']
 starts={i.address for i in code};tail_calls={}
 for i in code:
  if i.mnemonic.startswith('j') and i.op_str.startswith('0x'):
   target=int(i.op_str,16)
   if target not in starts:
    assert i.mnemonic=='jmp' and target==0x4023f0,(hex(i.address),i.op_str)
    tail_calls[hex(i.address)]=hex(target)
 checked[at]={'instructions':len(code),'end':hex(a+n),'terminator':code[-1].mnemonic,'external_tail_calls':tail_calls}
report={'result':'pass','routines_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':checked}
(p/'skater-walk-extents.json').write_text(json.dumps(report,indent=2)+'\n');print('Checked',len(checked),'routine spans')
