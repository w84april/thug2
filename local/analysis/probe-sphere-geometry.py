"""Compare original point/triangle and stationary sphere/triangle geometry."""
import hashlib,itertools,json,math,random,struct
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';BASE=0x1800000;SIZE=0x4000
PROBE=BASE+0x400;POINT=BASE+0x2000;A=POINT+32;B=A+32;C=B+32;S=C+32;T=S+16;OUT=T+16;NORMAL=OUT+16
rng=random.Random(0x40b860);initial=bytes((i*37+19)&255 for i in range(SIZE))
functions={};ranges={0x403210:10,0x418330:123,0x40b860:1372,0x40f9e0:540}
def bind(at,name,n,result,this=False):
 functions[hex(at)]={'name':name,'this':this,'result':result,'stack_args':list(range(n)),'cleanup':n*4 if this else 0}
bind(0x403210,'thug_sphere_initialize_draft',0,'word',True)
bind(0x418330,'thug_sphere_probe_construct_draft',2,'word',True);functions['0x418330']['float_args']=[1]
bind(0x40b860,'thug_triangle_distance_squared_draft',6,'double')
bind(0x40f9e0,'thug_sphere_triangle_draft',6,'byte')
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,[],[],functions,observe=[*ranges,0x4023f0])
hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def call(at,args=(),this=0):return at,this,list(args)
def check(calls,patches,label):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 try:steps=oracle.case(calls,patches)
 except Exception:print('Failed',len(labels),label,flush=True);raise
 labels.append(label)
 if len(labels)%250==0:print('Original sphere geometry cases',len(labels),flush=True)
 return steps
def vectors(point,a,b,c,radius=1):return [patch(POINT,'<5f',*point,radius),patch(A,'<4f',*a),patch(B,'<4f',*b),patch(C,'<4f',*c)]
triangle=[(0,0,0,1),(10,0,0,1),(0,10,0,1)]
for destination in [PROBE,PROBE+1,PROBE+64]:
 check([call(0x403210,this=destination)]*2,[],'sphere radius-only constructor')
for center_offset in [0,4,16,24,0x500]:
 for radius in [0.,-0.,1.,-2.,1e-20,1e20]:
  center=PROBE+center_offset
  check([call(0x418330,[center,bits(radius)],PROBE)],[patch(center,'<4f',11,-22,33,-44)],f'probe constructor overlap/{center_offset}/{radius}')
# Every triangle region with zero/nonzero perpendicular distance.
for x,y,z in itertools.product([-20,-10,-1,0,.001,2,5,9.999,10,11,20],[-20,-1,0,2,5,10,11,20],[-7,0,7]):
 check([call(0x40b860,[POINT,A,B,C,S,T])],vectors((x,y,z,1),*triangle),f'distance region/{x}/{y}/{z}')
for out_s,out_t in [(0,0),(S,0),(0,T),(S,S),(POINT,POINT+4),(A,A+4),(B,B+4),(C,C+4)]:
 for point in [(-2,-3,4,1),(2,3,4,1),(12,3,4,1),(-2,13,4,1),(2,-13,4,1)]:
  check([call(0x40b860,[POINT,A,B,C,out_s,out_t])],vectors(point,*triangle),'optional or aliased barycentric outputs')
check([call(0x40b860,[POINT,A,B,C,S,T])],vectors((3,-1,4,1),(0,0,0,1),(2,.1,0,1),(1,0,0,1)),'obtuse edge endpoint clamp')
# Translated/rotated/skewed finite triangles; all arithmetic stays exact.
for i in range(600):
 scale=[1e-6,.001,1,1000,1e6][i%5]
 a=[rng.uniform(-scale,scale) for _ in range(3)]+[1]
 b=[a[j]+rng.uniform(-scale,scale) for j in range(3)]+[1]
 c=[a[j]+rng.uniform(-scale,scale) for j in range(3)]+[1]
 point=[a[j]+rng.uniform(-2*scale,2*scale) for j in range(3)]+[1]
 check([call(0x40b860,[POINT,A,B,C,S,T])],vectors(point,a,b,c),f'random distance/{i}')
# Degenerate triangles retain original output/return behavior.
for vertices in [[(0,0,0,1)]*3,[(0,0,0,1),(1,0,0,1),(2,0,0,1)],[(0,0,0,1),(0,0,0,1),(0,2,0,1)]]:
 for point in [(0,0,0,1),(2,3,4,1),(-2,-3,-4,1)]:
  check([call(0x40b860,[POINT,A,B,C,S,T])],vectors(point,*vertices),'degenerate distance')
for x,y,z,radius in itertools.product([-2,0,2,5,10,12],[-2,0,2,5,10,12],[-1,0,.999,1,1.001],[0,.5,1,2,10]):
 check([call(0x40f9e0,[POINT,A,B,C,OUT,NORMAL])],vectors((x,y,z,1),*triangle,radius),f'sphere sidedness/region/tangency/{x}/{y}/{z}/{radius}')
for vertices in [[(0,0,0,1)]*3,[(0,0,0,1),(1,0,0,1),(2,0,0,1)],triangle,triangle[::-1]]:
 for z in [-10,0,10]:
  check([call(0x40f9e0,[POINT,A,B,C,OUT,NORMAL])],vectors((2,3,z,1),*vertices,20),'sphere degenerate or reversed winding')
for i in range(400):
 scale=[.001,1,1000][i%3]
 a=[rng.uniform(-scale,scale) for _ in range(4)]
 b=[a[j]+rng.uniform(-scale,scale) for j in range(4)]
 c=[a[j]+rng.uniform(-scale,scale) for j in range(4)]
 center=[a[j]+rng.uniform(-2*scale,2*scale) for j in range(4)]
 radius=rng.uniform(0,2*scale)
 check([call(0x418330,[POINT,bits(radius)],PROBE),call(0x40f9e0,[PROBE,A,B,C,OUT,NORMAL])],vectors(center,a,b,c,radius),f'actual probe construction then triangle/{i}')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,n in ranges.items():
 instructions=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in instructions if not hits[i.address]]
 coverage[hex(at)]={'covered':len(instructions)-len(missing),'total':len(instructions),'missing':missing,'excluded':{}}
scope='Four complete original routines: radius-only sphere construction, full sphere-probe construction, squared point/triangle distance with optional barycentric outputs, and one-sided stationary sphere/triangle contact. Original normal normalization and constructor/distance callees execute. Finite geometry, all regions, tangency, winding, degeneracy, selected output/constructor aliases and varied scales compare exactly over the whole arena and return values; no tolerance or NaN-classification exceptions. Swept-sphere tests, scene query/contact assembly, complete Rigidbody updates and playability remain unfinished.'
fixture={'base':BASE,'memory':'sphere-geometry-memory.bin','globals':[],'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
# The existing generic checker classifies NaN double returns. This ABI adapter
# strengthens this fixture to compare every return bit, including degeneracy.
functions['0x40b860']['result']='wide';functions['0x40b860']['name']='thug_triangle_distance_squared_bits_draft'
for case in oracle.cases:
 for step in case['steps']:
  if step['fn']=='0x40b860':step['result']=str(int.from_bytes(bytes.fromhex(step['result']),'little'))
(p/fixture['memory']).write_bytes(initial)
(p/'sphere-geometry-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
(p/'sphere-geometry-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
