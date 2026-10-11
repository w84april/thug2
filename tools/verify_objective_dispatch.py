"""Compare original goal manager and actual native script lifecycle commands."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-dispatch.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'score-display-fixtures.json').read_text());BASE,SIZE=prior['base'],0x600000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
OBJ,REF,OWNED,EM,TABLES,SCRIPTS,FRAMES,CACHE,SYMBOLS,TLS,LOCALE,UM,EVENTS,ENTRIES,SERVICES=[BASE+x for x in [0x10000,0x16000,0x18000,0x60000,0x6c000,0x70000,0x72000,0x73000,0x78000,0x7e000,0x7e100,0x80000,0x83800,0x83900,0x83a00]]
FONT,METRICS,GLYPHS,BUCKETS,FENTRY=BASE+0x2000,BASE+0x2400,BASE+0x3000,BASE+0x6800,BASE+0x6900
PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE=[TABLES+i*256 for i in range(5)]
WIDGET,ARRAY,TEXTS,TRICKS,ITEMS,SCORE,GAME,NODES,BODIES,LOG,HEAP=[BASE+x for x in [0x85000,0x88000,0x90000,0xb0000,0xe0000,0xe1000,0xe3000,0xe4000,0xe5000,0x180000,0x300000]]
NOTIFY=0xd4491be1

def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ALLOCATOR+0x124,'<I',ALLOCATOR+0x300)
# Both configured and default font IDs resolve to the same real metrics.
put(BUCKETS+24,'<I',BUCKETS+32);put(BUCKETS+32,'<3I',0,FENTRY,0)
for at,n in [(WIDGET,0x1c4),(SCORE,0x1550),(GAME,0x200),(NODES,0x100),(BODIES,0x2000)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(WIDGET,'<I',0x64a264);put(WIDGET+8,'<I',0x14400);put(WIDGET+0x14,'<I',0x44727dae);put(WIDGET+0x18,'<I',0x40d92263)
put(WIDGET+0x28,'<5I',0x6477e4,WIDGET,0,WIDGET+0x28,WIDGET+0x28);put(WIDGET+0x40,'<3I',0x6477e0,0,WIDGET)
for off in [0xa4,0xa8,0xe8,0xec,0xf0,0xf4,0x170,0x19c,0x1a0]:put(WIDGET+off,'<f',1)
put(WIDGET+0x160,'<2f',80,100);put(WIDGET+0x178,'<I',0xabc);put(WIDGET+0x190,'<I',3);put(WIDGET+0x1bc,'<I',0x80000000)
put(GAME+0x34,'<I',NODES)
for i in range(8):
 put(NODES+i*16,'<4I',0,BODIES+i*0x400,0,NODES+(i+1)*16)
 put(BODIES+i*0x400+0x14,'<I',0x100+i);put(BODIES+i*0x400+0x2b8,'<I',i)
put(NODES+128,'<4I',0,0xffffffff,0,NODES+128)
put(SCORE+8,'<h',0x100);put(SCORE+0x4c,'<3I',ITEMS,250,0)
for i in range(250):
 put(ITEMS+i*4,'<I',TRICKS+i*256);put(ARRAY+i*4,'<I',TEXTS+i*256)
 for at in [TEXTS+i*256,TRICKS+i*256+0x5c]:memory[at-BASE]=0
# A real bytecode symbol and cache entry for the post-update notification.
NOTIFY_SYMBOL=CACHE+0x400
put(SYMBOLS+(NOTIFY&0xfff)*4,'<I',NOTIFY_SYMBOL);put(NOTIFY_SYMBOL,'<BBHIIII',0,7,0,NOTIFY,0,CACHE+0x500,0)
put(CACHETABLE+8,'<I',1);put(CACHETABLE+32+(NOTIFY&3)*12,'<3I',NOTIFY,CACHE+0x440,0)
put(CACHE+0x440,'<5I',NOTIFY,CACHE+0x500,1,0,0)
memory[CACHE+0x500-BASE:CACHE+0x502-BASE]=b'\x01\x24'
NUMERIC,SETTINGS,COMPONENT,PRINT,DIAG,GRAPH=BASE+0x86000,BASE+0x87000,BASE+0x87400,BASE+0x87500,BASE+0x87600,BASE+0xf0000
for at,n in [(NUMERIC,0x1b0),(SETTINGS,64),(COMPONENT,64),(DIAG,512)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(NUMERIC,'<I',0x64a290);put(NUMERIC+8,'<I',0x14400);put(NUMERIC+0x14,'<I',0xf4d3a70e)
put(NUMERIC+0x28,'<5I',0x6477e4,NUMERIC,0,NUMERIC+0x28,NUMERIC+0x28);put(NUMERIC+0x40,'<3I',0x6477e0,0,NUMERIC)
for off in [0xa4,0xa8,0xe8,0xec,0xf0,0xf4,0x170]:put(NUMERIC+off,'<f',1)
put(NUMERIC+0x180,'<I',FONT);put(COMPONENT+4,'<I',0x8bce7e66);put(COMPONENT+12,'<I',BODIES);put(BODIES+0x100,'<I',COMPONENT)
put(PRINT,'<2I',DIAG,0);put(DIAG+4,'<I',SCORE)
# Add numeric-display notification to the existing initialized QB cache.
NUMERIC_NOTIFY=0xa611bb15
put(SYMBOLS+(NUMERIC_NOTIFY&0xfff)*4,'<I',CACHE+0x600)
put(CACHE+0x600,'<BBHIIII',0,7,0,NUMERIC_NOTIFY,0,CACHE+0x680,0)
put(CACHE+0x640,'<5I',NUMERIC_NOTIFY,CACHE+0x680,1,0,0)
put(CACHETABLE+8,'<I',2);put(CACHETABLE+32+(NUMERIC_NOTIFY&3)*12,'<3I',NUMERIC_NOTIFY,CACHE+0x640,CACHE+0x660)
put(CACHE+0x660,'<3I',NOTIFY,CACHE+0x440,0)
memory[CACHE+0x680-BASE:CACHE+0x682-BASE]=b'\x01\x24'
# Typed required special-color and rate symbols.
for i in range(3):
 put(GRAPH+i*32,'<BBHII',0,1,0,4,GRAPH+0x100+i*16)
 put(GRAPH+0x100+i*16,'<4I',0x100+i,0xabcdef80+i,0xfffffffe,255)
put(GRAPH+0x80,'<BBHII',0,12,0,3,GRAPH+0x140);put(GRAPH+0x140,'<3I',GRAPH,GRAPH+32,GRAPH+64)
for i,(name,kind,value) in enumerate([(0x2e8b9f1c,12,GRAPH+0x80),(0x3abcda81,2,0x3e4ccccd)]):
 at=GRAPH+0x200+i*32;put(at,'<BBHIIII',0,kind,0,name,0,value,0);put(SYMBOLS+(name&0xfff)*4,'<I',at)
put(SETTINGS+8,'<I',SETTINGS+16);put(SETTINGS+16,'<4I',26,0xa1dc81f9,0,0)
OBJECT,MANAGER,NETWORK,PLAYERS,PLAYER_NODES,PROFILES,PROFILE,ROOT_PARAMS,OBJECT_LINKS,PARENTS,GOAL_GRAPH,PARSED,CODE,META= [BASE+x for x in [0x110000,0x112000,0x113000,0x114000,0x115000,0x118000,0x119000,0x11a000,0x11b000,0x11b100,0x140000,0x170000,0x171000,0x120000]]
QUEUE=MANAGER+0x18;objects=[OBJECT+i*256 for i in range(8)]
SCORE_COMPONENTS=BASE+0x11c000;SCORES=[SCORE]+[BASE+0x124000+i*0x1600 for i in range(7)]
for at,n in [(OBJECT,0x800),(MANAGER,0x3a0),(NETWORK,0x200),(PLAYERS,0x1000),(PLAYER_NODES,0x100),(PROFILES,0x100),(PROFILE,0x100),(ROOT_PARAMS,0x100),(OBJECT_LINKS,0x100),(PARENTS,0x100),(SCORE_COMPONENTS,0x100),(PARSED,12),(META,0x1000)]:memory[at-BASE:at-BASE+n]=bytes(n)
for o in SCORES[1:]:memory[o-BASE:o-BASE+0x1550]=bytes(0x1550)
put(GAME+0x38c,'<I',MANAGER);put(ALLOCATOR+0x114,'<I',ALLOCATOR+0x500)
put(MANAGER,'<5I',8,OBJECT_LINKS,0,0,0);put(MANAGER+0x398,'<I',ROOT_PARAMS)
put(QUEUE,'<5I',0x6474cc,0xffffffff,0,QUEUE,QUEUE)
put(PROFILES+0x14,'<3I',PROFILE,PROFILE,0)
for i,o in enumerate(objects):
 put(o,'<5I',0x64ddd0 if i&1 else 0x64ea30,o,i,o,o)
 put(o+0x1c,'<2I',ROOT_PARAMS,ROOT_PARAMS+8);put(o+0x2c,'<I',PARENTS+i*4)
 put(o+0x44,'<I',0xfffffffe);put(o+0x60,'<I',0xdeadbeef);put(o+0x6c,'<2B',0x80,0)
 put(OBJECT_LINKS+i*16,'<3I',0x100+i,o,OBJECT_LINKS+(i+1)*16 if i<7 else 0)
 put(PLAYERS+i*512+0x14,'<I',BODIES+i*0x400)
 put(PLAYER_NODES+i*16,'<4I',0,PLAYERS+i*512,0,PLAYER_NODES+(i+1)*16)
 component=SCORE_COMPONENTS+i*32;put(component,'<7I',0,0xd262802f,0,BODIES+i*0x400,COMPONENT if not i else 0,0,SCORES[i])
 put(BODIES+i*0x400+0x100,'<I',component);put(SCORES[i]+8,'<h',0x100+i)
put(PLAYER_NODES+128,'<4I',0,0xffffffff,0,PLAYER_NODES+128)
put(NETWORK+0x11c,'<4I',0,0xffffffff,0,PLAYER_NODES)
# Initialized cache contains real return-only bytecode for each lifecycle script.
memory[CACHETABLE+32-BASE:CACHETABLE+80-BASE]=bytes(48)
for i,name in enumerate([NOTIFY,NUMERIC_NOTIFY,5,6,7,8]):
 at=META+i*256;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,7,0,name,0,at+64,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,at+64,1,0,0);memory[at+64-BASE:at+66-BASE]=b'\x01\x24'
 slot=CACHETABLE+32+(name&3)*12
 previous=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',previous,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=previous
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',6)
put(SERVICES,'<2I',PRINT,ADAPTER)
for o in objects:put(o+0x38,'<i',-1)
put(MANAGER+0x2c,'<I',0xdead1234)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value,width in [('thug_ui_manager',0x701440,UM,4),('thug_game_context',0x7ce478,GAME,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_script_updating',0x6f3544,0,1),('thug_script_stop_pending',0x6f3545,0,1),('thug_game_settings',0x7ce470,SETTINGS,4),('thug_network_state',0x7cce14,NETWORK,4),('thug_profile_manager',0x7ce4b4,PROFILES,4)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
defaults[index[0x7cefa0]]=0
for i in range(8):
 at=0x690fa4+i*4;defaults[index[at]]=0xa5a5a5a5
functions={}
def bind(at,name,argc=0,result='void',heap=False,diag=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
bind(0x4b0810,'thug_ui_multiline_initialize',result='word',heap=True)
bind(0x4b08b0,'thug_ui_multiline_destroy',heap=True,diag=True)
bind(0x4b0b30,'thug_ui_multiline_delete',1,'word',True,True)
bind(0x4b0cd0,'thug_ui_multiline_set_text',2,heap=True,diag=True)
bind(0x561670,'thug_score_update_combo_text',1,heap=True,diag=True)
bind(0x561890,'thug_score_update_numeric_text',2,heap=True,diag=True);functions['0x561890']['float_args']=[1]
bind(0x564a10,'thug_score_reset',heap=True,diag=True)
for at in [0x41d1d0,0x461a00,0x461930,0x4aa8e0,0x4b0920,0x4b3fd0,0x4ab250,0x4ad100]:functions[hex(at)]=prior['functions'][hex(at)]
bind(0x557360,'thug_objective_activate',result='byte',heap=True,diag=True)
bind(0x557270,'thug_objective_initialize',heap=True,diag=True)
bind(0x557560,'thug_objective_deactivate',2,'byte',True,True)
training_prior=json.loads((out/'objective-initialize-fixtures.json').read_text())
functions['0x471b00']=training_prior['functions']['0x471b00']
bind(0x557fc0,'thug_objective_manager_activate',2,'byte',True,True)
for at,name in [(0x559230,'activate'),(0x559290,'deactivate'),(0x5592f0,'clear_last')]:bind(at,'thug_script_goal_'+name,2,'byte',this=False)
bind(0x475790,'thug_script_run_sync',4,heap=True,diag=True,this=False)
bind(0x475420,'thug_script_spawn',10,'word',True,True,this=False)
bind(0x474b40,'thug_script_invoke_command',result='byte',heap=True,diag=True)
observe=[int(k,16) for k in functions]+[0x401cc0,0x4a8940,0x4abd40,0x461140,0x473800,0x460470,0x474540,0x4748e0,0x473a80,0x475790,0x474420,0x4621d0,0x6234fe,0x4b1830,0x4b0760,0x48d5f0,0x4b3e70,0x48d1d0,0x4abbe0,0x4af720,0x4af8c0,0x4a94a0,0x4ac400,0x4aaff0,0x4637c0,0x4637e0,0x561890,0x564a10,0x402200,0x6285af,0x6286ab,0x5532a0,0x5612d0,0x518390,0x460a20,0x5633e0,0x45db90]
observe=list(dict.fromkeys(observe+[0x557360,0x557270,0x554bd0,0x553ea0,0x557f90,0x55dbe0,0x5372c0,0x537010,0x476b40,0x477860,0x5566d0,0x556a00,0x44e4f0,0x554220,0x554460,0x559110]))
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=12000000,scope_entries={ALLOCATOR+0x200:6,ALLOCATOR+0x300:1,ALLOCATOR+0x500:5})
# Real CRT signed auto-ID formatting runs; only its Windows TLS services adapt.
os_calls=Counter();last_error=0x12345678
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7);oracle.setword(0x68ecfc,LOCALE)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
def os_service(cpu,address,size,user):
 global last_error
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:cpu.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
 elif address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
 else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for at in [GET_ERROR,GET_TLS,SET_ERROR]:oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=at,end=at)
from unicorn.x86_const import UC_X86_REG_EIP,UC_X86_REG_FPCW
sp=oracle.stack+0x18000;oracle.cpu.mem_write(sp,struct.pack('<I',oracle.stop));oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
oracle.cpu.emu_start(0x622f48,oracle.stop,count=1000)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
# Format/output is an explicit platform boundary, with its literal checked.
def debug_output(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ptr=oracle.word(sp+4)
 text=bytes(cpu.mem_read(ptr,29)).split(b'\0')[0];assert text==b'Score::RESET ...............\n',text
 n=oracle.word(DIAG);assert n<20;oracle.setword(DIAG,n+1)
 h=0
 for ch in text:h=(h*33+ch)&0xffffffff
 cpu.mem_write(DIAG+16+n*16,struct.pack('<4I',h,oracle.word(SCORE+0x1538),oracle.word(SCORE+0x54),oracle.word(SCORE+0x38)))
 if oracle.word(DIAG+8):oracle.setword(oracle.word(DIAG+8),oracle.word(DIAG+12))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,begin=0x401c30,end=0x401c30)
fields={p for p in prior['pointer_fields'] if p<BASE+0x100000}|{WIDGET,WIDGET+0x28,WIDGET+0x40,NUMERIC,NUMERIC+0x28,NUMERIC+0x40}
def identities(cpu,address,size,user):
 at=cpu.reg_read(UC_X86_REG_ECX);fields.add(at)
 if address in [0x460b80,0x4615d0]:fields.update([at+0x28,at+0x40])
for at in [0x460b80,0x4615d0,0x463870,0x460b20,0x460b40,0x4dfa70,0x48d220]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
record=oracle.record
def relocated_record(kind,a,b,c):
 log=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48;pointer=a if kind==2 else c
 for i in range(4):
  if pointer+i*4 in fields:fields.add(log+16+i*4)
 record(kind,a,b,c)
oracle.record=relocated_record
exports=prior['pointer_exports']+[[0x64ddd0,'thug_objective_base_methods'],[0x64ea30,'thug_objective_event_methods'],[0x6474cc,'thug_plain_queue_methods']]
fields.update(objects+[QUEUE])
labels=[];branches=Counter()
branch_at={0x4b0d30:'delete_previous_child',0x4b0eaf:'check_auto_height',0x4b0f29:'auto_height_measure',0x4b0fbf:'fixed_height_ring',0x4b0fa3:'second_wrap',0x4b0fe2:'create_text_child',0x4b1139:'row_ring_reset',0x561701:'clear_combo_text',0x56170f:'run_combo_notification'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
branch_at.update({0x561944:'integer_multiplier',0x561965:'fractional_multiplier',0x56198a:'plain_points',0x5618fc:'zero_points',0x564ae3:'mode_starts_at_100',0x564ade:'mode_starts_at_zero',0x564aaa:'local_score_text_reset',0x564b2d:'special_broadcast',0x564b69:'local_component_reset',0x5183ae:'guarded_score_event'})
branch_at.update({0x557547:'already_active_return',0x5573f4:'player_score_reset',0x55743d:'parent_lookup',0x557455:'inherit_parent_timer',0x557486:'root_uninitialize',0x55749c:'self_uninitialize',0x5574be:'initialize_inactive',0x557500:'activation_script',0x557515:'offline_flag',0x557525:'queue_insert'})
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([PRINT] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='multiline'):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=DIAG and at+len(data)//2>=DIAG+4:
    current=int.from_bytes(bytes.fromhex(data)[DIAG-at:DIAG-at+4],'little');s['callbacks']=current-previous;previous=current
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%25==0:print('Original objective dispatch cases:',len(labels),flush=True)
 return stages

def texts_patch(texts,capacity=3,width=80,scale=1,spacing=1,automatic=0):
 p=[patch(WIDGET+0x190,'<i',capacity),patch(WIDGET+0x160,'<f',width),patch(WIDGET+0x19c,'<2f',scale,spacing),patch(WIDGET+0x1b1,'<B',automatic)]
 for i,t in enumerate(texts):
  assert len(t)<196;p += [raw(TEXTS+i*256,t+b'\0'),raw(TRICKS+i*256+0x5c,t+b'\0')]
 return p

def setup(children=0):
 calls=[call(0x4b3fd0,args=[32]),call(0x461a00,UM,[WIDGET]),call(0x41d1d0,REF,[WIDGET]),call(0x4ab250,UM,[REF,0])]
 for i in range(children):
  at=OBJ+i*512
  calls += [call(0x4b0920,at),call(0x461930,at,[0x100+i]),call(0x461a00,UM,[at]),call(0x41d1d0,REF+(i+1)*16,[at]),call(0x4aa8e0,at,[REF if i<2 else REF+i*16,1]),call(0x4ab250,UM,[REF+(i+1)*16,0])]
 return calls
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
def numeric_setup():return [call(0x461a00,UM,[NUMERIC])]

class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.extra=[]
 def alloc(self,data):
  at=GOAL_GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GOAL_GRAPH+len(self.data)<BASE+SIZE;return at
 def text(self,s):return self.alloc(s+b'\0')
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2+(i&1),0x5a,0,name,value&0xffffffff,0)) for i,(name,kind,value) in enumerate(entries)]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GOAL_GRAPH+12,b)
  return self.alloc(struct.pack('<II',0xabcdef01,nodes[0] if nodes else 0))
 def array(self,kind,items):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items)) if items else 0
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items),value))
 def header(self,at,source):self.extra.append(raw(at,self.data[source-GOAL_GRAPH:source-GOAL_GRAPH+8]))
 def symbol(self,name,kind,value):
  bucket=SYMBOLS+(name&4095)*4;old=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  self.buckets[bucket]=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,old))
 def patches(self):return [raw(GOAL_GRAPH,self.data)]+[patch(at,'<I',v) for at,v in self.buckets.items()]+self.extra
 def goal(self,i,params=(),state=None,flags=0x80,active=0):
  p=self.structure(params);s=self.structure([(0x700+i,1,7)]) if state is None else state
  self.extra += [patch(objects[i]+0x1c,'<2I',p,s),patch(objects[i]+0x6c,'<2B',flags,active)]
  return p,s
 def children(self,i,ids):
  links=[self.alloc(struct.pack('<2IB3x',id_,0,0xff)) for id_ in ids]
  for a,b in zip(links,links[1:]):struct.pack_into('<I',self.data,a-GOAL_GRAPH+4,b)
  self.extra.append(patch(objects[i]+0x28,'<I',links[0] if links else 0))
 def parent(self,i,parent):
  self.extra += [patch(objects[i]+0x2c,'<I',PARENTS+i*4),patch(PARENTS+i*4,'<I',parent)]
 def queue(self,indices):
  nodes=[objects[i] for i in indices]
  for j,node in enumerate(nodes):self.extra.append(patch(node+12,'<2I',nodes[j-1] if j else QUEUE,nodes[j+1] if j+1<len(nodes) else QUEUE))
  self.extra.append(patch(QUEUE+12,'<2I',nodes[-1] if nodes else QUEUE,nodes[0] if nodes else QUEUE))

rng=random.Random(0x557360)
def environment():
 b=Build()
 for i in range(8):b.goal(i);b.parent(i,0)
 b.queue([])
 return b

def run(b,calls=None,p=(),changes=None,label='goal activation'):
 return case(calls or [call(0x557360,OBJECT),call(0x557360,OBJECT)],b.patches()+list(p),changes,label)

def player_patches(count=0,hidden=0,local=0,special=0):
 p=[patch(PLAYER_NODES+count*16+4,'<I',0xffffffff)]
 for i in range(8):
  p += [patch(PLAYERS+i*512+0x1d0,'<I',4 if hidden&(1<<i) else 0),patch(BODIES+i*0x400+0xbc,'<B',local if not i else 0),patch(SCORES[i]+0x74,'<B',special),patch(SCORES[i]+0x1538,'<2I',0x11220000+i,0x33550000+i)]
 return p

def ui_setup():return setup(2)+numeric_setup()
import zlib
def crc(s):return zlib.crc32(s.lower().encode())^0xffffffff
NATIVE_NAMES=['GoalManager_ActivateGoal','GoalManager_DeactivateGoal','GoalManager_ClearLastGoal']
NATIVE_ADDR=[0x559230,0x559290,0x5592f0]
NATIVE_KEYS=[crc(s) for s in NATIVE_NAMES]
bindings=json.loads((ROOT/'local/analysis/script-bindings.json').read_text())
for name,at in zip(NATIVE_NAMES,NATIVE_ADDR):assert any(e['name']==name and int(e['address'],16)==at for e in bindings)
function_exports=[[at,'thug_script_goal_'+name] for at,name in zip(NATIVE_ADDR,['activate','deactivate','clear_last'])]
PROGRAM=BASE+0x174000
STATE=BASE+0x17d000
CONNECTION1,CONNECTION2=BASE+0x134000,BASE+0x136000
ALT_GAME,ALT_MANAGER=BASE+0x139000,BASE+0x13a000
fields.add(DIAG+8);exports += [[0x7ce478,'thug_game_context']]
def word(n):return struct.pack('<I',n&0xffffffff)
def name_token(n):return b'\x16'+word(n)
def command(i,id_=0x100,fast=False):
 head=b'\x43'+word(NATIVE_ADDR[i]) if fast else name_token(NATIVE_KEYS[i])
 return head+(name_token(0xa1dc81f9)+b'\x07'+name_token(id_) if i<2 else b'')
def natives(b):
 for key,at in zip(NATIVE_KEYS,NATIVE_ADDR):
  b.symbol(key,8,at);fields.add(b.buckets[SYMBOLS+(key&4095)*4]+12)
def program(b,id_,body):
 assert id_ in [5,6,7,8] and len(body)<0x1000
 i=id_-3;at=PROGRAM+(id_-5)*0x1000
 b.extra += [raw(at,body),patch(META+i*256+12,'<I',at),patch(META+i*256+36,'<I',at)]
 # Direct-pointer tokens are relocation sites, including unaligned operands.
 for offset in range(len(body)-4):
  if body[offset]==0x43 and int.from_bytes(body[offset+1:offset+5],'little') in NATIVE_ADDR:fields.add(at+offset+1)
def args(b,id_=0x100,allow=0):return b.structure([(0xa1dc81f9,13,id_)]+([(0,13,0x9ac8d54f)] if allow else []))
def manager_call(id_=0x100,allow=0,manager=MANAGER):return call(0x557fc0,manager,[id_,allow])
def native_call(at,params=0):return call(at,args=[params,0])
def sync(id_,params=0):return call(0x475790,args=[id_,params,0,0])
def dispatch(b,calls,p=(),changes=None,label='goal dispatch'):
 return case(calls,b.patches()+list(p),changes,label)

# Original lookups retain cache mutations even for absent keys and both forms
# of allow-missing. The second successful activation returns zero unchanged.
for id_ in [0,0xdeadbeef]+[0x100+i for i in range(8)]:
 for allow in [0,1,0x100,0x101,0xffffff00,0xffffffff]:
  b=environment();stages=dispatch(b,[manager_call(id_,allow),manager_call(id_,allow)],label='manager lookup, missing flag byte and repeat activation')
  assert stages[0]['result']==int(0x100<=id_<0x108) and stages[1]['result']==0
for flags in [0,1,0x20,0x80]:
 for active in [0,1]:
  for select in [0,1]:
   for parent in [0,0x101]:
    b=environment();b.goal(0,[(0,13,0xdbeb46e2)] if select else [],flags=flags,active=active);b.parent(0,parent)
    if active:b.queue([0])
    stages=dispatch(b,[manager_call()],label='eligibility, original virtual activation, selection and parent condition')
    activated=not(flags&0x20 or active)
    assert stages[0]['result']==int(activated)
    assert oracle.word(MANAGER+0x2c)==(0x100 if activated and select and not parent else 0xdead1234)

# Availability reads the current level when level=-1; index=-1 short-circuits.
for index_ in [-1,0,3]:
 for level in [-1,0,2]:
  for available in [0,0x80000000]:
   b=environment();slot=MANAGER+0x4c+4*(max(index_,0)+10*(1 if level==-1 else level))
   p=[raw(STATE,bytes(0x800)),patch(STATE+0x630,'<I',1),patch(GAME+0x20,'<I',STATE),patch(OBJECT+0x34,'<2i',level,index_),patch(slot,'<I',available)]
   stages=dispatch(b,[manager_call()],p,label='actual availability grid and current-level lookup')
   assert stages[0]['result']==int(index_==-1 or bool(available))

# Native wrappers use the exact callable ABI and distinguish found/inactive
# deactivation from an absent goal. ClearLastGoal always returns AL=1.
for id_ in [0x100,0x103,0xdeadbeef]:
 for allow in [0,1]:
  b=environment();a=args(b,id_,allow)
  stages=dispatch(b,[native_call(0x559290,a),native_call(0x559230,a),native_call(0x559230,a),native_call(0x559290,a),native_call(0x559290,a),native_call(0x5592f0)],label='actual native activate/deactivate/clear lifecycle and return semantics')
  exists=int(id_ in [0x100,0x103]);assert [s['result'] for s in stages]==[exists,exists,0,exists,exists,1]
  assert oracle.word(MANAGER+0x2c)==0

# Real native symbols are dispatched by the scheduler, including the temporary
# script-instance path. No gameplay callback is replaced in the oracle or Wasm.
for spawn in [False,True]:
 for count,hidden,local in [(0,0,0),(1,0,1),(8,0xaa,1)]:
  b=environment();natives(b);a=args(b);b.goal(0,[(0,13,0x4599b58c),(0,13,0xdbeb46e2)])
  calls=ui_setup()
  for key in [NATIVE_KEYS[0],NATIVE_KEYS[1],NATIVE_KEYS[0],NATIVE_KEYS[2]]:
   calls.append(call(0x475420,args=[key,a,0,0,0,0,0,0,0,0]) if spawn else sync(key,a))
  dispatch(b,calls,player_patches(count,hidden,local,1),label='native spawn/synchronous scheduler dispatch through full score/UI reset')
  assert oracle.word(MANAGER+0x2c)==0
  assert oracle.cpu.mem_read(OBJECT+0x6d,1)[0]&1

# Loaded bytecode executes both symbolic and relocated direct-native opcodes;
# nested goal handlers call another real goal and resume their caller.
for fast in [False,True]:
 for nested in [False,True]:
  for include_score in [False,True]:
   b=environment();natives(b)
   params=[(0,13,0xdbeb46e2)]+([(0,13,0x4599b58c)] if include_score else [])
   b.goal(0,params+([(0x4999fb52,13,6)] if nested else []));b.goal(1,params)
   program(b,5,b'\x01'+command(0,fast=fast)+b'\x01'+command(1,fast=fast)+b'\x01'+command(0,fast=fast)+b'\x01'+command(2,fast=fast)+b'\x01\x24')
   program(b,6,b'\x01'+command(0,0x101,fast)+b'\x01\x24')
   dispatch(b,ui_setup()+[sync(5)],player_patches(1,0,1,1),label='real QB symbolic/direct native commands, nested activation and caller resumption')
   assert oracle.word(MANAGER+0x2c)==0 and oracle.word(OBJECT+0x44)==0
   assert oracle.cpu.mem_read(objects[1]+0x6d,1)[0]&1==int(nested)

# Predicates run the real native command through the original expression parser
# and yield its boolean result into an ordinary script argument assignment.
for id_ in [0x100,0xdeadbeef]:
 b=environment();natives(b);b.goal(0,[(0,13,0x4599b58c)])
 body=b'\x01'+name_token(0x701)+b'\x07\x0e'+command(0,id_)+b'\x0f\x01\x24'
 program(b,5,body)
 dispatch(b,ui_setup()+[sync(5)],player_patches(1,0,1,1),label='real native activation from QB expression predicate with scoped services')
 assert bool(oracle.cpu.mem_read(OBJECT+0x6d,1)[0]&1)==(id_==0x100)

# Poison the ambient service record: runtime entry points must supply their own
# memory/diagnostics and restore the previous binding after nested execution.
for route in ['native_sync','native_spawn','symbolic','direct','predicate']:
 b=environment();natives(b);a=args(b)
 b.goal(0,[(0,13,0x4599b58c),(0x4999fb52,13,6)])
 b.goal(1,[(0,13,0x4599b58c)])
 program(b,6,b'\x01'+command(0,0x101)+b'\x01\x24')
 body=command(0,fast=route=='direct')
 if route=='predicate':body=name_token(0x701)+b'\x07\x0e'+body+b'\x0f'
 program(b,5,b'\x01'+body+b'\x01\x24')
 action=sync(NATIVE_KEYS[0],a) if route=='native_sync' else call(0x475420,args=[NATIVE_KEYS[0],a,0,0,0,0,0,0,0,0]) if route=='native_spawn' else sync(5)
 dispatch(b,ui_setup()+[action],player_patches(1,0,1,1)+[patch(SERVICES,'<2I',0,0)],label='poisoned ambient services restored after '+route+' with real nested score/UI resets')
 assert oracle.word(DIAG)==2 and oracle.cpu.mem_read(objects[1]+0x6d,1)[0]&1

# The native entry captures its manager. Score diagnostic mutation changes the
# global context during activation; last_goal must still target that manager.
for direct in [False,True]:
 b=environment();natives(b);a=args(b);b.goal(0,[(0,13,0x4599b58c),(0,13,0xdbeb46e2)])
 p=player_patches(1,0,1,1)+[raw(ALT_GAME,bytes(0x400)),patch(ALT_GAME+0x34,'<I',NODES),patch(ALT_GAME+0x38c,'<I',ALT_MANAGER),raw(ALT_MANAGER,bytes(0x400)),patch(ALT_MANAGER+0x18,'<5I',0x6474cc,0xffffffff,0,ALT_MANAGER+0x18,ALT_MANAGER+0x18),patch(DIAG+8,'<2I',0x7ce478,ALT_GAME)]
 fields.add(ALT_MANAGER+0x18)
 dispatch(b,ui_setup()+[native_call(0x559230,a) if direct else sync(NATIVE_KEYS[0],a)],p,label='native captured manager survives global replacement during actual score reset')
 assert oracle.word(MANAGER+0x2c)==0x100 and oracle.word(ALT_MANAGER+0x2c)==0

# Parse every exact archived training flag array, then execute the native
# start/stop commands from real bytecode, with complete score/UI effects.
token_fixture=json.loads((out/'script-tokens-fixtures.json').read_text())
token_report=json.loads((out.parent/'script-tokens.json').read_text());token_memory=(out/token_fixture['memory']).read_bytes()
arrays=json.loads((ROOT/'local/analysis/training-objective-arrays.json').read_text());assets=[]
for entry in arrays:
 asset=next(a for a in token_report['assets'] if a['member']==entry['member'])
 data=token_memory[asset['address']-token_fixture['base']:asset['address']-token_fixture['base']+asset['size']]
 assert hashlib.sha256(data).hexdigest()==asset['sha256']==entry['asset_sha256']
 data=data[entry['offset']:entry['offset']+entry['bytes']];assert data[0]==5 and data[-1]==6
 b=environment();natives(b)
 mode=0x9abcdef0;setting=b.structure([(mode,1,0)])
 b.extra += [patch(MANAGER+0x398,'<I',setting),patch(SETTINGS+24,'<I',mode)]
 level=b.structure([(0xcc3c4cc4,12,PARSED)])
 b.goal(0,[(0x85104ab3,12,b.array(10,[level])),(0x398b1b8b,13,6),(0x4999fb52,13,7),(0,13,0x4599b58c),(0,13,0xdbeb46e2)])
 program(b,5,b'\x01'+command(0)+b'\x01'+command(1)+b'\x01'+command(0)+b'\x01\x24')
 dispatch(b,ui_setup()+[call(0x471b00,args=[PARSED,CODE,0]),sync(5)],player_patches(1,0,1,1)+[raw(CODE,data)],label='archived '+entry['script']+' native goal lifecycle @'+str(entry['offset']))
 assert oracle.word(MANAGER+0x2c)==0x100
 assets.append({k:entry[k] for k in ['member','asset_sha256','script','offset','bytes']})
for at in [0x557fc0,0x559230,0x559290,0x5592f0,0x557360,0x557560,0x564a10,0x556a00,0x475790,0x475420,0x474b40,0x554220,0x554460]:assert oracle.coverage[hex(at)]>0,hex(at)
scope='Four original goal dispatch routines: manager activation and actual native GoalManager_ActivateGoal, DeactivateGoal and ClearLastGoal. Exact lookup/cache, eligibility/current-level grid, virtual activation/deactivation, selection/parent semantics and captured-manager behavior. Real native functions execute from symbolic/direct QB commands, expression predicates, synchronous native dispatch, spawned native dispatch and nested goal handlers. All thirty hash-verified archived training flag arrays execute through native script lifecycles with full player score/UI reset. Complete arena/global/return/heap/scope bytes compare exactly; only diagnostic prints are instrumented. Scoped memory/diagnostic ABI adapters and native pointer relocation are port infrastructure, not recovered functions. Required IDs, valid original graphs and successful allocations remain preconditions. Goal completion, remaining native bindings, startup, movement/rendering and browser input/audio integration remain unfinished.'
fixture={'base':BASE,'memory':'objective-dispatch-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'objective-dispatch-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_dispatch_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'training_assets':assets,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'score-display-diagnostics.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
