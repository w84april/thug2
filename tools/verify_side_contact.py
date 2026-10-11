"""Compare complete side-contact parents, input history and vector support."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'side-contact.json';report_path.unlink(missing_ok=True)
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
for i,name in enumerate([NOTIFY,NUMERIC_NOTIFY,5,6,7,8,0x888ef05e,0x7cf09270,0x5ed34deb,0xf2e85a34,0x96de9a0c]):
 at=META+i*256;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,7,0,name,0,at+64,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,at+64,1,0,0);memory[at+64-BASE:at+66-BASE]=b'\x01\x24'
 slot=CACHETABLE+32+(name&3)*12
 previous=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',previous,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=previous
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',11)
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
PHYS,PHYS2,SKATER_STATE,SKATER_STATE2,NAME_CONTEXT,NAME_CONTEXT2,INPUT,SOUND,SOUND2,EVENT_COMPONENT,MAP_BUCKETS,RING,MAP_OBJECTS=[BASE+x for x in [0x191000,0x193000,0x195000,0x195200,0x196000,0x198000,0x19a000,0x19b000,0x19b100,0x19c000,0x19d000,0x19e000,0x19f000]]
for at,n in [(PHYS,0x1534),(PHYS2,0x1534),(SKATER_STATE,0x100),(SKATER_STATE2,0x100),(NAME_CONTEXT,0x2000),(NAME_CONTEXT2,0x2000),(INPUT,0x200),(SOUND,0x30),(SOUND2,0x30),(EVENT_COMPONENT,0x100),(MAP_BUCKETS,0x100),(RING,0x804),(MAP_OBJECTS,0x400)]:memory[at-BASE:at-BASE+n]=bytes(n)
for phy,state,context,sound in [(PHYS,SKATER_STATE,NAME_CONTEXT,SOUND),(PHYS2,SKATER_STATE2,NAME_CONTEXT2,SOUND2)]:
 put(phy+12,'<I',BODIES);put(phy+0x150c,'<I',INPUT);put(phy+0x1514,'<2I',sound,context);put(phy+0x1528,'<I',state)
 put(state+12,'<I',WIDGET);put(context+0x28,'<I',BODIES)
put(EVENT_COMPONENT+4,'<I',0x43686585);put(EVENT_COMPONENT+12,'<2I',BODIES,SCORE_COMPONENTS)
put(BODIES+0x100,'<I',EVENT_COMPONENT);put(BODIES+0x1b0,'<I',0xabc000)
put(OWNED_MANAGER+0x20,'<2I',2,MAP_BUCKETS)
for i in range(4):
 put(MAP_BUCKETS+12*i,'<3I',0xabc000+i,MAP_OBJECTS+32*i,0);put(MAP_OBJECTS+32*i+0x14,'<I',0xe0+i)

# Keep the initialized script/goal arena at its original addresses and add the
# previously verified training collision scene below it. No gameplay hook is used.
OLD_BASE=BASE;BASE,SIZE=0x1000000,0x1500000
memory=bytearray(b'\xad'*(OLD_BASE-BASE))+memory
memory.extend(b'\xad'*(SIZE-len(memory)))
world=json.loads((out/'skater-fixtures.json').read_text());loader=world['loader'];a=world['addresses']
DATA,GRID,SCENE,SCENES,RUNTIME,COLL_NODES,OWNERS,REFS,COLLISION_HEAP=[a[k] for k in ['data','grid','scene','scenes','runtime','nodes','owners','refs','heap']]
QUERY=0x2000500;NODE_TABLE=0x1600000;NODE_ARRAY=0x1611000
GATE,GROUND_GATE,COLLISION_EVENT,VECTORS=0x1620000,0x1621000,0x1622000,0x1623000

def copy(at,data):memory[at-BASE:at-BASE+len(data)]=data
for at,key in [(DATA,'loaded'),(GRID,'grid'),(COLLISION_HEAP,'heap')]:copy(at,(out/loader[key]).read_bytes())
copy(SCENE,bytes(0xd8));put(SCENE+0xd4,'<I',GRID)
put(SCENES,'<8I',0,SCENE,0,SCENES+16,0,0xffffffff,0,SCENES+16)
put(COLL_NODES,'<4I',0,0xffffffff,0,COLL_NODES)
copy(RUNTIME,bytes.fromhex(world['world'][0]['actors']));copy(OWNERS,bytes.fromhex(world['owners']));copy(REFS,bytes.fromhex(world['references']))
copy(NODE_TABLE,b'\xff'*0x10000+bytes(16));copy(NODE_ARRAY,bytes(32))
for at,n in [(GATE,0x100),(GROUND_GATE,0x100),(COLLISION_EVENT,0x100),(VECTORS,0x1000),(QUERY,12)]:copy(at,bytes(n))
probe=bytes.fromhex(next(c['output'] for c in world['constructors'] if c['kind']=='default'))
for phy in [PHYS,PHYS2]:
 copy(phy+0xa8,probe);copy(phy+0x158,probe)
 put(phy+0x14c,'<I',0);put(phy+0x1fc,'<I',0)
 put(phy+4,'<I',0x5bd63b29);put(phy+0x1510,'<I',COLLISION_EVENT);put(phy+0x152c,'<2I',GROUND_GATE,GATE)
 put(phy+0x68,'<4f',0,1,0,0);put(phy+0x22a,'<B',1)
put(COMPONENT+16,'<I',PHYS);put(COLLISION_EVENT+12,'<I',BODIES)
for state in [SKATER_STATE,SKATER_STATE2]:put(state+12,'<I',BODIES)
for body in [BODIES,BODIES+0x400]:
 put(body+0x4c,'<4f',20000,20000,20000,1);put(body+0x5c,'<4f',20000,20000,19999,1)
 put(body+0x6c,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)
 put(body+0xac,'<4f',0,0,100,0)
put(NAME_CONTEXT+0xa0c,'<B',1)
put(CONTEXT+16,'<2I',BASE,BASE+SIZE)

initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value,width in [('thug_ui_manager',0x701440,UM,4),('thug_game_context',0x7ce478,GAME,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_script_updating',0x6f3544,0,1),('thug_script_stop_pending',0x6f3545,0,1),('thug_game_settings',0x7ce470,SETTINGS,4),('thug_network_state',0x7cce14,NETWORK,4),('thug_profile_manager',0x7ce4b4,PROFILES,4)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
for name,at,value,width in [('thug_frame_counter',0x7d1ec8,100,4),('thug_frame_rate',0x684fd0,0x42700000,4),('thug_timer_origin',0x696d64,0,4),('thug_timer_offset',0x696d60,0,4),('thug_time_scale',0x67d7c0,0x3f800000,4)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
index[0x7ce500]=len(globals_);globals_.append(['thug_objective_objects',0x7ce500,4,0]);defaults.append(OWNED_MANAGER)
defaults[index[0x7cefa0]]=0
for i in range(8):
 at=0x690fa4+i*4;defaults[index[at]]=0xa5a5a5a5

def glob(name,at,value=0,width=4,offset=0):
 if at in index:defaults[index[at]]=value;return index[at]
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value);return index[at]
glob('thug_collision_scene_list',0x6fa7ec,SCENES);glob('thug_moving_collision_list',0x691984,COLL_NODES)
glob('thug_collision_default_cache',0x691974);glob('thug_collision_select_farthest',0x691910,0,1);glob('thug_collision_grid_stamp',0x693998,1,1)
glob('thug_node_table',0x6f0d84,NODE_TABLE)
for name,address,count in [('thug_collision_selected_scenes',0x6fa738,16),('thug_collision_selected_grids',0x6fa778,16),('thug_collision_grid_output',0x691998,2048)]:
 for j in range(count):glob(name,address+j*4,0,offset=j*4)
for j in range(1024):glob('thug_collision_fallback_indices',0x67c6b8+j*4,j*2|((j*2+1)<<16),offset=j*4)
BUTTONS=[0,0xbc6b118f,0xe3006fc4,0x85981897,0x4b358aeb,0xb7231a95,0xa50950c5,0xd8847efa,0x786b8b68,0x2b489a86,0x321c9756,0x7323e97c,0x20689278,0x26b0c991,0xbfb9982b,0xc8bea8bd,0xf2f1f64e,0x6bf8a7f4,0x1cff9762,0x767a45d7,0xbd30325b,0x9d2d8850]
for j,v in enumerate(BUTTONS):glob('thug_input_button_names',0x67d6d8+j*4,v,offset=j*4)

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
NEW=[(0x556330,'thug_objective_set_flag',3,'byte',True,True,True),(0x559670,'thug_script_goal_set_flag',2,'byte',False,False,False),(0x576520,'thug_objective_handle_event',1,'void',True,True,True),(0x559150,'thug_objective_manager_notify',1,'void',True,True,True),(0x588a20,'thug_objective_notify',1,'byte',True,True,True),(0x5232a0,'thug_skater_set_notification_flag',1,'void',True,True,True),(0x522370,'thug_skater_notify',1,'void',True,True,True),(0x4fded0,'thug_skater_change_state',1,'void',True,True,True)]
for row in NEW:bind(*row)

NEW=[(0x4024a0,'thug_vector_scaled_copy',3,'word',False,False,False),(0x40af20,'thug_vector_divided',3,'word',False,False,False),(0x44e5a0,'thug_input_button_index',1,'word',False,False,False),(0x51ecf0,'thug_skater_named_button',1,'byte',False,False,True),(0x51f6b0,'thug_skater_consume_recent_input',3,'byte',False,False,True),(0x506ba0,'thug_skater_save_surface',1,'void',False,False,True),(0x508140,'thug_skater_try_wall_transition',0,'byte',True,True,True),(0x50a2c0,'thug_skater_correct_side',2,'byte',True,True,True),(0x50c930,'thug_skater_correct_sides',0,'void',True,True,True)]
for row in NEW:bind(*row)
for at in [0x4024a0,0x40af20]:functions[hex(at)]['float_args']=[2]
functions['0x50a2c0']['float_args']=[0,1]
bind(0x460b80,'thug_ui_object_initialize',result='word')

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
fields={p for p in prior['pointer_fields'] if p<OLD_BASE+0x100000}|{WIDGET,WIDGET+0x28,WIDGET+0x40,NUMERIC,NUMERIC+0x28,NUMERIC+0x40}
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
 try:stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()})
 except Exception:
  print('Failed case:',len(labels),label,'EIP',hex(oracle.cpu.reg_read(UC_X86_REG_EIP)),'ESP',hex(oracle.cpu.reg_read(UC_X86_REG_ESP)),dict(oracle.coverage),flush=True);raise
 labels.append(label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=DIAG and at+len(data)//2>=DIAG+4:
    current=int.from_bytes(bytes.fromhex(data)[DIAG-at:DIAG-at+4],'little');s['callbacks']=current-previous;previous=current
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%25==0:print('Original side-contact cases:',len(labels),flush=True)
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
NATIVE_NAMES=['GoalManager_ActivateGoal','GoalManager_DeactivateGoal','GoalManager_ClearLastGoal','GoalManager_WinGoal','GoalManager_SetGoalFlag']
NATIVE_ADDR=[0x559230,0x559290,0x5592f0,0x559310,0x559670]
NATIVE_KEYS=[crc(s) for s in NATIVE_NAMES]
bindings=json.loads((ROOT/'local/analysis/script-bindings.json').read_text())
for name,at in zip(NATIVE_NAMES,NATIVE_ADDR):assert any(e['name']==name and int(e['address'],16)==at for e in bindings)
function_exports=[[at,'thug_script_goal_'+name] for at,name in zip(NATIVE_ADDR,['activate','deactivate','clear_last','win','set_flag'])]
PROGRAM=OLD_BASE+0x174000
# STATE is allocated above with the progress counters.
CONNECTION1,CONNECTION2=OLD_BASE+0x134000,OLD_BASE+0x136000
ALT_GAME,ALT_MANAGER=OLD_BASE+0x139000,OLD_BASE+0x13a000
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
 assert id_ in [5,6,7,8,0x888ef05e,0x7cf09270,0x5ed34deb,0xf2e85a34,0x96de9a0c] and len(body)<0x1000
 i=[NOTIFY,NUMERIC_NOTIFY,5,6,7,8,0x888ef05e,0x7cf09270,0x5ed34deb,0xf2e85a34,0x96de9a0c].index(id_);at=PROGRAM+(i-2)*0x1000
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

# Mirror only the lifted twelve-byte collision query context at outer entry/ret.
# The original collision routines and every gameplay callback run unchanged.
oracle.setword(0x684fe4,0x5df4ac)
def query_boundary(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if oracle.word(sp)!=oracle.stop:return
 if address in [0x508140,0x50a2c0,0x50c930]:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at in [0x508140,0x50a2c0,0x50c930,0x508189,0x5083bf,0x508772,0x50a301,0x50a765,0x50c9b8,0x50c9f9]:oracle.cpu.hook_add(UC_HOOK_CODE,query_boundary,begin=at,end=at)
exports += [[6577176,'thug_static_collision_methods'],[6577376,'thug_moving_collision_methods'],[0x67c6b8,'thug_collision_fallback_indices']]
fields.update([QUERY,*[loader['instances']+24*i for i in range(loader['count'])],*[RUNTIME+256*i for i in range(3)]])
for at in [0x5003a0,0x4172f0,0x5021d0,0x434bf0,0x434a60,0x4609f0,0x5039f0,0x43a930,0x5be970]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
for at,name in {0x5086e5:'wall_orientation',0x508743:'wall_change_state',0x50a4b2:'air_correction',0x50a623:'standing_correction',0x50c989:'outer_first_success',0x50c992:'outer_restore_first',0x50c9c2:'outer_third_probe',0x50c9d3:'outer_restore_third'}.items():
 branch_at[at]=name;oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)

def body_setup():return [call(0x460b80,BODIES),call(0x461930,BODIES,[0x200]),call(0x461a00,UM,[BODIES])]
def configuration(**kw):
 b=environment()
 values={'height':(0xb45b39e2,0),'distance':(0x406b425f,12),'extra':(0x1c58c8b4,0),'window':(0x5d241b00,.25),'cooldown':(0xf0c74ec2,0),'speed':(0xf0636a67,0),'slope':(0xae23e850,45),'angle':(0x6ac9f64d,90),'up':(0xbfcbb7e8,90),'turn':(0xe07ee1a9,.5),'skatable':(0x3eede4d3,30)}
 for name,(key,value) in values.items():b.symbol(key,2,bits(kw.get(name,value)))
 b.symbol(0x8cbc89dd,10,b.structure([]));b.symbol(0xd3d12913,10,b.structure([]))
 return b

def parent(at=0x508140,args=(),b=None,p=(),changes=None,label='side contact'):
 b=b or configuration()
 stages=dispatch(b,body_setup()+[call(at,PHYS,[*args,QUERY])],p,changes,label)
 return stages[-1]

# Writable checksum table, unmatched slot zero and raw button-state byte.
for key in BUTTONS+[0xdeadbeef]:
 for value in [0,1,255]:
  case([call(0x44e5a0,args=[key]),call(0x51ecf0,NAME_CONTEXT,[key])],[raw(NAME_CONTEXT+0xa00,bytes([value])*22)],label='button table lookup and raw byte')
case([call(0x44e5a0,args=[BUTTONS[12]])],changes={0x67d6dc:BUTTONS[12]},label='duplicate checksum selects first index')
# History ring wrap, unsigned ages, early stale entry, filters and repeated use.
for count,head in [(0,0),(1,0),(2,0),(100,99),(100,0)]:
 for position in [0,1,99]:
  for window in [0,1666,1667,0xffffffff]:
   entries=bytearray(2400);slot=(head-position)%100
   struct.pack_into('<6I',entries,slot*24,0,1,BUTTONS[12],0xdeadbeef,0xff,0)
   case([call(0x51f6b0,NAME_CONTEXT,[BUTTONS[12],window,0xffffffff])]*2,[raw(NAME_CONTEXT+0x38,entries),patch(NAME_CONTEXT+0x998,'<2H',count,head)],label='input ring bounds wrap expiry and repeated consumed entry')
for time in [0,1665,1666,1667,0xffffffff,0x80000000]:
 for kind,key,mask,requested in [(1,BUTTONS[12],0,0xffffffff),(1,BUTTONS[12],0x10,0),(1,BUTTONS[12],0x10,0x10),(0,BUTTONS[12],0,0),(1,0xdeadbeef,0,0)]:
  case([call(0x51f6b0,NAME_CONTEXT,[BUTTONS[12],10,requested])],[patch(NAME_CONTEXT+0x38,'<6I',time,kind,key,0,0,mask),patch(NAME_CONTEXT+0x998,'<2H',1,0)],label='history timestamp type name and bitmask')
# Vector operations snapshot all lanes before writes, including partial overlap.
patterns=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x3dcccccd,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for fn in [0x4024a0,0x40af20]:
 for i,value in enumerate(patterns):
  for offset in [0,4,16]:
   outvec=VECTORS+offset
   stages=case([call(fn,args=[outvec,VECTORS,patterns[(i*7+3)%len(patterns)]])],[patch(VECTORS,'<4I',value,patterns[(i+3)%len(patterns)],patterns[(i+7)%len(patterns)],patterns[(i+11)%len(patterns)])],label='vector arithmetic exceptional values and aliasing')
   stages[0]['float_fields']=list(range(outvec,outvec+16,4))
for source in [PHYS+0xa8,PHYS+0x158]:
 for material in [0,7,255]:
  case([call(0x506ba0,PHYS,[source])]*2,[patch(source+0x52,'<B',material)],label='saved probe copy or self assignment with raw sound material')
# Actual parent gates, all body/object events use its recovered base constructor.
for at in [0x508140,0x50a2c0,0x50c930]:
 for mode in [0,1,2]:
  parent(at,[bits(1),bits(12)] if at==0x50a2c0 else [],p=[patch(SKATER_STATE+0x18,'<I',mode),patch(PHYS+0x2ed,'<B',1)],label='parent mode gates and real empty-space queries')
# Direct transition fixture uses a saved contact in empty space; following query
# still executes the entire original training scene. The contact is test input.
for side in [-1,1]:
 parent(p=[patch(PHYS+0x120,'<4f',20000,20000,20000,1),patch(PHYS+0x130,'<4f',side,0,0,0),patch(SKATER_STATE+0x18,'<I',1),raw(PHYS+0xcc,bytes(0x4c))],label='full wall transition in clear space')

# Exercise the complete parents against selected, unmodified training geometry.
import math
contact_cases=[]
for i in [0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]:
 q=loader['queries'][i];segment=struct.unpack('<8f',bytes.fromhex(q['segment']));r=bytes.fromhex(q['result'])
 normal=struct.unpack_from('<4f',r);point=struct.unpack_from('<4f',r,16)
 delta=[segment[j+4]-segment[j] for j in range(3)];distance=math.sqrt(sum(v*v for v in delta));side=[v/distance for v in delta]+[0]
 velocity=[-normal[2]*100,0,normal[0]*100,0]
 p=[patch(BODIES+0x4c,'<4f',*segment[:4]),patch(BODIES+0x5c,'<4f',*[segment[j]-velocity[j]*.01 for j in range(4)]),patch(PHYS+0x98,'<4f',*segment[:4]),patch(BODIES+0x6c,'<4f',*side),patch(BODIES+0xac,'<4f',*velocity)]
 contact_cases.append((i,q,normal,point,distance,p))
 for mode in [0,1]:
  for sign in [-1,1]:
   parent(0x50a2c0,[bits(sign),bits(distance)],p=p+[patch(SKATER_STATE+0x18,'<I',mode)],label=f'training geometry {i} mode {mode} side {sign}')
 for sign in [-1,1]:
  parent(0x50c930,b=configuration(distance=distance),p=p+[patch(SKATER_STATE+0x18,'<I',0),patch(BODIES+0x6c,'<4f',*[v*sign for v in side])],label=f'both sides training {i} orientation {sign}')
# Saved contacts at real mesh points also test the preliminary rising probe.
for i,q,normal,point,distance,p in contact_cases:
 if abs(normal[1])>.3:continue
 for yspeed in [0,20,1000]:
  parent(p=p+[raw(PHYS+0xcc,bytes(0x50)),patch(PHYS+0x120,'<4f',*point),patch(PHYS+0x130,'<4f',*normal),patch(BODIES+0xb0,'<f',yspeed),patch(SKATER_STATE+0x18,'<I',1)],label=f'wall transition from training contact {i} rising {yspeed}')

clear_contact=[raw(PHYS+0xcc,bytes(0x50)),patch(PHYS+0x120,'<4f',20000,20000,20000,1),patch(PHYS+0x130,'<4f',1,0,0,0),patch(SKATER_STATE+0x18,'<I',1)]
for key,values in {'speed':[99,100,101,float('nan')],'slope':[-90,0,45,90],'angle':[0,.001,90,180],'up':[-90,0,90,180],'cooldown':[1.665,1.666,1.667,2,float('nan')],'window':[0,.001,.25,2]}.items():
 for value in values:
  parent(b=configuration(**{key:value}),p=clear_contact,label=f'wall transition {key} {value}')
for held,count,time,mask in [(0,0,1600,0),(0,1,1600,0),(0,1,1400,0),(0,1,1600,1),(255,0,0,0)]:
 parent(p=clear_contact+[patch(NAME_CONTEXT+0xa0c,'<B',held),patch(NAME_CONTEXT+0x998,'<2H',count,99),patch(NAME_CONTEXT+0x38+99*24,'<6I',time,1,BUTTONS[12],0,0xff,mask)],label='wall transition held versus buffered input')
for at,value in [(PHYS+0x2ed,1),(PHYS+0x22a,0),(GATE+0x26,1),(NAME_CONTEXT+0x13b0,1)]:
 parent(p=clear_contact+[patch(at,'<B',value)],label=f'wall transition gate {at:x}')
for field in [PHYS+0x39c,PHYS+0x3a0]:
 for timestamp in [1666,1667,0xffffffff,0x80000000]:
  parent(p=clear_contact+[patch(field,'<I',timestamp)],label='wall cooldown signed elapsed wrap')
# Intrusive saved-probe references are assigned by the original link routines.
for same in [False,True]:
 for prelinked in [False,True]:
  source=PHYS+0x158 if same else PHYS+0xa8
  calls=[call(0x41d1d0,source+0x98,[BODIES])]
  if prelinked and not same:calls.append(call(0x41d1d0,PHYS+0x1f0,[BODIES+0x400]))
  case(calls+[call(0x506ba0,PHYS,[source])]*2,label='save probe with real linked owner and self assignment')

# Complete state notification -> actual event goal -> flag update.
def goal_flag(b,i=0,previous=0,params=(),active=1,flags=0x81):
 return b.goal(i,params,b.structure([(0x700+i,1,previous)]),flags,active)
def event_goal(b,i=0,event=0xe0,active=1,extra=()):
 params=b.structure([(0x3c95ccd7,13,event),(0x2e0b1465,13,0x700+i)])
 return goal_flag(b,i,params=[(0,13,0xefc35592),(0x3cce31f0,12,b.array(10,[params]))]+list(extra),active=active)
def activity():return [patch(EVENT_COMPONENT+0xe0,'<B',1),patch(SCORE+0x14,'<I',1),patch(SCORE+0x60,'<f',1),patch(BODIES+0xbc,'<B',1)]
for target,value in [(0,0),(PHYS+0x1514,SOUND2),(PHYS+0x1528,SKATER_STATE2)]:
 b=configuration();event_goal(b,active=0 if target else 1,extra=[(0,13,0x4599b58c)] if target else [])
 dispatch(b,ui_setup()+body_setup()+[call(0x508140,PHYS,[QUERY])],clear_contact+activity()+player_patches(1,0,1,1)+([patch(DIAG+8,'<2I',target,value)] if target else []),label='wall transition through actual notification and goal activation')
 assert oracle.word(DIAG)==bool(target)

# Capture the real constructor output for fixtures needing an attached script.
# Registration and all script/event operations still execute original functions.
case([call(0x460b80,BODIES)],label='capture real generic event-owner construction')
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
for event in [0x51372712,0xa7662059]:
 for target,value in [(PHYS+0x1514,SOUND2),(PHYS+0x1528,SKATER_STATE2),(GATE+0x26,1)]:
  b=configuration();natives(b);goal_flag(b,1,params=[(0,13,0x4599b58c)],active=0)
  program(b,5,b'\x01'+command(0,0x101)+b'\x01\x24')
  script=bytearray(244)
  for offset,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,offset,v)
  p=[raw(BODIES,body_base),raw(SCRIPTS,script),patch(BODIES+0x10,'<I',SCRIPTS),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',event,5,0,0,0),patch(DIAG+8,'<2I',target,value)]
  calls=ui_setup()+[call(0x461930,BODIES,[0x200]),call(0x461a00,UM,[BODIES]),call(0x41d1d0,SCRIPTS+0xbc,[BODIES]),call(0x508140,PHYS,[QUERY])]
  dispatch(b,calls,clear_contact+player_patches(1,0,1,1)+p,label='wall or mode event invokes actual QB native activation and mutation')
  assert oracle.word(DIAG)==1,(len(labels),labels[-1],dict(oracle.coverage))

# Contact triggers resolve an actual node, spawn real QB and invoke the native
# goal activation. The diagnostic boundary checks late field rereads.
for target,value in [(GATE+0x26,1),(PHYS+0x1514,SOUND2),(SKATER_STATE+0x18,0)]:
 b=configuration();natives(b);goal_flag(b,1,params=[(0,13,0x4599b58c)],active=0)
 program(b,5,b'\x01'+command(0,0x101)+b'\x01\x24')
 checksum=0x12345678;node=b.structure([(0xa1dc81f9,13,checksum),(0x2ca8a299,13,5)]);nodes=b.array(10,[node])
 p=[patch(NODE_TABLE+(checksum&0x3fff)*4,'<Hh',0,0),patch(NODE_TABLE+0x1000c,'<I',nodes),patch(PHYS+0x100,'<I',checksum),patch(PHYS+0x115,'<B',0x40),patch(DIAG+8,'<2I',target,value)]
 stages=dispatch(b,ui_setup()+body_setup()+[call(0x508140,PHYS,[QUERY])],clear_contact+player_patches(1,0,1,1)+p,label='real contact-trigger QB mutates gate sound or state')
 assert oracle.word(DIAG)==1
 assert stages[-1]['result']==(target!=GATE+0x26)

# Acquire an existing moving contact through its real constructor, then verify
# successful wall transition detaches/releases it after the clear surface probe.
bind(0x416e70,'thug_moving_contact_initialize',1,'word');CONTACT=0x1631000
oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=0x416e70,end=0x416e70)
for locked in [0,1]:
 b=configuration()
 dispatch(b,body_setup()+[call(0x416e70,CONTACT,[BODIES]),call(0x508140,PHYS,[QUERY])],clear_contact+[patch(GROUND_GATE+0x18,'<I',CONTACT),patch(SKATER_STATE+0x88,'<B',locked)],label='wall transition releases actual moving contact unless locked')
# Live moving collision instances use the same geometry and original owner links.
for i,q,normal,point,distance,p in contact_cases[:4]:
 links=[patch(COLL_NODES+j*16,'<4I',0,RUNTIME+j*0x100,0,COLL_NODES+(j+1)*16) for j in range(3)]+[patch(COLL_NODES+48,'<4I',0,0xffffffff,0,COLL_NODES+48)]
 for mode in [0,1]:
  parent(0x50a2c0,[bits(1),bits(distance)],p=p+links+[patch(SKATER_STATE+0x18,'<I',mode)],label='side contact queries real moving and static collision instances')

for label in ['wall_orientation','wall_change_state','air_correction','standing_correction']:assert branches[label]>0,label
for at,_,*rest in NEW:assert oracle.coverage[hex(at)]>0,hex(at)
scope='Nine original routines: vector scale/division, writable button-name lookup and history consumption, saved surface probe and complete side-contact/wall-transition parents. Original collision, script, goal and state callees run without gameplay stubs. A recovered generic base object constructor supplies valid event ownership; skater construction is not yet recovered. Only heap, Windows TLS, diagnostic output and lifted collision-query context are adapted. All defined arena/global words compare exactly; arithmetic NaNs are classified only at typed output lanes. Required valid components, history count <=100 and head <100, terminating script graphs and positive finite frame rate are contracts. Training level is not playable yet.'
fixture={'base':BASE,'memory':'side-contact-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'side-contact-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_side_contact_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'score-display-diagnostics.wasm']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
