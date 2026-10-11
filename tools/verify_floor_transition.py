"""Complete original floor transition with real QB, orientation and timer callees."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'floor-transition.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x10000
CONTEXT,MANAGER,BUCKETS,ORIENTATION,SYMBOLS,P,BODY,BODY2,STATE,STATE2,QUERY,FROM,TO,DIAG,PRINT=[BASE+x for x in
 [0x20,0x100,0x1000,0x5000,0x6000,0x8000,0xa000,0xa400,0xb000,0xb100,0xb200,0xb300,0xb320,0xc000,0xc900]]
TRACK,DISTANCE=0x19fb78fa,0x78384871
memory=bytearray(b'\xad'*SIZE);memory[0x1000:0x5000]=bytes(0x4000)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def number(n):return struct.unpack('<f',struct.pack('<I',n))[0]
identity=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,7.,8.,9.,1.]
put(P+12,'<I',BODY);put(P+0x1528,'<I',STATE);put(P+0x18,'<16f',*identity)
put(P+0x58,'<12f',0,1,0,0,.6,.8,0,1,0,1,0,0);put(P+0x88,'<f',0)
for body in [BODY,BODY2]:
 put(body+0x4c,'<8f',10,20,30,1,9,19,29,1);put(body+0x6c,'<16f',*identity);put(body+0xac,'<4f',12,23,34,1)
for state in [STATE,STATE2]:
 for offset in [0x30,0x38,0x40,0x68]:put(state+offset,'<B',1 if offset==0x40 else 0)
put(ORIENTATION+64,'<I',0);put(DIAG,'<4I',0,0,0,0);put(PRINT,'<2I',DIAG,0)
put(FROM,'<4f',1,2,3,4);put(TO,'<4f',5,6,7,8)
for i,(name,kind,value) in enumerate([(TRACK,1,0),(DISTANCE,2,bits(12))]):
 at=SYMBOLS+i*40;put(BUCKETS+(name&4095)*4,'<I',at);put(at,'<BBHIIII',0,kind,0,name,0,value,0)
initial=bytes(memory)
globals_=[['thug_script_symbol_buckets',0x6f3624,4],['thug_skater_orientation_context',0x7ce5d8,4],
 ['thug_frame_counter',0x7d1ec8,4],['thug_frame_rate',0x684fd0,4],['thug_timer_origin',0x696d64,4],
 ['thug_time_scale',0x67d7c0,4],['thug_timer_offset',0x696d60,4]]
defaults=[BUCKETS,ORIENTATION,60,bits(60),0,bits(1),17];index={g[1]:i for i,g in enumerate(globals_)}
functions={'0x4fc4a0':{'name':'thug_skater_track_movement','this':False,'result':'void','cleanup':0,'stack_args':[0,1,2]},
 '0x4feba0':{'name':'thug_skater_prepare_floor_transition','this':True,'result':'void','cleanup':0,'stack_args':[]}}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[0x4fc4a0,0x4feba0,0x478f60,0x478f00,0x478cf0,0x4023f0,0x4060f0,0x4fe860,0x405170,0x44ece0,0x5be970,0x4172f0])
cpu=oracle.cpu;events=[];outcomes=Counter();labels=[]
def entry(cpu,address,size,user):events.append(Counter())
def branch(cpu,address,size,user):events[-1][{0x4febb8:'surface_enabled',0x4fec76:'transition_prepared',0x4fedc6:'horizontal_rejected',0x4feded:'surface_disabled',0x4fedf4:'disabled_flag_cleared',0x4fedd6:'rejected_flag_cleared'}[address]]+=1
def repair(cpu,address,size,user):events[-1]['basis_repaired']+=1
cpu.hook_add(UC_HOOK_CODE,entry,begin=0x4feba0,end=0x4feba0)
cpu.hook_add(UC_HOOK_CODE,repair,begin=0x405170,end=0x405170)
for at in [0x4febb8,0x4fec76,0x4fedc6,0x4feded,0x4fedf4,0x4fedd6]:cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
fmt='Tracking%d %.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n'
assert load().get_data(0x64b998-0x400000,len(fmt)+1)==fmt.encode()+b'\0'
def diagnostic(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);count=oracle.word(DIAG);assert count<32 and oracle.word(sp+4)==0x64b998
 record=bytes(cpu.mem_read(sp+4,56))+struct.pack('<2I',oracle.word(P+0x1528),oracle.word(P+12))
 cpu.mem_write(DIAG+16+count*64,record);oracle.setword(DIAG,count+1)
 mode,at,value=[oracle.word(DIAG+i*4) for i in [1,2,3]]
 if mode==1:oracle.setword(at,value)
 if mode==2:cpu.mem_write(at,bytes([value&255]))
 cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
def symbol(which,value,integer=False,alias=False,kind=None):
 name=[TRACK,DISTANCE][which];at=SYMBOLS+which*40;k=(1 if integer else 2) if kind is None else kind
 raw=int(value)&0xffffffff if integer else bits(value)
 if alias:
  alias_name=(name&0xffff)|0x12340000
  return [patch(at,'<BBHIIII',0,13,0,name,0,alias_name,at+20),patch(at+20,'<BBHIIII',0,k,0,alias_name,0,raw,0)]
 return [patch(at,'<BBHIIII',0,k,0,name,0,raw,0)]
def case(fn=0x4feba0,args=None,p=(),changes=None,label='floor transition',repeat=1,quiet=False):
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 events.clear();args=[QUERY,PRINT] if args is None else [*args,PRINT]
 stages=oracle.case([(fn,P if fn==0x4feba0 else 0,args)]*repeat,p,{index[k]:v for k,v in (changes or {}).items()});labels.append(label);callbacks=0;derived=set()
 for j,s in enumerate(stages):
  if fn==0x4feba0:
   event=events[j];outcomes.update(event)
   if event['surface_enabled']:
    derived.add(P+0x26c)
    # A later snapshot may copy a NaN produced by the preceding update.
    derived.update(P+0x278+i*4 for i in range(3) if P+0x68+i*4 in derived)
   if event['transition_prepared']:
    body=oracle.word(P+12)
    derived.update([*range(body+0x4c,body+0x5c,4),*range(body+0xac,body+0xb8,4)])
    if event['basis_repaired']:
     derived.update(range(P+0x68,P+0x74,4))
     derived.update(body+0x6c+(row+lane)*4 for row in [0,4,8] for lane in range(3))
    derived.update(P+0x288+i*4 for i in range(3) if body+0x8c+i*4 in derived)
    if quiet:s['quiet_float_fields']=[P+0x28c]
  s['float_fields']=sorted(derived)
  for at,data in s['outputs']:
   if at==DIAG:
    count=int.from_bytes(bytes.fromhex(data),'little');s['callbacks']=count-callbacks;callbacks=count
  s['quiet_double_fields']=[DIAG+24+i*64+j*8 for i in range(callbacks) for j in range(6)]
  outcomes['diagnostics']+=s['callbacks']
 if len(labels)%100==0:print('Original floor-transition cases:',len(labels),flush=True)
 return stages

# The diagnostic reads exact doubles only when its integer QB flag is enabled.
rng=random.Random(0x4feba0)
for enabled in [0,1,0xffffffff,256]:
 for i in range(12):
  values=[rng.uniform(-1e10,1e10) for _ in range(8)]
  case(0x4fc4a0,[rng.randrange(2**32),FROM,TO],symbol(0,enabled,True,alias=i%2==0)+[patch(FROM,'<4f',*values[:4]),patch(TO,'<4f',*values[4:])],label='tracking format and exact promoted double arguments',repeat=2)
for kind in [0,2,3,13]:
 case(0x4fc4a0,[0,0,0],symbol(0,0,True,kind=kind),label='disabled or unsupported tracking does not read null vectors')
for lane in range(6):
 for value in [0x80000000,1,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]:
  address=(FROM if lane<3 else TO)+(lane%3)*4
  case(0x4fc4a0,[0xffffffff,FROM,TO],symbol(0,1,True)+[patch(address,'<I',value)],label='tracking float promotion preserves exact argument representation')

for enabled in [0,1,255]:
 for flags in [(0,0,0),(1,1,1),(255,255,255),(0,1,255),(1,0,1),(255,1,0)]:
  for target in [[0,1,0,1],[1,0,0,1],[0,0,1,-2],[.6,.8,0,0]]:
   p=[patch(STATE+0x40,'<B',enabled),patch(P+0x68,'<4f',*target)]+[patch(STATE+at,'<B',v) for at,v in zip([0x30,0x38,0x68],flags)]
   case(p=p,label='surface and transition flags with repeated preparation',repeat=3)
special=[0.,-0.,1e-30,-1e-30,1e30,-1e30,float('nan'),float('inf'),-float('inf')]
for i in range(256):
 target=[rng.uniform(-4,4),rng.uniform(-4,4),rng.uniform(-4,4),rng.choice([0.,1.,-2.])]
 if i>=128:target=[rng.choice(special) for _ in range(4)]
 value=rng.choice([0.,12.,-12.,1e-30,1e30,3e38,float('nan'),float('inf'),2**31-1,-2**31])
 p=symbol(1,value,isinstance(value,int),i%3==0)+[patch(P+0x68,'<4f',*target),patch(BODY+0xac,'<4f',*[rng.choice(special) if i>=192 else rng.uniform(-100,100) for _ in range(4)])]
 case(p=p,label='complete transition numeric and parameter boundaries',repeat=2 if i%7==0 else 1)
for value in range(bits(.001)-4,bits(.001)+5):
 for lane in [0,2]:
  p=[patch(P+0x68,'<4f',0,1,0,1),patch(P+0x68+lane*4,'<I',value)]
  case(p=p,label='adjacent words at original horizontal threshold')
# Saved position subtraction and distinct X/other-lane product spills.
for value in special+[3e38,-3e38]:
 for distance in [1e-30,3e38,2**31-1,-2**31]:
  p=symbol(1,distance,isinstance(distance,int))+[patch(BODY+0x4c,'<8f',value,value,value,value,value,value,value,value),patch(P+0x68,'<4f',.6,1,.8,1e30)]
  case(p=p,label='wide position offset and saved previous Y arithmetic')
normals=(out/'normals.bin').read_bytes()
for i in range(0,len(normals)//16,199):
 case(p=[patch(P+0x68,'<4f',*struct.unpack_from('<4f',normals,i*16))],label='training collision normals feed original transition',repeat=2)
# Diagnostic mutation precedes the snapshot and all subsequent state/body reads.
for mode,at,value in [(1,P+12,BODY2),(1,P+0x1528,STATE2),(1,P+0x68,bits(0)),(1,P+0x70,bits(.001)),
 (2,STATE+0x40,0),(2,STATE+0x30,255),(1,BODY+0x60,bits(-17)),(1,0x696d60,0xfffffff0),(1,0x7d1ec8,0xffffffff)]:
 case(p=symbol(0,1,True)+[patch(DIAG+4,'<3I',mode,at,value)],label='tracking callback changes values before actual transition',repeat=2)
for i in range(128):
 changes={0x7d1ec8:rng.randrange(2**32),0x684fd0:bits(rng.choice([.5,30,60,144,1000])),0x696d64:rng.randrange(2**32),0x67d7c0:bits(rng.choice([0,.5,1,1.5])),0x696d60:rng.randrange(2**32)}
 case(changes=changes,label='original timer conversion and wrapping timestamps')
# No matrix repair when target equals normalized local up: preserve raw rows,
# including the FLD/FCHS quieting exception already documented for Unicorn.
for value in [0x7fa12345,0xffa12345,0x7fc12345,0x80000000]:
 case(p=[patch(P+0x68,'<4f',1,0,0,1),patch(BODY+0x90,'<I',value)],label='raw forward Y copy then x87 negation',quiet=True)
assert outcomes['transition_prepared'] and outcomes['horizontal_rejected'] and outcomes['surface_disabled']
assert oracle.coverage['0x4fe860'] and oracle.coverage['0x405170'] and not oracle.coverage['0x4172f0']
assert not oracle.heap_events
scope='Complete original floor transition 004feba0 and tracking diagnostic wrapper 004fc4a0 through actual QB getters, normalization, speed-preserving plane projection, orientation repair and timers. Full arena/global bytes compare across repeated calls, flag timestamps, adjacent thresholds, training normals, wide offset arithmetic, numeric aliases and mutations during the debug-output callback. The caller always supplies horizontal up, so the unchanged orientation callee never enters its upward probe; this is observed, not stubbed. Formatted-output service is an instrumented platform boundary; its format and promoted double argument bits compare exactly after the explicitly tracked x87 signaling-NaN quiet-bit correction. Only arithmetic-derived NaN outputs and their subsequent snapshots use classification; raw forward-Y signaling NaNs also use the exact quiet-bit correction. Full floor/ground parents and a playable level remain unfinished.'
fixture={'base':BASE,'memory':'floor-transition-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks',
 'pointer_symbols':[[0x64b998,'thug_skater_tracking_format',fmt]],
 'pointer_exports':[[g[1],g[0]] for g in globals_],
 'pointer_fields':[DIAG+8,*[DIAG+16+i*64 for i in range(32)]],
 'native_callback':{'module':'floor-transition-diagnostics.wasm','export':'fixture_floor_transition_print','slots':[PRINT+4]}}
path=out/'floor-transition-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
adapter=out/'floor-transition-diagnostics.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/floor_transition_diagnostics.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_floor_transition_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
