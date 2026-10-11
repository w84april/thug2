"""Original standard controller, factory/channel routing and concrete frame updates."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_animation_controllers.py').read_text().split('rng=random.Random(0x488b40)')[0]
exec(compile(prefix.replace("'animation-controllers.json'","'animation-playback.json'"),str(Path(__file__).with_name('verify_animation_controllers.py')),'exec'))
from unicorn.x86_const import UC_X86_REG_EIP
NEW=[
 (0x4a4500,'thug_standard_animation_initialize',1,'word',True,True,True),
 (0x4a4590,'thug_standard_animation_destroy',0,'void',True,False,True),
 (0x4a4f30,'thug_standard_animation_allocate',2,'word',True,False,False),
 (0x4a5600,'thug_standard_animation_free',1,'void',True,False,False),
 (0x4a55e0,'thug_standard_animation_delete',1,'word',True,False,True),
 (0x4a4670,'thug_standard_animation_command',3,'word',True,True,True),
 (0x481fb0,'thug_animation_create_controller',1,'word',True,True,True),
 (0x481870,'thug_animation_clear_controllers',0,'void',True,False,True),
 (0x481f20,'thug_animation_channel_destroy',0,'void',True,False,True),
 (0x482360,'thug_animation_channel_free',1,'void',True,False,False),
 (0x482340,'thug_animation_channel_delete',1,'word',True,False,True),
 (0x482200,'thug_animation_channel_command',3,'word',True,True,True),
 (0x481ac0,'thug_animation_channel_update',0,'void',True,True,True),
 (0x4a4620,'thug_standard_animation_update',0,'void',True,True,True),
 (0x4a4ef0,'thug_timed_animation_update',0,'void',True,True,True),
 (0x4a5180,'thug_balance_animation_position',0,'double',False,False,True),
 (0x4a52e0,'thug_balance_animation_update',0,'void',True,True,True),
 (0x488100,'thug_bone_animation_update',0,'void',True,True,True)]
assert len(NEW)==18
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
# This RET was already recovered for drawing; this is its controller ABI adapter.
bind(0x5480a0,'thug_animation_controller_idle',0,'void',True,True,True)
for file_,roots in [('animation-events',[0x481830,0x481c00,0x481bb0,0x481e10,0x4865d0]),('animation-loading',[0x4809f0,0x482af0,0x4856c0,0x482b30]),('animation-cache',[0x485270,0x482ba0,0x482bd0])]:
 f=json.loads((out/(file_+'-fixtures.json')).read_text())
 for a in roots:
  functions[hex(a)]=f['functions'][hex(a)]
  if a not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a);observe.append(a)
CM,CB,STANDARD,SPOOL,SBLOCKS,ALT_SPOOL,ALT_SBLOCKS,CP,CPBLOCKS,ALT_CP,ALT_CPBLOCKS=[BASE+x for x in [0x1e0000,0x1e1000,0x1e8000,0x1e9000,0x1e9100,0x1ea000,0x1ea100,0x1eb000,0x1eb100,0x1ec000,0x1ec100]]
ANIM,ANIM2,FILE,FILE2=BASE+0x1c1000,BASE+0x1c1100,BASE+0x280000,BASE+0x290000
memory[CM-BASE:BASE+0x1ed000-BASE]=bytes(0x1ed000-(CM-BASE))
put(STANDARD,'<10I',0x649f50,CHANNEL,0,50,0x200,0xabcdef12,ANIM,READER,0,0xffffffff)
put(CHANNEL,'<5I',0x648794,CHANNEL,0,CHANNEL,CHANNEL);put(CHANNEL+0x38,'<I',2)
put(CHANNEL+0x68,'<2I',0,0);put(CHANNEL+0x70,'<B',1)
put(CONTROLLER+0x30,'<I',ANIM)
put(ANIM,'<15I',*[0]*15);put(ANIM2,'<15I',*[0]*15)
put(ANIM,'<f',2);put(ANIM2,'<f',3)
put(AB+48,'<3I',0x124,ASSET2,0)
for p,storage,stride in [(SPOOL,SBLOCKS,0x40),(ALT_SPOOL,ALT_SBLOCKS,0x40),(CP,CPBLOCKS,0x80),(ALT_CP,ALT_CPBLOCKS,0x80)]:
 put(p,'<6I',storage,storage+8*stride,0,0,0,storage)
 for i in range(8):put(storage+i*stride,'<I',storage+(i+1)*stride if i<7 else 0)
cache_blocks=[CB+i*0x180 for i in range(50)]
put(CM,'<50I',*cache_blocks);put(CM+0xd0,'<2I',16,2)
for b in cache_blocks:put(b+0x164,'<H',0x8000);fields.add(b+0x20)
fields.add(STANDARD);exports += [[0x649f50,'thug_standard_animation_methods'],[0x6487b0,'thug_animation_event_base_methods'],[0x6487bc,'thug_animation_event_methods']]
for at in [0x4a4500,0x4a4590,0x481830,0x481f20,0x481690,0x481a20,0x486560,0x48d000]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
for name,at,value in [('thug_standard_animation_pool_index',0x701430,0),('thug_animation_channel_pool_index',0x6f92c8,0),('thug_animation_objects',0x6f0fb8,EM)]:addglobal(name,at,value)
for name,at in [('thug_standard_animation_pools',0x701438),('thug_animation_channel_pools',0x6f92d0)]:
 for i in range(2):addglobal(name,at+i*4,offset=i*4)
cache_fixture=json.loads((out/'animation-cache-fixtures.json').read_text())
for entry,value in zip(cache_fixture['globals'],cache_fixture['cases'][0]['globals']):
 name,at,width,offset=entry
 if at not in index:addglobal(name,at,CM if at==0x6f92b0 else value,width,offset)
CACHE_HEAP=ALLOCATOR+0x700
put(ADAPTER+16,'<I',0);put(CONTEXT+32,'<2I',0x200000,CACHE_HEAP)
oracle.scope_entries[CACHE_HEAP]=7
services=Counter()
def cache_service(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==0x5baf50:
  assert oracle.word(sp+4)==0x8f21a798 and oracle.word(sp+8)==1
  result=CACHE_HEAP;cleanup=8;oracle.record(5,0x8f21a798,1,result)
 else:
  assert oracle.word(CONTEXT+28)==7
  result=oracle.word(CONTEXT+32);cleanup=0;oracle.record(4,result,0,0)
 services[hex(address)]+=1
 cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x5baf50,0x5bb050]:oracle.cpu.hook_add(UC_HOOK_CODE,cache_service,begin=at,end=at)
def cache_padding(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 for delta in [-0x22,-0x12,-0x32]:cpu.mem_write(sp+delta,b'\0\0')
oracle.cpu.hook_add(UC_HOOK_CODE,cache_padding,begin=0x485270,end=0x485270)
# Reuse the actual QB event routing and terminal native observer from event tests.
EV,EV2=BASE+0x1c9004,BASE+0x1ca004
memory[EV-4-BASE:EV2+0x100-BASE]=bytes(EV2+0x100-(EV-4))
for at in [EV,EV2]:
 put(at-4,'<I',8)
 for i in range(8):put(at+i*20,'<IiB3xII',0x6487bc,i*10,1,0xabc100+i,0);fields.add(at+i*20)
# Real registered objects receive each event through 461140 and their QB table.
# Only the terminal native command is an instrumented test observer.
EVENT_STATE,PROGRAM,NATIVE=BASE+0x1cf000,BASE+0x1ce000,oracle.stop+0x400
memory[EVENT_STATE-BASE:EVENT_STATE-BASE+4096]=bytes(4096)
put(EM+0x14,'<I',0)
put(PRIMARY+8,'<I',2)
for i,widget in enumerate([WIDGET,NUMERIC]):
 put(PRIMARY+32+i*12,'<3I',0x100+i,widget,0)
 put(widget+0x14,'<I',0x100+i);put(widget+0x10,'<I',SCRIPTS)
script=bytearray(244)
for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
memory[SCRIPTS-BASE:SCRIPTS-BASE+244]=script
put(EVENTS,'<IIBBHI',ENTRIES,8,1,0,0,0)
for i in range(8):put(ENTRIES+i*20,'<5I',0xabc100+i,NOTIFY,0,0,1)
memory[PROGRAM-BASE:PROGRAM-BASE+8]=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24'
# Objective prefix installs NOTIFY's current symbol/cache pair at META.
put(META+12,'<I',PROGRAM);put(META+36,'<I',PROGRAM)
fields.update([SCRIPTS+0xec,PROGRAM+2])
def event_native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
 n=oracle.word(EVENT_STATE);assert n<32;oracle.setword(EVENT_STATE,n+1)
 row=[oracle.word(CHANNEL+0x6c),oracle.word(CHANNEL+0x64),oracle.word(CHANNEL+0x68),oracle.word(script+0xc8),oracle.word(script+0xbc),oracle.word(params+4) if params else 0]
 row += [bytes(cpu.mem_read(EV+i*20+8,1))[0] for i in range(8)]
 cpu.mem_write(EVENT_STATE+128+n*64,struct.pack('<16I',*row,0,0))
 if n==0:
  for off in [4,16,28]:
   at=oracle.word(EVENT_STATE+off);value=oracle.word(EVENT_STATE+off+4);width=oracle.word(EVENT_STATE+off+8)
   if at:assert width in [1,4];cpu.mem_write(at,value.to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,event_native,begin=NATIVE,end=NATIVE)

from prx import entries
asset_root=ROOT/'local/game-files/Game/Data';archive=asset_root/'pre/Bits.prx'
input_hashes={str(archive.relative_to(ROOT)):hashlib.sha256(archive.read_bytes()).hexdigest()}
for item in entries(archive.read_bytes()):
 if item.name.lower() in ['anims\\standardkeyq.bin','anims\\standardkeyt.bin']:
  start=0x6f9ad8 if item.name.lower().endswith('keyq.bin') else 0x6f92d8
  assert not item.compressed and len(item.payload)==2048
  for i,v in enumerate(struct.unpack('<512I',item.payload)):defaults[index[start+4*i]]=v
clips=[]
for name in ['AirIdle.ska.xbx','AirTurnLeft.ska.xbx']:
 p=asset_root/'anims/THPS6_skater_basics'/name;data=p.read_bytes();clips.append(data);input_hashes[str(p.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
initial=bytes(memory);oracle.initial=initial
labels=[]
def case(calls,patches=(),changes=None,label='animation playback',float_fields=(),quiet_fields=()):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=EVENT_STATE and at+len(data)//2>=EVENT_STATE+4:
    current=int.from_bytes(bytes.fromhex(data)[EVENT_STATE-at:EVENT_STATE-at+4],'little');s['callbacks']=current-previous;previous=current
  s['float_fields']=sorted(set(float_fields));s['quiet_float_fields']=sorted(set(quiet_fields))
 if len(labels)%100==0:print('Original animation playback cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x482200)
special=[0,0x80000000,1,0x80000001,bits(1),bits(-1),0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for i in range(32):
 case([call(0x4a4500,STANDARD,[CHANNEL]),call(0x4a4590,STANDARD)],[raw(STANDARD,bytes(rng.getrandbits(8) for _ in range(40)))],{0x6fa7f4:i&1,0x6fa7fc+4*(i&1):APOOL if i%3 else 0},label='standard constructor preserves extra word and destroys owned reader')
for selected in [0,1]:
 for where in ['heap','selected','alternate','outside']:
  change={0x701430:selected,0x701438+selected*4:SPOOL if where!='heap' else 0,0x701438+(selected^1)*4:ALT_SPOOL if where!='heap' else 0}
  pointer=SBLOCKS if where=='selected' else ALT_SBLOCKS if where=='alternate' else STANDARD
  for root in [0x4a4f30,0x4a5600]:
   case([call(root,args=[40,0xffffffff] if root==0x4a4f30 else [pointer])],changes=change,label='standard selected/alternate pools and heap '+where)
  cp=CPBLOCKS if where=='selected' else ALT_CPBLOCKS if where=='alternate' else CHANNEL
  case([call(0x482360,args=[cp])],changes={0x6f92c8:selected,0x6f92d0+selected*4:CP if where!='heap' else 0,0x6f92d0+(selected^1)*4:ALT_CP if where!='heap' else 0},label='channel pool or heap free '+where)
 for size in [0,1,40,512]:case([call(0x4a4f30,args=[size,0])],[patch(SPOOL+20,'<I',0)],{0x701430:selected,0x701438+selected*4:SPOOL},label='empty selected pool returns null')
for flag in [0,1,2,3,255,256,257,258,0xffffffff]:
 case([call(0x4a55e0,STANDARD,[flag])],label='standard scalar delete low byte')
 case([call(0x482340,CHANNEL,[flag])],label='channel scalar delete low byte')
for mask in range(4):
 case([call(0x4a4590,STANDARD)],[patch(STANDARD+0x18,'<2I',ANIM if mask&1 else 0,READER if mask&2 else 0)],label='standard cleanup with missing asset or reader')

types=[0xcb4533ff,0x6d941203,0x659bf355,0x26205db6,0x7e1940a1,0xdf5c091a,0xcfc5b380]
def factory_params(b,type_,name=0x200,priority=None):
 entries=[(0x7321a8d6,13,type_),(0x40c698af,13,name),(0x6c2bfb7f,13,0x123)]
 if priority is not None:entries.append((0x9d5923d8,1,priority&0xffffffff))
 return b.structure(entries)
for type_ in types+[0,0xffffffff]:
 for priority in [None,-2147483648,-1,0,100,500,2147483647]:
  for pooled in [False,True]:
   b=Build();p=factory_params(b,type_,priority=priority)
   case([call(0x481fb0,CHANNEL,[p]),call(0x481870,CHANNEL)],b.patches(),{0x701438:SPOOL if pooled else 0},label='factory concrete type priorities and owned cleanup')
for i in range(24):
 b=Build();calls=[]
 for j,type_ in enumerate(rng.sample(types,6)):
  p=factory_params(b,type_,0x200+j,rng.choice([-1,0,100,500]));calls.append(call(0x482200,CHANNEL,[0x83654874,p,CSCRIPT]))
 calls.append(call(0x482200,CHANNEL,[0,0,0]));calls.append(call(0x481f20,CHANNEL))
 case(calls,b.patches(),label='six mixed factory products stable ordering forwarding and full destruction')
for count in [-1,0,1,3,6]:
 p=[patch(CHANNEL+0x54,'<i',count),patch(CHANNEL+0x3c,'<6I',FLAGS,0,POSE,0,BONE,0)]
 case([call(0x481870,CHANNEL)],p,label='clear signed count and null controller slots')
for name in [0,0x200,0x201,0x202,0x999]:
 b=Build();calls=[call(0x481fb0,CHANNEL,[factory_params(b,t,0x200+i)]) for i,t in enumerate([0xdf5c091a,0xcfc5b380,0x26205db6])]
 p=b.structure([(0x40c698af,13,name)]);calls += [call(0x482200,CHANNEL,[0x986d274e,p,CSCRIPT]),call(0x481f20,CHANNEL)]
 case(calls,b.patches(),label='remove matching controller then forward to remaining live list')
for type_ in [0,0x7e1940a0,0xffffffff]:
 b=Build();p=factory_params(b,type_);case([call(0x482200,CHANNEL,[0x83654874,p,0])],b.patches(),label='create command reports handled even for unknown factory type')

def start_params(b,name=0x123,first=0,last=2,speed=1,loop=1):
 return b.structure([(0x6c2bfb7f,13,name),(0xd16b61e6,2,bits(first)),(0xab81bb3d,2,bits(last)),(0xcd8d7c1b,1,loop),(0x8f0d24ed,2,0),(0xf0d90109,2,bits(speed))])
for i in range(100):
 b=Build();p=start_params(b,first=rng.uniform(-5,0),last=rng.uniform(1,10),speed=rng.uniform(-5,5),loop=i%4)
 case([call(0x4a4670,STANDARD,[0xaf2fae19,p,CSCRIPT]),call(0x4a4670,STANDARD,[0x5f495ae0,0,CSCRIPT]),call(0x4a4590,STANDARD)],b.patches(),label='standard timeline setup asset selection pin refresh and release')
for i in range(28):
 b=Build();p=start_params(b);s=b.structure([(0x98549ba4,13,0x124)])
 case([call(0x4a4670,STANDARD,[0xaf2fae19,p,0]),call(0x4a4670,STANDARD,[0xc68365eb,s,0]),call(0x4a4590,STANDARD)],b.patches(),{0x6fa7f4:i&1,0x6fa7fc+4*(i&1):APOOL if i%3 else 0},label='replace original reader and unpin previous asset')
for command in [0,0x92267216,0x92267218,0xffffffff]:case([call(0x4a4670,STANDARD,[command,0xffffffff,0xffffffff])],label='unknown standard command does not access parameters')
for fmt in [2,3,4]:
 for evict in [0,1]:
  for pooled in [False,True]:
   b=Build();p=start_params(b);replacement=b.structure([(0x98549ba4,13,0x124)])
   calls=[call(0x482af0,ANIM),call(0x4856c0,ANIM,[FILE,len(clips[0]),0]),call(0x482af0,ANIM2),call(0x4856c0,ANIM2,[FILE2,len(clips[1]),0]),call(0x4a4500,STANDARD,[CHANNEL]),call(0x4a4670,STANDARD,[0xaf2fae19,p,0]),call(0x4a4670,STANDARD,[0x92267217,0,0]),call(0x4a4670,STANDARD,[0xc68365eb,replacement,0]),call(0x4a4670,STANDARD,[0x92267217,0,0]),call(0x4a55e0,STANDARD,[1]),call(0x482b30,ANIM),call(0x482b30,ANIM2)]
   patches=b.patches()+[raw(FILE,clips[0]),raw(FILE2,clips[1]),patch(CM+0xd4,'<I',fmt),patch(CM+0xdc,'<B',evict)]
   case(calls,patches,{0x6fa7fc:APOOL if pooled else 0},label='real clips load select cache build replace and full ownership release')

# Real QB event arrays load through the full channel change command.
for keep in [False,True]:
 for current in [0,.25,1,2,5]:
  for old_events in [0,8]:
   b=Build();items=[b.structure([(0x4a07c332,1,i*10),(0xc451f558,13,0xabc100+i),(0x7031f10c,10,b.structure([(1,1,i)]))]) for i in range(4)]
   b.symbol(0xabc123,10,b.structure([(0x124,12,b.array(10,items))]))
   p=b.structure([(0x98549ba4,13,0x124),(0x79a07f3f,2,bits(3))]+([(0,13,0xd3d40a85)] if keep else []))
   calls=[call(0x482200,CHANNEL,[0xc68365eb,p,0]),call(0x481f20,CHANNEL)]
   patch_=b.patches()+[patch(CHANNEL+0x14,'<4f',0,current,2,1/60),patch(CHANNEL+0x24,'<2I',0,1),patch(CHANNEL+0x68,'<2I',EV if old_events else 0,old_events),patch(CHANNEL+0x54,'<I',1),patch(CHANNEL+0x3c,'<I',STANDARD)]
   case(calls,patch_,label='channel replacement reloads real QB event array and preserves normalized time')

for i in range(140):
 first,last=(-5,5);current=rng.choice([-5,5,rng.uniform(-8,8)]);speed=rng.uniform(-.1,.1);direction=0 if i&1 else 0xffffffff
 p=[patch(CHANNEL+0x14,'<4f',first,current,last,speed),patch(CHANNEL+0x24,'<2I',direction,i%4),patch(CHANNEL+0x68,'<2I',EV,8),patch(TIME+0x14,'<4f',first,current,last,speed),patch(TIME+0x24,'<2I',direction,i%4)]
 case([call(0x4a4620,STANDARD),call(0x4a4ef0,TIMED)],p,label='standard and private timed updates advance wrap emit real QB events and refresh readers')
for i in range(320):
 start,end=(-2,4) if i<240 else (0,0)
 values=[rng.uniform(0,.5),rng.uniform(0,.25),rng.uniform(-.02,.02),rng.uniform(-.01,.01),rng.uniform(.25,3)] if i<240 else [rng.choice(special) for _ in range(5)]
 # Unicorn leaves infinite FSIN arguments unchanged, unlike hardware and the
 # platform adapter. Keep infinities in amplitude inputs, but use signed maximum
 # finite values for phase frequencies. NaNs and finite out-of-range phases stay.
 if i>=240:
  for j in [2,3]:
   if values[j]&0x7fffffff==0x7f800000:values[j]=(values[j]&0x80000000)|0x7f7fffff
 patch_=patch(CONTROLLER+0x14,'<5f',*values) if i<240 else patch(CONTROLLER+0x14,'<5I',*values)
 p=[patch_,patch(CONTROLLER+0x28,'<f',rng.uniform(-5,5)),patch(CHANNEL+0x14,'<4f',start,rng.uniform(-5,5),end,1/60)]
 case([call(0x4a5180,CONTROLLER),call(0x4a52e0,CONTROLLER)],p,{0x7d1ec8:rng.getrandbits(32),0x696d60:rng.getrandbits(32)},label='balance modulation signed ticks nested phases range clamps and nonfinite arithmetic',float_fields=[CHANNEL+0x18])
for i in range(80):
 p=[]
 for j in range(4):
  body=BODIES+j*0x400
  p += [patch(PRIMARY+32+j*12,'<3I',0x100+j,body if (i+j)%3 else 0,0),patch(body+0x4c,'<4I',*[rng.choice(special) if i<40 else bits(rng.uniform(-100,100)) for _ in range(4)]),patch(BONE+0x18+j*0x64,'<I',0x100+j),patch(BONE+0x74+j*0x64,'<3B',i&1,(i+j)%3==0,0),patch(BONE+0x54+j*0x64,'<4I',*[rng.choice(special) if i<40 else bits(rng.uniform(-100,100)) for _ in range(4)])]
 case([call(0x488100,BONE)],p,label='bone target lookup missing objects flags and four-lane offsets',float_fields=[BONE+0x44+j*0x64+k*4 for j in range(4) for k in range(4)])
for i in range(160):
 p=[patch(CHANNEL+0x38,'<I',[0,1,2,3,0xffffffff][i%5]),patch(CHANNEL+0x58,'<3I',*[rng.choice(special) for _ in range(3)]),patch(CHANNEL+0x2c,'<B',255)]
 case([call(0x481ac0,CHANNEL)],p,{0x684fc8:rng.choice(special)},label='fade gates signed zero nonfinite and unspilled arithmetic',float_fields=[CHANNEL+0x5c])
case([call(0x5480a0,FLAGS)],label='shared empty update')

# Complete mixed virtual update order, with a native QB handler changing the
# live controller count or channel time while the original loop is active.
for target,value,width in [(0,0,0),(CHANNEL+0x54,0,4),(CHANNEL+0x54,2,4),(CHANNEL+0x18,bits(.75),4),(CHANNEL+0x38,1,4),(CHANNEL+0x70,0,1)]:
 p=[patch(CHANNEL+0x54,'<I',4),patch(CHANNEL+0x3c,'<4I',STANDARD,TIMED,BONE,FLAGS),patch(CHANNEL+0x14,'<4f',0,0,2,.5),patch(CHANNEL+0x24,'<2I',0,1),patch(CHANNEL+0x68,'<2I',EV,8),patch(EVENT_STATE+4,'<3I',target,value,width)]
 case([call(0x481ac0,CHANNEL)],p,label='full channel concrete updates and real native handler mutation')

adapter=out/'animation-playback-memory.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(ROOT/'tools/animation_cache_memory.c'),'-o',str(adapter)],check=True)
scope='Eighteen new complete routines and the already recovered shared empty update recover the standard cache controller, all seven factory types, channel command/ownership/fade/frame dispatch and each concrete controller update. Real game virtual methods, asset lookup, original clips/dictionaries, cache pin/build/replace/release, QB event arrays and native event delivery execute through original callees. Terminal native handlers and diagnostic/heap services are explicit observers. All memory/globals/returns and heap records compare, apart from typed arithmetic NaNs and documented x87 quieting. FSIN uses the existing platform math adapter; physical x87 transcendental accuracy is not claimed. Infinite phase frequencies are outside strict comparisons because Unicorn leaves infinite FSIN inputs unchanged, unlike hardware and the adapter; a read-only original trace is retained separately. Nonfinite amplitudes and finite/NaN phases are covered. Required parameters/live assets, successful allocation, at most six controllers and terminating timelines are internal contracts. Pose interpolation/render methods, component integration, full movement/startup and playable training remain unfinished.'
fixture={'base':BASE,'memory':'animation-playback-memory.bin','memory_adapter':ADAPTER,'memory_fixture':adapter.name,'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_animation_cache_scope','fixture_animation_cache_available'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_native_event_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'function_exports':[[0x482b90,'thug_keyframe_animation_cache_cleared']],'native_callbacks':[{'module':'animation-asset-callbacks.wasm','export':'fixture_animation_diagnostics','slots':[PRINT+4]},{'module':'animation-events-callbacks.wasm','export':'fixture_animation_event_native','original':NATIVE}]}
path=out/'animation-playback-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),sum(oracle.counts.values()),dict(oracle.counts),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_animation_playback_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'heap_service_events':dict(services),'scope':scope,'input_hashes':input_hashes,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()),'new roots',len(NEW))
