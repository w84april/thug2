"""Original script destruction, ownership stopping and execute/copy/dispose chains."""
import hashlib,json,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-lifetime.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-execute-fixtures.json').read_text());BASE=prior['base'];SIZE=0x100000
memory=bytearray((out/prior['memory']).read_bytes()[:SIZE])
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
SCRIPT,PARAMS,ARGS,RETURNS,FRAMES,OWNER,OTHER=BASE+0x5800,BASE+0x5a00,BASE+0x5a10,BASE+0x5a20,BASE+0x6800,BASE+0x8000,BASE+0x8200
OBJECTS,PROGRAM,CALLBACK,PRINT,LOG,HEAP=BASE+0x9200,BASE+0x40000,BASE+0x30000,BASE+0x35f00,BASE+0x60000,BASE+0x80000
TARGET,REFS,FOREIGN,EVENTS,ENTRIES,COMPLETION=BASE+0x20000,BASE+0x20100,BASE+0x20500,BASE+0x21000,BASE+0x21020,BASE+0x21800
POOL0,POOL1,BLOCK0,BLOCK1,SCRIPTS,BRANCHES=BASE+0x22000,BASE+0x22100,BASE+0x22400,BASE+0x22800,BASE+0x24000,BASE+0x26000
TABLE,BUCKETS,SENTINEL,NODES=BASE+0x27000,BASE+0x27100,BASE+0x27200,BASE+0x27400
NATIVE=0x3f01000

def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(n):return struct.pack('<I',n&0xffffffff)
def name(n):return b'\x16'+word(n)
def number(n):return b'\x17'+word(n)
def assign(n,v):return name(n)+b'\x07'+v
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,SCRIPT+0xec,0)
put(TARGET,'<2I',0xdeadbeef,0);put(FOREIGN,'<2I',0xdeadbeef,0)
for p,block in [(POOL0,BLOCK0),(POOL1,BLOCK1)]:
 put(p,'<6I',block,block+0x400,0xaaaa,0xbbbb,0,block);put(p+0x58,'<I',0)
 put(block,'<I',block+0x100);put(block+0x100,'<I',0)
put(EVENTS,'<IIB3xI',ENTRIES,3,1,0)
for i in range(4):
 p=COMPLETION+i*0x60;c=p+8;t=p+32
 put(p,'<2I',0xabcdef01,c);put(c,'<BBHIII',7,0x75,0x9876,100+i,t,0)
 data=b'owned lifetime '+str(i).encode()+b'\0';memory[t-BASE:t-BASE+len(data)]=data
 if i<3:put(ENTRIES+i*20,'<5I',1 if i!=1 else 9,0x1234+i,i,p,0xeeee0000+i)
put(OBJECTS+16,'<I',TABLE);put(TABLE,'<6I',2,BUCKETS,0,0xffffffff,0,0)
memory[BUCKETS-BASE:BUCKETS-BASE+48]=bytes(48)
for i in range(6):
 s=SCRIPTS+i*0x100;memory[s-BASE:s-BASE+244]=bytes(244)
 put(s+0x2c,'<I',s+0x1c);put(s+0x94,'<I',s+0x34)
for i in range(4):
 b=BRANCHES+i*96;memory[b-BASE:b-BASE+96]=b'\xad'*96
 put(b,'<I',SCRIPT if i%2 else OTHER);put(b+88,'<2I',b+96 if i<3 else 0,b-96 if i else 0)
# Keep genuine cached scripts and native binding from the executor fixture.
initial=bytes(memory);(out/'script-lifetime-memory.bin').write_bytes(initial)
globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:]
for export,address,width,value,offset in [
 ('thug_script_pool_index',0x6f3548,4,0,0),('thug_script_pools',0x6f3550,4,0,0),('thug_script_pools',0x6f3554,4,0,4),
 ('thug_script_updating',0x6f3544,1,0,0),('thug_script_stop_pending',0x6f3545,1,0,0)]:
 globals_.append([export,address,width,offset]);defaults.append(value)
index={g[1]:i for i,g in enumerate(globals_)}
for at,value in [(0x6f3538,SCRIPT),(0x6f353c,1),(0x6f3530,0),(0x6f2358,BRANCHES),(0x6f235c,BRANCHES+288),(0x6f2360,4)]:defaults[index[at]]=value
functions={}
def bind(at,n,argc=0,this=True,heap=True,result='void',diag=False):
 f={'name':n,'this':this,'memory':heap,'result':result,'cleanup':argc*4 if this else 0}
 if diag:f.update(stack_args=list(range(argc)),diagnostics=True)
 functions[hex(at)]=f
bind(0x463820,'thug_object_references_clear',heap=False)
bind(0x463870,'thug_reference_target_destroy',heap=False)
bind(0x463880,'thug_reference_target_delete',1,result='word')
bind(0x46f870,'thug_script_branch_detach',1,False,False)
bind(0x45fb70,'thug_script_events_destroy')
bind(0x449970,'thug_script_allocate',1,False,True,'word')
bind(0x4499b0,'thug_script_free',1,False)
bind(0x474420,'thug_script_destroy',diag=True)
bind(0x4752f0,'thug_script_run_collect',4,False,diag=True)
bind(0x4753c0,'thug_script_stop_spawned',0,False,diag=True)
bind(0x4756c0,'thug_script_delete_spawned',1,False,diag=True)
bind(0x475700,'thug_script_collect_finished',0,False,diag=True)
bind(0x4742b0,'thug_script_stop_owner',2,False,diag=True)
bind(0x474350,'thug_script_stop_owner_stack',2,False,diag=True)
bind(0x4756f0,'thug_script_stop_all_for_owner',1,False,diag=True)
# Existing initialization is exercised before complete destruction and list sweeps.
bind(0x4738e0,'thug_script_initialize',heap=False,result='word')
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=10000000,
 observe=[int(k,16) for k in functions]+[0x5ba3b0,0x5ba3d0,0x5ba400,0x473a80,0x473010,0x4750b0,0x474540,0x478480,0x475e80,0x475d60,0x473880,0x477130,0x462b90],scope_entries={BASE+0x6000:1,MANAGER+0x300:2})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.cpu.mem_map(NATIVE,4096)
def callback(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
 first=oracle.word(params+4) if params else 0;count=oracle.word(CALLBACK)
 cpu.mem_write(CALLBACK+32+count*40,struct.pack('<10I',0,0,0,params,script,first,oracle.word(first+4) if first else 0,oracle.word(first+8) if first else 0,oracle.word(script+12),oracle.word(script+200)))
 oracle.setword(CALLBACK,count+1);mode=oracle.word(CALLBACK+8);v=oracle.word(CALLBACK+12)
 if mode==1:oracle.setword(script+164,1);oracle.setword(script+152,v)
 if mode==2:oracle.setword(script+12,0)
 if mode==3 and first:oracle.setword(first+8,oracle.word(first+8)^v)
 if mode==4:oracle.setword(script+232,v)
 if mode==5:oracle.setword(script+12,v)
 if mode==6:
  next_=oracle.word(script);oracle.setword(v,next_);oracle.setword(v+4,script)
  if next_:oracle.setword(next_+4,v)
  oracle.setword(script,v)
 cpu.reg_write(UC_X86_REG_EAX,oracle.word(CALLBACK+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=NATIVE,end=NATIVE)
labels=[]
def call(at,*args,this=SCRIPT):return (at,this,list(args)+([PRINT] if functions[hex(at)].get('diagnostics') else []))
def case(calls,patches=(),changes=None,label='synthetic'):
 labels.append(label);stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});commands=0
 for step in stages:
  prior_count=commands
  for at,data in step['outputs']:
   if at==CALLBACK:commands=int.from_bytes(bytes.fromhex(data),'little')
  step['callbacks']=commands-prior_count
 return stages
# Owned/unowned reference nodes, foreign ownership, and untouched null-node links.
def references(target,count,unowned=(),foreign=()):
 p=[patch(target+4,'<I',REFS if count else 0),patch(FOREIGN+4,'<I',REFS if count else 0)]
 for i in range(count):p.append(patch(REFS+i*12,'<3I',0 if i in unowned else FOREIGN if i in foreign else target,REFS+(i-1)*12 if i else 0,REFS+(i+1)*12 if i<count-1 else 0))
 return p
for length in [0,1,2,6]:
 for layout in range(4):
  patches=references(TARGET,length,range(length) if layout==1 else [0] if layout==2 else [],range(length) if layout==3 else [])
  for at in [0x463820,0x463870,0x463880]:
   for flags in ([0] if at!=0x463880 else [0,1,2,255,256,257]):
    case([call(at,*([flags] if at==0x463880 else []),this=TARGET)],patches,label='reference graph destruction')
for target in [0,SCRIPT,OTHER,SCRIPTS]:case([call(0x46f870,target,this=0)]*2,label='branch ownership detach')
# Pool exhaustion and range-based selected/alternate release; no fallback on empty pool.
for selected in [0,1]:
 for pools in [(0,0),(POOL0,0),(0,POOL1),(POOL0,POOL1),(POOL0,POOL0)]:
  changes={0x6f3548:selected,0x6f3550:pools[0],0x6f3554:pools[1]}
  for size in [0,4,244,256]:case([call(0x449970,size,this=0)]*3,changes=changes,label='script allocation pools and exhaustion')
  for pointer in [0,BLOCK0-4,BLOCK0,BLOCK0+4,BLOCK0+0x400,BLOCK1,BLOCK1+0x400,TARGET]:
   case([call(0x4499b0,pointer,this=0)],changes=changes,label='script pool release membership')
for entries in [0,ENTRIES]:
 for count in [0,1,3,0xffffffff,0x80000000]:
  case([call(0x45fb70,this=EVENTS)],[patch(EVENTS,'<2I',entries,count)],label='event table owned data disposal')
# Real listener removals during script destruction, including duplicate listeners.
def subscriptions(script):
 return [patch(TABLE+8,'<I',1),patch(BUCKETS+12,'<3I',1,SENTINEL,0),
  patch(SENTINEL,'<5I',0x6478dc,0xffffffff,0,SENTINEL+20,NODES),
  patch(SENTINEL+20,'<5I',0x6478d8,script,0,NODES,SENTINEL),
  patch(NODES,'<5I',0x6478d8,script,0,SENTINEL,SENTINEL+20)]
def chain(size):
 scripts=[SCRIPT]+[SCRIPTS+i*256 for i in range(size-1)];p=[]
 for i,s in enumerate(scripts):p.append(patch(s,'<2I',scripts[i+1] if i+1<size else 0,scripts[i-1] if i else 0))
 return scripts,p
for size in [1,3,6]:
 scripts,links=chain(size)
 for target in scripts:
  for event_state in [0,1,2]:
   for completion in [0,COMPLETION+3*0x60]:
    patches=links+[patch(target+0xe0,'<I',EVENTS if event_state else 0),patch(EVENTS+12,'<I',event_state-1 if event_state else 0),patch(target+0xdc,'<I',completion),patch(target+0xcc,'<B',0x10)]
    patches+=subscriptions(target)+references(target+0xec,3)
    case([call(0x474420,this=target)],patches,{0x6f353c:size},'whole script destruction')
# The destructor runs deferred script bodies before releasing arguments and owner links.
for deferred in [5,6,7,8]:
 case([call(0x474420)],[patch(SCRIPT+0xe8,'<I',deferred)],label='deferred execution during destruction')
# End-to-end allocate/construct/setup/execute/copy/destroy/free, including aliases,
# cached nested scripts, native waits, output aliasing, and cache-miss cleanup.
for n in [5,6,7,8,0xeeeeeeee]:
 for arguments in [0,ARGS,RETURNS]:
  for owner in [0,OWNER]:
   for pool in [0,POOL0]:
    case([call(0x4752f0,n,arguments,owner,RETURNS,this=0)],changes={0x6f3550:pool},label='run and collect output')
for mode in [1,2,3,5]:
 case([call(0x4752f0,8,ARGS,OWNER,ARGS,this=0)],[patch(CALLBACK+8,'<2I',mode,PROGRAM+0x1001 if mode==5 else 2)],label='one execution even if yielded')
# Constructors prepend to the global list; destruction retains stale own links.
case([call(0x4738e0,this=SCRIPTS),call(0x4738e0,this=SCRIPTS+256),call(0x474420,this=SCRIPTS),call(0x474420,this=SCRIPTS+256)],label='construct then destroy middle and head')
# Deferred mass-stop gate and sweep decisions across mixed script states.
for updating in [0,1,255]:
 for pending in [0,1,255]:
  for pattern in range(8):
   scripts,patches=chain(6)
   for i,s in enumerate(scripts):patches+=[patch(s+0xcc,'<B',(i+pattern)%8)]
   case([call(0x4753c0,this=0)],patches,{0x6f3544:updating,0x6f3545:pending,0x6f353c:6},'stop spawned sweep or defer')
for flags in [0,1,2,3,0xfe,255]:
 for target in [0,SCRIPT]:case([call(0x4756c0,target,this=0)],[patch(SCRIPT+0xcc,'<B',flags)],label='delete one spawned script')
for pattern in range(8):
 scripts,patches=chain(6)
 for i,s in enumerate(scripts):patches += [patch(s+12,'<I',PROGRAM if (i+pattern)&1 else 0),patch(s+0xcc,'<B',((i+pattern)>>1)&1),patch(s+0xe0,'<I',EVENTS if (i+pattern)&4 else 0)]
 case([call(0x475700,this=0)]*2,patches,{0x6f353c:6},'collect finished ordinary scripts')
# Owner and checksum tests are independent. A matching suspended owner and a
# checksum in a different frame still satisfy the broader stop variant.
for current_owner in [0,OWNER,OTHER]:
 for frame_owner in [0,OWNER,OTHER]:
  for requested_owner in [0,OWNER,OTHER,FOREIGN]:
   for requested_name in [0,5,6,7,0xdeadbeef]:
    patches=[patch(SCRIPT+0xbc,'<I',current_owner),patch(SCRIPT+0x30,'<I',2),patch(SCRIPT+0x94,'<I',FRAMES)]
    for i,n in enumerate([6,7]):patches.append(patch(FRAMES+i*48,'<12I',n,0,PROGRAM,frame_owner if i==0 else 0,0,0,0,0,0,0,0,0))
    for at in [0x4742b0,0x474350]:case([call(at,requested_owner,requested_name,this=0)],patches,label='owner and call-stack matching')
for requested_owner in [0,OWNER,OTHER]:
 case([call(0x4756f0,requested_owner,this=0)],[patch(SCRIPT+0xbc,'<I',OWNER)],label='owner stop wrapper')
# Nonmatching owner/checksum searches treat negative frame counts as empty.
# Do not call cleanup with an invalid negative depth: deferred execution uses it.
for depth in [0,0x80000000,0xffffffff]:
 for at in [0x4742b0,0x474350]:
  for owner in [0,OWNER]:case([call(at,owner,0xdeadbeef,this=0)],[patch(SCRIPT+0x30,'<I',depth)],label='signed frame count search')
# A deferred native command inserts a new valid instance after the current one.
# Deleting sweeps use a captured next; owner-stop walks read the updated link.
for at,args in [(0x4753c0,[]),(0x475700,[]),(0x4742b0,[0,0]),(0x474350,[0,0])]:
 scripts,patches=chain(3);added=SCRIPTS+5*256
 patches += [patch(SCRIPT+0xe8,'<I',8),patch(SCRIPT+0xcc,'<B',1 if at==0x4753c0 else 0),
  patch(SCRIPT+12,'<I',0 if at==0x475700 else PROGRAM),patch(added+12,'<I',PROGRAM),patch(added+0xc8,'<I',5),
  patch(CALLBACK+8,'<2I',6,added)]
 case([call(at,*args,this=0)],patches,{0x6f353c:3},'deferred insertion and list traversal')
# Relocations are restricted to actual method/function pointer slots and snapshots.
fields=set(prior['pointer_fields']);fields.update([TARGET,FOREIGN,SCRIPT+0xec,HEAP+0xec,BLOCK0+0xec,BLOCK1+0xec])
fields.update(SCRIPTS+i*256+0xec for i in range(6));fields.update([SENTINEL,SENTINEL+20,NODES])
for i in range((HEAP-LOG)//48):fields.update(LOG+i*48+j for j in [16,20,24,28,40])
scope='Fifteen original lifetime routines: referenced-object base clearing and both destructors, random-branch owner detachment, event-table disposal, script pool allocation/free, complete script destruction, one-shot execute/copy/dispose, spawned-stop deferral, single spawned deletion, ordinary-finished collection, and both current/stack checksum owner-stop variants plus wrapper. Existing constructor, executor, parser/cache, listener destructors and reference unlinking execute unchanged. Generic heap/scopes and configured native commands are instrumented boundaries; fixed pools execute original code. Host memory services are initialized. Full fixture/global bytes and heap order are compared, including pooled and generic run/collect, deferred scripts, owned event data, in-flight event tables, external reference graphs and mixed-list stopping. Frame scheduling, spawn/network wrappers and actual native gameplay handlers remain separate work.'
fixture={'base':BASE,'memory':'script-lifetime-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'native_command_callbacks',
 'pointer_symbols':prior['pointer_symbols'],'pointer_exports':prior['pointer_exports']+[[0x6478e4,'thug_reference_target_methods'],[0x6478d8,'thug_script_listener_methods'],[0x6478dc,'thug_script_listener_list_methods']],
 'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals'],
 'native_callbacks':[{'module':'script-lifetime-callbacks.wasm','export':'fixture_lifetime_native','original':NATIVE}]+prior['native_callbacks'][1:]}
path=out/'script-lifetime-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
adapter=out/'script-lifetime-callbacks.wasm'
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_lifetime_callbacks.c'),'-o',str(adapter)],check=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_lifetime_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-lifetime-memory.bin',adapter,out/'script-execute-callbacks.wasm',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
