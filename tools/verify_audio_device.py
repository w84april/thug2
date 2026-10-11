"""Original audio update/play paths, with explicit OS interface instrumentation."""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'audio-device.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'sound-voices-fixtures.json').read_text());BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes())
VECTORS=BASE+0x6000;MAPPING=BASE+0x6100;CAMERAS=[BASE+0x6200+i*0x200 for i in range(4)];VIEWPORTS=BASE+0x6a00
CONFIG=BASE+0x5400;SAMPLE=BASE+0x7000;BINDING=SAMPLE+128;CONTROLS=SAMPLE+160;PCM=BASE+0x7200
DEVICE=BASE+0x7300;BUFFER=DEVICE+16;BUFFER2=DEVICE+32;SPATIAL=DEVICE+48;LISTENER=DEVICE+64
BM=BASE+0x7400;SM=BASE+0x7500;LM=BASE+0x7600;DM=BASE+0x7700;CONTEXT=BASE+0x8000;LOG=CONTEXT+128
VOLUME=BASE+0xf000;CHUNK1=VOLUME+256;CHUNK2=VOLUME+512;BUCKETS=BASE+0x1000;TLS=0x2000800
SLOTS=0x6f85c8;VOICES=0x6f7a68;ASSET=0x6f5e68
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
put(SAMPLE,'<16I',0x11111111,22050,0,0,0,36,0xabcdef01,13,0,PCM+128,1,2,3,4,0xeeeeeeee,PCM)
put(BINDING,'<2I',SAMPLE,0);put(CONTROLS,'<4I',bits(75),bits(85),bits(200),0x12345678)
for at,methods in [(DEVICE,DM),(BUFFER,BM),(BUFFER2,BM),(SPATIAL,SM),(LISTENER,LM)]:put(at,'<I',methods)
put(VOLUME,'<6I',bits(50),bits(25),0,0,0,0);put(VOLUME+24,'<5f',25,10,30,1,1020)
for i in range(128):memory[PCM-BASE+i]=(i*37+11)&255
names=['orientation','commit','min','max','position','volume','pan','frequency','stop','release','release_spatial','create','query','lock','unlock','seek','play']
argc=[8,1,3,3,5,2,2,2,1,1,1,4,3,8,5,2,4];CALLBACK=0x3f02000
methods={LM+0x34:0,LM+0x44:1,SM+0x40:2,SM+0x44:3,SM+0x4c:4,BM+0x3c:5,BM+0x40:6,BM+0x44:7,BM+0x48:8,BM+8:9,SM+8:10,DM+0xc:11,BM:12,BM+0x2c:13,BM+0x4c:14,BM+0x34:15,BM+0x30:16}
for at,kind in methods.items():put(at,'<I',CALLBACK+kind*16)
put(CONTEXT,'<32I',0,0xffffffff,0x80004005,0,BUFFER2,SPATIAL,CHUNK1,7,CHUNK2,6,0xffffffff,0,0,4,0,0,SLOTS,VOICES,0x6f8a48,0x67db08,0x6f8a4c,*([0]*11))
# Real global-number lookup for the parent playback's optional checks.
symbol=BASE+0x5500;put(symbol,'<BBHIIII',0,1,0,0xd7bb618d,0,1,0);put(BUCKETS+(0xd7bb618d&4095)*4,'<I',symbol)
initial=bytes(memory);(out/'audio-device-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,width=4,offset=0):
 if at in index:defaults[index[at]]=value;return
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
glob('thug_sound_device',0x7d6a38,DEVICE);glob('thug_audio_slot_count',0x6f8a50,1)
for name,at,value,width in [('thug_audio_spatial_enabled',0x6f8a4c,0,1),('thug_audio_frequency_enabled',0x67da40,1,1),('thug_sound_debug_mode',0x684fa8,0,1),('thug_audio_master_volume',0x67db08,bits(100),4),('thug_audio_play_attempts',0x6f8a48,0,4),('thug_audio_listener',0x6f85c0,LISTENER,4),('thug_math_errno',TLS+8,0,4),('thug_script_symbol_buckets',0x6f3624,BUCKETS,4),('thug_sound_asset_count_a',0x6f85b8,1,4),('thug_sound_asset_count_b',0x6f85b4,0,4)]:glob(name,at,value,width)
exports=[[0x666b34,'thug_audio_spatial_iid',0],[ASSET,'thug_sound_assets_a',0]]
pointer_globals=[]
for i in range(48):
 exports.extend([[SLOTS+i*24,'thug_audio_slots',i*24],[SLOTS+i*24+4,'thug_audio_slots',i*24+4],[VOICES+i*60,'thug_sound_voices',i*60]])
 for j in range(15):
  glob('thug_sound_voices',VOICES+i*60+j*4,0,offset=i*60+j*4)
  if j==2:pointer_globals.append(index[VOICES+i*60+j*4])
for j,value in enumerate([0x12345678,0,bits(100),bits(100),bits(1020),SAMPLE,0]):glob('thug_sound_assets_a',ASSET+j*4,value,offset=j*4)
glob('thug_audio_slots',SLOTS,BUFFER);glob('thug_audio_slots',SLOTS+4,SPATIAL);glob('thug_audio_slots',SLOTS+8,22050)
functions={}
def bind(at,name,argc=0,this=False,result='word',floats=()):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'float_args':list(floats)}
bind(0x406460,'thug_vector_angle_degrees',2,result='double')
bind(0x420a90,'thug_vector_rotate_y',1,True,floats=[0])
bind(0x47cd70,'thug_audio_apply_settings',3,result='void',floats=[2])
bind(0x47d130,'thug_audio_play_buffer',3,floats=[2])
bind(0x47bd20,'thug_sound_play',6,True,floats=[2])
observe=[int(k,16) for k in functions]+[0x47c720,0x47c7e0,0x47bab0,0x47bb20,0x47b480,0x47af40,0x47b2c0,0x478f60,0x4a09e0,0x4a0950,0x623630,0x6236fc]
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,globals_,defaults,functions,observe=observe,instruction_limit=4000000)
cpu=oracle.cpu;cpu.mem_map(CALLBACK,4096);cpu.mem_map(0x2000000,0x10000)
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
last_error=0x12345678;os_calls=Counter();callback_counts=Counter()
def os_service(uc,address,size,user):
 global last_error
 sp=uc.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:uc.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
 elif address==GET_TLS:
  assert oracle.word(sp+4)==7;uc.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
 else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for address in [GET_ERROR,GET_TLS,SET_ERROR]:cpu.hook_add(UC_HOOK_CODE,os_service,begin=address,end=address)
def callback(uc,address,size,user):
 kind=(address-CALLBACK)//16;sp=uc.reg_read(UC_X86_REG_ESP);a=[oracle.word(sp+4+i*4) for i in range(argc[kind])];c=[oracle.word(CONTEXT+i*4) for i in range(32)]
 assert c[0]<200
 args=a[1:] if kind!=13 else [a[1],a[2],a[7],c[6],c[7],c[8],c[9]]
 record=[kind,a[0],*args,*([0]*(7-len(args))),*[oracle.word(c[16]+i*4) for i in range(6)],oracle.word(c[18]),oracle.word(c[17]),oracle.word(c[17]+4),oracle.word(c[19]),uc.mem_read(c[20],1)[0]]
 assert len(record)==20;uc.mem_write(LOG+c[0]*80,struct.pack('<20I',*record));oracle.setword(CONTEXT,c[0]+1)
 if c[10]==kind:
  if c[13]==1:uc.mem_write(c[11],bytes([c[12]&255]))
  else:oracle.setword(c[11],c[12])
 if kind==11:oracle.setword(a[2],c[4])
 if kind==12:oracle.setword(a[2],c[5])
 if kind==13:
  for at,value in zip(a[3:7],c[6:10]):oracle.setword(at,value)
 result=c[2] if c[1]==kind else 0;callback_counts[names[kind]]+=1
 uc.reg_write(UC_X86_REG_EAX,result);uc.reg_write(UC_X86_REG_EIP,oracle.word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+argc[kind]*4)
for i in range(len(names)):cpu.hook_add(UC_HOOK_CODE,callback,begin=CALLBACK+i*16,end=CALLBACK+i*16)
labels=[];fields=set(methods)|{CONTEXT+64,CONTEXT+68,CONTEXT+72,CONTEXT+76,CONTEXT+80};exports.extend([[0x6f8a48,'thug_audio_play_attempts',0],[0x67db08,'thug_audio_master_volume',0],[0x6f8a4c,'thug_audio_spatial_enabled',0]])
rng=random.Random(0x47cd70)
def call(at,*args,this=0):return at,this,list(args)
def case(calls,p=(),changes=None,label='synthetic',floats=()):
 if len(labels)%100==0:print('Original audio device cases:',len(labels),label,flush=True)
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 labels.append(label);stages=oracle.case(calls,p,{index[k]:v for k,v in (changes or {}).items()});count=0
 for s in stages:
  current=oracle.word(CONTEXT) if s is stages[-1] else next((int.from_bytes(bytes.fromhex(v),'little') for a,v in s['outputs'] if a==CONTEXT),count)
  s['callbacks']=current-count;count=current
  float_fields=list(floats)
  # Device float argument words are arithmetic outputs; raw metadata remains exact.
  after=bytearray(initial)
  for at,v in p:after[at-BASE:at-BASE+len(v)//2]=bytes.fromhex(v)
  for previous in stages[:stages.index(s)+1]:
   for at,v in previous['outputs']:after[at-BASE:at-BASE+len(v)//2]=bytes.fromhex(v)
  for i in range(current):
   at=LOG+i*80;kind=struct.unpack_from('<I',after,at-BASE)[0]
   if kind in [0,2,3,4]:float_fields.extend(at+8+j*4 for j in range(6 if kind==0 else 3 if kind==4 else 1))
   if kind==11:fields.add(at+12)
   if kind==12:fields.update([at+8,at+12])
  s['float_fields']=float_fields
 assert last_error==0x12345678
 return stages
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),bits(100),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345]
for i in range(320):
 v=[rng.choice(special) for _ in range(8)] if i<64 else [bits(rng.uniform(-1e20,1e20)) for _ in range(8)]
 case([call(0x406460,VECTORS,VECTORS+16)],p=[patch(VECTORS,'<8I',*v)],label='normalized vector angle wide arithmetic and CRT errors')
for i in range(192):
 v=[rng.choice(special) for _ in range(4)];angle=[0.,-0.,.001,math.pi/2,-math.pi,1e6,1e30,float('nan')][i%8] if i<64 else rng.uniform(-100,100)
 case([call(0x420a90,bits(angle),this=VECTORS)],p=[patch(VECTORS,'<4I',*v)],label='Y rotation finite and NaN angle',floats=[VECTORS,VECTORS+8])
def volume(left=50,right=25,format_=0,position=(25,10,30,1),distance=1020):return [patch(VOLUME,'<6I',bits(left),bits(right),0xaaaaaaaa,0xbbbbbbbb,0xcccccccc,format_),patch(VOLUME+24,'<5f',*position,distance)]
for i in range(400):
 values=[0.,-0.,-1.,.00001,1.,25.,50.,100.,1e30,float('nan'),float('inf')]
 # Unicorn 2.1.4 FYL2X does not pop for zero/negative/NaN inputs.
 # Keep logarithm arguments positive; master/pitch retain nonfinite coverage.
 channels=[0.,.00001,1.,25.,50.,100.,1e30]
 left=channels[i%len(channels)];right=channels[(i//len(channels))%len(channels)];master=values[(i//3)%len(values)];pitch=values[(i//7)%len(values)]
 c={0x67db08:bits(master),0x67da40:i%2,SLOTS+8:[0,100,22050,44100,200000,0xffffffff][i%6],SLOTS+12:[0,100,22050][i%3]}
 case([call(0x47cd70,0,VOLUME,bits(pitch))],p=volume(left,right),changes=c,label='stereo logarithmic volume pan and frequency clamping')
for i in range(20):
 values=[0.,-0.,-1.,float('nan'),-float('inf')]
 case([call(0x47cd70,0,VOLUME,bits(100))],p=volume(values[i%5],values[i//5]),label='silent signed and nonfinite channels bypass logarithms')
for i in range(120):
 primary=0 if i%7==0 else CAMERAS[0]
 p=volume(50 if i%3 else 0,25 if i%4 else 0,3,position=(25 if i%2 else 280,10,30,1),distance=[0,10,1020,1e30,float('nan')][i%5])+[patch(VIEWPORTS+24,'<I',primary)]
 # Rotate the primary/nearest axes to exercise the complete angle/rotation path.
 p += [patch(CAMERAS[0]+0x8c,'<4f',1,0,0,0),patch(CAMERAS[3]+0x8c,'<4f',0,0,-1,0)]
 case([call(0x47cd70,0,VOLUME,bits(123))],p,{0x6f8a4c:1,0x67db08:bits([0,1,25,50,99,100,150,float('nan')][i%8])},'positional device updates multiple listeners and deferred commit')
for i in range(90):
 p=volume(50,25,3 if i%3==0 else 0)+[patch(BINDING+4,'<I',[0,1,0x100,255][i%4]),patch(CONTEXT+4,'<2I',[0xffffffff,11,12,13,16][i%5],0x80004005),patch(CONTEXT+28,'<I',i%14),patch(CONTEXT+36,'<I',13-i%14)]
 c={0x6f8a4c:i%2,SLOTS+16:i%2,SLOTS+20:SAMPLE if i%7==0 else 0,0x6f8a48:0xffffffff if i%9==0 else 0}
 case([call(0x47d130,BINDING,VOLUME,bits(100))],p,c,'buffer cache recreation split writes errors and active state')
for i in range(100):
 p=volume()+[patch(CONTEXT+4,'<2I',16 if i%11==0 else 0xffffffff,0x80004005),patch(symbol+12,'<I',i%2)]
 c={ASSET+8:bits([50,100,150][i%3]),ASSET+12:bits([50,100,200][i%3]),0x684fa8:i%2,0x6f85b8:0 if i%13==0 else 1,SLOTS+20:SAMPLE if i%2 else 0}
 case([call(0x47bd20,0x12345678,VOLUME,bits(90),0 if i%2 else 7,CONTROLS if i%3 else 0,PCM,this=CONFIG)],p,c,'complete game playback naming settings and voice parameters',floats=list(range(VOLUME,VOLUME+20,4)))
# OS callbacks may replace the active buffer or adjust global state between calls.
for kind,address,value,width in [(5,SLOTS,BUFFER2,4),(6,SLOTS+8,44100,4),(6,0x67da40,0,1),(0,0x67db08,bits(25),4),(0,0x6f85c0,0,4),(11,0x6f8a4c,1,1),(15,SLOTS,BUFFER,4),(16,0x6f8a48,99,4)]:
 p=volume(50,25,3 if kind==0 else 0)+[patch(CONTEXT+40,'<4I',kind,address,value,width)]
 fields.add(CONTEXT+44)
 export_name={SLOTS:'thug_audio_slots',SLOTS+8:'thug_audio_slots',0x67da40:'thug_audio_frequency_enabled',0x67db08:'thug_audio_master_volume',0x6f85c0:'thug_audio_listener',0x6f8a4c:'thug_audio_spatial_enabled',0x6f8a48:'thug_audio_play_attempts'}[address]
 exports.append([address,export_name,8 if address==SLOTS+8 else 0])
 case([call(0x47cd70,0,VOLUME,bits(150))] if kind in [0,5,6] else [call(0x47d130,BINDING,VOLUME,bits(150))],p,{0x6f8a4c:int(kind==0)},'device callback changes before subsequent state reads')
case([call(0x47cd70,0,VOLUME,bits(100))],changes={SLOTS:0},label='missing device buffer leaves state untouched')
case([call(0x47d130,BINDING,VOLUME,bits(100))],p=[patch(BINDING,'<I',0)],label='missing sample fails before selecting a slot')
for changes in [{0x7d6a38:0},{0x7cefa8:2},{0x7cefa8:6}]:
 case([call(0x47bd20,0x12345678,VOLUME,bits(90),7,CONTROLS,PCM,this=CONFIG)],changes=changes,label='disabled game playback leaves volume and voices untouched')
scope='Five original routines: normalized vector angle, Y rotation, complete stereo/positional device settings, buffer creation/caching/upload/play and game sound playback through voice setup. Original callees execute with OS audio methods instrumented for call order, semantic arguments, configured results/writes and callback mutation; CRT TLS/last-error services are the only other boundaries. Full fixture memory, tracked globals, device callback traces and returns compare with original x86. SDK trigonometry/logarithms model x87 instructions without claiming physical transcendental accuracy; rotation tests cover finite/NaN angles, with the previously documented infinite-angle difference outside this comparison. Logarithm arguments are positive (including positive infinity): Unicorn 2.1.4 leaves its operand stack unpopped on zero, negative or NaN FYL2X inputs, so those cases are excluded. Nonfinite master/pitch and silent nonpositive/NaN channels are included. Arithmetic NaN outputs compare by classification. Actual browser audio device implementation, audio loading/startup, parent sound dispatcher, wall response and playable training remain incomplete.'
fixture={'base':BASE,'memory':'audio-device-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'audio_device_calls','pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':pointer_globals,'native_callbacks':[{'module':'audio-device-callbacks.wasm','export':'fixture_audio_'+name,'original':CALLBACK+i*16} for i,name in enumerate(names)]}
path=out/'audio-device-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
adapter=out/'audio-device-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/audio_device_callbacks.c'),'-o',str(adapter)],check=True)
assert not oracle.heap_events
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',dict(callback_counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_audio_device_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'audio_device_calls':dict(callback_counts),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'audio-device-memory.bin',adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
