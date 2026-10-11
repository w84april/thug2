"""Original synchronous/spawned script scheduling with concrete network queues."""
import hashlib,json,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-schedule.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-lifetime-fixtures.json').read_text());BASE=prior['base'];SIZE=0x180000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
ENTRY,SCRIPT,PARAMS,ARGS,RETURNS,OWNER,OTHER,METHODS,DESC=BASE+0x2000,BASE+0x5800,BASE+0x5a00,BASE+0x5a10,BASE+0x5a20,BASE+0x8000,BASE+0x8200,BASE+0x8400,BASE+0x8700
BUCKETS,CALLBACK,PRINT,PROGRAM,LOG,HEAP=BASE+0x10000,BASE+0x30000,BASE+0x35f00,BASE+0x40000,BASE+0x60000,BASE+0x80000
POOL0,BLOCK0,SCRIPTS=BASE+0x22000,BASE+0x22400,BASE+0x24000
NETWORK,CLIENT,PEERS,LINKS=BASE+0x28000,BASE+0x29000,BASE+0x2c000,BASE+0x2e000
NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN,ACTIVE,NODE_FN=0x3f01000,0x3f01010,0x3f01020,0x3f01030,0x3f01040,0x3f01050
N,M,D,F,A=0xabc01001,0xabc01002,0xabc01003,0xabc01004,0xabc01005
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(n):return struct.pack('<I',n&0xffffffff)
def name(n):return b'\x16'+word(n)
put(CONTEXT,'<8I',HEAP,BASE+0x100000,0,LOG,BASE,BASE+SIZE,0,0)
put(MANAGER+0x12c,'<I',MANAGER+0x400)
put(CALLBACK,'<11I',0,1,0,0,0x6f3544,0x6f352c,0x6f3545,0x6f3530,0x6f3538,0x6f353c,0)
put(METHODS+0x1c,'<I',ACTIVE)
for owner,id_ in [(OWNER,0x12345678),(OTHER,0xffffffff)]:put(owner+0x14,'<I',id_)
put(NETWORK,'<3I',4,0,CLIENT);put(CLIENT+8,'<I',0xfffffff9);put(CLIENT+0x1e84,'<I',0)
peers=[PEERS+i*0x500 for i in range(3)];links=[LINKS+i*20 for i in range(3)];sentinel=CLIENT+0x1e8c
put(sentinel,'<5I',0x6474cc,0xffffffff,0,links[-1],links[0])
for i,p in enumerate(peers):
 for k in range(3):put(p+k*20,'<5I',0x6474cc+k*4,0xffffffff,0,p+k*20,p+k*20)
 put(p+0x3c,'<I',i);put(p+0x60,'<I',1);put(p+0x78,'<256I',*[(0xfffffffd+g+i)&0xffffffff for g in range(256)])
 put(links[i],'<5I',0x6474cc,p,0,links[i-1] if i else sentinel,links[i+1] if i<2 else sentinel)
# Parameter structures include compact names, nested values and a serialization
# overflow. Neither broadcast wrapper substitutes the real serializer.
sym_cursor=BASE+0xa200
def symbol(n,kind,value):
 global sym_cursor
 at=sym_cursor;sym_cursor+=20;bucket=BUCKETS+(n&0xfff)*4;prior_=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0x91,kind,0x9876,n,0,value,prior_);put(bucket,'<I',at);return at
for n,at,values in [(0x35115a20,BASE+0xd000,[99,N]),(0x25231f42,BASE+0xd020,[102,M])]:
 put(at,'<BBHII',0,13,0,len(values),at+12);put(at+12,'<2I',*values);symbol(n,12,at)
COMPLETION,NESTED,BIG,EMPTY=BASE+0xd100,BASE+0xd200,BASE+0xd300,BASE+0xd400
put(EMPTY,'<2I',0,0)
put(COMPLETION,'<2I',0,COMPLETION+8);put(COMPLETION+8,'<BBHIII',2,0,0,102,0xdeadbeef,0)
put(NESTED,'<2I',0,NESTED+8);put(NESTED+8,'<BBHIII',20,0,0,99,COMPLETION,NESTED+24);put(NESTED+24,'<BBHIII',26,0,0,M,N,0)
put(BIG,'<2I',0,BIG+8);put(BIG+8,'<BBHIII',6,0,0,99,BASE+0xe000,0)
memory[0xe000:0xe000+1101]=b'A'*1100+b'\0'
# Additional symbol aliases: bytecode alias and a missing endpoint.
symbol(0x12340007,13,7);symbol(0x12340008,13,0xeeeeeeee)
# Collision event data: a terminated global node table, duplicate local names,
# moving-owner parameter sets and an explicit virtual node provider.
NODE_TABLE,NODE_ARRAY,NODE_ITEMS,NODE_DATA=BASE+0x100000,BASE+0x111000,BASE+0x111100,BASE+0x118000
PROVIDER,PROVIDER_METHODS,PROBE,EVENT_COMPONENT,EVENT_BITS,SETTINGS=BASE+0x11c000,BASE+0x11c100,BASE+0x11d000,BASE+0x11e000,BASE+0x11e100,BASE+0x11e200
LOCAL_ARRAY,LOCAL_ITEMS=BASE+0x111200,BASE+0x111300
node_names=[0,0x1111,0x2222,0x3333,0x12345678,0xffffffff,0x1111]
nodes=[];node_fields=[]
for i,n in enumerate(node_names):
 at=NODE_DATA+i*0x100;nodes.append(at);entries=[(0xa1dc81f9,13,n),(0x2ca8a299,13,[5,8,5,6,5,5,6][i]),(0x5180a4db,10,NESTED),(0,13,0),(0,13,0),(0,13,0)]
 put(at,'<2I',0,at+8);node_fields.append([at+8+j*16 for j in range(len(entries))])
 for j,(key,kind,value) in enumerate(entries):put(at+8+j*16,'<BBHIII',kind*2,0,0,key,value,at+8+(j+1)*16 if j+1<len(entries) else 0)
for i in range(16384):put(NODE_TABLE+4*i,'<Hh',0,-1)
put(NODE_TABLE+0x1000c,'<I',NODE_ARRAY);put(NODE_ARRAY,'<BBHII',0,10,0,6,NODE_ITEMS);put(NODE_ITEMS,'<6I',*nodes[:6])
for i,n in enumerate(node_names[:6]):
 slot=n&0x3fff
 while struct.unpack_from('<h',memory,NODE_TABLE-BASE+slot*4+2)[0]!=-1:slot=(slot+1)&0x3fff
 put(NODE_TABLE+slot*4,'<Hh',0,i)
put(LOCAL_ARRAY,'<BBHII',0,10,0,4,LOCAL_ITEMS);put(LOCAL_ITEMS,'<4I',nodes[0],nodes[1],nodes[3],nodes[6])
put(PROVIDER,'<5I',PROVIDER_METHODS,0xc472ecc5,0,OWNER,0);put(PROVIDER_METHODS+0x34,'<I',NODE_FN)
memory[PROBE-BASE:PROBE-BASE+0xb0]=bytes(0xb0);put(PROBE+0x58,'<I',0x1111);put(PROBE+0x6d,'<B',1)
put(EVENT_COMPONENT+12,'<I',OTHER);put(EVENT_BITS,'<3I',1,2,31)
put(SETTINGS,'<3I',0,0,SETTINGS+12);put(SETTINGS+12,'<BBHIII',2,0,0,0x6dc3d6f1,1,0)
put(CALLBACK+44,'<4I',LOCAL_ARRAY,PROBE,0,0x2222)
initial=bytes(memory);(out/'script-schedule-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for at,v in [(0x7cce14,NETWORK),(0x6f3538,0),(0x6f353c,0),(0x6f3530,0),(0x6f2358,0),(0x6f235c,0),(0x6f2360,0)]:defaults[index[at]]=v
for export,at,v in [('thug_node_table',0x6f0d84,NODE_TABLE),('thug_game_settings',0x7ce470,SETTINGS)]:
 if at in index:defaults[index[at]]=v
 else:index[at]=len(globals_);globals_.append([export,at,4]);defaults.append(v)
functions={}
def bind(at,n,argc=0,this=False,result='void'):
 functions[hex(at)]={'name':n,'this':this,'result':result,'memory':True,'cleanup':argc*4 if this else 0,'stack_args':list(range(argc)),'diagnostics':True}
bind(0x473350,'thug_script_broadcast_sync',3)
bind(0x473420,'thug_script_broadcast_spawn',4)
bind(0x475420,'thug_script_spawn',10,result='word')
bind(0x475790,'thug_script_run_sync',4)
bind(0x475920,'thug_script_update_spawned')
bind(0x461480,'thug_object_spawn_script',5,True,'word')
bind(0x434a60,'thug_collision_event_start',4,True,'byte')
bind(0x434bf0,'thug_collision_event_from_probe',2,True,'byte')
for at in [0x4753c0]:functions[hex(at)]=prior['functions'][hex(at)]
observe=[int(k,16) for k in functions]+[0x4738e0,0x474540,0x4750b0,0x474420,0x475e80,0x475d60,0x479e20,0x459e50,0x457eb0,0x44e4f0,0x472980,0x5ba3d0,0x5ba400,0x45c1b0,0x45be40,0x565bb0,0x45db90,0x417140,0x417210,0x417240]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=30000000,
 observe=observe,scope_entries={BASE+0x6000:1,MANAGER+0x300:2,MANAGER+0x400:4})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.cpu.mem_map(NATIVE,4096)
# Explicit portable difference: the three unwritten spawn-packet tail bytes
# are zero in the port. Seed just those preexisting x86 stack bytes at entry;
# the original wrapper/serializer/queue instructions then execute unchanged.
# No defined field, return, global, heap event or output byte is masked.
padding_entries=0
def pad_stack(cpu,address,size,user):
 global padding_entries
 cpu.mem_write(cpu.reg_read(UC_X86_REG_ESP)-0x23,b'\0'*3);padding_entries+=1
oracle.cpu.hook_add(UC_HOOK_CODE,pad_stack,begin=0x473420,end=0x473420)
def callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);kind=[NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN,ACTIVE,NODE_FN].index(address);owner=cpu.reg_read(UC_X86_REG_ECX) if kind else 0
 n=oracle.word(sp+4) if kind in [1,2,3] else 0
 params=0 if kind>=4 else oracle.word(sp+(8 if kind else 4));script=0 if kind>=4 else oracle.word(sp+(12 if kind else 8))
 first=oracle.word(params+4) if params else 0;count=oracle.word(CALLBACK);assert count<300
 fields=[kind,owner,n,params,script,first,oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,
  oracle.word(script+12) if script else 0,oracle.word(script+200) if script else 0,cpu.mem_read(script+0xcc,1)[0] if script else 0,
  cpu.mem_read(0x6f3544,1)[0],cpu.mem_read(0x6f352c,1)[0],cpu.mem_read(0x6f3545,1)[0],oracle.word(0x6f3530),oracle.word(0x6f3538)]
 cpu.mem_write(CALLBACK+128+count*64,struct.pack('<16I',*fields));oracle.setword(CALLBACK,count+1)
 mode=oracle.word(CALLBACK+8);v=oracle.word(CALLBACK+12)
 if mode==1 and script:oracle.setword(script+164,1);oracle.setword(script+152,v)
 if mode==2 and script:oracle.setword(script+12,0)
 if mode==3 and first:oracle.setword(first+8,oracle.word(first+8)^v)
 if mode==4 and script:oracle.setword(script+232,v)
 if mode==5 and script:oracle.setword(script+12,v)
 if mode==6:cpu.mem_write(0x6f3545,b'\x01')
 if mode==7 and script:
  next_=oracle.word(script);oracle.setword(v,next_);oracle.setword(v+4,script)
  if next_:oracle.setword(next_+4,v)
  oracle.setword(script,v);oracle.setword(0x6f353c,oracle.word(0x6f353c)+1);oracle.setword(CALLBACK+8,0)
 if mode==8:cpu.mem_write(v+0xcc,bytes([oracle.word(CALLBACK+40)&255]))
 if mode==9 and script:oracle.setword(script+164,11);oracle.setword(script+152,0)
 if mode==10 and kind==5:oracle.setword(PROBE+0x68,oracle.word(CALLBACK+52));oracle.setword(PROBE+0x58,oracle.word(CALLBACK+56))
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(CALLBACK+(44 if kind==5 else 4)));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(12 if kind in [1,2,3] else 0))
for at in [NATIVE,OBJECT_FN,MEMBER_FN,COMPONENT_FN,ACTIVE,NODE_FN]:oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
labels=[];fields=set(prior['pointer_fields']);exports=prior['pointer_exports']+json.loads((out/'network-queue-fixtures.json').read_text())['pointer_exports']
exports += [[0x6f3544,'thug_script_updating'],[0x6f352c,'thug_script_wait_gate'],[0x6f3545,'thug_script_stop_pending'],[0x6f3530,'thug_current_script'],[0x6f3538,'thug_script_list'],[0x6f353c,'thug_script_count']]
exports=dict(exports);fields.update(CALLBACK+16+i*4 for i in range(6));fields.add(METHODS+0x1c);fields.add(PROVIDER_METHODS+0x34)
fields.update(at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in exports)
def call(at,*args,this=0):return (at,this,list(args)+[PRINT])
def case(calls,patches=(),changes=None,label='synthetic'):
 if len(labels)%250==0:print('Original schedule cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});callbacks=0
 for step in stages:
  merged=[]
  for at,data in step['outputs']:
   if at==CALLBACK:
    count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-callbacks;callbacks=count
   if int.from_bytes(bytes.fromhex(data),'little') in exports:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  step['outputs']=merged
 return stages
# Both packet formats, network gates, absent peer, invalid parameter encoding,
# and original low-byte network arguments. Source structures remain unchanged.
for active in [0,4,8,12,0x100]:
 for connection_flags in [0,8]:
  for owner in [0,OWNER,OTHER]:
   for params in [0,EMPTY,ARGS,COMPLETION,NESTED,BIG]:
    p=[patch(NETWORK,'<I',active),patch(CLIENT+0x1e84,'<I',connection_flags)]
    case([call(0x473350,0x87654321,params,owner),call(0x473420,0x12345678,owner,0xffffffff,0x123456ff)],p,label='broadcast serialization and gating')
for empty in [0,1]:
 p=[patch(sentinel+12,'<I',sentinel)] if empty else [patch(links[-1]+4,'<I',0)]
 case([call(0x473350,5,NESTED,OWNER),call(0x473420,5,OWNER,99,0)],p,label='empty network client')
# Native spawning is transient, does not send and ignores completion metadata.
for name_ in [N,A]:
 for params in [0,ARGS,COMPLETION]:
  for pool in [0,POOL0]:
   for completion in [0,N]:
    case([call(0x475420,name_,params,completion,NESTED,99,0xabcdef01,1,255,1,1)],changes={0x6f3550:pool},label='native spawn transient lifetime')
# Full spawn setup then frame execution, including completion handlers and pools.
for name_ in [5,6,7,8,0x12340007,0xeeeeeeee,0x12340008]:
 for params in [0,ARGS,NESTED]:
  for pool in [0,POOL0]:
   for completion in [0,N,6]:
    case([call(0x475420,name_,params,completion,COMPLETION,0xffffffff,0x12345678,1,257,0,0),call(0x475920)],changes={0x6f3550:pool},label='spawn to frame completion')
for persistent in [0,1,2,3,255,256,257,0xffffffff]:
 for activity in [0,1,2,3,255,256,257,0xffffffff]:
  case([call(0x475420,5,0,0,0,8,9,0x100,0,persistent,activity),call(0x4753c0)],label='spawn flags and persistent stopping')
# Synchronous dispatch covers script/native/member/component, alias resolution,
# unavailable names and ignored symbol tags, plus finite waits inside the loop.
for name_ in [5,6,7,8,N,A,M,D,F,0x12340007,0xeeeeeeee,0x12340008]:
 for params in [0,ARGS,NESTED]:
  for net in [0,1,256,257]:
   for owner in ([OWNER,OTHER] if name_ in [M,D] else [0,OWNER]):
    case([call(0x475790,name_,params,owner,net)],label='synchronous symbol dispatch')
for component in [0x57525413,0x0ada4e74,0x12345678]:
 for result in [0,1,256,257,0xffffffff]:
  case([call(0x475790,D,NESTED,OWNER,1)],[patch(DESC+4,'<I',component),patch(CALLBACK+4,'<I',result)],label='synchronous descriptor targets')
for frames in [0,1,2,3,9]:
 case([call(0x475790,8,ARGS,OWNER,1)],[patch(CALLBACK+8,'<2I',1,frames)],label='synchronous finite command waits')
# Collision-object wrapper executes only once and returns the still-owned
# spawned instance even when its script has finished; the next frame retires it.
for name_ in [5,6,7,8,0xeeeeeeee]:
 for owner in [0,OWNER,OTHER]:
  for net in [0,1,256,257]:
   case([call(0x461480,name_,0xabcdef01,net,0x12345680,ARGS,this=owner),call(0x475920)],label='object spawn and owner reference lifecycle')
# Construct valid active lists with distinct owned parameter structures. All
# cache references are real and their releases execute the original cache code.
def frame_list(flags,programs=None,owners=None,wait_type=0,remaining=0):
 programs=programs or [5]*len(flags);owners=owners or [0]*len(flags);scripts=[SCRIPTS+i*0x200 for i in range(len(flags))];p=[]
 for i,(s,flag,prog,owner) in enumerate(zip(scripts,flags,programs,owners)):
  b=bytearray(244);struct.pack_into('<2I',b,0,scripts[i+1] if i+1<len(scripts) else 0,scripts[i-1] if i else 0)
  struct.pack_into('<3I',b,12,PROGRAM+0x1000+(prog-5)*0x1000 if prog else 0,s+0x100,s+0x110)
  struct.pack_into('<I',b,0x2c,s+0x1c);struct.pack_into('<I',b,0x94,s+0x34);struct.pack_into('<I',b,0x98,remaining);struct.pack_into('<I',b,0xa4,wait_type)
  struct.pack_into('<I',b,0xbc,owner);struct.pack_into('<I',b,0xc8,prog);b[0xcc]=flag;p.append([s,b.hex()])
  p += [patch(s+0x100,'<2I',0,0),patch(s+0x110,'<2I',0,0)]
 for owner in set(owners)-{0}:
  selected=[s+0xbc for s,o in zip(scripts,owners) if o==owner];p.append(patch(owner+4,'<I',selected[0]))
  for i,r in enumerate(selected):p.append(patch(r+4,'<2I',selected[i-1] if i else 0,selected[i+1] if i+1<len(selected) else 0))
 for prog in range(5,9):p.append(patch(ENTRY+(prog-5)*20+8,'<I',1+programs.count(prog)))
 return scripts,p,{0x6f3538:scripts[0] if scripts else 0,0x6f353c:len(scripts)}
case([call(0x475920)],changes={0x6f3544:255,0x6f352c:255,0x6f3545:1},label='empty frame clears gates and deferred stop')
for flag in range(256):
 for prog in [0,5]:
  scripts,p,c=frame_list([flag],[prog],[OWNER]);c[0x6f352c]=1
  case([call(0x475920)],p,c,'all frame flag bytes')
for result in [0,1,255,256,257,0xffffffff]:
 for owner in [0,OWNER]:
  scripts,p,c=frame_list([9],[8],[owner]);p.append(patch(CALLBACK+4,'<I',result))
  case([call(0x475920)],p,c,'activity result low byte')
for pattern in range(16):
 flags=[(i+pattern)&15 for i in range(6)];programs=[5,8,5,8,0,5];owners=[OWNER,0,OWNER,OTHER,OTHER,0]
 scripts,p,c=frame_list(flags,programs,owners)
 for stop in [0,1,255]:
  case([call(0x475920)]*2,p,{**c,0x6f3545:stop},'mixed list and deferred stop sweep')
for wait in [1,3,11]:
 for remaining in [0,1,2]:
  scripts,p,c=frame_list([1,1,1],[5,5,5],wait_type=wait,remaining=remaining)
  case([call(0x475920)]*5,p,c,'multi-frame waits and shared gate')
for completion in [0,N,M,D,5,6,8,0xeeeeeeee]:
 scripts,p,c=frame_list([1,1],[0,5],[OWNER,OTHER])
 # Separate completion structures are owned and disposed after callback.
 for i,s in enumerate(scripts):p += [patch(s+0xd8,'<2I',completion,s+0x120),patch(s+0x120,'<2I',0,0)]
 case([call(0x475920)],p,c,'completion dispatch before disposal')
for mode in [1,2,3,4,5,6,7,8,9]:
 scripts,p,c=frame_list([1,0,3,1],[8,5,5,8],[OWNER,0,0,0]);added=SCRIPTS+7*0x200
 v={1:2,2:0,3:7,4:5,5:PROGRAM+0x1001,6:0,7:added,8:scripts[1],9:0}[mode]
 p.append(patch(CALLBACK+8,'<2I',mode,v));p.append(patch(CALLBACK+40,'<I',1))
 if mode==7:
  b=bytearray(244);struct.pack_into('<3I',b,12,PROGRAM+0x1001,added+0x100,added+0x110);struct.pack_into('<I',b,0x2c,added+0x1c);struct.pack_into('<I',b,0x94,added+0x34);struct.pack_into('<I',b,0xc8,5);b[0xcc]=1
  p += [[added,b.hex()],patch(added+0x100,'<6I',0,0,0,0,0,0),patch(ENTRY+8,'<I',4)]
 case([call(0x475920)]*3,p,c,'native changes during frame traversal')
# Actual collision-to-script paths: global/local search, reverse duplicate
# precedence, no-match first-entry behavior, additive masks and network flags.
for local in [0,LOCAL_ARRAY]:
 for n in ([0,0x1111,0x2222,0x3333] if not local else [0,0x1111,0x3333,0xdeadbeef]):
  for moving in [0,OWNER,OTHER]:
   for events in [(0,0,0),(1,2,3),(1,1,1),(31,31,31),(32,64,96),(0xffffffff,0x80000000,33)]:
    case([call(0x434a60,EVENT_BITS,n,local,moving,this=EVENT_COMPONENT),call(0x475920)],
         [patch(EVENT_BITS,'<3I',*events)],label='collision event node selection and mask')
for flags in range(8):
 for net in [0,4]:
  for players in [0,1,2,0xffffffff]:
   for script_name in [0,5]:
    p=[patch(NETWORK,'<I',net),patch(SETTINGS+20,'<I',players),patch(node_fields[1][1]+8,'<I',script_name)]
    for i,flag in enumerate([0x68910ac6,0x20209c31,0x23627fd7]):p.append(patch(node_fields[1][3+i]+8,'<I',flag if flags&(1<<i) else 0))
    case([call(0x434a60,EVENT_BITS,0x1111,0,OWNER,this=EVENT_COMPONENT),call(0x475920)],p,label='collision multiplayer and broadcast flags')
for flag in [0,1,255]:
 for checksum in [0,0x1111]:
  for event_owner in [0,OWNER]:
   for moving_owner in [0,OTHER]:
    for provider in [0,PROVIDER]:
     p=[patch(PROBE+0x6d,'<B',flag),patch(PROBE+0x58,'<I',checksum),patch(PROBE+0x68,'<I',event_owner),patch(PROBE+0x98,'<I',moving_owner),patch(OWNER+0x100,'<I',provider),patch(OTHER+0x100,'<I',provider)]
     if moving_owner:p += [patch(moving_owner+4,'<I',PROBE+0x98),patch(PROBE+0x9c,'<2I',0,0)]
     case([call(0x434bf0,EVENT_BITS,PROBE,this=EVENT_COMPONENT),call(0x475920)],p,label='probe callback-owner and moving-reference precedence')
for stale in [0,1,0xffffffff]:
 case([call(0x434bf0,EVENT_BITS,PROBE,this=EVENT_COMPONENT)],[patch(PROBE+0xa4,'<I',stale)],label='stale moving identity clears node checksum')
for returned in [0,LOCAL_ARRAY]:
 for changed_owner in [0,OWNER,OTHER]:
  p=[patch(PROBE+0x68,'<I',OWNER),patch(OWNER+0x100,'<I',PROVIDER),patch(CALLBACK+8,'<I',10),patch(CALLBACK+44,'<4I',returned,PROBE,changed_owner,0x2222)]
  case([call(0x434bf0,EVENT_BITS,PROBE,this=EVENT_COMPONENT)],p,label='node provider mutates owner and checksum')
# Inlining a single node preserves the original array accessor behavior.
case([call(0x434a60,EVENT_BITS,0x1111,LOCAL_ARRAY,0,this=EVENT_COMPONENT)],
 [patch(LOCAL_ARRAY+4,'<2I',1,nodes[1])],label='inline local collision node')
# All actual pointer fields, including allocated instance/reference headers and
# queue-node methods, are relocated. No byte is skipped in memory comparison.
for i in range((HEAP-LOG)//48):fields.update(LOG+i*48+j for j in [16,20,24,28,40])
scope='Eight original scheduling/broadcast/collision-event routines, plus existing spawned stopping: synchronous script/native/member/component dispatch; transient native and persistent bytecode spawning; completion parameters/flags; object-owned spawn and one execution; complete frame iteration, owner-activity gating, completion calls and deferred stopping; both wire message wrappers through actual parameter serialization and shared message queuing; collision event mask/node selection, multiplayer gating and full probe-to-owned-script execution, including callback/moving owner precedence and virtual node-provider mutations. Concrete executor/cache/ownership/queue callees run unchanged. Native/virtual commands and heap/scopes are instrumented boundaries, not recovered gameplay handlers. All fixture/global/output bytes and callback/heap ordering are compared. Explicit port difference: the original spawn packet copies three unwritten stack tail bytes; the port zeros them, and the oracle seeds exactly those preexisting stack bytes to zero before entry. No defined output fields are masked. Successful allocations, disabled script-value pools, valid existing owners/caches/queues and terminating synchronous scripts are internal preconditions. Runtime startup, general object-event delivery, native gameplay handlers and complete skating/rendering remain unrecovered.'
fixture={'base':BASE,'memory':'script-schedule-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'command_and_activity_callbacks',
 'pointer_symbols':prior['pointer_symbols'],'pointer_exports':list(exports.items()),'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],
 'native_callbacks':[{'module':'script-schedule-callbacks.wasm','export':'fixture_schedule_'+n,'original':a} for n,a in [('native',NATIVE),('object',OBJECT_FN),('member',MEMBER_FN),('component',COMPONENT_FN),('active',ACTIVE),('nodes',NODE_FN)]]}
path=out/'script-schedule-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
adapter=out/'script-schedule-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_schedule_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_schedule_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'zeroed_stack_padding_entries':padding_entries,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-schedule-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
