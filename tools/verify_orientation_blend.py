"""Original orientation blend with actual symbol, vector and matrix callees."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'orientation-blend.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x10000
CONTEXT,MANAGER=BASE+0x20,BASE+0x100
BUCKETS,SYMBOL,ALIAS,LEFT,RIGHT,OUTPUT,P,BODY=[BASE+x for x in [0x1000,0x6000,0x6014,0x7000,0x7020,0x7040,0x8000,0xa000]]
NAME,ALIAS_NAME=0xd8120182,0x12340182
memory=bytearray(b'\xad'*SIZE);memory[0x1000:0x5000]=bytes(0x4000)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def number(word):return struct.unpack('<f',struct.pack('<I',word))[0]
identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,7.,8.,9.,1.]
put(BUCKETS+(NAME&4095)*4,'<I',SYMBOL)
put(SYMBOL,'<BBHIIII',0,2,0,NAME,0,bits(.125),0)
put(P+12,'<I',BODY);put(P+0x18,'<16f',*identity);put(BODY+0x6c,'<16f',*identity)
put(P+0x58,'<4f',0,1,0,0);put(P+0x68,'<4f',0,1,0,0);put(P+0x78,'<4f',0,0,1,0)
put(P+0x88,'<2f',.75,1/60)
put(LEFT,'<4f',1,2,3,4);put(RIGHT,'<4f',1,2,3,4)
initial=bytes(memory)
globals_=[['thug_script_symbol_buckets',0x6f3624,4]];defaults=[BUCKETS]
functions={
 '0x40aed0':{'name':'thug_vector_equal','this':True,'result':'word','cleanup':4},
 '0x43d990':{'name':'thug_vector_lerp','this':False,'result':'word','cleanup':0,'float_args':[3]},
 '0x4fea50':{'name':'thug_skater_blend_orientation','this':True,'result':'void','cleanup':0}}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[int(k,16) for k in functions]+[0x478f00,0x478cf0,0x4023f0,0x405170,0x4a86d0])
events=[];outcomes=Counter();labels=[]
def entry(cpu,address,size,user):events.append(Counter())
def branch(cpu,address,size,user):events[-1][{0x4fea83:'equal_targets',0x4fea92:'rate_reads',0x4feaca:'clamped',0x4feaed:'interpolated',0x4feb31:'cache_rebuilt'}[address]]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,entry,begin=0x4fea50,end=0x4fea50)
for at in [0x4fea83,0x4fea92,0x4feaca,0x4feaed,0x4feb31]:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def case(fn,this,args=(),p=(),label='blend',floats=(),repeat=1,body_alias=False):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 events.clear();stages=oracle.case([(fn,this,list(args))]*repeat,p);labels.append(label)
 for j,s in enumerate(stages):
  fields=list(floats)
  if fn==0x4fea50:
   e=events[j];outcomes.update(e)
   if e['rate_reads']:fields.append(P+0x88)
   if e['interpolated']:
    fields.extend(range(P+0x58,P+0x68,4))
    if e['cache_rebuilt']:fields.extend(range(P+0x28,P+0x38,4))
   if body_alias and e['cache_rebuilt']:fields.extend(range(P+0x18,P+0x48,4))
  s['float_fields']=fields
 if len(labels)%200==0:print('Original orientation cases:',len(labels),flush=True)
 return stages
def rate(value,integer=False,alias=False):
 raw=int(value)&0xffffffff if integer else bits(value)
 if alias:
  return [patch(SYMBOL,'<BBHIIII',0,13,0,NAME,0,ALIAS_NAME,ALIAS),patch(ALIAS,'<BBHIIII',0,1 if integer else 2,0,ALIAS_NAME,0,raw,0)]
 return [patch(SYMBOL,'<BBHIIII',0,1 if integer else 2,0,NAME,0,raw,0)]
rng=random.Random(0x4fea50)
special=[0,0x80000000,1,0x80000001,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for lane in range(4):
 for value in special:
  for same in [False,True]:
   p=[patch(LEFT+lane*4,'<I',value)]
   if same:p.append(patch(RIGHT+lane*4,'<I',value))
   case(0x40aed0,LEFT,[RIGHT],p,label='ordered four-lane equality preserves raw inputs')

# Exact spill order matters for extreme exponents and overlapping output.
for i in range(512):
 if i<256:
  left=[rng.uniform(-100,100) for _ in range(4)];right=[rng.uniform(-100,100) for _ in range(4)];factor=rng.uniform(-4,4)
 else:
  values=[0.,-0.,1e30,-1e30,1e-30,-1e-30,3e38,-3e38,float('nan'),float('inf')]
  left=[rng.choice(values) for _ in range(4)];right=[rng.choice(values) for _ in range(4)];factor=rng.choice(values+[.5,1.,-1.])
 target=[OUTPUT,LEFT,LEFT+4,LEFT-4,RIGHT,RIGHT+4,RIGHT-4][i%7]
 source=LEFT+4 if i%13==0 else RIGHT
 case(0x43d990,0,[target,LEFT,source,bits(factor)],[patch(LEFT,'<4f',*left),patch(RIGHT,'<4f',*right)],
  label='lerp asymmetric wide intermediates and partial aliases',floats=range(target,target+16,4))

vectors=[[0,1,0,0],[0,0,1,0],[1,0,0,0],[0,0,0,0],[0,1,0,1],[1e30,-1e30,1e30,0],
 [1e-30,1e-30,1e-30,7],[float('nan'),1,0,0],[float('inf'),0,0,1]]
blends=[0.,-0.,-.5,.125,.5,1.,1e-30,1e30,float('nan'),float('inf'),-float('inf')]
rates=[0.,.125,-.125,1.,1e-30,1e30,2**24+1,2**31-1,-2**31,float('nan')]
for i in range(640):
 source=vectors[i%len(vectors)];target=vectors[(i//3)%len(vectors)];previous=vectors[(i//7)%len(vectors)]
 blend=blends[(i//5)%len(blends)];dt=[0.,1/60,-1/60,1e30,1e-30,float('nan')][(i//11)%6]
 value=rates[(i//2)%len(rates)];integer=isinstance(value,int)
 cached=identity[:];body=identity[:]
 cached[4:8]=source if i%4==0 else [1,2,3,4]
 body[:4]=[2,3,4,5];body[8:12]=[6,7,8,9]
 p=rate(value,integer,i%3==0)+[patch(P+0x18,'<16f',*cached),patch(BODY+0x6c,'<16f',*body),
   patch(P+0x58,'<4f',*source),patch(P+0x68,'<4f',*target),patch(P+0x78,'<4f',*previous),patch(P+0x88,'<2f',blend,dt)]
 if i%29==0:p.append(patch(BODY+0x6c+(i%4)*4,'<I',0x7f812345))
 body_alias=i%31==0
 if body_alias:p.append(patch(P+12,'<I',P+0x18-0x6c))
 case(0x4fea50,P,p=p,label='full orientation blend numeric gates source preservation and cache rows',repeat=2 if i%9==0 else 1,body_alias=body_alias)

# Boundary cases around a one-frame decrement, with finite training normals.
normals=(out/'normals.bin').read_bytes()
for i in range(0,len(normals)//16,211):
 normal=struct.unpack_from('<4f',normals,i*16)
 for blend in [.12499999,.125,.12500001]:
  p=rate(.125)+[patch(P+0x68,'<4f',*normal),patch(P+0x88,'<2f',blend,1/60)]
  case(0x4fea50,P,p=p,label='training normals at exact decrement threshold',repeat=2)

# A positive wide value can underflow when stored, but the branch still tests
# the wide value. Conversely wide positive/negative overflow must not clamp
# through a prematurely rounded intermediate product.
for blend in [number(1),number(0x80000001),1e-30,1e30,3e38]:
 for value in [1e-30,-1e-30,3e38,-3e38,2**31-1,-2**31]:
  p=rate(value,isinstance(value,int))+[patch(P+0x88,'<2f',blend,1e-30)]
  case(0x4fea50,P,p=p,label='wide blend threshold versus stored float')
assert outcomes['equal_targets'] and outcomes['clamped'] and outcomes['interpolated'] and outcomes['cache_rebuilt']
assert not oracle.heap_events
scope='Complete original orientation blend 004fea50 through actual QB number lookup, ordered vector comparisons, asymmetric-spill vector interpolation, normalization and cached-basis repair. Full physics/body memory and globals compare, including repeated updates, four-lane gates, training normals, integer/alias parameters, partial vector overlaps and cached/body matrix aliasing. Typed arithmetic NaNs compare by classification; raw copied rows and other bytes remain exact. No collision or gameplay callees are stubbed. Physical x87 exception state, complete grounded/floor updates and playable-level integration remain outside this check.'
fixture={'base':BASE,'memory':'orientation-blend-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'orientation-blend-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_orientation_blend_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',dict(oracle.counts))
