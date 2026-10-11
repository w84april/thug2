"""Original attachment initialization and particle component prerequisites."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved component comparison services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
specs=[(0x476770,79,'script_get_pair_outputs',4,'byte',False,True),
 (0x41f520,569,'lockobj_initialize',1,'void',True,True),
 (0x41da00,125,'flexparticle_construct',0,'word',False,True),
 (0x41e1e0,86,'flexparticle_create',0,'word',True,False),
 (0x433e70,29,'suspend_force_distance',0,'void',False,True),
 (0x41d740,32,'flexparticle_finalize',0,'void',False,True),
 (0x41d760,20,'flexparticle_visibility',1,'void',False,True)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
for a,n,argc in [(0x461a00,'thug_object_manager_add',1),(0x45ee20,'thug_composite_add_parameters_draft',2)]:bind(a,n,argc,heap=True,diag=a==0x45ee20)
put(MANAGER_METHODS+0x10,'<I',0x4619d0);fields.add(MANAGER_METHODS+0x10);function_exports.append([0x4619d0,'thug_object_manager_set_priority'])
exports.append([0x645fe4,'thug_flexparticle_methods_draft']);function_exports.append([0x41e1e0,'thug_flexparticle_create_draft'])
oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=0x41da00,end=0x41da00)
for name,a,v in [('thug_frame_counter',0x7d1ec8,60),('thug_frame_rate',0x684fd0,bits(60))]:global_default(name,a,v)
for i,v in enumerate([0x12345678,0x98765432,0x31415926]):
 a=0x690fd4+4*i
 if a in index:defaults[index[a]]=v
 else:glob('thug_random_state',a,v,offset=4*i)
initial=bytes(memory);oracle.initial=initial
class ParticleGraph(PropGraph):
 def pair(self,x,y):
  p=self.alloc(12);self.put(p,'<3I',0xabcdef00,x,y);return p
 def lock(self,fill=0):
  self.image[P-BASE:P-BASE+0x90]=bytes([fill])*0x90;self.put(P+12,'<I',OBJ)
  return P
def check(g,calls,label,changes=None):
 try:return case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
# Raw pair reads deliberately retain payload bits and overlapping write order.
for present in [False,True]:
 for required in [0,1,0xffffffff]:
  for alias in ['separate','same','x-to-source-y','y-to-source-x']:
   for words in [(bits(1.25),bits(-2.5)),(0x7f812345,0xffc54321),(0,0x80000000)]:
    g=ParticleGraph();pair=g.pair(*words);out=g.alloc(8);x,y=out,out+4
    if alias=='same':y=x
    if alias=='x-to-source-y':x=pair+8
    if alias=='y-to-source-x':y=pair+4
    s=g.structure([(123,5,pair)] if present else [])
    check(g,[call(0x476770,s,[123,x,y,required])],f'pair/{present}/{required}/{alias}/{words}')
for fill in [0,0xa5,0xff]:
 g=ParticleGraph();g.lock(fill);check(g,[call(0x41da00,P)]*2,f'particle-constructor/{fill}')
g=ParticleGraph();check(g,[call(0x41e1e0)],'particle-factory')
for present in [False,True]:
 for flag in [0,1,2,255,256,0xffffffff]:
  g=ParticleGraph();g.lock(0xa5);obj=g.alloc(0x140);g.put(P+0x18,'<I',obj if present else 0)
  check(g,[call(0x41d760,P,[flag])],f'particle-visibility/{present}/{flag:x}')
for kind in [None,123,0xce0ca665]:
 g=ParticleGraph();g.lock(0xa5);g.put(OBJ+0x100,'<I',0)
 if kind is not None:
  component=g.alloc(0x4c);g.put(component+4,'<I',kind);g.put(component+16,'<I',0);g.put(OBJ+0x100,'<I',component)
 check(g,[call(0x41d740,P)]*2,f'particle-finalize/{kind}')
g=ParticleGraph();g.lock(0xa5);check(g,[call(0x433e70,P)]*2,'suspend-force-distances')
for fill in [0,0xa5,0xff]:
 for disabled in [False,True]:
  g=ParticleGraph();g.lock(fill);s=g.structure([(0,13,0xd443a2bc)] if disabled else [])
  check(g,[call(0x41f520,P,[s])]*2,f'lock-default/{fill}/{disabled}')
for mode in ['id','fallback-name','both','missing']:
 for priority in [0,1,100,0x7fffffff,0x80000000,0xffffffff]:
  g=ParticleGraph();g.lock();g.put(OBJ+512+0x30,'<I',priority);g.put(OBJ+1024+0x30,'<I',priority^0xffffffff)
  items=[(0x40c698af,13,0x101 if mode in ['id','both'] else 0x9999),(0x2bfc2486,13,0x102 if mode in ['fallback-name','both'] else 0x9998)]
  calls=[call(0x461a00,MANAGER,[OBJ+i*512]) for i in range(3)]
  check(g,calls+[call(0x41f520,P,[g.structure(items)])]*2,f'lock-target/{mode}/{priority:x}')
for unnamed in [False,True]:
 for angles in [None,(0,0,0),(.2,-.3,1.2)]:
  g=ParticleGraph();g.lock(0xa5);items=[(0xbe9ab709,6,g.vector([bits(4),bits(5),bits(6)])),(0xcab94088,13,0x76543210)]
  if unnamed:items.append((0,6,g.vector([bits(1),bits(2),bits(3)])))
  if angles is not None:items.append((0x9d2d0915,6,g.vector([bits(v) for v in angles])))
  check(g,[call(0x41f520,P,[g.structure(items)])],f'lock-vector/{unnamed}/{angles}')
for scale,frequency in [(None,None),((1,2),None),(None,(.5,1)),((.2,3),(.5,1)),((-2,3),(-3,5)),((0,-0.0),(0,-0.0)),((1e30,-1e30),(1e-30,1e-30)),((1e-30,-1e-30),(1e30,-1e30))]:
 for time in [0,1,60,0x7fffffff,0x80000000,0xffffffff]:
  g=ParticleGraph();g.lock(0xa5);items=[]
  for key,values in [(0x700c4085,scale),(0xd25807f0,frequency)]:
   if values is not None:items.append((key,5,g.pair(*(bits(v) for v in values))))
  check(g,[call(0x41f520,P,[g.structure(items)])]*2,f'lock-envelope/{scale}/{frequency}/{time:x}',{0x7d1ec8:time})
# Exercise the recovered virtual initializer through actual component creation.
g=ParticleGraph();g.registry([(0x5cb5cb7e,0x41ff20)]);g.put(OBJ+0x100,'<I',0)
s=g.structure([(0xb6015ea8,13,0x5cb5cb7e),(0xbe9ab709,6,g.vector([bits(1),bits(2),bits(3)]))])
check(g,[call(0x45ee20,OBJ,[s,0])],'actual-lockobj-virtual-initialization')
scope='Seven original particle-component prerequisites: complete LockObj initialization with real registry priority, QB getters, timer, PRNG, sine envelope and Euler rotation; raw pair-output getter; FlexParticle constructor/factory/finalize/visibility and forced Suspend thresholds. Whole memory/globals/heap compare; finite envelope values, valid graphs and successful allocation contract. Existing libm adapter does not claim physical x87 transcendental accuracy. Particle engine initialization, effect update and playable frames remain unavailable.'
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]};print('MISSING',sorted(missing),flush=True)
excluded={'0x41f6c8':'unreachable negative conversion after phase mask1023',**{hex(a):'unreachable reference cleanup immediately after zero initialization' for a in [0x41da4d,0x41da4e,0x41da53]},**{hex(a):'successful allocation contract; failure behavior unverified' for a in [0x41e225,0x41e229,0x41e22b,0x41e232,0x41e235]}}
finish('particle-component',scope,excluded,extra)
