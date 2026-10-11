"""Original grounded steering, backwards response and release with real QB execution."""
import hashlib,json,math,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
import verify_wall_response as w
from specimen import ROOT,SHA256
out=w.out;report_path=out.parent/'grounded-steering.json';report_path.unlink(missing_ok=True)
prior=w.prior;BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
P,BODY,BODY2,STATE,STATE2,INPUT,CALLBACK=w.P,w.BODY,w.BODY2,w.STATE,w.STATE2,w.INPUT,w.CALLBACK
NAME,MODE,GRAPH=0x1956000,0x1958000,0x1960000
ENTRIES=0x1942400
patch=w.patch;bits=w.bits
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def number(n):return struct.unpack('<f',struct.pack('<I',n))[0]
put(P+4,'<I',0x5bd63b29);put(P+16,'<I',0);put(P+0x1518,'<I',NAME);put(P+0x1524,'<I',MODE)
put(P+0x2ed,'<B',0);put(P+0x302,'<B',0);put(P+0x304,'<B',0);put(P+0x324,'<B',0);put(P+0x388,'<B',0);put(P+0x8c,'<f',1/60)
put(MODE+0x18,'<I',0);put(NAME+0x1331,'<9s',b'ordinary\0')
for state in [STATE,STATE2]:
 for at in [0x20,0x70,0x88]:put(state+at,'<B',0)
for at in [0x40,0x60,0x80,0x1c0]:put(INPUT+at,'<BI',0,0xabcdeffe)
for body in [BODY,BODY2]:
 put(body+0xbc,'<B',0);put(body+0x100,'<I',P)
initial=bytes(memory);oracle=w.oracle;cpu=w.cpu
oracle.base=BASE;oracle.initial=initial
globals_=prior['globals'];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
oracle.globals=globals_;oracle.defaults=defaults
functions=w.functions;functions.clear()
for fn,name,result,heap in [(0x503560,'thug_skater_steer','void',False),(0x4ff920,'thug_skater_handle_backward_motion','void',True),
 (0x4ffb10,'thug_skater_handle_input_release','byte',True),(0x46b7f0,'thug_input_button_clear_pending','void',False)]:
 functions[hex(fn)]={'name':name,'this':True,'result':result,'cleanup':0,'stack_args':[],'memory':heap}
 cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=fn,end=fn)
for at in [0x478f60,0x401b90,0x402500,0x402320,0x4750b0,0x475750,0x462f00,0x46b920,0x44ece0]:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
fields=set(prior['pointer_fields']);known={entry[0] for entry in prior['pointer_exports']}|{w.NATIVE,w.RECEIVE,w.OBJECT}
events=[];outcomes=Counter();labels=[]
def entry(cpu,address,size,user):events.append(Counter())
for at in [0x503560,0x4ff920,0x4ffb10,0x46b7f0]:cpu.hook_add(UC_HOOK_CODE,entry,begin=at,end=at)
# The button helper is also nested inside release; skip that entry when matching
# the outer stage list below, while retaining its instruction coverage.
branches={0x503620:'turn_ramp',0x50365d:'turn_applied',0x50368d:'velocity_turned',0x4ff9db:'backward_threshold_passed',
 0x4ffa49:'reverse_script_requested',0x4ffa6d:'basis_reversed',0x4ffaed:'reversal_script',0x4ffb35:'input_released'}
def branch(cpu,address,size,user):events[-1][branches[address]]+=1
for at in branches:cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.pointers=[]
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert at+len(data)<BASE+SIZE;return at
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2,0,0,key,value,0)) for key,kind,value in entries]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<2I',0,nodes[0] if nodes else 0))
 def symbol(self,name,kind,value):
  bucket=w.BUCKETS+(name&4095)*4;previous=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  at=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,previous));self.buckets[bucket]=at
  if kind==8:self.pointers.append(at+12)
 def numeric(self,name,value,alias=False):
  kind=1 if isinstance(value,int) else 2;raw=value&0xffffffff if kind==1 else bits(value)
  if alias:
   other=(name&0xfff)|0xeeee0000;self.symbol(other,kind,raw);self.symbol(name,13,other)
  else:self.symbol(name,kind,raw)
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(at,'<I',v) for at,v in self.buckets.items()]
def setup(rate=2.,fast=4.,minimum=20.,skip=1,script='native',local=False,alias=False):
 b=Build();numbers=[(0x374e056b,rate),(0x7933a8ef,fast),(0x2bf71eeb,minimum)]
 entries=[(key,1 if isinstance(value,int) else 2,value&0xffffffff if isinstance(value,int) else bits(value)) for key,value in numbers] if local else []
 params=b.structure(entries);b.symbol(0x8cbc89dd,10,params);b.symbol(0xd3d12913,10,params)
 for key,value in numbers:b.numeric(key,value,alias)
 b.symbol(0xb1c84b5a,1,skip)
 for key in [0xa496aebd,0x3a8d6ab2]:
  b.symbol(key,13 if script=='qb' else 8 if script=='native' else 0,8 if script=='qb' else w.NATIVE if script=='native' else 0)
 return b
def call(fn,this=P):return fn,this,[w.PRINT] if functions[hex(fn)]['memory'] else []
def case(calls,b=None,p=(),changes=None,label='grounded',quiet=()):
 b=b or setup();fields.update(b.pointers)
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 events.clear();stages=oracle.case(calls,b.patches()+list(p),{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 callbacks=0;derived=set();event_index=0
 for s in stages:
  event=events[event_index];event_index+=1
  if s['fn']=='0x4ffb10' and event['input_released']:event_index+=1
  outcomes.update(event)
  if event['turn_applied']:
   derived.update(range(P+0x18,P+0x58,4));derived.update(range(BODY+0x6c,BODY+0xac,4))
   if event['velocity_turned']:derived.update([BODY+0xac,BODY+0xb4])
  s['float_fields']=sorted(derived)
  if event['basis_reversed']:s['quiet_float_fields']=list(quiet)
  merged=[]
  for at,data in s['outputs']:
   if at==CALLBACK:
    count=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=count-callbacks;callbacks=count
   if int.from_bytes(bytes.fromhex(data),'little') in known:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged;outcomes['event_or_command_callbacks']+=s['callbacks']
 if len(labels)%100==0:print('Original grounded cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x503560)
# Verify the button helper's precise four-byte store and all surrounding bytes.
for value in [0,1,0xffffffff,0x7fa12345]:
 case([call(0x46b7f0,INPUT+0x1c0)]*2,p=[patch(INPUT+0x1d4,'<I',value)],label='button pending word only')
for left in [0,1,255]:
 for right in [0,1,255]:
  for fast in [0,1,255]:
   for along in [0,1]:
    p=[patch(INPUT+0x60,'<B',left),patch(INPUT+0x80,'<B',right),patch(INPUT+0x40,'<B',fast),patch(P+0x388,'<B',along)]
    case([call(0x503560)]*2,p=p,label='turn input priority and velocity gate')
for elapsed in [0,1,599,600,601,0x7fffffff,0x80000000,0xffffffff]:
 for magnitude in [0.,9.999999,10.,10.000001,100.,float('nan')]:
  for right in [0,1]:
   p=[patch(INPUT+0x60,'<B',1-right),patch(INPUT+0x80,'<B',right),patch(INPUT+0x40,'<B',1),patch(BODY+0xac,'<4f',0,0,magnitude,1),
      patch(INPUT+(0x84 if right else 0x64),'<I',(1000-elapsed)&0xffffffff)]
   case([call(0x503560)],p=p,label='signed ramp age and stored speed threshold')
for i in range(192):
 rate=rng.choice([0.,-0.,.1,-.1,1e-30,1e30,float('nan'),2**24+1,2**31-1,-2**31])
 dt=rng.choice([0.,1/60,-1/60,1e-30])
 p=[patch(INPUT+0x60,'<B',1),patch(INPUT+0x40,'<B',i%2),patch(P+0x8c,'<f',dt),patch(BODY+0xac,'<4f',*[rng.uniform(-100,100) for _ in range(4)])]
 case([call(0x503560)],setup(rate,rate,local=i%3==0,alias=i%5==0),p,label='wide turn parameters and local/global retrieval')
# Matrix multiplication must preserve partial/full input-output aliasing and
# the separate cached/body bases. These finite cases compare every raw bit.
for i in range(32):
 p=[patch(INPUT+0x60,'<B',1),patch(BODY+0x6c,'<16f',*[rng.uniform(-4,4) for _ in range(16)]),
    patch(P+0x18,'<16f',*[rng.uniform(-4,4) for _ in range(16)])]
 case([call(0x503560)]*2,p=p,label='independent nonidentity body and cached matrix inputs')
for start in [P+0x18,P+0x1c,P+0x20]:
 body=start-0x6c
 p=[patch(P+12,'<I',body),patch(body+0xbc,'<B',0),patch(body+0xac,'<4f',1,2,3,1),patch(INPUT+0x60,'<B',1)]
 case([call(0x503560)]*2,p=p,label='body orientation overlaps cached orientation')
# Input release, timestamps and callback mutation use the real event dispatcher.
for flag in [0,1,255]:
 for pressed in [0,1,255]:
  for stamp in [0,999,1000,1001,0x80000000,0xffffffff]:
   p=[patch(STATE+0x20,'<B',flag),patch(STATE+0x24,'<I',stamp),patch(INPUT+0x1c0,'<B',pressed)]
   case([call(0x4ffb10)]*3,p=p,label='input release idempotence and timestamp wrap')
for mode,at,value in [(1,STATE+0x20,1),(2,P+0x378,0xdeadbeef),(2,INPUT+0x1d4,7),(3,0,BODY2),(4,0,STATE2),(5,0,0xfffffff0),(6,STATE+0x20,1)]:
 p=[patch(STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0),patch(CALLBACK+4,'<3I',mode,at,value)]
 if mode==6:p += [patch(w.EM+0x14,'<I',w.RECEIVER),patch(ENTRIES,'<I',0x8ffefb28)]
 case([call(0x4ffb10)]*2,p=p,label='event callback mutation after release writes')
# Ordinary reversal uses raw four-lane negations. The alternate path requests
# a real synchronous native or cached QB script once before setting no more data.
for blocked in [0,1,2,3]:
 for component in [0,0xef24413b,0x0ac90769]:
  for active in [0,1]:
   p=[patch(MODE+0x18,'<I',component),patch(P+0x2ed,'<B',active)]
   if blocked:p.append(patch([0,STATE+0x70,STATE+0x88,P+0x324][blocked],'<B',1))
   case([call(0x4ff920)]*2,setup(skip=0,script='qb'),p,label='backward gates and alternate synchronous QB branch')
names=[b'manual',b'Nose Manual',b'One Foot Nose Manual',b'One Foot Manual',b'Casper',b'Anti Casper']
assert [zlib.crc32(n.lower())^0xffffffff for n in names]==[0xef24413b,0x89b7dbe4,0xa84ef276,0x2fd8e618,0xeff59585,0xc692e824]
for name in names+[b'ordinary',b'',b'MANUAL']:
 for skip in [0,1,256]:
  for script in ['native','qb','missing']:
   p=[patch(P+0x2ed,'<B',1),[NAME+0x1331,(name+b'\0').hex()]]
   case([call(0x4ff920)]*2,setup(skip=skip,script=script),p,label='actual CRC name exclusions and script forms')
for value in [0.,1.,20.,-20.,1e-30,1e30,float('nan'),float('inf'),2**24+1,2**31-1,-2**31]:
 for velocity in [[0,0,-20,1],[0,0,-20.000002,1],[3e38,0,-3e38,1],[1e-30,0,-1e-30,1],[0,0,20,1],[float('nan'),0,-100,1]]:
  case([call(0x4ff920)],setup(minimum=value),[patch(BODY+0xac,'<4f',*velocity)],label='backward threshold strictness and exact parameter types')
# Exact integer-square halfway boundaries. Both products are just below a PC24
# midpoint, but first rounding them to double lands on that midpoint and rounds
# upward. These velocities have the upper squared speed, so original reversal
# occurs whereas the naive double-square comparison would reject it.
for n,velocity in [(884702309,[0.,945173.375,-884701824.,1.]),(1613624363,[0.,1890346.75,-1613623296.,1.])]:
 for sign in [-1,1]:
  before=outcomes['basis_reversed']
  case([call(0x4ff920)],setup(minimum=n*sign),[patch(BODY+0xac,'<4f',*velocity)],label='exact int32 square decides reversal at double-rounding boundary')
  assert outcomes['basis_reversed']==before+1
normals=(out/'normals.bin').read_bytes()
for i in range(0,len(normals)//16,331):
 normal=struct.unpack_from('<4f',normals,i*16)
 p=[patch(BODY+0x8c,'<4f',*normal),patch(BODY+0xac,'<4f',*[-x*300 for x in normal[:3]],1)]
 case([call(0x4ff920)]*2,setup(skip=0,script='qb'),p,label='training normal directions and repeated backward response')
for mode,at,value in [(1,P+0x304,0),(1,STATE+0x70,1),(2,P+0x324,255),(3,0,BODY2),(4,0,STATE2)]:
 for active in [0,1]:
  p=[patch(P+0x2ed,'<B',active),patch(CALLBACK+4,'<3I',mode,at,value)]
  case([call(0x4ff920)]*2,setup(skip=0,script='qb'),p,label='QB handler mutations survive reverse response')
for value in [0x7fa12345,0xffa12345,0x7fc12345,0x80000000]:
 addresses=[BODY+0x6c,BODY+0x98,P+0x18,P+0x38]
 p=[patch(a,'<I',value) for a in addresses]
 case([call(0x4ff920)],p=p,label='raw reversed row signaling NaNs and signed zero',quiet=[*range(BODY+0x6c,BODY+0x7c,4),*range(BODY+0x8c,BODY+0x9c,4),*range(P+0x18,P+0x28,4),*range(P+0x38,P+0x48,4)])
for i in range(64):
 changes={0x7d1ec8:rng.randrange(2**32),0x684fd0:bits(rng.choice([.5,30,60,144,1000])),0x696d64:rng.randrange(2**32),0x67d7c0:bits(rng.choice([0,.5,1,1.5])),0x696d60:rng.randrange(2**32)}
 p=[patch(INPUT+0x60,'<B',1),patch(INPUT+0x40,'<B',1),patch(BODY+0xac,'<4f',0,0,-1,1),patch(STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0)]
 case([call(0x503560),call(0x4ff920),call(0x4ffb10)],setup(minimum=.1,skip=0,script='qb'),p,changes,label='sequential grounded branches with wrapping timers')
assert outcomes['turn_applied'] and outcomes['turn_ramp'] and outcomes['basis_reversed'] and outcomes['reverse_script_requested'] and outcomes['input_released']
assert oracle.coverage['0x4750b0'] and oracle.heap_events and not w.callback_counts
scope='Four original grounded-movement functions: steering 00503560, backward-motion response 004ff920, release 004ffb10 and button pending-word clear 0046b7f0. Actual parameters, timers, CRCs, matrix backend, event delivery, synchronous script allocation/execution and cleanup run unchanged. Tests cover input priority, signed ramp ages, parameter widths, exact int32-square double-rounding boundaries, matrix overlap, training directions, six manual-name CRC branches, native/cached QB forms, callback mutations and sequential updates. Full arena/global bytes, callback ordering and heap effects compare; only arithmetic-derived NaNs use classification, with separately declared exact x87 quiet-bit corrections for raw negations. Native gameplay commands and successful heap allocation are instrumented boundaries; physical x87 transcendental accuracy and complete grounded/floor/startup/rendering integration remain outside this check.'
fixture={'base':BASE,'memory':'grounded-steering-memory.bin','memory_adapter':w.ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':prior['memory_exports'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_command_callbacks',
 'pointer_symbols':prior['pointer_symbols'],'pointer_exports':prior['pointer_exports'],'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],'native_callbacks':prior['native_callbacks']}
path=out/'grounded-steering-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_grounded_steering_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'rebound-callbacks.wasm',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
