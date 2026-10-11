"""Compare complete multiline widget rebuilding and combo text with original x86."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'ui-multiline.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'ui-manager-fixtures.json').read_text());BASE,SIZE=prior['base'],0x380000
memory=bytearray((out/prior['memory']).read_bytes());memory.extend(b'\xad'*(SIZE-len(memory)))
ADAPTER,CONTEXT,ALLOCATOR=BASE+0x100,BASE+0x200,BASE+0x400
OBJ,REF,OWNED,EM,TABLES,SCRIPTS,FRAMES,CACHE,SYMBOLS,TLS,LOCALE,UM,EVENTS,ENTRIES,SERVICES=[BASE+x for x in [0x10000,0x16000,0x18000,0x60000,0x6c000,0x70000,0x72000,0x73000,0x78000,0x7e000,0x7e100,0x80000,0x83800,0x83900,0x83a00]]
FONT,METRICS,GLYPHS,BUCKETS,FENTRY=BASE+0x2000,BASE+0x2400,BASE+0x3000,BASE+0x6800,BASE+0x6900
PRIMARY,SECONDARY,LISTENERS,NAMETABLE,CACHETABLE=[TABLES+i*256 for i in range(5)]
WIDGET,ARRAY,TEXTS,TRICKS,ITEMS,SCORE,GAME,NODES,BODIES,LOG,HEAP=[BASE+x for x in [0x85000,0x88000,0x90000,0xb0000,0xe0000,0xe1000,0xe3000,0xe4000,0xe5000,0x100000,0x180000]]
NOTIFY=0xd4491be1

def put(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ALLOCATOR+0x124,'<I',ALLOCATOR+0x300)
# Both configured and default font IDs resolve to the same real metrics.
put(BUCKETS+24,'<I',BUCKETS+32);put(BUCKETS+32,'<3I',0,FENTRY,0)
for at,n in [(WIDGET,0x1c4),(SCORE,0x1550),(GAME,0x200),(NODES,0x100),(BODIES,0x2000)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(WIDGET,'<I',0x64a264);put(WIDGET+8,'<I',0x14400);put(WIDGET+0x14,'<I',0x44727dae);put(WIDGET+0x18,'<I',0x40d92263)
put(WIDGET+0x28,'<5I',0x6477e4,WIDGET,0,WIDGET+0x28,WIDGET+0x28);put(WIDGET+0x40,'<3I',0x6477e0,0,WIDGET)
for off in [0xa4,0xa8,0xe8,0xec,0xf0,0xf4,0x170,0x19c,0x1a0]:put(WIDGET+off,'<f',1)
put(WIDGET+0x160,'<2f',80,100);put(WIDGET+0x178,'<I',0xabc);put(WIDGET+0x190,'<I',3);put(WIDGET+0x1bc,'<I',0x80000000)
put(GAME+0x34,'<I',NODES)
for i in range(8):
 put(NODES+i*16,'<4I',0,BODIES+i*0x400,0,NODES+(i+1)*16)
 put(BODIES+i*0x400+0x14,'<I',0x100+i);put(BODIES+i*0x400+0x2b8,'<I',i)
put(NODES+128,'<4I',0,0xffffffff,0,NODES+128)
put(SCORE+8,'<h',0x100);put(SCORE+0x4c,'<3I',ITEMS,250,0)
for i in range(250):
 put(ITEMS+i*4,'<I',TRICKS+i*256);put(ARRAY+i*4,'<I',TEXTS+i*256)
 for at in [TEXTS+i*256,TRICKS+i*256+0x5c]:memory[at-BASE]=0
# A real bytecode symbol and cache entry for the post-update notification.
NOTIFY_SYMBOL=CACHE+0x400
put(SYMBOLS+(NOTIFY&0xfff)*4,'<I',NOTIFY_SYMBOL);put(NOTIFY_SYMBOL,'<BBHIIII',0,7,0,NOTIFY,0,CACHE+0x500,0)
put(CACHETABLE+8,'<I',1);put(CACHETABLE+32+(NOTIFY&3)*12,'<3I',NOTIFY,CACHE+0x440,0)
put(CACHE+0x440,'<5I',NOTIFY,CACHE+0x500,1,0,0)
memory[CACHE+0x500-BASE:CACHE+0x502-BASE]=b'\x01\x24'
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value,width in [('thug_ui_manager',0x701440,UM,4),('thug_game_context',0x7ce478,GAME,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_script_updating',0x6f3544,0,1),('thug_script_stop_pending',0x6f3545,0,1)]:
 index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
functions={}
def bind(at,name,argc=0,result='void',heap=False,diag=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
bind(0x4b0810,'thug_ui_multiline_initialize',result='word',heap=True)
bind(0x4b08b0,'thug_ui_multiline_destroy',heap=True,diag=True)
bind(0x4b0b30,'thug_ui_multiline_delete',1,'word',True,True)
bind(0x4b0cd0,'thug_ui_multiline_set_text',2,heap=True,diag=True)
bind(0x561670,'thug_score_update_combo_text',1,heap=True,diag=True)
for at in [0x41d1d0,0x461a00,0x461930,0x4aa8e0,0x4b0920,0x4b3fd0,0x4ab250,0x4ad100]:functions[hex(at)]=prior['functions'][hex(at)]
observe=[int(k,16) for k in functions]+[0x401cc0,0x4a8940,0x4abd40,0x461140,0x473800,0x460470,0x474540,0x4748e0,0x473a80,0x475790,0x474420,0x4621d0,0x6234fe,0x4b1830,0x4b0760,0x48d5f0,0x4b3e70,0x48d1d0,0x4abbe0,0x4af720,0x4af8c0,0x4a94a0,0x4ac400,0x4aaff0,0x4637c0,0x4637e0]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=12000000,scope_entries={ALLOCATOR+0x200:6,ALLOCATOR+0x300:1})
# Real CRT signed auto-ID formatting runs; only its Windows TLS services adapt.
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
fields=set(prior['pointer_fields'])|{WIDGET,WIDGET+0x28,WIDGET+0x40}
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
exports=prior['pointer_exports']+[[0x64a264,'thug_ui_multiline_methods']]
labels=[];branches=Counter()
branch_at={0x4b0d30:'delete_previous_child',0x4b0eaf:'check_auto_height',0x4b0f29:'auto_height_measure',0x4b0fbf:'fixed_height_ring',0x4b0fa3:'second_wrap',0x4b0fe2:'create_text_child',0x4b1139:'row_ring_reset',0x561701:'clear_combo_text',0x56170f:'run_combo_notification'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([0] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='multiline'):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%25==0:print('Original multiline cases:',len(labels),flush=True)
 return stages

def texts_patch(texts,capacity=3,width=80,scale=1,spacing=1,automatic=0):
 p=[patch(WIDGET+0x190,'<i',capacity),patch(WIDGET+0x160,'<f',width),patch(WIDGET+0x19c,'<2f',scale,spacing),patch(WIDGET+0x1b1,'<B',automatic)]
 for i,t in enumerate(texts):
  assert len(t)<196;p += [raw(TEXTS+i*256,t+b'\0'),raw(TRICKS+i*256+0x5c,t+b'\0')]
 return p

def setup(children=0):
 calls=[call(0x4b3fd0,args=[32]),call(0x461a00,UM,[WIDGET]),call(0x41d1d0,REF,[WIDGET]),call(0x4ab250,UM,[REF,0])]
 for i in range(children):
  at=OBJ+i*512
  calls += [call(0x4b0920,at),call(0x461930,at,[0x100+i]),call(0x461a00,UM,[at]),call(0x41d1d0,REF+(i+1)*16,[at]),call(0x4aa8e0,at,[REF if i<2 else REF+i*16,1]),call(0x4ab250,UM,[REF+(i+1)*16,0])]
 return calls
rng=random.Random(0x4b0cd0)
for fill in [0,0xa5,0xff,None]:
 p=[raw(WIDGET,bytes([fill])*0x1c4 if fill is not None else bytes(rng.getrandbits(8) for _ in range(0x1c4)))]
 case([call(0x4b0810,WIDGET)],p,label='multiline constructor preserves row storage counts capacity and padding')
for flags in [0,1,2,3,256,257,0xffffffff]:
 for extra in [0,OWNED]:
  p=[patch(WIDGET+0x1ac,'<I',extra)]
  case([call(0x41d1d0,REF,[WIDGET]),call(0x4b0b30,WIDGET,[flags])],p,label='multiline deleting destructor releases optional object then actual UI base')
case([call(0x4b08b0,WIDGET)],label='ordinary multiline destructor')
# Full original set_text with actual constructors, automatic IDs, manager events,
# style pool acquisition and old nested children; repeated calls test style reuse.
samples=[[],[b''],[b' '],[b'A B'],[b'one two three four'],[b'alpha\\nbeta\\ngamma'],[b'A\\n'],[b'one ',b'two ',b'three'],[b'\\c1red \\s4 \\b4 \\m2'],[b'x'*95,b' y'],[b'one\\_two \\\\three']]
for texts in samples:
 for capacity,width in [(1,20),(3,80),(30,1024)]:
  for automatic in [0,1]:
   p=texts_patch(texts,capacity,width,automatic=automatic)
   calls=setup(4)+[call(0x4b0cd0,WIDGET,[ARRAY,len(texts)])]*2
   case(calls,p,label='full multiline replacement and repeated update, escapes wrapping ring and automatic height')
# Automatic resize uses retained x87 intermediates for the two integer converts.
for scale,spacing in [(0.125,0.5),(0.5,0.5),(0.75,1.5),(1.125,0.875),(1.9999999,1.0000001),(17/16,19/16)]:
 for width in [0,30,100]:
  for automatic in [0,1]:
   p=texts_patch([b'alpha beta ',b'gamma'],3,width,scale,spacing,automatic)
   case(setup()+[call(0x4b0cd0,WIDGET,[ARRAY,2])],p,label='PC24 operation order, fractional line sizes and rewrap')
# Fixed height allows zero/negative scale and nonfinite width without integer
# division of line height. Arithmetic outputs are still required bit-exact here.
for width in [-1,0,1e30,float('inf')]:
 for scale in [0,-1,0.00001,4]:
  p=texts_patch([b'one two ',b'three'],3,width,scale,0.75)
  case(setup()+[call(0x4b0cd0,WIDGET,[ARRAY,2])],p,label='fixed height signed scale and extreme widths')
for count in [0,0xffffffff,0x80000000]:
 case(setup(2)+[call(0x4b0cd0,WIDGET,[0,count])],texts_patch([],3,80),label='signed count skipping with nonzero final row increment')
# Bounded row/byte limits, including all thirty child widgets and a long ring.
for rows in [1,29,30,45]:
 texts=[b'A\\n']*rows
 case(setup()+[call(0x4b0cd0,WIDGET,[ARRAY,rows])],texts_patch(texts,30,1024),label='thirty-row storage capacity and ring overwrite')
# Existing parent owner/depth flags propagate to new children through real attach.
for flags,owner,depth in [(0x10014400,9,2.5),(0x1001c400,0xffffffff,-2),(0x214400,0,0)]:
 p=texts_patch([b'alpha beta'],3,80)+[patch(WIDGET+8,'<I',flags),patch(WIDGET+0x174,'<I',owner),patch(WIDGET+0x16c,'<f',depth)]
 case(setup()+[call(0x4b0cd0,WIDGET,[ARRAY,1])],p,label='owner depth and inherited disabled flags survive child rebuilding')
# Real parent QB handlers run on disable/enable around deletion and creation.
for old_children in [0,4]:
 p=texts_patch([b'A B C'],3,25)+[raw(SCRIPTS,bytes(244)),patch(WIDGET+0x10,'<I',SCRIPTS),patch(SCRIPTS+0x2c,'<I',SCRIPTS+0x1c),patch(SCRIPTS+0x94,'<I',SCRIPTS+0x34),patch(SCRIPTS+0xe0,'<I',EVENTS),patch(SCRIPTS+0xec,'<I',0x6478e4),patch(EVENTS,'<IIBBHI',ENTRIES,2,1,0,0,0),patch(ENTRIES,'<5I',0x4a57316b,NOTIFY,0,0,0),patch(ENTRIES+20,'<5I',0x3056434f,NOTIFY,0,0,0)]
 case(setup(old_children)+[call(0x41d1d0,SCRIPTS+0xbc,[WIDGET]),call(0x4b0cd0,WIDGET,[ARRAY,1])],p,label='real owned QB handlers bracket multiline child replacement')
# Real score caller: signed skater IDs, screen-ID wrap, low-byte clear, missing
# widget and cached QB notification rather than instrumented script callbacks.
for skater_id,screen,found in [(0x100,0,True),(0x100,7,True),(0x100,0xffffffff,True),(0x7fff,0,False),(0xffff,0,True)]:
 for clear in [0,1,256,257]:
  for count in [0,1,3]:
   p=texts_patch([b'Kickflip + ',b'50-50 + ',b'Ollie'],3,80)+[patch(SCORE+8,'<H',skater_id),patch(SCORE+0x54,'<I',count),patch(BODIES+0x2b8,'<I',screen),patch(WIDGET+0x14,'<I',(0x44727dae+screen)&0xffffffff)]
   if skater_id==0xffff:p.append(patch(BODIES+0x14,'<I',0xffffffff))
   if not found:p.append(patch(WIDGET+0x14,'<I',0x12345678))
   case(setup()+[call(0x561670,SCORE,[clear])],p,label='score combo text finds player screen and runs actual notification QB')
# Maximum original caller stack list; empty entries keep the output bounded.
case(setup()+[call(0x561670,SCORE,[0])],texts_patch([],30,1024)+[patch(SCORE+0x54,'<I',250)],label='250 score-entry pointers with bounded text output')
# Complete fresh construction, text replacement and manager-led recursive disposal.
case([call(0x4b3fd0,args=[32]),call(0x4b0810,WIDGET),call(0x461930,WIDGET,[0x44727dae]),call(0x461a00,UM,[WIDGET]),call(0x4b0cd0,WIDGET,[ARRAY,2]),call(0x4ad100,UM,[0x44727dae,1,0,0])],texts_patch([b'one ',b'two'],3,80),label='fresh multiline construct update and virtual recursive delete')
scope='Five complete original routines: multiline construction/destruction/deleting destructor, multiline text rebuilding and the score-combo text caller. Real wrapping/font measurement, actual text-child constructors, style reuse, automatic registry IDs, UI manager events and recursive deletion, scale/height math and cached QB notification/owner handlers execute unchanged. Full arena/globals/returns and heap/scope records compare exactly, with no substituted gameplay callbacks or numeric masks. Only generic memory and initialized Windows CRT services adapt. Original bounded internal contracts require <=30 visible rows, <=95-byte words, <=250 score entries, valid fonts/style pools, successful allocation and nonzero integer line height for automatic resizing. Numeric score formatting, remaining movement/startup/rendering and playable training integration remain unfinished.'
fixture={'base':BASE,'memory':'ui-multiline-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'substituted_gameplay_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES}}
path=out/'ui-multiline-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_ui_multiline_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
