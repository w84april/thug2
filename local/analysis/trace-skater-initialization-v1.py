"""Read-only original startup trace, stopping before the next unverified callee.

Existing immutable setup is reused without rerunning any pinned builder/output.
No game return is fabricated. This trace earns no completion credit.
"""
from pathlib import Path
source=Path('local/analysis/probe-skater-full-startup.py').read_text().split('records=[]')[0]
old="source=Path('local/analysis/probe-skater-final-startup.py').read_text().split('# Final complete startup cases.')[0]"
new=old+"\nsource='\\n'.join(line for line in source.splitlines() if not line.startswith(\"port=folder/'skater-final-startup-ports.c'\"))"
assert old in source
source=source.replace(old,new)
exec(compile(source,'<immutable startup setup, builders omitted>','exec'))
import capstone
from unicorn.x86_const import UC_X86_REG_EBX,UC_X86_REG_EBP,UC_X86_REG_ESI,UC_X86_REG_EDI
ledger=json.loads(Path('progress/ledger.json').read_text())
accepted={int(r['address'],16) for r in ledger['records']}
native={0x5bbae0,0x5bafc0,0x5ba0b0,0x5baba0,0x5bb0e0,0x5bb110,0x401c30,0x5b9e60,0x5b9ee0,0x5b9ea0,*PORTS}
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
state={'active':False,'pending':None};visits=Counter();edges=[];boundary=[]
def trace(cpu,at,size,user):
 if not state['active']:return
 if state['pending'] is not None:
  caller=state['pending'];state['pending']=None
  edge={'caller':hex(caller),'callee':hex(at),'accepted':at in accepted,'platform_boundary':at in native}
  edges.append(edge)
  if at not in accepted|native:
   sp=cpu.reg_read(UC_X86_REG_ESP)
   boundary.append({**edge,'this':cpu.reg_read(UC_X86_REG_ECX),'stack_words':[oracle.word(sp+4*i) for i in range(5)]})
   cpu.emu_stop();return
 if cpu.reg_read(UC_X86_REG_EIP)!=at:return
 if 0x581850<=at<0x582280:visits[at]+=1
 instruction=next(md.disasm(bytes(cpu.mem_read(at,size)),at),None)
 if instruction is not None and instruction.mnemonic=='call':state['pending']=at
oracle.cpu.hook_add(UC_HOOK_CODE,trace)
records=[]
for local,controller,existing in [(0,0,False),(0,1,False),(1,0,False),(1,1,True)]:
 state.update(active=False,pending=None);visits.clear();edges.clear();boundary.clear()
 g=FinalGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry(registry)
 profile=g.alloc(0x100)
 if existing:
  camera=g.alloc(0x110);component=g.component(0x5e43a604);next_component=g.component(0xc7d37ec2)
  g.put(component+16,'<I',next_component);g.put(camera+0x100,'<I',component)
  g.put(EM+8,'<I',g.table([(0xe17b231a,camera)]))
 stages=g.run([call(0x582d90,OBJ,[controller,MANAGER,local,0,0,1])],f'completed constructor before actual initialization/{local}/{controller}/{existing}')
 assert stages[0]['result']==OBJ
 cpu=oracle.cpu;sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<2I',oracle.stop,profile));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 state.update(active=True,pending=None);error=None
 try:cpu.emu_start(0x581850,oracle.stop,count=500000)
 except Exception as e:error=str(e)
 state['active']=False
 records.append({'local':local,'controller':controller,'existing_camera':existing,'completed_constructor':True,'initialization_returned':cpu.reg_read(UC_X86_REG_EIP)==oracle.stop,'stopped_at':hex(cpu.reg_read(UC_X86_REG_EIP)),'boundary':list(boundary),'calls':list(edges),'visited_initializer_instructions':len(visits),'instruction_addresses':[hex(x) for x in sorted(visits)],'error':error,'completion_credit':0})
 print(json.dumps({k:records[-1][k] for k in ['local','controller','existing_camera','stopped_at','boundary','visited_initializer_instructions','error']}),flush=True)
target=Path('local/analysis/skater-initialization-v1-trace.json');assert not target.exists()
target.write_text(json.dumps({'specimen_sha256':ledger['specimen_sha256'],'result':'discovery only; no completion claim','records':records,'no_game_callee_substitution':True,'pinned_builders_omitted':True},indent=2)+'\n')
