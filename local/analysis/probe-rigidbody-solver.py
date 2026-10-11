"""Full original Rigidbody contact solver including friction and side effects."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-rigidbody-response.py').read_text().split('for name in [0,0x0ca64c41')[0],'<verified contact and Sound graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
bind_new(0x430140,0xa92,'thug_rigidbody_solve_contacts_draft',0,'void',True,True)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
for offset in range(0,24*48,4):glob('thug_rigidbody_collision_contacts_draft',0x6949b0+offset,0xa5a5a5a5,offset=offset)
glob('thug_rigidbody_debug_contacts_draft',0x6939d5,0,1)
initial=bytes(memory);oracle.initial=initial
rng=random.Random(0x430140)
class SolverGraph(ResponseGraph):
 def __init__(self,n=1,active=None,cached=0,directions=None):
  super().__init__();self.put(RIGID+0x190,'<2B',n,n if active is None else min(n,bin(active).count('1')))
  self.put(RIGID+0x8c,'<H',n);self.put(RIGID+0x150,'<16f',*[1 if i%5==0 else 0 for i in range(16)])
  self.changes={}
  if directions is not None:
   shapes=self.alloc(max(n,1)*20);self.put(RIGID+0x88,'<I',shapes)
   for i in range(n):self.put(shapes+i*20,'<4fB',*directions,int(i%2==0))
  self.records=[]
  for i in range(n):
   record=struct.pack('<11f4B',*[0.,-1.,0.,0.],*[0.,1.,0.,0.],.5,0.,-.1,int(active is None or bool(active&(1<<i))),cached,i,0xa5)
   self.records.append(bytearray(record))
 def contact(self,i,arm=None,normal=None,depth=None,inverse=None,impulse=None,active=None,cached=None):
  a=self.records[i]
  if arm is not None:struct.pack_into('<4f',a,0,*arm)
  if normal is not None:struct.pack_into('<4f',a,16,*normal)
  for off,value in [(32,inverse),(36,impulse),(40,depth)]:
   if value is not None:struct.pack_into('<f',a,off,value)
  if active is not None:a[44]=active
  if cached is not None:a[45]=cached
 def run(self,calls=None,label='solver'):
  changes={**self.changes}
  for i,record in enumerate(self.records):changes.update({0x6949b0+i*48+4*j:v for j,v in enumerate(struct.unpack('<12I',record))})
  check(self,calls or [call(0x430140,RIGID)],label,changes)
  if len(labels)%25==0:print('Original contact solver cases',len(labels),flush=True)
# Count, inactive records, initialized inverse caching, and repeat ordering.
for n in [0,1,2,3,8,24]:
 for mask in [0,1,0xaaaaaaaa,(1<<n)-1]:
  for cached in [0,1]:
   g=SolverGraph(n,mask,cached);g.run([call(0x430140,RIGID)]*2,f'count{n}/mask{mask:x}/cached{cached}')
# Single-point early exit versus settled loop and20-iteration fallback.
for point_count in [0,1,2,24]:
 for velocity in [(0,0,0,1),(0,4,0,1),(0,-4,0,1),(3,-4,5,1),(0,.001,0,1),(0,-.001,0,1)]:
  for restitution in [0,.4,1,-.5]:
   g=SolverGraph(2);g.put(RIGID+0x8c,'<H',point_count);g.put(RIGID+0x120,'<4f',*velocity);g.put(RIGID+0x140,'<4f',0,0,0,1);g.put(RIGID+0x2c,'<f',restitution)
   g.run(label=f'iterations/points{point_count}/v{velocity}/bounce{restitution}')
# Tangent lengths below/equal/above original.001 boundary and friction caps.
for speed in [0.,.000999,.001,.001001,.1,10.,100.]:
 for friction in [0.,.1,1.,100.]:
  g=SolverGraph();g.put(RIGID+0x120,'<4f',speed,-2,0,1);g.put(RIGID+0x140,'<4f',0,0,0,1);g.put(RIGID+0x30,'<f',friction)
  g.run([call(0x430140,RIGID)]*2,f'tangent boundary/{speed}/{friction}')
# Shape-aligned friction: absent, disabled, normal-only, short and rotated axes.
for direction in [(0,0,0,1),(0,1,0,1),(1,0,0,0),(.0005,1,0,0),(.001,1,0,0),(.001001,1,0,0),(3,4,5,1)]:
 for rotated in [False,True]:
  g=SolverGraph(2,directions=direction);g.put(RIGID+0x8c,'<H',1)
  if rotated:g.put(RIGID+0x150,'<16f',0,0,-1,0,0,1,0,0,1,0,0,0,2,3,4,1)
  g.contact(1,arm=(1,-2,3,0),normal=(.6,.8,0,0));g.run(label=f'directional friction/{direction}/{rotated}')
# Original impact scripts/sound and failed-convergence script execute for real.
for failure in [False,True]:
 for script in [False,True]:
  for sound in [False,True]:
   g=SolverGraph(2 if failure else 1);calls=g.impactscript() if script else []
   if script and failure:g.put(RIGID+0xd0,'<I',g.word(RIGID+0xc8));g.put(RIGID+0xc8,'<I',0)
   if failure:g.put(RIGID+0x120,'<4f',0,0,0,1);g.put(RIGID+0x140,'<4f',0,0,0,1)
   else:g.put(RIGID+0x120,'<4f',30,-200,10,1)
   if sound:g.sound()
   g.run(calls+[call(0x430140,RIGID)],f'side effects/failure{failure}/script{script}/sound{sound}')
# All contacts inactive proves final no-impact scan, and debug branch has the
# actual original bare-RET drawing callee (no invented renderer).
for debug in [0,1,255]:
 for depth in [0.,-.25,.25,-100.]:
  for dt in [0.,.5,1.,-1.]:
   g=SolverGraph(3);g.put(RIGID+0x8c,'<H',1);g.changes={0x6939d5:debug,0x684fc8:bits(dt)}
   for i in range(3):g.contact(i,depth=depth,arm=(i+1,-2,i-.5,1))
   g.run(label=f'correction/debug{debug}/depth{depth}/dt{dt}')
# Diverse valid unit normals, inertia, contacts, cached impulses and lever arms.
for j in range(96):
 n=1+j%5;g=SolverGraph(n,cached=j%2,directions=(1,0,.5,0) if j%3==0 else None);g.put(RIGID+0x8c,'<H',1 if j%4 else n)
 g.put(RIGID+0x18,'<f',[0.,.003,.1,1.][j%4]);g.put(RIGID+0x2c,'<3f',rng.uniform(0,1),rng.uniform(0,2),rng.uniform(0,20))
 g.put(RIGID+0x120,'<4f',*[rng.uniform(-100,100) for _ in range(3)],1);g.put(RIGID+0x140,'<4f',*[rng.uniform(-3,3) for _ in range(3)],1)
 for i in range(n):
  normal=[rng.uniform(-1,1) for _ in range(3)];length=sum(x*x for x in normal)**.5
  g.contact(i,arm=(*[rng.uniform(-10,10) for _ in range(3)],0),normal=(*[x/length for x in normal],0),depth=rng.uniform(-2,0),inverse=rng.uniform(.001,1),impulse=rng.uniform(0,2),active=int((i+j)%4!=0))
 g.run(label=f'random valid contact geometry/{j}')
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()};print('MISSING',missing,flush=True)
excluded={hex(a):'unreachable alignment padding' for a in [0x4301b8,0x4301bf,0x43044d,0x430b5d]}
scope='Complete430140 contact solver: all normal-impulse iterations and20-iteration fallback, inverse-mass caching, optional shape-axis friction, correction, debug branch using original bare-RET draw, impact scripts/Sound and nonconvergence script. Actual matrix/vector/math/script/audio callees. Finite valid contact geometry, disjoint arrays bounded to24contacts, normalized normals, nonnegative inverse inertia and initialized successful allocation. Full arena/globals/return/heap comparison; no completed Rigidbody update, scene frame or playability claim.'
finish('rigidbody-solver',scope,excluded,extra)
