"""Compare the complete original goal completion, reward, unlock and progress chain."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-completion.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'score-display-fixtures.json').read_text());BASE,SIZE=prior['base'],0x600000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
OBJ,REF,OWNED,EM,TABLES,SCRIPTS,FRAMES,CACHE,SYMBOLS,TLS,LOCALE,UM,EVENTS,ENTRIES,SERVICES=[BASE+x for x in [0x10000,0x16000,0x18000,0x60000,0x6c000,0x70000,0x72000,0x73000,0x78000,0x7e000,0x7e100,0x80000,0x83800,0x83900,0x83a00]]
FONT,METRICS,GLYPHS,BUCKETS,FENTRY=BASE+0x2000,BASE+0x2400,BASE+0x3000,BASE+0x6800,BASE+0x6900
PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE=[TABLES+i*256 for i in range(5)]
WIDGET,ARRAY,TEXTS,TRICKS,ITEMS,SCORE,GAME,NODES,BODIES,LOG,HEAP=[BASE+x for x in [0x85000,0x88000,0x90000,0xb0000,0xe0000,0xe1000,0xe3000,0xe4000,0xe5000,0x200000,0x300000]]
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
for i,name in enumerate([NOTIFY,NUMERIC_NOTIFY,5,6,7,8,0x888ef05e,0x7cf09270]):
 at=META+i*256;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,7,0,name,0,at+64,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,at+64,1,0,0);memory[at+64-BASE:at+66-BASE]=b'\x01\x24'
 slot=CACHETABLE+32+(name&3)*12
 previous=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',previous,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=previous
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',8)
put(SERVICES,'<2I',PRINT,ADAPTER)
for o in objects:put(o+0x38,'<i',-1)
put(MANAGER+0x2c,'<I',0xdead1234)
OWNED_MANAGER,OWNED_BUCKETS,OWNED_VALUES,OWNED_LINKS,COUNTER,STATE,REWARDS,CLIENT,PEERS,PEER_LINKS,POOL,POOL_BLOCKS=[BASE+x for x in [0x180000,0x181000,0x182000,0x184000,0x185000,0x186000,0x188000,0x18a000,0x18c000,0x18d000,0x18f000,0x190000]]
for at,n in [(OWNED_MANAGER,0x40),(OWNED_BUCKETS,0x400),(OWNED_VALUES,0x2000),(OWNED_LINKS,0x800),(COUNTER,32),(STATE,0x800),(REWARDS,8),(CLIENT,0x2000),(PEERS,0x1000),(PEER_LINKS,0x100),(POOL,0x100),(POOL_BLOCKS,0x1000)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(OWNED_MANAGER+8,'<2I',3,OWNED_BUCKETS)
put(GAME+0x20,'<I',STATE)
for o in objects:put(o+0x28,'<I',o+0xe0);put(o+0xe0,'<3I',0,0,0)
put(POOL,'<6I',POOL_BLOCKS,POOL_BLOCKS+1024,0,0,0,POOL_BLOCKS)
for i in range(128):put(POOL_BLOCKS+8*i,'<I',POOL_BLOCKS+8*(i+1) if i<127 else 0)
put(ALLOCATOR+0x12c,'<I',ALLOCATOR+0x600)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value,width in [('thug_ui_manager',0x701440,UM,4),('thug_game_context',0x7ce478,GAME,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_script_updating',0x6f3544,0,1),('thug_script_stop_pending',0x6f3545,0,1),('thug_game_settings',0x7ce470,SETTINGS,4),('thug_network_state',0x7cce14,NETWORK,4),('thug_profile_manager',0x7ce4b4,PROFILES,4)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
index[0x7ce500]=len(globals_);globals_.append(['thug_objective_objects',0x7ce500,4,0]);defaults.append(OWNED_MANAGER)
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
NEW=[(0x557e40,'thug_objective_manager_add_reward',0,'void',True,True,True),(0x555df0,'thug_objective_build_rewards',1,'void',True,True,True),(0x555fb0,'thug_objective_unlock_targets',0,'void',True,True,True),(0x5588d0,'thug_objective_manager_unlock',1,'void',True,True,True),(0x557a40,'thug_objective_unlock',0,'void',True,True,True),(0x554a80,'thug_objective_run_handler',1,'byte',True,True,True),(0x556050,'thug_objective_reward_amount',0,'word',False,False,True),(0x5555e0,'thug_objective_mark_beaten',0,'void',False,False,True),(0x5845c0,'thug_gameplay_add_points',1,'word',False,False,True),(0x584620,'thug_gameplay_add_completion',0,'void',False,False,True),(0x561b40,'thug_score_current',0,'word',False,False,True),(0x533f90,'thug_network_flag_1',0,'word',False,False,True),(0x588400,'thug_objective_owned_count',1,'word',False,False,True),(0x5b8060,'thug_object_table_visit',2,'void',False,False,True),(0x588120,'thug_object_count_owned_callback',2,'void',False,False,False),(0x5576d0,'thug_objective_win',0,'byte',True,True,True),(0x558030,'thug_objective_manager_win',1,'byte',True,True,True),(0x559310,'thug_script_goal_win',2,'byte',False,False,False)]
NEW.append((0x409030,'thug_script_structure_allocate',1,'word',True,False,False))
for row in NEW:bind(*row)
functions['0x5b8060']['pointer_args']=[0]
observe=[int(k,16) for k in functions]+[0x401cc0,0x4a8940,0x4abd40,0x461140,0x473800,0x460470,0x474540,0x4748e0,0x473a80,0x475790,0x474420,0x4621d0,0x6234fe,0x4b1830,0x4b0760,0x48d5f0,0x4b3e70,0x48d1d0,0x4abbe0,0x4af720,0x4af8c0,0x4a94a0,0x4ac400,0x4aaff0,0x4637c0,0x4637e0,0x561890,0x564a10,0x402200,0x6285af,0x6286ab,0x5532a0,0x5612d0,0x518390,0x460a20,0x5633e0,0x45db90]
observe=list(dict.fromkeys(observe+[0x557360,0x557270,0x554bd0,0x553ea0,0x557f90,0x55dbe0,0x5372c0,0x537010,0x476b40,0x477860,0x5566d0,0x556a00,0x44e4f0,0x554220,0x554460,0x559110]))
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=12000000,scope_entries={ALLOCATOR+0x200:6,ALLOCATOR+0x300:1,ALLOCATOR+0x500:5,ALLOCATOR+0x600:4})
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
heap_record=oracle.record
def relocated_record(kind,a,b,c):
 log=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48;pointer=a if kind==2 else c
 for i in range(4):
  if pointer+i*4 in fields:fields.add(log+16+i*4)
 heap_record(kind,a,b,c)
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
 if len(labels)%25==0:print('Original objective completion cases:',len(labels),flush=True)
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
  p=self.structure([(0x9982e501,13,0x100+i)]+list(params));s=self.structure([(0x700+i,1,7)]) if state is None else state
  self.extra += [patch(objects[i]+0x1c,'<2I',p,s),patch(objects[i]+0x6c,'<2B',flags,active)]
  return p,s
 def children(self,i,ids):
  links=[self.alloc(struct.pack('<2IB3x',id_,0,0xff)) for id_ in ids]
  for a,b in zip(links,links[1:]):struct.pack_into('<I',self.data,a-GOAL_GRAPH+4,b)
  self.extra.append(patch(objects[i]+0x28,'<I',links[0] if links else 0))
 def parent(self,i,parent):
  self.extra.append(patch(objects[i]+0x2c,'<I',self.alloc(struct.pack('<2I',parent,0))))
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
NATIVE_NAMES=['GoalManager_ActivateGoal','GoalManager_DeactivateGoal','GoalManager_ClearLastGoal','GoalManager_WinGoal']
NATIVE_ADDR=[0x559230,0x559290,0x5592f0,0x559310]
NATIVE_KEYS=[crc(s) for s in NATIVE_NAMES]
bindings=json.loads((ROOT/'local/analysis/script-bindings.json').read_text())
for name,at in zip(NATIVE_NAMES,NATIVE_ADDR):assert any(e['name']==name and int(e['address'],16)==at for e in bindings)
function_exports=[[at,'thug_script_goal_'+name] for at,name in zip(NATIVE_ADDR,['activate','deactivate','clear_last','win'])]
PROGRAM=BASE+0x174000
# STATE is allocated above with the progress counters.
CONNECTION1,CONNECTION2=BASE+0x134000,BASE+0x136000
ALT_GAME,ALT_MANAGER=BASE+0x139000,BASE+0x13a000
fields.add(DIAG+8);exports += [[0x7ce478,'thug_game_context']]
def word(n):return struct.pack('<I',n&0xffffffff)
def name_token(n):return b'\x16'+word(n)
def command(i,id_=0x100,fast=False):
 head=b'\x43'+word(NATIVE_ADDR[i]) if fast else name_token(NATIVE_KEYS[i])
 return head+(name_token(0xa1dc81f9)+b'\x07'+name_token(id_) if i!=2 else b'')
def natives(b):
 for key,at in zip(NATIVE_KEYS,NATIVE_ADDR):
  b.symbol(key,8,at);fields.add(b.buckets[SYMBOLS+(key&4095)*4]+12)
def program(b,id_,body):
 assert id_ in [5,6,7,8,0x888ef05e,0x7cf09270] and len(body)<0x1000
 i=[NOTIFY,NUMERIC_NOTIFY,5,6,7,8,0x888ef05e,0x7cf09270].index(id_);at=PROGRAM+(i-2)*0x1000
 b.extra += [raw(at,body),patch(META+i*256+12,'<I',at),patch(META+i*256+36,'<I',at)]
 # Direct-pointer tokens are relocation sites, including unaligned operands.
 for offset in range(len(body)-4):
  if body[offset]==0x43 and int.from_bytes(body[offset+1:offset+5],'little') in NATIVE_ADDR:fields.add(at+offset+1)
def args(b,id_=0x100,allow=0):return b.structure([(0xa1dc81f9,13,id_)]+([(0,13,0x9ac8d54f)] if allow else []))
def manager_call(id_=0x100,allow=0,manager=MANAGER):return call(0x557fc0,manager,[id_,allow])
def native_call(at,params=0):return call(at,args=[params,0])
def sync(id_,params=0):return call(0x475790,args=[id_,params,0,0])
def dispatch(b,calls,p=(),changes=None,label='goal completion'):
 return case(calls,b.patches()+list(p),changes,label)

function_exports.append([0x588120,'thug_object_count_owned_callback'])
exports += [[0x6474d0,'thug_reliable_queue_methods'],[0x6474d4,'thug_sequenced_queue_methods'],[0x647578,'thug_plain_node_methods'],[0x64757c,'thug_reliable_node_methods'],[0x647580,'thug_sequenced_node_methods']]
for at in [0x4555f0,0x455620,0x455650]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
for at,branch_name in {0x5579df:'child_progression',0x55777d:'record_from_player',0x5577d0:'record_improved',0x557821:'reward_built',0x55784e:'unlock_targets',0x5578e3:'mark_beaten',0x557919:'career_points',0x5579a1:'classic_completion',0x558127:'network_win_queued',0x555ea9:'extra_binding_reward',0x555f29:'template_flag_conversion',0x555f67:'fallback_flag_reward',0x555f94:'fallback_integer_reward'}.items():
 branch_at[at]=branch_name;oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
old_environment=environment
def environment():
 b=old_environment();b.symbol(0x67f6e334,10,b.structure([]));b.symbol(0x20297d6f,1,4);b.symbol(0x2f507903,1,0)
 b.header(PROFILE+0x5c,b.structure([(0xac9b9eda,1,3)]))
 return b
def settings(b,mode=0,career=0,classic=0,graffiti=0):
 b.header(SETTINGS+4,b.structure([(0xa1dc81f9,13,mode),(0x1ded1ea4,1,career),(0x5a2c589a,1,classic),(0x11941568,1,graffiti)]))
def difficulty(b,value):b.extra.append(patch(MANAGER+0x398,'<I',b.structure([(0xface,1,value)])));settings(b,mode=0xface)
def parent_list(b,i,ids):
 links=[b.alloc(struct.pack('<2I',id_,0)) for id_ in ids]
 for a,c in zip(links,links[1:]):struct.pack_into('<I',b.data,a-GOAL_GRAPH+4,c)
 b.extra.append(patch(objects[i]+0x2c,'<I',links[0] if links else 0))
def queue_node(at,method=0x6474cc,value=0xffffffff,prev=None,next_=None):
 fields.add(at);return patch(at,'<5I',method,value,0,at if prev is None else prev,at if next_ is None else next_)
def online(active=True):
 p=[patch(NETWORK,'<3I',12 if active else 0,CLIENT,CLIENT),patch(NETWORK+0x38,'<B',3),patch(CLIENT+8,'<I',0xfffffffd),queue_node(CLIENT+0x1e8c,prev=PEER_LINKS,next_=PEER_LINKS),queue_node(PEER_LINKS,0x647578,PEERS,CLIENT+0x1e8c,CLIENT+0x1e8c),patch(PEERS+0x3c,'<I',17),patch(PEERS+0x60,'<I',1),patch(PEERS+0x78+8*4,'<I',0xffffffff)]
 for i in range(3):p.append(queue_node(PEERS+i*20,0x6474cc+i*4))
 return p
def owned(shift=3,owner=0x100):
 count=1<<(shift&31);assert count<=32
 p=[patch(OWNED_MANAGER+8,'<2I',shift,OWNED_BUCKETS)]
 for i in range(count):
  head=OWNED_BUCKETS+12*i;link=OWNED_LINKS+24*i;v=OWNED_VALUES+256*i
  p += [patch(head,'<3I',i,v,link),patch(link,'<3I',i+100,v+128,link+12),patch(link+12,'<3I',i+200,0,0),patch(v+0x3c,'<IB',owner,1 if i%3 else 0),patch(v+128+0x3c,'<IB',owner if i%2 else owner^1,255)]
 return p
def win(o=OBJECT):return call(0x5576d0,o)
def manager_win(id_=0x100):return call(0x558030,MANAGER,[id_])

# Allocation uses the selected pool even when empty, with no heap fallback.
for selected in [0,1]:
 for kind in ['heap','pool','empty']:
  for size in [0,8,32]:
   p=[patch(POOL+0x14,'<I',0)] if kind=='empty' else []
   case([call(0x409030,args=[size])],p,
    {0x6f3614:selected,0x6f361c+selected*4:0 if kind=='heap' else POOL},label='structure allocation '+kind+' selection and size')

# Integer counter boundaries and deliberate aliasing with totals/current level.
for level in [0,1,18,42,84,86,0xffffffff]:
 for amount in [0,1,0x7fff,0x8000,0xffff,0x10001,0xffffffff]:
  p=[raw(STATE,bytes([0xff])*0x800),patch(STATE+0x630,'<I',level)]
  case([call(0x5845c0,STATE,[amount])],p,label='wrapping halfword progress counters and aliased offsets')
 case([call(0x584620,STATE)],[raw(STATE,bytes([0xff])*0x800),patch(STATE+0x630,'<I',level)],label='wrapping byte progress counters and aliased offsets')
for flag in [0,1,2,3,12,13,0xffffffff]:case([call(0x533f90,NETWORK)],[patch(NETWORK,'<I',flag)],label='independent network flag predicate')
for active in [0,1,255]:
 for owner in [0,1,0x7fff,0xffff8000,0xffffffff]:
  for start in [0,0xffffffff]:
   case([call(0x588120,args=[OWNED_VALUES,COUNTER])],[patch(OWNED_VALUES+0x3c,'<IB',owner,active),patch(COUNTER,'<2I',start,owner)],label='actual owned-object callback and count wrap')
for shift in [0,1,2,3,4,5,32,33]:
 for owner in [0x100,0xffff8000,0xffffffff]:
  case([call(0x5b8060,OWNED_MANAGER+8,[0x588120,COUNTER]),call(0x588400,OWNED_MANAGER,[owner])],owned(shift,owner)+[patch(COUNTER,'<2I',0,owner)],label='real callback through overflow-first object-table visitation')
# Aliased callback state mutates either the current next link or the head value.
for context in [OWNED_LINKS+8,OWNED_BUCKETS+4]:
 p=owned(0,1)+[patch(OWNED_VALUES+0x3c,'<IB',1,1),patch(OWNED_VALUES+128+0x3c,'<IB',1,1)]
 if context==OWNED_LINKS+8:
  p += [patch(context+4,'<I',1)]
 else:
  p += [patch(OWNED_VALUES+0x3c,'<IB',OWNED_LINKS,1),patch(OWNED_VALUES+128+0x3c,'<IB',OWNED_LINKS,1)]
 case([call(0x5b8060,OWNED_MANAGER+8,[0x588120,context])],p,label='callback mutation preserves captured next and late head-value read')

# Complete score accessor chooses either stored score or real owned-object count.
for network_flag in [0,1,12,13]:
 for override in [0,1]:
  for mode in [0,1]:
   for id_ in [0x100,0x8000,0xffff]:
    b=environment();settings(b,graffiti=mode);b.symbol(0x2f507903,1,override)
    signed=id_ if id_<0x8000 else id_-0x10000
    dispatch(b,[call(0x561b40,SCORE)],owned(3,signed&0xffffffff)+[patch(SCORE+8,'<H',id_),patch(SCORE+12,'<I',0xdeadbeef),patch(NETWORK,'<I',network_flag)],label='score accessor uses real ownership count with signed player id')

# Multiple parents and shared ancestors, both original concrete virtual tables.
for net in [False,True]:
 for mode in [0,0xec200eaa]:
  for flags in [0,4,8,0xff]:
   b=environment();settings(b,mode)
   for i in range(4):b.goal(i,flags=flags)
   parent_list(b,0,[0x101,0x102]);parent_list(b,1,[0x103]);parent_list(b,2,[0x103]);parent_list(b,3,[0,0x100])
   dispatch(b,[call(0x5555e0,OBJECT),call(0x5555e0,OBJECT)],online(net),label='recursive beaten marking across full parent DAG and zero-id terminator')
   for i in range(4):assert oracle.cpu.mem_read(objects[i]+0x6c,1)[0]==flags|(8 if net and mode==0xec200eaa else 4)

# Scalar/difficulty-array reward amounts, including missing/out-of-range arrays.
for count in [0,1,2,3,5]:
 for diff in [0,1,2,3,0xffffffff]:
  b=environment();difficulty(b,diff);b.goal(0,[(0xbaffb052,12,b.array(1,[0x80000000+i for i in range(count)]))])
  dispatch(b,[call(0x556050,OBJECT)],label='difficulty-indexed reward amount bounds')
for value in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 b=environment();b.goal(0,[(0xbaffb052,1,value)])
 dispatch(b,[call(0x556050,OBJECT)],label='scalar reward amount bit preservation')
b=environment();dispatch(b,[call(0x556050,OBJECT)],label='missing reward amount')

# Unlocks clear disabled state before checks, initialize selectively and always
# run the offline unlock handler. Real script handlers can mutate last_goal.
for net in [False,True]:
 for flags in [0,0x20,0x24,0x28,0x2c]:
  for mode,extra in [(0,0),(0x4c10de52,0),(0,0x4e863e93),(0,0x981d3ad0)]:
   b=environment();natives(b);settings(b,mode);b.goal(1,[(0x951b4f10,13,6),(0x398b1b8b,13,7)]+([(0,13,extra)] if extra else []),flags=flags)
   program(b,6,b'\x01'+command(2)+b'\x01\x24')
   dispatch(b,[call(0x5588d0,MANAGER,[0x101]),call(0x557a40,objects[1])],online(net),label='manager and direct unlock through actual initialization/native QB handlers')
   assert not(oracle.cpu.mem_read(objects[1]+0x6c,1)[0]&0x20)
for values in [None,0x101,[0,0x101,0x102,0x101],[],[0]]:
 b=environment();b.goal(1,flags=0x20);b.goal(2,flags=0x20)
 params=[] if values is None else [(0x0232844a,12,b.array(13,values))] if isinstance(values,list) else [(0x0232844a,13,values)]
 b.goal(0,params)
 dispatch(b,[call(0x555fb0,OBJECT)],label='scalar/array unlock targets, duplicates and skipped zero entries')
for present in [False,True]:
 b=environment();natives(b);b.goal(0,[(0x951b4f10,13,6)] if present else []);program(b,6,b'\x01'+command(2)+b'\x01\x24')
 stages=dispatch(b,[call(0x554a80,OBJECT,[0x951b4f10])],label='optional native-script handler returns presence')
 assert stages[0]['result']==int(present)

# Reward construction: mutable template flags, owned values and fallback fields;
# profile capacity controls the extra binding reward and its parameter changes.
for net in [False,True]:
 for template in ['missing','plain','flag','owned']:
  for fallback in [None,'flag',0,7]:
   b=environment();natives(b)
   params=[] if fallback is None else [(0,13,0xde569045)] if fallback=='flag' else [(0xde569045,1,fallback)]
   b.goal(0,params)
   if template!='missing':
    entries=[(0xabc,1,0x12345678)]
    if template=='flag':entries += [(0,13,0xde569045),(0xde569045,1,9)]
    if template=='owned':entries += [(0xdef,3,b.text(b'owned reward')),(0x123,12,b.array(1,[1,2,3]))]
    reward=b.structure(entries);b.symbol(0x67f6e334,10,b.structure([(0x100,10,reward)]))
   program(b,0x888ef05e,b'\x01'+command(2)+b'\x01\x24')
   dispatch(b,[call(0x555df0,OBJECT,[REWARDS])],online(net)+[patch(MANAGER+0x38,'<2I',0xffffffff,0x7fffffff)],label='full reward template/fallback merge and real manager notification')
for slots in [2,4,5,0xffffffff]:
 for marker in [0,1,2]:
  for excluded in [0,0x8e6014f6]:
   b=environment();b.header(PROFILE+0x5c,b.structure([(0xac9b9eda,1,slots)]));b.goal(0,[(0,13,0xb6432d23),(0xbc678826,1,marker)]+([(0,13,excluded)] if excluded else []))
   dispatch(b,[call(0x555df0,OBJECT,[REWARDS])],label='profile binding capacity and extra reward parameter mutations')
b=environment();natives(b);program(b,0x888ef05e,b'\x01'+command(2)+b'\x01\x24')
dispatch(b,[call(0x557e40,MANAGER)],[patch(MANAGER+0x38,'<2I',0xffffffff,0xffffffff)],label='direct reward counters wrap before notification')

# Leaf completion through every entry point, real score records, reward ownership,
# virtual parent propagation, career/classic counters, native handlers and queues.
for entry in ['direct','manager','native','qb']:
 for net in [False,True]:
  for progress in ['none','career','classic']:
   for record in ['none','score','time','combo','owned']:
    b=environment();natives(b);settings(b,career=progress=='career',classic=progress=='classic',graffiti=record=='owned')
    params=[(0xbaffb052,1,5),(0x90ff204d,13,6)]
    if record in ['score','combo','owned']:params += [(0x96963902,13,0xcd66c8ae)]
    if record=='score':params += [(0xfc9630ab,1,12345)]
    if record=='combo':params += [(0,13,0xc63432a7)]
    if record=='time':params += [(0x96963902,13,0x906b67ba)]
    b.goal(0,params,flags=0x81,active=1);b.queue([0]);a=args(b)
    program(b,6,b'\x01'+command(2)+b'\x01\x24')
    program(b,5,b'\x01'+command(3)+b'\x01\x24')
    action=win() if entry=='direct' else manager_win() if entry=='manager' else native_call(0x559310,a) if entry=='native' else sync(5)
    p=online(net)+owned(3)+[patch(MANAGER+0x2c,'<I',0x100),patch(OBJECT+0x48,'<2I',999999,1),patch(OBJECT+0x60,'<I',12345),patch(SCORE+12,'<I',77),patch(SCORE+0x20,'<I',222),patch(BODIES+0xbc,'<B',1),patch(STATE+0x630,'<I',2)]
    if record=='owned' and not net:p += [patch(NETWORK,'<I',1)]
    dispatch(b,[action,action],p,label='complete '+entry+' goal win '+progress+'/'+record+('/online' if net else '/offline'))
    assert not(oracle.cpu.mem_read(OBJECT+0x6d,1)[0]&1)

# Required child sentinel and captured child pointer survive deactivation and
# self-uninitialization before the original child initialization/activation.
for entry in ['direct','manager','qb']:
 for active in [0,1]:
  b=environment();natives(b);b.goal(0,flags=0x81,active=active);b.goal(1,[(0,13,0x4599b58c)],flags=0x80)
  b.children(0,[0x101]);b.queue([0] if active else []);program(b,5,b'\x01'+command(3)+b'\x01\x24')
  action=win() if entry=='direct' else manager_win() if entry=='manager' else sync(5)
  dispatch(b,ui_setup()+[action],player_patches(1,0,1,1),label='child goal progression through full score/UI activation')
  assert oracle.cpu.mem_read(objects[1]+0x6d,1)[0]&1
  assert oracle.cpu.mem_read(oracle.word(OBJECT+0x28)+8,1)[0]==1

# Repeated wins preserve records when not improved; testing goals skip beaten
# and progress writes. Both owned reward replacement and pool disposal execute.
for score in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 for best in [0,0x7fffffff,0x80000000,0xffffffff]:
  b=environment();b.goal(0,[(0x96963902,13,0xcd66c8ae),(0xfc9630ab,1,score),(0,13,0x54d3cac1)])
  dispatch(b,[win(),win()],[patch(OBJECT+0x4c,'<I',best)],label='signed score record boundaries and repeated testing wins')
for state in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 b=environment();b.goal(0,[(0x96963902,13,0x906b67ba)])
 dispatch(b,[win()],[patch(OBJECT+0x48,'<I',0x80000000),patch(OBJECT+0x60,'<I',state)],label='unsigned best-time record boundaries')
for flags in [4,8,12,0x84]:
 b=environment();b.goal(0,[(0x128b3088,10,b.structure([(0xaaa,3,b.text(b'old owned reward'))]))],flags=flags)
 dispatch(b,[win()],label='already beaten goal removes owned previous reward data')
for id_ in [0,0xdeadbeef]:
 b=environment();a=args(b,id_);stages=dispatch(b,[manager_win(id_),native_call(0x559310,a)],label='missing manager/native win preserves lookup effects')
 assert all(s['result']==0 for s in stages)

# Selected structure pools retain rewards across the first win and release them
# on the second; completion also unlocks a real goal and marks its parent chain.
for selected in [0,1]:
 for progress in ['none','career','classic']:
  b=environment();natives(b);settings(b,career=progress=='career',classic=progress=='classic')
  b.goal(0,[(0xbaffb052,1,7),(0x0232844a,13,0x104)])
  b.goal(4,[(0x951b4f10,13,6)],flags=0x20)
  nested=b.structure([(0x987,3,b.text(b'nested reward'))])
  reward=b.structure([(0x456,10,nested),(0x654,12,b.array(10,[nested,nested]))])
  b.symbol(0x67f6e334,10,b.structure([(0x100,10,reward)]))
  parent_list(b,0,[0x101,0x102]);parent_list(b,1,[0x103]);parent_list(b,2,[0x103])
  program(b,6,b'\x01'+command(2)+b'\x01\x24')
  dispatch(b,[manager_win(),manager_win()],[patch(MANAGER+0x2c,'<I',0x103)],
   {0x6f3614:selected,0x6f361c+selected*4:POOL},label='pooled reward lifetime, parent-chain win and real goal unlock '+progress)
  for i in range(4):assert oracle.cpu.mem_read(objects[i]+0x6c,1)[0]&4
  assert not(oracle.cpu.mem_read(objects[4]+0x6c,1)[0]&0x20)
  assert oracle.word(POOL+0x58)>0 and oracle.word(MANAGER+0x2c)==0

# The native script lifecycle now reaches completion with exact archived state.
token_fixture=json.loads((out/'script-tokens-fixtures.json').read_text())
token_report=json.loads((out.parent/'script-tokens.json').read_text());token_memory=(out/token_fixture['memory']).read_bytes()
arrays=json.loads((ROOT/'local/analysis/training-objective-arrays.json').read_text());assets=[]
for entry in arrays:
 asset=next(a for a in token_report['assets'] if a['member']==entry['member'])
 data=token_memory[asset['address']-token_fixture['base']:asset['address']-token_fixture['base']+asset['size']]
 assert hashlib.sha256(data).hexdigest()==asset['sha256']==entry['asset_sha256']
 data=data[entry['offset']:entry['offset']+entry['bytes']]
 b=environment();natives(b);difficulty(b,0);level=b.structure([(0xcc3c4cc4,12,PARSED)])
 b.goal(0,[(0x85104ab3,12,b.array(10,[level])),(0,13,0x4599b58c),(0,13,0xdbeb46e2),(0x90ff204d,13,6)])
 program(b,5,b'\x01'+command(0)+b'\x01'+command(3)+b'\x01\x24')
 program(b,6,b'\x01'+command(2)+b'\x01\x24')
 dispatch(b,ui_setup()+[call(0x471b00,args=[PARSED,CODE,0]),sync(5)],player_patches(1,0,1,1)+[raw(CODE,data)],label='archived '+entry['script']+' actual native activation/completion @'+str(entry['offset']))
 assert oracle.cpu.mem_read(OBJECT+0x6c,1)[0]&4
 assets.append({k:entry[k] for k in ['member','asset_sha256','script','offset','bytes']})
for at,_,*rest in NEW:assert oracle.coverage[hex(at)]>0,hex(at)
for key in ['child_progression','record_from_player','record_improved','reward_built','unlock_targets','mark_beaten','career_points','classic_completion','network_win_queued','extra_binding_reward','template_flag_conversion','fallback_flag_reward','fallback_integer_reward']:assert branches[key]>0,key
scope='Nineteen complete original routines join goal completion, manager/native WinGoal, child progression, score/time records, reward templates and owned reward transfer, selective unlocking and handlers, recursive parent-DAG beaten state, career/classic counters and real network win queueing. Actual native QB start/win commands execute with all thirty exact archived training flag arrays and full local score/UI reset. The score getter uses the real overflow-first table visitor and owned-object callback. Shared structure allocation and disposal preserve selected-pool behavior through nested rewards and QB execution. Complete memory/globals/returns and heap/scope records compare; only diagnostic output is instrumented. Valid original graphs, required parameters/templates, terminating handlers and successful allocations remain contracts. Other native bindings, remaining movement/state parents, startup, rendering and browser input/audio integration remain unfinished.'
fixture={'base':BASE,'memory':'objective-completion-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'objective-completion-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_completion_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'training_assets':assets,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'score-display-diagnostics.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
