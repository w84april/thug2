"""Verify each claimed complete routine's exact instruction and branch extent."""
import hashlib,json,struct
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe')
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True
path=p/'walk-common-routines.json';routines=json.loads(path.read_text());checked={}
for address,row in routines.items():
 start=int(address,16);end=start+row['bytes'];code=list(dis.disasm(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase,row['bytes']),start))
 assert len(code)==row['instructions'] and code[-1].address+code[-1].size==end and code[-1].mnemonic in ['ret','jmp'],address
 boundaries={i.address for i in code}
 indirect={}
 for instruction in code:
  if instruction.group(capstone.CS_GRP_JUMP):
   operand=instruction.operands[0]
   if operand.type==capstone.x86.X86_OP_IMM:
    assert operand.imm in boundaries,(address,instruction.address,instruction.op_str)
   else:
    assert start==0x529ce0 and instruction.mnemonic=='jmp' and operand.type==capstone.x86.X86_OP_MEM
    assert (operand.mem.base,operand.mem.index,operand.mem.scale,operand.mem.disp)==(0,capstone.x86.X86_REG_EAX,4,0x529f64)
    # Prior unsigned check bounds state to0..3 before this indexed dispatch.
    previous=code[code.index(instruction)-2:code.index(instruction)]
    assert [(i.mnemonic,i.op_str) for i in previous]==[('cmp','eax, 3'),('ja','0x529efb')]
    targets=struct.unpack('<4I',pe.get_data(0x529f64-pe.OPTIONAL_HEADER.ImageBase,16))
    assert targets==(0x529e6a,0x529e6a,0x529e97,0x529ee6) and set(targets)<=boundaries
    indirect[hex(instruction.address)]={'table':hex(0x529f64),'targets':[hex(x) for x in targets],'bounded_states':[0,3]}
 checked[address]={'instructions':len(code),'end':hex(end),'terminator':code[-1].mnemonic,'external_tail_calls':{},'indirect_jumps':indirect}
report={'result':'pass','routines_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':checked}
(p/'walk-common-extents.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checked),'exact routine extents')
