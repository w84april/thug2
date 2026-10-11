"""Original positional sound and complete nearest-camera selection, without playback."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'sound-spatial.json';report_path.unlink(missing_ok=True)
BASE=0x1800000;VECTORS=BASE+0x6000;MAPPING=BASE+0x6100;CAMERAS=[BASE+0x6200+i*0x200 for i in range(4)];VIEWPORTS=BASE+0x6a00
POSITION=BASE+0x6c00;ORIGIN=POSITION+32;CONFIG=BASE+0x5400;VOLUME=BASE+0xf000;OUTPUT=VOLUME+128
memory=bytearray(0x10000);memory[0xf000:]=b'\xa5'*0x1000
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
identity=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
put(CONFIG,'<2I',0,2);put(MAPPING,'<10i',0,-1,1,-1,2,-1,3,-1,-1,-1)
for i,c in enumerate(CAMERAS):
 put(c+0x5c,'<4f',i*100,0,0,1);put(c+0x6c,'<16f',*identity);put(VIEWPORTS+i*32+24,'<I',c)
put(POSITION,'<4f',25,10,30,1);put(ORIGIN,'<4f',100,0,0,1)
initial=bytes(memory);(out/'sound-spatial-memory.bin').write_bytes(initial)
globals_=[];defaults=[];index={}
def glob(name,address,value=0,width=4,offset=0):index[address]=len(globals_);globals_.append([name,address,width,offset]);defaults.append(value)
for name,at,value in [('device',0x7d6a38,1),('mode',0x7cefa8,0),('configuration',0x6f85a8,CONFIG),('default_distance',0x67da34,bits(1020))]:glob('thug_sound_'+name,at,value)
glob('thug_sound_suppressed_a',0x6fc49c,width=1);glob('thug_sound_suppressed_b',0x6fa7d4,width=1)
glob('thug_viewport_mode',0x70134c,3);glob('thug_viewport_mapping',0x67e540,MAPPING)
for i in range(10):glob('thug_viewports',0x701350+i*4,VIEWPORTS+i*32,offset=i*4)
functions={}
def bind(at,name,argc=0,this=False,result='word',floats=()):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'float_args':list(floats)}
bind(0x402470,'thug_vector_difference',3);bind(0x402500,'thug_vector_negated',2);bind(0x423680,'thug_vector_distance',2,result='double')
bind(0x485a00,'thug_camera_position',this=True);bind(0x485a10,'thug_camera_orientation',this=True)
bind(0x4a09e0,'thug_camera_nearest',2);bind(0x47b080,'thug_sound_volume_peak',this=True,result='double')
bind(0x47be10,'thug_sound_spatialize',6,True,'byte',floats=[2])
oracle=ScriptHeapOracle(initial,BASE,BASE+32,BASE+256,globals_,defaults,functions,observe=[int(k,16) for k in functions]+[0x4023f0,0x402320])
labels=[];rng=random.Random(0x47be10)
def call(at,*args,this=0):return at,this,list(args)
def case(calls,p=(),changes=None,label='synthetic',floats=()):
 if len(labels)%200==0:print('Original spatial sound cases:',len(labels),label,flush=True)
 stages=oracle.case(calls,p,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:s['float_fields']=list(floats)
 return stages
special=[0,0x80000000,1,0x80000001,bits(-1),bits(1),bits(100),bits(1020),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345]
for i in range(96):
 words=[rng.randrange(2**32) for _ in range(32)] if i>=len(special) else [special[(i+j)%len(special)] for j in range(32)]
 for delta in [-12,-4,0,4,12,24]:
  a=VECTORS+32;b=a+16;dest=a+delta
  for fn,args in [(0x402470,[dest,a,b]),(0x402500,[dest,a])]:case([call(fn,*args)],p=[patch(VECTORS,'<32I',*words)],label='vector snapshot overlap',floats=range(dest,dest+16,4))
 case([call(0x423680,VECTORS+32,VECTORS+48)],p=[patch(VECTORS,'<32I',*words)],label='wide vector distance')
for camera in CAMERAS:case([call(0x485a00,this=camera),call(0x485a10,this=camera)],label='camera field pointers')
for format_ in [0,1,2,3,4,0xffffffff]:
 for i in range(48):
  words=[rng.choice(special) for _ in range(5)]
  if i<5:words=[bits(-100),bits(100),bits(-100),bits(100),bits(-100)]
  case([call(0x47b080,this=VOLUME)],p=[patch(VOLUME,'<6I',*words,format_)],label='peak magnitude signed ties and NaNs')

# Six real viewport modes, sparse/reordered maps, null camera slots and first
# equal-distance winner. The optional distance pointer can alias source data.
for i in range(240):
 mapping=[0,1,2,3,-1,-1,-1,-1,-1,-1];rng.shuffle(mapping)
 p=[patch(MAPPING,'<10i',*mapping),patch(POSITION,'<4I',*[rng.choice(special[:8]) for _ in range(4)])]
 for j,c in enumerate(CAMERAS):
  values=[0,0,0,0] if i<12 else [rng.choice(special) for _ in range(4)]
  p += [patch(c+0x5c,'<4I',*values),patch(VIEWPORTS+j*32+24,'<I',0 if (i+j)%7==0 else c)]
 output=[OUTPUT,0,POSITION][i%3]
 case([call(0x4a09e0,POSITION,output)],p,{0x70134c:i%6},'nearest camera ordered map and optional distance',floats=[] if not output else [output])
for mode in range(6):case([call(0x4a09e0,POSITION,OUTPUT)],p=[patch(VIEWPORTS+i*32+24,'<I',0) for i in range(4)],changes={0x70134c:mode},label='no camera preserves optional output')

def spatial(range_=bits(1020),curve=0,camera=0,origin=0,p=(),changes=None,label='positional sound',position=POSITION,repeat=1):
 return case([call(0x47be10,VOLUME,position,range_,curve,camera,origin,this=CONFIG)]*repeat,p,changes,label,floats=list(range(VOLUME,VOLUME+20,4))+[VOLUME+40])
for device in [0,1,0xffffffff]:
 for mode in [0,2,6,7]:
  for flag in [0,1,0x100,0xff]:
   for suppress in [0,1,255]:
    spatial(p=[patch(CONFIG,'<I',flag)],changes={0x7d6a38:device,0x7cefa8:mode,0x6fc49c:suppress,0x6fa7d4:0 if flag%2 else suppress},label='device and global suppression gates')
for i in range(128):
 p=[patch(VIEWPORTS+j*32+24,'<I',0 if (i>>j)&1 else CAMERAS[j]) for j in range(4)]
 spatial(curve=i%4,changes={0x70134c:i%6},p=p,label='complete automatic listener selection')
for curve in [0,1,2,3,4,0xffffffff]:
 for range_ in [0,0x80000000,bits(-100),bits(1),bits(100),bits(1020),0x7f800000,0x7fc12345]:
  for distance in [0,bits(1),bits(100)-1,bits(100),bits(100)+1,bits(1020),bits(1100),0x7fc12345]:
   spatial(range_,curve,CAMERAS[0],p=[patch(POSITION,'<4I',distance,0,0,bits(1))],label='four attenuation curves and ordered range boundaries')
for range_ in [bits(100)-1,bits(100),bits(100)+1,bits(105)-1,bits(105),bits(105)+1]:
 spatial(range_,0,CAMERAS[0],p=[patch(POSITION,'<4f',100,0,0,1)],label='range and five-percent outer margin')
for i in range(320):
 # Finite random positions/orientations include arbitrary non-unit axes so the
 # original comparison/clamp behavior is exercised without inventing a clamp.
 p=[patch(POSITION,'<4f',*[rng.uniform(-2000,2000) for _ in range(4)]),patch(ORIGIN,'<4f',*[rng.uniform(-1000,1000) for _ in range(4)]),patch(CAMERAS[0]+0x5c,'<4f',*[rng.uniform(-100,100) for _ in range(4)]),patch(CAMERAS[0]+0x6c,'<16f',*[rng.uniform(-2,2) for _ in range(16)])]
 spatial(bits(rng.uniform(1,5000)),i%4,CAMERAS[0],ORIGIN if i%2 else 0,p,label='full finite panning and alternate range origin',repeat=2)
for i in range(100):
 p=[patch(POSITION,'<4I',*[rng.choice(special) for _ in range(4)]),patch(CAMERAS[0]+0x5c,'<4I',*[rng.choice(special) for _ in range(4)]),patch(CAMERAS[0]+0x6c,'<16I',*[rng.choice(special) for _ in range(16)])]
 spatial(rng.choice(special),i%4,CAMERAS[0],ORIGIN if i%3==0 else 0,p,label='full spatial wide exponent and nonfinite arithmetic')
for offset in [0,4,8,24,28]:
 spatial(bits(1020),0,CAMERAS[0],position=VOLUME+offset,p=[patch(VOLUME,'<12f',*([10.,20.,30.,1.]*3))],label='input overlaps cleared channels or final position copy')

scope='Eight original routines: complete positional sound calculation and nearest-camera selection, both camera field accessors, maximum-magnitude channel lookup, vector difference/negation and vector distance. Original callees execute without callbacks or heap instrumentation being invoked. Full fixture memory, globals, returns and preserved output bytes compare with original x86; arithmetic NaN outputs/returns compare by classification. Covers all six viewport modes with valid populated mappings, sparse/reordered slots, absent cameras, ties, optional-output aliasing, disabled/suppressed audio, four attenuation curves, range boundaries, alternate range origins, arbitrary axes, overlapping position input and wide/nonfinite arithmetic. The spatial routine forces format 3 before panning, making its subsequent format-1 subbranch unreachable for these synchronous calls. Camera startup/update, Windows/browser playback, full wall response and playable training remain incomplete.'
fixture={'base':BASE,'memory':'sound-spatial-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'sound-spatial-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
assert not oracle.heap_events
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_sound_spatial_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'sound-spatial-memory.bin']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
