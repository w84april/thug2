"""Bounded evidence for the original reset loop; never run this path in browser."""
import json,struct,subprocess,hashlib
from pathlib import Path
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_ECX,UC_X86_REG_ESI
from specimen import load,SHA256,ROOT
BASE,STACK,STOP=0x1800000,0x3000000,0x3f00000
pe=load();results=[]
for entry,loop in [(0x554030,0x554045),(0x554070,0x5540c0)]:
 cpu=Uc(UC_ARCH_X86,UC_MODE_32)
 for at,size in [(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095),(BASE,0x10000),(STACK,0x10000),(STOP,0x1000)]:cpu.mem_map(at,size)
 cpu.mem_write(0x400000,pe.get_memory_mapped_image())
 def put(at,fmt,*values):cpu.mem_write(at,struct.pack(fmt,*values))
 root,flat,group,nodes=BASE,BASE+0x100,BASE+0x200,BASE+0x300
 put(flat,'<II',0,nodes)
 for i,name in enumerate([0x11111111,0xb3790f33,0x22222222]):put(nodes+i*16,'<BBHIII',2,0,0,name,7+i*2,nodes+(i+1)*16 if i<2 else 0)
 put(group,'<II',0,BASE+0x400)
 put(BASE+0x400,'<BBHIII',26,0,0,0,0xe462e527,BASE+0x410)
 put(BASE+0x410,'<BBHIII',20,0,0,1,flat,0)
 put(root+0x20,'<I',group)
 sp=STACK+0x8000;put(sp,'<II',STOP,flat);cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,root)
 visits=[]
 def observe(cpu,address,size,user):visits.append(cpu.reg_read(UC_X86_REG_ESI))
 cpu.hook_add(UC_HOOK_CODE,observe,begin=loop,end=loop)
 cpu.emu_start(entry,STOP,count=1000)
 values=[struct.unpack('<I',cpu.mem_read(nodes+i*16+8,4))[0] for i in range(3)]
 assert cpu.reg_read(UC_X86_REG_EIP)!=STOP and values==[0,9,11]
 assert visits[0]==nodes and len(visits)>20 and set(visits[1:])=={nodes+16}
 results.append({'function':hex(entry),'loop':hex(loop),'visits':dict((hex(k),v) for k,v in Counter(visits).items()),'member_values_after_budget':values,'stopped_at':hex(cpu.reg_read(UC_X86_REG_EIP)),'instruction_budget':1000})
report={'specimen_sha256':SHA256,'result':'confirmed repeated same-member cycle after bounded original execution','functions':results,'scope':'Both original reset loops skip the next-member assignment for name b3790f33. The earlier value is zeroed; this reserved member and following member retain their values. The recovered source retains this nonterminating path.'}
out=ROOT/'local/validation/collision'
subprocess.run(['node',str(ROOT/'tools/verify_objective_reset_loop_wasm.mjs'),str(out)],check=True)
report['wasm_observations']=json.loads((out.parent/'objective-reset-loop-wasm.json').read_text())
report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'tools/verify_objective_reset_loop.py',ROOT/'tools/verify_objective_reset_loop_wasm.mjs',out/'script-values-memory.wasm',out.parent/'objective-reset-loop-wasm.json']}
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
(out.parent/'objective-reset-loop.json').write_text(json.dumps(report,indent=2)+'\n')
print('Original bounded reset loops:',results)
