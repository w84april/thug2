"""Compare event delivery, reentrant callbacks and script lifetime with x86."""
import hashlib,json,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'event-delivery.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-schedule-fixtures.json').read_text());BASE=prior['base'];SIZE=0x180000
memory=bytearray((out/prior['memory']).read_bytes())
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
ENTRY,SCRIPT,ARGS,OWNER,OTHER,METHODS=BASE+0x2000,BASE+0x5800,BASE+0x5a10,BASE+0x8000,BASE+0x8200,BASE+0x8400
BUCKETS,CALLBACK,DIAGNOSTICS,PRINT,PROGRAM,LOG,HEAP=BASE+0x10000,BASE+0x30000,BASE+0x35000,BASE+0x35f00,BASE+0x40000,BASE+0x60000,BASE+0x80000
POOL0,POOL1,BLOCK0,BLOCK1=BASE+0x22000,BASE+0x22100,BASE+0x22400,BASE+0x22800
EM=BASE+0x130000;ELOG=EM+0x20;WAITERS=EM+0xb038
OTABLE,OBUCKETS,LTABLE,LBUCKETS,NTABLE=BASE+0x140000,BASE+0x140100,BASE+0x140200,BASE+0x140300,BASE+0x140400
EVENT,RECEIVERS,RMETHODS,LIST,LISTNODES=BASE+0x140800,BASE+0x141000,BASE+0x141200,BASE+0x141300,BASE+0x141400
EVENTS,ENTRIES,SCRIPTS,VALUES,FRAMES,REFS=BASE+0x142000,BASE+0x142400,BASE+0x144000,BASE+0x146000,BASE+0x148000,BASE+0x149000
NAMES,NAMEITEMS,NAMETEXT=BASE+0x14a000,BASE+0x14a100,BASE+0x14b000
NATIVE,RECEIVE,OBJECT_FN,DONE=0x3f01000,0x3f01060,0x3f01070,0x3f01100
N=0xabc01001;EV=0x1111;WILDCARD=0x36b2ee74

def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,data.hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
put(CONTEXT,'<8I',HEAP,BASE+0x100000,0,LOG,BASE,BASE+SIZE,0,0)
memory[EM-BASE:EM-BASE+0xb218]=bytes(0xb218)
put(EM,'<5I',0,0,OTABLE,OTABLE,LTABLE);put(EM+0xb034,'<I',0xabcdef01)
put(ELOG+0xb008,'<I',NTABLE)
for table,buckets in [(OTABLE,OBUCKETS),(LTABLE,LBUCKETS),(NTABLE,NTABLE+32)]:
 put(table,'<6I',2,buckets,0,0xffffffff,0,0);memory[buckets-BASE:buckets-BASE+48]=bytes(48)
put(OTABLE+8,'<I',2);put(OBUCKETS+12,'<3I',1,OWNER,0);put(OBUCKETS+24,'<3I',2,OTHER,0)
put(METHODS+0x14,'<I',OBJECT_FN)
for owner,key in [(OWNER,1),(OTHER,2)]:
 put(owner+4,'<I',0);put(owner+8,'<I',0x20);put(owner+0x14,'<I',key);put(owner+0x4c,'<4f',0,0,0,1)
put(RMETHODS,'<2I',0xabcdef01,RECEIVE)
for i in range(3):put(RECEIVERS+i*32,'<7I',RMETHODS,0,0,0,RECEIVERS+(i+1)*32 if i<2 else 0,0,5+i)
put(EVENT,'<5I',EV,1,WILDCARD,0,0)
put(LIST,'<5I',0x6478dc,0xffffffff,0,LIST,LIST)
for i in range(8):
 at=EVENTS+i*16;put(at,'<IIBBHI',ENTRIES+i*80,0,1,0,0x9876,0)
 for j in range(4):put(ENTRIES+i*80+j*20,'<5I',EV,8,j,0,0)
 at=VALUES+i*128;put(at,'<2I',0,at+8);put(at+8,'<BBHIII',2,0,0,99,20+i,0)
put(CALLBACK,'<32I',0,1,0,0,0,0,0,0,EVENTS,EM,PRINT,ADAPTER,EVENT,0,0,0,0,0,*([0]*14))
put(DIAGNOSTICS,'<I',0)
# Readable event names exercise duplicate checksums and hash collisions.
name_texts=[b'Land',b'WALL\\Hit',b'land',b'',b'x'*63]+[('event_'+str(i)).encode() for i in range(27)]
put(NAMES,'<BBHII',0,3,0,len(name_texts),NAMEITEMS)
for i,value in enumerate(name_texts):
 at=NAMETEXT+i*64;memory[at-BASE:at-BASE+len(value)+1]=value+b'\0';put(NAMEITEMS+i*4,'<I',at)
nsym=BASE+0xa600;bucket=BUCKETS+(0x08114f90&0xfff)*4
put(nsym,'<BBHIIII',0,12,0,0x08114f90,0,NAMES,struct.unpack_from('<I',memory,bucket-BASE)[0]);put(bucket,'<I',nsym)
initial=bytes(memory);(out/'event-delivery-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for at,value in [(0x6f0fc0,EM),(0x6f3538,0),(0x6f353c,0),(0x6f3530,0)]:defaults[index[at]]=value
for n,at,offset in [('thug_script_structure_pool_index',0x6f3614,0),('thug_script_structure_pools',0x6f361c,0),('thug_script_structure_pools',0x6f3620,4)]:
 index[at]=len(globals_);globals_.append([n,at,4,offset]);defaults.append(0)
functions={}
def bind(at,n,argc=0,this=True,heap=False,result='void',diag=False):
 functions[hex(at)]={'name':n,'this':this,'memory':heap,'result':result,'cleanup':argc*4 if this else 0,'stack_args':list(range(argc)),'diagnostics':diag}
bind(0x409070,'thug_script_structure_free',1,False,True)
bind(0x416dd0,'thug_object_reference_destroy')
bind(0x41a820,'thug_vector_distance_squared',2,False,result='double')
bind(0x42b580,'thug_object_reference_initialize',result='word')
bind(0x45f7f0,'thug_event_initialize',4)
bind(0x45f9b0,'thug_event_mark_handled',2,heap=True)
bind(0x460150,'thug_event_destroy',heap=True)
bind(0x460470,'thug_script_events_deliver',2,heap=True,diag=True)
bind(0x4609f0,'thug_object_emit_event',2,heap=True,diag=True)
bind(0x4620a0,'thug_event_log_print',2,diag=True)
bind(0x4627c0,'thug_event_log_record',6,heap=True)
bind(0x462b10,'thug_event_record_handled',3,heap=True)
bind(0x462f00,'thug_event_emit',6,heap=True,result='byte',diag=True);functions['0x462f00']['float_args']=[5]
bind(0x472e20,'thug_script_find_spawned',1,False,result='word')
bind(0x472ed0,'thug_script_set_interrupt_checksum',1)
bind(0x472ee0,'thug_script_get_interrupt_checksum',result='word')
bind(0x4734b0,'thug_script_find_serial',1,False,result='word')
bind(0x473800,'thug_script_receive_event',1,heap=True,result='word',diag=True)
bind(0x4747a0,'thug_script_setup_named',3,heap=True,diag=True)
bind(0x4783c0,'thug_script_set_scalar',3,heap=True)
bind(0x4a1090,'thug_event_receiver_dispatch',1)
# Existing functions only for full setup/disposal and reference lifecycle sequences.
for source,addresses in [('script-lifetime',[0x4738e0,0x474420,0x4756c0]),('script-schedule',[0x475920])]:
 f=json.loads((out/(source+'-fixtures.json')).read_text())['functions']
 for at in addresses:functions[hex(at)]=f[hex(at)]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=30000000,
 observe=[int(k,16) for k in functions]+[0x475750,0x4750b0,0x475420,0x475e80,0x475d60,0x477130,0x478480,0x463820,0x4637c0,0x4637e0,0x5ba3d0,0x5ba400,0x463450,0x401b90,0x46cb70],
 scope_entries={BASE+0x6000:1,MANAGER+0x300:2,MANAGER+0x400:4})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.cpu.mem_map(NATIVE,4096)
pending=[]
def return_callback(cpu,sp,cleanup=0):
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(CALLBACK+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
def nested(cpu,fn,this,args,sp,cleanup):
 pending.append((sp,cleanup));newsp=sp-4*(len(args)+1)
 cpu.mem_write(newsp,struct.pack('<'+'I'*(len(args)+1),DONE,*args));cpu.reg_write(UC_X86_REG_ESP,newsp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EIP,fn)
def callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if address==DONE:
  original,cleanup=pending.pop();return_callback(cpu,original,cleanup);return
 kind=0 if address==NATIVE else 1 if address==RECEIVE else 2
 owner=cpu.reg_read(UC_X86_REG_ECX) if kind else 0
 params=0 if kind else oracle.word(sp+4);script=0 if kind else oracle.word(sp+8);event=oracle.word(sp+4) if kind else 0
 first=oracle.word(params+4) if params else 0;count=oracle.word(CALLBACK);assert count<190
 record=[kind,owner,script,params,first,oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,
  oracle.word(script+200) if script else 0,oracle.word(script+164) if script else 0,oracle.word(script+48) if script else 0,
  cpu.mem_read(script+0xcc,1)[0] if script else 0,oracle.word(oracle.word(CALLBACK+32)+12),oracle.word(EM+0x1c),
  *([oracle.word(event+j*4) for j in range(5)] if event else [0]*5),oracle.word(owner+24) if kind==1 else 0,
  oracle.word(EM+0xb034),oracle.word(ELOG+0xb00c),oracle.word(ELOG+0x7000),oracle.word(ELOG+0xb010),oracle.word(CALLBACK+4)]
 cpu.mem_write(CALLBACK+128+count*96,struct.pack('<24I',*record));oracle.setword(CALLBACK,count+1)
 if not kind:
  mode=oracle.word(CALLBACK+8);arg=oracle.word(CALLBACK+12);value=oracle.word(CALLBACK+16)
  if mode==1:oracle.setword(script+164,1);oracle.setword(script+152,value)
  if mode==2:cpu.mem_write(arg+9,bytes([value&255]))
  if mode==3:cpu.mem_write(arg+8,bytes([value&255]))
  if mode==4:oracle.setword(arg,value)
  if mode in [5,6,7]:
   oracle.setword(CALLBACK+8,0)
   if mode==5:nested(cpu,0x4756c0,0,[arg],sp,0)
   if mode==6:nested(cpu,0x460470,arg,[oracle.word(CALLBACK+48),script],sp,0)
   if mode==7:nested(cpu,0x462f00,EM,[arg,value,oracle.word(CALLBACK+20),oracle.word(CALLBACK+24),oracle.word(CALLBACK+28),bits(-1)],sp,0)
   return
 else:
  mode=oracle.word(CALLBACK+52);arg=oracle.word(CALLBACK+56)
  if mode==1:oracle.setword(event+12,oracle.word(event+12)|arg)
  if mode==2:oracle.setword(event+8,arg)
  if mode==3:oracle.setword(owner+16,arg);oracle.setword(CALLBACK+52,0)
  if mode==4:
   for off,c in [(0,56),(4,60),(8,64),(16,68)]:oracle.setword(event+off,oracle.word(CALLBACK+c))
  if mode==5:oracle.setword(event+16,arg);oracle.setword(event+12,oracle.word(event+12)|4)
  if mode==6:
   oracle.setword(CALLBACK+52,0);nested(cpu,0x462f00,EM,[arg,oracle.word(CALLBACK+60),oracle.word(CALLBACK+64),0,0,bits(-1)],sp,4);return
 return_callback(cpu,sp,4 if kind else 0)
for at in [NATIVE,RECEIVE,OBJECT_FN,DONE]:oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
def diagnostic(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);format_=oracle.word(sp+4);assert format_ in [0x647890,0x647850,0x647868]
 count=oracle.word(DIAGNOSTICS);oracle.setword(DIAGNOSTICS+4+count*8,format_);oracle.setword(DIAGNOSTICS+8+count*8,0);oracle.setword(DIAGNOSTICS,count+1)
 cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
labels=[];fields=set(prior['pointer_fields']);exports=dict(prior['pointer_exports'])
fields.update([METHODS+0x14,RMETHODS+4]);fields.update(DIAGNOSTICS+4+8*i for i in range(20))
# Prior callback-global addresses are no longer stored at those context offsets.
fields.difference_update(range(CALLBACK,CALLBACK+128,4))
symbols=prior['pointer_symbols']+[[0x647890,'thug_event_log_separator','='*56+'\n'],[0x647850,'thug_event_log_title','PRINTING EVENT LOG\n\n'],[0x647868,'thug_event_log_new_title','PRINTING EVENT LOG (ONLY NEW ENTRIES)\n\n']]
def call(at,*args,this=0):return (at,this,list(args)+([PRINT] if functions[hex(at)].get('diagnostics') else []))
def case(calls,patches=(),changes=None,label='synthetic'):
 if len(labels)%200==0:print('Original event cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});callbacks=0
 assert not pending
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
# Build valid owned script lists and real cached-program references. Distinct
# event parameter structures are owned by each entry, so disposal is observable.
def script_list(count,program=5,handlers=0,owner=0,flags=1):
 scripts=[SCRIPTS+i*0x200 for i in range(count)];p=[]
 for i,s in enumerate(scripts):
  b=bytearray(244);struct.pack_into('<2I',b,0,scripts[i+1] if i+1<count else 0,scripts[i-1] if i else 0)
  struct.pack_into('<3I',b,12,PROGRAM+(program-4)*0x1000 if program else 0,s+0x100,s+0x110)
  struct.pack_into('<I',b,0x2c,s+0x1c);struct.pack_into('<I',b,0x94,s+0x34)
  struct.pack_into('<I',b,0xb0,100+i);struct.pack_into('<I',b,0xbc,owner);struct.pack_into('<I',b,0xc8,program);b[0xcc]=flags
  struct.pack_into('<I',b,0xd4,0x200+i);struct.pack_into('<I',b,0xe0,EVENTS+i*16 if handlers else 0);struct.pack_into('<I',b,0xec,0x6478e4)
  p += [raw(s,b),patch(s+0x100,'<6I',0,0,0,0,0,0),patch(EVENTS+i*16+4,'<I',handlers)]
  for j in range(handlers):p.append(patch(ENTRIES+i*80+j*20,'<5I',EV,8,0,0,0))
  if owner:p.append(patch(s+0xc0,'<2I',scripts[i-1]+0xbc if i else 0,scripts[i+1]+0xbc if i+1<count else 0))
 if owner:p.append(patch(owner+4,'<I',scripts[0]+0xbc if count else 0))
 for prog in range(5,9):p.append(patch(ENTRY+(prog-5)*20+8,'<I',1+(count if program==prog else 0)))
 return scripts,p,{0x6f3538:scripts[0] if count else 0,0x6f353c:count}
def subscribe(scripts):
 nodes=[LISTNODES+i*20 for i in range(len(scripts))]
 p=[patch(LTABLE+8,'<I',1),patch(LBUCKETS+(EV&3)*12,'<3I',EV,LIST,0),patch(LIST,'<5I',0x6478dc,0xffffffff,0,nodes[0] if nodes else LIST,nodes[-1] if nodes else LIST)]
 for i,(node,s) in enumerate(zip(nodes,scripts)):p.append(patch(node,'<5I',0x6478d8,s,0,nodes[i+1] if i+1<len(nodes) else LIST,nodes[i-1] if i else LIST))
 return p
# Event value ownership and handlers' ability to mark an event repeatedly.
for flags in [0,1,2,3,4,5,6,7,0xffffffff]:
 for params in [0,VALUES,ARGS]:
  case([call(0x460150,this=EVENT)],[patch(EVENT+12,'<2I',flags,params)],label='event parameter ownership')
for name in [0,EV,0xffffffff]:
 for params in [0,VALUES]:
  case([call(0x45f7f0,name,0xffffffff,WILDCARD,params,this=EVENT),call(0x45f9b0,2,5,this=EVENT),call(0x462b10,EVENT,3,8,this=EM)],label='event initialize and mark handled')
# Raw log behavior, including wrap, consecutive phase coalescing and lazy names.
for next_ in [0,1,1022,1023]:
 for depth in [0,1,0xffffffff]:
  for phase in [0,1,2,3,0xffffffff]:
   for prior_phase in [0,3]:
    p=[patch(ELOG+0x7000,'<I',next_),patch(ELOG+0xb00c,'<2I',depth,0xffffffff),patch(ELOG+((next_-1)&1023)*28+20,'<I',prior_phase)]
    case([call(0x4627c0,EV,1,2,5,7,phase,this=ELOG)]*3,p,label='log phase and ring boundaries')
for count in [0,1,2,3,5,32]:
 case([call(0x4627c0,EV,1,2,5,7,0,this=ELOG),call(0x4627c0,EV,1,2,5,7,1,this=ELOG)],
  [patch(ELOG+0xb008,'<I',0),patch(NAMES+4,'<2I',count,NAMETEXT if count==1 else NAMEITEMS)],label='lazy event names and duplicate checksum buckets')
for wrapped in [0,1,255]:
 for flag in [0,1,256,257,0xffffffff]:
  case([call(0x4620a0,flag,17,this=ELOG)],[patch(ELOG+0x7000,'<IB',7,wrapped),patch(ELOG+0xb010,'<I',99)],label='log diagnostic headers')
# Reference initialization/destruction, including head, interior and null nodes.
for count in [0,1,4]:
 for selected in range(max(count,1)):
  p=[patch(OWNER+4,'<I',REFS if count else 0)]
  for i in range(count):p.append(patch(REFS+i*12,'<3I',OWNER,REFS+(i-1)*12 if i else 0,REFS+(i+1)*12 if i+1<count else 0))
  if not count:p.append(patch(REFS,'<3I',0,0x12345678,0xabcdef01))
  case([call(0x416dd0,this=REFS+selected*12)]*2+[call(0x42b580,this=REFS+selected*12)],p,label='intrusive reference lifetime')
# Standalone structure free checks both selected/alternate fixed pools.
for selected in [0,1]:
 for pools in [(0,0),(POOL0,0),(0,POOL1),(POOL0,POOL1)]:
  for pointer in [0,BLOCK0-4,BLOCK0,BLOCK0+4,BLOCK0+0x400,BLOCK1,BLOCK1+0x400,VALUES]:
   case([call(0x409070,pointer)],changes={0x6f3614:selected,0x6f361c:pools[0],0x6f3620:pools[1]},label='structure release pool membership')
# Scalar dispatcher tags include unsupported values and raw float payloads.
for tag in [0,1,2,3,10,11,12,13,14,255,0xffffffff]:
 for key in [0,99,100]:
  values=[0,1,0xffffffff,0x7fa12345] if tag not in [11,12] else [VALUES+128] if tag==11 else [NAMES]
  for value in values:case([call(0x4783c0,key,tag,value,this=VALUES)],label='generic setter tag switch')
# Extended exponent arithmetic and X/Z/Y order, plus ignored W and nonfinite.
rng=random.Random(0x41a820)
for i in range(512):
 a=[rng.randrange(0x100000000) for _ in range(4)];b=[rng.randrange(0x100000000) for _ in range(4)]
 if i<8:a=[([0,0x80000000,1,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7fa12345][i])]*4;b=[0]*4
 case([call(0x41a820,OWNER+0x4c,OTHER+0x4c)], [patch(OWNER+0x4c,'<4I',*a),patch(OTHER+0x4c,'<4I',*b)],label='squared distance float boundaries')
# Find by spawned ID or serial; only user-value lookup consults the flag.
for count in [0,1,4]:
 for flag in [0,1,2,3,255]:
  scripts,p,c=script_list(count,flags=flag)
  for key in [0,100,102,0x200,0x202,0xffffffff]:
   case([call(0x472e20,key),call(0x4734b0,key)],p,c,'script list identity searches')
for value in [0,1,0xffffffff,0xabcdef01]:case([call(0x472ed0,value,this=SCRIPT),call(0x472ee0,this=SCRIPT)],label='interrupt checksum accessors')
for name in [5,6,7,8]:
 for params in [0,VALUES,ARGS]:
  for owner in [0,OWNER]:
   case([call(0x4738e0,this=SCRIPTS),call(0x4747a0,name,params,owner,this=SCRIPTS),call(0x474420,this=SCRIPTS)],label='named setup wrapper full lifecycle')
# Wait wake-up affects active and saved frames but leaves all arguments intact.
for event in [0,EV,EV+1]:
 for wait in [0,1,3,19]:
  for arg in [0,EV,EV+1]:
   scripts,p,c=script_list(1);s=scripts[0];p += [patch(EVENT,'<I',event),patch(s+0xa4,'<2I',wait,arg),patch(s+0x30,'<I',8),patch(s+0x94,'<I',FRAMES)]
   for i in range(8):p += [patch(FRAMES+i*48+32,'<I',[0,EV,EV+1][i%3]),patch(FRAMES+i*48+40,'<I',0xa1b2c3d0|([3,1,3,0][i%4]))]
   case([call(0x473800,EVENT,this=s)]*2,p,c,'active and suspended event waits')
# Direct table delivery: immediate calls, full replacement, interrupt callback,
# owner-spawn behavior and merge precedence. All handler bytecode really executes.
for handlers in [0,1,3]:
 for flag in [0,1,2,3]:
  for owner_flags in [0,0x10000]:
   for event_params in [0,VALUES]:
    for entry_params in [0,VALUES+128]:
     scripts,p,c=script_list(1,handlers=handlers,owner=OWNER);s=scripts[0]
     p += [patch(OWNER+8,'<I',owner_flags),patch(EVENT+16,'<I',event_params)]
     for j in range(handlers):p += [patch(ENTRIES+j*20+12,'<2I',entry_params,flag)]
     case([call(0x473800,EVENT,this=s)],p,c,'event table immediate replacement spawn and merge')
for interrupt in [0,5,6,8]:
 for stop in [0,1,255]:
  for callbacks in [0,2,3,4]:
   scripts,p,c=script_list(1,handlers=3);s=scripts[0]
   arg=ENTRIES+4 if callbacks==4 else EVENTS;val=0xc377c572 if callbacks==4 else 1 if callbacks==2 else 0
   p += [patch(s+0xe4,'<I',interrupt),patch(EVENTS+9,'<B',stop),patch(ENTRIES+16,'<I',1),patch(CALLBACK+8,'<3I',callbacks,arg,val)]
   case([call(0x460470,EVENT,s,this=EVENTS)],p,c,'interrupt handler mutations and nested stop state')
for mode,arg,val in [(2,EVENTS,255),(3,EVENTS,0),(4,EVENTS+4,0),(4,ENTRIES+4,0xc377c572),(4,ENTRIES+20+4,0xc377c572),(4,ENTRIES+20,EV+1)]:
 for active in [0,2]:
  scripts,p,c=script_list(1,handlers=3);s=scripts[0];p += [patch(CALLBACK+8,'<3I',mode,arg,val),patch(EVENTS+12,'<I',active)]
  case([call(0x460470,EVENT,s,this=EVENTS)],p,c,'handler disables table entries or iteration')
for alive in [0,1]:
 for count in [0,1,0xffffffff,0x80000000]:
  case([call(0x460470,EVENT,SCRIPT,this=EVENTS)],[patch(EVENTS+4,'<IB',count,alive),patch(ENTRIES,'<I',EV+1)],label='signed table count and nonmatching dead table')
# A nested table delivery shares active-call count and preserves prior stop state.
for stop in [0,1,255]:
 scripts,p,c=script_list(1,handlers=2);s=scripts[0];p += [patch(EVENTS+9,'<B',stop),patch(CALLBACK+8,'<3I',6,EVENTS,0)]
 case([call(0x460470,EVENT,s,this=EVENTS)],p,c,'reentrant delivery on same table')
# Direct receivers and object dispatch can handle, redirect, mutate or take
# ownership of parameters. Receiver next is read after its callback.
for target in [WILDCARD,1,2]:
 for receivers in [0,RECEIVERS]:
  for mode,value in [(0,0),(1,1),(1,2),(1,0xffffffff),(2,WILDCARD),(2,2),(3,0),(3,RECEIVERS+64),(4,EV+1),(5,VALUES)]:
   p=[patch(EM+20,'<I',receivers),patch(CALLBACK+52,'<5I',mode,value,2,WILDCARD,VALUES)]
   case([call(0x462f00,EV,target,1,0,0,bits(-1),this=EM)],p,label='receivers object target mutation and ownership')
for mode in [0,1,2,5]:
 case([call(0x4a1090,EVENT,this=RECEIVERS)],[patch(CALLBACK+52,'<2I',mode,2 if mode!=5 else VALUES)],label='receiver virtual thunk')
for params in [0,VALUES]:
 for id_ in [1,2,WILDCARD]:
  case([call(0x4609f0,EV,params,this=OWNER)],[patch(OWNER+0x14,'<I',id_)],label='owner event identity wrapper')
for flag in [0,1,2]:
 scripts,p,c=script_list(2,handlers=flag)
 case([call(0x462f00,EV,0x201,1,VALUES,0,bits(-1),this=EM)],p,c,'direct spawned user-value delivery')
# Broadcast fast and snapshot paths, radius boundaries, unowned/nonspatial
# listeners, repeated scripts, and a missing subscription.
for count in [0,1,2,4]:
 for radius in [bits(-1),bits(0),bits(1),bits(5),bits(5)+1,bits(float('inf')),0x7fc12345,0x7fa12345]:
  for owner in [0,OTHER]:
   for spatial in [0,0x20]:
    scripts,p,c=script_list(count,handlers=1,owner=owner);p+=subscribe(scripts)+[patch(OTHER+8,'<I',spatial),patch(OTHER+0x4c,'<4f',3,4,0,1)]
    case([call(0x462f00,EV,WILDCARD,1,0,1,radius,this=EM)],p,c,'broadcast count radius and owner flags')
for flag in [0,1,256,257,0xffffffff]:
 for missing in [0,1]:
  scripts,p,c=script_list(2,handlers=1);p+=subscribe(scripts)
  case([call(0x462f00,EV+missing,WILDCARD,1,0,flag,bits(-1),this=EM)],p,c,'broadcast low-byte and absent listener list')
for duplicates in [[0,0],[0,1,0],[1,1,0,1]]:
 scripts,p,c=script_list(2,handlers=1);p+=subscribe([scripts[i] for i in duplicates])
 case([call(0x462f00,EV,WILDCARD,1,VALUES,1,bits(-1),this=EM)],p,c,'duplicate snapshot references')
# Real deletion during delivery: self, next or last. The original destructor
# unsubscribes, retires the in-flight table and clears pending snapshot references.
for count in [1,2,4]:
 for which in [0,count-1]:
  scripts,p,c=script_list(count,handlers=2);p+=subscribe(scripts)
  p += [patch(CALLBACK+8,'<3I',5,scripts[which],0)]
  case([call(0x462f00,EV,WILDCARD,1,VALUES,1,bits(-1),this=EM)],p,c,'recipient deletion during actual broadcast execution')
# Earlier recipients can change later owners' spatial state or even source
# position; radius uses the source position captured before callbacks.
for address,value in [(OTHER+8,0),(OTHER+0x4c,bits(100)),(OWNER+0x4c,bits(100))]:
 scripts,p,c=script_list(2,handlers=1,owner=OTHER);p+=subscribe(scripts)
 p += [patch(CALLBACK+8,'<3I',4,address,value),patch(OTHER+0x4c,'<4f',1,0,0,1)]
 case([call(0x462f00,EV,WILDCARD,1,0,1,bits(5),this=EM)],p,c,'broadcast mutations and captured source position')
# Waiters match the original event/target, even after receiver mutation. Missing
# serials are cleared; processing stops after the first live script wakes.
for target in [1,WILDCARD,0x200]:
 for broadcast in [0,1]:
  for waiter_target in [0,1,2,WILDCARD,0x200]:
   for live in [0,1,39]:
    scripts,p,c=script_list(2);p += [patch(EM+20,'<I',RECEIVERS),patch(CALLBACK+52,'<5I',4,EV+1,2,WILDCARD,0)]
    for i in range(40):p.append(patch(WAITERS+i*12,'<3I',100 if i==live else 999,EV,waiter_target))
    p += [patch(scripts[0]+0xa4,'<I',11),patch(scripts[0]+0x98,'<I',99)]
    case([call(0x462f00,EV,target,1,0,broadcast,bits(-1),this=EM)],p,c,'waiter matching clearing missing serials and first wake')
# Nested broadcasts and nested receiver events preserve manager/log depth and
# consume source-script context only in the outer entry.
for mode in [6,7]:
 scripts,p,c=script_list(2,handlers=1);p+=subscribe(scripts)
 if mode==6:p += [patch(EM+20,'<I',RECEIVERS),patch(CALLBACK+52,'<4I',6,EV+1,WILDCARD,1)]
 else:p += [patch(CALLBACK+8,'<6I',7,EV,WILDCARD,1,0,1)]
 case([call(0x462f00,EV,WILDCARD,1,0,0 if mode==6 else 1,bits(-1),this=EM)],p,c,'nested manager event dispatch')
# Relocate actual pointer fields, including reference vtables captured by frees.
for i in range((HEAP-LOG)//48):fields.update(LOG+i*48+j for j in [16,20,24,28,40])
for c in oracle.cases:
 for at,data in c['patches']:
  data=bytes.fromhex(data)
  for j in range(0,len(data)-3,4):
   if int.from_bytes(data[j:j+4],'little') in exports:fields.add(at+j)
scope='Twenty-one original event-delivery and supporting routines: full direct/receiver/spawned/broadcast delivery; one-recipient fast path and reference-protected snapshots; radius filtering; wait wake-up and saved frames; parameter merging, immediate/spawned/replacement/interrupt handlers; nested callbacks, actual recipient destruction and table retirement; event ownership, logging/ring/name initialization and diagnostics; scalar dispatch, structure pools, reference lifecycle, ID searches, named setup and squared distance. Existing executor/cache/destructor/unsubscription functions execute unchanged. Configured native/virtual handlers, output and generic heap are instrumented boundaries, not recovered gameplay commands. Every fixture/global/output byte and callback/heap order is compared with pointer relocation; only returned arithmetic NaNs compare by classification. Valid initialized internal state, successful allocations and terminating scripts are required. Names fit the original fixed log storage. Integrated executor cases use disabled value pools; standalone structure-free cases also cover both fixed pools. Registration/startup, actual native gameplay handlers, movement/rendering integration and a playable level remain unfinished.'
imports=['thug_script_delete_spawned','thug_script_events_deliver','thug_event_emit']
fixture={'base':BASE,'memory':'event-delivery-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_command_callbacks',
 'pointer_symbols':symbols,'pointer_exports':list(exports.items()),'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],
 'native_callbacks':[{'module':'event-delivery-callbacks.wasm','export':'fixture_delivery_'+n,'original':at,'engine_imports':imports} for n,at in [('native',NATIVE),('receiver',RECEIVE),('object',OBJECT_FN)]]+
 [{'module':'event-delivery-callbacks.wasm','export':'fixture_delivery_print','slots':[PRINT+4],'engine_imports':imports}]}
path=out/'event-delivery-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
adapter=out/'event-delivery-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--allow-undefined,--global-base=58720256',str(ROOT/'tools/event_delivery_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_event_delivery_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'event-delivery-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
