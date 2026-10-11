"""Exercise every outer initializer branch, stopping before real420d10.
No replacement configuration result is supplied to either original or Wasm.
"""
from pathlib import Path
source=Path('local/analysis/probe-model-initialize.py').read_text().split('for count,directional')[0]
exec(compile(source,'<preserved lighting and registry state>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
from unicorn.x86_const import *
BOUNDARY=BASE+0x1f0000
for a,name,argc,result,heap in [(0x45e510,'thug_composite_initialize_draft',0,'word',False),
 (0x420bf0,'thug_model_component_construct_draft',0,'word',True),
 (0x45da30,'thug_composite_add_component_draft',1,'void',False),
 (0x493bd0,'thug_model_renderer_create_lights_draft',0,'byte',True),
 (0x492dd0,'thug_model_renderer_bind_skeleton_draft',1,'byte',False),
 (0x4214f0,'thug_model_initialize_prefix_draft',1,'void',False)]:bind(a,name,argc,result,heap)
prefix_hits=Counter()
def breakpoint_(cpu,at,size,user):
 params=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);receiver=cpu.reg_read(UC_X86_REG_ECX)
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,receiver,1));cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,breakpoint_,begin=0x420d10,end=0x420d10)
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:prefix_hits.update([at]),begin=0x4214f0,end=0x4215e0)
for requested,existing,skeleton_mode,flag in itertools.product([False,True],[False,True],['absent','new','bound'],[None,0,0x80000000]):
 g=LightGraph();items=[]
 if requested:items.append((0,13,0x10079f2d))
 enabled=[None,0,0x12345678][len(labels)%3]
 if enabled is not None:items.append((0xd223b8bd,1,enabled))
 if flag is not None:items.append((0x2a1f92c0,1,flag))
 params=g.structure(items)
 calls=[call(0x45e510,OBJ),call(0x420bf0,P),call(0x45da30,OBJ,[P])]
 if skeleton_mode!='absent':
  skeleton=g.component(0x222756d5);data=g.alloc(16);g.put(data+4,'<2I',0x12345678,0x76543210);g.put(skeleton+0x18,'<I',data)
  calls.append(call(0x45da30,OBJ,[skeleton]))
  if skeleton_mode=='bound':
   first=g.alloc(16);g.put(first+4,'<2I',0x11223344,0x55667788);calls.append(call(0x492dd0,HEAP,[first]))
 if existing:calls.append(call(0x493bd0,HEAP))
 stages=case(calls,g.patches(),{0x6faae0:3,0x6faae4:2},f'initializer lights{requested}/existing{existing}/skeleton{skeleton_mode}/flag{flag}/key{enabled}')
 assert oracle.word(P+0x208)==HEAP
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 cpu.mem_write(sp,struct.pack('<2I',oracle.stop,params));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,P);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 cpu.emu_start(0x4214f0,oracle.stop,count=100000)
 assert cpu.reg_read(UC_X86_REG_EIP)==0x420d10 and oracle.word(BOUNDARY+8)==P
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={e[0] for e in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x4214f0','this':P,'args':[params],'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_model_initialize_prefix_draft']+=1
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x420d10,
 'native_callbacks':[{'module':'model-initialize-prefix-boundary.wasm','export':'fixture_configure','original':0x420d10}],
 'pointer_initializers':[['thug_model_configuration_pending_draft',0x420d10,0]]}
scope='Controlled Model initializer inputs execute actual model/renderer/light construction, optional lighting creation/retention/removal, position/key assignment, absent/new/already-bound skeleton routes and full-word optional renderer flags. Every case stops before420d10 configuration/loading, with no replacement return. All arena bytes, globals and heap effects compare through that boundary. No complete Model initialization, model asset load or rendering is claimed.'
finish('model-initialize-prefix',scope,{},extra)
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4214f0-0x400000,241),0x4214f0))
report_path=folder/'model-initialize-prefix-original.json';report=json.loads(report_path.read_text())
report['partial_initializer']={'address':'0x4214f0','covered_instructions':sum(bool(prefix_hits[i.address]) for i in code),'total_instructions':len(code),'not_reached':[hex(i.address) for i in code if not prefix_hits[i.address]],'boundary':'0x420d10','interrupted_calls':len(labels)}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['partial_initializer']),flush=True)
