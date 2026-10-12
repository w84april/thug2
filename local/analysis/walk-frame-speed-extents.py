"""Verify each claimed complete routine's exact instruction and branch extent."""
import hashlib,json
from pathlib import Path
import capstone,pefile
p=Path('local/analysis');exe=Path('local/discs/cd3/Crack/THUG2.exe')
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3'
pe=pefile.PE(str(exe));dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.detail=True
path=p/'walk-frame-speed-routines.json';routines=json.loads(path.read_text());checked={}
for address,row in routines.items():
 start=int(address,16);end=start+row['bytes'];code=list(dis.disasm(pe.get_data(start-pe.OPTIONAL_HEADER.ImageBase,row['bytes']),start))
 assert len(code)==row['instructions'] and code[-1].address+code[-1].size==end and code[-1].mnemonic in ['ret','jmp'],address
 boundaries={i.address for i in code}
 for instruction in code:
  if instruction.group(capstone.CS_GRP_JUMP):
   assert instruction.operands[0].type==capstone.x86.X86_OP_IMM,(address,instruction.address)
   assert instruction.operands[0].imm in boundaries,(address,instruction.address,instruction.op_str)
 checked[address]={'instructions':len(code),'end':hex(end),'terminator':code[-1].mnemonic,'external_tail_calls':{}}
frame=list(dis.disasm(pe.get_data(0x52d4b0-pe.OPTIONAL_HEADER.ImageBase,463),0x52d4b0))
assert len(frame)==142 and frame[-1].address==0x52d67e and frame[-1].mnemonic=='ret'
frame_boundaries={i.address for i in frame};jump=next(i for i in frame if i.address==0x52d531)
assert jump.mnemonic=='jmp' and jump.operands[0].type==capstone.x86.X86_OP_MEM
assert jump.operands[0].mem.disp==0x52d680 and jump.operands[0].mem.scale==4
import struct
entries=struct.unpack('<5I',pe.get_data(0x52d680-pe.OPTIONAL_HEADER.ImageBase,20))
assert entries==(0x52d538,0x52d541,0x52d54a,0x52d553,0x52d55c)
for instruction in frame:
 if instruction.group(capstone.CS_GRP_JUMP) and instruction.address!=0x52d531:
  assert instruction.operands[0].type==capstone.x86.X86_OP_IMM and instruction.operands[0].imm in frame_boundaries
report={'result':'pass','routines_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checked':checked,'partial_frame':{'address':'0x52d4b0','bytes':463,'instructions':142,'jump_table':[hex(x) for x in entries],'recovered_routine':False}}
(p/'walk-frame-speed-extents.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(checked),'exact routine extents')
