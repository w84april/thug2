"""Compare complete multiline widget rebuilding and combo text with original x86."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'score-display.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'ui-multiline-fixtures.json').read_text());BASE,SIZE=prior['base'],0x380000
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
NUMERIC,SETTINGS,COMPONENT,PRINT,DIAG,GRAPH=BASE+0x86000,BASE+0x87000,BASE+0x87400,BASE+0x87500,BASE+0x87600,BASE+0xf0000
for at,n in [(NUMERIC,0x1b0),(SETTINGS,64),(COMPONENT,64),(DIAG,512)]:memory[at-BASE:at-BASE+n]=bytes(n)
put(NUMERIC,'<I',0x64a290);put(NUMERIC+8,'<I',0x14400);put(NUMERIC+0x14,'<I',0xf4d3a70e)
put(NUMERIC+0x28,'<5I',0x6477e4,NUMERIC,0,NUMERIC+0x28,NUMERIC+0x28);put(NUMERIC+0x40,'<3I',0x6477e0,0,NUMERIC)
for off in [0xa4,0xa8,0xe8,0xec,0xf0,0xf4,0x170]:put(NUMERIC+off,'<f',1)
put(NUMERIC+0x180,'<I',FONT);put(COMPONENT+4,'<I',0x8bce7e66);put(COMPONENT+12,'<I',BODIES);put(BODIES+0x100,'<I',COMPONENT)
put(PRINT,'<2I',DIAG,0);put(DIAG+4,'<I',SCORE)
# Add numeric-display notification to the existing initialized QB cache.
NUMERIC_NOTIFY=0xa611bb15
put(SYMBOLS+(NUMERIC_NOTIFY&0xfff)*4,'<I',CACHE+0x600)
put(CACHE+0x600,'<BBHIIII',0,7,0,NUMERIC_NOTIFY,0,CACHE+0x680,0)
put(CACHE+0x640,'<5I',NUMERIC_NOTIFY,CACHE+0x680,1,0,0)
put(CACHETABLE+8,'<I',2);put(CACHETABLE+32+(NUMERIC_NOTIFY&3)*12,'<3I',NUMERIC_NOTIFY,CACHE+0x640,CACHE+0x660)
put(CACHE+0x660,'<3I',NOTIFY,CACHE+0x440,0)
memory[CACHE+0x680-BASE:CACHE+0x682-BASE]=b'\x01\x24'
# Typed required special-color and rate symbols.
for i in range(3):
 put(GRAPH+i*32,'<BBHII',0,1,0,4,GRAPH+0x100+i*16)
 put(GRAPH+0x100+i*16,'<4I',0x100+i,0xabcdef80+i,0xfffffffe,255)
put(GRAPH+0x80,'<BBHII',0,12,0,3,GRAPH+0x140);put(GRAPH+0x140,'<3I',GRAPH,GRAPH+32,GRAPH+64)
for i,(name,kind,value) in enumerate([(0x2e8b9f1c,12,GRAPH+0x80),(0x3abcda81,2,0x3e4ccccd)]):
 at=GRAPH+0x200+i*32;put(at,'<BBHIIII',0,kind,0,name,0,value,0);put(SYMBOLS+(name&0xfff)*4,'<I',at)
put(SETTINGS+8,'<I',SETTINGS+16);put(SETTINGS+16,'<4I',26,0xa1dc81f9,0,0)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
for name,at,value,width in [('thug_ui_manager',0x701440,UM,4),('thug_game_context',0x7ce478,GAME,4),('thug_script_wait_gate',0x6f352c,0,1),('thug_script_updating',0x6f3544,0,1),('thug_script_stop_pending',0x6f3545,0,1),('thug_game_settings',0x7ce470,SETTINGS,4)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,width,0]);defaults.append(value)
index[0x7cefa0]=len(globals_);globals_.append(['thug_text_language',0x7cefa0,4,0]);defaults.append(0)
for i in range(8):
 at=0x690fa4+i*4;index[at]=len(globals_);globals_.append(['thug_integer_text',at,4,i*4]);defaults.append(0xa5a5a5a5)
functions={}
def bind(at,name,argc=0,result='void',heap=False,diag=False,this=True):
 functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'stack_args':list(range(argc)),'memory':heap,'diagnostics':diag}
bind(0x4b0810,'thug_ui_multiline_initialize',result='word',heap=True)
bind(0x4b08b0,'thug_ui_multiline_destroy',heap=True,diag=True)
bind(0x4b0b30,'thug_ui_multiline_delete',1,'word',True,True)
bind(0x4b0cd0,'thug_ui_multiline_set_text',2,heap=True,diag=True)
bind(0x561670,'thug_score_update_combo_text',1,heap=True,diag=True)
bind(0x561890,'thug_score_update_numeric_text',2,heap=True,diag=True);functions['0x561890']['float_args']=[1]
bind(0x564a10,'thug_score_reset',heap=True,diag=True)
for at in [0x41d1d0,0x461a00,0x461930,0x4aa8e0,0x4b0920,0x4b3fd0,0x4ab250,0x4ad100]:functions[hex(at)]=prior['functions'][hex(at)]
observe=[int(k,16) for k in functions]+[0x401cc0,0x4a8940,0x4abd40,0x461140,0x473800,0x460470,0x474540,0x4748e0,0x473a80,0x475790,0x474420,0x4621d0,0x6234fe,0x4b1830,0x4b0760,0x48d5f0,0x4b3e70,0x48d1d0,0x4abbe0,0x4af720,0x4af8c0,0x4a94a0,0x4ac400,0x4aaff0,0x4637c0,0x4637e0,0x561890,0x564a10,0x402200,0x6285af,0x6286ab,0x5532a0,0x5612d0,0x518390,0x460a20,0x5633e0,0x45db90]
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
from unicorn.x86_const import UC_X86_REG_EIP,UC_X86_REG_FPCW
sp=oracle.stack+0x18000;oracle.cpu.mem_write(sp,struct.pack('<I',oracle.stop));oracle.cpu.reg_write(UC_X86_REG_ESP,sp)
oracle.cpu.emu_start(0x622f48,oracle.stop,count=1000)
assert oracle.cpu.reg_read(UC_X86_REG_EIP)==oracle.stop
# Format/output is an explicit platform boundary, with its literal checked.
def debug_output(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ptr=oracle.word(sp+4)
 text=bytes(cpu.mem_read(ptr,29)).split(b'\0')[0];assert text==b'Score::RESET ...............\n',text
 n=oracle.word(DIAG);assert n<20;oracle.setword(DIAG,n+1)
 h=0
 for ch in text:h=(h*33+ch)&0xffffffff
 cpu.mem_write(DIAG+16+n*16,struct.pack('<4I',h,oracle.word(SCORE+0x1538),oracle.word(SCORE+0x54),oracle.word(SCORE+0x38)))
 if oracle.word(DIAG+8):oracle.setword(oracle.word(DIAG+8),oracle.word(DIAG+12))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,begin=0x401c30,end=0x401c30)
fields=set(prior['pointer_fields'])|{WIDGET,WIDGET+0x28,WIDGET+0x40,NUMERIC,NUMERIC+0x28,NUMERIC+0x40}
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
exports=prior['pointer_exports']
labels=[];branches=Counter()
branch_at={0x4b0d30:'delete_previous_child',0x4b0eaf:'check_auto_height',0x4b0f29:'auto_height_measure',0x4b0fbf:'fixed_height_ring',0x4b0fa3:'second_wrap',0x4b0fe2:'create_text_child',0x4b1139:'row_ring_reset',0x561701:'clear_combo_text',0x56170f:'run_combo_notification'}
def branch(cpu,address,size,user):branches[branch_at[address]]+=1
branch_at.update({0x561944:'integer_multiplier',0x561965:'fractional_multiplier',0x56198a:'plain_points',0x5618fc:'zero_points',0x564ae3:'mode_starts_at_100',0x564ade:'mode_starts_at_zero',0x564aaa:'local_score_text_reset',0x564b2d:'special_broadcast',0x564b69:'local_component_reset',0x5183ae:'guarded_score_event'})
for at in branch_at:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(at,this=0,args=()):return at,this,[v&0xffffffff for v in args]+([PRINT] if functions[hex(at)].get('diagnostics') else [])
def case(calls,patches=(),changes=None,label='multiline'):
 stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=DIAG and at+len(data)//2>=DIAG+4:
    current=int.from_bytes(bytes.fromhex(data)[DIAG-at:DIAG-at+4],'little');s['callbacks']=current-previous;previous=current
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%25==0:print('Original score display/reset cases:',len(labels),flush=True)
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
def bits(f):return int.from_bytes(struct.pack('<f',f),'little')
def numeric_setup():return [call(0x461a00,UM,[NUMERIC])]
rng=random.Random(0x561890)
# Every floating exponent, both signs, with changing mantissas. Every call runs
# the complete game caller and real initialized CRT before font/QB execution.
for exponent in range(256):
 values=[(exponent<<23)|rng.getrandbits(23),(exponent<<23)|0x7fffff,0x80000000|(exponent<<23)|rng.getrandbits(23)]
 case(numeric_setup()+[call(0x561890,SCORE,[1234567,value]) for value in values],label='all multiplier exponents and signed mantissas, buffer reuse and CRT precision')
for point in [0,1,-1,999,1000,-1000,123456789,0x7fffffff,0x80000000]:
 for language in range(8):
  values=[0,0x80000000,bits(1),bits(-1),bits(1.25),bits(-1.25),0x7f800000,0xffc12345]
  case(numeric_setup()+[call(0x561890,SCORE,[point,value]) for value in values],changes={0x7cefa0:language},label='integer grouping/localization, zeros, exact multipliers, decimal ties and nonfinite display')
for value in [0.05,0.15,0.25,0.35,0.75,1.05,1.25,9.95,99.95,999.95,65535.95,2147483648.,4294967296.]:
 center=bits(value)
 case(numeric_setup()+[call(0x561890,SCORE,[10000,(center+d)|sign]) for sign in [0,0x80000000] for d in [-1,0,1]],label='adjacent floats around decimal carries and integer conversion boundaries')
for skater_id,body_id,screen in [(0x100,0x100,7),(0xffff,0xffffffff,0xffffffff),(0x7fff,0x100,0)]:
 p=[patch(SCORE+8,'<H',skater_id),patch(BODIES+0x14,'<I',body_id),patch(BODIES+0x2b8,'<I',screen),patch(NUMERIC+0x14,'<I',(0xf4d3a70e+screen)&0xffffffff)]
 if skater_id==0x7fff:p[-1]=patch(NUMERIC+0x14,'<I',0xf4d3a70e)
 case(numeric_setup()+[call(0x561890,SCORE,[12345,bits(2.5)])],p,label='signed player ID, screen wrap and missing-player screen-zero fallback')
# Full reset uses both widgets, actual owned list/map cleanup and typed settings.
def reset_patches(count,local,special,mode,missing=False):
 data=bytes(rng.getrandbits(8) for _ in range(0x1550))
 p=[raw(SCORE,data),patch(SCORE+8,'<h',0x7fff if missing else 0x100),patch(SCORE+0x4c,'<3I',ITEMS,250,count),patch(SCORE+0x38,'<5I',count,GRAPH+0x400 if count else 0,GRAPH+0x400+(count-1)*16 if count else 0,0,0),patch(SCORE+0x74,'<B',special),patch(SETTINGS+24,'<I',mode),patch(BODIES+0xbc,'<B',local),patch(COMPONENT+0x18,'<I',0x12345678)]
 for i in range(count):
  p += [patch(ITEMS+i*4,'<I',TRICKS+i*256),patch(GRAPH+0x400+i*16,'<3I',i,TRICKS+0x800+i*256,GRAPH+0x400+(i+1)*16 if i+1<count else 0)]
 return p
for mode in [0,0xbff33600,0x3d6d444f,0xffffffff]:
 for local in [0,1,255]:
  for special in [0,1]:
   for count in [0,1,4]:
    calls=setup(2)+numeric_setup()+[call(0x564a10,SCORE)]*2
    case(calls,reset_patches(count,local,special,mode),label='full reset with owned trick/map records, both histories, modes, local UI and special broadcast')
    assert oracle.word(SCORE+0xc)==(100 if mode in [0xbff33600,0x3d6d444f] else 0)
for missing in [False,True]:
 case(setup()+numeric_setup()+[call(0x564a10,SCORE)],reset_patches(2,1,1,0,missing),label='reset absent skater preserves local UI/component while clearing score')
case([call(0x564a10,SCORE)],[raw(SCORE,b'\xa5'*0x1550)],changes={0x7ce478:0},label='null game context returns without touching score or diagnostics')
# Diagnostic service is called before clears, and can mutate later reads.
for offset,value in [(0x74,1),(8,0x7fff),(0x1538,0xfeedface)]:
 case(setup()+numeric_setup()+[call(0x564a10,SCORE)],reset_patches(0,1,0,0)+[patch(DIAG+8,'<2I',SCORE+offset,value)],label='diagnostic callback ordering and later rereads')
# Real spawned QB scripts guard component events; the target widget's original
# virtual handler delivers the bytecode. Broadcast and screen notifications share
# this actual event path, with no native gameplay substitution.
for subscribed in [False,True]:
 for special in [0,1]:
  event=0x813cc576;script=bytearray(244)
  struct.pack_into('<I',script,0x2c,SCRIPTS+0x1c);struct.pack_into('<I',script,0x94,SCRIPTS+0x34)
  struct.pack_into('<I',script,0xa8,0x44727dae);struct.pack_into('<I',script,0xd4,0x44727dae);script[0xcc]=1;struct.pack_into('<I',script,0xe0,EVENTS if subscribed else 0);struct.pack_into('<I',script,0xec,0x6478e4)
  p=reset_patches(1,1,special,0)+[raw(SCRIPTS,script),patch(WIDGET+0x10,'<I',SCRIPTS),patch(BODIES+0x2bc,'<I',(0x44727dae-0x83321dea)&0xffffffff),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',event,NOTIFY,0,0,0)]
  case(setup()+numeric_setup()+[call(0x41d1d0,SCRIPTS+0xbc,[WIDGET]),call(0x564a10,SCORE)],p,changes={0x6f3538:SCRIPTS,0x6f353c:1},label='actual spawned-script guard and cached QB score reset handler')
assert branches['guarded_score_event']>0 and branches['mode_starts_at_100']>0 and branches['mode_starts_at_zero']>0
assert oracle.coverage['0x473800']>0
scope='Two complete original routines: numeric score display and full score reset. Actual screen lookup/references, localized integer grouping, text ownership/font measurement, combo child rebuilding, both history clears, trick/map release, mode lookup, special-meter broadcast/configuration, component lookup and guarded QB event dispatch execute. The initialized original CRT runs in the oracle; bounded C-locale signed/f32 fixed-one formatting adapters preserve its seventeen-digit intermediate and decimal rounding, including signed zeros and nonfinite text. All arena/global/return/heap/scope bytes compare exactly; diagnostic output is the only instrumented callback. Existing internal bounds and valid widgets/fonts/settings/component pointers remain required. Level activation, movement/startup/rendering and playable training integration remain unfinished.'
fixture={'base':BASE,'memory':'score-display-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callback':{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]}}
path=out/'score-display-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'score-display-diagnostics.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/score_display_diagnostics.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_score_display_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
