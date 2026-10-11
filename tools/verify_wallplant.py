"""Compare complete 503710 vertical wallplants through the recovered engine callees."""
import hashlib,json,struct,subprocess,math
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from script_heap_oracle import ScriptHeapOracle
from specimen import ROOT,SHA256
out=ROOT/'local/validation/collision';report_path=out.parent/'wallplant.json'
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
functions={'0x503710':{'name':'thug_skater_try_vert_wallplant','this':True,'result':'byte','cleanup':0,'memory':True,'stack_args':[]}}
exports=prior['pointer_exports']+[[0x6477e8,'thug_ui_object_methods'],[0x64bb8c,'thug_vert_wallplant_events']]
fields=set(prior['pointer_fields'])|{BODY,BODY2,PROGRAM+2}
observed=[0x503710,0x51ecf0,0x51f6b0,0x580400,0x5003a0,0x51ddf0,0x51dbc0,0x4928a0,0x434bf0,0x434a60,0x4609f0,0x462f00,0x461140,0x522370,0x44ece0,0x4172f0,0x475750,0x475e80,0x4750b0,0x460470,0x473800,0x474b40,0x461480,0x475420,0x588a20,0x559150]
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
branch_names={0x503738:'history_path',0x503769:'input_accepted',0x5037a5:'early_reject',0x5037ac:'probe_start',0x503836:'late_reject',0x50383f:'surface_hit',0x503889:'distance_accepted',0x5038b0:'velocity_accepted',0x5038cd:'state_accepted',0x5038d6:'normal_checked',0x5038ef:'contact_attempt',0x503908:'contact_accepted',0x503930:'apply_response',0x503946:'boost_velocity',0x503969:'emit_event',0x5039a0:'clear_c0',0x5039c7:'clear_b0',0x5039df:'success'}
def boundary(cpu,at,size,user):
 global padding_entries
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at in branch_names:branches[branch_names[at]]+=1;return
 if at==0x503710:cpu.mem_write(0x691968,bytes(cpu.mem_read(QUERY,12)));return
 if at in [0x5037ab,0x50383e,0x5039e7]:cpu.mem_write(QUERY,bytes(cpu.mem_read(0x691968,12)));return
 if at==0x51dbc0:cpu.mem_write(sp-0x26,bytes(2));padding_entries+=1;return
 cleanup=0;result=0
 if at==0x629be5:result=TLS
 elif at==0x62411b:oracle.record(2,oracle.word(sp+4),1,0)
 elif at==0x401c30:
  fmt=oracle.word(sp+4);assert fmt in [0x64c3c8,0x64c3e8],hex(fmt);oracle.record(4,fmt,0,0)
 else:
  device,stream,out_ptr,offset,stride=struct.unpack('<5I',cpu.mem_read(sp+4,20));assert device==DEVICE and stream==0
  for p in [out_ptr,offset,stride]:oracle.setword(p,0)
  oracle.setword(GPU,oracle.word(GPU)+1);cleanup=20
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [*branch_names,0x503710,0x5037ab,0x50383e,0x5039e7,0x51dbc0,0x629be5,0x62411b,0x401c30,GET]:oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=at,end=at)
labels=[]
def case(label,p=(),changes=None,repeats=1):
 cpu=oracle.cpu;cpu.reg_write(UC_X86_REG_FPSW,0);cpu.reg_write(UC_X86_REG_FPTAG,0xffff);cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 steps=oracle.case([(0x503710,PHYS,[QUERY,PRINT])]*repeats,p,changes);labels.append(label)
 previous_callbacks=0
 for step in steps:
  callbacks=previous_callbacks
  for at,data in step['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in dict(exports):fields.add(at)
   if at==OBS:callbacks=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=callbacks-previous_callbacks;previous_callbacks=callbacks
 print('Wallplant original',len(labels),label,[s['result'] for s in steps],flush=True)
 return steps
case('complete wallplant')
case('armed projection and event',p=[patch(EFFECT+0x1c,'<B',1)])
for field,value in [(PHYS+0x2ed,1),(NAME+0xa0b,0),(STATE+0x30,0),(STATE+0xd8,0),(PHYS+0x4e8,1)]:case('early gate '+hex(field),[patch(field,'<B',value)])
for spin in [-360,-0.,1,360,float('nan'),float('inf')]:case('spin '+str(spin),[patch(NAME+0x13a4,'<f',spin)])
case('surface miss',[patch(NODES+4,'<I',0xffffffff)])
for value in [-1,0,9,10,11,0x7fffffff]:case('distance limit '+str(value),[patch(numeric[0xdc2c15ad],'<i',value)])
for velocity in [-1001,-1000,-999,-1,-0.,0,1,1e20,float('inf'),float('-inf'),float('nan')]:case('velocity '+str(velocity),[patch(BODY+0xb0,'<f',velocity)])
for value in [-1,59.99999,60,60.00001,float('nan'),float('inf'),float('-inf')]:case('state threshold '+str(value),[patch(STATE+0x11c,'<f',value)])
for c0,b0 in [(0,0),(1,0),(0,1),(1,1),(255,2)]:case('state clears '+str((c0,b0)),[patch(STATE+0xc0,'<B',c0),patch(STATE+0xb0,'<B',b0)])
for gate in [1,255]:case('suppressed response '+str(gate),[patch(GATE+0x26,'<B',gate)])
for field,fmt,value in [(EFFECT+0x20,'<f',1),(EFFECT+0x18,'<i',1),(BODY+0x50,'<f',90)]:case('contact rejects '+hex(field),[patch(field,fmt,value)])
case('success then repeat',repeats=2)
# Strict recent-input age and consumption before a later gate fails.
for age in [0,199,200,201,1000]:
 for blocked in [False,True]:
  p=[patch(NAME+0xa0b,'<B',0),patch(NAME+0x998,'<2H',1,0),patch(NAME+0x38,'<6I',(999-age)&0xffffffff,1,0x7323e97c,0,0,0)]
  if blocked:p.append(patch(STATE+0x30,'<B',0))
  case('history age/gate '+str((age,blocked)),p)
for target,value,width in [(0,0,0),(PHYS+12,BODY2,4),(PHYS+0x1528,STATE2,4),(PHYS+0x1518,NAME2,4),(STATE+0xc0,1,1),(STATE+0xb0,1,1),(BODY+0xb0,bits(-25),4),(GATE+0x26,1,1)]:
 case('QB handler mutation '+hex(target),[patch(BODY+0x10,'<I',SCRIPT),patch(OBS+4,'<3I',target,value,width)])
for target,value,width in [(0,0,0),(GATE+0x26,1,1),(PHYS+12,BODY2,4),(PHYS+0x1528,STATE2,4),(PHYS+0x1518,NAME2,4),(BODY+0xb0,bits(-25),4)]:
 case('collision QB mutation '+hex(target),[patch(CONTACT_FACES,'<H',0x40),patch(NODE+40,'<I',HANDLER),patch(OBS+4,'<3I',target,value,width)])
for count in [0,1,511,512,513]:
 case('objective notification count '+str(count),[patch(NAME+0x13b0,'<B',1),patch(NAME+0x1bb4,'<I',count)])
case('QB redirects notification context',[patch(BODY+0x10,'<I',SCRIPT),patch(OBS+4,'<3I',PHYS+0x1518,NAME2,4),patch(NAME2+0x13b0,'<B',1)])
for value in [-0x80000000,-16777217,-1,0,1,16777217,0x7fffffff]:
 case('signed boost '+str(value),[patch(numeric[0x751dbcb4],'<i',value),patch(BODY+0xb0,'<f',1)])
for frame,origin,offset,scale in [(0,1,0xffffffff,1),(0xffffffff,0x80000000,123,.25),(0x80000000,0xffffffff,999,2),(60,999,0xfffffffe,1)]:
 case('wrapped timers '+str((frame,origin,offset,scale)),[patch(STATE+0xc0,'<B',1),patch(STATE+0xb0,'<B',1)],
  {index[0x7d1ec8]:frame,index[0x696d64]:origin,index[0x696d60]:offset,index[0x67d7c0]:bits(scale)})
for type_,key,mask,consumed in [(1,0x7323e97c,1,0),(2,0x7323e97c,0,0),(1,0x12345678,0,0),(1,0x7323e97c,0,1)]:
 case('history filters '+str((type_,key,mask,consumed)),[patch(NAME+0xa0b,'<B',0),patch(NAME+0x998,'<2H',1,99),patch(NAME+0x38+99*24,'<6I',999,type_,key,0,consumed,mask)])
# Normal threshold, face flag bypass, and non-vertical body orientation.
for slope in [-2,-.10050379,-.1,-.09,0,.09,.1,.10050379,2]:
 for flags in [0,8]:
  points=[(-100,-100,-100*slope),(100,-100,-100*slope),(0,100,100*slope)]
  normal=[0,-slope/math.sqrt(1+slope*slope),1/math.sqrt(1+slope*slope),0]
  p=[patch(CONTACT_FACES,'<H',flags),patch(BODY+0x7c,'<4f',*normal),patch(BODY+0x4c,'<4f',*[v*10 for v in normal[:3]],1),
     patch(COLLISION+0x10,'<8f',-100,-100,min(v[2] for v in points),1,100,100,max(v[2] for v in points),1)]
  for j,point in enumerate(points):p.extend([patch(CONTACT_VERTICES+j*12,'<3f',*point),patch(VERTICES+j*16,'<3f',*point)])
  case('normal slope/flags '+str((slope,flags)),p)
# Use the complete relocated training geometry, with genuine sampled face planes.
TRAIN_GRID,TRAIN_TABLE,TRAIN_RENDER,CONTAINER=BASE+0x80000,BASE+0xb0000,BASE+0xb7000,BASE+0x1200
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
 p=[patch(SCENE+0xd0,'<2I',TRAIN_TABLE,TRAIN_GRID),patch(TRAIN_RENDER+sample*32+20,'<I',CONTAINER),
    patch(BODY+0x7c,'<4f',*normal,0),patch(BODY+0x4c,'<4f',*[center[k]+normal[k]*5 for k in range(3)],1)]
 p.extend(patch(VERTICES+j*16,'<3f',*point) for j,point in enumerate(points))
 for armed in [0,1]:case('training object/armed '+str((sample,armed)),p+[patch(EFFECT+0x1c,'<B',armed)])
fixture={**{k:v for k,v in prior.items() if k not in ['cases','case_labels','branch_counts','zeroed_packet_padding_entries']},'memory':'wallplant-memory.bin','globals':globals_,'functions':functions,'pointer_exports':exports,'pointer_fields':sorted(fields),'float_fields':[],
 'native_callbacks':prior['native_callbacks']+[{'module':'wallplant-callbacks.wasm','export':'fixture_wallplant_native','original':NATIVE}],
 'callback_counter':'native_qb_observer_callbacks','cases':oracle.cases,'case_labels':labels,'branch_counts':dict(branches),'zeroed_packet_padding_entries':padding_entries,
 'scope':'Complete vertical-wallplant caller 503710 through original input, surface query, wall contact, mark projection/network, concrete object-event dispatch, notification gate and state timers. Sloped walls, full training geometry, signed boost limits, timer wrap and actual QB handler execution with callback mutations are covered. Configured valid state, initialized successful heap, a configured native QB observer, and terminal diagnostics/GPU/CRT boundaries. Only the emitter packet padding is initialized as in wall-contact fixtures.'}
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export=fixture_wallplant_native',str(ROOT/'tools/wallplant_callbacks.c'),'-o',str(out/'wallplant-callbacks.wasm')],check=True)
(out/fixture['memory']).write_bytes(memory);path=out/'wallplant-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
subprocess.run(['node',str(ROOT/'tools/verify_wallplant_wasm.mjs'),str(out)],check=True)
assert all(branches[name]>0 for name in branch_names.values()),dict(branches)
assert sum(qb_calls.values())==15 and sum(s['callbacks'] for c in oracle.cases for s in c['steps'])==15
artifacts=[path,out/fixture['memory'],*[out/s['module'] for s in fixture['native_callbacks']],out/fixture['memory_fixture']]
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'branch_counts':dict(branches),'callee_coverage':dict(oracle.coverage),'qb_calls':dict(qb_calls),'heap_events':dict(oracle.heap_events),'scope':fixture['scope'],
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS wallplant',flush=True)
