"""Compare complete moving-contact routines with original isolated x86 code."""
import itertools,json,math,random,struct
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';BASE=0x1800000;SIZE=0x4000
A=BASE+0x400;B=A+0x100;C=B+0x100;SPHERE=C+0x100;VEL=SPHERE+0x100;ZERO=VEL+0x100;SIDE=ZERO+0x100;EDGE=SIDE+0x100;TIME=EDGE+0x100;COUNT=TIME+32;OUT=COUNT+32;NORMAL=OUT+64
rng=random.Random(0x40ec90);initial=bytes((i*37+19)&255 for i in range(SIZE))
ranges={0x401020:48,0x40e560:984,0x40e940:839,0x40ec90:3402};functions={}
def bind(at,name,n,result,floats=[]):
 functions[hex(at)]={'name':'thug_'+name+'_draft','this':False,'result':result,'stack_args':list(range(n)),'cleanup':16 if at==0x401020 else 0}
 if floats:functions[hex(at)]['float_args']=floats
bind(0x401020,'array_construct',4,'void');functions['0x401020']['pointer_args']=[3]
bind(0x40e560,'moving_segment_sphere',8,'byte',[5]);bind(0x40e940,'sphere_vertex_edge',13,'byte',[10]);bind(0x40ec90,'swept_sphere_triangle',9,'byte',[5])
observe=[*ranges,0x5902e0,0x403210,0x40e280,0x4032a0,0x4032e0,0x402640,0x40aed0,0x4023f0,0x40b860,0x403230,0x403330,0x40b610,0x4024d0,0x402440,0x402470,0x402320]
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,[],[],functions,observe=observe)
hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
def patch(at,fmt,*v):return[at,struct.pack(fmt,*v).hex()]
def floats(at,v):return patch(at,'<'+str(len(v))+'f',*v)
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def call(at,args=()):return at,0,list(args)
def check(calls,patches,label):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 try:oracle.case(calls,patches)
 except Exception:print('Failed',len(labels),label,flush=True);raise
 labels.append(label)
 if len(labels)%500==0:print('Original moving contacts',len(labels),flush=True)
for ctor,count,stride in itertools.product([0x5902e0,0x403210],[0,1,2,5,0xffffffff],[0,4,20,0xfffffffc]):
 check([call(0x401020,[A,stride,count,ctor])],[],'array constructor/stride/count')
segment=[0,0,0,1,10,0,0,1]
for x,y,z,vx,vy in itertools.product([-2,0,5,10,12],[-4,-1,0,1,4],[0,1,2],[-5,0,5],[-5,0,5]):
 check([call(0x40e560,[A,ZERO,SPHERE,VEL,TIME,bits(2),COUNT,OUT])],[floats(A,segment),floats(ZERO,[0,0,0,1]),floats(SPHERE,[x,y,z,1,1]),floats(VEL,[vx,vy,0,0])],f'moving segment/{x}/{y}/{z}/{vx}/{vy}')
for i in range(900):
 scale=[.001,1,1000][i%3]
 seg=[rng.uniform(-scale,scale) for _ in range(8)];center=[rng.uniform(-scale,scale) for _ in range(4)]+[rng.uniform(0,2*scale)]
 v0=[rng.uniform(-scale,scale) for _ in range(4)];v1=[rng.uniform(-scale,scale) for _ in range(4)]
 check([call(0x40e560,[A,ZERO,SPHERE,VEL,TIME,bits(1),COUNT,OUT])],[floats(A,seg),floats(SPHERE,center),floats(ZERO,v0),floats(VEL,v1)],f'random moving segment/{i}')
triangle=[[0,0,0,1],[10,0,0,1],[0,10,0,1]]
for corner in range(3):
 a=triangle[corner];b=triangle[(corner+1)%3];edge=[b[j]-a[j] for j in range(4)];side=[-edge[1]*100,edge[0]*100,0,0]
 for x,y,z,vx,vy in itertools.product([-3,3,13],[-3,3,13],[0,3],[-5,5],[-5,5]):
  patches=[floats(A,triangle[0]),floats(B,triangle[1]),floats(C,triangle[2]),floats(SPHERE,[x,y,z,1,1]),floats(VEL,[vx,vy,-1,0]),floats(ZERO,[0,0,0,1]),floats(SIDE,side),floats(EDGE,edge)]
  check([call(0x40e940,[[A,B,C][corner],SPHERE,VEL,ZERO,A,B,C,SIDE,EDGE,TIME,bits(2),COUNT,OUT])],patches,f'vertex edge choice/{corner}/{x}/{y}/{z}/{vx}/{vy}')
# Inside-vertex early return and plane denominator zero fallback.
for corner in range(3):
 v=triangle[corner];nextv=triangle[(corner+1)%3];edge=[nextv[j]-v[j] for j in range(4)];side=[-edge[1]*100,edge[0]*100,0,0]
 for pos,velocity in [(v,[1,1,1,0]),([v[0]-1,v[1]-1,0,1],[0,0,0,0]),([v[0]-1,v[1]-1,0,1],edge)]:
  check([call(0x40e940,[[A,B,C][corner],SPHERE,VEL,ZERO,A,B,C,SIDE,EDGE,TIME,bits(2),COUNT,OUT])],[floats(A,triangle[0]),floats(B,triangle[1]),floats(C,triangle[2]),floats(SPHERE,pos+[1]),floats(VEL,velocity),floats(ZERO,[0,0,0,1]),floats(SIDE,side),floats(EDGE,edge)],'vertex initial overlap/zero approach/zero denominator')
for x,y,z,velocity,maximum in itertools.product([-4,-1,0,2,5,10,11,14],[-4,-1,0,2,5,10,11,14],[-5,-1,-.5,0,.5,1,5],[[0,0,-1,0],[0,0,1,0],[3,3,-1,0],[-3,-3,1,0],[0,0,0,0]],[.25,2]):
 check([call(0x40ec90,[SPHERE,A,B,C,TIME,bits(maximum),VEL,OUT,NORMAL])],[floats(A,triangle[0]),floats(B,triangle[1]),floats(C,triangle[2]),floats(SPHERE,[x,y,z,1,1]),floats(VEL,velocity)],f'full sweep regions/{x}/{y}/{z}/{velocity}/{maximum}')
for i in range(1000):
 scale=[.001,1,1000][i%3]
 verts=[[rng.uniform(-scale,scale) for _ in range(4)] for _ in range(3)]
 center=[rng.uniform(-2*scale,2*scale) for _ in range(4)]+[rng.uniform(0,2*scale)]
 velocity=[rng.uniform(-2*scale,2*scale) for _ in range(4)]
 check([call(0x40ec90,[SPHERE,A,B,C,TIME,bits(1),VEL,OUT,NORMAL])],[floats(at,v) for at,v in zip([A,B,C,SPHERE,VEL],[*verts,center,velocity])],f'random full sweep/{i}')
for verts in [triangle[::-1],[[0,0,0,1]]*3,[[0,0,0,1],[1,0,0,1],[2,0,0,1]]]:
 for center in [[2,2,1,1,1],[2,2,-1,1,1]]:
  check([call(0x40ec90,[SPHERE,A,B,C,TIME,bits(1),VEL,OUT,NORMAL])],[floats(at,v) for at,v in zip([A,B,C,SPHERE,VEL],[*verts,center,[0,0,-1,0]])],'degenerate or reversed triangle')
# Output/input aliases at the complete routines' ordered writes.
for time,count,out in [(SPHERE,COUNT,OUT),(TIME,VEL,OUT),(TIME,COUNT,A+4),(TIME,COUNT,SPHERE),(TIME,OUT,OUT)]:
 for center in [[5,0,0,1,1],[5,2,0,1,1],[12,2,0,1,1]]:
  check([call(0x40e560,[A,ZERO,SPHERE,VEL,time,bits(1),count,out])],[floats(A,segment),floats(SPHERE,center),floats(VEL,[-4,-4,0,0]),floats(ZERO,[0,0,0,1])],'moving-contact aliased outputs')
for time,out,normal in [(TIME,OUT,OUT),(TIME,SPHERE,NORMAL),(TIME,A,NORMAL),(NORMAL,OUT,NORMAL),(TIME,OUT,A)]:
 for center in [[2,2,3,1,1],[2,2,.5,1,1],[-1,3,.5,1,1],[-1,-1,.5,1,1]]:
  check([call(0x40ec90,[SPHERE,A,B,C,time,bits(1),VEL,out,normal])],[floats(A,triangle[0]),floats(B,triangle[1]),floats(C,triangle[2]),floats(SPHERE,center),floats(VEL,[3,3,-3,0])],'full sweep output aliases')
for radius,maximum in itertools.product([-2,0,2],[-1,0,1]):
 check([call(0x40ec90,[SPHERE,A,B,C,TIME,bits(maximum),VEL,OUT,NORMAL])],[floats(A,triangle[0]),floats(B,triangle[1]),floats(C,triangle[2]),floats(SPHERE,[2,2,.5,1,radius]),floats(VEL,[0,0,-2,0])],'signed radius and maximum time')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,n in ranges.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
 coverage[hex(at)]={'covered':len(ins)-len(missing),'total':len(ins),'missing':missing,'excluded':{}}
scope='Four complete original routines: generic array construction, moving segment/sphere contact, adjacent-edge selection at a known triangle vertex, and full swept sphere/triangle contact. All original geometric callees execute. Whole arena and semantic return comparisons use no tolerance or NaN classification. Scene-wide candidate queries, full contact assembly, complete Rigidbody/scene updates and browser playability remain unfinished.'
fixture={'base':BASE,'memory':'sphere-contact-memory.bin','globals':[],'functions':functions,'function_exports':[[0x5902e0,'thug_segment_initialize'],[0x403210,'thug_sphere_initialize_draft']],'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(p/fixture['memory']).write_bytes(initial);(p/'sphere-contact-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
(p/'sphere-contact-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
