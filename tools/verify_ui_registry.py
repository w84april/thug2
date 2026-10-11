"""Compare object registry and full object/UI/text destruction with original x86."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'ui-registry.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'ui-construction-fixtures.json').read_text());BASE,SIZE=prior['base'],0x80000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
OBJ,TREE,REF,POOL,BLOCKS,OWNED,ARRAYS,LOG,HEAP=[BASE+x for x in [0x10000,0x11000,0x16000,0x17000,0x17400,0x18000,0x1c000,0x20000,0x30000]]
STYLE,DRAW=BASE+0xc000,BASE+0xb000
EM,TABLES,NODES,MANAGER,SCRIPTS,FRAMES,CACHE,SYMBOLS,NAMES,TLS,LOCALE=[BASE+x for x in [0x60000,0x6c000,0x6d000,0x6e000,0x70000,0x72000,0x73000,0x78000,0x7c000,0x7e000,0x7e100]]
PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE=[TABLES+i*256 for i in range(5)]
def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,EM,0,LOG,BASE,BASE+SIZE,0,0)
memory[EM-BASE:EM-BASE+0xb218]=bytes(0xb218)
put(EM,'<5I',0,0,PRIMARY,SECONDARY,LISTENERS);put(EM+0x20+0xb008,'<I',NAMETABLE)
for table in [PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE]:
 put(table,'<6I',2,table+32,0,0xffffffff,0,0);memory[table+32-BASE:table+80-BASE]=bytes(48)
put(CACHE,'<9I',0,0,0,0,0,CACHETABLE,0,0,0)
memory[SYMBOLS-BASE:SYMBOLS-BASE+0x4000]=bytes(0x4000)
put(SYMBOLS+(0x08114f90&0xfff)*4,'<I',NAMES)
put(NAMES,'<BBHIIII',0,12,0,0x08114f90,0,NAMES+32,0)
put(NAMES+32,'<BBHII',0,3,0,3,NAMES+64)
for i,text in enumerate([b'Registered',b'Unregistered',b'']):
 put(NAMES+64+i*4,'<I',NAMES+128+i*32);memory[NAMES+128+i*32-BASE:NAMES+128+i*32-BASE+len(text)+1]=text+b'\0'
for at in [TLS,LOCALE]:memory[at-BASE:at-BASE+256]=bytes(256)
put(TLS+0x64,'<I',LOCALE)
# Base object/manager instances provide valid unlinked storage for standalone methods.
for i in range(8):
 at=OBJ+i*512;memory[at-BASE:at-BASE+0x1b0]=bytes(0x1b0)
 put(at,'<I',0x64a290);put(at+0x14,'<I',0x100+i)
 put(at+0x28,'<5I',0x6477e4,at,0,at+0x28,at+0x28)
 put(at+0x40,'<3I',0x6477e0,0,at)
for i in range(2):
 at=MANAGER+i*128;memory[at-BASE:at-BASE+0x28]=bytes(0x28)
 put(at,'<6I',0x647818,0x647814,0xffffffff,0,at+4,at+4)
memory[REF-BASE:REF-BASE+0x200]=bytes(0x200)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
def glob(name,at,value=0,width=4,offset=0):
 index[at]=len(globals_);globals_.append([name,at,width,offset]);defaults.append(value)
names={'thug_script_list','thug_script_count','thug_script_next_serial','thug_current_script','thug_script_pool_index','thug_script_pools','thug_script_branch_first','thug_script_branch_last','thug_script_branch_count','thug_script_cache','thug_script_listener_pool_index','thug_script_listener_pools','thug_script_string_pool','thug_script_string_pool_size','thug_lookup_node_pool','thug_object_lookup_manager','thug_script_symbol_buckets'}
for g in json.loads((out/'event-delivery-fixtures.json').read_text())['globals']:
 if g[0] in names and g[1] not in index:
  glob(g[0],g[1],{'thug_script_cache':CACHE,'thug_object_lookup_manager':EM,'thug_script_symbol_buckets':SYMBOLS}.get(g[0],0),g[2],g[3] if len(g)>3 else 0)
functions={}
def bind(at,name,argc=0,result='void',heap=False,diag=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
bind(0x461bc0,'thug_object_manager_initialize',result='word')
bind(0x4621d0,'thug_object_registry_next_id',result='word')
bind(0x462590,'thug_object_registry_clear_aliases',1,heap=True)
bind(0x462980,'thug_object_registry_add',1,heap=True)
bind(0x462a20,'thug_object_registry_remove',3,heap=True)
bind(0x461930,'thug_ui_object_set_id',1,heap=True)
bind(0x461a00,'thug_object_manager_add',1,heap=True)
bind(0x461a50,'thug_object_manager_remove',1,heap=True)
bind(0x4619a0,'thug_object_manager_rename',2,heap=True)
bind(0x4619d0,'thug_object_manager_set_priority',2,heap=True)
bind(0x472f00,'thug_script_clear_deferred')
bind(0x460af0,'thug_ui_object_secondary_delete',1,'word',True)
bind(0x460b20,'thug_ui_object_queue_destroy')
bind(0x460b40,'thug_ui_object_queue_delete',1,'word',True)
bind(0x461b20,'thug_object_manager_queue_delete',1,'word',True)
bind(0x461b50,'thug_object_manager_destroy')
bind(0x461b80,'thug_object_manager_delete',1,'word',True)
for at,name,argc,result in [(0x4615d0,'thug_ui_object_destroy',0,'void'),(0x461900,'thug_ui_object_delete',1,'word'),(0x4aab30,'thug_ui_destroy',0,'void'),(0x4aac90,'thug_ui_delete',1,'word'),(0x4b1830,'thug_ui_text_destroy',0,'void'),(0x4b2030,'thug_ui_text_delete',1,'word')]:bind(at,name,argc,result,True,True)
# Already verified production routines build real lifecycle sequences.
for at in [0x460b80,0x4a8f90,0x4b0920,0x41d1d0,0x4aa8e0,0x4b3fd0,0x4b0620]:functions[hex(at)]=prior['functions'][hex(at)]
bind(0x4738e0,'thug_script_initialize',result='word')
bind(0x462740,'thug_object_table_insert',2,'byte',True)
bind(0x477d40,'thug_script_set_checksum',2,heap=True)
observe=[int(k,16) for k in functions]+[0x6234fe,0x472e60,0x4627c0,0x5b80d0,0x588190,0x45a540,0x477130,0x409070,0x474420,0x4499b0,0x4756f0,0x4742b0,0x473a80,0x473880,0x463870,0x463820,0x4637c0,0x4637e0,0x48d5f0,0x48d5a0,0x4b0760,0x5480a0,0x5ba400,0x5ba3d0,0x46f870,0x463450,0x45fb70,0x475d60,0x475750,0x4750b0,0x473e70,0x474540,0x4748e0]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,scope_entries={ALLOCATOR+0x200:6})
# Only initialized Windows CRT TLS/last-error services are adapted; real sprintf runs.
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
fields=set(prior['pointer_fields'])|{MANAGER,MANAGER+4,MANAGER+128,MANAGER+132}
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
exports=prior['pointer_exports']+[[0x647818,'thug_object_manager_methods'],[0x647814,'thug_object_manager_queue_methods']]
labels=[];branches=Counter()
branch_at={0x462206:'auto_id_wrap',0x4621e0:'auto_id_attempt',0x4629c3:'replace_alias',0x46260a:'alias_count_decrement',0x462a5b:'wait_retarget',0x461a29:'automatic_id',0x461a78:'unlink_manager',0x461627:'cancel_owned_script',0x461633:'destroy_owned_script',0x4b1865:'optional_text_object'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([0] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='object registry and destruction'):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%50==0:print('Original UI registry cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x4615d0)
for fill in [0,0xa5,0xff,None]:
 data=bytes([fill])*0x28 if fill is not None else bytes(rng.getrandbits(8) for _ in range(0x28))
 case([call(0x461bc0,MANAGER)]*2,[raw(MANAGER,data)],label='manager constructor preserves replacement ID and padding')
# Decimal formatting includes all signed boundaries and real collision retries.
def autoid(n):return zlib.crc32(('autoid'+str(n if n<0x80000000 else n-0x100000000)).encode())^0xffffffff
for n in [0,1,9,10,99,100,999998,999999,1000000,0x7ffffffe,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]+[rng.getrandbits(32) for _ in range(96)]:
 for collide in [False,True]:
  p=[patch(EM+4,'<I',n)]
  if collide:
   key=autoid(n);p += [patch(PRIMARY+32+(key&3)*12,'<3I',key,OBJ,0),patch(PRIMARY+8,'<I',1)]
  case([call(0x4621d0,EM)],p,label='signed auto-ID formatting and collision retry')
# Secondary aliases use actual insertions, including colliding keys, same IDs on
# different objects, and signed alias counters. Log initialization also executes.
for count in [0,1,3,0x7fffffff,0x80000000,0xffffffff]:
 for lazy in [False,True]:
  p=[patch(OBJ+0x3c,'<I',count),patch(OBJ+512+0x3c,'<I',count),patch(OBJ+512+0x14,'<I',0x100),patch(OWNED,'<4I',0x100,0x104,0x108,0x10c)]
  if lazy:p.append(patch(EM+0x20+0xb008,'<I',0))
  calls=[call(0x462740,SECONDARY,[OWNED,OBJ]),call(0x462740,SECONDARY,[OWNED+4,OBJ]),call(0x462740,SECONDARY,[OWNED+8,OBJ+512]),call(0x462740,SECONDARY,[OWNED+12,OBJ+1024])]
  calls += [call(0x462980,EM,[OBJ]),call(0x462590,EM,[OBJ]),call(0x462590,EM,[OBJ])]
  case(calls,p,label='alias replacement and restarted iteration match object IDs')
for mode in [0,1,256,257,0xffffffff]:
 for name in [0,0x100,0xffffffff]:
  p=[patch(OBJ+0x14,'<I',name),patch(EM+0x20+0x7000,'<I',1023)]
  p += [patch(EM+0xb038+i*12,'<3I',i,0xabc,name if i%2 else name^1) for i in range(40)]
  case([call(0x462980,EM,[OBJ]),call(0x462a20,EM,[OBJ,0x12345678,mode])],p,label='rename wait retargeting and lifecycle log ring wrap')
# Full registration/rename/reprioritization/remove through actual manager virtuals.
for name in [0,0x100,0xffffffff]:
 for target in [0x100,0x104,0xffffffff]:
  for order in [0,1,0x80000000,0xffffffff]:
   p=[patch(OBJ+0x14,'<I',name),patch(OBJ+0x30,'<I',order),patch(OBJ+512+0x30,'<I',order^0xffffffff)]
   calls=[call(0x461a00,MANAGER,[OBJ+512]),call(0x461a00,MANAGER,[OBJ]),call(0x461930,OBJ,[target]),call(0x4619d0,MANAGER,[OBJ,order^0xffffffff]),call(0x461a50,MANAGER,[OBJ]),call(0x461a50,MANAGER,[OBJ])]
   case(calls,p,label='real register, ID mutation, queue priority, linked and unlinked removal')
# Cancel active/suspended deferred calls without touching interrupt checksums.
for depth in [0,1,2,3,16]:
 for fill in [0,0xa5,0xff]:
  p=[raw(SCRIPTS,bytes([fill])*244),patch(SCRIPTS+0x30,'<I',depth),patch(SCRIPTS+0x94,'<I',FRAMES),raw(FRAMES,bytes([fill])*768)]
  case([call(0x472f00,SCRIPTS)]*2,p,label='deferred cancellation preserves all other frame words')
# Embedded queue and reference deletion, self-linked and linked neighbors.
for flags in [0,1,2,3,256,257,0xffffffff]:
 for linked in [False,True]:
  node=OBJ+0x28;p=[]
  if linked:p=[patch(node+12,'<2I',OBJ+512+0x28,OBJ+1024+0x28),patch(OBJ+512+0x28+16,'<I',node),patch(OBJ+1024+0x28+12,'<I',node)]
  for fn in [0x460b40,0x461b20]:case([call(fn,node,[flags])],p,label='queue deleting destructors retain original neighbor order')
  case([call(0x460b20,node)],p,label='ordinary queue destructor')
  calls=[call(0x41d1d0,REF,[OBJ+0x40]),call(0x41d1d0,REF+16,[OBJ+0x40]),call(0x460af0,OBJ+0x40,[flags])]
  case(calls,label='secondary target deletion clears live references')
  calls=[call(0x461a00,MANAGER,[OBJ])] if linked else []
  case(calls+[call(0x461b80,MANAGER,[flags])],label='manager base destruction unlinks only its sentinel')
case([call(0x461b50,MANAGER)],label='manager ordinary destructor')
# Full object/UI/Text destruction, including live parent trees and style arrays.
for kind,ctor,dtor in [('object',0x460b80,0x461900),('ui',0x4a8f90,0x4aac90),('text',0x4b0920,0x4b2030)]:
 for flags in [0,1,256,257]:
  for registered in [False,True]:
   p=[raw(OBJ,bytes(0x1b0))]
   calls=([call(0x4b3fd0,args=[8])] if kind=='text' else [])+[call(ctor,OBJ),call(0x41d1d0,REF,[OBJ]),call(0x41d1d0,REF+16,[OBJ+0x40])]
   if registered:calls.append(call(0x461a00,MANAGER,[OBJ]))
   if kind!='object':calls += [call(0x41d1d0,REF+32,[OBJ+512]),call(0x4aa8e0,OBJ,[REF+32,0]),call(0x41d1d0,REF+48,[OBJ]),call(0x4aa8e0,OBJ+1024,[REF+48,0])]
   calls.append(call(dtor,OBJ,[flags]));case(calls,p,label=kind+' complete constructed lifetime and deletion')
# Full text destructor's optional190 path allocates and releases again; owned
# buffers and secondary styles coexist. The remaining pool has enough entries.
for secondary in [0,1]:
 for extra in [0,OWNED+512]:
  p=[patch(OBJ+0x178,'<I',OWNED+768),patch(OBJ+0x190,'<I',extra),patch(OBJ+0x194,'<B',secondary)]
  calls=[call(0x4b3fd0,args=[8]),call(0x4b0620,OBJ,[3,0]),call(0x4b1830,OBJ)]
  case(calls,p,label='text owned buffers and optional-object reacquisition branch')
# Owned scripts with suspended frames, completion storage, empty event tables,
# and a second owned live script exercise the real cleanup/stop chain.
def script_bytes(at,next_=0,previous=0,depth=0):
 b=bytearray(244)
 def w(off,fmt,*v):struct.pack_into(fmt,b,off,*v)
 w(0,'<2I',next_,previous);w(0x2c,'<I',at+0x1c);w(0x30,'<I',depth);w(0x94,'<I',FRAMES if depth else at+0x34)
 w(0xe4,'<2I',0xabcdef01,0x12345678 if at==SCRIPTS else 0)
 return b
for depth in [0,1,2,3,16]:
 for selected in [0,1]:
  p=[raw(SCRIPTS,script_bytes(SCRIPTS,SCRIPTS+256,0,depth)),raw(SCRIPTS+256,script_bytes(SCRIPTS+256,0,SCRIPTS)),patch(OBJ+0x10,'<I',SCRIPTS),patch(SCRIPTS+0xdc,'<I',OWNED+1024),patch(OWNED+1024,'<2I',0,0),patch(SCRIPTS+0xe0,'<I',OWNED+1056),patch(OWNED+1056,'<IIBBHI',0,0,1,0,0,0),raw(FRAMES,bytes(768))]
  for j in range(depth):p += [patch(FRAMES+j*48+0x14,'<I',0x200+j),patch(FRAMES+j*48+12,'<I',OBJ)]
  changes={0x6f3538:SCRIPTS,0x6f353c:2,0x6f3548:selected}
  calls=[call(0x41d1d0,SCRIPTS+0xbc,[OBJ]),call(0x41d1d0,SCRIPTS+256+0xbc,[OBJ]),call(0x41d1d0,REF,[OBJ]),call(0x41d1d0,REF+16,[SCRIPTS+0xec]),call(0x4615d0,OBJ)]
  case(calls,p,changes,label='object cancels its deferred scripts then destroys and stops all owned scripts')
# Exercise selected and alternate script pools, and real QB execution when a
# different owned script has a deferred callback (the deleted script cancels its own).
for selected in [0,1]:
 for membership in [-1,0,1]:
  for deferred in [False,True]:
   p=[raw(SCRIPTS,script_bytes(SCRIPTS,SCRIPTS+256)),raw(SCRIPTS+256,script_bytes(SCRIPTS+256,0,SCRIPTS)),patch(OBJ+0x10,'<I',SCRIPTS),patch(SCRIPTS+256+0xe8,'<I',5 if deferred else 0),patch(CACHETABLE+8,'<I',1),patch(CACHETABLE+32+12,'<3I',5,CACHE+128,0),patch(CACHE+128,'<5I',5,CACHE+192,1,0,0),raw(CACHE+192,b'\x01\x24')]
   changes={0x6f3538:SCRIPTS,0x6f353c:2,0x6f3548:selected}
   if membership>=0:
    pool=POOL+256+membership*128
    p += [patch(pool,'<6I',SCRIPTS,SCRIPTS+256,0,0,1,0),patch(pool+88,'<I',1)]
    changes[0x6f3550+membership*4]=pool
   calls=[call(0x41d1d0,SCRIPTS+0xbc,[OBJ]),call(0x41d1d0,SCRIPTS+256+0xbc,[OBJ]),call(0x4615d0,OBJ)]
   case(calls,p,changes,label='selected/alternate script-pool release and real deferred QB on another owned script')
# The normal UI deletion caller unregisters before invoking the destructor.
for name in [0x100,0xffffffff]:
 calls=[call(0x4b3fd0,args=[8]),call(0x4b0920,OBJ),call(0x461930,OBJ,[name]),call(0x461a00,MANAGER,[OBJ]),call(0x4619a0,MANAGER,[OBJ,0x12345678]),call(0x461a50,MANAGER,[OBJ]),call(0x4b2030,OBJ,[1])]
 case(calls,[raw(OBJ,bytes(0x1b0))],label='text-widget lifetime through registration, rename, unregister and deleting destructor')
# Direct UI destructor and pooled parameter release after real construction.
for selected in [0,1]:
 for fn in [0x4615d0,0x4aab30]:
  p=[raw(OBJ,bytes(0x1b0))];changes={0x6f3614:selected,0x6f361c:POOL,0x6f3620:POOL+128}
  case([call(0x4a8f90,OBJ),call(0x461930,OBJ,[0x1234]),call(fn,OBJ)],p,changes,label='actual parameter construction and selected/alternate structure pool release')
scope='Twenty-three original routines recover global object ID/alias registration and lifecycle logging, local manager construction/register/remove/rename/priority/destruction, complete object/UI/Text destructors, embedded queue/reference deletion and cancellation of deferred script calls. Real virtual manager calls, script destruction/stopping, parameter pools, references, parent detachment and style cleanup execute. Original CRT signed auto-ID formatting runs with only initialized Windows TLS/last-error services adapted. Full arena/globals, returns and heap/scope records compare exactly; no gameplay callback or numeric mask. Generic memory services are adapted. Valid mapped acyclic object graphs, initialized registry/cache/log tables, successful allocation and sufficient style pools preserve original contracts. Derived UI manager attachment/deletion, rendering and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'ui-registry-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'substituted_gameplay_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields)}
path=out/'ui-registry-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_ui_registry_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
