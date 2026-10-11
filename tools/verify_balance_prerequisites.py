"""Original x86 comparisons for balance parameters and complete timed-trick checks."""
from pathlib import Path
prefix=Path(__file__).with_name('verify_objective_notifications.py').read_text().split('rng=random.Random(0x557360)')[0]
exec(compile(prefix.replace("'objective-notifications.json'","'balance-prerequisites.json'").replace('Original objective notification cases:','Original balance prerequisite cases:'),str(Path(__file__).with_name('verify_objective_notifications.py')),'exec'))
NEW=[(0x5480c0,'thug_network_first_connection',0,'word',False,False,True),
 (0x543300,'thug_player_flag_1',0,'word',False,False,True),
 (0x5434b0,'thug_player_network_index',0,'word',False,False,True),
 (0x564fc0,'thug_game_profile_at',1,'word',False,False,True),
 (0x5807f0,'thug_skater_structure_stat_parameter',2,'double',False,False,True),
 (0x4f90a0,'thug_balance_parameter',1,'double',False,False,True),
 (0x51c950,'thug_timed_tricks_enabled',0,'byte',False,False,True),
 (0x51ce80,'thug_timed_trick_complete',1,'void',True,True,True),
 (0x51d6a0,'thug_timed_tricks_check_balance',3,'void',True,True,True),
 (0x46c270,'thug_input_find_button',1,'word',False,False,True)]
for row in NEW:
 bind(*row)
 if row[0] not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=row[0],end=row[0]);observe.append(row[0])
functions['0x51d6a0']['float_args']=[1]
for at in [0x5805b0,0x580490,0x57b640,0x553220,0x476950,0x4767c0,0x475790]:
 if at not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at);observe.append(at)
EXTRA=BASE+0x1c0000
TIMED,BALANCE,CONTROL,MOD_OWNER,MODIFIER,CON1,CON2=EXTRA,EXTRA+0xb00,EXTRA+0xc00,EXTRA+0x3000,EXTRA+0x3040,EXTRA+0x4000,EXTRA+0x6000
NATIVE=oracle.stop+0x300
assert CONTROL==0x19c0c00
memory[EXTRA-BASE:EXTRA-BASE+0x10000]=bytes(0x10000)
put(BODIES+0x278,'<I',MOD_OWNER);put(MOD_OWNER+0x18,'<I',MODIFIER)
put(BODIES+0x280,'<I',PHYS);put(BODIES+0x290,'<8f',*range(1,9));put(GAME+0x3d0,'<f',0)
put(BALANCE+12,'<I',BODIES);put(CONTROL+24,'<I',TIMED)
put(NETWORK+4,'<2I',CON1,CON2);put(CON1+0x1e84,'<I',8);put(CON2+0x1e84,'<I',8)
put(PROFILES+0x14,'<3I',PROFILE,PROFILE+0x80,0)
for i in range(70):put(TIMED+0x1c+i*36+0x10,'<I',1)
for i,name in enumerate([0x55e516c8,0x41b03551]):
 at=EXTRA+0x8000+i*128;program=at+64;bucket=SYMBOLS+(name&0xfff)*4
 old=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(at,'<BBHIIII',0,7,0,name,0,program,old);put(bucket,'<I',at)
 put(at+32,'<5I',name,program,1,0,0)
 memory[program-BASE:program-BASE+8]=b'\x01\x43'+struct.pack('<I',NATIVE)+b'\x01\x24';fields.add(program+2)
 slot=CACHETABLE+32+(name&3)*12;previous=bytes(memory[slot-BASE:slot-BASE+12]);occupied=struct.unpack_from('<I',previous,4)[0]
 if occupied:memory[at+80-BASE:at+92-BASE]=previous
 put(slot,'<3I',name,at+32,at+80 if occupied else 0)
put(CACHETABLE+8,'<I',13)
if 0x7ce4fd not in index:
 index[0x7ce4fd]=len(globals_);globals_.append(['thug_last_gameplay_flag',0x7ce4fd,1,0]);defaults.append(0)
initial=bytes(memory);oracle.initial=initial

def text_hash(at):
 value=0
 for i in range(128):
  ch=bytes(oracle.cpu.mem_read(at+i,1))[0] if at else 0
  if not ch:return value
  value=(value*33+ch)&0xffffffff
 raise AssertionError('unterminated fixture string')
def native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);script=oracle.word(sp+8)
 n=oracle.word(CONTROL);assert n<128;oracle.setword(CONTROL,n+1)
 entries={};p=oracle.word(params+4) if params else 0
 while p:
  assert len(entries)<8
  entries[oracle.word(p+4)]=(bytes(cpu.mem_read(p,1))[0]>>1,oracle.word(p+8));p=oracle.word(p+12)
 i=entries.get(0x7f8c98fe,(0,0xffffffff))[1]
 record=TIMED+0x1c+i*36 if i<70 else 0
 row=[oracle.word(script+0xc8),len(entries),i,entries.get(0xe288a7cb,(0,0))[1],
      text_hash(entries.get(0x61414d56,(0,0))[1]),text_hash(entries.get(0xc257d69a,(0,0))[1]),
      bytes(cpu.mem_read(record+12,1))[0] if record else 0,oracle.word(record+16) if record else 0,
      oracle.word(record) if record else 0,oracle.word(TIMED+0xa90),bytes(cpu.mem_read(TIMED+0x9f4,1))[0],
      oracle.word(record+44) if i<69 else 0,0,0,0,0]
 cpu.mem_write(CONTROL+64+n*64,struct.pack('<16I',*row))
 if oracle.word(CONTROL+4) and (not oracle.word(CONTROL+12) or not n) and oracle.word(CONTROL+20) in [0,row[0]]:
  width=oracle.word(CONTROL+16);assert width in [1,4]
  cpu.mem_write(oracle.word(CONTROL+4),oracle.word(CONTROL+8).to_bytes(4,'little')[:width])
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,native,begin=NATIVE,end=NATIVE)
old_case=case
def case(calls,patches=(),changes=None,label='balance prerequisites'):
 stages=old_case(calls,patches,changes,label);previous=0
 for s in stages:
  for at,data in s['outputs']:
   if at<=CONTROL and at+len(data)//2>=CONTROL+4:
    current=int.from_bytes(bytes.fromhex(data)[CONTROL-at:CONTROL-at+4],'little');s['callbacks']+=current-previous;previous=current
 return stages
new_branches={0x4f90a7:'explicit_parameters',0x4f90e3:'normal_parameters',0x4f911e:'manual_parameters',0x4f90da:'lip_parameters',0x4f9141:'alternate_parameters',0x4f9114:'unknown_mode',0x51c99a:'profile_gate',0x51cf35:'optional_text',0x51cf65:'completion_write',0x51d726:'threshold_satisfied',0x51d740:'aggregate_notification'}
branch_at.update(new_branches)
for at in new_branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
rng=random.Random(0x51d6a0)

def settings(b,career=1,difficulty=1):
 b.header(SETTINGS+4,b.structure([(0xa1dc81f9,13,0x12345),(0x6dc3d6f1,1,1),(0x1ded1ea4,1,career),(0x5a2c589a,1,0)]))
 b.extra.append(patch(MANAGER+0x398,'<I',b.structure([(0x12345,1,difficulty)])))
 b.symbol(0x6357d57c,2,bits(9));b.symbol(0x6b0f24bc,1,0x11223344);b.symbol(0x11223344,1,0)
def timed_config(career=1,profile_mode=0x0a7be964,enabled=1,available=1,excluded=False):
 b=Build();settings(b,career)
 b.header(PROFILE+0x5c,b.structure([] if profile_mode is None else [(0xa1dc81f9,13,profile_mode)]))
 b.extra += [patch(TIMED+0x9f4,'<B',enabled),patch(TIMED+0xa90,'<I',available),patch(GAME+0x378,'<I',0xe92ecafe if excluded else 0)]
 return b
def record(b,i,kind=0xc1336019,threshold=1,complete=0,disabled=0,extra=True):
 at=TIMED+0x1c+i*36
 b.extra.append(patch(at,'<2IiB3x3I2I',kind,0x11111111,threshold,complete,disabled,b.text(('Balance '+str(i)).encode()),b.text(b'Optional target') if extra else 0,0xaaaaaaaa,0xbbbbbbbb))
 return at

# Stored getters and full sixteen-button search; duplicate names test its priority.
for value in [0,1,2,3,0x100,0x80000000,0xfffffffe,0xffffffff]+[rng.getrandbits(32) for _ in range(24)]:
 case([call(0x5480c0,NETWORK),call(0x543300,PLAYERS),call(0x5434b0,PLAYERS)],
      [patch(NETWORK+4,'<I',value),patch(PLAYERS+0x1d0,'<I',value),patch(BODIES+0x2bc,'<I',value)],label='raw connection/index words and player flag bit')
for receiver in [0,GAME,0xffffffff]:
 for i in [0,1,0xffffffff]:
  case([call(0x564fc0,receiver,[i])],[patch(PROFILES+0x10,'<I',0xdeadbeef)],label='profile wrapper ignores receiver and retains wrapping index')
order=[0,0x20,0x40,0x60,0x160,0x140,0x180,0x1a0,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x1c0,0x1e0]
for name in [0,1,0x80000000,0xffffffff]:
 for first in range(17):
  p=[patch(INPUT+off+0x18,'<I',name if j>=first else name^1) for j,off in enumerate(order)]
  case([call(0x46c270,INPUT,[name]),call(0x46c270,INPUT,[name^0x23456789])],p,label='ordered duplicate checksums and absent button')

# Nested structures retain the complete existing stat evaluator and its graph.
modes=[0x8d10119d,0x255ed86f,0x0ac90769,0xef24413b,0x3506ce64,0xa549b57b,0,0xffffffff]
for mode in modes:
 for explicit in [False,True]:
  for lookup in ['present','missing','alias','nested']:
   b=Build();settings(b)
   pair=b.alloc(struct.pack('<I2f',5,2,12));value=b.structure([(0,5,pair)])
   entries=[] if lookup=='missing' else [(0x76543210,13,0x90123456)] if lookup=='alias' else [(0x76543210,10,value)]
   b.symbol(0x90123456,10,value);container=b.structure(entries)
   if lookup=='nested':container=b.structure([(0,10,container)])
   for j,key in enumerate([0x6b7fdadd,0xb8cc8633,0xfc87cc01,0xbe615d0a]):b.symbol(key,10,container)
   b.symbol(0x76543210,10,value) # A missing nested value must NOT use this fallback.
   b.extra += [patch(BALANCE+0x18,'<I',mode),patch(BALANCE+0x20,'<I',container if explicit else 0)]
   case([call(0x5807f0,BODIES,[0x76543210,container]),call(0x4f90a0,BALANCE,[0x76543210])],b.patches(),label=f'parameter selection {lookup}, mode {mode:x}, explicit {explicit}')
for i in range(120):
 b=Build();settings(b,difficulty=[0,1,2,0xffffffff][i%4])
 special=[0.,-0.,1e-30,1e30,-1e30,float('inf'),-float('inf'),float('nan')]
 x,y=(rng.choice(special),rng.choice(special)) if i<32 else (rng.uniform(-1000,1000),rng.uniform(-1000,1000))
 pairs=[b.alloc(struct.pack('<I2f',5,*xy)) for xy in [(x,y),(-.2,1.4),(.5,1.5)]]
 value=b.structure([(0,5,pairs[0]),(0,1,i%8),(0x9016b4e7,5,pairs[1]),(0xba8fb854,5,pairs[2]),(0x8069179f,2,bits(100))]);container=b.structure([(0x123,10,value)])
 b.symbol(0x6b7fdadd,10,container)
 b.extra += [patch(BALANCE+0x18,'<I',0x8d10119d),patch(BODIES+0x110,'<B',(i//2)%2),patch(SKATER_STATE+0x28,'<B',i%2),patch(MODIFIER+0x74,'<B',(i//4)%2),patch(STATE+0x5f0,'<I',(i//8)%2),patch(BODIES+0x290,'<8f',*([1,3,5,-1,7,10,-2,1e30]))]
 case([call(0x5807f0,BODIES,[0x123,container]),call(0x4f90a0,BALANCE,[0x123])],b.patches(),label='full nested stat arithmetic, selectors, difficulty, bounds and nonfinite values')

# Every enable gate, including the original seeded output on missing profile mode.
for available in [0,1,0xffffffff]:
 for career in [0,1,256]:
  for enabled in [0,1,255]:
   for excluded,profile_mode in [(False,0x0a7be964),(True,0x0a7be964),(False,0),(False,None)]:
    b=timed_config(career,profile_mode,enabled,available,excluded)
    name=b.text(b'Gate test')
    case([call(0x51c950,TIMED),call(0x51ce80,TIMED,[0]),call(0x51d6a0,TIMED,[0,0,0])],b.patches()+[patch(TIMED+0x30,'<I',name)],label='all timed-trick enable gates and missing profile checksum')
for i in [0,1,35,69]:
 for complete in [0,1,255]:
  for extra in [False,True]:
   b=timed_config();record(b,i,threshold=-2147483648 if i&1 else 2147483647,complete=complete,disabled=0xffffffff,extra=extra)
   case([call(0x51ce80,TIMED,[i])]*2,b.patches(),label='direct completion deliberately ignores completed/disabled flags; owned string notifications')
for mode in modes:
 for elapsed in [-float('inf'),-1.,0.,1.,16777216.,16777218.,float('inf'),float('nan')]:
  b=timed_config()
  for i,(kind,threshold) in enumerate([(0xc1336019,-1),(0xd9ffc141,0),(0xb67cff14,1),(0xc1336019,16777217),(0xd9ffc141,2147483647),(0xb67cff14,-2147483648),(0xc1336019,0),(0xc1336019,0)]):
   record(b,i,kind,threshold,complete=255 if i==6 else 0,disabled=1 if i==7 else 0,extra=i%2)
  case([call(0x51d6a0,TIMED,[mode,bits(elapsed),0xffffffff])]*2,b.patches(),label='complete timed scan, mode groups, integer precision, nonfinite time and repeat suppression')
b=timed_config()
for i in range(70):record(b,i,threshold=i,extra=i%2)
case([call(0x51d6a0,TIMED,[0x8d10119d,bits(100),0])],b.patches(),label='all seventy notifications followed by one aggregate notification')
assert oracle.word(CONTROL)==71
# A genuine QB/native callback changes later eligibility and completion ordering.
mutations=[(TIMED+0x9f4,0,1),(TIMED+0xa90,0,4),(GAME+0x378,0xe92ecafe,4),
 (TIMED+0x1c+12,255,1),(TIMED+0x1c+36+8,100,4),(TIMED+0x1c+36+12,255,1),
 (TIMED+0x1c+36+16,1,4),(TIMED+0x1c+36,0xdeadbeef,4)]
for target,value,width in mutations:
 b=timed_config();record(b,0,threshold=0);record(b,1,threshold=0)
 b.extra.append(patch(CONTROL+4,'<5I',target,value,1,width,0x55e516c8))
 case([call(0x51d6a0,TIMED,[0x8d10119d,bits(1),0])],b.patches(),label='real QB native mutation of current/later record or nested enable gate')
 expected_callbacks=3 if target==TIMED+0x1c+12 else 2
 assert oracle.word(CONTROL)==expected_callbacks,(hex(target),oracle.word(CONTROL))
assert all(branches[name]>0 for name in new_branches.values()),dict(branches)
scope='Ten complete routines: balance parameter selection and nested stat evaluation wrapper, timed-trick enable/completion/full balance scan, ordered input checksum lookup, indexed profile wrapper and three stored network/player getters. Original gameplay callees run unchanged; full scans execute owned parameter/string construction, synchronous QB notifications, completion writes and aggregate notification. Eight actual QB/native mutation cases test later record reads and nested enable gates, plus all seventy records and signed threshold precision. The native observer is an instrumented test boundary. Whole arena/global/heap/return bytes compare; only typed arithmetic NaN return values compare by classification. Valid full-sized input/player records, valid stat indices and terminating scripts/successful allocations are internal contracts. Balance animation/physics, complete movement/startup and playable browser integration remain unfinished.'
fixture={'base':BASE,'memory':'balance-prerequisites-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'instrumented_native_callbacks','pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'score-display-diagnostics.wasm','export':'fixture_score_print','slots':[PRINT+4]},{'module':'balance-prerequisites-callbacks.wasm','export':'fixture_timed_trick_native','original':NATIVE}]}
path=out/'balance-prerequisites-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'balance-prerequisites-callbacks.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/balance_prerequisites_callbacks.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(labels),dict(oracle.counts),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_balance_prerequisites_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'branches':dict(branches),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],adapter]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
