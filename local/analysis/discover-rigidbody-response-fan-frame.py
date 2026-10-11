"""Observe a full original scene update, allowing original Rigidbody execution."""
from pathlib import Path
source=Path('local/analysis/trace-particle-dispatch-training.py').read_text().split("scope='Actual complete31prop")[0]
needle='cpu.hook_add(UC_HOOK_CODE,stop_motion,begin=0x430e20,end=0x430e20)'
assert source.count(needle)==1
source=source.replace(needle,'# Original Rigidbody is allowed in this discovery only.')
exec(compile(source,'<unchanged verified startup and selected updates>','exec'))
from collections import deque,Counter
recent=deque(maxlen=64);objects=[];rigid=[];calls_seen=Counter()
def observe(cpu,at,size,user):recent.append(at)
def object_entry(cpu,at,size,user):objects.append(cpu.reg_read(UC_X86_REG_ECX))
def rigid_entry(cpu,at,size,user):
 p=cpu.reg_read(UC_X86_REG_ECX);rigid.append({'component':p,'owner':oracle.word(p+12),'mode':oracle.word(p+0x10c),'contacts':int.from_bytes(cpu.mem_read(p+0x9c,2),'little')})
def dependency(cpu,at,size,user):calls_seen[hex(at)]+=1
cpu.hook_add(UC_HOOK_CODE,observe,begin=0x400000,end=0x680000)
cpu.hook_add(UC_HOOK_CODE,object_entry,begin=0x45d920,end=0x45d920)
cpu.hook_add(UC_HOOK_CODE,rigid_entry,begin=0x430e20,end=0x430e20)
for at in [0x42c140,0x42c950,0x430140,0x430be0,0x42cf90,0x42e980,0x42d9d0]:cpu.hook_add(UC_HOOK_CODE,dependency,begin=at,end=at)
diagnostics=[]
def diagnostic(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);args=[oracle.word(sp+4+i*4) for i in range(8)];strings=[]
 for address in args:
  try:
   raw=bytes(cpu.mem_read(address,512)).split(b'\0')[0];strings.append(raw.decode('latin1') if raw and all(v in [9,10,13] or 32<=v<127 for v in raw) else None)
  except Exception:strings.append(None)
 diagnostics.append({'args':[hex(x) for x in args],'strings':strings})
cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
fan=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
assert hashlib.sha256(bytes(cpu.mem_read(fan['address'],fan['size']))).hexdigest()=='21c9f93830a0a740bc41e13d81e4ec47adf8e7b33f52235a990ca45231807f87'
sp=oracle.stack+0x18000;cpu.mem_write(sp,struct.pack('<6I',oracle.stop,fan['filename'],fan['address'],0,1,0));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,0)
cpu.emu_start(0x472420,oracle.stop,count=oracle.instruction_limit)
assert cpu.reg_read(UC_X86_REG_EIP)==oracle.stop,hex(cpu.reg_read(UC_X86_REG_EIP))
print('ARCHIVED LEVEL SCRIPTS LOADED',flush=True)
boundary_hits.clear();sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJECTS);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
error=None
try:cpu.emu_start(0x45f4a0,oracle.stop,count=oracle.instruction_limit)
except Exception as e:error=str(e)
sp=cpu.reg_read(UC_X86_REG_ESP)
report={'result':'failed' if error else 'returned' if cpu.reg_read(UC_X86_REG_EIP)==oracle.stop else 'stopped','error':error,'entry':'0x45f4a0','manager':OBJECTS,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'object_update_entries':objects,'object_names':[hex(oracle.word(o+0x14)) for o in objects],'rigidbody_updates':rigid,'diagnostics':diagnostics,'dependency_calls':dict(calls_seen),'boundaries':list(map(hex,boundary_hits)),'recent':list(map(hex,recent)),'stack':[hex(oracle.word(sp+i)) for i in range(0,32,4)],'loaded_level_scripts':fan['member'],'scope':'Original-only composite-manager discovery after training startup, selected barrel/fire updates and loading archived TR_scripts.qb. Unrecovered Rigidbody code is executed in the isolated original emulator, never replaced. No Wasm/full playable-frame claim.','playable':False}
(folder/'rigidbody-response-fan-frame.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
