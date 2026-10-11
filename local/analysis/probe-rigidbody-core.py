"""Original Rigidbody prerequisites, whole-memory and allocation comparisons."""
from pathlib import Path
exec(compile(Path('local/analysis/composite-construction-fixture-setup.py').read_text(),'<preserved comparison services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
P=BASE+0xc0000
specs=[(0x403220,10,'rigidbody_record_construct',0,'word',False),
 (0x42e3f0,324,'rigidbody_construct',0,'word',False),(0x42ef00,89,'rigidbody_create',0,'word',True),
 (0x42e1f0,281,'matrix_quaternion',1,'word',False),(0x42e310,98,'quaternion_scale_length',1,'word',False),
 (0x41a730,220,'matrix_euler',1,'word',False),(0x42d4b0,168,'rigidbody_points',1,'void',True),
 (0x42d560,297,'rigidbody_box',2,'void',True),(0x42d690,253,'rigidbody_pyramid',2,'void',True),
 (0x42d790,260,'rigidbody_cylinder',4,'void',True),(0x42d8a0,292,'rigidbody_prism',1,'void',True),
 (0x42ed60,202,'rigidbody_spheres',1,'void',True),(0x42eb10,587,'rigidbody_sound_profile',1,'void',True),
 (0x42bd90,253,'rigidbody_finalize',0,'void',False)]
for a,n,name,argc,result,heap in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=a!=0x42ef00)
for a,args in [(0x42e310,[0]),(0x42d690,[0,1]),(0x42d790,[0,1,2])]:functions[hex(a)]['float_args']=args
exports.append([0x6463f8,'thug_rigidbody_methods_draft']);oracle.setword(0x684fe4,0x5df4ac)
for at in [0x42e3f0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
def check(g,calls,label):
 try:return case(calls,g.patches(),label=label)
 except Exception:print('FAILED',label,flush=True);raise
def body(g):
 g.image[P-BASE:P-BASE+0x1a0]=bytes(0x1a0)
 return P
def vector(g,values):return g.vector([bits(v) for v in values])
for fill in [0,0xa5,0xff]:
 for a,n in [(0x403220,36),(0x42e3f0,0x1a0)]:
  g=CompositeGraph();g.image[P-BASE:P-BASE+n]=bytes([fill])*n;check(g,[call(a,P)]*2,f'construct{a:x}/poison{fill}')
 check(CompositeGraph(),[call(0x42ef00)],f'factory{fill}')
# Matrix/quaternion arithmetic: all finite outputs compare exact bits. Include
# all diagonal branches, overlap ordering, extreme exponents and signed zero.
matrices=[]
for diag in [(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1),(-1,-1,-1),(0,0,0),(0,-1,-2),(-2,-1,0)]:
 m=[0.0]*16;m[0],m[5],m[10]=diag;m[15]=1;matrices.append(m)
rng=random.Random(0x42e1f0)
for i in range(48):
 m=[rng.uniform(-2,2) for _ in range(16)];matrices.append(m)
for j,m in enumerate(matrices):
 for offset in [-32,0,4,16,32,48]:
  g=CompositeGraph();a=g.alloc(128)+32;g.put(a,'<16f',*m);q=a+offset
  check(g,[call(0x42e1f0,q,[a])],f'matrixquat{j}/alias{offset}')
quats=[(0,0,0,0),(0,0,0,1),(1,2,-3,4),(-0.0,0,0,-0.0),(1e-40,-2e-40,3e-40,-4e-40),(1e30,-2e30,3e30,-4e30)]
quats += [tuple(rng.uniform(-50,50) for _ in range(4)) for _ in range(16)]
for i,q in enumerate(quats):
 for length in [0,1,-2,1e-30,1e30]:
  g=CompositeGraph();g.put(P,'<4f',*q);check(g,[call(0x42e310,P,[bits(length)])],f'normalize{i}/length{length}')
for angles in [(0,0,0),(-0.0,0,0),(.1,.2,.3),(-2,1,3),(1e-35,0,0),(0,1,0),(0,0,1)]:
 for offset in [-32,0,4,16,48]:
  g=CompositeGraph();a=g.alloc(128)+32;g.put(a+offset,'<4f',*angles,9);check(g,[call(0x41a730,a,[a+offset])],f'euler{angles}/alias{offset}')
for count in [0,1,3,0x10000,0x10002]:
 for old in [False,True]:
  g=CompositeGraph();body(g);n=count&0xffff;items=[vector(g,[i+.25,-i-.5,i+10.5]) for i in range(max(n,2))];a=g.array(6,items);g.put(a+4,'<I',count)
  if count==1:g.put(a+8,'<I',items[0])
  if old:g.put(P+0x60,'<I',g.alloc(80))
  check(g,[call(0x42d4b0,P,[a])]*2,f'points{count}/old{old}')
for dims in [(1,2,3),(0,-0.0,0),(-3,2,-1),(1e-30,1e30,-3.5)]:
 for old in [False,True]:
  g=CompositeGraph();body(g);a=g.alloc(32);g.put(a,'<8f',*dims,9,4,5,6,8)
  if old:g.put(P+0x60,'<I',g.alloc(16))
  check(g,[call(0x42d560,P,[a,a+16]),call(0x42d8a0,P,[a]),call(0x42d690,P,[bits(dims[0]),bits(dims[1])])],f'shapes{dims}/old{old}')
for n in [0,1,2,3,7,16]:
 for sizes in [(1,2,3),(0,0,-0.0),(-.25,3.5,-2)]:
  g=CompositeGraph();body(g);check(g,[call(0x42d790,P,[*[bits(v) for v in sizes],n])]*2,f'cylinder{n}/{sizes}')
for n in [0,1,3]:
 for old in [False,True]:
  g=CompositeGraph();body(g);a=g.array(10,[g.structure([(0,6,vector(g,[i+1,i-2,i+3])),(0xc48391a5,2,bits(i+.5))]) for i in range(n)])
  if old:g.put(P+0x90,'<I',g.alloc(80))
  check(g,[call(0x42ed60,P,[a])]*2,f'spheres{n}/old{old}')
# Sound-profile copies: optional independent structures, repeated replacement,
# nested values and omissions, plus both integer settings and both floats.
for mask in range(4):
 for old in [False,True]:
  for settings in [False,True]:
   g=CompositeGraph();body(g);value=g.structure([(123,1,456),(124,6,vector(g,[1,2,3])),(125,10,g.structure([(7,1,8)]))]);items=[]
   for i,key in enumerate([0xbf8e0ace,0x1fb2f60c]):
    if mask&(1<<i):items.append((key,10,value))
    if old:g.put(P+0xd8+i*4,'<I',g.structure([(123,1,999)]))
   if settings:items += [(0x3818ee47,1,0xffffffff),(0xad67a34d,1,0x80000000),(0x4511ca8d,2,bits(.75)),(0x8fc6519f,2,bits(-8.5))]
   profile=g.structure(items);g.symbol(0xb9738eba,10,g.structure([(0x1234,10,profile)]))
   check(g,[call(0x42e3f0,P),call(0x42eb10,P,[0x1234])]*2,f'profile{mask}/old{old}/settings{settings}')
g=CompositeGraph();body(g);g.symbol(0xb9738eba,10,g.structure([]));check(g,[call(0x42eb10,P,[0x1234])],'missingprofile')
for n in [0,1,4]:
 for sound in [False,True]:
  for scale in [1,1e-20,1e20]:
   g=CompositeGraph();body(g);obj=g.alloc(0x108);g.put(P+12,'<I',obj);c=g.component(0x07713c7b if sound else 123);g.put(obj+0x100,'<I',c)
   a=g.alloc(max(n,1)*36);g.put(P+0x98,'<IH',a,n);g.put(P+0x110,'<4f',10,20,30,1)
   g.put(P+0x150,'<16f',*[rng.uniform(-2,2)*scale for _ in range(16)])
   for i in range(n):g.put(a+i*36,'<9f',*[rng.uniform(-2,2) for _ in range(9)])
   check(g,[call(0x42bd90,P)]*2,f'finalize{n}/sound{sound}/scale{scale}')
scope='Fourteen original Rigidbody startup prerequisites: embedded record/component/factory construction, matrix/quaternion conversion and normalization, Euler rotation, all five point-shape builders, sphere arrays, owned sound-profile copies, finalization. Finite arithmetic compares exact bits, including selected aliases and wide exponents. Initialized successful heap, valid internal graphs and capacity-safe nonnegative cylinder counts; lifecycle/update/initializer42f050 remain unavailable. Existing sine/cosine adapter is not physical x87 verification. No playable claim.'
bootstrap=[0x42d4e7,0x42d593,0x42d6c0,0x42d7ca,0x42d8d2,0x42ed9a,0x42ebbc,0x42ec6d]
failure=[0x42ef48,0x42ef4c,0x42ef4e,0x42ef55,0x42ef58,0x42ebeb,0x42ec9c]
pools=[0x42ebac,0x42ebb1,0x42ec5d,0x42ec62]
padding=[0x42edd6,0x42eddd,0x42bdbd]
excluded={hex(a):reason for addresses,reason in [(bootstrap,'initialized allocator contract'),(failure,'successful allocation contract; failure behavior unverified'),(pools,'fixed structure pools disabled by comparison platform contract'),(padding,'unreachable alignment padding')] for a in addresses}
assert {hex(i.address) for code in coverage.values() for i in code if not hits[i.address]}==set(excluded)
finish('rigidbody-core',scope,excluded,extra)
