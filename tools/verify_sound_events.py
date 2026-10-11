"""Complete impact dispatch and component entry through real sound/queue callees."""
import hashlib,json,math,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'sound-events.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'audio-device-fixtures.json').read_text());BASE=prior['base'];SIZE=0x80000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
HEAP_CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,CONFIG=BASE+0x1000,BASE+0x5400
SAMPLE=BASE+0x7000;BUFFER=BASE+0x7310;BUFFER2=BASE+0x7320;SPATIAL=BASE+0x7330
CONTEXT=BASE+0x8000;LOG=CONTEXT+128;CALLBACK=0x3f02000;TLS=0x2000800
CLIENT,PEER,LINK,STATE,COMPONENT,OWNER=BASE+0x10000,BASE+0x13000,BASE+0x14000,BASE+0x15000,BASE+0x16000,BASE+0x17000
POSITION=OWNER+0x4c;GRAPH=BASE+0x20000;HEAP_LOG=BASE+0x30000;HEAP=BASE+0x40000
SLOTS=0x6f85c8;VOICES=0x6f7a68;ASSET=0x6f5e68
MATERIAL_NAME,EVENT_PARAMETER=0xa1000001,0xa1000002
names=['orientation','commit','min','max','position','volume','pan','frequency','stop','release','release_spatial','create','query','lock','unlock','seek','play']
argc=[8,1,3,3,5,2,2,2,1,1,1,4,3,8,5,2,4]
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
put(HEAP_CONTEXT,'<8I',HEAP,BASE+SIZE,0,HEAP_LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',HEAP_CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);put(MANAGER+0x12c,'<I',MANAGER+0x400)
def node(at,methods,value,previous,next_):put(at,'<5I',methods,value,0,previous,next_)
for k in range(3):node(PEER+k*20,0x6474cc+k*4,0xffffffff,PEER+k*20,PEER+k*20)
put(PEER+0x3c,'<I',1);put(PEER+0x60,'<I',1)
node(CLIENT+0x1e8c,0x647578,0xffffffff,LINK,LINK);node(LINK,0x647578,PEER,CLIENT+0x1e8c,CLIENT+0x1e8c)
put(CLIENT+8,'<I',0xfffffffa);put(STATE,'<3I',0,0,CLIENT)
put(COMPONENT+0xc,'<I',OWNER);put(COMPONENT+0x24,'<f',1);put(POSITION,'<4f',25,10,30,1)
# Use a normal volume format on paths that return before positional fields exist.
put(CONFIG,'<2I',1,0)
initial=bytes(memory);(out/'sound-events-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,width=4,offset=0):
 if at in index:defaults[index[at]]=value;return
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
for n,a in [('materials',0x6968d0),('events',0x6968e8)]:
 for j in range(6):glob('thug_sound_'+n,a+j*4,0,offset=j*4)
for j,value in enumerate([0x12345678,0xabcdef01,0x87654321]):glob('thug_random_state',0x690fd4+j*4,value,offset=j*4)
glob('thug_network_state',0x7cce14,STATE)
exports=prior['pointer_exports'][:]
checksums=[zlib.crc32(x)^0xffffffff for x in [b'impact_a.wav',b'impact_b.wav']]
for i,checksum in enumerate(checksums):
 exports.append([ASSET+i*28,'thug_sound_assets_a',i*28])
 for j,value in enumerate([checksum,0,bits(100),bits(100),bits(1020),SAMPLE,0]):glob('thug_sound_assets_a',ASSET+i*28+j*4,value,offset=i*28+j*4)
glob('thug_sound_asset_count_a',0x6f85b8,2)
queue_exports=[[0x6474cc+4*k,'thug_'+n+'_queue_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]+[[0x647578+4*k,'thug_'+n+'_node_methods'] for k,n in enumerate(['plain','reliable','sequenced'])]
exports+=queue_exports;queue_pointers={x[0] for x in queue_exports}
fields=set(prior['pointer_fields'])|{a for a in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[a-BASE:a-BASE+4],'little') in queue_pointers}
functions={'0x444bb0':{'name':'thug_sound_dispatch_impact','this':False,'result':'void','cleanup':0,'memory':True,'stack_args':list(range(7)),'float_args':[3,4,5]},
 '0x518dd0':{'name':'thug_sound_component_impact','this':True,'result':'void','cleanup':8,'memory':True,'stack_args':[0,1],'float_args':[0]}}
observe=[0x444bb0,0x518dd0,0x444480,0x444310,0x476af0,0x479020,0x4767c0,0x444830,0x444760,0x4445b0,0x4549f0,0x532ea0,0x459e50,0x457eb0,0x454fa0,0x47b030,0x47b760,0x47be10,0x47ac50,0x47acf0,0x47bd20,0x47d130,0x47cd70,0x47bab0,0x47bb20,0x47af40,0x5480a0,0x6236fc]
oracle=ScriptHeapOracle(initial,BASE,HEAP_CONTEXT,MANAGER,globals_,defaults,functions,observe=observe,instruction_limit=4000000,scope_entries={MANAGER+0x200:1,MANAGER+0x400:4})
cpu=oracle.cpu;cpu.mem_map(CALLBACK,4096);cpu.mem_map(0x2000000,0x10000)
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
last_error=0x12345678;os_calls=Counter();callback_counts=Counter();padding_entries=0
# Exactly one undefined packet tail byte is made deterministic. All eleven
# defined payload bytes and the subsequent real queue operations compare.
def seed_padding(uc,address,size,user):
 global padding_entries
 uc.mem_write(uc.reg_read(UC_X86_REG_ESP)-0x95,b'\0');padding_entries+=1
cpu.hook_add(UC_HOOK_CODE,seed_padding,begin=0x444bb0,end=0x444bb0)
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
 uc.mem_write(LOG+c[0]*80,struct.pack('<20I',*record));oracle.setword(CONTEXT,c[0]+1)
 if c[10]==kind:
  if c[13]==1:uc.mem_write(c[11],bytes([c[12]&255]))
  else:oracle.setword(c[11],c[12])
 if kind==11:oracle.setword(a[2],c[4])
 if kind==12:oracle.setword(a[2],c[5])
 if kind==13:
  for at,value in zip(a[3:7],c[6:10]):oracle.setword(at,value)
 callback_counts[names[kind]]+=1;uc.reg_write(UC_X86_REG_EAX,c[2] if c[1]==kind else 0)
 uc.reg_write(UC_X86_REG_EIP,oracle.word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+argc[kind]*4)
for i in range(len(names)):cpu.hook_add(UC_HOOK_CODE,callback,begin=CALLBACK+i*16,end=CALLBACK+i*16)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.changes={}
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert len(self.data)<0x8000;return at
 def words(self,*values):return self.alloc(struct.pack('<'+'I'*len(values),*values))
 def text(self,value):return self.alloc(value+b'\0')
 def structure(self,components):
  entries=[self.alloc(struct.pack('<BBHIII',kind*2,0xa5,0xa5a5,name,value,0)) for name,kind,value in components]
  for a,b in zip(entries,entries[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.words(0xadadadad,entries[0] if entries else 0)
 def symbol(self,name,kind,value):
  bucket=BUCKETS+(name&4095)*4;previous=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  at=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,previous));self.buckets[bucket]=at;return at
 def array(self,values):return self.words(0x1400,len(values),values[0] if len(values)==1 else self.words(*values))
 def table(self,which,entries):
  buckets=self.alloc(bytes(4*12))
  for key,value in entries:struct.pack_into('<3I',self.data,buckets-GRAPH+(key&3)*12,key,value,0)
  address=0x6968d0 if which=='materials' else 0x6968e8
  self.changes.update({address:2,address+4:buckets,address+8:len(entries),address+12:0xdeadbeef,address+16:buckets})
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(k,'<I',v) for k,v in self.buckets.items()]
def graph(mode='direct',bounds=(100,100,100,0)):
 b=Build();clips=[]
 for i in range(2):
  components=[] if mode=='missing_path' else [(0x07713c7b,3,b.text([b'sfx\\impact_a.wav',b'other/impact_b.wav'][i]))]
  components += [(key,2,bits(value)) for key,value in zip([0xfa3e14c5,0x1c5ebb24,0x0693daaf,0x4391992d],bounds)]
  components.append((0xdbc4c4db,1,i+1));clips.append(b.structure(components))
 if mode in ['weighted','threshold','empty']:
  entries=[]
  if mode!='empty':
   entries=[b.structure([(0x9ee9a09a,2,bits(50)),(0x25f654c8,10,clips[0])]),b.structure([(0x25f654c8,12,b.array(clips))])]
  settings=b.structure([(EVENT_PARAMETER,12,b.array(entries))])
 else:settings=b.structure([(EVENT_PARAMETER,10,clips[0])])
 fallback=b.structure([(0x5c969c50,10,settings)])
 specific=b.structure([(0x5c969c50,10,b.structure([]) if mode=='event_fallback' else settings)])
 if mode=='material_fallback':specific=b.structure([])
 if mode!='missing_settings':
  b.symbol(MATERIAL_NAME,10,specific);b.symbol(0x5b80cfcb,10,fallback);b.symbol(0x64967688,10,fallback)
 b.table('materials',[(7,b.words(7,MATERIAL_NAME))]);b.table('events',[(5,b.words(5,0x67d72d44,EVENT_PARAMETER))])
 return b
labels=[];rng=random.Random(0x444bb0)
def dispatch(volume=100,pitch=100,selection=100,network=0,event=5,material=7):return 0x444bb0,0,[event,material,POSITION,bits(volume),bits(pitch),bits(selection),network,0]
def component(intensity,material=7):return 0x518dd0,COMPONENT,[bits(intensity),material,0]
def case(calls,b,p=(),changes=None,label='synthetic'):
 if len(labels)%100==0:print('Original impact cases:',len(labels),label,flush=True)
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff)
 c=dict(b.changes);c.update(changes or {});patches=b.patches()+list(p);labels.append(label)
 stages=oracle.case(calls,patches,{index[k]:v for k,v in c.items()});count=0
 after=bytearray(initial)
 for at,data in patches:after[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
 for s in stages:
  for at,data in s['outputs']:
   after[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
   if int.from_bytes(bytes.fromhex(data),'little') in queue_pointers:fields.add(at)
  current=struct.unpack_from('<I',after,CONTEXT-BASE)[0];s['callbacks']=current-count;count=current;s['float_fields']=[]
  for i in range(current):
   at=LOG+i*80;kind=struct.unpack_from('<I',after,at-BASE)[0]
   if kind in [0,2,3,4]:s['float_fields'].extend(at+8+j*4 for j in range(6 if kind==0 else 3 if kind==4 else 1))
   if kind==11:fields.add(at+12)
   if kind==12:fields.update([at+8,at+12])
 assert last_error==0x12345678
 return stages
# Selection/fallback, ordered remapping and notification before audibility.
for i in range(336):
 mode=['direct','weighted','threshold','empty','event_fallback','material_fallback','missing_path','missing_settings'][i%8]
 bounds=[(100,100,100,0),(100,0,100,0),(150,50,75,25),(20,120,25,125),(0,0,0,0),(100,100,100,100)][(i//8)%6]
 volume=[0,1,25,50,100,150,-10][(i//3)%7];pitch=[0,25,100,150,-10,float('nan')][(i//5)%6];selection=[0,49.99,50,50.01,100,float('nan')][i%6]
 p=[patch(POSITION,'<4f',*[ (25,10,30,1),(280,10,30,1),(5000,0,0,1),(0,0,0,1)][(i//7)%4])]
 c={0x6f8a4c:(i//2)%2,SLOTS+20:SAMPLE if i%3 else 0,0x67db08:bits([0,25,100,150][i%4])}
 case([dispatch(volume,pitch,selection,[0,1,0x100,0x101][(i//2)%4],event=0xad000005,material=0xbc000007)],graph(mode,bounds),p,c,'selection fallback remapping attenuation and real network enqueue')
for i in range(120):
 intensity=[0.,-0.,.001,.5,1.,1.5,-1.,float('nan')][i%8];scale=[0.,.25,1.,2.,-1.][(i//3)%5]
 p=[patch(COMPONENT+0x24,'<f',scale),patch(CONTEXT+4,'<2I',[0xffffffff,11,12,13,16][i%5],0x80004005)]
 case([component(intensity)],graph('weighted' if i%2 else 'direct',(120,40,100,0)),p,{0x6f8a4c:i%2},'component percentage scaling and complete dispatch with device failures')
# Queue conditions, disabled paths, suppression and missing assets.
for i in range(32):
 p=[patch(PEER+0x60,'<I',[0,1,8,9][i%4])]
 if i%8==0:p.append(patch(CLIENT+0x1e8c+12,'<I',CLIENT+0x1e8c))
 c={0x6f85b8:0 if i%5==0 else 2,0x6fc49c:(i//2)%2,0x6fa7d4:i%2}
 p.append(patch(CONFIG,'<I',i%2))
 case([dispatch(network=1)],graph(),p,c,'peer eligibility suppression and unloaded sound')
for c in [{0x7d6a38:0},{0x7cefa8:2},{0x7cefa8:6}]:case([dispatch(network=1),component(.5)],graph(),changes=c,label='disabled dispatch and component')
# The original packet truncates/wraps coordinates and intensities independently.
for i in range(48):
 values=[0.,-0.,32767.99,32768.,-32769.,65536.,1e30,float('nan'),float('inf'),-float('inf')]
 p=[patch(POSITION,'<4f',values[i%10],values[(i+3)%10],values[(i+7)%10],1),patch(CONFIG,'<I',0)]
 # Suppression avoids device reads of uninitialized positional stack fields.
 case([dispatch(values[(i+2)%10],values[(i+4)%10],values[(i+6)%10],1)],graph(),p,{0x6fc49c:1},'wire coordinate and intensity truncation with silent local audio')
# Repeated calls retain voice/slot/queue/PRNG state.
for i in range(16):
 case([dispatch(50+j*10,75+j*5,100,1) for j in range(3)],graph('weighted'),changes={0x6f8a4c:i%2,0x690fd4:rng.randrange(2**32)},label='sequential impacts preserve queue voice and random state')
scope='Two original routines: complete material impact sound dispatch and component percentage/volume wrapper. Real original selection, descriptor, attenuation, device playback, voice setup, message construction and first-peer queue callees execute unchanged. OS audio methods and heap/scope services are instrumented boundaries; no gameplay helper is stubbed. Full arena, globals, returns, device traces and queued payload bytes compare. Port difference: the original twelve-byte sound packet has one unwritten tail byte; the port zeros it and the oracle seeds only that original stack byte. Positive logarithm argument restrictions and physical x87 precision limits from audio-device validation remain. Silent nonfinite wire inputs and NaN pitch/remapping are included. Valid registered events, required fallback structures, initialized camera/device/queue state and successful allocations are internal preconditions. Runtime startup, audio loading/backend, enclosing wall response, remaining movement and rendering remain incomplete.'
fixture={'base':BASE,'memory':'sound-events-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'audio_device_calls','pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],'native_callbacks':prior['native_callbacks']}
path=out/'sound-events-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',dict(callback_counts),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_sound_events_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'audio_device_calls':dict(callback_counts),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'zeroed_packet_padding_entries':padding_entries,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'sound-events-memory.bin',out/'audio-device-callbacks.wasm',out/'script-values-memory.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
