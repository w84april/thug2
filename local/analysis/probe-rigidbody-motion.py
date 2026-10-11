"""Motion, scratch rotation, settling and destruction against original x86."""
from pathlib import Path
source=Path('local/analysis/probe-rigidbody-core.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved Rigidbody services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
specs=[(0x42be90,103,'stop',0,True,True),(0x42bf00,561,'rotate',0,False,False),
 (0x42c6d0,441,'friction',0,False,False),(0x42c890,177,'settle',0,True,True),
 (0x42e540,1088,'integrate',1,False,False),(0x42ef60,239,'destroy',0,True,False),
 (0x430df0,33,'delete',1,True,False)]
for a,n,name,argc,heap,diag in specs:bind_new(a,n,'thug_rigidbody_'+name+'_draft',argc,'word' if name=='delete' else 'void',heap,diag)
functions['0x42e540']['float_args']=[0]
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
bind(0x42e3f0,'thug_rigidbody_construct_draft',0,'word')
for name,a,n in [('points',0x694e30,24),('spheres',0x694fb0,24),('contacts',0x695130,2)]:
 for off in range(0,n*16,4):glob('thug_rigidbody_rotated_'+name+'_draft',a+off,0x12345678+off,offset=off)
rng=random.Random(0x42e540)
def ready(g,contacts=0):
 body(g);g.put(P+0x191,'<B',contacts&255);g.put(P+0x10c,'<I',1)
 for offset,values in [(0x1c,[0,-386.4,0,1]),(0x110,[100,-3.5,23,1]),(0x120,[3,4,12,1]),(0x130,[.2,-.1,.3,.9]),(0x140,[.1,-.2,.3,1])]:g.put(P+offset,'<4f',*values)
 g.put(P+0x150,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
 g.put(P+0x108,'<f',-1)
def shapes(g,ns):
 for kind,(offset,countoff,stride,n) in enumerate(zip([0x60,0x90,0x98],[0x8c,0x94,0x9c],[16,20,36],ns)):
  a=g.alloc(max(n,1)*stride);g.put(P+offset,'<I',a);g.put(P+countoff,'<H',n)
  for i in range(n):
   g.put(a+i*stride,'<4f',*[rng.uniform(-400,400) for _ in range(4)])
   if kind==2:g.put(a+i*stride+32,'<B',i%2)
def script(g):
 key=0x71663311;g.image[OBJ-BASE:OBJ-BASE+0x108]=bytes(0x108);g.put(P+12,'<I',OBJ)
 code=g.alloc(8);g.put(code,'<2B',1,0x24);entry=g.alloc(20);g.put(entry,'<5I',key,code,1,0,0)
 blob=g.alloc(20);g.put(blob,'<3I2B',0,2,2,1,0x24);g.symbol(key,7,blob)
 g.put(CACHE+20,'<4I',g.table([(key,entry)]),0,0,0);g.put(P+0xcc,'<I',key)
 g.put(P+0xd4,'<I',g.structure([(123,1,456),(124,6,vector(g,[1,2,3]))]))
 return [call(0x45e510,OBJ)]
for ns in [(0,0,0),(1,0,0),(0,1,0),(0,0,1),(0,0,2),(16,4,2),(24,24,2)]:
 for scale in [0,1,1e20]:
  g=CompositeGraph();ready(g);shapes(g,ns)
  g.put(P+0x150,'<16f',*[rng.uniform(-2,2)*scale for _ in range(16)])
  check(g,[call(0x42bf00,P)]*2,f'rotate{ns}/scale{scale}')
for v in [(0,0,0,7),(3,4,0,7),(1e-30,-2e-30,3e-30,-0.0),(1e30,-2e30,3e30,1)]:
 for t in [0,1e-35,2.5,5,10]:
  g=CompositeGraph();ready(g);g.put(P+0x120,'<4f',*v);g.put(P+0x140,'<4f',*v);g.put(P+0x38,'<2f',t,t)
  check(g,[call(0x42c6d0,P)]*2,f'friction{v}/threshold{t}')
for t1,t2 in [(0,2),(2,0),(-2,-3),(5,5),(13,13)]:
 g=CompositeGraph();ready(g);g.put(P+0x38,'<2f',t1,t2);check(g,[call(0x42c6d0,P)]*2,f'friction-independent{t1}/{t2}')
for contacts in [0,2,3,4,127,128,255]:
 for dt in [0,1/60,.125,-.01]:
  g=CompositeGraph();ready(g,contacts);shapes(g,(16,3,2))
  for offset in [0x1c,0x110,0x120,0x130,0x140]:g.put(P+offset,'<4f',*[rng.uniform(-4,4) for _ in range(4)])
  check(g,[call(0x42e540,P,[bits(dt)])]*3,f'integrate/contactbyte{contacts}/dt{dt}')
for scale in [1e-30,1e30]:
 for contacts in [0,3]:
  g=CompositeGraph();ready(g,contacts);shapes(g,(0,0,0))
  for offset in [0x1c,0x110,0x120]:g.put(P+offset,'<4f',*[rng.uniform(-2,2)*scale for _ in range(4)])
  check(g,[call(0x42e540,P,[bits(1/60)])],f'integrate-wide{scale}/contacts{contacts}')
for q in [(0,0,0,0),(0,0,0,1),(-0.0,0,-0.0,1),(1e-30,2e-30,3e-30,4e-30)]:
 g=CompositeGraph();ready(g);g.put(P+0x130,'<4f',*q);check(g,[call(0x42e540,P,[bits(1/60)])],f'integrate-quaternion{q}')
for contacts in [2,3,128,255]:
 for lv,av in [(168,1),(169,0),(170,0),(170,.14),(170,1)]:
  g=CompositeGraph();ready(g,contacts);g.put(P+0x58,'<2f',lv,av)
  check(g,[call(0x42c890,P)]*2,f'settle/contact{contacts}/limits{lv}/{av}')
for distance in [0,47.999,48,48.001,100]:
 for flags in [0,1,2,3]:
  g=CompositeGraph();ready(g,3);g.put(P+0x58,'<2f',170,1);g.put(P+0xf4,'<I',flags)
  g.put(P+0xf8,'<4f',0,0,0,1);g.put(P+0x110,'<4f',distance,0,0,1)
  check(g,[call(0x42c890,P)]*2,f'settle-expire/distance{distance}/flags{flags}')
for stop in [0x42be90,0x42c890]:
 for withscript in [False,True]:
  g=CompositeGraph();ready(g,3);g.put(P+0x58,'<2f',170,1)
  calls=script(g) if withscript else []
  check(g,calls+[call(stop,P)]*2,f'stop{stop:x}/script{withscript}')
# Independent ownership combinations prove null handling and release ordering.
for mask in [0,1,2,4,8,16,32,64,127]:
 for flags in [0,1,0x100]:
  g=CompositeGraph();ready(g);g.put(P,'<I',0x6463f8);fields.add(P)
  for j,off in enumerate([0x60,0x88,0x90,0x98,0xd4,0xdc,0xd8]):
   if mask&(1<<j):g.put(P+off,'<I',g.alloc(80) if j<4 else g.structure([(123,1,j),(124,6,vector(g,[1,2,3]))]))
  g.put(P+8,'<I',2 if mask==127 else 0)
  check(g,[call(0x430df0,P,[flags])],f'delete/mask{mask}/flags{flags}')
g=CompositeGraph();ready(g);check(g,[call(0x42ef60,P)],'direct-destructor')
# Sequential movement is tested separately from collision response, still pending.
g=CompositeGraph();ready(g);shapes(g,(8,0,0));g.put(P+0x38,'<2f',.125,.025)
check(g,[c for i in range(12) for c in [call(0x42e540,P,[bits(1/60)]),call(0x42c6d0,P)]]+[call(0x42be90,P)],'twelve-substeps-friction-stop')
scope='Seven original Rigidbody motion/lifetime routines: stop with real attached-script spawn/execute, point/sphere/active-contact rotation, linear/angular friction, settling/expiration, timestep integration, destruction and deleting wrapper. Exact finite PC24 arithmetic and original float spills; full arena, scratch globals, allocation order and callee-saved registers compare. Valid disjoint internal arrays bounded to 24 points,24 spheres,2 contacts; initialized successful heap, fixed pools disabled. Synthetic callback scripts terminate normally. These are collision-selected substep prerequisites, not full Update430e20 or collision response. No playable claim.'
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]}
print('MISSING',sorted(missing),flush=True)
excluded={hex(a):'unreachable alignment padding' for a in [0x42bf1d,0x42e86d]}
assert missing==set(excluded),(missing-set(excluded),set(excluded)-missing)
finish('rigidbody-motion',scope,excluded,extra)
