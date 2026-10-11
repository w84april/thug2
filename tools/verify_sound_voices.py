"""Original voice IDs, slot selection and playback parameters; no device callbacks."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'sound-voices.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'sound-spatial-fixtures.json').read_text());BASE=prior['base'];initial=(out/prior['memory']).read_bytes()
OUTPUT=BASE+0xf000;VOLUME=OUTPUT+128;ASSET=BASE+0x7000;CONTROLS=ASSET+64;PITCH=ASSET+96;PENDING=ASSET+256;MAPPING=BASE+0x6100;VIEWPORTS=BASE+0x6a00
(out/'sound-voices-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,offset=0):index[at]=len(globals_);globals_.append([name,at,4,offset]);defaults.append(value)
glob('thug_audio_slot_count',0x6f8a50,48);glob('thug_audio_slot_cursor',0x6f8a54);glob('thug_sound_pending',0x6f85b0)
for i in range(48):
 glob('thug_sound_voices',0x6f7a68+i*60,0,i*60)
 for j in range(6):glob('thug_audio_slots',0x6f85c8+i*24+j*4,0,i*24+j*4)
functions={}
def bind(at,name,argc=0,result='word',cleanup=0):functions[hex(at)]={'name':name,'this':False,'result':result,'cleanup':cleanup}
bind(0x47c7e0,'thug_audio_slot_active',1,'byte')
bind(0x47c720,'thug_audio_choose_slot',1)
bind(0x47bab0,'thug_sound_id_available',1,'byte',4)
bind(0x47bb20,'thug_sound_available_id',1,'word',4)
bind(0x47af40,'thug_sound_voice_parameters',3,'void',12)
bind(0x47b480,'thug_sound_apply_asset_settings',3,'void',12)
bind(0x4a0950,'thug_camera_at_viewport',1)
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,globals_,defaults,functions,observe=[int(k,16) for k in functions]+[0x47ac50])
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def call(at,*args):return at,0,list(args)
labels=[];rng=random.Random(0x47bd20)
def case(calls,p=(),changes=None,label='synthetic',floats=()):
 if len(labels)%200==0:print('Original voice cases:',len(labels),label,flush=True)
 stages=oracle.case(calls,p,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:s['float_fields']=list(floats)
 return stages
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),bits(100),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]
for i in range(48):
 for active in [0,1,255]:
  for buffer in [0,0xdeadbeef]:case([call(0x47c7e0,i)],changes={0x6f85c8+i*24:buffer,0x6f85d8+i*24:0xa5a5a500|active},label='slot flag and buffer pointer')
for i in range(480):
 count=i%48+1;cursor=[0,1,47,0x7fffffff,0xfffffffe,0xffffffff][(i//6)%6]
 changes={0x6f8a50:count,0x6f8a54:cursor}
 for j in range(48):
  active=1 if i%9==0 else 0 if i%9==1 else rng.choice([0,1,255])
  changes.update({0x6f85c8+j*24:rng.choice([0,ASSET]),0x6f85d8+j*24:0xa5a5a500|active,0x6f85dc+j*24:rng.choice([0,ASSET,ASSET+28,0xabcdef01])})
 case([call(0x47c720,key) for key in [ASSET,ASSET,0,0x11111111]],changes=changes,label='cached reuse last inactive all busy cursor wrap')

for i in range(256):
 changes={0x7d6a38:0 if i%7==0 else 1,0x7cefa8:[0,2,6,7][i%4]};keys=[0,1,2,0xfffffffe,0xffffffff]
 for j in range(48):
  changes.update({0x6f7a68+j*60:rng.choice(keys),0x6f85c8+j*24:rng.choice([0,ASSET]),0x6f85d8+j*24:rng.choice([0,1,255])})
 nodes=[];p=[]
 for j in range(i%6):
  nodes.append(PENDING+j*20);p.append(patch(PENDING+j*20,'<5I',rng.choice(keys),0xa5a5a5a5,0xabababab,0xcccccccc,PENDING+(j+1)*20 if j+1<i%6 else 0))
 changes[0x6f85b0]=nodes[0] if nodes else 0
 case([call(fn,key) for key in keys for fn in [0x47bab0,0x47bb20]],p,changes,'first matching voice and pending IDs while disabled')
# Explicit inactive-first duplicate: a later active voice with the same ID does
# not change the first-record rule. Pending entries still reserve that ID.
for reserve in [0,1]:
 for first_active in [0,1]:
  c={0x6f7a68:7,0x6f7a68+60:7,0x6f85c8:ASSET,0x6f85c8+24:ASSET,0x6f85d8:first_active,0x6f85d8+24:1,0x6f85b0:PENDING if reserve else 0}
  case([call(0x47bab0,7),call(0x47bb20,7)],p=[patch(PENDING,'<5I',7,0,0,0,0)],changes=c,label='inactive first duplicate versus pending reservation')
for start in [0,1,0xfffffffc,0xfffffffe,0xffffffff]:
 p=[patch(PENDING+j*20,'<5I',(start+j)&0xffffffff,0,0,0,PENDING+(j+1)*20 if j<7 else 0) for j in range(8)]
 case([call(0x47bb20,start),call(0x47bb20,start)],p,{0x6f85b0:PENDING},'consecutive pending IDs wrapping zero without reservation')

for i in range(320):
 controls=[rng.choice(special),rng.choice(special),rng.choice(special),rng.randrange(2**32)]
 p=[patch(ASSET,'<7I',0x12345678,0xa5a5a5a5,bits(100),bits(100),special[i%len(special)],0,0),patch(CONTROLS,'<4I',*controls)]
 case([call(0x47af40,OUTPUT,ASSET,0 if i%7==0 else CONTROLS)],p,label='voice parameter defaults raw versus float copies',floats=[OUTPUT+j for j in [4,16,20,24,28]])
for offset in [-8,0,4,8,16,24,32]:
 for i in range(24):
  values=[rng.choice(special) for _ in range(48)];p=[patch(OUTPUT-32,'<48I',*values),patch(ASSET,'<7I',0x11111111,0,bits(100),bits(100),special[i%len(special)],0,0)]
  stages=case([call(0x47af40,OUTPUT,ASSET,OUTPUT+offset)],p,label='overlapping controls retain sequential reads',floats=[OUTPUT+j for j in [4,16,20,24,28]])
  # FLD/FSTP quiet signaling NaNs on physical x87; Unicorn preserves their
  # signaling bit on these copies. With these exact overlaps, the final flags
  # word comes from a just-written floating field (4,16,20,28 respectively).
  # Require the exact quieted payload in this raw propagated word, not a general
  # NaN-class exception for flags. Other flags remain bit-for-bit comparisons.
  if offset in [-8,4,8,16]:stages[0]['quiet_float_fields']=[OUTPUT+40]
for offset in [0,4,8,16]:
 case([call(0x47af40,OUTPUT,OUTPUT+offset,0)],p=[patch(OUTPUT,'<16I',*range(16))],label='default parameters overlap asset checksum')

for i in range(384):
 fmt=[0,1,2,3,4,0xffffffff][i%6];words=[rng.choice(special) for _ in range(5)];pitch=special[(i//6)%len(special)]
 p=[patch(VOLUME,'<6I',*words,fmt),patch(PITCH,'<I',pitch),patch(ASSET,'<7I',0x12345678,0,special[i%len(special)],special[(i//3)%len(special)],0,0,0)]
 case([call(0x47b480,VOLUME,PITCH if i%5 else VOLUME+4,ASSET)],p,{0x7d6a38:0 if i%17==0 else 1,0x7cefa8:[0,1,2,6,7][i%5]},'asset volume pitch scaling and disabled preservation',floats=list(range(VOLUME,VOLUME+20,4))+[PITCH])

for i in range(48):
 mapping=[rng.choice([-1,0,1,2,3,4,5,6,7,8,9]) for _ in range(10)];p=[patch(MAPPING,'<10i',*mapping)]
 for j in range(10):p.append(patch(VIEWPORTS+j*32+24,'<I',0 if (i+j)%4==0 else BASE+0x6200+(j%4)*0x200))
 case([call(0x4a0950,j) for j in range(10)],p,label='direct viewport index including holes and null cameras')

scope='Seven original playback prerequisites: device-slot activity and circular cached-slot selection; first-match voice and pending-ID availability; wrapping available-ID search; voice parameter initialization; asset volume/pitch scaling; direct mapped camera access. Full 64-KiB fixture memory, tracked voice IDs/device-slot records/configuration/cursor globals and returns compare with original x86. Original volume-scaling and activity callees execute; no device callbacks, allocations or playback are substituted. Raw parameter fields remain bit-exact; derived/arithmetic NaN fields compare by classification. Four control/output overlaps propagate a just-written float into the raw flags word: require its exact payload with x87 NaN quieting, correcting the documented Unicorn FLD/FSTP signaling-bit difference; no general NaN-class exception applies to flags. Tests cover slot counts 1..48, unsigned cursor wrap, first inactive cached match, last inactive fallback, all-busy choice, duplicate voice IDs, pending reservations while disabled, ID wrap without reservation, preserved defaults, overlapping controls and camera-map holes. Valid initialized slot counts, acyclic pending lists and valid mapped viewports are caller contracts. Device-buffer playback, the parent dispatcher and full playable training remain incomplete.'
fixture={'base':BASE,'memory':'sound-voices-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'sound-voices-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));assert not oracle.heap_events
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_sound_voices_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'sound-voices-memory.bin']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
quieting=[]
for case_index,c in enumerate(oracle.cases):
 if not any(s.get('quiet_float_fields') for s in c['steps']):continue
 expected=bytearray(initial)
 for at,value in c['patches']:expected[at-BASE:at-BASE+len(value)//2]=bytes.fromhex(value)
 for step_index,s in enumerate(c['steps']):
  for at,value in s['outputs']:expected[at-BASE:at-BASE+len(value)//2]=bytes.fromhex(value)
  for at in s.get('quiet_float_fields',[]):
   word=struct.unpack_from('<I',expected,at-BASE)[0]
   if (word&0x7f800000)==0x7f800000 and word&0x7fffff and not word&0x400000:
    quieting.append({'case':case_index,'step':step_index,'address':hex(at),'unicorn_word':hex(word),'required_x87_word':hex(word|0x400000)})
report['propagated_signaling_nan_corrections']=quieting
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',dict(oracle.counts))
