"""Compare the complete grounded frame with its original game callees."""
from pathlib import Path
source=Path(__file__).with_name('verify_floor.py').read_text()
exec(compile(source.split('\nidentity=')[0].replace("'floor.json'","'grounded-update.json'"),'<floor prerequisites>','exec'))
identity=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
exec(compile(source[source.index('# All four parents'):source.index('for at,args in [(0x4fee10')],'<floor graph and helpers>','exec'))
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
NEW=[(0x50ee70,'thug_skater_update_grounded',0,'void',True,True,True)]
for row in NEW:bind(*row);oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0])
ROOTS.add(0x50ee70)
for at in [0x50ee70,0x50f82c]:oracle.cpu.hook_add(UC_HOOK_CODE,floor_observe,begin=at,end=at)
bind(0x402320,'thug_vector_copy',1,'word')
grounded_returns=[]
def grounded_return(cpu,at,size,user):
 if oracle.word(cpu.reg_read(UC_X86_REG_ESP))==oracle.stop:
  grounded_returns.append((list(retained_caches.values()),oracle.word(GOBS),oracle.word(oracle.word(PHYS+0x1528)+0x18)))
oracle.cpu.hook_add(UC_HOOK_CODE,grounded_return,begin=0x50f82c,end=0x50f82c)
oracle.setword(0x684fe4,0x5df4ac)
GCONTEXT,GMODOWNER,GMODIFIER=0x1640000,0x1640200,0x1640240
copy(GCONTEXT,bytes(0x1000));put(PHYS+0x1524,'<I',GCONTEXT)
put(BODIES+0x278,'<I',GMODOWNER);put(GMODOWNER+0x18,'<I',GMODIFIER);put(BODIES+0x280,'<I',PHYS)
put(BODIES+0x290,'<10f',*range(1,11));put(BODIES+0x2b8,'<2I',0,0);put(NAME_CONTEXT+0x1331,'<9s',b'ordinary\0')
# body_setup registers this skater as 0x200; meter lookup requires that same ID.
put(SCORE+8,'<h',0x200)
# Concrete animation and balance instances occupy otherwise unused world space.
GTIMED,GACOMP,GASTATE,GCHANNEL,GCONTROLLER,GOBS,GPROGRAMS=0x1641000,0x1650000,0x1650100,0x1650200,0x1650300,0x1655000,0x1657000
copy(GTIMED,bytes(0xb00));copy(GACOMP,bytes(0x9000))
put(PHYS+16,'<I',GTIMED);put(GTIMED+4,'<I',0x4ff8dac6);put(GTIMED+12,'<2I',BODIES,GACOMP)
put(GACOMP+4,'<I',0x7149b753);put(GACOMP+12,'<2I',BODIES,GCONTEXT);put(GACOMP+0x34,'<I',GASTATE)
put(GCONTEXT+4,'<I',0x12345678);put(GCONTEXT+12,'<2I',BODIES,0)
put(GASTATE+0x20,'<I',GCHANNEL);put(GASTATE+0x68,'<I',BODIES)
put(GCHANNEL,'<I',0x648794);put(GCHANNEL+0x14,'<3f',0,0,1);put(GCHANNEL+0x38,'<2I',2,GCONTROLLER);put(GCHANNEL+0x54,'<I',1);put(GCHANNEL+0x64,'<I',BODIES)
put(GCONTROLLER,'<2I',0x649f80,GCHANNEL)
fields.update([GCHANNEL,GCONTROLLER]);exports += [[0x648794,'thug_animation_channel_methods'],[0x649f80,'thug_balance_animation_methods']]
for at in [GCONTEXT+0x24,GCONTEXT+0x12c]:
 put(at,'<5I',0,BODIES,GCONTEXT,SCORE_COMPONENTS,INPUT);put(at+0x24,'<6f',0,0,0,100,2,1)
 put(at+0x3c,'<B',1);put(at+0x40,'<5I',0,0xbc6b118f,0xe3006fc4,3,0);put(at+0x54,'<4B',1,0,1,0)
put(INPUT+0x38,'<I',0xbc6b118f);put(INPUT+0x58,'<I',0xe3006fc4)
for i in range(70):put(GTIMED+0x1c+i*36+0x10,'<I',1)
put(GTIMED+0x9f4,'<B',1);put(GTIMED+0xa90,'<I',1);put(GAME+0x3d0,'<f',0)
glob('thug_frame_length_scale',0x684fc8,bits(1));glob('thug_animation_last_balance',0x67dc10,255,1)
def script_identity(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,script_identity,begin=0x4738e0,end=0x4738e0)
# Reuse actual sprite visibility QB and concrete sprite methods.
display_source=Path(__file__).with_name('verify_balance_display.py').read_text()
exec(compile(display_source[display_source.index('METER,CHILD,STYLE,'):display_source.index('initial=bytes(memory);oracle.initial=initial')],'<balance sprite graph>','exec'))
exports += [[0x649a80,'thug_sprite_style_base_methods'],[0x64a744,'thug_sprite_style_methods'],[0x64ad28,'thug_sprite_drawable_methods'],[0x64a228,'thug_ui_sprite_methods']]
# Terminating QB programs retain actual event and interpreter execution.
EVENT_NAMES=[0x8ffefb28,0x3b1001b6,0xd3fde02a,0xa7662059,0xd77b6ff9,0x47d44b84,0x55e516c8,0x41b03551,0x3a8d6ab2,0xa496aebd]
for j,name in enumerate(EVENT_NAMES):
 at=GPROGRAMS+j*128;code=at+64;bucket=SYMBOLS+(name&0xfff)*4
 old=struct.unpack_from('<I',memory,bucket-BASE)[0];put(at,'<BBHIIII',0,7,0,name,0,code,old);put(bucket,'<I',at);put(at+32,'<5I',name,code,1,0,0)
 copy(code,b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24');fields.add(code+2)
 slot=CACHETABLE+32+(name&3)*12;old=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',old,4)[0]
 if occupied:copy(at+80,old)
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',14)
qb_calls=Counter()
def native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8);n=oracle.word(GOBS);assert n<64
 name=oracle.word(script+0xc8);body=oracle.word(PHYS+12);state=oracle.word(PHYS+0x1528)
 oracle.setword(GOBS,n+1);qb_calls[hex(name)]+=1
 row=[name,oracle.word(script+0xbc),body,state,oracle.word(state+0x18),oracle.word(GCONTEXT+0x18),oracle.word(GCONTEXT+0x54),oracle.word(GCONTEXT+0x15c),oracle.word(body+0x4c),oracle.word(body+0x50),oracle.word(body+0x54),params]
 cpu.mem_write(GOBS+64+n*48,struct.pack('<12I',*row))
 if not oracle.word(GOBS+16) or oracle.word(GOBS+16)==name:
  target=oracle.word(GOBS+4);width=oracle.word(GOBS+12)
  if target:assert width in [1,4];cpu.mem_write(target,oracle.word(GOBS+8).to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,native,begin=NATIVE,end=NATIVE)
GOWNER,GCONTACT,GATTACH,GPROVIDER,GPOINTS,GNODES=0x1660000,0x1660400,0x1660600,0x1660640,0x1660680,0x1660700
copy(GOWNER,bytes(0x1000))
put(GOWNER+4,'<I',GCONTACT);put(GOWNER+0x100,'<I',GATTACH)
put(GOWNER+0x6c,'<16f',*identity);put(GOWNER+0xc0,'<16f',*identity)
put(GCONTACT,'<3I',GOWNER,0,0);put(GCONTACT+12,'<16f',*identity);put(GCONTACT+0x6c,'<16f',*identity)
put(GATTACH,'<8I',0,0x3506ce64,0,GOWNER,0,0,0,GPROVIDER)
put(GPROVIDER,'<I',0x6462d4);put(GPROVIDER+0x18,'<I',GPOINTS);put(GPOINTS,'<I',GNODES)
for j in range(3):put(GNODES+j*32,'<4fI',j*24,0,0,1,GNODES+(j+1)*32 if j<2 else 0)
fields.add(GPROVIDER);exports.append([0x6462d4,'thug_attachment_provider_methods'])
initial=bytes(memory);oracle.initial=initial
for at in [0x403ef0,0x406080,0x4060f0,0x416f00,0x427c70,0x44ece0,0x478f00,0x478f60,0x4fe320,0x4fe490,0x4fe530,0x4feba0,0x4ff590,0x4ff920,0x4ffb10,0x5003a0,0x5019e0,0x501db0,0x503560,0x503b30,0x5055b0,0x506df0,0x506e50,0x509bd0,0x50c930,0x5196a0,0x522370,0x5232a0,0x579cc0,0x580400,0x5843a0,0x584cc0,0x5bfa8c]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
new_branches={0x50efce:'heading_reverse',0x50f015:'project_velocity',0x50f074:'gravity_override',0x50f137:'brake',0x50f157:'accelerate',0x50f167:'balance_secondary',0x50f1a0:'balance_secondary_reset',0x50f200:'balance_primary',0x50f243:'balance_primary_reset',0x50f2d0:'locked_owner_velocity',0x50f33d:'locked_attachment',0x50f35c:'dead_contact_release',0x50f36a:'contact_update',0x50f375:'failed_contact_release',0x50f39c:'contact_displacement',0x50f42c:'contact_rotation',0x50f4a2:'movement_sweep',0x50f5ce:'locked_surface_probe',0x50f5ec:'locked_material',0x50f5fe:'floor_contact',0x50f6e8:'second_pass',0x50f766:'steer',0x50f780:'align_velocity',0x50f797:'side_correction',0x50f79e:'low_speed_correction',0x50f7af:'backward_motion',0x50f7c1:'release_transition',0x50f81b:'notify'}
new_branches={at:'grounded_'+name for at,name in new_branches.items()}
branch_at.update(new_branches)
for at in new_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)

def grounded_config(numbers=None,**kw):
 b=floor_config(**kw)
 values={0x6618a713:-800,0x78f80ec4:0,0x62a1fa03:25,0xc3527ef2:.25,0xe5d73f6f:100,0xbed96eda:.001,0x1a78b6fc:.0005,0x7dd5678b:1,0x374e056b:2,0x7933a8ef:4,0x2bf71eeb:20,0xbc33d268:50,0x435f0653:.6,0x4b8bab12:12,0xbfbbd0af:6,0xb45b39e2:6,0x1c58c8b4:12,0xdef25b34:.75}
 values.update({0x406b425f:8,0xd4205c9b:6,0x20102726:4,0xe07ee1a9:1,0x1483fd01:45,0xbe0a58a0:1000,0x21fb182c:0,0x97496256:120})
 values.update(numbers or {})
 for name,value in values.items():b.symbol(name,2,bits(value))
 for name,value in [(0xb1c84b5a,1),(0x69a1ce96,2),(0xb38341c9,3)]:b.symbol(name,1,value)
 b.symbol(0xd3d12913,10,b.structure([]))
 for name,value in [(0x4610c2e3,500),(0x92e0247c,600),(0x5f9b864d,100),(0x3d24128e,200)]:
  pair=b.alloc(struct.pack('<I2f',0,value,value));b.symbol(name,10,b.structure([(0,5,pair)]))
 b.extra.append(patch(PHYS+0x1524,'<I',GCONTEXT))
 # The original stat evaluator receives constant pairs through its real graph.
 entries=[]
 for name,value in {0x1231ae3c:.2,0xa4362662:2,0x06851748:.01,0xa9fef5ab:.1,0xb6a634f3:1,0xef27e8ff:1,0x32eb3308:13,0x61ad5596:.25,0xf81ab0e9:8192}.items():
  pair=b.alloc(struct.pack('<I2f',0,value,value));entries.append((name,10,b.structure([(0,5,pair)])))
 b.extra += [patch(GCONTEXT+0x20,'<I',b.structure(entries))]
 b.symbol(0x8cc8f176,1,2000);b.symbol(0x07da1621,1,1000)
 difficulty(b,1)
 return b

def grounded(p=(),b=None,changes=None,label='grounded',before=(),attached=False,repeat=1):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 grounded_returns.clear();calls=list(before)
 for _ in range(repeat-1):calls += [call(0x50ee70,PHYS,[QUERY]),call(0x402320,BODIES+0x5c,[BODIES+0x4c])]
 s=floor_parent(0x50ee70,b=b or grounded_config(),p=p,changes=changes,label=label,before=calls,attached=attached)
 s['float_fields'] += [PHYS+0x348,GCONTROLLER+0x28]+[GCONTEXT+o+i for o in [0x24,0x12c] for i in [0x24,0x28,0x30,0x34,0x38]]+[GOBS+64+n*48+off for n in range(64) for off in [24,28,32,36,40]]
 roots=[r for r in oracle.cases[-1]['steps'] if r['fn']=='0x50ee70'];assert len(roots)==len(grounded_returns)==repeat
 previous=0
 for j,(root,(caches,count,mode)) in enumerate(zip(roots,grounded_returns)):
  root['stack_objects']=caches;root['float_fields']=s['float_fields'];root['global_float_indices']=s['global_float_indices'];root['callbacks']+=count-previous;previous=count
  if j<repeat-1:assert mode==0,(label,'next grounded frame requires grounded mode',mode)
 return s

for speed in [0,100]:grounded(p=[patch(BODIES+0xac,'<4f',0,0,speed,0)],label='full clear-space grounded frame')

training_cases=[]
for i in [0,1,2,3,13,24,26,30,34,39,57,70,98,129,278,400,488,510,521,545]:
 q=loader['queries'][i];data=bytes.fromhex(q['result']);normal=struct.unpack_from('<4f',data);point=struct.unpack_from('<4f',data,16)
 forward=[-normal[2],0,normal[0],0];length=math.hypot(forward[0],forward[2]);forward=[v/length for v in forward] if length else [0,0,1,0]
 right=[normal[1]*forward[2]-normal[2]*forward[1],normal[2]*forward[0]-normal[0]*forward[2],normal[0]*forward[1]-normal[1]*forward[0],0];basis=right+list(normal)+forward+[0,0,0,1]
 for distance in [-2,0,2,10,100]:
  position=[point[j]+normal[j]*distance for j in range(3)]+[1]
  p=[patch(BODIES+0x4c,'<4f',*position),patch(BODIES+0x5c,'<4f',position[0]-forward[0]*10,position[1],position[2]-forward[2]*10,1),patch(BODIES+0x6c,'<16f',*basis),patch(PHYS+0x18,'<16f',*basis),patch(PHYS+0x58,'<4f',*normal),patch(PHYS+0x68,'<4f',*normal),patch(BODIES+0xac,'<4f',forward[0]*100,20,forward[2]*100,0)]
  training_cases.append((i,distance,p,normal,point))
  grounded(p=p,label=f'full grounded training floor {i} distance {distance}')

for mode in [0x3506ce64,0x0ac90769,0xef24413b,0x12345678]:
 for flag in [0,1]:
  for fallback in [0,1]:
   p=training_cases[2][2]+[patch(GCONTEXT+0x18,'<I',mode),patch(STATE+0x5f0,'<I',12 if flag else 0),patch(PHYS+0x302,'<B',fallback),patch(PHYS+0x2d9,'<B',1)]
   grounded(p=p,before=[call(0x461a00,UM,[METER])],label=f'grounded balance mode {mode:x} reset {flag} acceleration {fallback}')

# Carry a valid reference through translation, rotation, release and attachment.
for i,distance,base,normal,point in training_cases:
 if distance!=0 or i not in [0,34,70,129]:continue
 for locked in [0,1]:
  for angle in [0,.25,-1.2]:
   c,s=math.cos(angle),math.sin(angle);matrix=[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]
   p=base+[patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(SKATER_STATE+0x88,'<B',locked),patch(GCONTACT+0x4c,'<4f',*point),patch(GOWNER+0x4c,'<4f',point[0]+2,point[1],point[2]-1,1),patch(GOWNER+0x6c,'<16f',*matrix),patch(GOWNER+0xc0,'<16f',*matrix),patch(GOWNER+0xac,'<4f',10,20,30,0)]
   grounded(p=p,label=f'grounded moving contact {i} lock {locked} angle {angle}')
 for dead in [0,1]:
  grounded(p=base+[patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(GCONTACT,'<I',0 if dead else GOWNER),patch(GOWNER+0x4c,'<4f',*point),patch(GCONTACT+0x4c,'<4f',*point)],label=f'grounded contact release owner {dead}')

for i,distance,base,normal,point in training_cases:
 if distance!=0 or i not in [34,70,129,278]:continue
 for speed in [.0005,.001,.5,10,49,50,100,500,1200]:
  for variant in [0,1,2]:
   p=base+[patch(BODIES+0xac,'<4f',normal[2]*speed,20,-normal[0]*speed,0),patch(PHYS+0x2d9,'<B',variant!=0),patch(PHYS+0x311,'<B',1),patch(PHYS+0x388,'<B',variant==2),patch(INPUT+0x40,'<B',variant==0),patch(INPUT+0x60,'<B',variant==1),patch(INPUT+0x80,'<B',variant==2),patch(PHYS+0x350,'<2f',1,0),patch(PHYS+0x360,'<f',300)]
   p += [patch(SKATER_STATE+off,'<B3sI',255,b'xyz',0x12345678) for off in [0x48,0x30,0x38,0x78,0xa8,0x80,0xb0]]
   grounded(p=p,changes={0x7d1ec8:0xffffffff,0x696d60:0x80000000},label=f'grounded inputs {i} speed {speed} variant {variant}')

case([call(0x460b80,BODIES)],label='capture grounded event owner constructor')
body_base=bytes(oracle.cpu.mem_read(BODIES,0x4c));fields.add(SCRIPTS+0xec)
def attached_events():
 script=bytearray(244)
 for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
 p=[raw(BODIES,body_base),patch(BODIES+0x10,'<I',SCRIPTS),raw(SCRIPTS,script),patch(EVENTS,'<IIBBHI',ENTRIES,len(EVENT_NAMES),1,0,0,0)]
 return p+[patch(ENTRIES+20*j,'<5I',name,name,0,0,1) for j,name in enumerate(EVENT_NAMES)]
for event in [0x8ffefb28,0xd3fde02a,0xa7662059,0xba95da16]:
 for target,value,width in [(0,0,0),(PHYS+0x1528,SKATER_STATE2,4),(PHYS+0x1514,SOUND2,4),(PHYS+0x2d8,1,1),(PHYS+0x388,1,1),(GCONTEXT+0x18,0,4)]:
  base=next(t[2] for t in training_cases if t[0]==34 and t[1]==0)
  if event==0xa7662059:base=[]
  p=attached_events()+base+[patch(GOBS+4,'<4I',target,value,width,event)]
  if event==0x8ffefb28:p += [patch(SKATER_STATE+0x20,'<B',1),patch(INPUT+0x1c0,'<B',0)]
  if event==0xd3fde02a:p.append(patch(SKATER_STATE+0xe1,'<B',255))
  if event==0xba95da16:p.append(patch(GCONTEXT+0x18,'<I',0x3506ce64))
  prior_count=qb_calls[hex(event)]
  grounded(p=p,attached=True,before=[call(0x41d1d0,SCRIPTS+0xbc,[BODIES]),call(0x461a00,UM,[METER])],label=f'grounded actual QB event {event:x} mutates {target:x}')
  assert qb_calls[hex(event)]>prior_count,(hex(event),hex(target),'event did not execute')

# The original locked branch writes probe endpoints directly, then 5003a0
# replaces them from the retained surface_segment at +208. Preserve that quirk.
for i in [30,34,46,74,85,129,278]:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][i]['result']),16)
 p=[patch(BODIES+0x4c,'<4f',*point),patch(BODIES+0x5c,'<4f',*point),patch(GROUND_GATE+0x18,'<I',GCONTACT),patch(SKATER_STATE+0x88,'<B',1),patch(GCONTACT+0x4c,'<4f',*point),patch(GOWNER+0x4c,'<4f',*point),[PHYS+0x208,loader['queries'][i]['segment']]]
 grounded(p=p,label=f'locked grounded retained collision segment {i}')
for i in [30,34,39,46,74,85,129,278]:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][i]['result']),16)
 for direction in [(1,0),(0,1),(-1,0),(0,-1)]:
  for dt in [.05,.2]:
   p=[patch(BODIES+0x4c,'<4f',*point),patch(BODIES+0x5c,'<4f',*point),patch(BODIES+0xac,'<4f',direction[0]*1200,0,direction[1]*1200,0),patch(PHYS+0x8c,'<f',dt)]
   grounded(p=p,label=f'grounded collision retry {i} direction {direction} step {dt}')
for speed in [0,10,50,100]:
 point=struct.unpack_from('<4f',bytes.fromhex(loader['queries'][46]['result']),16)
 p=[patch(BODIES+0x4c,'<4f',*point),patch(BODIES+0x5c,'<4f',*point),patch(BODIES+0xac,'<4f',0,0,speed,0),patch(PHYS+0x2d9,'<B',1)]
 grounded(p=p,repeat=8,label=f'eight consecutive grounded frames speed {speed}')

assert all(branches[name] for name in new_branches.values() if name!='grounded_failed_contact_release')
# 416f00 returns one for every non-null owner. No callback runs between the
# parent's owner check and that call, so the false-return branch is unreachable
# for this valid synchronous graph; do not replace a game callee to force it.

scope='Complete grounded update 50ee70 through actual balance, attachment, moving-contact, sweep, floor, steering and QB callees. Full training geometry, movement retry, both balance groups/reset bits, gravity override, braking/acceleration, timed flag wrap, platform carry/rotation/release, retained locked-probe segments, input release and component mutation are compared. Eight-frame sequences retain state and update previous position through the original copy. Required live components, finite valid geometry/meter inputs, successful allocations and terminating QB are internal contracts; generic event-owner construction does not recover skater startup. Heap and terminal native QB commands remain instrumentation boundaries. The contact-update false branch is unreachable after its non-null-owner guard in this synchronous graph. Original training is not playable; airborne/state integration, startup and rendering remain.'
fixture={'base':BASE,'memory':'grounded-update-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_qb_callbacks','pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':[index[0x6918ec+4*i] for i in range(8)],'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'grounded-update-callbacks.wasm','export':'fixture_grounded_native','original':NATIVE}]}
callback=out/'grounded-update-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/grounded_update_callbacks.c'),'-o',str(callback)],check=True)
path=out/'grounded-update-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original grounded:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_grounded_update_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'native_qb_calls':dict(qb_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],callback]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
