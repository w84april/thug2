"""Original-only discovery of the complete composite-manager update frontier."""
from pathlib import Path
source=Path('local/analysis/trace-particle-dispatch-training.py').read_text().split("scope='Actual complete31prop")[0]
exec(compile(source,'<verified training setup and two complete object updates>','exec'))
from collections import deque
recent=deque(maxlen=48);objects=[]
def frame_recent(cpu,at,size,user):recent.append(at)
def object_entry(cpu,at,size,user):objects.append(cpu.reg_read(UC_X86_REG_ECX))
cpu.hook_add(UC_HOOK_CODE,frame_recent,begin=0x400000,end=0x680000)
cpu.hook_add(UC_HOOK_CODE,object_entry,begin=0x45d920,end=0x45d920)
boundary_hits.clear();sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJECTS);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
error=None
try:cpu.emu_start(0x45f4a0,oracle.stop,count=oracle.instruction_limit)
except Exception as e:error=str(e)
sp=cpu.reg_read(UC_X86_REG_ESP)
report={'result':'failed' if error else 'returned' if cpu.reg_read(UC_X86_REG_EIP)==oracle.stop else 'stopped','error':error,'entry':'0x45f4a0','manager':OBJECTS,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'object_update_entries':objects,'object_names':[hex(oracle.word(o+0x14)) for o in objects],'boundaries':list(map(hex,boundary_hits)),'boundary_record':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),'recent':list(map(hex,recent)),'stack':[hex(oracle.word(sp+i)) for i in range(0,32,4)],'scope':'Original-only composite-manager update discovery after verified training startup and the selected barrel/fire updates. No recovered manager or complete game-frame claim.'}
(folder/'particle-dispatch-next-frame.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
