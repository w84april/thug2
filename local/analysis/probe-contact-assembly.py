"""Original Rigidbody contact construction with concrete scene/geometry inputs."""
import importlib.util,itertools,json,math,random,struct
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from specimen import ROOT,load
spec=importlib.util.spec_from_file_location('contact_support',ROOT/'local/analysis/contact-assembly-support.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
p=ROOT/'local/analysis';BASE=0x1800000;INST=BASE+0x1000;GEO=BASE+0x2000;FACES=BASE+0x3000;VERTS=BASE+0x6000
GRID=BASE+0xc000;NODES=BASE+0x18000;LIST=BASE+0x1a000;RIGID=BASE+0x600;SHAPES=BASE+0x1b000;MOVING=BASE+0x1b800
memory=bytearray((p/'sphere-query-memory.bin').read_bytes())
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
for x,z in itertools.product(range(2),repeat=2):put(GRID+0x30+(x*20+z)*48+0x24,'<I',1)
put(MOVING+4,'<I',0xffffffff);put(LIST,'<I',INST)
put(RIGID+0x8c,'<H',0);put(RIGID+0x90,'<I',SHAPES);put(RIGID+0x94,'<H',0)
put(RIGID+0x110,'<4f',2,2,1,1);put(RIGID+0x198,'<f',20)
q=s.Assembly(memory,BASE,NODES,[INST+i*32 for i in range(8)],MOVING);hits=Counter();labels=[];outcomes=Counter()
def trace(cpu,at,size,user):hits[at]+=1
q.oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x42c950,end=0x42ced6)
def run(points=(),spheres=(),position=(2,2,1,1),radius=20,patches=(),extra=None,label='contact assembly',repeat=1):
 pp=[s.patch(RIGID+0x8c,'<H',len(points)),s.patch(RIGID+0x94,'<H',len(spheres)),s.floats(RIGID+0x110,*position),s.floats(RIGID+0x198,radius),*patches]
 for i,row in enumerate(spheres):pp.append(s.floats(SHAPES+i*20,*row))
 changes=q.changes(points,[row[:4] for row in spheres],extra)
 steps=q.check([(0x42c950,RIGID,[s.Q])]*repeat,pp,label,changes)
 count=q.oracle.cpu.mem_read(RIGID+0x190,2);assert count[0]<=24,(label,list(count))
 outcomes[f'contacts{count[0]}/active{count[1]}/return{steps[-1]["result"]}']+=1
for n,kind in itertools.product([0,1,2,8,24],['point-hit','point-miss','sphere-hit','sphere-miss']):
 points=[(0,0,-2 if kind=='point-hit' else 2,0)]*n if kind.startswith('point') else []
 spheres=[(0,0,-.5 if kind=='sphere-hit' else 5,0,1)]*n if kind.startswith('sphere') else []
 run(points,spheres,label=f'capacity/{n}/{kind}',repeat=2)
for n in [1,2,8,12]:run([(0,0,-2,0)]*n,[(0,0,-.5,0,1)]*n,label=f'mixed point/sphere capacity/{n}')
for position,offset,kind in itertools.product([(2,2,-2,1),(2,2,0,1),(2,2,.5,1),(2,2,1,1),(12,2,1,1)],[(0,0,-2,0),(0,0,2,0),(-4,0,-1,0),(0,0,0,1)],['point','sphere']):
 run([offset] if kind=='point' else [],[(*offset,1)] if kind=='sphere' else [],position=position,label=f'contact gates/{position}/{offset}/{kind}')
for small,compressed,flags in itertools.product([0,1],[0,1],[0,0x10,0x41,0xffff]):
 patches=[s.patch(GEO+10,'<BB',small,compressed),s.patch(FACES,'<HH4B' if small else '<HH3H',flags,0,0,1,2,*([255] if small else []))]
 if not small:patches.append(s.words(INST+16,BASE+0x1bf00));patches.append(s.patch(BASE+0x1bf00,'<B',255))
 if compressed:patches.append(s.patch(VERTS,'<9H',0,0,0,160,0,0,0,160,0))
 run([(0,0,-2,0)],[(0,0,-.5,0,1)],patches=patches,label=f'geometry encoding and filters/{small}/{compressed}/{flags}')
for stamp,disabled in itertools.product([0,17,254,255],[0,2,4,6]):
 run([(0,0,-2,0)],[(0,0,-.5,0,1)],patches=[s.patch(INST+8,'<H',disabled)],extra={0x693998:stamp},label=f'cache stamps and disabled flags/{stamp}/{disabled}',repeat=2)
for count in [0,1,3]:
 run([(0,0,-2,0)]*count,[(0,0,-.5,0,1)]*count,extra={0x6fa7ec:NODES+32},label=f'no scenes/count{count}')
# Cache bounds that force sphere-probe fallback and a preliminary stamp update.
for radius in [0,.25,1,2,20]:run([],[(0,0,-.5,0,1)],radius=radius,label=f'sphere cache containment/{radius}')
for sphere_radius in [0,.49999,.5,.50001,1,4]:run([],[(0,0,-.5,0,sphere_radius)],label=f'sphere radius boundary/{sphere_radius}')
# Distinct offsets ensure reverse shape and hit order are observable.
run([(1,0,-2,0),(0,1,-3,0),(-1,0,-4,0)],[(0,1,-.5,0,1),(1,0,-.25,0,1)],label='reverse distinct shape order',repeat=2)
rng=random.Random(0x42c950)
for i in range(220):
 position=(*[rng.uniform(-5,15) for _ in range(3)],rng.choice([0.,1.]))
 points=[(*[rng.uniform(-20,20) for _ in range(3)],rng.choice([0.,1.])) for _ in range(i%4)]
 spheres=[(*[rng.uniform(-10,10) for _ in range(3)],0.,rng.uniform(.1,10)) for _ in range((i//4)%4)]
 run(points,spheres,position,label=f'random point/sphere geometry/{i}')
# Rotated triangles at varied scales target cancellation and coincident-point
# normal fallback without forcing any narrowphase result.
for i in range(420):
 scale=[.001,1,100,10000][i%4];vertices=[[rng.uniform(-scale,scale) for _ in range(3)] for _ in range(3)]
 a,b,c=vertices;e=[b[j]-a[j] for j in range(3)];f=[c[j]-a[j] for j in range(3)];normal=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0]];length=math.sqrt(sum(x*x for x in normal));normal=[x/length for x in normal]
 center=[sum(v[j] for v in vertices)/3 for j in range(3)];height=[0,scale*.000001,scale*.1][(i//4)%3]
 position=[center[j]+height*normal[j] for j in range(3)]+[1.]
 lower=[min(v[j] for v in vertices) for j in range(3)];upper=[max(v[j] for v in vertices) for j in range(3)]
 patches=[s.floats(VERTS,*sum(vertices,[])),s.floats(GEO+16,*lower,1,*upper,1),s.floats(GRID,-scale*4,-scale*4,-scale*4,1,scale*4,scale*4,scale*4,1,scale*4,scale*4)]
 run([],[(0,0,0,0,scale*.5)],position=position,radius=scale*2,patches=patches,label=f'rotated triangle cancellation/{i}')
 if q.oracle.cpu.mem_read(RIGID+0x190,1)[0]:
  arm=struct.unpack('<3f',q.oracle.cpu.mem_read(0x6949b0,12));f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
  distance=f32(math.sqrt(f32(f32(f32(arm[0]*arm[0])+f32(arm[1]*arm[1]))+f32(arm[2]*arm[2]))))
  bits=struct.unpack('<I',struct.pack('<f',distance))[0]
  if bits>2:
   for reduction in [0,1,2]:
    radius=struct.unpack('<f',struct.pack('<I',bits-reduction))[0]
    run([],[(0,0,0,0,radius)],position=position,radius=scale*2,patches=patches,label=f'observed contact distance/radius boundary/{i}/{reduction}')
 if i%3==0:
  run([],[(0,0,0,0,scale*.5)],position=vertices[1]+[1.],radius=scale*2,patches=patches,label=f'rotated exact vertex coincidence/{i}')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);ins=list(md.disasm(pe.get_data(0x42c950-0x400000,1415),0x42c950));missing=[hex(i.address) for i in ins if not hits[i.address]]
coverage={'0x42c950':{'covered':len(ins)-len(missing),'total':len(ins),'missing':missing,'excluded':{}}}
scope='Complete42c950 Rigidbody contact assembly using the real broadphase cache builder, segment probes, sphere probes, static geometry/BSP queries and contact arithmetic. Finite valid shapes and at most24contacts; mixed point/sphere reverse ordering, filters, miss writes, cache fallback, stamps, penetration and active-count behavior. Exact whole arena and all observed globals; no tolerance, trap masks, substituted game callees or NaN classification. Full Rigidbody update, complete scene update and playable original training level remain unfinished.'
q.save('contact-assembly',scope,{'instruction_coverage':coverage,'contact_outcomes':dict(outcomes)})
