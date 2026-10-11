"""Complete wall response with original training collision, events and audio.

One deterministic arena lets the existing checker compare all mutated memory.
Only OS/allocator/native gameplay boundaries are instrumented; collision, script
execution, impact selection, playback setup and queuing run recovered callees.
"""
import hashlib,json,math,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'wall-response.json'
if __name__=='__main__':report_path.unlink(missing_ok=True)
prior=json.loads((out/'rebound-fixtures.json').read_text())
audio=json.loads((out/'sound-events-fixtures.json').read_text())
world=json.loads((out/'skater-fixtures.json').read_text());loader=world['loader'];a=world['addresses']
BASE,SIZE=0x1000000,0x1600000;REBOUND=prior['base'];AUDIO=0x1b00000;AUDIO_OLD=audio['base']
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def copy(at,data):memory[at-BASE:at-BASE+len(data)]=data
def word(at):return struct.unpack_from('<I',memory,at-BASE)[0]
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def rebase(value):return value+(AUDIO-AUDIO_OLD) if AUDIO_OLD<=value<AUDIO_OLD+0x80000 else value
copy(REBOUND,(out/prior['memory']).read_bytes())
am=bytearray((out/audio['memory']).read_bytes())
# The saved synthetic audio arena contains no scalar integers in its private
# address interval. Relocate those internal references together, retaining all
# callback and original-image references for the checker's typed relocations.
for i in range(0,len(am),4):
 value=struct.unpack_from('<I',am,i)[0]
 if rebase(value)!=value:struct.pack_into('<I',am,i,rebase(value))
copy(AUDIO,am)
CONTEXT,ADAPTER,MANAGER=REBOUND+0x20,REBOUND+0x50,REBOUND+0x100
METHODS,BUCKETS,CALLBACK,PRINT,PROGRAM,LOG,HEAP=REBOUND+0x8400,REBOUND+0x10000,REBOUND+0x30000,REBOUND+0x35f00,REBOUND+0x40000,REBOUND+0x60000,REBOUND+0x80000
EM,RECEIVER,STATE,STATE2,BODY,BODY2,P,INPUT,VECTORS=0x1930000,0x1941000,0x1953000,0x1953100,0x1954000,0x1954400,0x1950000,0x1952000,0x1955000
NATIVE,RECEIVE,OBJECT=0x3f01000,0x3f01060,0x3f01070
AUDIO_CONTEXT=AUDIO+0x8000;AUDIO_LOG=AUDIO_CONTEXT+128;AUDIO_CALLBACK=0x3f02000
CONFIG,SAMPLE,COMPONENT,CLIENT=AUDIO+0x5400,AUDIO+0x7000,AUDIO+0x16000,AUDIO+0x10000
GRAPH=AUDIO+0x20000;GAME=0x1c00000;DIFFICULTY=GAME+0x1000;EMPTY=GAME+0x2000
DATA,GRID,SCENE,SCENES,RUNTIME,NODES,OWNERS,REFS,COLLISION_HEAP=[a[k] for k in ['data','grid','scene','scenes','runtime','nodes','owners','refs','heap']]
QUERY,TLS=0x2000500,0x2700800
copy(DATA,(out/loader['loaded']).read_bytes());copy(GRID,(out/loader['grid']).read_bytes());copy(COLLISION_HEAP,(out/loader['heap']).read_bytes())
copy(SCENE,bytes(0xd4));put(SCENE+0xd4,'<I',GRID)
put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
for j in range(3):put(NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,NODES+(j+1)*16)
put(NODES+48,'<4I',0,0xffffffff,0,NODES+48)
copy(RUNTIME,bytes.fromhex(world['world'][0]['actors']));copy(OWNERS,bytes.fromhex(world['owners']));copy(REFS,bytes.fromhex(world['references']))
copy(P+0xa8,bytes.fromhex(next(c['output'] for c in world['constructors'] if c['kind']=='default')))
put(P+4,'<I',0x5bd63b29);put(P+16,'<I',0);put(P+0x2ed,'<B',0);put(P+0x302,'<B',0);put(P+0x1514,'<I',COMPONENT)
put(INPUT+0x1a0,'<B',0);put(STATE+0x28,'<B',0);put(STATE2+0x28,'<B',1)
put(P+0x120,'<4f',25,10,30,1);put(P+0x130,'<4f',-.5,0,-.8660254,0);put(P+0xfa,'<B',7)
for body in [BODY,BODY2]:
 put(body+0x4c,'<4f',25,10,40,1);put(body+0x5c,'<4f',25,10,20,1)
 put(body+0x100,'<I',P);put(body+0x280,'<I',P)
put(COMPONENT+12,'<I',BODY);put(COMPONENT+0x24,'<f',1)
copy(GAME,bytes(0x400));put(GAME+0x38c,'<I',DIFFICULTY);put(DIFFICULTY+0x398,'<I',EMPTY);put(EMPTY,'<2I',0,0)
put(QUERY,'<3I',0x12345678,0xabcdef01,0x13579bdf)
initial=bytes(memory)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
pointer_globals=set(prior['pointer_globals'])
def glob(name,at,value=0,width=4,offset=0,override=True):
 if at in index:
  if override:defaults[index[at]]=value
  return index[at]
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value);return index[at]
for j,(entry,value) in enumerate(zip(audio['globals'],audio['cases'][0]['globals'])):
 name,at,width,*offset=entry
 if name=='thug_math_errno':at=TLS+8
 k=glob(name,at,rebase(value),width,offset[0] if offset else 0,override=False)
 if j in audio['pointer_globals']:pointer_globals.add(k)
# Retain the initialized script/event graph and allocator; use the audio client
# for impact notification. Stat interpolation gets initialized difficulty data.
glob('thug_network_state',0x7cce14,AUDIO+0x15000);glob('thug_game_context',0x7ce478,GAME)
glob('thug_audio_master_volume',0x67db08,bits(100));glob('thug_audio_spatial_enabled',0x6f8a4c,0,1)
glob('thug_collision_scene_list',0x6fa7ec,SCENES);glob('thug_moving_collision_list',0x691984,NODES)
glob('thug_collision_default_cache',0x691974,0);glob('thug_collision_select_farthest',0x691910,0,1);glob('thug_collision_grid_stamp',0x693998,1,1)
for name,address,count in [('thug_collision_selected_scenes',0x6fa738,16),('thug_collision_selected_grids',0x6fa778,16),('thug_collision_grid_output',0x691998,2048)]:
 for j in range(count):glob(name,address+j*4,0,offset=j*4)
for j in range(1024):glob('thug_collision_fallback_indices',0x67c6b8+j*4,j*2|((j*2+1)<<16),offset=j*4)
# Obtain exact method-table addresses from the previously verified geometry.
exports=prior['pointer_exports']+audio['pointer_exports']+[[word(loader['instances']),'thug_static_collision_methods'],[word(RUNTIME),'thug_moving_collision_methods'],[0x67c6b8,'thug_collision_fallback_indices']]
fields=set(prior['pointer_fields'])|{rebase(x) for x in audio['pointer_fields']}|{QUERY}
fields.update(loader['instances']+i*24 for i in range(loader['count']));fields.update(RUNTIME+i*0x100 for i in range(3))
fields.update(LOG+i*48+j for i in range((HEAP-LOG)//48) for j in [16,20,24,28,40])
functions={'0x5059d0':{'name':'thug_skater_wall_response','this':True,'result':'void','cleanup':4,'memory':True,'stack_args':[0]}}
observe=[0x5059d0,0x4ff670,0x5039f0,0x580400,0x478f00,0x4609f0,0x580790,0x518dd0,0x444bb0,0x475790,0x457eb0,0x47bd20,0x47d130,0x47cd70,0x5003a0,0x4172f0,0x414460,0x4118c0,0x414590,0x4637c0,0x4637e0,0x404e20,0x5df4ac]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=10000000,scope_entries={REBOUND+0x6000:1,MANAGER+0x300:2,MANAGER+0x400:4,MANAGER+0x200:1})
cpu=oracle.cpu
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:cpu.mem_write(at,bytes(4))
cpu.mem_map(NATIVE,4096);cpu.mem_map(AUDIO_CALLBACK,4096);cpu.mem_map(0x2700000,0x10000)
oracle.setword(0x684fe4,0x5df4ac)
boundary_kinds={NATIVE:0,RECEIVE:1,OBJECT:2}
def event_callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);kind=boundary_kinds[address]
 owner=cpu.reg_read(UC_X86_REG_ECX) if kind else 0;event=oracle.word(sp+4) if kind in [1,2] else 0;script=oracle.word(sp+8) if not kind else 0
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
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(CALLBACK+40) if kind==3 else 1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(4 if kind in [1,2] else 0))
for address in [NATIVE,RECEIVE,OBJECT]:oracle.cpu.hook_add(UC_HOOK_CODE,event_callback,begin=address,end=address)

names=['orientation','commit','min','max','position','volume','pan','frequency','stop','release','release_spatial','create','query','lock','unlock','seek','play']
argc=[8,1,3,3,5,2,2,2,1,1,1,4,3,8,5,2,4]
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
 kind=(address-AUDIO_CALLBACK)//16;sp=uc.reg_read(UC_X86_REG_ESP);a=[oracle.word(sp+4+i*4) for i in range(argc[kind])];c=[oracle.word(AUDIO_CONTEXT+i*4) for i in range(32)]
 assert c[0]<200
 args=a[1:] if kind!=13 else [a[1],a[2],a[7],c[6],c[7],c[8],c[9]]
 record=[kind,a[0],*args,*([0]*(7-len(args))),*[oracle.word(c[16]+i*4) for i in range(6)],oracle.word(c[18]),oracle.word(c[17]),oracle.word(c[17]+4),oracle.word(c[19]),uc.mem_read(c[20],1)[0]]
 uc.mem_write(AUDIO_LOG+c[0]*80,struct.pack('<20I',*record));oracle.setword(AUDIO_CONTEXT,c[0]+1)
 if c[10]==kind:
  if c[13]==1:uc.mem_write(c[11],bytes([c[12]&255]))
  else:oracle.setword(c[11],c[12])
 if kind==11:oracle.setword(a[2],c[4])
 if kind==12:oracle.setword(a[2],c[5])
 if kind==13:
  for at,value in zip(a[3:7],c[6:10]):oracle.setword(at,value)
 callback_counts[names[kind]]+=1;uc.reg_write(UC_X86_REG_EAX,c[2] if c[1]==kind else 0)
 uc.reg_write(UC_X86_REG_EIP,oracle.word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+argc[kind]*4)
for i in range(len(names)):cpu.hook_add(UC_HOOK_CODE,callback,begin=AUDIO_CALLBACK+i*16,end=AUDIO_CALLBACK+i*16)

MATERIAL_NAME,EVENT_PARAMETER=0xa1000001,0xa1000002
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

# Stable QB definitions fill the existing bucket graph, including the wall's
# sound intensity pair and empty default physics set. Per-case parameters are
# patched at these records without replacing the real getter.
def configuration(height=8.,extra=20.,turn=.5,angle=45.,speed=100.,mode='direct'):
 b=graph(mode)
 for key,value in [(0xd4205c9b,height),(0x20102726,extra),(0xe07ee1a9,turn),(0x1483fd01,angle),(0xbe0a58a0,speed)]:
  b.symbol(key,1 if isinstance(value,int) else 2,value&0xffffffff if isinstance(value,int) else bits(value))
 b.symbol(0x8cbc89dd,10,b.structure([]));b.symbol(0xd3d12913,10,b.structure([]))
 b.symbol(0xcc5f87aa,10,b.structure([(0,5,b.words(0,bits(1000),bits(1000)))]))
 b.symbol(0xd478c96d,8,NATIVE)
 return b
labels=[];outcomes=Counter();case_events=Counter()
def branch(uc,address,size,user):
 if address==0x505e61:case_events['second_probe_hit' if uc.reg_read(UC_X86_REG_EAX)&255 else 'second_probe_miss']+=1
 elif address==0x505e7a:case_events['reverse_after_second_hit']+=1
 elif address==0x5059de:case_events['rebound_return' if uc.reg_read(UC_X86_REG_EAX)&255 else 'continue_wall']+=1
 elif address==0x505f47:case_events['final_displacement_event']+=1
for address in [0x505e61,0x505e7a,0x5059de,0x505f47]:cpu.hook_add(UC_HOOK_CODE,branch,begin=address,end=address)
# Explicit query context replaces only the original twelve-byte global state.
# Initialize and mirror it at the function boundary, never intercept the query.
def begin(uc,address,size,user):uc.mem_write(0x691968,bytes(uc.mem_read(QUERY,12)))
query_hook=cpu.hook_add(UC_HOOK_CODE,begin,begin=0x5059d0,end=0x5059d0)
float_fields=[*[body+i for body in [BODY,BODY2] for i in list(range(0x4c,0x5c,4))+list(range(0x6c,0xac,4))+list(range(0xac,0xbc,4))],*range(P+24,P+88,4),*range(P+0x208,P+0x228,4),*range(P+0xa8,P+0xc8,4),*range(P+0xcc,P+0xec,4),P+0xf0,*range(P+0x11c,P+0x140,4)]
def case(b=None,p=(),changes=None,normal=P+0x130,label='wall',fn=0x5059d0):
 if len(labels)%40==0:print('Original wall/sweep cases:',len(labels),label,flush=True)
 b=b or configuration();patches=b.patches()+list(p);c=dict(b.changes);c.update(changes or {})
 cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 case_events.clear();labels.append(label)
 s=oracle.case([(fn,P,[normal,QUERY,PRINT] if fn==0x5059d0 else [QUERY,PRINT])],patches,{index[k]:v for k,v in c.items()})[0]
 s['outputs'].append([QUERY,bytes(cpu.mem_read(0x691968,12)).hex()]);s['float_fields']=float_fields[:]
 events=oracle.word(CALLBACK);device=oracle.word(AUDIO_CONTEXT);s['callbacks']=events+device
 outcomes.update(case_events);outcomes['event_and_command_callbacks']+=events;outcomes['audio_device_calls']+=device
 for i in range(events):s['float_fields'].extend(CALLBACK+128+i*96+j*4 for j in range(16,24))
 for i in range(device):
  at=AUDIO_LOG+i*80;kind=oracle.word(at)
  if kind in [0,2,3,4]:s['float_fields'].extend(at+8+j*4 for j in range(6 if kind==0 else 3 if kind==4 else 1))
  if kind==11:fields.add(at+12)
  if kind==12:fields.update([at+8,at+12])
 known={x[0] for x in exports}|set(boundary_kinds)
 for at,data in patches+s['outputs']:
  raw=bytes.fromhex(data)
  for i in range(0,len(raw)-3,4):
   if int.from_bytes(raw[i:i+4],'little') in known:fields.add(at+i)
 assert last_error==0x12345678
 return s
if __name__=='__main__':
 # First smoke cases are also retained in the permanent oracle.
 case(label='complete event impact audio queue and second collision probe')
 case(p=[patch(INPUT+0x1a0,'<B',1)],label='rebound short circuit')
 case(p=[patch(P+0x2ed,'<B',1)],label='synchronous special-mode native command')

 # Angle, speed and raw side-selector gates. Changes in the angle sign choose
 # between the two real event IDs; a non-boolean selector must stay raw.
 rng=random.Random(0x5059d0)
 for i in range(144):
  angle=[0.,30.,45.,60.,89.,90.,100.,float('nan')][i%8]
  sign=[-.5,.5,-1.,1.,0.,float('nan')][(i//8)%6]
  p=[patch(P+0x130,'<4f',sign,0,-.8660254,0),patch(STATE+0x28,'<B',[0,1,2,255][(i//6)%4]),
     patch(P+0x2ed,'<B',(i//12)%2),patch(BODY+0xac,'<4f',120,20,-300,[0,1,7][i%3])]
  case(configuration(angle=angle,speed=[0.,100.,1000.,float('nan')][(i//4)%4],turn=[0.,.5,1.][i%3]),p,label='angle speed direction and raw side byte gates')
 # Exact int32 returns, wide intermediate exponents and the separate two adds
 # in the probe start. Keep event audio out of deliberately extreme geometry.
 for i in range(64):
  height=[0.,-0.,8.,-8.,24.25,2**24+1,2**31-1,-2**31,1e-30,1e30][i%10]
  extra=[0.,20.,-20.,2**24+1,1e-30,1e30][(i//3)%6]
  position=[(25,10,40,1),(1e30,2e30,-1e30,7),(1e-30,2e-30,0,0)][(i//7)%3]
  p=[patch(BODY+0x4c,'<4f',*position),patch(BODY+0x5c,'<4f',*[x*.5 for x in position]),
     patch(P+0x120,'<4f',*position)]
  case(configuration(height,extra,angle=100.,speed=1e30),p,label='numeric parameter types and wide segment arithmetic')
 # The second probe crosses faces from the actual archived training geometry.
 # Angle response is disabled so the constructed velocity points through the
 # face; the hit branch still rotates and scales with the original functions.
 for i,test in enumerate(loader['queries'][::5]):
  if not test['returned']:continue
  result=bytes.fromhex(test['result']);normal=struct.unpack_from('<4f',result);point=struct.unpack_from('<4f',result,16)
  for enabled in [0,1]:
   p=[patch(P+0x120,'<4f',*point),patch(P+0x130,'<4f',*normal),patch(BODY+0xbc,'<B',enabled),
      patch(BODY+0xac,'<4f',*[-n*300 for n in normal[:3]],1),patch(BODY+0x4c,'<4f',*point),
      patch(BODY+0x5c,'<4f',point[0]+64,point[1],point[2],point[3])]
   if i%3==0:
    p += [patch(P+0x140,'<3I',OWNERS,0,REFS),patch(OWNERS+4,'<I',P+0x140),patch(REFS+4,'<I',P+0x140)]
   case(configuration(height=0.,extra=0.,turn=[0.,.125,-.125][i%3],angle=100.,speed=[0.,63.9,64.,64.1,100.][i%5]),p,
        {0x693998:[1,254,255][i%3]},label='second real training face hit reversal and final displacement gate')
 # Native/object handlers can mutate the fields reread after event delivery.
 for mode,address,value in [(1,P+0x2ed,1),(1,STATE+0x28,2),(1,BODY+0xbc,1),(2,P+0x130,bits(1)),
  (2,P+0x120,bits(100)),(2,BODY+0xac,bits(1000)),(2,COMPONENT+0x24,bits(.25)),
  (3,0,BODY2),(4,0,STATE2),(5,0,0xfffffff0)]:
  for special in [0,1]:
   p=[patch(CALLBACK+4,'<3I',mode,address,value),patch(P+0x2ed,'<B',special)]
   case(configuration(),p,label='event mutation rereads body state surface and sound')
 # Aliasing the supplied normal exercises the original snapshots around position
 # writes and velocity/orientation updates.
 for normal in [P+0x130,P+0x120,BODY+0x4c,BODY+0xac,BODY+0x6c,BODY+0x7c,BODY+0x8c]:
  for turn in [0.,.5,1.]:
   case(configuration(turn=turn,angle=100.,speed=1e30),normal=normal,label='normal input aliases mutable body or probe')
 # Cancellation falls through into the complete wall path after clearing the
 # flag and recording time; successful rebounds must skip the wall path.
 for cancel in [0,1,255]:
  for mode in [0,1,3,4]:
   p=[patch(INPUT+0x1a0,'<B',1),patch(STATE+0xb8,'<B',cancel),patch(STATE2+0xb8,'<B',cancel),
      patch(CALLBACK+4,'<3I',mode,STATE+0xb8,1 if mode==1 else BODY2 if mode==3 else STATE2)]
   case(p=p,label='rebound cancellation and complete wall fallthrough')
 # Explicit randomized finite contacts mix body motion, height, volume and
 # normal angle through the real audio and message-queue chain.
 for i in range(64):
  angle=rng.uniform(-math.pi,math.pi);normal=(math.cos(angle),0,math.sin(angle),0)
  p=[patch(P+0x130,'<4f',*normal),patch(P+0x120,'<4f',rng.uniform(-500,500),rng.uniform(-50,50),rng.uniform(-500,500),1),
     patch(BODY+0xac,'<4f',rng.uniform(-700,700),rng.uniform(-50,50),rng.uniform(-700,700),rng.uniform(-3,3)),
     patch(BODY+0x5c,'<4f',rng.uniform(-100,100),rng.uniform(-100,100),rng.uniform(-100,100),1),
     patch(P+0x2ed,'<B',i%2),patch(STATE+0x28,'<B',i%4)]
  case(configuration(height=rng.uniform(-10,30),extra=rng.uniform(-20,80),turn=rng.uniform(-1,1),speed=50.,mode='weighted' if i%3==0 else 'direct'),p,
       {0x6f8a4c:(i//2)%2},label='random finite contact integration')
 # Event-driven body replacement must not change the saved parameter source.
 for extra in [0.,20.,99.]:
  b=configuration(extra=extra)
  b.symbol(0xd3d12913,10,b.structure([(0x20102726,2,bits(1234))]))
  other=GAME+0x3000
  p=[patch(BODY+0xbc,'<B',1),patch(BODY2+0xbc,'<B',1),patch(BODY2+0x100,'<I',other),
     patch(other+4,'<I',0x5bd63b29),patch(other+16,'<I',0),patch(other+0x2ed,'<B',0),patch(other+0x302,'<B',1),
     patch(CALLBACK+4,'<3I',3,0,BODY2)]
  case(b,p,label='saved parameter body survives active body replacement')
 # A QB alias enters the full synchronous script allocation/execution/cleanup
 # path as well as the already tested native-command form of the same wrapper.
 for key in [5,8]:
  b=configuration();b.symbol(0xd478c96d,13,key)
  case(b,[patch(P+0x2ed,'<B',1)],label='special-mode alias executes actual QB script')
 assert outcomes['second_probe_hit'] and outcomes['second_probe_miss'] and outcomes['reverse_after_second_hit'] and outcomes['final_displacement_event'] and outcomes['rebound_return']
 assert oracle.coverage['0x580790'] and oracle.coverage['0x475790'] and oracle.coverage['0x457eb0'] and oracle.coverage['0x4637e0']

 scope='Complete original wall response 005059d0 through rebound, tangent turn, impact events, stat-dependent audio, real network enqueue, special-mode synchronous command dispatch and second training-level collision query. All arena bytes, tracked globals and boundary logs compare against unchanged x86 callees. Original twelve-byte query globals are mapped to the port context argument at the outer function boundary. Only heap/scope, native/object gameplay handlers and OS audio/CRT services are instrumented. Sound packet padding is deterministically zeroed as documented in sound-events. Physical x87 transcendental precision and invalid-logarithm Unicorn limitations remain. This is a recovered movement component; full movement, gameplay callbacks, runtime startup, renderer, browser audio and a playable level remain incomplete.'
 callbacks=prior['native_callbacks']+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']]
 fixture={'base':BASE,'memory':'wall-response-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':prior['memory_exports'],
  'globals':globals_,'functions':functions,'float_fields':float_fields,'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_audio_callbacks',
  'pointer_symbols':prior['pointer_symbols'],'pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(pointer_globals),'native_callbacks':callbacks}
 path=out/'wall-response-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
 adapter=out/'wall-audio-callbacks.wasm'
 subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-DAUDIO_CONTEXT=0x1b08000','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/audio_device_callbacks.c'),'-o',str(adapter)],check=True)
 print('x86 complete:',len(oracle.cases),'cases',dict(outcomes),dict(oracle.coverage),flush=True)
 subprocess.run(['node',str(ROOT/'tools/verify_wall_response_wasm.mjs'),str(out)],check=True)
 report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'audio_device_calls':dict(callback_counts),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'zeroed_packet_padding_entries':padding_entries,'scope':scope,
  'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
  'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter,out/'rebound-callbacks.wasm',out/'script-values-memory.wasm']},
  'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
 report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
