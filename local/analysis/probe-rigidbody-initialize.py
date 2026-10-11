"""Full original Rigidbody initialization, with real QB/math/heap callees."""
from pathlib import Path
source=Path('local/analysis/probe-rigidbody-core.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved Rigidbody services>','exec'))
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
bind(0x42e3f0,'thug_rigidbody_construct_draft',0,'word',False,False,True)
bind_new(0x42f050,4305,'thug_rigidbody_initialize_draft',1,'void',True)
bind_new(0x477010,38,'thug_script_get_vector_text_draft',3,'byte')
bind_new(0x468b60,333,'thug_level_object_finalize_draft',2,'void',True,True,this=False)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
glob('thug_rigidbody_initialization_constant_draft',0x6939d0,0x12345678)
rng=random.Random(0x42f050)
def ready(g,rotation=False):
 body(g);obj=g.alloc(0x108);g.image[obj-BASE:obj-BASE+0x108]=bytes(0x108);g.put(P+12,'<I',obj)
 g.put(obj+0x4c,'<4f',100.5,-23.25,84.125,1)
 matrix=[1 if i%5==0 else 0 for i in range(16)]
 if rotation:matrix=[rng.uniform(-1,1) for _ in range(16)]
 g.put(obj+0x6c,'<16f',*matrix)
 g.put(P+0xf4,'<I',0xa5a5a5a5)
 return obj
def run(g,items,label,repeat=True):
 s=g.structure(items);calls=[call(0x42e3f0,P),call(0x42f050,P,[s])]
 if repeat:calls.append(call(0x42f050,P,[s]))
 return check(g,calls,label)
def vitem(g,key,v):return key,6,vector(g,v)
shape_flags=[0xf756b7c5,0x1cb1a2b6,0x64fba415,0x20689278]
# Every shape with defaults/overrides, known/unknown mode, gravity scalar/vector,
# quaternion branches, optional rotations and nonzero/automatic centers.
for shape in range(5):
 for variant in range(12):
  g=CompositeGraph();ready(g,variant%2);items=[]
  if shape<4:items.append((0,13,shape_flags[shape]))
  if variant%6:items.append((0x61fbb62c,13,[0,0x4484b712,0x7b01911c,0x99a34896,0x87654321,0][variant%6]))
  if variant%3==1:items.append((0x6fae5c9a,2,bits(-117.3)))
  if variant%3==2:items.append(vitem(g,0x6fae5c9a,[4,-270,12]))
  if variant>=6:
   keys=[0x60b4860d,0xf9d75930,0xf1ecb30f,0xde76c3a7,0x9da897cf,0xc11e4dd8,0xa457ece3,0x3390d1e5,0x5a18f61f,0x85f112c1,0x8ab2db68,0xe9156e6d,0x1f4d0ca5]
   items += [(k,2,bits(rng.uniform(-20,20))) for k in keys]
   items += [(k,13,0x1234+i) for i,k in enumerate([0x58cdc0f0,0x2d075f90,0x571917fa,0xccb84047])]
   items += [vitem(g,k,[rng.uniform(-20,20) for _ in range(3)]) for k in [0x0c4c809e,0xfb1a83b2,0x851211b0]]
   items += [vitem(g,crc(k),[rng.uniform(1,100) for _ in range(3)]) for k in ['dimensions','top_dimensions','bottom_dimensions']]
   items += [(k,2,bits(rng.uniform(1,100))) for k in [0x0ab21af0,0x055ce396,0xc48391a5,0x937e3b29,0xe2ac8c3a]]
   items += [(0x4055f24a,1,1+variant),(0x0dd85bda,10,g.structure([(123,1,456),(124,6,vector(g,[7,8,9]))]))]
   items += [vitem(g,0x1d82745a,[22,41,18])]
   profile=g.structure([(0xbf8e0ace,10,g.structure([(45,1,67)])),(0x1fb2f60c,10,g.structure([(89,1,10)])),(0x4511ca8d,2,bits(.25))])
   g.symbol(0xb9738eba,10,g.structure([(0x1234,10,profile)]));items.append((0x94956e48,13,0x1234))
  if variant%4:items.append(vitem(g,0x9d2d0915,[.2*variant,-.13*variant,.07*variant]))
  if variant%4 in [1,2,3]:
   center=[0,0,0];center[variant%4-1]=13.75;items.append(vitem(g,0x737612c6,center))
  if variant%2:items.append((0,13,0x5e51924f))
  if variant%3:items.append((0,13,0xa92b9954))
  if variant%5==2:items.append((0x967cd3ae,2,bits(.00023)))
  run(g,items,f'shape{shape}/variant{variant}')
# Point/sphere arrays and metadata, including empty arrays with explicit center
# (automatic center of an empty shape has undefined geometry, tested separately).
for n in [0,1,3,8]:
 for spheres in [0,1,4]:
  for rotate in [False,True]:
   g=CompositeGraph();ready(g,rotate);items=[]
   items.append((0xccbfea8c,12,g.array(6,[vector(g,[rng.uniform(-300,300) for _ in range(3)]) for i in range(n)])))
   items.append((0x5b6a8d18,12,g.array(10,[g.structure([vitem(g,0,[rng.uniform(-300,300) for _ in range(3)]),(0xc48391a5,2,bits(i+1.5))]) for i in range(spheres)])))
   items.append((0xc35cac0d,12,g.array(10,[g.structure([(0,13,0x806fff30)] if i%2 else [vitem(g,0,[i+1,i+2,i+3])]) for i in range(n)])))
   items.append((0xb77be94a,12,g.array(6,[vector(g,[i+7,i-5,i+.25]) for i in range(n)])))
   if not n and not spheres:items.append(vitem(g,0x737612c6,[1,2,3]))
   if rotate:items.append(vitem(g,0x9d2d0915,[.3,-.7,.2]))
   # Existing allocations exercise replacement without changing preserved flags.
   for offset in [0x60,0x90,0x98,0x88,0xd4]:g.put(P+offset,'<I',g.alloc(40))
   run(g,items,f'points{n}/spheres{spheres}/rotate{rotate}')
# Independent sphere-only path: no implicit default box, radius/max comparisons,
# original flag priority over custom arrays and accumulation order.
for flags in [[],shape_flags,shape_flags[1:],shape_flags[2:],shape_flags[3:]]:
 for scale in [0,1,1e-20,1e10]:
  g=CompositeGraph();ready(g,True)
  items=[(0,13,f) for f in flags]+[(0x5b6a8d18,12,g.array(10,[g.structure([vitem(g,0,[scale*i,scale*(4-i),scale*(i-2)]),(0xc48391a5,2,bits(scale*(i+1)))]) for i in range(4)]))]
  run(g,items,f'spheres-only/flags{flags}/scale{scale}')
for name in ['dimensions','DIMENSIONS','top_dimensions','bottom_dimensions','missing','a/b','a\\b','']:
 g=CompositeGraph();out=g.alloc(16);g.put(out,'<4f',9,8,7,6);s=g.structure([vitem(g,crc(name),[1,2,3])])
 check(g,[call(0x477010,s,[g.text(name),out,0]),call(0x477010,g.structure([]),[g.text(name),out,1])],f'text-vector/{name}')
for trigger in [None,0,0x71663311]:
 for color in [None,0,0xdeadbeef]:
  for params in [False,True]:
   g=CompositeGraph();g.image[OBJ-BASE:OBJ-BASE+0x108]=bytes(0x108);entries=[]
   for key in [0x413b766d,0x71663311]:
    code=g.alloc(8);g.put(code,'<2B',1,0x24);entry=g.alloc(20);g.put(entry,'<5I',key,code,1,0,0);entries.append((key,entry))
    blob=g.alloc(20);g.put(blob,'<3I2B',0,2,2,1,0x24);g.symbol(key,7,blob)
   g.put(CACHE+20,'<4I',g.table(entries),0,0,0)
   items=[(0xa1dc81f9,13,0x12345678)]
   if trigger is not None:items.append((0x2ca8a299,13,trigger))
   if color is not None:items.append((0x99a9b716,1,color))
   if params:items.append((0x7031f10c,10,g.structure([(4,1,5),(6,6,vector(g,[7,8,9]))])))
   node=g.structure(items)
   check(g,[call(0x45e510,OBJ),call(0x468b60,args=[OBJ,node]),call(0x468b60,args=[OBJ,node])],f'level-finalize/trigger{trigger}/color{color}/params{params}')
scope='Original full Rigidbody initialization42f050, text vector getter477010 and common LevelObject finalization468b60. Real constructors, QB getters/executor, shape builders, quaternion/Euler conversion, owned scripts/copies and allocations. Common finalization synthetic scripts only terminate; whole training tests separately use actual scripts. Valid internal graphs, initialized successful heap, nonnegative bounded cylinder counts; nonempty automatic-center shapes or explicit nonzero centers. Float math uses the existing PC24/libm platform contract. Update/destruction and a playable level remain unavailable.'
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]}
print('MISSING',sorted(missing),flush=True)
# Initialized allocator, disabled fixed pools, successful allocation and padding.
groups=[([0x42f412,0x42f417,0x468c0b,0x468c10],'fixed structure pools disabled by comparison platform contract'),
 ([0x42f422,0x42f521,0x42f99c,0x468c1b],'initialized allocator contract'),
 ([0x42f454,0x42f562,0x468c4c],'successful allocation contract; failure behavior unverified'),
 ([0x42fdd7,0x42fdde,0x42fe2a],'unreachable alignment padding')]
excluded={hex(a):reason for addresses,reason in groups for a in addresses}
assert missing==set(excluded),(missing-set(excluded),set(excluded)-missing)
finish('rigidbody-initialize',scope,excluded,extra)
