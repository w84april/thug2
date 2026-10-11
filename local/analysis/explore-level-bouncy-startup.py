"""Read original bouncing-prop startup in the established isolated comparison VM.
No instructions are replaced; only the already documented platform ports apply.
This produces exploration evidence, not a claim of recovered Wasm behavior.
"""
from pathlib import Path
source=Path('local/analysis/trace-level-collision-component.py').read_text().split("f=json.loads((folder/'level-collision-load-fixtures.json')")[0]
assert '.write_text(' not in source and "function_exports += [[0x41c920" in source
exec(compile(source,'<preserved original whole scene comparison setup>','exec'))
# The game registration at004e4bbf names this actual type and factory.
count=int.from_bytes(memory[OBJECTS+0x44-BASE:OBJECTS+0x48-BASE],'little')
assert count==10
put(OBJECTS+0x44,'<I',count+1);put(OBJECTS+0x48+count*8,'<2I',0xffb39248,0x42ef00)
oracle.initial=initial=bytes(memory)
old=json.loads((folder/'level-collision-component-fixtures.json').read_text())['cases'][0]['steps']
all_nodes=json.loads((folder/'level-collision-load-trace.json').read_text())['all_startup']
bouncing=[n for n in all_nodes if n['alternate']];assert len(bouncing)==19
calls=[(int(s['fn'],16),s['this'],s['args']) for s in old]+[(0x5a4ff0,0,[n['node'],SCRIPT]) for n in bouncing]
executed=Counter();entries=[]
def rigid_trace(cpu,at,size,user):
 executed[at]+=1
 if at in [0x42ef00,0x42e3f0,0x42f050,0x42bd90,0x430e20]:
  this=cpu.reg_read(UC_X86_REG_ECX);entries.append({'address':hex(at),'this':hex(this)})
  print('Rigid entry',hex(at),hex(this),flush=True)
cpu.hook_add(UC_HOOK_CODE,rigid_trace,begin=0x42bb00,end=0x431100)
error=None;steps=[]
try:
 steps=oracle.case(calls)
 assert len(steps)==43 and not factory_hit and len(created)==31
except Exception as exc:
 error=repr(exc);print('ORIGINAL STOP',error,'at',hex(cpu.reg_read(UC_X86_REG_EIP)),flush=True)
objects=[]
for obj in created:
 chain=[];c=oracle.word(obj+0x100)
 while c:
  assert len(chain)<20;chain.append({'address':hex(c),'type':hex(oracle.word(c+4))});c=oracle.word(c+16)
 objects.append({'object':hex(obj),'name':hex(oracle.word(obj+0x14)),'flags':hex(oracle.word(obj+0x104)),'components':chain})
report={'result':'original exploration complete' if error is None else 'original exploration stopped','error':error,'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'specimen_sha256':SHA256,'completed_calls':len(steps),'created_objects':objects,'rigid_entries':entries,'executed_rigid_instructions':{hex(k):v for k,v in sorted(executed.items())},'recent_blocks':list(recent_blocks),'heap_events':oracle.word(CONTEXT+8),'playable':False,'scope':'Original isolated execution only; no recovered implementation or Wasm claim. Existing file/GPU comparison ports and explicit initialized heap/registries.'}
(folder/'level-bouncy-startup-exploration.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED exploration',report['result'],'objects',len(objects),'rigid instructions',len(executed),flush=True)
if error:raise SystemExit(1)
