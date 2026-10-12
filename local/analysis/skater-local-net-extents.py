"""Verify each claimed complete routine's exact instruction and branch extent."""
import hashlib,json
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe')
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True
path=p/'skater-local-net-routines.json';routines=json.loads(path.read_text());checked={}
for address,row in routines.items():
 start=int(address,16);end=start+row['bytes'];code=list(dis.disasm(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase,row['bytes']),start))
 assert len(code)==row['instructions'] and code[-1].address+code[-1].size==end and code[-1].mnemonic in ['ret','jmp'],address
 boundaries={i.address for i in code};tails={0x512e36:0x45d740} if start==0x512e30 else {}
 for instruction in code:
  if instruction.group(capstone.CS_GRP_JUMP):
   assert instruction.operands[0].type==capstone.x86.X86_OP_IMM,(address,instruction.address)
   assert instruction.operands[0].imm in boundaries or (instruction.mnemonic=='jmp' and instruction.address+instruction.size==end and tails.get(instruction.address)==instruction.operands[0].imm),(address,instruction.address,instruction.op_str)
 checked[address]={'instructions':len(code),'end':hex(end),'terminator':code[-1].mnemonic,'external_tail_calls':{hex(k):hex(v) for k,v in tails.items()}}
report={'result':'pass','routines_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':checked}
(p/'skater-local-net-extents.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(routines),'exact extents')
