"""Compare complete airborne frames with original x86 and real game callees."""
import hashlib,json,struct,subprocess,math
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT,SHA256
out=ROOT/'local/validation/collision';report_path=out.parent/'airborne-update.json'
report_path.unlink(missing_ok=True)
prior=json.loads((out/'wall-contact-fixtures.json').read_text())
BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
CONTEXT,MANAGER,DEVICE,GPU,QUERY,PRINT=[BASE+x for x in [0x20,0x100,0x400,0x800,0xd0500,0xd0700]]
EFFECT,BODY,COMPONENT,DIRECTION,OWNER=[BASE+x for x in [0xd0000,0xd0100,0xd0300,0xd0400,0xc0100]]
SCENE,NODES,INSTANCE,COLLISION,VERTICES,CONTACT_VERTICES,CONTACT_FACES=[BASE+x for x in [0x2600,0x2400,0x2a00,0x2b00,0x1700,0xd0800,0xd0900]]
SYMBOLS,PHYS,STATE,NAME,GATE,EVENT_COMPONENT,PARAMS,META,EM,TABLES=[BASE+x for x in [0x15000,0xe0000,0xe2000,0xe3000,0xe5000,0xe5100,0xe5200,0xe5400,0xf0000,0xfc000]]
TLS=0x7d2100;GET=0x3f00100

def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
def zero(at,n):memory[at-BASE:at-BASE+n]=bytes(n)
for at,n in [(PHYS,0x153c),(STATE,0x200),(NAME,0x2000),(GATE,0x100),(EVENT_COMPONENT,0x100),(PARAMS,0x100),(META,0x1000),(EM,0xb220),(TABLES,0x1000),(BODY,0x200)]:zero(at,n)
put(PHYS+12,'<I',BODY);put(PHYS+0x1510,'<I',EVENT_COMPONENT);put(PHYS+0x1518,'<I',NAME)
put(PHYS+0x1528,'<I',STATE);put(PHYS+0x1530,'<I',GATE);put(PHYS+0x1538,'<I',EFFECT)
world=json.loads((out/'skater-fixtures.json').read_text())
probe=bytes.fromhex(next(c['output'] for c in world['constructors'] if c['kind']=='default'))
memory[PHYS+0xa8-BASE:PHYS+0xa8-BASE+len(probe)]=probe
put(PHYS+0x14c,'<I',0);put(STATE+12,'<I',BODY);put(STATE+0x30,'<B',1);put(STATE+0xd8,'<B',1)
put(STATE+0x11c,'<f',100);put(NAME+0xa0b,'<B',1)
put(BODY,'<I',0x6477e8);put(BODY+0x14,'<I',0x101)
put(BODY+0x4c,'<4f',0,0,10,1)
put(BODY+0x6c,'<16f',1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1)
put(BODY+0xac,'<4f',0,10,5,0)
put(EFFECT+12,'<I',BODY)
put(EVENT_COMPONENT+12,'<I',BODY)
# Real event dispatcher and concrete generic object receiver, initially scriptless.
for i in range(4):put(TABLES+i*256,'<6I',2,TABLES+i*256+32,0,0,0,0)
put(EM+8,'<3I',TABLES,TABLES+256,TABLES+512);put(EM+0xb028,'<I',TABLES+768)
put(TABLES+8,'<I',2);put(TABLES+32+12,'<3I',0x101,BODY,0)
SCRIPT,EVENTS,ENTRIES,CACHE,CTABLE,CENTRY,PROGRAM,OBS,BODY2,STATE2,NAME2=[BASE+x for x in [0xe6000,0xe6100,0xe6120,0xe6200,0xe6240,0xe62c0,0xe6300,0xe6400,0xe7000,0xe7200,0xe8000]]
NATIVE=0x3f00800;HANDLER=0xabcdef12
zero(SCRIPT,0x1000);zero(BODY2,0x200);zero(STATE2,0x200);zero(NAME2,0x2000)
memory[BODY2-BASE:BODY2-BASE+0x200]=memory[BODY-BASE:BODY-BASE+0x200]
put(BODY2+0x14,'<I',0x102);put(BODY2+0xb0,'<f',555)
put(TABLES+32+24,'<3I',0x102,BODY2,0)
put(STATE2+0xc0,'<B',1);put(STATE2+0xb0,'<B',1)
put(SCRIPT+0x2c,'<I',SCRIPT+0x1c);put(SCRIPT+0x94,'<I',SCRIPT+0x34);put(SCRIPT+0xe0,'<I',EVENTS)
put(EVENTS,'<4I',ENTRIES,1,1,0);put(ENTRIES,'<5I',0x3722e9bf,HANDLER,0,0,0)
put(CACHE+20,'<I',CTABLE);put(CTABLE,'<6I',2,CTABLE+32,1,0,0,0)
put(CTABLE+32+(HANDLER&3)*12,'<3I',HANDLER,CENTRY,0);put(CENTRY,'<5I',HANDLER,PROGRAM,1,0,0)
program=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24'
memory[PROGRAM-BASE:PROGRAM-BASE+len(program)]=program

NODE_TABLE,NODE_ARRAY,NODE,GOALS,GAME,OWNED,OWNED_BUCKETS,NOTIFY_OBJECT=[BASE+x for x in [0x190000,0x1a0100,0x1a0200,0x1a2000,0x1a1000,0x1a3000,0x1a3100,0x1a3200]]
memory[NODE_TABLE-BASE:NODE_TABLE-BASE+0x10000]=b'\xff'*0x10000
zero(NODE_TABLE+0x10000,0x4000)
put(NODE_TABLE+0x101*4,'<2H',0,0);put(NODE_TABLE+0x1000c,'<I',NODE_ARRAY)
put(NODE_ARRAY,'<3I',0xa00,1,NODE);put(NODE,'<2I',0,NODE+16)
put(NODE+16,'<4I',26,0xa1dc81f9,0x101,NODE+32);put(NODE+32,'<4I',26,0x2ca8a299,0,0)
put(GAME+0x38c,'<I',GOALS)
put(OWNED+0x20,'<6I',2,OWNED_BUCKETS,1,0,0,0);put(OWNED_BUCKETS+12,'<3I',0x101,NOTIFY_OBJECT,0)
put(NOTIFY_OBJECT+0x14,'<I',0x1234)
# Wide wall: both the qualifying probe and the mark at Y+30 hit it.
points=[(-100,-100,0),(100,-100,0),(0,100,0)]
for j,point in enumerate(points):put(CONTACT_VERTICES+j*12,'<3f',*point);put(VERTICES+j*16,'<3f',*point)
put(COLLISION+0x10,'<8f',-100,-100,0,1,100,100,0,1)
numeric={}
for i,(name,kind,value) in enumerate([(0x8cbc89dd,10,PARAMS),(0xe4d79235,2,bits(4)),(0xdc2c15ad,1,100),(0x273c9920,1,0xfffffc18),(0x751dbcb4,1,80),(0x5d241b00,2,bits(.2)),(0x3eede4d3,2,bits(30))]):
 at=META+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',kind<<8,name,0,value,old);put(bucket,'<I',at);numeric[name]=at+12

globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,width=4,offset=0):
 if at in index:defaults[index[at]]=value;return index[at]
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value);return index[at]
for name,at,value in [('thug_object_lookup_manager',0x6f0fc0,EM),('thug_timer_origin',0x696d64,0),('thug_timer_offset',0x696d60,0),('thug_time_scale',0x67d7c0,bits(1))]:glob(name,at,value)
BUTTONS=[0,0xbc6b118f,0xe3006fc4,0x85981897,0x4b358aeb,0xb7231a95,0xa50950c5,0xd8847efa,0x786b8b68,0x2b489a86,0x321c9756,0x7323e97c,0x20689278,0x26b0c991,0xbfb9982b,0xc8bea8bd,0xf2f1f64e,0x6bf8a7f4,0x1cff9762,0x767a45d7,0xbd30325b,0x9d2d8850]
for j,v in enumerate(BUTTONS):glob('thug_input_button_names',0x67d6d8+j*4,v,offset=j*4)
for name,at,value in [('thug_node_table',0x6f0d84,NODE_TABLE),('thug_script_list',0x6f3538,0),('thug_script_count',0x6f353c,0),('thug_script_next_serial',0x6f3540,1),('thug_script_pool_index',0x6f3548,0),('thug_script_pools',0x6f3550,0),('thug_objective_objects',0x7ce500,OWNED),('thug_game_context',0x7ce478,GAME)]:glob(name,at,value)
glob('thug_script_pools',0x6f3554,0,offset=4)
# Explicit runtime globals for the terminating native-observer QB handler.
for name,at,value,width in [('thug_script_cache',0x6f3558,CACHE,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_current_script',0x6f3530,0,4),('thug_script_debug_enabled',0x7cefac,0,1)]:glob(name,at,value,width)
# The oracle disables these pools at construction; compare the same configuration.
script_prior=json.loads((out/'script-execute-fixtures.json').read_text())
for entry in script_prior['globals']:
 name,at,width,*offset=entry
 if ('pool' in name or name.startswith('thug_script_expression') or name.startswith('thug_script_temporary')) and at not in index:glob(name,at,0,width,offset[0] if offset else 0)
functions={}
exports=prior['pointer_exports']+[[0x6477e8,'thug_ui_object_methods'],[0x64bb8c,'thug_vert_wallplant_events']]
fields=set(prior['pointer_fields'])|{BODY,BODY2,PROGRAM+2}
observed=[0x507500,0x4fded0,0x51fda0,0x51ecf0,0x51f6b0,0x580400,0x5003a0,0x51ddf0,0x51dbc0,0x4928a0,0x434bf0,0x434a60,0x4609f0,0x462f00,0x461140,0x522370,0x44ece0,0x4172f0,0x475750,0x475e80,0x4750b0,0x460470,0x473800,0x474b40,0x461480,0x475420,0x588a20,0x559150]
oracle=ScriptHeapOracle(memory,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=observed,instruction_limit=20000000,scope_entries={MANAGER+0x200:1,MANAGER+0x400:4})
for at,fn in [(0x684ff4,0x5e17ed),(0x685000,0x5e16ea),(0x684fe4,0x5df4ac)]:oracle.setword(at,fn)
qb_calls=Counter()
def native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);script=oracle.word(sp+8);count=oracle.word(OBS);assert count<16
 body,state,name=[oracle.word(PHYS+offset) for offset in [12,0x1528,0x1518]]
 values=[oracle.word(script+0xc8),body,state,name,oracle.word(body+0xb0),oracle.word(PHYS+0x4e8),oracle.word(state+0xc0),oracle.word(state+0xb0)]
 cpu.mem_write(OBS+64+count*32,struct.pack('<8I',*values));oracle.setword(OBS,count+1);qb_calls[hex(values[0])]+=1
 target,value,width=[oracle.word(OBS+i) for i in [4,8,12]]
 if target:assert width in [1,4];cpu.mem_write(target,value.to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,native,begin=NATIVE,end=NATIVE)
padding_entries=0
branches=Counter()
branch_names={}
def boundary(cpu,at,size,user):
 global padding_entries
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at in branch_names:branches[branch_names[at]]+=1;return
 if at==0x51dbc0:cpu.mem_write(sp-0x26,bytes(2));padding_entries+=1;return
 cleanup=0;result=0
 if at==0x629be5:result=TLS
 elif at==0x62411b:oracle.record(2,oracle.word(sp+4),1,0)
 elif at==0x401c30:
  fmt=oracle.word(sp+4);assert fmt in [0x64c3c8,0x64c3e8,0x64bd58],hex(fmt);oracle.record(4,fmt,0,0)
 else:
  device,stream,out_ptr,offset,stride=struct.unpack('<5I',cpu.mem_read(sp+4,20));assert device==DEVICE and stream==0
  for p in [out_ptr,offset,stride]:oracle.setword(p,0)
  oracle.setword(GPU,oracle.word(GPU)+1);cleanup=20
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x51dbc0,0x629be5,0x62411b,0x401c30,GET]:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
import random
INPUT,GROUND,SOUND,TRIGGER_GATE,TRIGGER_SCALE,TRICKS,TRIGGER= [BASE+x for x in [0xeb000,0xeb300,0xeb400,0xea000,0xea500,0xe5800,0xe5820]]
for at,n in [(INPUT,0x200),(GROUND,0x100),(SOUND,0x40),(TRIGGER_GATE,0x500),(TRIGGER_SCALE,0x300),(TRICKS,0x100)]:zero(at,n)
put(PHYS+0x150c,'<I',INPUT);put(PHYS+0x1514,'<I',SOUND);put(PHYS+0x152c,'<I',GROUND)
put(STATE2+12,'<I',BODY);put(NAME2+0x28,'<I',BODY);
put(NAME+0x20,'<I',TRIGGER_GATE);put(NAME+0x28,'<I',BODY);put(BODY+0x1b0,'<I',0x101)
# PressTwo-style held chord requires no historical input or scale lookup.
put(TRICKS,'<3I',0xa00,1,TRIGGER);put(TRIGGER,'<2I',0,TRIGGER+16)
for i,(kind,key) in enumerate([(26,0xa8123ecf),(26,0x7323e97c),(26,0x7323e97c),(26,0x7323e97c)]):
 at=TRIGGER+16+i*16;put(at,'<4I',kind,0,key,at+16 if i<3 else 0)
put(PHYS+0x120,'<4f',0,0,0,1);put(PHYS+0x130,'<4f',0,0,1,0);put(PHYS+0x100,'<I',0x101);put(PHYS+0xf8,'<H',8)
put(PHYS+0x208,'<8f',0,0,14,1,0,0,-190,1)
put(BODY+0x6c,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1);put(BODY+0xac,'<4f',0,0,-100,0)
put(BODY+0x5c,'<4f',0,0,20,1)
put(PHYS+0x14d0,'<8f',0,0,-100,0,0,0,10,1);put(PHYS+0x14f0,'<4f',0,0,1,0)
nums=[(0x82135dd7,2,bits(0)),(0x545840c4,2,bits(0)),(0xd5349cc6,2,bits(0)),(0x5d1f84a7,12,TRICKS),(0x3b389187,1,10),(0xd4205c9b,2,bits(4)),(0x20102726,2,bits(24)),(0x8f79cc1c,2,bits(20)),(0x7cee396c,2,bits(20)),(0x09b2d4a3,2,bits(10)),(0x5f768d84,2,bits(50)),(0x074957fa,2,bits(100)),(0x024be8f0,2,bits(5))]
for i,(name,kind,value) in enumerate(nums):
 at=META+0x200+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',kind<<8,name,0,value,old);put(bucket,'<I',at);numeric[name]=at+12
# The input trigger table above is beyond these numeric records.
assert META+0x200+len(nums)*32<TRICKS
functions.clear()
functions['0x5003a0']={'name':'thug_skater_query_surface','this':True,'result':'byte','cleanup':8,'memory':False,'stack_args':[0,1]}
functions['0x507500']={'name':'thug_skater_try_wallplant','this':True,'result':'byte','cleanup':12,'memory':True,'stack_args':[0,1,2]}
exports += [[0x64bd58,'thug_late_wallplant_text'],[0x64bbec,'thug_wallplant_events']]
oracle.initial=bytes(memory)
def roots(cpu,at,size,user):
 if at==0x507500:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))

def query_boundary(cpu,at,size,user):
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))!=oracle.stop:return
 if at==0x5003a0:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at in [0x5003a0,0x5003f0,0x500446,0x500468,0x50049e]:oracle.cpu.hook_add(UC_HOOK_CODE,query_boundary,begin=at,end=at)
branch_names={0x5075b5:'cooldown_ready',0x507612:'height_gate',0x50766f:'input_array',0x5076bf:'remember_late',0x5077ea:'restore_late',0x5079a3:'forced_probe',0x507ab4:'surface_ready',0x507ac3:'speed_check',0x507b98:'angle_check',0x507c09:'rising_probe',0x507d35:'wall_mark',0x507d82:'reflect',0x507e1f:'speed_loss',0x507e6e:'zero_speed_fallback',0x507e9c:'forced_velocity',0x507f1c:'moving_contact',0x507f49:'outward_probe',0x507fa5:'outward_hit',0x507fc9:'outward_miss',0x507fdb:'orient',0x508055:'event',0x5080fa:'change_state',0x50811a:'success',0x507d29:'rejected'}
branches.clear()
for at in branch_names:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
PREVIOUS=BASE+0xee000
put(PREVIOUS,'<4f',0,0,20,1)
put(PHYS+0x8c,'<f',1/60)
put(SOUND+12,'<I',BODY)
for i,(name,value) in enumerate([(0x786b3272,16),(0x23410c14,1)]):
 at=BASE+0xed000+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0x200,name,0,bits(value),old);put(bucket,'<I',at);numeric[name]=at+12
# Stat/settings graph; active sound configuration is merged below.
put(BODY+0x280,'<I',PHYS);put(BODY2+0x280,'<I',PHYS)
put(GOALS+0x398,'<I',PARAMS)
SETTINGS,STAT,PAIR,PAIR_ENTRY,SOUND_BUCKETS=[BASE+x for x in [0xee100,0xee200,0xee220,0xee240,0xee300]]
zero(SETTINGS,0x300);put(STAT,'<2I',0,PAIR_ENTRY);put(PAIR,'<2f',100,100);put(PAIR_ENTRY,'<4I',10,0,PAIR,0)
name=0xcc5f87aa;at=BASE+0xed080;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
put(at,'<5I',0xa00,name,0,STAT,old);put(bucket,'<I',at)
glob('thug_game_settings',0x7ce470,SETTINGS)
sound_prior=json.loads((out/'sound-selection-fixtures.json').read_text())
for name,at,width,offset in sound_prior['globals']:
 if name=='thug_sound_events':glob(name,at,[2,SOUND_BUCKETS,0,0,0,0][offset//4],width,offset)
 elif name in ['thug_sound_device','thug_sound_mode']:glob(name,at,0,width,offset)
name=0xd478c96d;at=BASE+0xed0a0;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
put(at,'<5I',0x700,name,0,PROGRAM,old);put(bucket,'<I',at)
put(CTABLE+32+(name&3)*12,'<3I',name,BASE+0xee500,0);put(BASE+0xee500,'<5I',name,PROGRAM,1,0,0)
for i,(name,value) in enumerate([(0xf0c74ec2,0),(0xf0636a67,0),(0xae23e850,20),(0x6ac9f64d,80),(0xbfcbb7e8,45)]):
 at=BASE+0xed0c0+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0x200,name,0,bits(value),old);put(bucket,'<I',at);numeric[name]=at+12
functions['0x508780']={'name':'thug_skater_resolve_air_wall','this':True,'result':'byte','cleanup':4,'memory':True,'stack_args':[0]}
exports += [[0x64bbbc,'thug_air_wall_events'],[0x6478e4,'thug_reference_target_methods']]
oracle.initial=bytes(memory)
def air_root(cpu,at,size,user):
 if at==0x508780:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))

for at in [0x508780,0x4ffdb0,0x4f8200,0x43a930,0x508140,0x518dd0,0x580790,0x475790]:
 if at not in observed:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observed.append(at)
air_branches={0x50893e:'surface_hit',0x5089b7:'contact_response',0x508a6c:'raised_accepted',0x508ac1:'restore_probe',0x508b07:'step_probe',0x508b70:'step_lower',0x508bc1:'step_accepted',0x508bfa:'grounded_response',0x508c9a:'preserve_length',0x508cd0:'air_response',0x508cf3:'standard_wallplant',0x508d02:'wall_transition',0x508d0f:'ordinary_response',0x508d6b:'impact',0x508db7:'mode_script',0x508dce:'velocity',0x508de7:'save_vertical',0x508f6f:'moving_owner',0x508fc7:'moving_push'}
branch_names.update(air_branches)
for at in air_branches:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
def transition_return(cpu,at,size,user):
 branches['wall_transition_accepted' if cpu.reg_read(UC_X86_REG_EAX)&255 else 'wall_transition_rejected']+=1
oracle.cpu.hook_add(UC_HOOK_CODE,transition_return,begin=0x508d07,end=0x508d07)
# Isolated, initialized audio arena; real engine callees with OS-only callbacks.
audio=json.loads((out/'sound-events-fixtures.json').read_text())
AUDIO=0x1b00000;AUDIO_OLD=audio['base'];old_size=len(memory);new_size=AUDIO+0x80000-BASE
memory.extend(bytes(new_size-old_size));oracle.cpu.mem_map(BASE+old_size,new_size-old_size);SIZE=len(memory)
def audio_rebase(v):return v+AUDIO-AUDIO_OLD if AUDIO_OLD<=v<AUDIO_OLD+0x80000 else v
def audio_bytes(data):
 data=bytearray(data)
 for i in range(0,len(data)-3,4):
  v=struct.unpack_from('<I',data,i)[0]
  if audio_rebase(v)!=v:struct.pack_into('<I',data,i,audio_rebase(v))
 return data
am=audio_bytes((out/audio['memory']).read_bytes())
for at,raw in audio['cases'][0]['patches']:
 at=audio_rebase(at)-AUDIO;data=audio_bytes(bytes.fromhex(raw));am[at:at+len(data)]=data
memory[AUDIO-BASE:AUDIO-BASE+len(am)]=am
# Only this controlled synthetic arena is word-relocated; actual game assets are not.
# Merge real symbol chains into the existing skater's bucket graph.
for i in range(4096):
 head=struct.unpack_from('<I',am,0x1000+i*4)[0]
 if not head:continue
 at=head
 while struct.unpack_from('<I',memory,at-BASE+16)[0]:at=struct.unpack_from('<I',memory,at-BASE+16)[0]
 old=struct.unpack_from('<I',memory,SYMBOLS-BASE+i*4)[0];put(at+16,'<I',old);put(SYMBOLS+i*4,'<I',head)
pointer_globals=set(prior.get('pointer_globals',[]))
for j,(entry,value) in enumerate(zip(audio['globals'],audio['cases'][0]['globals'])):
 name,at,width,*offset=entry
 if name=='thug_script_symbol_buckets':continue
 if name=='thug_math_errno':at=TLS+8
 k=glob(name,at,audio_rebase(value),width,offset[0] if offset else 0)
 if j in audio['pointer_globals']:pointer_globals.add(k)
glob('thug_audio_master_volume',0x67db08,bits(100));glob('thug_audio_spatial_enabled',0x6f8a4c,0,1)
exports+=audio['pointer_exports'];fields.update(audio_rebase(x) for x in audio['pointer_fields'])
AUDIO_CONTEXT=AUDIO+0x8000;AUDIO_LOG=AUDIO_CONTEXT+128;AUDIO_CALLBACK=0x3f02000
cpu=oracle.cpu;cpu.mem_map(AUDIO_CALLBACK,4096)
names=['orientation','commit','min','max','position','volume','pan','frequency','stop','release','release_spatial','create','query','lock','unlock','seek','play']
argc=[8,1,3,3,5,2,2,2,1,1,1,4,3,8,5,2,4]
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x900,oracle.stop+0x910,oracle.stop+0x920
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
last_error=0x12345678;os_calls=Counter();callback_counts=Counter();audio_padding_entries=0

def audio_seed_padding(uc,address,size,user):
 global audio_padding_entries
 uc.mem_write(uc.reg_read(UC_X86_REG_ESP)-0x95,b'\0');audio_padding_entries+=1
cpu.hook_add(UC_HOOK_CODE,audio_seed_padding,begin=0x444bb0,end=0x444bb0)
def os_service(uc,address,size,user):
 global last_error
 sp=uc.reg_read(UC_X86_REG_ESP)
 if address==GET_ERROR:uc.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
 elif address==GET_TLS:
  assert oracle.word(sp+4)==7;uc.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
 else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for address in [GET_ERROR,GET_TLS,SET_ERROR]:cpu.hook_add(UC_HOOK_CODE,os_service,begin=address,end=address)
def audio_callback(uc,address,size,user):
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
for i in range(len(names)):cpu.hook_add(UC_HOOK_CODE,audio_callback,begin=AUDIO_CALLBACK+i*16,end=AUDIO_CALLBACK+i*16)
for at in [0x444bb0,0x444480,0x444830,0x4445b0,0x457eb0,0x47be10,0x47bd20,0x47d130,0x47cd70]:
 if at not in observed:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observed.append(at)
put(PAIR,'<I2f',0,100,100);put(SOUND+0x24,'<f',1)
# Mirror the same component owner and actual sound bindings; keep caller skater pointers.
oracle.initial=bytes(memory)

EXTRA=BASE+0x210000;FLAGS=EXTRA+0x1000;LOCK=EXTRA+0x2000
glob('thug_frame_counter',0x7d1ec8,100) # Match the 1666 ms timestamps used below.
put(CONTEXT+20,'<I',BASE+len(memory)) # Match oracle snapshot range after extending arena.
put(PHYS+0x151c,'<I',LOCK);put(GAME+0x20,'<I',FLAGS)
put(STATE+0x18,'<I',1);put(STATE+0x30,'<B',0);put(STATE+0xc0,'<B',1);put(STATE+0xb0,'<B',1)
put(PHYS+0x370,'<B',0);put(BODY+0x5c,'<4f',0,0,10,1)
memory[PHYS+0x158-BASE:PHYS+0x158-BASE+len(probe)]=probe
# Independent valid parameters for the actual airborne callees.
for i,(name,kind,value) in enumerate([
 (0xfaa40754,2,bits(-100)),(0xc31ca696,2,bits(1)),(0x441c38a0,2,bits(1)),(0x9c8c6df1,1,0),
 (0xbe33a41e,2,bits(0)),(0x406b425f,2,bits(4)),(0xb45b39e2,2,bits(4)),(0x1c58c8b4,2,bits(2)),
 (0x542cf0c7,2,bits(20)),(0x2757ed2c,1,0),(0x26495947,1,100),(0x6bb5b751,1,100),
 (0x78384871,2,bits(1)),(0x59484878,2,bits(10)),(0x5f70ef46,2,bits(100)),(0x12cd2d14,2,bits(300)),
 (0xa092b2be,2,bits(100)),(0x5d756349,2,bits(300)),(0xabd57877,2,bits(90))]):
 at=EXTRA+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',kind<<8,name,0,value,old);put(bucket,'<I',at);numeric[name]=at+12
for name,at,width,*offset in json.loads((out/'motion-fixtures.json').read_text())['globals']:
 if name=='thug_last_gameplay_flag':glob(name,at,0,width,offset[0] if offset else 0)
# Register ordinary landing and fallback event IDs against the same valid clip settings.
event_buckets=defaults[index[0x6968ec]]
impact_record=struct.unpack_from('<I',memory,event_buckets-BASE+16)[0]
event_parameter=struct.unpack_from('<I',memory,impact_record-BASE+8)[0]
for event,name in [(0,0x11111111),(6,0x1d296aec)]:
 at=EXTRA+0x3000+event*16;put(at,'<3I',event,name,event_parameter);put(event_buckets+(event&3)*12,'<3I',event,at,0)
defaults[index[0x6968f0]]=3
identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
put(PHYS+0x18,'<16f',*identity)
for at in [PHYS+0x58,PHYS+0x68,PHYS+0x78]:put(at,'<4f',0,1,0,0)
glob('thug_skater_orientation_context',0x7ce5d8,EXTRA+0x2400)
functions['0x50ca00']={'name':'thug_skater_update_airborne','this':True,'result':'void','cleanup':0,'memory':True,'stack_args':[]}
exports += [[0x64bb98,'thug_air_landing_events']]
put(PHYS+0x3f0,'<37fB',*(identity+identity+[0,1,0,0,0]),1)
put(PHYS+0x488,'<2f',0,1);put(PHYS+0x4a0,'<16f',*identity)
SCORE_COMPONENT,SCORE_EMPTY=EXTRA+0x6000,EXTRA+0x6100
put(PHYS+0x1520,'<I',SCORE_COMPONENT);put(SCORE_COMPONENT+0x18,'<I',SCORE_EMPTY)
for i,name in enumerate([0x4957db43,0xf7a2acc1,0xcbfdd841,0xe7116a96]):
 at=EXTRA+0x7000+i*128;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0xa00,name,0,at+32,old);put(bucket,'<I',at)
 put(at+32,'<2I',0,at+48);put(at+48,'<4I',10,0,at+64,0);put(at+64,'<I2f',0,2,2)
for i,(name,value) in enumerate([(0xa5a02449,100),(0xabdd3395,500),(0x61224f2e,10),(0x9db33213,3),(0x50c5cc2f,10)]):
 at=EXTRA+0x7300+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0x200,name,0,bits(value),old);put(bucket,'<I',at)
from unicorn.x86_const import UC_X86_REG_ECX
TRANSFER_MODE,TRANSFER_MOTION,TRANSFER_SYMBOL=EXTRA+0x8000,EXTRA+0x8200,EXTRA+0xa000
put(GATE+0x2c,'<I',TRANSFER_MODE);put(PHYS+0x1534,'<I',TRANSFER_MOTION)
put(TRANSFER_MOTION+4,'<I',0x726e85aa);put(TRANSFER_MOTION+12,'<I',BODY);put(TRANSFER_MOTION+0x1868,'<f',.5)
# The ordinary mode defaults to zero and preserves existing cases.
for i,(name,value) in enumerate([(0x95a79c32,150),(0xe50a9d56,500),(0x32c20f7e,0)]):
 at=TRANSFER_SYMBOL+i*32;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0x200,name,0,bits(value),old);put(bucket,'<I',at);numeric[name]=at+12
# Add high/low transfer speed to the existing configuration structure.
struct_symbol=struct.unpack_from('<I',memory,SYMBOLS-BASE+(0x6775e538&0xfff)*4)[0]
while struct.unpack_from('<I',memory,struct_symbol-BASE+4)[0]!=0x6775e538:struct_symbol=struct.unpack_from('<I',memory,struct_symbol-BASE+16)[0]
config=struct.unpack_from('<I',memory,struct_symbol-BASE+12)[0]
old=struct.unpack_from('<I',memory,config-BASE+4)[0]
put(TRANSFER_SYMBOL+0x100,'<4I',4,0x7213ef07,bits(500),TRANSFER_SYMBOL+0x120)
put(TRANSFER_SYMBOL+0x120,'<4I',4,0xcc461b87,bits(100),old);put(config+4,'<I',TRANSFER_SYMBOL+0x100)
# Actual spawned transfer bytecode invokes the same native observer.
name=0xc7ed5fef;at=TRANSFER_SYMBOL+0x200;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
put(at,'<5I',0x700,name,0,PROGRAM,old);put(bucket,'<I',at)
slot=CTABLE+32+(name&3)*12;memory[at+80-BASE:at+92-BASE]=memory[slot-BASE:slot+12-BASE]
put(at+32,'<5I',name,PROGRAM,1,0,0);put(slot,'<3I',name,at+32,at+80)
for j in range(8):pointer_globals.add(glob('thug_collision_cache_registry',0x6918ec+j*4,0,offset=j*4))
glob('thug_collision_cache_mask',0x69190c,0);glob('thug_matrix_small_angle',0x67c648,0x3d0efa35)
for j in range(4):glob('thug_skater_transfer_velocity',0x7ccdbc+j*4,0xa5a5a5a5,offset=j*4)
for i,name in enumerate([0xa5179e9e,0x283bb5d6]):
 at=EXTRA+0xd000+i*128;bucket=SYMBOLS+(name&0xfff)*4;old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<5I',0x700,name,0,PROGRAM,old);put(bucket,'<I',at)
 slot=CTABLE+32+(name&3)*12;memory[at+80-BASE:at+92-BASE]=memory[slot-BASE:slot+12-BASE]
 put(at+32,'<5I',name,PROGRAM,1,0,0);put(slot,'<3I',name,at+32,at+80)
stack_objects=[]
def cache_end(cpu,address,size,user):
 ptr=cpu.reg_read(UC_X86_REG_ECX)
 slot=next(i for i in range(8) if oracle.word(0x6918ec+i*4)==ptr and oracle.word(0x69190c)&(1<<i))
 # A later transfer application can reuse this expired automatic storage.
 # Verify the retained identity and dead registry bit; prior cache tests cover
 # its defined fields at destruction, when their lifetime is still valid.
 stack_objects.append({'original':ptr,'global':['thug_collision_cache_registry',4*slot],'mask':['thug_collision_cache_mask',slot,0],'size':0xfcc,'blocks':[]})
oracle.cpu.hook_add(UC_HOOK_CODE,cache_end,begin=0x40ab40,end=0x40ab40)
transfer_branches={0x50da98:'frame_transfer_search',0x50dabf:'frame_transfer_apply',0x502e77:'transfer_success',0x5034e9:'transfer_script'}
branch_names.update(transfer_branches)
for at in transfer_branches:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)

"""Use the previously verified shipped AerialFlips bytecode in full frames."""
ROT,ROT_ARRAY,ROT_CODE,ROT_SYMBOL,INPUT2= [EXTRA+x for x in [0xb000,0xb600,0xb800,0xc000,0xc200]]
put(BODY+0x100,'<I',NAME);put(NAME+4,'<I',0x270f56e1);put(NAME+12,'<2I',BODY,ROT)
put(ROT+4,'<I',0x286a8d26);put(ROT+12,'<2I',BODY,TRANSFER_MOTION)
# The audio arena supplies network flags; rotation also needs a valid player list.
network=defaults[index[0x7cce14]];put(network+0x11c,'<4I',0,0xffffffff,0,network+0x11c)
rotation_prior=json.loads((out/'airborne-rotation-fixtures.json').read_text())
functions['0x471b00']=rotation_prior['functions']['0x471b00']
shipped_case=next(c for c,label in zip(rotation_prior['cases'],rotation_prior['case_labels']) if label.startswith('shipped AerialFlips'))
shipped_array=bytes.fromhex(dict(shipped_case['patches'])[0x1661c00])
memory[ROT_CODE-BASE:ROT_CODE-BASE+len(shipped_array)]=shipped_array
name=0xb75d73e5;bucket=SYMBOLS+(name&0xfff)*4
put(ROT_SYMBOL,'<5I',0xc00,name,0,ROT_ARRAY,struct.unpack_from('<I',memory,bucket-BASE)[0]);put(bucket,'<I',ROT_SYMBOL)
name=0xd8fa65d7;at=ROT_SYMBOL+0x40;bucket=SYMBOLS+(name&0xfff)*4
put(at,'<5I',0x700,name,0,PROGRAM,struct.unpack_from('<I',memory,bucket-BASE)[0]);put(bucket,'<I',at)
slot=CTABLE+32+(name&3)*12;memory[at+80-BASE:at+92-BASE]=memory[slot-BASE:slot+12-BASE]
put(at+32,'<5I',name,PROGRAM,1,0,0);put(slot,'<3I',name,at+32,at+80)
memory[INPUT2-BASE:INPUT2-BASE+0x200]=memory[INPUT-BASE:INPUT-BASE+0x200]
rotation_branches={0x4ffc91:'frame_rotation_match',0x4ffd02:'frame_rotation_x',0x4ffd33:'frame_rotation_half_turn',0x4ffd53:'frame_rotation_y',0x4ffd8d:'frame_rotation_z',0x4ffd9e:'frame_rotation_handler'}
branch_names.update(rotation_branches)
for at in rotation_branches:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
def rotation_history(key,held,head=50):
 patches=[patch(NAME+0x998,'<2H',3,head),patch(INPUT+0x160,'<B',held),patch(INPUT+0x180,'<B',1)]
 for i,k in enumerate([key,key,0x2b489a86 if held else 0x321c9756]):
  patches.append(patch(NAME+0x38+((head-i)%100)*24,'<4IB3sI',1666,1,k,0,0,b'xyz',0))
 return patches

oracle.initial=bytes(memory)
def frame_root(cpu,at,size,user):
 if at==0x50ca00:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at in [0x50ca00,0x50d948,0x50dacb]:oracle.cpu.hook_add(UC_HOOK_CODE,frame_root,begin=at,end=at)
DIRECT_TARGETS=[4203296, 4203328, 4203424, 4203456, 4203504, 4203680, 4210832, 4215152, 4219008, 4219120, 4219296, 4288256, 4325968, 4357232, 4373488, 4410352, 4517088, 4590064, 4634880, 4634912, 4689664, 4689760, 5227376, 5227520, 5227632, 5234384, 5236528, 5236832, 5237328, 5239920, 5240208, 5241616, 5241744, 5242288, 5243808, 5245376, 5251536, 5251648, 5254944, 5256976, 5259360, 5261584, 5261920, 5262144, 5262832, 5263072, 5270432, 5271840, 5272832, 5277568, 5294384, 5344496, 5386912, 5768192, 5769104]
for at in DIRECT_TARGETS:
 if at not in observed:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observed.append(at)
parent_instructions=Counter()
def trace_parent(cpu,at,size,user):parent_instructions[hex(at)]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace_parent,begin=0x50ca00,end=0x50dad5)
labels=[]
def frame(label,p=(),changes=None,repeats=1,before=(),floats=()):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stack_objects.clear()
 print('Start',len(labels),label,flush=True)
 stages=oracle.case(list(before)+[(0x50ca00,PHYS,[QUERY,PRINT])]*repeats,p,changes);labels.append(label)
 if stack_objects:
  assert repeats==1 and not before
  stages[-1]['stack_objects']=stack_objects[:]
 previous_callbacks=0;previous_audio=0
 for step in stages:
  step['float_fields']=list(floats)
  callbacks=previous_callbacks;device_calls=previous_audio
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in {entry[0] for entry in exports}:fields.add(at)
   if at==OBS:callbacks=int.from_bytes(bytes.fromhex(data),'little')
   if at==AUDIO_CONTEXT:device_calls=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=callbacks-previous_callbacks+device_calls-previous_audio;previous_callbacks=callbacks;previous_audio=device_calls
 print('Done',len(labels),label,flush=True)
 return stages
for dt in [0,1/60,1,-.1]:
 frame('no collision dt '+str(dt),[patch(NODES+4,'<I',0xffffffff),patch(PHYS+0x8c,'<f',dt)])
frame('wide wall')
for mode in [0,1,2,5]:
 for vy in [-100,0,100]:
  frame('wall mode/vertical '+str((mode,vy)),[patch(STATE+0x18,'<I',mode),patch(BODY+0xb0,'<f',vy),patch(PHYS+0x8c,'<f',.25)])
points=[(-100,0,-100),(0,0,100),(100,0,-100)]
floor=[patch(COLLISION+0x10,'<8f',-100,0,-100,1,100,0,100,1),patch(CONTACT_FACES,'<2H',1,7),patch(BODY+0x4c,'<4f',0,5,0,1),patch(BODY+0x5c,'<4f',0,5,0,1),patch(PHYS+0x8c,'<f',.1),patch(PHYS+0x68,'<4f',0,1,0,0),patch(BODY+0xac,'<4f',0,-100,0,0)]
for j,point in enumerate(points):floor.extend([patch(CONTACT_VERTICES+j*12,'<3f',*point),patch(VERTICES+j*16,'<3f',*point)])
for flags in [1,2,0,4,8]:
 for suppressed in [0,1]:frame('floor flags/suppressed '+str((flags,suppressed)),floor+[patch(CONTACT_FACES,'<H',flags),patch(GATE+0x26,'<B',suppressed)])


for target,value,width in [(0,0,0),(GATE+0x26,1,1),(PHYS+12,BODY2,4),(PHYS+0x1528,STATE2,4),(PHYS+0x1518,NAME2,4),(PHYS+0x150c,INPUT2,4),(BODY+0xb0,bits(77),4)]:
 frame('floor collision QB '+hex(target),floor+[patch(CONTACT_FACES,'<2H',0x41,7),patch(NODE+40,'<I',HANDLER),patch(OBS+4,'<3I',target,value,width)])
for kind in [5,7,11,13,16]:
 frame('landing audio mutation '+str(kind),floor+[patch(AUDIO_CONTEXT+40,'<4I',kind,BODY+0xb0,bits(77),4)])
for flag in [0x30,0x38,0x40,0x48,0x70,0x80,0xa8,0xb0]:
 for value in [0,1,255]:
  frame('no geometry state flag '+str((flag,value)),[patch(NODES+4,'<I',0xffffffff),patch(STATE+flag,'<B',value)])
for i in range(40):
 r=random.Random(0x50ca00+i)
 frame('finite displacement '+str(i),[patch(NODES+4,'<I',0xffffffff),patch(BODY+0xac,'<4f',*[r.uniform(-1000,1000) for _ in range(4)]),patch(BODY+0x4c,'<4f',*[r.uniform(-1000,1000) for _ in range(4)]),patch(PHYS+0x8c,'<f',r.uniform(-.1,.1))])

for ground in [0,1]:
 for moving in [0,1]:
  for vy in [-100,0,100]:
   frame('transfer velocity/ground '+str((ground,moving,vy)),[patch(STATE+0x30,'<B',ground),patch(STATE+0x78,'<B',1),patch(PHYS+0x14c0,'<B',moving),patch(STATE+0xe4,'<4f',10,20,30,1),patch(BODY+0xb0,'<f',vy)])
for latch in [0,1]:
 for height in [0,.5,10]:
  for flags in [0,8]:
   frame('vertical transition follow '+str((latch,height,flags)),[patch(STATE+0x30,'<B',1),patch(STATE+0x38,'<B',1),patch(STATE+0x48,'<B',latch),patch(PHYS+0x268,'<4f',0,0,0,1),patch(PHYS+0x278,'<4f',0,0,1,0),patch(PHYS+0x298,'<f',height),patch(CONTACT_FACES,'<H',flags)])
for late in [0,1,2,0x7fffffff,0x80000000,0xffffffff]:
 frame('late wallplant attempts '+str(late),[patch(PHYS+0x14cc,'<I',late)])
functions['0x416e70']={'name':'thug_moving_contact_initialize','this':True,'result':'word','cleanup':4,'memory':False,'stack_args':[0]}
MOVING_CONTACT,TRANSPORT_OWNER=EXTRA+0x4000,EXTRA+0x4200
for alive in [0,1]:
 for transfer in [0,1]:
  for moving in [0,1]:
   # A live contact starts with the owner's previous matrix/position;
   # update computes the displacement from its new position.
   patches=[patch(GROUND+0x18,'<I',MOVING_CONTACT),patch(MOVING_CONTACT,'<3I',TRANSPORT_OWNER if alive else 0,0,0),patch(MOVING_CONTACT+12,'<16f',*identity),patch(MOVING_CONTACT+0x4c,'<4f',0,0,0,1),patch(TRANSPORT_OWNER+0x4c,'<4f',10,20,30,1),patch(TRANSPORT_OWNER+0x6c,'<16f',*identity),patch(STATE+0x78,'<B',transfer),patch(PHYS+0x14c0,'<B',moving),patch(NODES+4,'<I',0xffffffff)]
   frame('moving transport alive/transfer/enabled '+str((alive,transfer,moving)),patches)

for button in [0x20,0x40,0x60,0x80,0xa0,0x100]:
 for age in [0,100,101,301,600]:
  frame('active pitch/spin button '+str((button,age)),[patch(STATE+0xc0,'<B',0),patch(INPUT+button,'<B3xI',1,(1666-age)&0xffffffff),patch(NODES+4,'<I',0xffffffff)])
for i in range(4):
 frame('tap turn edge '+str(i),[patch(PHYS+0x2da,'<B',1),patch(INPUT+0xb0,'<B',i&1),patch(INPUT+0x110,'<B',i>>1),patch(NODES+4,'<I',0xffffffff)])

for direction in [(1,0,0,0),(0,1,0,0),(1,1,1,1)]:
 frame('transfer landing projection '+str(direction),floor+[patch(STATE+0x78,'<B',1),patch(PHYS+0x490,'<4f',*direction)])
for age in [0,499,500,501,1000]:
 frame('raised landing contact age '+str(age),floor+[patch(BODY+0x4c,'<4f',0,-20,0,1),patch(BODY+0xac,'<4f',0,100,0,0),patch(GROUND+0x70,'<I',(1666-age)&0xffffffff)])
for coefficient in [0,1,10,100]:
 frame('friction entry '+str(coefficient),[patch(PHYS+0x320,'<f',1),patch(PHYS+0x314,'<f',coefficient),patch(NODES+4,'<I',0xffffffff)])
frame('transfer scan empty',[patch(INPUT+0xc0,'<B',1),patch(INPUT+0x120,'<B',1),patch(STATE+0xb0,'<B',0),patch(GATE+0x2c,'<I',LOCK),patch(BODY+0xac,'<4f',0,10,0,0),patch(NODES+4,'<I',0xffffffff)])

transfers=json.loads((out/'transfer-fixtures.json').read_text());seen=set()
for c,label in zip(transfers['cases'],transfers['case_labels']):
 if not label.startswith('training transfer ') or not c['steps'][-1]['result']:continue
 mesh=label.split()[2]
 if mesh in seen:continue
 seen.add(mesh);pp=dict(c['patches']);start=struct.unpack('<4f',bytes.fromhex(pp[0x1637000]));origin=struct.unpack('<4f',bytes.fromhex(pp[0x1637010]));v=struct.unpack('<4f',bytes.fromhex(pp[0x1637020]))
 patches=[patch(SCENE+0xd0,'<2I',BASE+0xb0000,BASE+0x80000),patch(BODY+0x4c,'<4f',*start),patch(BODY+0x5c,'<4f',*origin),patch(BODY+0xac,'<4f',*v),patch(INPUT+0xc0,'<B',1),patch(INPUT+0x120,'<B',1),patch(STATE+0xb0,'<B',0),patch(PHYS+0x8c,'<f',0),patch(numeric[0xfaa40754],'<f',-800),patch(BODY+0x100,'<I',TRANSFER_MOTION)]
 patches += [[TRANSFER_MOTION+0x48,pp[0x1635000+0x48]],[TRANSFER_MODE+0x1c,pp[0x1634100+0x1c]],[TRANSFER_MOTION+0x18,pp[0x1635000+0x18]]]
 frame('original training transfer '+label,patches)
assert branches['frame_transfer_apply']==branches['transfer_script']>=7

for key in [0xe3006fc4,0xbc6b118f,0x85981897,0x4b358aeb]:
 for held in [0,1]:
  for head in [0,50]:
   frame('full frame shipped rotation '+str((hex(key),held,head)),rotation_history(key,held,head)+[patch(NODES+4,'<I',0xffffffff)],repeats=2,before=[(0x471b00,0,[ROT_ARRAY,ROT_CODE,0])])
   if head==50:assert oracle.word(PHYS+0x2d8)&0xff000000
for target,value,width in [(PHYS+0x150c,INPUT2,4),(PHYS+0x1528,STATE2,4),(PHYS+0x1518,NAME2,4),(PHYS+12,BODY2,4),(PHYS+0x2db,0,1)]:
 frame('rotation QB changes live component '+hex(target),rotation_history(0xe3006fc4,1)+[patch(NODES+4,'<I',0xffffffff),patch(OBS+4,'<3I',target,value,width)],before=[(0x471b00,0,[ROT_ARRAY,ROT_CODE,0])])
assert branches['frame_rotation_x'] and branches['frame_rotation_z'] and branches['frame_rotation_handler']

# Synthetic Y turns supplement the four shipped X/Z definitions.
for angle in [180,-180,181]:
 st,first=EXTRA+0xc600,EXTRA+0xc620
 patches=[patch(ROT_ARRAY,'<3I',0xa00,1,st),patch(st,'<2I',0,first)]
 for i,(kind,key,value) in enumerate([(26,0x24715af5,0xe3006fc4),(26,0xbd780b4f,0xe3006fc4),(2,0x7df8e00b,angle&0xffffffff)]):
  patches.append(patch(first+i*16,'<4I',kind,key,value,first+(i+1)*16 if i<2 else 0))
 frame('full frame configured Y rotation '+str(angle),patches+rotation_history(0xe3006fc4,1)+[patch(NODES+4,'<I',0xffffffff)])
assert branches['frame_rotation_y'] and branches['frame_rotation_half_turn']
for held in [0,1]:
 patches=rotation_history(0xe3006fc4,1)+[patch(NODES+4,'<I',0xffffffff),patch(OBS+4,'<3I',PHYS+0x150c,INPUT2,4)]
 for offset in [0xc0,0x120]:patches += [patch(INPUT+offset,'<B',held),patch(INPUT2+offset,'<B',1-held)]
 frame('rotation callback replaces captured input '+str(held),patches,before=[(0x471b00,0,[ROT_ARRAY,ROT_CODE,0])])

for now in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 for age in [99,100,101]:
  frame('transition timer signed wrap '+str((now,age)),[patch(NODES+4,'<I',0xffffffff),patch(STATE+0x48,'<B3xI',1,(now-age)&0xffffffff)],{index[0x7d1ec8]:now,index[0x684fd0]:bits(1000)})
for mesh in [0,1,13,30,34,57,70,129,278,488,521,545]:
 data=bytes.fromhex(world['loader']['queries'][mesh]['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 for height in [2,20]:
  position=[point[k]+normal[k]*height for k in range(3)]+[1]
  velocity=[-100*normal[k] for k in range(3)]+[0]
  patches=[patch(SCENE+0xd0,'<2I',BASE+0xb0000,BASE+0x80000),patch(BODY+0x4c,'<4f',*position),patch(BODY+0x5c,'<4f',*position),patch(BODY+0xac,'<4f',*velocity),patch(PHYS+0x8c,'<f',.1)]
  frame('original training airborne frame '+str((mesh,height)),patches)
for rate in [1/60,.1]:
 frame('repeated airborne movement '+str(rate),[patch(NODES+4,'<I',0xffffffff),patch(PHYS+0x8c,'<f',rate)],repeats=5)
frame('transfer block flag changes and timestamps',[patch(NODES+4,'<I',0xffffffff),patch(STATE+0xa8,'<B',1),patch(STATE+0xb0,'<B',0)])
frame('descending transfer below target height',[patch(NODES+4,'<I',0xffffffff),patch(STATE+0x78,'<B',1),patch(BODY+0xb0,'<f',-100),patch(PHYS+0x37c,'<f',20),patch(STATE+0xe4,'<4f',10,20,30,0)])
for via in ['held','latch']:
 patches=[patch(STATE+0x30,'<B',1),patch(BODY+0xb0,'<f',100)]
 if via=='held':patches += [patch(INPUT+0xc0,'<B',1),patch(INPUT+0x120,'<B',1)]
 else:patches.append(patch(PHYS+0x2d0,'<B',1))
 frame('leave rising transition '+via,patches)
frame('standing landing while crouch held',floor+[patch(INPUT+0x40,'<B',1)])
frame('landing clears transition timestamp',floor+[patch(STATE+0x30,'<B',1)])
frame('transfer landing raises minimum speed',floor+[patch(STATE+0x78,'<B',1),patch(PHYS+0x490,'<4f',1,0,0,0),patch(numeric[0x59484878],'<f',1000)])
frame('transfer landing restores upward alignment',floor+[patch(STATE+0x78,'<B',1),patch(PHYS+0x490,'<4f',1,0,0,0),patch(AUDIO_CONTEXT+40,'<4I',7,BODY+0x90,bits(1),4)])
frame('nonskatable landing sets transfer gate',floor+[patch(CONTACT_FACES,'<H',2),patch(STATE+0xb0,'<B',0)])
for age in [249,250,251]:
 frame('forced transfer age '+str(age),[patch(NODES+4,'<I',0xffffffff),patch(STATE+0xb0,'<B',0),patch(INPUT+0xc0,'<B',1),patch(INPUT+0x120,'<B',1),patch(PHYS+0x380,'<I',1666-age),patch(PHYS+0x4ec,'<I',0)])
frame('late wallplant succeeds within full frame',[patch(STATE+0x30,'<B',1),patch(PHYS+0x14cc,'<I',2),patch(BODY+0x5c,'<4f',0,0,20,1)],before=[(0x5003a0,PHYS,[0x10,0,QUERY])])
for flags in [0,1]:
 ceiling=floor+[patch(BODY+0x4c,'<4f',0,-10,0,1),patch(BODY+0x5c,'<4f',0,-10,0,1),patch(BODY+0xac,'<4f',0,100,0,0),patch(PHYS+0x8c,'<f',0),patch(STATE+0xb0,'<B',0),patch(CONTACT_FACES,'<HH3B',flags,7,2,1,0)]
 frame('overhead ceiling transfer gate '+str(flags),ceiling)
follow=[patch(STATE+0x30,'<B',1),patch(STATE+0x38,'<B',1),patch(PHYS+0x268,'<4f',0,0,0,1),patch(PHYS+0x278,'<4f',0,0,1,0),patch(PHYS+0x8c,'<f',0),patch(CONTACT_FACES,'<H',8)]
short_wall=[patch(COLLISION+0x10,'<8f',-100,-100,0,1,100,-1,0,1)]
for j,point in enumerate([(-100,-100,0),(100,-100,0),(0,-1,0)]):
 short_wall += [patch(CONTACT_VERTICES+j*12,'<3f',*point),patch(VERTICES+j*16,'<3f',*point)]
frame('transition follow finds lower wall',follow+short_wall)
frame('transition follow preserves prior height',follow+[patch(PHYS+0x278,'<4f',0,1,1,0)])
frame('nonskatable landing without earlier wall response',floor+[patch(CONTACT_FACES,'<H',2),patch(STATE+0xb0,'<B',0),patch(numeric[0xd4205c9b],'<f',100)])
assert all(parent_instructions[hex(at)] for at in [0x50cb8f,0x50d27c,0x50d2e4,0x50d76d,0x50d828,0x50d891,0x50d8d5,0x50d9e1,0x50da13,0x50da7e])
assert all(oracle.coverage.get(hex(at)) for at in DIRECT_TARGETS)
numeric_fields=[BODY+o for o in range(0x4c,0xbc,4)]+[PHYS+o for o in list(range(0x18,0x90,4))+list(range(0x98,0xa8,4))+list(range(0xa8,0xc8,4))+list(range(0x11c,0x140,4))+list(range(0x208,0x228,4))]
for dt,velocity,gravity in [(1e-30,3e38,-100),(1e-20,1e30,-1e30),(1e10,1e-30,-1e-30),(1e20,1e-20,-1e-30),(3e38,1e-38,0),(1e10,1e30,-1e-30),(1e-30,1e-30,-1e-30),(1e-20,-3e38,1e30)]:
 frame('airborne finite exponent limits '+str((dt,velocity,gravity)),[patch(NODES+4,'<I',0xffffffff),patch(LOCK+0x28,'<B',1),patch(PHYS+0x8c,'<f',dt),patch(BODY+0xac,'<4f',velocity,velocity,-velocity,0),patch(numeric[0xfaa40754],'<f',gravity)],floats=numeric_fields)
for value in [float('nan'),float('inf'),-float('inf')]:
 frame('airborne nonfinite displacement '+str(value),[patch(NODES+4,'<I',0xffffffff),patch(LOCK+0x28,'<B',1),patch(BODY+0xac,'<4f',value,value,value,0)],floats=numeric_fields)

# The existing alternate-transfer fixture supplies real successful training poses.
alt=json.loads((out/'floor-fixtures.json').read_text());used=set()
for c,label in zip(alt['cases'],alt['case_labels']):
 if not label.startswith('raised alternate ') or not c['steps'][-1]['result']:continue
 activated=False
 for at,data in c['steps'][-1]['outputs']:
  if at<=0x1995078<at+len(data)//2:activated=bool(bytes.fromhex(data)[0x1995078-at])
 if not activated:continue
 mesh=label.split()[2]
 if mesh in used:continue
 used.add(mesh);pp=dict(c['patches'])
 p=[patch(SCENE+0xd0,'<2I',BASE+0xb0000,BASE+0x80000),patch(STATE+0x30,'<B',1),patch(PHYS+0x2d0,'<B',1),patch(PHYS+0x8c,'<f',0),patch(numeric[0xfaa40754],'<f',-800)]
 for old,data in c['patches']:
  if 0x18e504c<=old and old+len(data)//2<=0x18e50bc:p.append([old-0x18e5000+BODY,data])
  elif 0x1991018<=old and old+len(data)//2<=0x1991078:p.append([old-0x1991000+PHYS,data])
 p += [patch(GROUND+0x18,'<I',MOVING_CONTACT),patch(MOVING_CONTACT,'<3I',TRANSPORT_OWNER,0,0),patch(MOVING_CONTACT+12,'<16f',*identity),patch(MOVING_CONTACT+0x4c,'<4f',0,0,0,1),patch(TRANSPORT_OWNER+0x4c,'<4f',0,0,0,1),patch(TRANSPORT_OWNER+0x6c,'<16f',*identity),patch(OBS+4,'<3I',MOVING_CONTACT,0,4)]
 frame('alternate transfer kills moving owner '+mesh,p)
assert parent_instructions['0x50cfd8']
fixture={**{k:v for k,v in prior.items() if k not in ['cases','case_labels','branch_counts','zeroed_packet_padding_entries']},'memory':'airborne-update-memory.bin','globals':globals_,'functions':functions,'pointer_exports':exports,'pointer_fields':sorted(fields),'float_fields':[],
 'pointer_symbols':prior['pointer_symbols']+[[0x64bd58,'thug_late_wallplant_text','late wallplant\n']],
 'pointer_globals':sorted(pointer_globals),
 'native_callbacks':prior['native_callbacks']+[{'module':'wallplant-callbacks.wasm','export':'fixture_wallplant_native','original':NATIVE}]+[dict(spec,module='wall-audio-callbacks.wasm') for spec in audio['native_callbacks']],
 'callback_counter':'native_qb_and_audio_callbacks','cases':oracle.cases,'case_labels':labels,'scope':'Complete original airborne update0050ca00 with its input, pitch/spin/flip scheduling, gravity/transport, transition following, wallplants, floor/ceiling responses, landing sound/events, and both transfer applications. Full arenas, globals, heap and native QB/audio observations compare. Includes shipped AerialFlips parsed by the original parser, real training geometry, repeated frames, live component replacement, owner death in alternate-transfer QB, timer wrap, and numeric exponent/nonfinite cases. Only declared arithmetic NaNs classify; other bytes compare exactly. The three instructions following an impossible false return from416f00 with a nonnull owner remain unexecuted in the single-threaded oracle; their defensive release is retained. OS/GPU/CRT/heap and terminal native QB remain existing explicit boundaries. Required components/parameters, valid lists and successful allocation retain original contracts. Complete scoring/UI integration is covered separately by airborne-score. Movement dispatch, rendering, startup and playable training remain unfinished.'}
path=out/'airborne-update-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(memory)
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
instructions=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(load().get_data(0x10ca00,4310),0x50ca00))
uncovered=[i.address for i in instructions if not parent_instructions[hex(i.address)]]
assert uncovered==[0x50cc5f,0x50cc61,0x50cc66],list(map(hex,uncovered))
subprocess.run(['node',str(ROOT/'tools/verify_airborne_update_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'parent_instruction_counts':dict(parent_instructions),'instruction_coverage':{'covered':len(instructions)-len(uncovered),'total':len(instructions),'unexecuted':[hex(x) for x in uncovered],'reason':'416f00 returns false only for a null owner; the caller checks that owner immediately before the call, and the helper has no callbacks.'},'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'audio_callbacks':dict(callback_counts),'zeroed_emitter_padding_entries':padding_entries,'zeroed_audio_padding_entries':audio_padding_entries,'scope':fixture['scope'],'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()},'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'wallplant-callbacks.wasm',out/'wall-audio-callbacks.wasm']}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS airborne update',len(labels),dict(oracle.counts),report['instruction_coverage'])
