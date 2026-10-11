"""Full FlexParticle command registration, forwarding and update against x86."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-particle-simulation.py').read_text().split('for segments in [0,1,2,4,5,8,9]:')[0],'<verified particle simulation fixture setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x642fe0,737,'particle_descriptors_initialize',0,'void',False,False,False),(0x41d6e0,21,'particle_descriptors_register',0,'void',True,False,False),
 (0x41d700,52,'flexparticle_descriptor_scoped',3,'word',True,True,True),(0x41d780,101,'flexparticle_checksum',3,'word',False,False,True),(0x41d7f0,38,'flexparticle_forward',3,'word',False,False,True),
 (0x41d820,25,'flexparticle_clear',3,'word',False,False,True),(0x41d840,164,'flexparticle_scripts',3,'word',False,False,True),(0x41d8f0,46,'flexparticle_running',3,'word',False,False,True),
 (0x41d920,22,'flexparticle_start',3,'word',False,False,True),(0x41d940,22,'flexparticle_stop',3,'word',False,False,True),(0x41d960,91,'flexparticle_remove',3,'word',False,False,True),(0x41e190,71,'flexparticle_destroy_owner',3,'word',False,False,True),
 (0x41df80,526,'flexparticle_update',0,'void',True,True,True)]
for a,n,name,argc,result,heap,diag,this_ in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,diag,this_)
for a,name in [(0x497790,'particle_setup_script'),(0x497900,'particle_update_script')]:bind(a,'thug_'+name+'_draft',3,'void',True,True)
bind(0x41d1d0,'thug_object_reference_assign',1,'void');bind(0x461a00,'thug_object_manager_add',1,heap=True)
exports[:]=[x for x in exports if x[0]!=0x645fe4];exports.append([0x645fe4,'thug_flexparticle_dispatch_methods_draft'])
for a,n,name,*_ in specs:
 if a not in [0x41d700,0x642fe0,0x41d6e0,0x41df80]:function_exports.append([a,'thug_'+name+'_draft'])
for i in range(26):exports.append([0x683ac0+i*24,'thug_particle_descriptors_draft',i*24])
for offset in range(0,26*24,4):
 at=0x683ac0+offset;v=int.from_bytes(pe.get_data(at-0x400000,4),'little');glob('thug_particle_descriptors_draft',at,v,offset=offset)
 if offset%24==8:extra['pointer_globals'].append(index[at])
for name,at,v in [('thug_frame_length_scale',0x684fc8,bits(1)),('thug_particle_suspend_half_counter_draft',0x6951b4,0),('thug_particle_suspend_quarter_counter_draft',0x6951b8,0)]:global_default(name,at,v)
glob('thug_particle_network_state_draft',0x6fa7d0,NET)
global_default('thug_particle_parameter_scale_draft',0x67d6d0,bits(.1))
initial=bytes(memory);oracle.initial=initial
class DispatchGraph(SimulationGraph):
 def __init__(self,count=3):
  super().__init__(count);self.image[COMP-BASE:COMP-BASE+0x3c]=bytes(0x3c)
  self.put(COMP,'<2I',0x645fe4,0xc5bceb9e);self.put(COMP+12,'<I',OBJ);fields.add(COMP)
  self.put(OBJ,'<I',OBJECT_METHODS);self.put(OBJ+0x104,'<I',0)
  self.put(OBJ+0x4c,'<4f',2,3,4,1);self.put(OBJ+0xc0,'<16f',*[(1 if i%5==0 else 0) for i in range(16)])
  self.put(P+0x12a,'<B',1);self.put(P+0xf0,'<I',0x11223344);self.put(COMP+0x24,'<I',0x11223344)
  self.put(NET,'<3I',0,0,0);self.symbol(0xdb120fb5,2,bits(3));self.symbol(0x3271aa80,2,bits(7))
  self.link()
 def attach(self):return call(0x41d1d0,COMP+0x18,[P])
 def update(self):return call(0x41df80,COMP,[self.query])
 def descriptor(self,member,name=0x12345678,items=(),adjustment=0):
  entry=self.alloc(24);self.put(entry,'<6I',name,0xc5bceb9e,member,adjustment&0xffffffff,0,0);fields.add(entry+8)
  return call(0x41d700,COMP-adjustment,[entry,self.structure(items),0,self.query])
 def suspend(self,far=False,ready=True):
  s=self.alloc(0x50);self.image[s-BASE:s-BASE+0x50]=bytes(0x50);self.put(COMP+0x30,'<I',s)
  self.put(s+0x24,'<f',0 if ready else 100);self.put(s+0x34,'<f',2);self.put(s+0x30,'<B',far);return s
for fill in [0,0xdeadbeef]:
 g=DispatchGraph();changes={0x683ac0+i*24+j:fill for i in range(26) for j in [8,12,16,20]}
 run_sim(g,[call(0x642fe0),call(0x642fe0),call(0x41d6e0),call(0x41d6e0)],f'initialize and register/{fill}',changes)
for attached in [False,True]:
 for member in [0x41d7f0,0x41d820,0x41d8f0,0x41d920,0x41d940]:
  for adjustment in [0,4,-4]:
   g=DispatchGraph();calls=[g.attach()] if attached else []
   calls += [g.descriptor(member,0x35b65bd4,[(0x2013c0c6,2,bits(128))],adjustment)]
   run_sim(g,calls,f'direct member/{attached}/{member:x}/{adjustment}')
for name in [0x2299a9f2,0x96896315,0,0xffffffff]:
 for rate in [-1,0,.01]:
  for running in [0,1]:
   g=DispatchGraph();g.put(P+0x70,'<f',rate);g.put(P+0x12b,'<B',running)
   run_sim(g,[g.attach(),g.descriptor(0,name,[(0,13,0x652f5d69)])],f'checksum fallback/{name:x}/{rate}/{running}')
g=DispatchGraph();run_sim(g,[g.descriptor(0,0x96896315)],'fallback missing effect')
for rate in [-1,0,.01]:
 for running in [0,1]:
  g=DispatchGraph();g.put(P+0x70,'<f',rate);g.put(P+0x12b,'<B',running)
  run_sim(g,[g.attach(),g.descriptor(0x41d8f0)],f'running/{rate}/{running}')
for attached in [False,True]:
 for slots in [0,1,2,3]:
  g=DispatchGraph();g.programs();items=[(0x7031f10c,10,g.structure([(0x123,1,17)]))]
  if slots&1:items.append((0xfc57577f,13,0xcd1e6836))
  if slots&2:items.append((0x092276db,13,0x11223344))
  calls=[g.attach()] if attached else []
  run_sim(g,calls+[g.descriptor(0x41d840,items=items),g.descriptor(0x41d840,items=[(0xfc57577f,13,0),(0x092276db,13,0)])],f'scripts/{attached}/{slots}')
for found in [False,True]:
 for delayed in [0,1,256,0xffffffff]:
  g=DispatchGraph()
  if not found:g.put(COMP+0x24,'<I',0x88776655)
  run_sim(g,[g.attach(),g.descriptor(0x41d960,items=[(0x0cf50f29,1,delayed)])],f'manager removal/{found}/{delayed}')
for attached in [False,True]:
 for found in [False,True]:
  g=DispatchGraph()
  if not found:g.put(COMP+0x24,'<I',0x88776655)
  run_sim(g,[call(0x461a00,MANAGER,[OBJ])]+([g.attach()] if attached else [])+[g.descriptor(0x41e190)],f'destroy owner/{attached}/{found}')
g=DispatchGraph();run_sim(g,[call(0x461a00,MANAGER,[OBJ]),g.update()],'no effect owner deletion')
for far in [False,True]:
 for ready in [False,True]:
  for execute in [False,True]:
   for elapsed in [0,.2]:
    for hidden in [0,4]:
     g=DispatchGraph();g.suspend(far,ready);g.put(P+0x12a,'<B',execute);g.put(COMP+0x2c,'<f',elapsed);g.put(OBJ+0x104,'<I',hidden)
     run_sim(g,[g.attach(),g.update()]*1,f'update gates/{far}/{ready}/{execute}/{elapsed}/{hidden}')
for orient in [False,True]:
 for model in [False,True]:
  for frame in [0,1,-.5]:
   g=DispatchGraph();g.put(COMP+0x38,'<B',orient);g.put(P+0xe0,'<3f',.1,-.2,.3)
   g.put(OBJ+0xc0,'<16f',.8,0,-.6,0,0,1,0,0,.6,0,.8,0,2,3,4,1)
   if model:
    modelptr=g.alloc(0x230);g.put(COMP+0x34,'<I',modelptr);g.put(modelptr+0x22c,'<f',.75)
   run_sim(g,[g.attach()]+[g.update()]*3,f'orientation/model/{orient}/{model}/{frame}',{0x684fc8:bits(frame)})
g=DispatchGraph();g.suspend(True,False);connection=g.alloc(0x1e88);g.put(connection+0x1e84,'<I',0);g.put(NET,'<3I',4,connection,0)
run_sim(g,[g.attach(),g.update()],'network bypass far branch')
for far in [False,True]:
 g=DispatchGraph(0);g.suspend(far);g.put(P+0x125,'<B',1);g.put(COMP+0x2c,'<f',.2)
 run_sim(g,[g.attach(),g.update()],'engine deletion reference clear/'+str(far))
g=DispatchGraph();g.programs();g.suspend(False,False)
run_sim(g,[g.attach(),call(0x497790,P,[0xcd1e6836,0,OBJ]),g.update()],'not ready executes real setup')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',json.dumps(missing),flush=True)
scope='Thirteen complete FlexParticle descriptor registration, three-argument dispatch, command members and full component update routines. Actual particle simulation, scripts, object deletion, reference unlinking, suspension/network gates, orientation and model lighting execute. Initialized valid point-effect graphs, finite math, full arena/globals/heap comparison. This fixture is not a completed training frame or playable game.'
finish('particle-dispatch',scope,{},extra)
