"""Original-only exploration beyond the verified flame material/reference boundary."""
from pathlib import Path
source=Path('local/analysis/trace-particle-image-training.py').read_text().split("print('Original43prop startup")[0]
source=source.replace('cpu.hook_add(UC_HOOK_CODE,stop_particle,begin=0x41dd49,end=0x41dd49)','')
import ast
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_text','write_bytes','unlink'] for n in ast.walk(ast.parse(source)))
exec(compile(source,'<preserved real training texture and particle setup>','exec'))
entries=[];active=False

def trace_next(cpu,at,size,user):
 if not active:return
 sp=cpu.reg_read(UC_X86_REG_ESP);record={'at':hex(at),'this':hex(cpu.reg_read(UC_X86_REG_ECX)),'args':[hex(oracle.word(sp+4+4*i)) for i in range(4)]};entries.append(record);print('NEXT',record,flush=True)
for at in [0x41dd49,0x497790,0x497900,0x41df68,0x41d740,0x41df80]:cpu.hook_add(UC_HOOK_CODE,trace_next,begin=at,end=at)
print('Original full startup and real texture load before exploring remaining initializer',flush=True)
steps=oracle.case(calls[:-1]);assert len(steps)==48
active=True;fn,this,args=calls[-1];sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
error=None
try:cpu.emu_start(fn,oracle.stop,count=oracle.instruction_limit)
except Exception as e:error=repr(e)
complete=cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
report={'result':'original barrel owner update completed' if complete else 'original stopped beyond initializer boundary','error':error,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'startup_calls':len(steps),'entries':entries,'initializer_parameters':initializer_args,'effect_entries':point_entries,'heap_events':oracle.word(CONTEXT+8),'heap_end':hex(oracle.word(CONTEXT)),'recent_blocks':list(recent_blocks),'playable':False,'scope':'Original isolated instructions only. Real training scene, shared particle dictionary and original load_level_particle_textures script. No missing initializer or script behavior is supplied. This exploration is not a Wasm comparison or playable game.'}
(folder/'particle-image-frame-exploration.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',report['result'],report['eip'],flush=True)
if error:raise SystemExit(1)
