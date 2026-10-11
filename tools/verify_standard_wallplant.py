"""Compare complete 507500 standard wallplants through the original engine callees."""
import hashlib,json,struct,subprocess,math
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT,SHA256
out=ROOT/'local/validation/collision';report_path=out.parent/'standard-wallplant.json'
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
for at in [0x507500,0x508134]:oracle.cpu.hook_add(UC_HOOK_CODE,roots,begin=at,end=at)
def query_boundary(cpu,at,size,user):
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))!=oracle.stop:return
 if at==0x5003a0:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)))
 else:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)))
for at in [0x5003a0,0x5003f0,0x500446,0x500468,0x50049e]:oracle.cpu.hook_add(UC_HOOK_CODE,query_boundary,begin=at,end=at)
branch_names={0x5075b5:'cooldown_ready',0x507612:'height_gate',0x50766f:'input_array',0x5076bf:'remember_late',0x5077ea:'restore_late',0x5079a3:'forced_probe',0x507ab4:'surface_ready',0x507ac3:'speed_check',0x507b98:'angle_check',0x507c09:'rising_probe',0x507d35:'wall_mark',0x507d82:'reflect',0x507e1f:'speed_loss',0x507e6e:'zero_speed_fallback',0x507e9c:'forced_velocity',0x507f1c:'moving_contact',0x507f49:'outward_probe',0x507fa5:'outward_hit',0x507fc9:'outward_miss',0x507fdb:'orient',0x508055:'event',0x5080fa:'change_state',0x50811a:'success',0x507d29:'rejected'}
branches.clear()
for at in branch_names:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
labels=[]
def attempt(label,args=(0,0,0),p=(),changes=None,before=(),repeats=1):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 steps=oracle.case(list(before)+[(0x5003a0,PHYS,[0x10,0,QUERY])]+[(0x507500,PHYS,[*args,QUERY,PRINT])]*repeats,p,changes);labels.append(label)
 previous_callbacks=0
 for step in steps:
  callbacks=previous_callbacks
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):fields.add(at)
   if at==OBS:callbacks=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=callbacks-previous_callbacks;previous_callbacks=callbacks
 print('Standard wallplant',len(labels),label,step['result'],flush=True)
 return step
for args in [(0,0,0),(0,1,0),(0,0,1),(0,1,1),(1,0,0),(1,1,0),(1,0,1)]:attempt('argument modes '+str(args),args)
for at,value in [(PHYS+0x2ed,1),(PHYS+0x2db,1),(GATE+0x24,1),(NAME+0xa0b,0)]:attempt('early gate '+hex(at),p=[patch(at,'<B',value)])
for speed in [-1000,-100,-.01,0,.01,100]:attempt('speed '+str(speed),p=[patch(BODY+0xb4,'<f',speed)])
for vy in [0,100]:
 for button in [0,1]:attempt('rising probe '+str((vy,button)),p=[patch(BODY+0xb0,'<f',vy),patch(INPUT+0x1a0,'<B',button)])
# All gameplay callees remain the original instructions.
for key in [0x82135dd7,0x545840c4,0xd5349cc6]:
 for value in [-1,0,999,1000,1e10,float('nan')]:attempt('threshold '+hex(key)+' '+str(value),p=[patch(numeric[key],'<f',value)])
for late,check,forced in [(0,255,0),(0,256,0),(0,257,0),(255,0,0),(256,0,0),(0,0,255),(0,0,256),(0,0,257)]:attempt('byte args '+str((late,check,forced)),(late,check,forced))
for value in [-1,0,1]:
 p=[patch(PHYS+0x2ed,'<B',1),patch(BODY+0x20,'<I',PARAMS+32),patch(PARAMS+32,'<2I',0,PARAMS+48),patch(PARAMS+48,'<4I',2,0x5310e7b5,value&0xffffffff,0)]
 attempt('special mode parameter '+str(value),p=p)
attempt('zero-horizontal fallback',p=[patch(BODY+0xac,'<4f',0,100,0,1),patch(numeric[0x8f79cc1c],'<f',0)])
for mode in [0,1]:
 for speed in [.000001,.0001,.001,20,10000]:attempt('forced tiny speed '+str((mode,speed)),(0,0,mode),p=[patch(BODY+0xb4,'<f',-speed)])
for distance in [-5,-.000001,0,.1,5]:attempt('outward distance '+str(distance),p=[patch(numeric[0x024be8f0],'<f',distance)])
for vy in [1,100,1000]:attempt('rising clearance '+str(vy),p=[patch(BODY+0xb0,'<f',vy),patch(INPUT+0x1a0,'<B',1)])
for target,value,width in [(0,0,0),(GATE+0x26,1,1),(PHYS+12,BODY2,4),(PHYS+0x1528,STATE2,4),(BODY+0xb0,bits(-25),4)]:
 attempt('collision handler '+hex(target),p=[patch(CONTACT_FACES,'<H',0x40),patch(NODE+40,'<I',HANDLER),patch(OBS+4,'<3I',target,value,width)])
for target,value,width in [(0,0,0),(PHYS+12,BODY2,4),(PHYS+0x1528,STATE2,4),(PHYS+0x1518,NAME2,4),(STATE+0xc0,1,1),(STATE+0xb0,1,1)]:
 attempt('self event handler '+hex(target),p=[patch(BODY+0x10,'<I',SCRIPT),patch(ENTRIES,'<I',0xcf74f6b7),patch(OBS+4,'<3I',target,value,width)])
for body_velocity in [(20,0,-100),(-50,100,-50),(1,10,-1),(0,-100,-100)]:attempt('velocity vector '+str(body_velocity),p=[patch(BODY+0xac,'<4f',*body_velocity,1)])
MOVING,MOVING_OWNER,MOVING_REF,MOVING_POSITION,MOVING_MATRIX,MOVING_NODES=[BASE+x for x in [0xd1000,0xd1200,0xd1300,0xd1400,0xd1500,0xd0600]]
for key in ['0x413000','0x412f90','0x412070','0x40ae40']:functions[key]=prior['functions'][key]
setup=[(0x413000,MOVING,[COLLISION]),(0x412f90,MOVING,[MOVING_POSITION]),(0x412070,MOVING,[MOVING_MATRIX]),(0x40ae40,MOVING,[MOVING_OWNER])]
for old in [0,1,2]:
 for forced in [0,1]:
  p=[patch(MOVING_NODES,'<4I',0,MOVING,0,MOVING_NODES+16),patch(MOVING_NODES+16,'<4I',0,0xffffffff,0,MOVING_NODES+16),
    patch(MOVING_OWNER+0x4c,'<4f',0,0,2,1),patch(MOVING_OWNER+0x6c,'<16f',1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)]
  if old:
   contact=BASE+0xec000;owner=MOVING_OWNER if old==1 else 0
   p += [patch(GROUND+0x18,'<I',contact),patch(contact,'<3I',owner,0,0)]
   if owner:p.append(patch(owner+4,'<I',contact))
  attempt('moving owner/contact/forced '+str((old,forced)),(0,0,forced),p=p,before=setup)
rng=random.Random(0x507500)
for i in range(36):
 v=[rng.uniform(-100,100),rng.uniform(-20,100),rng.uniform(-1000,-10),[0,1,-1,2][i%4]]
 attempt('finite velocity/spill '+str(i),p=[patch(BODY+0xac,'<4f',*v),patch(numeric[0x09b2d4a3],'<f',rng.uniform(0,50)),patch(numeric[0x7cee396c],'<f',rng.uniform(10,40))])
# A second back-facing wall is invisible to the approach probe but hit by
# the outgoing probe, exercising its changed normal and point in the caller.
for gap in [0.01,1,4]:
 p=[patch(COLLISION+6,'<2H',6,2),patch(COLLISION+0x28,'<f',gap),patch(CONTACT_FACES+8,'<HH4B',0,7,3,5,4,255)]
 for j,point in enumerate([(-100,-100,gap),(100,-100,gap),(0,100,gap)]):p.append(patch(CONTACT_VERTICES+(j+3)*12,'<3f',*point))
 attempt('outward second wall '+str(gap),p=p)
# Timer arithmetic distinguishes an unsigned cooldown from signed time_since.
for frame,origin,offset,scale in [(0,1,0xffffffff,1),(0xffffffff,0x80000000,123,.25),(0x80000000,0xffffffff,999,2),(60,999,0xfffffffe,1)]:
 for forced in [0,1]:
  attempt('wrapped timers '+str((frame,origin,offset,scale,forced)),(0,0,forced),
   p=[patch(STATE+0xc0,'<B',1),patch(STATE+0xb0,'<B',1)],
   changes={index[0x7d1ec8]:frame,index[0x696d64]:origin,index[0x696d60]:offset,index[0x67d7c0]:bits(scale)})
for a0,c0,b0 in [(0,0,0),(1,0,0),(2,1,1),(255,255,2)]:
 attempt('state flags '+str((a0,c0,b0)),p=[patch(STATE+0xa0,'<B',a0),patch(STATE+0xc0,'<B',c0),patch(STATE+0xb0,'<B',b0)])
attempt('successful response then repeat',repeats=2)
for y in [-1,0,.09999999,.1,.10000001,1,float('nan')]:
 attempt('body up threshold '+str(y),p=[patch(BODY+0x80,'<f',y)])
for angle in [-90,-20,-0.,20,89.99999,90,90.00001,180,float('nan')]:
 for vx in [0,100]:attempt('approach angle '+str((angle,vx)),p=[patch(numeric[0x8f79cc1c],'<f',angle),patch(BODY+0xac,'<f',vx)])
for count in [0,1,511,512,513]:
 attempt('notification list '+str(count),p=[patch(NAME+0x13b0,'<B',1),patch(NAME+0x1bb4,'<I',count)])
attempt('callback redirects active notification',p=[patch(BODY+0x10,'<I',SCRIPT),patch(ENTRIES,'<I',0xcf74f6b7),patch(OBS+4,'<3I',PHYS+0x1518,NAME2,4),patch(NAME2+0x13b0,'<B',1)])
for at,value in [(EFFECT+0x20,bits(1)),(EFFECT+0x18,1)]:
 attempt('mark rejects without cancelling wallplant '+hex(at),p=[patch(at,'<I',value)])
for late,forced in [(1,0),(0,1),(1,1)]:
 attempt('constructed probe misses '+str((late,forced)),(late,0,forced),p=[patch(NODES+4,'<I',0xffffffff)])
for late in [0,1]:
 attempt('no matching trigger '+str(late),(late,0,0),p=[patch(NAME+0xa0b,'<B',0)])
 attempt('empty trigger array '+str(late),(late,0,0),p=[patch(TRICKS+4,'<I',0)])
# The original caller's saved flat normal must win over a newly found face.
for saved in [(0,0,1,0),(1,0,0,1),(0,0,-1,1)]:
 attempt('late saved normal '+str(saved),(1,0,0),p=[patch(PHYS+0x14f0,'<4f',*saved)])
for slope in [-.2,-.10050379,-.09,0,.09,.10050379,.2]:
 for flags in [0,8]:
  for late,check in [(0,0),(0,1),(1,0)]:
   points=[(-100,-100,-100*slope),(100,-100,-100*slope),(0,100,100*slope)]
   p=[patch(CONTACT_FACES,'<H',flags),patch(COLLISION+0x10,'<8f',-100,-100,min(v[2] for v in points),1,100,100,max(v[2] for v in points),1)]
   for j,point in enumerate(points):p.extend([patch(CONTACT_VERTICES+j*12,'<3f',*point),patch(VERTICES+j*16,'<3f',*point)])
   attempt('surface slope/flags/late/check '+str((slope,flags,late,check)),(late,check,0),p=p)

training=(out/'scene-training.bin').read_bytes();geometry=json.loads((out/'geometry-fixtures.json').read_text())
verts=(out/'vertices.bin').read_bytes();normals=(out/'normals.bin').read_bytes();by_offset={o['object']:o for o in geometry['objects']}
for sample in range(0,605,12):
 offset=struct.unpack_from('<I',training,0x100000+sample*24+12)[0]-0x1000000;obj=by_offset[offset]
 if not obj['faces']:continue
 face=(sample*13)%obj['faces'];small=training[offset+10];start=struct.unpack_from('<I',training,offset+12)[0]-0x1000000
 ids=struct.unpack_from('<3B' if small else '<3H',training,start+face*(8 if small else 10)+4)
 points=[struct.unpack_from('<3f',verts,obj['vertex_start']+i*16) for i in ids];normal=struct.unpack_from('<3f',normals,obj['normal_start']+face*16)
 if not all(math.isfinite(v) for v in normal) or math.hypot(normal[0],normal[2])<.1:continue
 center=[sum(p[k] for p in points)/3 for k in range(3)]
 position=[center[k]+normal[k]*10 for k in range(3)];end=[center[k]-normal[k]*100 for k in range(3)]
 p=[patch(SCENE+0xd0,'<2I',BASE+0xb0000,BASE+0x80000),patch(BASE+0xb7000+sample*32+20,'<I',BASE+0x1200),
    patch(BODY+0x4c,'<4f',*position,1),patch(BODY+0xac,'<4f',-normal[0]*100,0,-normal[2]*100,0),patch(PHYS+0x208,'<8f',*position,1,*end,1)]
 p.extend(patch(VERTICES+j*16,'<3f',*point) for j,point in enumerate(points))
 for armed in [0,1]:attempt('training surface/armed '+str((sample,armed)),p=p+[patch(EFFECT+0x1c,'<B',armed)])
fixture={**{k:v for k,v in prior.items() if k not in ['cases','case_labels','branch_counts','zeroed_packet_padding_entries']},'memory':'standard-wallplant-memory.bin','globals':globals_,'functions':functions,'pointer_exports':exports,'pointer_fields':sorted(fields),'float_fields':[],
 'pointer_symbols':prior['pointer_symbols']+[[0x64bd58,'thug_late_wallplant_text','late wallplant\n']],
 'native_callbacks':prior['native_callbacks']+[{'module':'wallplant-callbacks.wasm','export':'fixture_wallplant_native','original':NATIVE}],
 'callback_counter':'native_qb_observer_callbacks','cases':oracle.cases,'case_labels':labels,'branch_counts':dict(branches),'zeroed_packet_padding_entries':padding_entries,
 'scope':'Complete standard wallplant 507500 through original input matching, collision queries, mark projection/network, moving contacts, object/collision QB events, notifications and state changes. Late/check-only/forced modes, signed and wrapped timers, zero horizontal speed, outgoing obstacles, training geometry and mutable native QB observers are covered. All new arena/global/result bytes are exact. Initialized successful heap, valid components, configured native QB observer and terminal diagnostics/GPU/CRT are explicit boundaries; only previously documented emitter padding is seeded.'}
(out/fixture['memory']).write_bytes(memory);path=out/'standard-wallplant-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_standard_wallplant_wasm.mjs'),str(out)],check=True)
assert all(branches[name]>0 for name in branch_names.values()),dict(branches)
assert sum(qb_calls.values())>0 and sum(s['callbacks'] for c in oracle.cases for s in c['steps'])==sum(qb_calls.values())
artifacts=[path,out/fixture['memory'],*[out/s['module'] for s in fixture['native_callbacks']],out/fixture['memory_fixture']]
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'branch_counts':dict(branches),'callee_coverage':dict(oracle.coverage),'qb_calls':dict(qb_calls),'heap_events':dict(oracle.heap_events),'scope':fixture['scope'],
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS standard wallplant',flush=True)
