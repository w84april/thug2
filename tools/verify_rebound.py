"""Original complete rebound path with real event delivery, timers and QB access."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'rebound.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'event-delivery-fixtures.json').read_text());BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
ENTRY,METHODS,BUCKETS,CALLBACK,PRINT,PROGRAM,LOG,HEAP=BASE+0x2000,BASE+0x8400,BASE+0x10000,BASE+0x30000,BASE+0x35f00,BASE+0x40000,BASE+0x60000,BASE+0x80000
EM,OBUCKETS=BASE+0x130000,BASE+0x140100
RECEIVER,RMETHODS,EVENTS,ENTRIES,SCRIPT=BASE+0x141000,BASE+0x141200,BASE+0x142000,BASE+0x142400,BASE+0x144000
P,INPUT,STATE,STATE2,BODY,BODY2,VECTORS=BASE+0x150000,BASE+0x152000,BASE+0x153000,BASE+0x153100,BASE+0x154000,BASE+0x154400,BASE+0x155000
NATIVE,RECEIVE,OBJECT=0x3f01000,0x3f01060,0x3f01070
EV=0x4c03635b

def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,data.hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def f32(f):return struct.unpack('<f',struct.pack('<f',f))[0]
def number(n):return (1,n&0xffffffff) if isinstance(n,int) else (2,bits(n))
identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,11.,22.,33.,1.]
put(P+12,'<I',BODY);put(P+24,'<16f',*identity);put(P+0x68,'<4f',0,1,0,0);put(P+0x130,'<4f',0,0,-1,0)
put(P+0x4e0,'<2I',0,0);put(P+0x150c,'<I',INPUT);put(P+0x1528,'<I',STATE)
put(INPUT+0x1a0,'<B',1);put(STATE+0xb8,'<B',0);put(STATE2+0xb8,'<B',0)
for body,id_ in [(BODY,1),(BODY2,2)]:
 memory[body-BASE:body-BASE+0x400]=bytes(0x400);put(body,'<I',METHODS);put(body+0x14,'<I',id_)
 put(body+0x6c,'<16f',*identity);put(body+0xac,'<4f',120,20,-300,7)
put(OBUCKETS+16,'<I',BODY);put(OBUCKETS+28,'<I',BODY2)
put(METHODS+0x14,'<I',OBJECT);put(RMETHODS+4,'<I',RECEIVE);put(RECEIVER+16,'<I',0)
put(CALLBACK,'<32I',0,0,0,0,P,STATE,BODY2,STATE2,0x696d60,0x7d1ec8,*([0]*22))
# The optional receiver redirects to a real spawned script. Its immediate event
# handler executes cached QB bytecode and the configured native cancellation.
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244)
put(SCRIPT+12,'<3I',PROGRAM+0x1000,SCRIPT+0x100,SCRIPT+0x110)
put(SCRIPT+0x2c,'<I',SCRIPT+0x1c);put(SCRIPT+0x94,'<I',SCRIPT+0x34);put(SCRIPT+0xb0,'<I',100)
put(SCRIPT+0xc8,'<IB',5,1);put(SCRIPT+0xd4,'<I',0x200);put(SCRIPT+0xe0,'<I',EVENTS);put(SCRIPT+0xec,'<2I',0x6478e4,0)
put(SCRIPT+0x100,'<6I',0,0,0,0,0,0);put(ENTRY+8,'<I',2)
put(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0);put(ENTRIES,'<5I',EV,8,0,0,0)
# Four parameter symbols are resolved by the game's real QB getter.
PARAMETERS=[0x0017d543,0x1483fd01,0x1112fb1c,0xb78542c2];symbols=[]
for i,(key,value) in enumerate(zip(PARAMETERS,[100.,45.,50.,200.])):
 at=BASE+0xa700+i*20;bucket=BUCKETS+(key&4095)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,2,0,key,0,bits(value),previous);put(bucket,'<I',at);symbols.append(at)
initial=bytes(memory);(out/'rebound-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for address,value in [(0x7d1ec8,60),(0x684fd0,bits(60)),(0x696d64,0),(0x67d7c0,bits(1)),(0x696d60,0),(0x6f3538,SCRIPT),(0x6f353c,1)]:defaults[index[address]]=value
functions={}
def bind(at,name,argc=0,this=True,result='word',heap=False,diag=False,floats=()):
 functions[hex(at)]={'name':name,'this':this,'result':result,'memory':heap,'diagnostics':diag,'stack_args':list(range(argc)),'cleanup':4*argc if this else 0,'float_args':list(floats)}
bind(0x402320,'thug_vector_copy',1)
bind(0x402340,'thug_vector_add',1)
bind(0x402370,'thug_vector_scale',1,floats=[0])
bind(0x4023c0,'thug_vector_length',result='double')
bind(0x4024d0,'thug_vector_scaled',3,False,floats=[1])
bind(0x402530,'thug_vector_dot',2,False,'double')
bind(0x402550,'thug_vector_cross',3,False)
bind(0x406050,'thug_vector_subtract',1)
bind(0x4196b0,'thug_max_number',2,False,'double',floats=[0,1])
bind(0x4ff670,'thug_skater_try_rebound',result='byte',heap=True,diag=True)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=10000000,
 observe=[int(k,16) for k in functions]+[0x4609f0,0x462f00,0x460470,0x473800,0x475750,0x4750b0,0x478f00,0x44ece0,0x5be970,0x4060f0,0x4023f0,0x404090],
 scope_entries={BASE+0x6000:1,MANAGER+0x300:2,MANAGER+0x400:4})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.cpu.mem_map(NATIVE,4096)
def callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);kind=0 if address==NATIVE else 1 if address==RECEIVE else 2
 owner=cpu.reg_read(UC_X86_REG_ECX) if kind else 0;event=oracle.word(sp+4) if kind else 0;script=oracle.word(sp+8) if not kind else 0
 body=oracle.word(P+12);state=oracle.word(P+0x1528);count=oracle.word(CALLBACK);assert count<200
 record=[kind,owner,script,*([oracle.word(event+j*4) for j in range(5)] if event else [0]*5),body,state,oracle.word(P+0x4e0),oracle.word(P+0x4e4),
  cpu.mem_read(state+0xb8,1)[0],oracle.word(state+0xbc),oracle.word(0x696d60),oracle.word(0x7d1ec8),*[oracle.word(body+0xac+i*4) for i in range(4)],*[oracle.word(P+0x130+i*4) for i in range(4)]]
 cpu.mem_write(CALLBACK+128+count*96,struct.pack('<24I',*record));oracle.setword(CALLBACK,count+1)
 mode=oracle.word(CALLBACK+4);at=oracle.word(CALLBACK+8);value=oracle.word(CALLBACK+12)
 if mode==1:cpu.mem_write(at,bytes([value&255]))
 if mode==2:oracle.setword(at,value)
 if mode==3:oracle.setword(P+12,value)
 if mode==4:oracle.setword(P+0x1528,value)
 if mode==5:oracle.setword(0x696d60,value)
 if mode==6:
  if event:oracle.setword(event+8,0x200)
  else:cpu.mem_write(at,bytes([value&255]))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(4 if kind else 0))
for address in [NATIVE,RECEIVE,OBJECT]:oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=address,end=address)
labels=[];fields=set(prior['pointer_fields']);exports=dict(prior['pointer_exports']);fields.difference_update(range(CALLBACK,CALLBACK+128,4))
exports.update({0x696d60:'thug_timer_offset',0x7d1ec8:'thug_frame_counter'});fields.update([CALLBACK+32,CALLBACK+36])
for at in [METHODS+0x14,RMETHODS+4,SCRIPT+0xec]:fields.add(at)
def call(at,*args,this=0):return (at,this,list(args)+([PRINT] if functions[hex(at)].get('diagnostics') else []))
def case(calls,patches=(),changes=None,label='synthetic',float_fields=()):
 if len(labels)%300==0:print('Original rebound cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});callbacks=0
 for step in stages:
  step['float_fields']=list(float_fields);merged=[]
  for at,data in step['outputs']:
   if at==CALLBACK:
    count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-callbacks;callbacks=count
   if int.from_bytes(bytes.fromhex(data),'little') in exports:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  step['outputs']=merged
 return stages
rng=random.Random(0x4ff670)
# Raw copy is checked bit-for-bit, including signaling NaNs. Arithmetic compares
# only NaN output words by classification; untouched input bytes stay exact.
for i in range(256):
 values=[rng.randrange(2**32) for _ in range(32)]
 if i<16:
  special=[0,0x80000000,1,0x80000001,bits(.001),bits(1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0xffa12345,bits(-1),bits(1e-30),bits(1e30)]
  values=[special[(i+j)%len(special)] for j in range(32)]
 for offset in [-8,0,4,12,24]:
  a=VECTORS+48;b=a+offset;p=[patch(VECTORS,'<32I',*values)]
  for fn in [0x402320,0x402340,0x406050]:
   case([call(fn,b,this=a)],p,label='vector sequential overlap',float_fields=[] if fn==0x402320 else list(range(a,a+16,4)))
 for fn in [0x4024d0,0x402550]:
  for offset in [0,4,16]:
   a=VECTORS+32;b=a+16;output=a+offset
   args=[output,values[0],a] if fn==0x4024d0 else [output,a,b]
   case([call(fn,*args)], [patch(VECTORS,'<32I',*values)],label='snapshot vector output overlap',float_fields=range(output,output+16,4))
 a=VECTORS+32;b=a+16;p=[patch(VECTORS,'<32I',*values)]
 case([call(0x4023c0,this=a),call(0x402530,a,b)],p,label='vector magnitude and dot')
 case([call(0x402370,values[0],this=a)],p,label='four-lane scaling',float_fields=range(a,a+16,4))
# Ordered/equal/unordered max preserves second-operand selection on equality.
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),0x7f800000,0xff800000,0x7fc12345,0x7fa12345,0x7f7fffff,bits(.001)]
for a in special:
 for b in special:case([call(0x4196b0,a,b)],label='max signed zeros and unordered values')
# Complete rebound uses a body in the real object table and the entire event
# dispatcher. Input bytes and timestamps are poisoned outside relevant fields.
arithmetic_fields=[*[body+i for body in [BODY,BODY2] for i in list(range(0x6c,0x9c,4))+list(range(0xac,0xbc,4))],*range(P+24,P+24+48,4)]
outcomes=Counter()
def rebound(p=(),changes=None,label='rebound',repeat=1):
 stages=case([call(0x4ff670,this=P)]*repeat,p,changes,label,arithmetic_fields)
 for s in stages:outcomes['success' if s['result'] else 'not_rebounded']+=1;outcomes['event_callbacks']+=s['callbacks']
 return stages
def settings(values):
 p=[]
 for at,v in zip(symbols,values):
  kind,value=number(v);p += [patch(at+1,'<B',kind),patch(at+12,'<I',value)]
 return p
for pressed in [0,1,255]:
 for cancel in [0,1,255]:
  for first in [0,899,900,901,1000,1001,0x80000000,0xffffffff]:
   for second in [0,899,900,901,1000,1001,0x80000000,0xffffffff]:
    rebound([patch(INPUT+0x1a0,'<B',pressed),patch(STATE+0xb8,'<B',cancel),patch(P+0x4e0,'<2I',second,first)],label='input cooldown cancellation and wrap',repeat=2)
# Threshold rounding, numeric symbol types, missing/unsupported globals.
for value in [0,1,999,1000,1001,2**24+1,2**31-1,-2**31,0.,1000.,float('nan'),float('inf'),float('-inf')]:
 rebound(settings([value,45.,50.,200.]),label='cooldown numeric type boundaries')
for field in range(4):
 for kind in [0,3,13]:
  rebound([patch(symbols[field]+1,'<B',kind),patch(symbols[field]+12,'<I',0xeeeeeeee)],label='missing alias or unsupported parameter')
# Finite angle range and NaNs; FSIN infinity is an existing documented adapter
# difference and is outside this full-branch oracle comparison.
for angle in [-360.,-90.,0.,1.,15.,30.,45.,60.,89.,90.,91.,180.,360.,1e30,float('nan')]:
 for dot in [-1.,-.9,-.5,0.,.5,.9,1.,float('nan')]:
  rebound(settings([100.,angle,50.,200.])+[patch(P+0x130,'<4f',0,0,dot,0)],label='impact angle gate and unordered inputs')
for angle in [0.,1.,15.,30.,45.,60.,89.]:
 threshold=-math.sin(f32(f32(angle-1)*f32(0.01745329238474369)))
 center=bits(threshold)
 for adjacent in [-2,-1,0,1,2]:
  rebound(settings([100.,angle,50.,200.])+[patch(P+0x138,'<I',(center+adjacent)&0xffffffff)],label='adjacent angle-dot boundary words')
velocities=[[0,0,0,7],[0,0,-1e-40,1],[0,0,-.001,1],[0,0,-1,1],[120,20,-300,7],[1e30,-1e30,1e30,1],[float('inf'),0,0,1],[float('nan'),1,0,1]]
for velocity in velocities:
 for loss in [0,50,2**24+1,-50,float('nan'),float('inf')]:
  for minimum in [0,200,-200,1e-30,float('nan')]:
   rebound(settings([100.,45.,loss,minimum])+[patch(BODY+0xac,'<4f',*velocity)],label='reflected speed reduction minimum and fallback')
for word in [bits(.001)-1,bits(.001),bits(.001)+1]:
 rebound([patch(BODY+0xac,'<4I',0,0,word,0)],label='wide magnitude versus stored threshold')
# Training collision normals feed the original normal input; body direction is
# set against each selected face. No collision lookup is claimed by this routine.
normal_data=(out/'normals.bin').read_bytes();normal_count=len(normal_data)//16
assert normal_count>=19934
for i in range(0,19934,157):
 nx,ny,nz,_=struct.unpack_from('<4f',normal_data,i*16)
 rebound([patch(P+0x130,'<4f',nx,ny,nz,0),patch(BODY+0x8c,'<4f',-nx,-ny,-nz,0),patch(BODY+0xac,'<4f',-nx*350,-ny*350,-nz*350,1)],label='training collision normal rebound')
# Callbacks occur before reflection and cancellation reads. They can alter the
# active body/state, normal, velocity, orientation, or final timestamp inputs.
for mode,address,value in [(1,STATE+0xb8,1),(1,STATE+0xb8,255),(2,P+0x130,bits(1)),(2,P+0x138,bits(1)),
 (2,P+0x68,bits(.7)),(2,BODY+0xac,bits(1000)),(2,BODY+0xb4,bits(0)),(3,0,BODY2),(4,0,STATE2),(5,0,0xfffffffa)]:
 for cancel in [0,1]:
  for receiver in [0,RECEIVER]:
   rebound([patch(CALLBACK+4,'<3I',mode,address,value),patch(STATE2+0xb8,'<B',cancel),patch(EM+20,'<I',receiver)],label='event callback changes before physical response')
for requested in [0,1,255]:
 rebound([patch(CALLBACK+4,'<3I',6,STATE+0xb8,requested),patch(EM+20,'<I',RECEIVER)],label='real script event handler requests cancellation')
# Full timer arithmetic, high-word wrap and unsigned-age conversion.
for i in range(192):
 changes={0x7d1ec8:rng.randrange(2**32),0x684fd0:bits(rng.choice([.5,30,59.94,60,144,1000])),0x696d64:rng.randrange(2**32),0x67d7c0:bits(rng.choice([0,.5,1,1.5])),0x696d60:rng.randrange(2**32)}
 rebound([patch(P+0x4e0,'<2I',rng.randrange(2**32),rng.randrange(2**32))]+settings([rng.randrange(2**31),45.,50.,200.]),changes,'complete timer and cooldown arithmetic')
for i in range((HEAP-LOG)//48):fields.update(LOG+i*48+j for j in [16,20,24,28,40])
scope='Ten original routines: complete rebound selection/response and nine vector/scalar prerequisites, including the next movement sweep\'s in-place addition. Uses original cooldown/angle gates, real timers and global QB numeric access, full event delivery and optional real script-handler execution, event-controlled cancellation, velocity reflection, minimum/reduced-speed selection, projection, orientation reconstruction and timestamp writes. Full memory, globals, callbacks and heap order compare with the original x86 instructions; only typed arithmetic NaN outputs/returns compare by classification. Partial-overlap copies remain bit-exact. Covers real training face normals, unsigned timer wrap, input flags, numeric parameter types, boundary comparisons and callback mutation of body/state/physics/timers. Native/object handlers and heap are instrumentation boundaries, not recovered gameplay implementations. Integrated value pools are disabled. Full-branch tests cover finite and NaN impact-angle parameters; infinite-angle FSIN behavior retains the already documented SDK/Unicorn difference and is not validated here. No physical x87 transcendental-accuracy claim. Full wall response, movement loop, sound/rendering/input/startup integration and a playable training level remain incomplete.'
fixture={'base':BASE,'memory':'rebound-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_command_callbacks',
 'pointer_symbols':prior['pointer_symbols'],'pointer_exports':list(exports.items()),'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],
 'native_callbacks':[{'module':'rebound-callbacks.wasm','export':'fixture_rebound_'+n,'original':at} for n,at in [('native',NATIVE),('receiver',RECEIVE),('object',OBJECT)]]}
path=out/'rebound-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
adapter=out/'rebound-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/rebound_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_rebound_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'training_normals':len(range(0,19934,157)),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'rebound-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
