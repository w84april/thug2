"""Exact comparisons for the original capsule and moving-contact primitives."""
import itertools,json,random,struct
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';BASE=0x1800000;SIZE=0x4000
A=BASE+0x400;B=A+0x100;C=B+0x100;D=C+0x100;CAP=D+0x100;S=CAP+0x100;T=S+32;OUT=T+32;COUNT=OUT+64;DIST=COUNT+32
rng=random.Random(0x402640);initial=bytes((i*37+19)&255 for i in range(SIZE))
ranges={0x402640:1817,0x402d60:412,0x403230:100,0x4032a0:62,0x4032e0:71,0x403330:90,0x40b610:310,0x40e280:729}
functions={}
def bind(at,name,n,result,this=False,floats=[]):
 functions[hex(at)]={'name':'thug_'+name+'_draft','this':this,'result':result,'stack_args':list(range(n)),'cleanup':n*4 if this else 0}
 if floats:functions[hex(at)]['float_args']=floats
bind(0x402640,'segment_distance_squared',3,'double',True)
bind(0x402d60,'segment_point_distance_squared',2,'double',True)
bind(0x403230,'capsule_from_delta',3,'word',True,[2])
bind(0x4032a0,'capsule_from_segment',2,'word',True,[1])
bind(0x4032e0,'capsule_segment',4,'word',True)
bind(0x403330,'capsule_point',2,'byte',True)
bind(0x40b610,'sphere_relative_time',6,'byte',False,[5])
bind(0x40e280,'segment_sphere_intersections',4,'byte')
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,[],[],functions,observe=[*ranges,0x4024d0,0x402440,0x402320])
hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
for at,n in ranges.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=at+n-1)
def patch(at,fmt,*v):return[at,struct.pack(fmt,*v).hex()]
def floats(at,v):return patch(at,'<'+str(len(v))+'f',*v)
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def call(at,args=(),this=0):return at,this,list(args)
def check(calls,patches,label):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 try:oracle.case(calls,patches)
 except Exception:print('Failed',len(labels),label,flush=True);raise
 labels.append(label)
 if len(labels)%500==0:print('Original sweep primitives',len(labels),flush=True)
# Full parameter regions, parallel/opposed directions and degenerate segments.
base=[0,0,0,1,10,0,0,1]
for x,y,z,dx,dy in itertools.product([-15,-1,0,3,10,11,20],[-4,0,4],[0,7],[-12,0,12],[-8,0,8]):
 b=[x,y,z,1,x+dx,y+dy,z,1]
 check([call(0x402640,[B,S,T],A)],[floats(A,base),floats(B,b)],f'segment regions/{x}/{y}/{z}/{dx}/{dy}')
for b in [[-2,-2,0,1,-1,-1,0,1],[12,-2,0,1,11,-1,0,1],[31,-2,0,1,15,-1,0,1]]:
 check([call(0x402640,[B,S,T],A)],[floats(A,base),floats(B,b)],'oblique endpoint region clamp')
for i in range(1800):
 scale=[1e-6,.001,1,1000,1e6][i%5]
 a=[rng.uniform(-scale,scale) for _ in range(8)];b=[rng.uniform(-scale,scale) for _ in range(8)]
 check([call(0x402640,[B,S,T],A)],[floats(A,a),floats(B,b)],f'random segments/{i}')
for a,b in [(base,base),(base,base[4:]+base[:4]),([1,2,3,4]*2,base),(base,[1,2,3,4]*2),([0,0,0,1]*2,[0,0,0,1]*2)]:
 for s,t in [(0,0),(S,0),(0,T),(S,S),(A,A+4),(B,B+4)]:
  check([call(0x402640,[B,s,t],A)],[floats(A,a),floats(B,b)],'parallel/degenerate parameters and output aliases')
for x,y,z in itertools.product([-20,-1,0,.1,5,9.99,10,11,20],[-7,0,7],[-7,0,7]):
 for out in [OUT,0]:
  check([call(0x402d60,[B,out],A)],[floats(A,base),floats(B,[x,y,z,2])],f'point/segment/{x}/{y}/{z}/output{out}')
for i in range(350):
 scale=[1e-6,.001,1,1000,1e6][i%5]
 a=[rng.uniform(-scale,scale) for _ in range(8)];b=[rng.uniform(-scale,scale) for _ in range(4)]
 check([call(0x402d60,[B,OUT],A)],[floats(A,a),floats(B,b)],f'random point/segment/{i}')
for out in [0,OUT,A,A+4,B,B+4]:
 check([call(0x402d60,[B,out],A)],[floats(A,[1,2,3,4]*2),floats(B,[3,4,5,6])],'zero-length point/segment and aliases')
for offset in [0,4,16,32,64]:
 for radius in [0.,-0.,1.,-2.,1e-20,1e20]:
  check([call(0x403230,[CAP+offset,B,bits(radius)],CAP)],[floats(CAP+offset,[1,-2,3,-4]),floats(B,[11,22,-33,44])],f'capsule delta construction/{offset}/{radius}')
  check([call(0x4032a0,[CAP+offset,bits(radius)],CAP)],[floats(CAP+offset,base)],f'capsule segment construction/{offset}/{radius}')
for x,y,z,radius in itertools.product([-1,0,5,10,11],[-2,-1,0,1,2],[-1,0,1],[0,1,2]):
 b=[x,y,z,1,x,y+5,z+3,1]
 patches=[floats(A,base),floats(B,b)]
 check([call(0x4032a0,[A,bits(radius)],CAP),call(0x4032e0,[B,S,T,DIST],CAP),call(0x403330,[B,OUT],CAP)],patches,f'capsule inclusive radius/{x}/{y}/{z}/{radius}')
for out in [0,OUT,CAP,CAP+4,B]:
 for distance in [0,DIST,S,T,CAP+32]:
  check([call(0x4032a0,[A,bits(3)],CAP),call(0x4032e0,[B,S,T,distance],CAP),call(0x403330,[B,out],CAP)],[floats(A,base),floats(B,[5,2,0,1,5,2,1,1])],'capsule optional/aliased outputs')
# Perpendicular gate, past/future roots, maximum time and retained miss output.
for x,y,z,speed,radius,maximum in itertools.product([-5,0,5],[-2,-1,0,1,2],[0,1],[-5,0,5],[0,1,2],[0,.5,2]):
 check([call(0x40b610,[A,B,C,D,S,bits(maximum)])],[floats(A,[0,0,0,1]),floats(B,[0,0,0,0]),floats(C,[x,y,z,1,radius]),floats(D,[speed,0,0,0])],f'relative sphere time/{x}/{y}/{z}/{speed}/{radius}/{maximum}')
for i in range(400):
 scale=[.001,1,1000][i%3]
 origin=[rng.uniform(-scale,scale) for _ in range(4)];v0=[rng.uniform(-scale,scale) for _ in range(4)]
 sphere=[rng.uniform(-scale,scale) for _ in range(4)]+[rng.uniform(0,2*scale)];v1=[rng.uniform(-scale,scale) for _ in range(4)]
 check([call(0x40b610,[A,B,C,D,S,bits(rng.uniform(-2,2))])],[floats(A,origin),floats(B,v0),floats(C,sphere),floats(D,v1)],f'random relative sphere motion/{i}')
for out in [A,A+4,B,B+4,OUT]:
 for x in [-2,5,12]:
  check([call(0x402d60,[B,out],A)],[floats(A,base),floats(B,[x,3,4,5])],'point/segment output aliases in all regions')
# Two, one, no intersections; tangency and entirely-inside segment behavior.
for x,y,z,dx,radius in itertools.product([-10,-2,-1,0,1,2,10],[-2,-1,0,1,2],[0,1],[-20,-2,0,2,20],[0,1,2]):
 check([call(0x40e280,[A,B,COUNT,OUT])],[floats(A,[x,y,z,1,x+dx,y,z,2]),floats(B,[0,0,0,1,radius])],f'segment/sphere roots/{x}/{y}/{z}/{dx}/{radius}')
for i in range(500):
 scale=[.001,1,1000][i%3];a=[rng.uniform(-scale,scale) for _ in range(8)];b=[rng.uniform(-scale,scale) for _ in range(4)]+[rng.uniform(0,2*scale)]
 check([call(0x40e280,[A,B,COUNT,OUT])],[floats(A,a),floats(B,b)],f'random segment/sphere/{i}')
for count,points in [(COUNT,A),(COUNT,A+4),(COUNT,B),(COUNT,OUT),(OUT,OUT),(A,OUT)]:
 for segment in [[-3,0,0,1,3,0,0,1],[-3,1,0,1,3,1,0,1],[0,0,0,1,.5,0,0,1]]:
  check([call(0x40e280,[A,B,count,points])],[floats(A,segment),floats(B,[0,0,0,1,1])],'intersection count/point/input aliases')
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);coverage={}
for at,n in ranges.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));missing=[hex(i.address) for i in ins if not hits[i.address]]
 coverage[hex(at)]={'covered':len(ins)-len(missing),'total':len(ins),'missing':missing,'excluded':{}}
scope='Eight complete original segment/capsule and moving-contact primitives. Exact whole-arena and all return-bit comparisons cover segment distance/parameters, point displacement, capsule constructors/tests, relative-motion sphere time and finite segment/sphere intersections. Original vector callees execute without substitutions. No tolerances or NaN-classification exceptions. Full swept sphere/triangle40ec90 and its40e560/40e940 dependencies, scene contact assembly, complete Rigidbody updates and browser playability remain unfinished.'
fixture={'base':BASE,'memory':'sphere-sweep-memory.bin','globals':[],'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
for address in ['0x402640','0x402d60']:
 functions[address]['result']='wide';functions[address]['name']=functions[address]['name'].replace('_draft','_bits_draft')
 for case in oracle.cases:
  for step in case['steps']:
   if step['fn']==address:step['result']=str(int.from_bytes(bytes.fromhex(step['result']),'little'))
(p/fixture['memory']).write_bytes(initial);(p/'sphere-sweep-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'instruction_coverage':coverage,'scope':scope}
(p/'sphere-sweep-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
