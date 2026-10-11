"""Execute complete original sphere queries and record exact memory/global effects."""
import importlib.util,itertools,random,struct
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from specimen import ROOT,load
spec=importlib.util.spec_from_file_location('sphere_query_support',ROOT/'local/analysis/sphere-query-support.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
BASE=0x1800000;SIZE=0x1c000;INST=BASE+0x1000;GEO=BASE+0x2000;FACES=BASE+0x3000;VERTS=BASE+0x6000;TREE=BASE+0x7000
PROBE=BASE+0x8000;RESULT=PROBE+0x14;BOUNDS=BASE+0x9000;CACHE=BASE+0xa000;GRID=BASE+0xc000;GRID2=BASE+0x12000;NODES=BASE+0x18000;SCENES=BASE+0x19000;LIST=BASE+0x1a000
memory=bytearray((i*37+19)&255 for i in range(SIZE));Q=s.Q
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def w(at,*v):put(at,'<'+'I'*len(v),*v)
def f(at,*v):put(at,'<'+'f'*len(v),*v)
for i in range(8):
 obj=GEO+i*64;inst=INST+i*32;face=FACES+i*0x400;vertices=VERTS+i*128
 w(inst,0x645c18,0xabc00000+i,0,obj);w(obj,0xabc00000+i);put(obj+4,'<HHHBB',0,3,1,1,0);w(obj+12,face)
 f(obj+16,0,0,0,1,10,10,0,1);w(obj+0x30,vertices,0,0);f(obj+0x3c,1)
 f(vertices,0,0,0,10,0,0,0,10,0)
 for j in range(40):put(face+j*8,'<HH4B',0x41,0,0,1,2,255)
for grid in [GRID,GRID2]:
 f(grid,-20,-20,-20,1,20,20,20,1,20,20);w(grid+0x28,2,2)
 for x,z in itertools.product(range(2),repeat=2):
  cell=grid+0x30+(x*20+z)*48;w(cell+0x24,3 if grid==GRID else 0);w(cell+0x2c,LIST)
w(LIST,INST,INST+32,INST)
for i in range(2):w(NODES+i*16+4,SCENES+i*0x100);w(NODES+i*16+12,NODES+(i+1)*16);w(SCENES+i*0x100+0xd4,[GRID,GRID2][i])
w(NODES+36,0xffffffff)
f(CACHE,-100,-100,-100,1,100,100,100,1)
for i in range(8):w(CACHE+32+8*i,INST+32*i,GEO+64*i+16)
w(CACHE+0xfc0,8,8,0)
f(PROBE,2,2,.5,1,1);f(RESULT+0x584,0,0,-3,0,0);w(RESULT+0x598,0);put(RESULT+0x59c,'<HHI',0,0,0);w(PROBE+0xb5c,0)
f(BOUNDS,-10,-10,-10,1,20,20,20,1)
q=s.Queries(memory,BASE,NODES,[INST+32*i for i in range(8)]);hits=Counter()
def trace(cpu,at,size,user):hits[at]+=1
for at,n in s.RANGES.items():q.oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
static=(0x4110b0,INST,[PROBE,BOUNDS,RESULT,Q])
scene=lambda cache:(0x410240,0,[PROBE,RESULT,cache,Q])
wrapper=(0x418300,PROBE,[0xdeadbeef,Q])
for state in ['first','second','none','sentinel']:
 patches=[];changes={}
 if state in ['second','none']:patches.append(s.words(SCENES+0xd4,0))
 if state=='none':patches.append(s.words(SCENES+0x100+0xd4,0))
 if state=='sentinel':changes[q.scene_index]=NODES+32
 q.check([(0x48c940,0,[])],patches,'first grid/'+state,changes)
# Both face/vertex encodings; flags, stationary/swept/negative travel, retained
# time fields and nonzero pre-existing hit count. No mocked geometric results.
for small,compressed,travel,mode,count,filters in itertools.product([0,1],[0,1],[0,1,-1],[0,2],[0,31,32],[(0x41,0,0),(0x10,0x10,0),(1,0,2)]):
 flags,excluded,required=filters
 patches=[s.patch(GEO+10,'<BB',small,compressed),s.floats(RESULT+0x594,travel),s.words(RESULT+0x598,count),s.patch(RESULT+0x59c,'<HHI',excluded,required,mode),s.patch(FACES,'<HH4B' if small else '<HH3H',flags,0,0,1,2,*([255] if small else []))]
 if compressed:patches.append(s.patch(VERTS,'<9H',0,0,0,160,0,0,0,160,0))
 q.check([static],patches,f'face/vertices/travel/mode/count/filter {small}/{compressed}/{travel}/{mode}/{count}/{filters}')
# No-tree, empty leaf, duplicate leaves, overflow-to-all fallback, and all
# branches of a real split. Faces remain valid; the original owns its local list.
for kind,faces in itertools.product(['empty','one','duplicate','overflow','split'],[1,2,40]):
 treepatch=[s.words(GEO+0x34,TREE),s.patch(GEO+8,'<H',faces)]
 n={'empty':0,'one':1,'duplicate':faces,'overflow':faces+1,'split':0}[kind]
 treepatch += [s.words(TREE,(n<<16)|3,TREE+0x100),s.patch(TREE+0x100,'<'+'H'*(faces+1),*([0]*(faces+1)))]
 if kind=='split':
  treepatch += [s.words(TREE,4*16*5,(TREE+8)|1),s.words(TREE+8,(1<<16)|3,TREE+0x100),s.words(TREE+16,(1<<16)|3,TREE+0x100)]
 for lo,hi in [(-10,20),(-10,4),(6,20)]:
  q.check([static,static],treepatch+[s.floats(BOUNDS,lo,-10,-10,1,hi,20,20,1)],f'BSP {kind}/{faces}/{lo}/{hi}, sequential queries')
for faces,mode in itertools.product([0,2,33,40],[0,2]):
 q.check([static],[s.patch(GEO+8,'<H',faces),s.words(RESULT+0x5a0,mode)],f'contact capacity/{faces}/mode{mode}')
# Signed final count with no append; the original uses SETG rather than !=0.
for count in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 q.check([static],[s.patch(GEO+8,'<H',0),s.words(RESULT+0x598,count)],f'no faces/signed existing count{count}')
for cache,travel,mode,stamp in itertools.product([0,CACHE],[0,1,-1],[0,2],[0,17,254,255]):
 q.check([scene(cache),scene(cache)], [s.floats(RESULT+0x594,travel),s.words(RESULT+0x5a0,mode)],f'whole scene/cache{cache}/travel{travel}/mode{mode}/stamp{stamp}',{q.stamp_index:stamp})
for local,default,ignored in itertools.product([0,CACHE],[0,CACHE],[0,1,0xffffffff]):
 q.check([(0x418300,PROBE,[ignored,Q])],[s.words(PROBE+0xb5c,local)],f'probe/local{local}/default{default}/ignored{ignored}',{q.cache_index:default})
for condition in ['empty-cache','invalid-cache','no-scenes','null-grids','no-selected-scene','empty-grid','intersect-reject','disabled-objects','multiple-grids']:
 patches=[s.words(RESULT+0x598,17)];changes={};cache=0
 if condition=='empty-cache':cache=CACHE;patches.append(s.words(CACHE+0xfc4,0))
 if condition=='invalid-cache':cache=CACHE;patches.append(s.floats(CACHE+16,-100,-100,-100,1))
 if condition=='no-scenes':changes[q.scene_index]=NODES+32
 if condition=='null-grids':patches += [s.words(SCENES+0xd4,0),s.words(SCENES+0x100+0xd4,0)]
 if condition=='no-selected-scene':patches.append(s.floats(PROBE,1000,1000,1000,1,1))
 if condition=='empty-grid':
  for x,z in itertools.product(range(2),repeat=2):patches.append(s.words(GRID+0x30+(x*20+z)*48+0x24,0))
 if condition=='intersect-reject':
  for i in range(2):patches.append(s.floats(GEO+64*i+16,100,100,100,1,110,110,110,1))
 if condition=='disabled-objects':patches += [s.patch(INST+8,'<H',2),s.patch(INST+40,'<H',4)]
 if condition=='multiple-grids':
  for x,z in itertools.product(range(2),repeat=2):patches.append(s.words(GRID2+0x30+(x*20+z)*48+0x24,3))
 q.check([scene(cache),wrapper],patches,'scene branch/'+condition,changes)
# Cache overlap short circuits on both sides of every axis. Cached entries
# intentionally need not point to the geometry object's own bounds.
for axis,side in itertools.product(range(3),[-1,1]):
 bounds=[-10.,-10.,-10.,1.,20.,20.,20.,1.]
 if side<0:bounds[axis+4]=-100
 else:bounds[axis]=100
 q.check([scene(CACHE)],[s.words(CACHE+0xfc4,1),s.words(CACHE+36,BOUNDS),s.floats(BOUNDS,*bounds)],f'cached overlap/axis{axis}/side{side}')
# Finite randomized trajectories exercise broadphase bounds and real narrowphase.
rng=random.Random(0x410240)
for i in range(180):
 center=[rng.uniform(-30,30) for _ in range(3)]+[rng.uniform(-2,2),rng.uniform(0,20)]
 velocity=[rng.uniform(-40,40) for _ in range(4)];travel=rng.choice([0.,.125,1.,2.,-1.])
 q.check([scene([0,CACHE][i%2])],[s.floats(PROBE,*center),s.floats(RESULT+0x584,*velocity,travel)],f'random broadphase and contact/{i}')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,n in s.RANGES.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
 coverage[hex(at)]={'covered':len(ins)-len(missing),'total':len(ins),'missing':missing,'excluded':{}}
scope='Four complete original functions: first collision-grid lookup48c940, static sphere virtual4110b0, scene sphere query410240 and probe wrapper418300. Real BSP, face/vertex decoding, stationary and swept contacts, cache/scene/grid traversal execute unchanged. Entire fixture arena, all selected arrays, grid output/stamps, BSP state and semantic returns compare exactly. No substituted game callees, tolerance, traps or NaN classification. Full contact assembly, Rigidbody/scene updates and original browser playability remain unfinished.'
q.save('sphere-query',scope,{'instruction_coverage':coverage})
