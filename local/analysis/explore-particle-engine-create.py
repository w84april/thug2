"""Original-only effect creation exploration after real manager initialization."""
from pathlib import Path
source=Path('local/analysis/trace-particle-engine-training.py').read_text().split("print('Original43prop startup")[0]
source=source.replace('cpu.hook_add(UC_HOOK_CODE,stop_particle,begin=0x41db00,end=0x41db00)','')
import ast
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_text','write_bytes','unlink'] for n in ast.walk(ast.parse(source)))
exec(compile(source,'<preserved manager and training setup>','exec'))
def register_heap(cpu,at,size,user):
 heap=cpu.reg_read(UC_X86_REG_ECX);oracle.scope_entries[heap]=heap
cpu.hook_add(UC_HOOK_CODE,register_heap,begin=0x5ba520,end=0x5ba520)
entries=[];frame=False;boundary=None
def inspect(cpu,at,size,user):
 global boundary
 if not frame:return
 sp=cpu.reg_read(UC_X86_REG_ESP)
 record={'at':hex(at),'this':hex(cpu.reg_read(UC_X86_REG_ECX)),'args':[hex(oracle.word(sp+4+4*i)) for i in range(13)]}
 entries.append(record);print('EFFECT',record,flush=True)
 if at==0x5bb000:boundary=record;cpu.emu_stop()
for at in [0x41db00,0x49ac20,0x49ac60,0x4bcef0,0x5bb000,0x4c21a0,0x49b660,0x4d9b80]:cpu.hook_add(UC_HOOK_CODE,inspect,begin=at,end=at)
print('Original training startup with actual particle manager; next effect allocation boundary',flush=True)
steps=oracle.case(calls[:-1]);assert len(steps)==46
frame=True;fn,this,args=calls[-1];sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
error=None
try:cpu.emu_start(fn,oracle.stop,count=oracle.instruction_limit)
except Exception as e:error=repr(e)
report={'result':'original exploration stopped at explicit allocation boundary' if boundary else 'original exploration stopped','error':error,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'completed_startup_calls':len(steps),'entries':entries,'boundary':boundary,'recent_blocks':list(recent_blocks),'playable':False,'scope':'Original isolated instructions only. Real complete31prop startup and particle-manager constructor. No missing gameplay implementation or allocator result is substituted; stop before5bb000 allocation. This exploratory trace is not a recovered routine or browser comparison.'}
(folder/'particle-engine-create-exploration.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',report['result'],report['eip'],flush=True)
if error or not boundary:raise SystemExit(1)
