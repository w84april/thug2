"""Original eighteen-selector trigger interpreter and five complete helpers."""
import ctypes,hashlib,itertools,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
from prx import entries,decoded_size
out=ROOT/'local/validation/collision';report_path=out.parent/'trick-input.json'
report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x40000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
GAME,GATE,SCALE=BASE+0x1000,BASE+0x3000,BASE+0x4000
STRUCT,MEMBERS,OUTPUT,SYMBOL=BASE+0x5000,BASE+0x5040,BASE+0x5200,BASE+0x5400
PROGRAM,ARRAY,BUCKETS,LOG,POOL,TABLE,HEAP=[BASE+x for x in [0x6000,0x6100,0x8000,0xc000,0xe000,0x10000,0x20000]]
memory=bytearray(b'\xad'*SIZE);rng=random.Random(0x51fda0)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
put(GAME+0x20,'<3I',GATE,0xdeadbeef,SCALE);put(GAME+0x998,'<2H',0,0)
put(GATE+0x498,'<2B',0,0);put(SCALE+0x2e8,'<I',bits(1))
K=[0x7323e97c,0x2b489a86,0x321c9756]
BUTTONS=[0,0xbc6b118f,0xe3006fc4,0x85981897,0x4b358aeb,0xb7231a95,0xa50950c5,0xd8847efa,0x786b8b68,
 0x2b489a86,0x321c9756,0x7323e97c,0x20689278,0x26b0c991,0xbfb9982b,0xc8bea8bd,0xf2f1f64e,0x6bf8a7f4,0x1cff9762,0x767a45d7,0xbd30325b,0x9d2d8850]
DIRECTIONS=BUTTONS[1:9];WINDOW_NAME=0xebdef255
put(GAME+0x99c,'<3I',*K);memory[GAME-BASE+0xa00:GAME-BASE+0xa16]=bytes(22)
memory[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000)
put(BUCKETS+(WINDOW_NAME&0xfff)*4,'<I',SYMBOL)
put(SYMBOL,'<BBHIIII',0x91,1,0x1234,WINDOW_NAME,0xabcdef01,280,0)
put(STRUCT,'<2I',0xabcdef00,MEMBERS);put(ARRAY,'<3I',0,0,0)
initial=bytes(memory)
globals_=[];defaults=[]
def glob(name,at,value,width=4,offset=0):globals_.append([name,at,width,offset]);defaults.append(value)
glob('thug_frame_counter',0x7d1ec8,1000);glob('thug_frame_rate',0x684fd0,bits(1000))
for i,key in enumerate(BUTTONS):glob('thug_input_button_names',0x67d6d8+i*4,key,offset=i*4)
for name,at,value,width in [('string_pool',0x6f3574,POOL,4),('string_pool_size',0x6f357c,0x2000,4),
 ('string_interning',0x6f3570,0,1),('string_cursor',0x6f3578,POOL,4),('string_entries',0x6f3580,TABLE,4),
 ('string_count',0x6f3584,0,4),('symbol_buckets',0x6f3624,BUCKETS,4)]:glob('thug_script_'+name,at,value,width)
for export,at,size in [('thug_expression_temporary',0x6f2348,16),('thug_script_parser_expression',0x6f2370,504),('thug_script_parser_value',0x6f2568,16)]:
 for offset in range(0,size,4):glob(export,at+offset,0,offset=offset)
for export,at in [('thug_random_state',0x690fd4),('thug_random_alternate_state',0x690fc8)]:
 for offset,value in zip(range(0,12,4),[0x12345678,0x98765432,0x31415926]):glob(export,at+offset,value,offset=offset)
for export,at in [('thug_current_script',0x6f3530),('thug_script_branch_first',0x6f2358),('thug_script_branch_last',0x6f235c),('thug_script_branch_count',0x6f2360)]:glob(export,at,0)
functions={}
def bind(at,name,argc,result='byte',this=True,heap=False):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
NEW=[0x51ea40,0x51eb80,0x51ec40,0x51ecc0,0x51f7a0,0x51fda0]
bind(0x51ea40,'thug_input_is_direction',0,this=False);functions['0x51ea40'].update(register_args={'eax':0},stack_args=[])
bind(0x51eb80,'thug_skater_clear_input_marks',0,'void')
bind(0x51ec40,'thug_skater_read_trigger_arguments',3,'word')
bind(0x51ecc0,'thug_skater_set_matched_input',1,'void')
bind(0x51f7a0,'thug_skater_match_two_inputs',4)
bind(0x51fda0,'thug_skater_match_trick_input',4)
bind(0x471b00,'thug_script_parse_array',3,'word',False,True)
observe=NEW+[0x51ebd0,0x51ecf0,0x51f6b0,0x476490,0x478f60,0x5be970,0x6236fc,0x471b00,0x471860]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe,event_limit=160)
oracle.cpu.mem_write(0x6f2578,bytes(4));oracle.cpu.mem_write(0x6f2580,bytes(8))
SELECTORS={0x14fe9b7d:(2,0x51ffe6),0x2c434c90:(2,0x51fe3e),0x395ec2d4:(2,0x5200d3),
 0x3c3028f4:(2,0x5202a0),0x3f369070:(2,0x5202e6),0x3fe7c311:(3,0x5205d8),0x61b8fce2:(1,0x5204d7),
 0x696e5e66:(2,0x5207cd),0x7d482318:(2,0x52097f),0x7fa5cdbb:(1,0x520ac6),0x823b8342:(1,0x520e8b),
 0xa2e042d7:(3,0x520c6b),0xa8123ecf:(3,0x520fe0),0xac2b1445:(3,0x52103a),0xb6258557:(1,0x521217),
 0xc1ad35c0:(3,0x521740),0xf630dae5:(3,0x521552),0xffb718bd:(2,0x5213df)}
branches=Counter();branch_names={at:f'{selector:08x}' for selector,(_,at) in SELECTORS.items()}
def branch(cpu,at,size,user):branches[branch_names[at]]+=1
for at in branch_names:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
labels=[];outcomes=Counter()
def call(fn,args=(),this=GAME):return (fn,this,list(args))
def case(calls,p=(),changes=None,label='trick input'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 result=oracle.case(calls,p,changes);labels.append(label);return result
def history(rows,head=50,now=1000):
 p=[patch(GAME+0x998,'<2H',len(rows),head)]
 for i,(key,kind,mask,age,marked) in enumerate(rows):
  p.append(patch(GAME+0x38+((head-i)%100)*24,'<4IB3sI',(now-age)&0xffffffff,kind,key,0xabcd0000+i,marked,b'xyz',mask))
 return p
def row(key,kind=1,mask=0,age=0,marked=0):return key,kind,mask,age,marked
def arguments(selector,keys=K,window=280,tag=2):
 n=SELECTORS.get(selector,(0,0))[0];values=[selector,*keys[:n],window]
 p=[]
 for i,value in enumerate(values):p.append(patch(MEMBERS+i*16,'<BBHIII',tag if i==len(values)-1 else 26,0x75,17,0,value,MEMBERS+(i+1)*16 if i+1<len(values) else 0))
 return p
def held(value,keys=K):
 p=[]
 for key in keys:p.append(patch(GAME+0xa00+(BUTTONS.index(key) if key in BUTTONS else 0),'<B',value))
 return p
def trigger(selector,rows=(),keys=K,head=50,window=280,commit=0x100,ignore=0x100,scale=0,p=(),changes=None,repeat=1,label='selector'):
 stages=case([call(0x51fda0,[STRUCT,commit,ignore,scale]) for _ in range(repeat)],arguments(selector,keys,window)+history(rows,head)+list(p),changes,f'{label} {selector:08x}')
 for s in stages:outcomes[f'{selector:08x}:{s["result"]}']+=1
 return stages

for key in DIRECTIONS+[0,1,0xffffffff,*[d^1 for d in DIRECTIONS],*[rng.getrandbits(32) for _ in range(100)]]:
 stages=case([call(0x51ea40,[key],0)],label='eight direction checksums and nonmatches');assert stages[0]['result']==int(key in DIRECTIONS)
for n,head in itertools.product([0,1,2,99,100],[0,1,50,99]):
 rows=[row(K[i%3],mask=rng.getrandbits(32),marked=[0,1,255][i%3]) for i in range(n)]
 case([call(0x51eb80),call(0x51eb80)],history(rows,head),label='clear active ring only, twice')
for offset in [-12,-8,-4,0,4,8,12,0x100]:
 ptr=GAME+0x99c+offset
 case([call(0x51ecc0,[ptr])],[patch(ptr,'<3I',0x12345678,0x87654321,0xfeedabcd)],label='forward copies with all aligned overlaps')
placeholders=[0x03749393,0x7473a305,0x9a7dc229]
for keys in itertools.permutations(placeholders):
 for tag in [2,3,0,1,4,26,27,254,255]:
  for output in [OUTPUT,GAME+0x99c,GAME+0x998]:
   p=arguments(0xc1ad35c0,keys,280 if tag in [2,3] else WINDOW_NAME,tag)
   case([call(0x51ec40,[MEMBERS+16,3,output])],p,label='argument placeholders, raw tag and output alias')
for n in [0,0xffffffff,0x80000000,1,2,3]:
 first=MEMBERS+16
 p=[]
 for i in range(4):p.append(patch(first+i*16,'<BBHIII',2,0x75,17,0,37+i,first+(i+1)*16))
 case([call(0x51ec40,[first,n,OUTPUT])],p,label='signed argument count and arbitrary key tags')
# Output can change the next member value; the following read must see it.
case([call(0x51ec40,[MEMBERS+16,2,MEMBERS+40])],arguments(0x7d482318,[MEMBERS+48,K[1],K[2]]),label='argument output aliases later member payload and retains a valid next link')
# A write to the current next link changes traversal to another valid member.
case([call(0x51ec40,[MEMBERS+16,1,MEMBERS+28])],arguments(0x7d482318,[MEMBERS+48,K[1],K[2]]),label='argument output aliases current next link')

pair_patterns=[[],[row(K[0])],[row(K[1])],[row(K[0]),row(K[1])],[row(K[1]),row(K[0])],
 [row(K[0]),row(K[2]),row(K[1])],[row(K[0]),row(K[2],2),row(K[1])],
 [row(K[0]),row(K[2],mask=0x100),row(K[1])],[row(K[0]),row(K[0]),row(K[1])]]
for rows,head,equal in itertools.product(pair_patterns,[0,1,99],[False,True]):
 case([call(0x51f7a0,[K[0],K[0] if equal else K[1],280,0x100])],history(rows,head),label='two-input helper partial marks, interruptions and equal keys')

# Successful histories are newest first. Each truncation exercises an incomplete
# transition, and inserted releases, masked records and third keys test rejection.
patterns={0x14fe9b7d:[(0,1),(1,1)],0x2c434c90:[(1,2),(0,1),(0,1)],0x395ec2d4:[(0,2),(1,2)],
 0x3c3028f4:[(1,1),(0,1)],0x3f369070:[(0,1),(1,1)],0x3fe7c311:[(2,1),(1,2),(1,1),(0,2),(0,1)],
 0x61b8fce2:[(0,2)],0x696e5e66:[(1,2),(1,1),(0,2)],0x7d482318:[(1,1),(0,1)],
 0x7fa5cdbb:[(0,2),(0,1)],0x823b8342:[(0,1)],0xa2e042d7:[(2,1),(1,1),(0,2),(0,1)],
 0xa8123ecf:[],0xac2b1445:[(0,2),(1,2),(2,1)],0xb6258557:[(0,1)],0xc1ad35c0:[(2,1),(1,1),(0,1)],
 0xf630dae5:[(2,1),(1,1),(0,1)],0xffb718bd:[(1,2),(0,1)]}
for selector,pattern in patterns.items():
 good=[row(K[k],kind) for k,kind in pattern]
 success=trigger(selector,good,p=held(1),label='complete acceptance path');assert success[0]['result']==1,hex(selector)
 for length in range(len(good)+1):
  for head in [0,1,99]:trigger(selector,good[:length],head=head,label='truncated pattern')
 for i in range(len(good)+1):
  for extra in [row(K[0],2),row(K[1],2),row(K[2],2),row(77),row(77,mask=0x100),row(K[1],3,marked=255),row(0,0,marked=255)]:
   trigger(selector,good[:i]+[extra]+good[i:],p=held(255),repeat=2,label='interrupted/repeated pattern')
 for keys in [K,[K[0],K[0],K[2]],[K[0],K[1],K[1]],[K[0]]*3,[77,88,99],placeholders]:
  rows=[row(keys[k] if keys!=placeholders else K[[1,2,0][k]],kind,marked=255) for k,kind in pattern]
  for mask in [0,0x100,0xffffffff]:trigger(selector,rows,keys=keys,commit=mask,p=held(255,keys),label='equal keys, unknown held names, placeholders and commit mask')
 for flags in [0,1,0xff]:trigger(selector,good,p=held(flags),label='held input state')
 for age in [0,279,280,281,0x80000000,0xffffffff]:
  for pos in range(len(good)):
   rows=list(good);r=rows[pos];rows[pos]=(*r[:3],age,r[4])
   trigger(selector,rows,p=held(1),label='window cutoff and unsigned age')
 for gate,flag in itertools.product([GATE+0x498,GATE+0x499],[1,255]):
  trigger(selector,[row(K[0],marked=255)],p=[patch(gate,'<B',flag)],label='early gate retains marks')
case([call(0x51fda0,[0,0x100,0x100,1])],[patch(GAME+0x20,'<I',0)],label='null trigger before invalid gate')
case([call(0x51fda0,[STRUCT,0,0,0])],[patch(STRUCT+4,'<I',0)],label='no unnamed trigger selector')
for unknown in [0,1,0xffffffff,0x7fa5cdbc]:trigger(unknown,[row(K[0],marked=255)],label='unknown selector clears marks')

for selector in SELECTORS:
 for i in range(70):
  keys=rng.choice([K,[K[0]]*3,[K[1],K[0],K[1]],DIRECTIONS[:3]])
  rows=[row(rng.choice([*keys,77,*DIRECTIONS]),rng.choice([0,1,1,1,2,2,3]),rng.choice([0,0,0x100,0xffffffff]),rng.choice([0,1,50,279,280,0xffffffff]),rng.choice([0,0,1,255])) for _ in range(rng.randrange(13))]
  trigger(selector,rows,keys=keys,head=rng.randrange(100),commit=rng.choice([0,1,0x100,0xffffffff]),ignore=rng.choice([0,1,0x100]),p=held(rng.choice([0,1,255]),keys),label=f'seeded mixed history {i}')
# Expiry and exhaustion have selector-specific cleanup. Full rings wrap exactly.
for selector in SELECTORS:
 for head in [0,1,50,99]:
  rows=[row(77,3,marked=i%2) for i in range(99)]+[row(K[0],1,marked=255)]
  trigger(selector,rows,head=head,p=held(1),label='full 100-record ring')
# All eight directional codes affect grab logic, but only cardinal directions
# are skipped by the special three-record matcher.
for direction in DIRECTIONS:
 for matched in [[direction,0,0],[direction,DIRECTIONS[(DIRECTIONS.index(direction)+1)%8],0],[0,0,0]]:
  for tail in [row(K[0]),row(77,age=280),row(77,2)]:
   trigger(0xb6258557,[row(K[0]),row(direction),tail],p=[patch(GAME+0x99c,'<3I',*matched)],label='last remembered direction and oldest grab key')
 trigger(0x696e5e66,[row(direction),row(K[1],2),row(direction,2),row(K[1]),row(K[0],2)],label='cardinal-only three-record skip')
# AirTrickLogic's held branch marks a release-independent key without age/mask
# filtering before searching for the main key with its actual window.
for age,mask,present in itertools.product([0,280,0xffffffff],[0,0x100],[False,True]):
 rows=([row(K[1],1,mask,age)] if present else [])+[row(K[0])]
 trigger(0x14fe9b7d,rows,p=held(255),label='held air trick unfiltered preliminary mark')
# Press converts unsigned windows through original PC24 arithmetic only when
# the low flag byte is set and the stored scale compares below one.
for value in [0,0x80000000,1,0x007fffff,0x3e800000,0x3f7fffff,0x3f800000,0x40000000,0xbf800000,0x7f800000,0xff800000,0x7f812345,0x7fc12345]:
 for window,flag in itertools.product([0,1,280,0x1000001,0x7fffffff,0x80000000,0xffffffff],[0,1,0x100,0xff]):
  trigger(0x823b8342,[row(K[0],age=300,marked=255)],window=window,scale=flag,p=[patch(SCALE+0x2e8,'<I',value)],label='scaled Press numeric and low-byte boundaries')
for now in [0,1,0x7fffffff,0x80000000,0xffffffff]:
 for age in [0,279,280,0xffffffff]:
  # At high frame counts PC24 can round the absolute timer; derive the actual
  # frame clock via the separately validated exact conversion, not Python float.
  fn=0x5be970
  if hex(fn) not in functions:bind(fn,'thug_frame_time',0,'word',False)
  time=case([call(fn,this=0)],changes={0:now},label='absolute frame clock')[0]['result']
  trigger(0x823b8342,[row(K[0],age=age)],p=history([row(K[0],age=age)],now=time),changes={0:now},label='wrapped absolute timestamps')

# Decode the installed archive with the validated original LZSS port, then feed
# its Wallplant_Trick array through the complete original QB parser and matcher.
archive_path=ROOT/'local/game-files/Game/Data/pre/qb_scripts.prx';archive_bytes=archive_path.read_bytes()
archived=next(e for e in entries(archive_bytes) if e.name=='scripts\\game\\skater\\walltricks.qb')
assert archived.compressed and decoded_size(archived.payload)==archived.size
decoder=ctypes.CDLL(str(ROOT/'local/validation/lzss.dylib')).thug_lzss_decode_unchecked
decoder.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_void_p,ctypes.c_uint32];decoder.restype=ctypes.c_void_p
dictionary=ctypes.create_string_buffer(4096);decoded=ctypes.create_string_buffer(archived.size)
assert decoder(dictionary,archived.payload,decoded,len(archived.payload))-ctypes.addressof(decoded)==archived.size
script=decoded.raw;assert hashlib.sha256(script).hexdigest()=='2d5e5285ac959ec0bccd22cd2f2fd5bea4f61fa34ca24b612c8a9546999a8cb1'
shipped=script[1585:1608];assert hashlib.sha256(shipped).hexdigest()=='adc6ae5e51da679c4433eee82e0d1d3d608e461750e8cad24be6e0d8634231ab'
# Parse once to learn deterministic heap placement, then repeat the entire
# chain in every recorded case. No parsed object replaces original QB parsing.
case([call(0x471b00,[ARRAY,PROGRAM,0],0)],[raw(PROGRAM,shipped)],label='archived Wallplant_Trick parse')
parsed=oracle.word(ARRAY+8);assert oracle.word(ARRAY+4)==1 and BASE<=parsed<BASE+SIZE
asset_cases=0
for age,scale in itertools.product([0,279,280,281],[bits(1),bits(0.5)]):
 p=[raw(PROGRAM,shipped),patch(SCALE+0x2e8,'<I',scale)]+history([row(K[0],age=age)])
 result=case([call(0x471b00,[ARRAY,PROGRAM,0],0),call(0x51fda0,[parsed,0,0,1])],p,label='archived Wallplant_Trick parse then match with game arguments')
 assert result[-1]['result']==int(age<(280 if scale==bits(1) else 560));asset_cases+=1

assert all(branches[n] for n in branch_names.values())
assert all(outcomes[f'{selector:08x}:{value}'] for selector in SELECTORS for value in [0,1])
scope='Six complete routines: direction classification 51ea40, mark clearing 51eb80, trigger arguments 51ec40, matched-key copying 51ecc0, two-key matching 51f7a0, and all eighteen selectors of trigger interpreter 51fda0. Exact full-arena comparison covers stateful press/release order, held buttons, equal keys, aliases, directional exclusions, pending mark cleanup, mask commits, wrapped rings/timestamps and PC24 scaled unsigned windows. The archived Wallplant_Trick QB array is parsed by the original parser before eight matches using the game call arguments. All game callees execute unchanged; only successful generic heap allocation for parser storage uses the existing diagnostic allocator. Valid rings/member chains and required configuration are internal contracts. Complete wallplant/airborne integration, startup, rendering and playable training remain unfinished.'
fixture={'base':BASE,'memory':'trick-input-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'trick-input-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('Original trick input:',len(labels),sum(oracle.counts.values()),dict(branches),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_trick_input_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'selector_entries':dict(branches),'selector_outcomes':dict(outcomes),'heap_events':dict(oracle.heap_events),'scope':scope,
 'real_asset':{'archive':str(archive_path.relative_to(ROOT)),'archive_sha256':hashlib.sha256(archive_bytes).hexdigest(),
 'member':archived.name,'member_sha256':hashlib.sha256(script).hexdigest(),'array_offset':1585,'array_end':1608,
 'array_sha256':hashlib.sha256(shipped).hexdigest(),'cases':asset_cases},
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'script-values-memory.wasm',archive_path]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(labels),sum(oracle.counts.values()))
