"""Verify each claimed complete routine's exact instruction and branch extent."""
import hashlib,json
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe')
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True
path=p/'walk-complete-update-routines.json';routines=json.loads(path.read_text());checked={}
for address,row in routines.items():
 start=int(address,16);end=start+row['bytes'];code=list(dis.disasm(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase,row['bytes']),start))
 assert len(code)==row['instructions'] and code[-1].address+code[-1].size==end and code[-1].mnemonic in ['ret','jmp'],address
 boundaries={i.address for i in code}
 for instruction in code:
  if instruction.group(capstone.CS_GRP_JUMP):
   if instruction.address==0x52d531:
    operand=instruction.operands[0];assert operand.type==capstone.x86.X86_OP_MEM and operand.mem.base==0 and operand.mem.index==capstone.x86.X86_REG_EAX and operand.mem.scale==4 and operand.mem.disp==0x52d680
    import struct
    targets=struct.unpack('<5I',pe.get_data(0x52d680-pe.OPTIONAL_HEADER.ImageBase,20));assert targets==(0x52d538,0x52d541,0x52d54a,0x52d553,0x52d55c) and set(targets)<=boundaries
    guard=[i for i in code if i.address in [0x52d52c,0x52d52f]];assert len(guard)==2 and guard[0].mnemonic=='cmp' and guard[0].op_str=='eax, 4' and guard[1].mnemonic=='ja' and guard[1].operands[0].imm==0x52d563
   else:
    assert instruction.operands[0].type==capstone.x86.X86_OP_IMM,(address,instruction.address)
    assert instruction.operands[0].imm in boundaries,(address,instruction.address,instruction.op_str)
 checked[address]={'instructions':len(code),'end':hex(end),'terminator':code[-1].mnemonic,'external_tail_calls':{}}
report={'result':'pass','routines_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':checked}
(p/'walk-complete-update-extents.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(routines),'exact extents')
