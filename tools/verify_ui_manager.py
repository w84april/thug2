"""Compare UI manager lifetime, subscriptions, actual event delivery and deletion."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ECX
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'ui-manager.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'ui-registry-fixtures.json').read_text());BASE,SIZE=prior['base'],0x90000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
OBJ,REF,OWNED,LOG,HEAP=[BASE+x for x in [0x10000,0x16000,0x18000,0x20000,0x30000]]
EM,TABLES,SCRIPTS,FRAMES,CACHE,SYMBOLS,NAMES=[BASE+x for x in [0x60000,0x6c000,0x70000,0x72000,0x73000,0x78000,0x7c000]]
PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE=[TABLES+i*256 for i in range(5)]
UM,UM2,R,EVENT,PARAMS,PADSYM,PADARRAY,INPUT,TEXT,EVENTS,ENTRIES,SERVICES=[BASE+x for x in [0x80000,0x81000,0x81800,0x82000,0x82100,0x83000,0x83100,0x83400,0x83600,0x83800,0x83900,0x83a00]]
EV,WILDCARD=0x1234,0x36b2ee74
crc=lambda s:zlib.crc32(s.encode())^0xffffffff

def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT+20,'<I',BASE+SIZE)
for at,n in [(UM,0x6a4),(UM2,0x6a4),(R,128),(PARAMS,128),(INPUT,0x140),(EVENTS,256),(ENTRIES,256)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(UM,'<6I',0x64a0e8,0x647814,0xffffffff,0,UM+4,UM+4)
put(UM+0x28,'<7I',0x64a104,0,0,0,0,1,0);put(UM+0x5dc,'<I',EV);put(UM+0x69c,'<I',1);put(EM+0x14,'<I',UM+0x28)
for i in range(3):put(R+32*i,'<7I',0x6477d8,0,0,0,0,0,0)
for i in range(8):
 at=OBJ+i*512;put(at+8,'<I',0x10400);put(at,'<I',0x64a090)
put(EVENT,'<5I',EV,0x5678,WILDCARD,0,0)
put(SYMBOLS+(crc('pad_event_types')&0xfff)*4,'<I',PADSYM)
put(PADSYM,'<BBHIIII',0,12,0,crc('pad_event_types'),0,PADARRAY,0)
put(PADARRAY,'<BBHII',0,13,0,3,PADARRAY+16);put(PADARRAY+16,'<3I',EV,EV+1,EV+2)
memory[TEXT-BASE:TEXT-BASE+16]=b'pad_event_types\0'
put(INPUT+0x110,'<8I',7,8,9,10,0xffffffff,0x80000000,0,4)
put(SERVICES,'<2I',0,ADAPTER)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
index[0x696d40]=len(globals_);globals_.append(['thug_input_manager',0x696d40,4,0]);defaults.append(INPUT)
functions={}
def bind(at,name,argc=0,result='void',heap=False,diag=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
for at,name in [(0x45faa0,'thug_event_receiver_initialize'),(0x4ab990,'thug_ui_manager_initialize')]:bind(at,name,result='word')
for at,name in [(0x45fac0,'thug_event_receiver_destroy'),(0x4abb00,'thug_ui_manager_destroy')]:bind(at,name)
for at,name in [(0x460170,'thug_event_receiver_delete'),(0x4acb40,'thug_ui_manager_delete')]:bind(at,name,1,'word',True)
for at,name,argc in [(0x45fb30,'thug_event_receiver_set_owner',1),(0x461fe0,'thug_event_receiver_register',1),(0x462000,'thug_event_receiver_unregister',1),(0x4ab250,'thug_ui_manager_subscribe',2),(0x4ab330,'thug_ui_manager_detach_subscriptions',3),(0x4ab4d0,'thug_ui_manager_reenable',1),(0x4abbe0,'thug_ui_manager_attach',3),(0x473be0,'thug_script_detach_owner',1)]:bind(at,name,argc)
bind(0x4aaff0,'thug_ui_manager_remove',1,heap=True)
bind(0x4ab7c0,'thug_ui_manager_matches_focus',1,'byte')
bind(0x4ac400,'thug_ui_manager_delete_tree',3,heap=True,diag=True)
bind(0x4ad100,'thug_ui_manager_delete_id',4,heap=True,diag=True)
bind(0x4abd40,'thug_ui_manager_receive_event',1,heap=True,diag=True)
bind(0x461140,'thug_ui_object_receive_event',1,'byte',True,True)
bind(0x4a8f00,'thug_ui_is_input_disabled',result='byte')
bind(0x4a86c0,'thug_ui_owner',result='word')
bind(0x45f9e0,'thug_ui_event_controller_index',1,'word',this=False)
bind(0x45f980,'thug_event_stop_propagation',2,heap=True)
bind(0x462b40,'thug_event_record_stopped',3,heap=True)
bind(0x479090,'thug_script_get_global_array_text',2,'word',this=False)
bind(0x44e630,'thug_input_device_id',1,'word')
new_functions=list(functions)
for at in [0x41d1d0,0x461a00,0x4a8f90,0x461930,0x4aa8e0,0x4b0920,0x4b3fd0]:functions[hex(at)]=prior['functions'][hex(at)]
bind(0x4a8940,'thug_ui_set_events_enabled',1,heap=True,diag=True)
bind(0x462f00,'thug_event_emit',6,'byte',True,True);functions['0x462f00']['float_args']=[5]
observe=[int(k,16) for k in functions]+[0x473800,0x460470,0x474540,0x4748e0,0x473a80,0x4a1090,0x45f9b0,0x4627c0,0x4aac90,0x4b2030,0x4756f0,0x4637c0,0x4637e0]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,scope_entries={ALLOCATOR+0x200:6})
fields=set(prior['pointer_fields'])|{UM,UM+4,UM+0x28,UM2,UM2+4,UM2+0x28,R,R+32,R+64}
for i in range(8):fields.update([OBJ+i*512,OBJ+i*512+0x28,OBJ+i*512+0x40,SCRIPTS+i*256+0xec])
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
exports=prior['pointer_exports']+[[0x6477d8,'thug_event_receiver_methods'],[0x64a0e8,'thug_ui_manager_methods'],[0x64a104,'thug_ui_manager_receiver_methods']]
labels=[];branches=Counter()
branch_at={0x4ab2a6:'existing_subscription',0x4ab29f:'subscription_capacity',0x4ac040:'subscription_dispatch_pass',0x4ac0f6:'forwarded_handled',0x4ac0cb:'next_subscription',0x4abda8:'pad_types_ready',0x4abf11:'special_disable_path'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([0] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='UI manager'):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%40==0:print('Original UI manager cases:',len(labels),flush=True)
 return stages

def refs(n=8):return [call(0x41d1d0,REF+i*16,[OBJ+i*512]) for i in range(n)]
def register(n=8):return [call(0x461a00,UM,[OBJ+i*512]) for i in range(n)]
def parents():return [call(0x4aa8e0,OBJ+i*512,[REF+p*16,0]) for i,p in [(1,0),(2,0),(3,1),(4,1),(5,2),(6,3)]]
def subscribe(n=8,controller=0):return [call(0x4ab250,UM,[REF+i*16,controller]) for i in range(n)]
def emit(name,target=WILDCARD,params=0):return call(0x462f00,EM,[name,target,0x5678,params,0,0xbf800000])
rng=random.Random(0x4ab990)
# Poisoned constructors and real base/derived teardown, including live references.
for fill in [0,0xa5,0xff,None]:
 for head in [0,UM+0x28]:
  data=bytes([fill])*0x6a4 if fill is not None else bytes(rng.getrandbits(8) for _ in range(0x6a4))
  case([call(0x4ab990,UM2),call(0x4abb00,UM2)],[raw(UM2,data),patch(EM+0x14,'<I',head)],label='derived manager poisoned constructor and destructor')
  case([call(0x45faa0,R)]*2,[raw(R,data[:28])],label='receiver constructor preserves next link and padding')
for flags in [0,1,2,256,257,0xffffffff]:
 calls=refs()+subscribe()+[call(0x41d1d0,UM+0x44,[OBJ]),call(0x41d1d0,UM+0x50,[OBJ+512])]
 calls += [call(0x41d1d0,UM+0x4ec+i*24,[OBJ+(i%8)*512]) for i in range(10)]
 case(calls+[call(0x4acb40,UM,[flags])],label='derived teardown clears every reference in reverse member order')
 case([call(0x45fb30,R,[OBJ]),call(0x45fb30,R+32,[OBJ]),call(0x460170,R,[flags]),call(0x45fac0,R+32)],label='receiver deletion unregisters middle or first entry')
for owner in [0,OBJ]:
 for target in [R,R+32,R+64]:
  case([call(0x45fb30,R,[owner]),call(0x461fe0,EM,[R+32]),call(0x462000,EM,[target]),call(0x462000,EM,[target])],label='receiver list removal retains next and clears only active low byte')
# Original cross-controller tail retention, duplicate reenabling, full capacity.
for controller in [0,1]:
 for count in [0,1,2,8]:
  calls=refs()+subscribe(count,controller)+subscribe(count,controller^1)+subscribe(count,controller)
  case(calls,label='controller list tail and duplicate registration')
p=[patch(UM+0x5c+i*24,'<I',OBJ+(i%8)*512) for i in range(48)]
case(refs()+[call(0x4ab250,UM,[REF,0])],p,label='48 occupied subscription slots preserve state')
for ancestors in [0,1,256,257]:
 for disable in [0,1,256,257]:
  for target in [0,1,3,7]:
   case(refs()+parents()+subscribe()+[call(0x4ab330,UM,[REF+target*16,ancestors,disable]),call(0x4ab4d0,UM,[REF+target*16])],label='subtree subscription detach disable and reenable')
# Attachment changes root using real references and removes descendant subscriptions.
for root in [0,OBJ,OBJ+512,OBJ+7*512]:
 for child,parent in [(1,2),(2,7),(3,2),(6,7)]:
  calls=refs()+parents()+subscribe()+[call(0x41d1d0,UM+0x44,[root]),call(0x4abbe0,UM,[REF+parent*16,REF+child*16,1])]
  case(calls,label='attach propagates root and clears subtree subscriptions')
for root in [0,OBJ,OBJ+512,OBJ+7*512]:
 for target in [0,1,7]:
  case(refs()+register()+parents()+[call(0x41d1d0,UM+0x44,[root]),call(0x4aaff0,UM,[OBJ+target*512])],label='derived removal selects parentless root in reverse queue order')
for count in [0,1,3,16]:
 for target in [0,OBJ,OBJ+512]:
  p=[raw(SCRIPTS,bytes(244)),raw(FRAMES,bytes(768)),patch(SCRIPTS+0x30,'<I',count),patch(SCRIPTS+0x94,'<I',FRAMES),patch(SCRIPTS+0xa4,'<I',3)]
  p += [patch(FRAMES+i*48+12,'<I',OBJ if i%2 else OBJ+512) for i in range(count)]
  case([call(0x41d1d0,SCRIPTS+0xbc,[OBJ]),call(0x473be0,SCRIPTS,[target])],p,label='caller owner detach preserves unrelated current and saved owners')
for owner in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 for active in [0,1,255]:
  p=[patch(OBJ+0x174,'<I',owner)]+[patch(UM+0x4ec+i*24+16,'<IB',owner if i==9 else i,active) for i in range(10)]
  case(register(1)+[call(0x4a86c0,OBJ),call(0x4ab7c0,UM,[0x100])],p,label='unsigned focus priority selection including final record')
for disabled in [-1,0,1,3,6]:
 p=[] if disabled<0 else [patch(OBJ+disabled*512+8,'<I',0x200000)]
 case(refs()+parents()+[call(0x4a8f00,OBJ+i*512) for i in range(8)],p,label='input-disabled status inherited over full tree')
for slot in range(8):case([call(0x44e630,INPUT,[slot])],label='stored input-device slots')
for tag in [0,12,13]:
 case([call(0x479090,args=[TEXT,1])],[patch(PADSYM+1,'<B',tag)],label='global pad event array text lookup')
for params,value in [(0,0),(PARAMS,0),(PARAMS,1),(PARAMS,0xffffffff)]:
 p=[patch(EVENT+16,'<I',params),patch(PARAMS,'<2I',0,PARAMS+16),patch(PARAMS+16,'<BBHIII',2,0,0,0xb30d9965,value,0)]
 case([call(0x45f9e0,args=[EVENT])],p,label='controller parameter integer and default')
for flags in [0,1,2,0xabcdef00]:
 case([call(0x462b40,EM,[EVENT,7,9]),call(0x45f980,EVENT,[5,6])],[patch(EVENT+12,'<I',flags)],label='stop log phase precedes flag mutation')
# Actual receiver, global and direct object virtual methods; no callback substitutes.
for lazy in [False,True]:
 for name in [EV,EV+9,0x9d3fb516,0x4adf0cd3,0x4a57316b,0x3056434f]:
  for target in [WILDCARD,0x100,0x101]:
   p=[patch(EVENT,'<3I',name,0x5678,target),patch(UM+0x69c,'<I',0 if lazy else 1)]
   case(refs()+register()+parents()+subscribe()+[call(0x4abd40,UM+0x28,[EVENT])],p,label='actual UI receiver specials and nested pad forwarding')
for device in [0,7,8]:
 for filter_ in [0,1]:
  for gated in [0,1]:
   p=[patch(UM+0x6a0,'<B',filter_),patch(UM+0x4e8,'<I',gated),patch(EVENT+16,'<I',PARAMS),patch(PARAMS,'<2I',0,PARAMS+16),patch(PARAMS+16,'<BBHIII',2,0,0,0xc9428a08,device,0)]
   case(refs()+register()+parents()+subscribe()+[call(0x4abd40,UM+0x28,[EVENT]),emit(EV,params=PARAMS)],p,label='device filter and owner focus gating in full dispatcher')
# Wake real current/saved script waits, including the no-script fast path.
for count in [1,2,8]:
 for controller in [0,1]:
  p=[patch(UM+0x5dc,'<I',0x4adf0cd3),patch(PARAMS,'<2I',0,PARAMS+16),patch(PARAMS+16,'<BBHIII',2,0,0,0xb30d9965,controller,0)]
  case(refs()+register()+subscribe(count,controller)+[emit(0x4adf0cd3,params=PARAMS)],p,label='real nested receiver removal dirties and restarts the active subscription list')
for focus_count in [0,1,0x80000000]:
 for owner in [0,7,0x80000000,0xffffffff]:
  for priority in [0,7,0x80000000,0xffffffff]:
   p=[patch(UM+0x4e8,'<I',focus_count),patch(UM+0x4ec+9*24+16,'<IB',priority,1),patch(OBJ+8,'<I',0x10010400),patch(OBJ+0x174,'<I',owner)]
   case(refs()+register()+parents()+subscribe()+[emit(EV)],p,label='focus-gated forwarding with inherited owner and unsigned maximum priority')
for script in [0,SCRIPTS]:
 for wait in [0,3,19]:
  p=[raw(SCRIPTS,bytes(244)),patch(OBJ+16,'<I',script),patch(SCRIPTS+0xa4,'<2I',wait,EV),patch(SCRIPTS+0x30,'<I',3),patch(SCRIPTS+0x94,'<I',FRAMES),raw(FRAMES,bytes(144))]
  p += [patch(FRAMES+i*48+32,'<I',EV+i%2) for i in range(3)]+[patch(FRAMES+i*48+40,'<I',0xabcde003) for i in range(3)]
  case([call(0x461140,OBJ,[EVENT])]*2,p,label='actual object receive protects lifetime and wakes saved waits')
# Cached return-only QB handlers execute through original object virtual dispatch.
for receiver_call in [True,False]:
 for controller in [0,1]:
  p=[raw(SCRIPTS,bytes(244)),patch(OBJ+16,'<I',SCRIPTS),patch(SCRIPTS+0x2c,'<I',SCRIPTS+0x1c),patch(SCRIPTS+0x94,'<I',SCRIPTS+0x34),patch(SCRIPTS+0xe0,'<I',EVENTS),patch(SCRIPTS+0xec,'<I',0x6478e4),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',EV,5,0,0,0),patch(CACHETABLE+8,'<I',1),patch(CACHETABLE+32+12,'<3I',5,CACHE+128,0),patch(CACHE+128,'<5I',5,CACHE+192,1,0,0),raw(CACHE+192,b'\x01\x24'),patch(EVENT+16,'<I',PARAMS),patch(PARAMS,'<2I',0,PARAMS+16),patch(PARAMS+16,'<BBHIII',2,0,0,0xb30d9965,controller,0)]
  calls=refs()+register()+subscribe(1,controller)
  calls += [call(0x4abd40,UM+0x28,[EVENT])] if receiver_call else [emit(EV,params=PARAMS)]
  case(calls,p,label='pad forwarding invokes real immediate QB handler and propagates handled flag')
# Recursive deletion with a live receiver exercises disable/enable events and
# both parent and child cleanup. Optional caller is independently owned.
for recursive in [0,1]:
 for keep in [0,1,256]:
  for target in [0,1,3,7]:
   for caller in [0,SCRIPTS]:
    p=[raw(SCRIPTS,bytes(244)),patch(SCRIPTS+0x30,'<I',3),patch(SCRIPTS+0x94,'<I',FRAMES),patch(SCRIPTS+0xa4,'<I',3),raw(FRAMES,bytes(144))]
    p += [patch(OBJ+i*512+8,'<I',0x14400) for i in range(8)]
    p += [patch(FRAMES+i*48+12,'<I',OBJ+target*512) for i in range(3)]
    calls=refs()+register()+parents()+subscribe()+[call(0x41d1d0,UM+0x44,[OBJ]),call(0x41d1d0,SCRIPTS+0xbc,[OBJ+target*512]),call(0x4ad100,UM,[0x100+target,recursive,keep,caller])]
    case(calls,p,label='real tree deletion events references registry removal and caller detach')
for keep in [0,1]:
 case(refs()+register()+parents()+subscribe()+[call(0x4ac400,UM,[keep,REF,0])],[patch(OBJ+8,'<I',0x14400)],label='direct recursive deletion retains only selected widget')
# Full freshly constructed widget, registry, receiver and delete lifecycle.
case([call(0x4a8f90,OBJ),call(0x461930,OBJ,[0x100]),call(0x461a00,UM,[OBJ]),call(0x41d1d0,REF,[OBJ]),call(0x4ab250,UM,[REF,0]),call(0x4a8940,OBJ,[1]),emit(EV),call(0x4ad100,UM,[0x100,1,0,0]),call(0x4abb00,UM)],label='complete constructed UI lifetime with actual events')
scope='Twenty-seven original routines recover the derived UI manager, controller subscription and focus routing, recursive widget deletion, caller-owner detach, original object event receipt and receiver registration/lifetime. Full dispatcher and actual cached QB handlers execute; no gameplay callbacks are substituted. Arena/globals/returns and heap/scope snapshots compare exactly. Nested virtual calls preserve a scoped platform service binding. Generic allocation is adapted; valid initialized acyclic graphs, registered targets, controller indices 0..1, pad arrays <=48 and successful allocations retain original contracts. Other UI methods, multiline score update, rendering and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'ui-manager-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'substituted_gameplay_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES}}
path=out/'ui-manager-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),'new functions',len(new_functions),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_ui_manager_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
