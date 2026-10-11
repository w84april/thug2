"""Compare balance score accumulation, special events and UI prerequisites to x86."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_score_display.py').read_text().split('rng=random.Random(0x561890)')[0]
prefix=prefix.replace("'score-display.json'","'balance-score.json'")
prefix=prefix.replace('oracle=ScriptHeapOracle(', 'observe=list(dict.fromkeys(observe))\noracle=ScriptHeapOracle(')
prefix=prefix.replace('Original score display/reset cases:', 'Original balance score cases:')
prefix=prefix.replace('oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,', 'debug_hook=oracle.cpu.hook_add(UC_HOOK_CODE,debug_output,')
exec(compile(prefix,str(Path(__file__).with_name('verify_score_display.py')),'exec'))
from unicorn.x86_const import UC_X86_REG_EIP
oracle.cpu.hook_del(debug_hook)
NEW=[(0x562760,'thug_score_set_special',1,'void',True,True,True),
 (0x562e40,'thug_score_recalculate',0,'void',True,True,True),
 (0x564270,'thug_score_add_balance',1,'void',True,True,True),
 (0x4607c0,'thug_ui_object_get_integer',2,'byte',False,False,True),
 (0x4616d0,'thug_ui_object_set_checksum',2,'void',True,False,True),
 (0x4a9100,'thug_ui_set_position',3,'void',False,False,True)]
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
functions['0x4a9100']['float_args']=[0,1]
bind(0x477b80,'thug_script_set_integer',2,heap=True)
EXTRA,PARAMS,RESULT,DIAG=GRAPH+0x8000,GRAPH+0x9000,GRAPH+0x9100,GRAPH+0x2000
memory[DIAG-BASE:DIAG-BASE+0x5000]=bytes(0x5000)
memory[EXTRA-BASE:EXTRA-BASE+0x2000]=bytes(0x2000)
put(PRINT,'<I',DIAG);put(DIAG+4,'<I',SCORE)
put(EXTRA,'<BBHIIII',0,1,0,0xb23d1fb5,0,1,0);put(SYMBOLS+(0xb23d1fb5&0xfff)*4,'<I',EXTRA)
initial=bytes(memory);oracle.initial=initial

def hash_text(data):
 h=0
 for b in data:h=(h*33+b)&0xffffffff
 return h
def cstring(at):
 data=bytearray()
 for i in range(256):
  b=bytes(oracle.cpu.mem_read(at+i,1))[0]
  if not b:return bytes(data)
  data.append(b)
 raise AssertionError('unterminated diagnostic string')
def score_output(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=cstring(oracle.word(sp+4))
 assert fmt in [b'base %d reduction mult %.2f spin mult %.1f score = %i %s\n',b'   total %d\n']
 n=oracle.word(DIAG);assert n<400;oracle.setword(DIAG,n+1)
 row=[hash_text(fmt),oracle.word(sp+8)]+[0]*10
 if fmt.startswith(b'base'):
  row[2:7]=[oracle.word(sp+k) for k in [12,16,20,24,28]]
  row[7]=hash_text(cstring(oracle.word(sp+32)))
 row[8:]=[oracle.word(SCORE+0x14),oracle.word(SCORE+0x5c),oracle.word(SCORE+0x70),bytes(cpu.mem_read(SCORE+0x74,1))[0]]
 cpu.mem_write(DIAG+32+n*48,struct.pack('<12I',*row))
 if oracle.word(DIAG+8) and oracle.word(DIAG+16) in [0,n+1]:oracle.setword(oracle.word(DIAG+8),oracle.word(DIAG+12))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,score_output,begin=0x401c30,end=0x401c30)
NATIVE,NATIVE_STATE,PROGRAM=oracle.stop+0x300,EXTRA+0x200,EXTRA+0x600
assert NATIVE_STATE==0x18f8200
def event_native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);n=oracle.word(NATIVE_STATE);assert n<32
 oracle.setword(NATIVE_STATE,n+1)
 row=[oracle.word(SCORE+0x14),oracle.word(SCORE+0x60),oracle.word(SCORE+0x70),bytes(cpu.mem_read(SCORE+0x74,1))[0]]
 cpu.mem_write(NATIVE_STATE+32+n*16,struct.pack('<4I',*row))
 if oracle.word(NATIVE_STATE+4) and (not oracle.word(NATIVE_STATE+12) or not n):oracle.setword(oracle.word(NATIVE_STATE+4),oracle.word(NATIVE_STATE+8))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,event_native,begin=NATIVE,end=NATIVE)
old_case=case
def case(calls,patches=(),changes=None,label='balance score'):
 stages=old_case(calls,patches,changes,label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=NATIVE_STATE and at+len(data)//2>=NATIVE_STATE+4:
    current=int.from_bytes(bytes.fromhex(data)[NATIVE_STATE-at:NATIVE_STATE-at+4],'little')
    s['callbacks']+=current-previous;previous=current
 return stages
new_branches={0x562e58:'empty_combo',0x562e94:'separator_multiplier',0x562eb2:'explicit_spin_multiplier',
 0x562ebc:'spin_table',0x562ec5:'spin_cap',0x562edf:'repeat_cap',0x562f0b:'stance_bonus',
 0x562fd0:'special_negative',0x562fec:'special_full',0x562ffa:'no_special_increase',
 0x56428b:'check_trick_label',0x5642b5:'check_trailing_limit',0x5642c5:'check_component',0x564302:'balance_accepted',
 0x4a912b:'position_changed',0x4a91c9:'target_changed'}
branch_at.update(new_branches)
for at in new_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
rng=random.Random(0x562e40)

def entries(values,multiplier=1,previous=0,special=0,enabled=0,debug=0):
 # (base, repetition, spin, flags, stance, label); the UI count is independent.
 p=[patch(SCORE+0x4c,'<5I',ITEMS,250,len(values),0,len(values)),patch(SCORE+0x60,'<f',multiplier),
    patch(SCORE+0x14,'<I',0xdeadbeef),patch(SCORE+0x20,'<2I',0x12345678,previous&0xffffffff),
    patch(SCORE+0x70,'<IB',special&0xffffffff,enabled),patch(SCORE+0x8c,'<B',debug),patch(SCORE+0x10,'<I',123)]
 for i,(base,repeat,spin,flags,stance,label) in enumerate(values):
  at=TRICKS+i*256
  p += [patch(at,'<7I',base&0xffffffff,repeat,spin&0xffffffff,0xabcdef01,0x98765432,stance,flags),raw(at+0x1c,label+b'\0'),raw(at+0x5c,b'Balance\0')]
 return p
def item(base=100,repeat=0,spin=0,flags=0,stance=0,label=b'Balance'):
 return (base,repeat,spin,flags,stance,label)

# Full score recalculation: table boundaries, chain grouping and wrapped products.
for spin in [0,1,2,5,6,7,0x7fffffff]:
 for repeat in [0,1,2,3,4,5,6,0x7fffffff]:
  for flags in [0,2,256]:
   values=[item(10001,repeat,spin,flags,1),item(12345,4,5,0),item(-1234,0,0,2),item(20000,repeat,spin,flags)]
   case([call(0x562e40,SCORE)]*2,entries(values,2.5,previous=11,debug=1),label='spin/repetition boundaries, separators and retained chain multiplier')
for i in range(160):
 values=[item(rng.getrandbits(32),rng.randrange(8),rng.randrange(9),rng.choice([0,2,256,258]),rng.choice([0,1,0xffffffff])) for _ in range(rng.randrange(1,18))]
 case([call(0x562e40,SCORE)],entries(values,rng.choice([0,-1,.5,1,2.5,17]),previous=rng.getrandbits(32),special=rng.getrandbits(32),enabled=rng.randrange(2),debug=1),label='wrapped products, signed division, total wrap and special bounds')
for count in [0,-1,-0x80000000]:
 case([call(0x562e40,SCORE)],entries([])+[patch(SCORE+0x5c,'<i',count),patch(SCORE+0x8c,'<B',1)],label='empty and negative internal entry counts')
for multiplier in [0,-0.,.5,-1,1,2.5,1e-30,1e30,float('inf'),-float('inf'),float('nan')]:
 for previous,special in [(0,0),(10000,123),(0,2999),(-2147483648,0),(0,0x7fffffff),(0,0x80000000)]:
  case([call(0x562e40,SCORE)],entries([item(12345)],multiplier,previous,special,1),label='x87 product/conversion and special overflow thresholds')
for active in [0,1,0xffffffff]:
 for base in [2999,3000,3001]:
  case([call(0x562e40,SCORE)],entries([item(base)])+[patch(EXTRA+12,'<I',active)],label='special configuration flag and exact full-meter boundary')
# Diagnostic callbacks change subsequent reads, including count termination.
for offset,value,when in [(0x14,0xfffffff0,1),(0x5c,1,1),(0x5c,3,1),(0x60,bits(3.5),1),(0x8c,0,1),(0x14,17,3),(0x24,0xffffffff,3),(0x70,0x7fffffff,3)]:
 p=entries([item(111),item(222),item(333)],2,debug=1)+[patch(SCORE+0x5c,'<I',2),patch(DIAG+8,'<3I',SCORE+offset,value,when)]
 case([call(0x562e40,SCORE)],p,label='diagnostic mutation and live score/count/multiplier rereads')

# Raw special-state byte and signed skater ID, with actual event delivery below.
for old in [0,1,255]:
 for enabled in [0,1,255,256,257,0xffffffff]:
  for missing in [False,True]:
   case([call(0x562760,SCORE,[enabled])]*2,[patch(SCORE+0x74,'<B',old),patch(SCORE+8,'<h',0x7fff if missing else 0x100)],label='raw low-byte special changes and missing player')

# Complete parent retains its real combo/numeric widgets, fonts, allocation,
# original integer formatting and both cached QB notification scripts.
for count in [0,1,2,10,11,12,13]:
 for flags in [0,2]:
  for base in [19999,20000,20001]:
   values=[item(100)]*max(0,count-1)+([item(base,flags=flags)] if count else [])
   p=entries(values,2)+[patch(SCORE+0x54,'<I',min(count,3))]
   case(setup()+numeric_setup()+[call(0x564270,SCORE,[7])],p,label='complete balance parent trailing-entry and 20000-point gates')
for present in [False,True]:
 for flag in [0,1,255]:
  for label in [b'',b'Balance']:
   p=entries([item(label=label)],2)+[patch(COMPONENT+4,'<I',0x9f9cc949 if present else 0x8bce7e66),patch(COMPONENT+0x1c,'<B',flag)]
   case(setup()+numeric_setup()+[call(0x564270,SCORE,[0xffffffff])],p,label='complete parent label/component gate and wrapped negative increment')
for boundary in [0,1,2,10]:
 values=[item() for i in range(14)];values[boundary]=item(flags=2)
 case(setup()+numeric_setup()+[call(0x564270,SCORE,[2])],entries(values)+[patch(SCORE+0x54,'<I',1)],label='backward chain scan stops at separator before ten-trick cutoff')
for offset,value in [(0x60,bits(3.5)),(0x14,600),(0x5c,1)]:
 p=entries([item(100),item(200)],2,debug=1)+[patch(DIAG+8,'<3I',SCORE+offset,value,1)]
 case(setup()+numeric_setup()+[call(0x564270,SCORE,[123])],p,label='complete parent preserves diagnostic callback effects through text refresh')

# Actual broadcast listeners run cached QB containing an instrumented native
# command. Mutations occur inside delivery, before the caller's clamp/rereads.
fields.update([SCRIPTS+0xec,PROGRAM+2])
def event_handler(event,target,value):
 script=bytearray(244)
 for off,v in [(0x2c,SCRIPTS+0x1c),(0x94,SCRIPTS+0x34),(0xe0,EVENTS),(0xec,0x6478e4)]:struct.pack_into('<I',script,off,v)
 bucket=EXTRA+0x700;head=EXTRA+0x740;node=EXTRA+0x760
 return [raw(SCRIPTS,script),patch(EVENTS,'<IIBBHI',ENTRIES,1,1,0,0,0),patch(ENTRIES,'<5I',event,NOTIFY,0,0,1),
  patch(LISTENERS,'<6I',2,bucket,1,0xffffffff,0,0),raw(bucket,bytes(48)),patch(bucket+(event&3)*12,'<3I',event,head,0),
  patch(head,'<5I',0x6478dc,0xffffffff,0,node,node),patch(node,'<5I',0x6478d8,SCRIPTS,0,head,head),
  raw(PROGRAM,b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24'),patch(NOTIFY_SYMBOL+12,'<I',PROGRAM),patch(CACHE+0x444,'<I',PROGRAM),
  patch(NATIVE_STATE,'<5I',0,target,value,1,SCORE)]
event_cases=0
for meter,enabled,event in [(2999,0,0xd0cd8081),(0x7fffffff,1,0x7ccf5ee2)]:
 for offset,value in [(0x14,600),(0x60,bits(3.5)),(0x70,3500),(0x74,255),(0x24,0xffffffff)]:
  p=entries([item(100)],1,special=meter,enabled=enabled)+event_handler(event,SCORE+offset,value)
  case([call(0x562e40,SCORE)],p,label='special broadcast QB/native mutation before clamp and final score product')
  assert oracle.word(NATIVE_STATE)==1;event_cases+=1
for offset,value in [(0x14,600),(0x60,bits(3.5))]:
 p=entries([item(3000)],1)+event_handler(0xd0cd8081,SCORE+offset,value)
 case(setup()+numeric_setup()+[call(0x564270,SCORE,[3])],p,label='complete parent special and combo QB handlers with one-time native mutation')
 assert oracle.word(NATIVE_STATE)==2;event_cases+=1

# The UI attribute wrappers execute actual parameter allocation, replacement and
# typed lookup. A checksum value must not be silently treated as an integer.
for name in [0,1,0xc22eb9a0,0x863a07e2,0xffffffff]:
 for value in [0,1,0x80000000,0xffffffff]:
  p=[patch(OBJ+0x20,'<I',0),patch(RESULT,'<I',0xdeadbeef)]
  case([call(0x4607c0,OBJ,[name,RESULT]),call(0x4616d0,OBJ,[name,value]),call(0x4607c0,OBJ,[name,RESULT]),call(0x4616d0,OBJ,[name,1])],p,label='lazy parameter allocation and checksum replacement')
  p=[patch(OBJ+0x20,'<I',PARAMS),patch(PARAMS,'<2I',0x6477c8,0),patch(RESULT,'<I',0xdeadbeef)]
  case([call(0x477b80,PARAMS,[name,value]),call(0x4607c0,OBJ,[name,RESULT]),call(0x4607c0,OBJ,[name^2,RESULT])],p,label='present integer attribute and missing output preservation')

# UI position: ordinary results compare bitwise; arithmetic NaNs only classify.
special=[0,0x80000000,bits(1),bits(-1),0x00000001,0x007fffff,0x7f7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for i in range(250):
 coords=[rng.choice(special) for _ in range(10)] if i<100 else [bits(rng.uniform(-100,100)*rng.choice([1e-30,1,1e30])) for _ in range(10)]
 x,y,px,py,w,h,sx,sy,tx,ty=coords
 p=[patch(OBJ+8,'<I',0xa000),patch(OBJ+0xd4,'<4I',x if i%3==0 else bits(17),y if i%3==0 else bits(19),0,0xaaaaaaaa),
    patch(OBJ+0x90,'<2I',tx,ty),patch(OBJ+0xe8,'<2I',sx,sy),patch(OBJ+0x158,'<4I',px,py,w,h)]
 stages=case([call(0x4a9100,OBJ,[x,y,[0,1,256,0xffffffff][i%4]])]*2,p,label='position/target independence, NaNs, zeros, exponent range and unchanged anchors')
 for s in stages:s['float_fields']=[OBJ+0xe0,OBJ+0xe4]

assert all(branches[name]>0 for name in new_branches.values()),dict(branches)
assert oracle.coverage['0x460a20'] and oracle.coverage['0x561890'] and oracle.coverage['0x475790']
scope='Six complete routines: special-meter byte/event setter, trick-score recalculation, balance score accumulation, UI integer attribute lookup/checksum setter and position/target setter. Original game callees run through score UI rebuilding, numeric formatting, QB notifications, script parameter ownership and broadcast delivery. Twelve cases execute actual special/notification QB handlers containing an instrumented native command that mutates score/multiplier/meter fields before subsequent reads. Typed diagnostic arguments and native callback mutations are explicit test boundaries, not recovered gameplay commands. All arena/global/heap bytes and return values compare, except declared arithmetic NaNs by classification; raw coordinate/target copies stay bit-exact. Valid nonnegative spin/repetition table indices, bounded entry/text counts, valid skater/widget/font/component graphs, terminating scripts and successful allocations are internal fixture contracts. Balance rotation/display, complete movement and playable training startup/rendering remain unfinished.'
fixture={'base':BASE,'memory':'balance-score-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'diagnostic_and_native_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_event','original':NATIVE}]}
path=out/'balance-score-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'balance-score-diagnostics.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/balance_score_diagnostics.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_balance_score_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'event_mutation_cases':event_cases,'heap_events':dict(oracle.heap_events),'os_services':dict(os_calls),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
