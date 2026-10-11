"""Exercise outer initialization and text configuration, stopping before4935e0.
No replacement configuration result is supplied to either original or Wasm.
"""
from pathlib import Path
source=Path('local/analysis/probe-model-initialize.py').read_text().split('for count,directional')[0]
exec(compile(source,'<preserved lighting and registry state>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
for off in range(0,24,4):glob('thug_model_texture_table_draft',0x700f04+off,0,offset=off)
from unicorn.x86_const import *
BOUNDARY=BASE+0x1f0000
for a,name,argc,result,heap in [(0x45e510,'thug_composite_initialize_draft',0,'word',False),
 (0x420bf0,'thug_model_component_construct_draft',0,'word',True),
 (0x45da30,'thug_composite_add_component_draft',1,'void',False),
 (0x493bd0,'thug_model_renderer_create_lights_draft',0,'byte',True),
 (0x492dd0,'thug_model_renderer_bind_skeleton_draft',1,'byte',False),
 (0x4214f0,'thug_model_initialize_prefix_draft',1,'void',False)]:bind(a,name,argc,result,heap)
prefix_hits=Counter();config_hits=Counter();active_model={}
def enter_configuration(cpu,at,size,user):
 active_model['component']=cpu.reg_read(UC_X86_REG_ECX);active_model['parameters']=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4)
def breakpoint_(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);args=[oracle.word(sp+4+i*4) for i in range(8)];path=bytearray();cursor=args[0]
 while cpu.mem_read(cursor,1)[0]:path.extend(cpu.mem_read(cursor,1));cursor+=1;assert len(path)<512
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,active_model['parameters'],active_model['component'],1))
 cpu.mem_write(BOUNDARY+16,struct.pack('<8I',cpu.reg_read(UC_X86_REG_ECX),args[1],args[2]&255,args[3],args[4]&255,args[5],args[6]&255,args[7]&255))
 cpu.mem_write(BOUNDARY+48,struct.pack('<I',len(path)));cpu.mem_write(BOUNDARY+64,bytes(path)+b'\0');cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,enter_configuration,begin=0x420d10,end=0x420d10)
oracle.cpu.hook_add(UC_HOOK_CODE,breakpoint_,begin=0x4935e0,end=0x4935e0)
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:prefix_hits.update([at]),begin=0x4214f0,end=0x4215e0)
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:config_hits.update([at]),begin=0x420d10,end=0x421227)
for requested,existing,skeleton_mode,flag in itertools.product([False,True],[False,True],['absent','new','bound'],[None,0,0x80000000]):
 g=LightGraph();items=[]
 if requested:items.append((0,13,0x10079f2d))
 enabled=[None,0,0x12345678][len(labels)%3]
 if enabled is not None:items.append((0xd223b8bd,1,enabled))
 if flag is not None:items.append((0x2a1f92c0,1,flag))
 serial=len(labels);mode=serial%4
 text=g.text(['gameobjects/skate/letter_s/letter_s.mdl','Letter_S','GameObjects\\SKATE\\S','MiXeD'][mode])
 if mode==1:items += [(0x286a8d26,1,0),(0xb974f2fc,3,text)]
 elif mode==2:items += [(0x286a8d26,4,text),(0xb974f2fc,3,g.text('ignored'))]
 elif mode==3:
  included=g.structure([(0x286a8d26,3,text)]);g.symbol(0x12312312,10,included);items.append((0,13,0x12312312))
 else:items.append((0x286a8d26,3,text))
 assets=[None,0,0x100,1][mode]
 if assets is not None:items.append((0xc63c8d38,1,assets))
 items.append((0xf891ac27,1,[0,0xffffffff,0x100,123][mode]))
 if serial%3:items.append((0x09794932,13,0 if serial%3==1 else 0x1234))
 if serial%2:items.append((0,13,0x6c37fdc7))
 if mode==1:items.append((0x13b9da7b,2,bits(2.5)))
 elif mode==2:items.append((0x13b9da7b,6,g.vector([bits(1),bits(2),bits(3)])))
 elif mode==3:items.append((0x0424d9ea,2,bits(-2)))
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
 cpu.emu_start(0x4214f0,oracle.stop,count=500000)
 assert cpu.reg_read(UC_X86_REG_EIP)==0x4935e0 and oracle.word(BOUNDARY+8)==P
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={e[0] for e in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x4214f0','this':P,'args':[params],'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_model_initialize_prefix_draft']+=1
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x4935e0,
 'native_callbacks':[{'module':'model-configuration-prefix-boundary.wasm','export':'fixture_model_load','original':0x4935e0}],
 'pointer_initializers':[['thug_model_load_pending_draft',0x4935e0,0]]}
scope='Thirty-six controlled cases combine all outer initializer routes with text-model configuration. Actual reset/scale parsing and source selection prepare loader arguments and paths, covering scalar/vector/axis scale, primary/localized/fallback/included text, optional skeleton extension, full-word asset and option flags and path lowercase. Every case traps before4935e0; no asset or success result is supplied. All arena bytes/globals/heap effects compare exactly. Only the text path of420d10 is implemented; alternate source branches and post-load tail remain unavailable. Neither4214f0 nor420d10 is complete or counted as a recovered function. No rendering or playable level.'
finish('model-configuration-prefix',scope,{},extra)
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4214f0-0x400000,241),0x4214f0))
report_path=folder/'model-configuration-prefix-original.json';report=json.loads(report_path.read_text())
report['partial_initializer']={'address':'0x4214f0','covered_instructions':sum(bool(prefix_hits[i.address]) for i in code),'total_instructions':len(code),'not_reached':[hex(i.address) for i in code if not prefix_hits[i.address]],'boundary':'0x4935e0','interrupted_calls':len(labels)}
config_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x20d10,1304),0x420d10))
report['partial_configuration']={'address':'0x420d10','boundary':'0x4935e0','covered_instructions':sum(bool(config_hits[i.address]) for i in config_code),'total_instructions':len(config_code),'executed':[hex(i.address) for i in config_code if config_hits[i.address]],'complete':False}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['partial_initializer']),flush=True)
