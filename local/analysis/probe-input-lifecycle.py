"""Original Input startup and intrusive tasks, with DirectInput only at COM boundary."""
from pathlib import Path
source=Path('local/analysis/probe-input-callbacks.py').read_text().split('for source in [False,True]:')[0]
exec(compile(source,'<preserved Input/event oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[
 (0x406850,16,'task_linked',0,'byte',False,False,True),
 (0x4069b0,5,'task_list_changed',0,'void',False,False,True),
 (0x4068f0,61,'task_unlink',0,'void',False,False,True),
 (0x406a00,31,'task_node_destroy',0,'void',False,False,True),
 (0x406860,33,'task_node_delete',1,'word',True,False,True),
 (0x406930,80,'task_base_destroy',0,'void',True,False,True),
 (0x406980,33,'task_base_delete',1,'word',True,False,True),
 (0x406a50,38,'task_list_construct',0,'word',False,False,True),
 (0x406a80,49,'task_list_add',1,'void',False,False,True),
 (0x406c90,8,'task_wrapper_add',1,'void',False,False,True),
 (0x406ac0,226,'task_list_update',2,'void',True,True,True),
 (0x406bb0,114,'task_list_clear',0,'void',False,False,True),
 (0x577270,6,'input_task_execute',0,'void',True,True,True),
 (0x577280,11,'input_task_destroy',0,'void',True,False,True),
 (0x536670,33,'input_task_delete',1,'word',True,False,True),
 (0x5ba1d0,3,'task_zero',0,'word',False,False,True),
 (0x5f3a50,411,'input_set_actuators',3,'void',False,False,False),
 (0x5bccb0,8,'input_device_enable_vibration',0,'void',False,False,True),
 (0x5bdad0,88,'input_device_disable_vibration',0,'void',False,False,True),
 (0x43d5c0,32,'vibration_bind_device',1,'void',False,False,True),
 (0x41f1b0,472,'input_bind_device',1,'void',True,False,True),
 (0x41f390,110,'input_initialize',1,'void',True,False,True),
 (0x41e850,112,'input_construct',0,'word',False,False,True),
 (0x41eec0,89,'input_create',0,'word',True,False,False),
 (0x41e710,168,'input_destroy',0,'void',True,False,True),
 (0x41e8c0,33,'input_delete',1,'word',True,False,True),
 (0x41e7c0,14,'input_enable_events',2,'word',False,False,True),
 (0x41e7d0,15,'input_disable_events',2,'word',False,False,True)]
for at,size,name,*rest in specs:bind_new(at,size,'thug_'+name+'_draft',*rest)
bind(0x406890,'thug_task_base_construct_draft',1,'word',True)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
bind(0x45ee20,'thug_composite_add_parameters_draft',2,heap=True,diag=True)
bind(0x45db30,'thug_composite_finalize_draft',0,heap=True,diag=True)
bind(0x45d890,'thug_composite_destroy_draft',0,heap=True,diag=True)
bind(0x461930,'thug_ui_object_set_id',1,heap=True)
bind(0x45d920,'thug_object_update_components',0,heap=True,diag=True)
MGR,L0,L1,D0,D1,E0,E1,EVT,OSLOG,TVT=[BASE+x for x in [0xc2000,0xc3000,0xc3100,0xc4000,0xc4200,0xc5000,0xc5010,0xc5100,0xc6000,0xc8000]]
for name,at,value in [('thug_input_device_manager_draft',0x696d40,MGR)]:global_default(name,at,value)
for name,at,values in [('thug_input_effects_draft',0x7d6668,[0,0]),('thug_input_effect_axes_draft',0x7d42c8,[2,2]),
 ('thug_input_effect_scales_draft',0x7d42d0,[10000]*4)]:
 for i,value in enumerate(values):glob(name,at+4*i,value,offset=4*i)
for at,name in [(0x64548c,'thug_task_base_methods_draft'),(0x64549c,'thug_task_node_methods_draft'),
 (0x646090,'thug_input_task_base_methods_draft'),(0x64d7d8,'thug_input_task_methods_draft'),(0x64605c,'thug_input_methods_draft')]:
 if not any(row[0]==at for row in exports):exports.append([at,name])
function_exports.extend([[0x41f170,'thug_input_primary_task_bridge_draft'],[0x41f190,'thug_input_secondary_task_bridge_draft'],
 [0x41eec0,'thug_input_create_draft'],[0x4068f0,'thug_task_unlink_frame_bridge_draft']])
put(ALLOCATOR+0x5d4,'<I',ALLOCATOR+0x208);oracle.scope_entries[ALLOCATOR+0x208]=8
STOP,SET=oracle.stop+0x300,oracle.stop+0x310
def hardware(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);effect=oracle.word(sp+4);context=oracle.word(effect+4)
 count=oracle.word(context);row=context+16+count*96;oracle.setword(context,count+1)
 values=[0]*24;values[:3]=[1 if at==STOP else 2,effect,0 if at==STOP else oracle.word(sp+12)]
 if at==SET:
  p=oracle.word(sp+8);descriptor=[oracle.word(p+4*i) for i in range(14)]
  values[3:17]=descriptor;values[12]=values[15]=0
  values[17:19]=[oracle.word(descriptor[9]),oracle.word(descriptor[9]+4)]
  values[19]=oracle.word(descriptor[12])
 cpu.mem_write(row,struct.pack('<24I',*values));cpu.reg_write(UC_X86_REG_EAX,0x80004005)
 cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+(8 if at==STOP else 16))
for at in [STOP,SET]:oracle.cpu.hook_add(UC_HOOK_CODE,hardware,begin=at,end=at)
extra['native_callbacks']=[{'module':'input-lifecycle-hardware-fixture.wasm','export':name,'slots':[slot]}
 for name,slot in [('fixture_input_effect_stop',EVT+0x20),('fixture_input_effect_set',EVT+0x18)]]
initial=bytes(memory);oracle.initial=initial
class LifecycleGraph(InputGraph):
 def __init__(self,fill=0):
  super().__init__(fill);self.image[MGR-BASE:BASE+0xc9000-BASE]=bytes(0x7000)
  self.put(P+0x490,'<2I',0,0);self.put(OBJ+0x100,'<I',0)
  for i,(d,l,e) in enumerate([(D0,L0,E0),(D1,L1,E1)]):
   self.put(MGR+0x84*i+4,'<I',d);self.put(MGR+0x84*i+0x3c,'<I',l)
   self.packet(MGR+0x84*i+0x44,[(6+4*i,255)],axes=(255-127*i,128,128,128))
   self.put(MGR+0x110+4*i,'<I',1-i);self.put(d+0xc,'<I',i)
   self.put(d+0xc4,'<I',2);self.put(d+0xcc,'<I',2);self.put(d+0xd4,'<I',2)
   self.put(d+0x5c,'<4B',33,66,99,111);self.put(e,'<2I',EVT,OSLOG)
  self.put(EVT+0x20,'<I',STOP);self.put(EVT+0x18,'<I',SET)
  self.put(TVT,'<3I',0x4068f0,0x5ba1d0,0x536670);fields.add(TVT)
 def lists(self):return [call(0x406a50,L0),call(0x406a50,L1)]
 def vibration(self,enabled):
  v=self.alloc(0x38);self.image[v-BASE:v-BASE+0x38]=bytes(0x38)
  self.put(v+4,'<I',0x404eb936);self.put(v+0x18,'<B',enabled);self.put(OBJ+0x100,'<I',v);return v
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  known={row[0] for row in function_exports}
  for s in result:
   for at,data in s['outputs']:
    if int.from_bytes(bytes.fromhex(data),'little') in known:fields.add(at)
  return result
def tick(list_=L0,mask=0):return call(0x406ac0,list_,[0x1357,mask])
def bind_input(slot=0):return call(0x41f1b0,P,[slot])
effects={0x7d6668:E0,0x7d666c:E1}
for fill in [0,0xa5,255]:
 g=LifecycleGraph(fill);g.run([call(0x41e850,P)]*2,'constructor preserves untouched bytes/'+str(fill))
 g=LifecycleGraph();g.image[L0-BASE:L0-BASE+32]=bytes([fill])*32
 g.run([call(0x406a50,L0)]*2+[call(0x4069b0,L0),tick(),call(0x406bb0,L0)],'empty task list/'+str(fill))
for flags in [0,1,2,255,256,257,0xffffffff]:
 g=LifecycleGraph();g.run([call(0x41eec0),call(0x41e8c0,HEAP,[flags])],'factory/delete/'+str(flags))
 g=LifecycleGraph();g.run([call(0x406890,TASK,[0xffffffff]),call(0x406980,TASK,[flags])],'task base/delete/'+str(flags))
 g=LifecycleGraph();g.run([call(0x406890,TASK,[8]),call(0x536670,TASK,[flags])],'input task/delete/'+str(flags))
 g=LifecycleGraph();n=TASK+0x80;g.put(n+0xc,'<2I',n,n)
 g.run([call(0x406860,n,[flags])],'node/delete/'+str(flags))
for slot,enabled,modal in itertools.product([0,1],[0,1,255],['absent','first','modal match','modal other']):
 g=LifecycleGraph();g.gate(modal)
 calls=g.lists()+[call(0x41e850,P),call(0x41e7c0 if enabled else 0x41e7d0,P,[0,0]),bind_input(slot),tick(),tick(L1),
  bind_input(1-slot),tick(L0,0xffffffff),tick(L1),call(0x406bb0,L0),call(0x41e710,P)]
 g.run(calls,f'bind/rebind/task events/clear/destroy/{slot}/{enabled}/{modal}')
for enabled in [0,1,255]:
 for device in [0,1]:
  g=LifecycleGraph();g.vibration(enabled)
  g.run(g.lists()+[bind_input(device),tick(),tick(L1),call(0x41e710,P)],f'optional vibration/{enabled}/{device}',effects)
for flags,ownerflag,disabled,mask,lock in [(0,0,0,0,0),(1,0,0,1,0),(3,0,0,2,0),(0xffffffff,0,0,0,0),
 (0,1,0,0,0),(0,0,1,0,0),(0,0,255,0,0),(0,0,0,0,1),(0,0,0,0,0xffffffff)]:
 g=LifecycleGraph();g.put(OBJ+0x104,'<I',ownerflag);g.put(TASK+4,'<I',disabled);g.put(TASK+0x14,'<I',flags)
 g.put(TASK,'<I',0x64d7d8);g.put(TASK+0x24,'<I',0x41f170);fields.update([TASK,TASK+0x24])
 node=TASK+0x80;g.put(TASK+8,'<I',node);g.put(node,'<5I',0x64549c,TASK,8,node,node);fields.add(node)
 g.put(L0,'<8I',lock,0x64549c,0xffffffff,0,node,node,0xffffffff,0)
 g.put(node+0xc,'<2I',L0+4,L0+4);g.put(TASK+0xc,'<2I',L0,0)
 g.run([tick(mask=mask),tick(mask=mask),call(0x406850,TASK),call(0x4068f0,TASK)]*2,
  f'task epoch wrap/flags/{flags}/{ownerflag}/{disabled}/{mask}/{lock}')
# A real unlink method as a virtual task removes itself during list iteration.
for priorities in [[],[0],[1,3,2],[-1,0,1],[4,4,4]]:
 g=LifecycleGraph();calls=g.lists()
 tasks=[]
 for i,priority in enumerate(priorities):
  t=TASK+i*0x100;node=t+0x80;tasks.append(t)
  g.put(t,'<6I',TVT,0,node,0,0,0);g.put(node,'<5I',0x64549c,t,priority&0xffffffff,node,node);fields.add(node)
  calls.append(call(0x406c90,MGR+8,[t]))
 calls += [tick(),tick(),call(0x406bb0,L0)]+[call(0x406850,t) for t in tasks]
 g.run(calls,'iteration restarts after original self-unlink/'+str(priorities))
for count in [0,1,3]:
 g=LifecycleGraph();calls=g.lists();tasks=[]
 for i in range(count):
  t=TASK+i*0x100;tasks.append(t)
  calls += [call(0x406890,t,[i]),call(0x406a80,L0,[t]),call(0x406850,t)]
 calls += [call(0x406bb0,L0)]*2+[call(0x406930,t) for t in tasks]
 g.run(calls,'clear detaches without freeing/'+str(count))
for fn in [0x406930,0x577280]:
 g=LifecycleGraph();g.run(g.lists()+[call(0x406890,TASK,[8]),call(0x406a80,L0,[TASK]),call(fn,TASK)],'destroy attached task/'+hex(fn))
g=LifecycleGraph();n=TASK+0x80;g.put(n+0xc,'<2I',n,n)
g.run([call(0x406a00,n),call(0x5ba1d0,TASK),call(0x577280,TASK)],'direct destructors with absent node')
for mode in ['empty','controller0','controller1','Player0','Player1','both','included','checksum','wrong type']:
 g=LifecycleGraph();items=[]
 if mode.startswith('controller'):items.append((0xb30d9965,1,int(mode[-1])))
 if mode.startswith('Player'):items.append((0x67e6859a,1,int(mode[-1])))
 if mode=='both':items=[(0x67e6859a,1,0),(0xb30d9965,1,0)]
 if mode=='checksum':items=[(0xb9b1e3b6,13,0x12345678)]
 if mode=='wrong type':items=[(0xb30d9965,3,g.text('unused'))]
 if mode=='included':
  g.symbol(0x77001122,10,g.structure([(0xb30d9965,1,1)]));items=[(0,13,0x77001122)]
 params=g.structure(items)
 g.run(g.lists()+[call(0x41f390,P,[params])]*2+[tick(),tick(L1),call(0x41e710,P)],'initialize params/'+mode)
for slot,override in itertools.product([0,1],[False,True]):
 g=LifecycleGraph();g.registry([(0x27d7cd28,0x41eec0)])
 descriptor=g.structure([(0xb6015ea8,13,0x27d7cd28),(0xb30d9965,1,slot),(0xb9b1e3b6,13,0x8899)])
 overrides=g.structure([(0xb30d9965,1,1-slot)]) if override else 0
 g.run(g.lists()+[call(0x45e510,OBJ),call(0x45ee20,OBJ,[descriptor,overrides]),call(0x461930,OBJ,[0x100]),call(0x45db30,OBJ),
  call(0x41e7c0,HEAP,[0,0]),call(0x45d920,OBJ,[0]),tick(),tick(L1),call(0x45d920,OBJ,[0]),
  tick(),tick(L1),call(0x45d890,OBJ)],f'actual shared factory/init/finalize/tasks/owner destroy/{slot}/{override}')
 assert oracle.word(EM+0x7020)>0 and oracle.word(HEAP+0x498)==0x10000
for index_,axes,scale,second_scale in itertools.product([0,1],[1,2],[0,1,10000,65535,0x80000000,0xffffffff],[10000,0x80000000]):
 for a,b in [(0,0),(1,0),(0,1),(65535,65536),(65536,65535),(0xffffffff,0xffffffff)]:
  g=LifecycleGraph();change={**effects,0x7d42c8+4*index_:axes,0x7d42d0+8*index_:scale,0x7d42d4+8*index_:second_scale}
  g.run([call(0x5f3a50,args=[index_,a,b])],f'effect COM descriptor/{index_}/{axes}/{scale}/{a}/{b}',change)
for index_ in [0,1]:
 g=LifecycleGraph();g.run([call(0x5f3a50,args=[index_,0,0]),call(0x5f3a50,args=[index_,255,255])],'no hardware/'+str(index_))
for enabled,kind,flags,count in itertools.product([0,1,255],[0,2],[0,2,255],[-1,0,1,2]):
 g=LifecycleGraph();g.put(D0+0xc0,'<B',enabled);g.put(D0+0xd4,'<I',kind);g.put(D0+0xc4,'<I',flags);g.put(D0+0xcc,'<I',count&0xffffffff)
 g.run([call(0x5bdad0,D0)]*2+[call(0x5bccb0,D0),call(0x5bdad0,D0)],f'vibration flags/{enabled}/{kind}/{flags}/{count}',effects)
g=LifecycleGraph();g.put(TASK,'<I',0x64d7d8);g.put(TASK+0x24,'<I',0x41f170);fields.update([TASK,TASK+0x24])
g.run([call(0x577270,TASK)],'direct original virtual execute')
scope='28 original routines: Input factory/construction/parameter initialization/device binding/destruction and event-enable commands; task links, allocation ownership, list registration, priority traversal with mutation restart, clear and virtual dispatch; Vibration binding/device toggles and complete force-feedback wrapper. Generic composite factory creates and initializes actual Input, both task lists execute original pad/events, owner destruction removes tasks. DirectInput COM stop/set are explicit test-only hardware observations; no game callee is replaced. Initialized allocator and bounded device slots, successful live task allocations, valid list ownership and modal parameters are required. Whole arena/globals/heap/returns compare without arithmetic masks. Full skater startup and playable rendering remain unfinished.'
report_coverage={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),
 'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'input-lifecycle-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':labels,
 'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),**extra}
(folder/fixture['memory']).write_bytes(initial)
(folder/'input-lifecycle-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':report_coverage,'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'input-lifecycle-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['callees','counts','scope']}),flush=True)
