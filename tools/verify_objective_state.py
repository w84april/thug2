"""Original objective lookup/state prerequisites with actual QB getters."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-state.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x80000
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
GAME,MANAGER,FLAGS,OBJECTS,LINKS,TABLE,BUCKETS,RING,SKATERS,BODIES,INDEX,OUTPUT,TEXT,SYMBOLS,GRAPH=[BASE+x for x in [0x1000,0x4000,0x8000,0x10000,0x14000,0x18000,0x19000,0x1a000,0x1b000,0x1c000,0x22000,0x22100,0x22200,0x24000,0x30000]]
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
def crc(text):return zlib.crc32(text.lower().replace(b'/',b'\\'))^0xffffffff
put(CONTEXT,'<8I',BASE+0x70000,BASE+SIZE,0,BASE+0x60000,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(GAME+0x20,'<I',FLAGS);put(GAME+0x34,'<I',SKATERS);put(GAME+0x38c,'<I',MANAGER)
put(FLAGS+0x630,'<I',1);put(MANAGER,'<5I',8,LINKS,0,0,0)
for i in range(8):
 put(LINKS+i*16,'<3I',0x100+i,OBJECTS+i*0x100,LINKS+(i+1)*16 if i<7 else 0)
 put(OBJECTS+i*0x100+0x34,'<2i',1,i);put(OBJECTS+i*0x100+0x6c,'<B',0)
 put(SKATERS+i*16,'<4I',0,BODIES+i*0x200,0,SKATERS+(i+1)*16)
 put(BODIES+i*0x200+0xbc,'<B',1 if i==3 else 0)
put(SKATERS+128,'<4I',0,0xffffffff,0,SKATERS+128)
put(TABLE+0x20,'<2I',4,BUCKETS)
for i in range(16):put(BUCKETS+i*12,'<3I',0,0,0)
put(INDEX,'<i',0);put(TEXT,'<8s',b'goal_id\0')
memory[SYMBOLS-BASE:SYMBOLS-BASE+4096*4]=bytes(4096*4)
initial=bytes(memory)
globals_=[['thug_game_context',0x7ce478,4],['thug_script_symbol_buckets',0x6f3624,4]];defaults=[GAME,SYMBOLS]
functions={}
def bind(at,name,argc=0,result='word',this=True):functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'stack_args':list(range(argc))}
bind(0x588380,'thug_objective_object_find',1)
bind(0x588180,'thug_objective_notifications_clear',result='byte')
bind(0x5591b0,'thug_objective_manager',this=False)
bind(0x553e90,'thug_objective_parameters')
bind(0x557f10,'thug_objective_at',2)
bind(0x561430,'thug_objective_find',1)
bind(0x584130,'thug_game_current_level')
bind(0x559110,'thug_objective_unavailable',2,'byte')
bind(0x554220,'thug_objective_is_disabled')
bind(0x5541e0,'thug_objective_state_flag',2)
bind(0x554280,'thug_objective_id')
bind(0x5764b0,'thug_objective_event_parameters',1)
bind(0x566520,'thug_game_local_skater')
bind(0x476a00,'thug_script_get_checksum_string',3,'byte')
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=sorted({int(k,16) for k in functions}|{0x564d90,0x4767c0,0x476630,0x476860,0x476950,0x46cc30,0x401b90,0x478cf0}))
labels=[];outcomes=Counter()
branches={0x557f27:'cache_forward_steps',0x557f3c:'cache_restarts',0x557f6a:'key_outputs',0x561466:'key_hits',0x55912d:'current_level_fallbacks',0x576514:'event_parameter_matches',0x57650a:'event_parameter_misses'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(fn,this=0,args=()):return fn,this,[x&0xffffffff for x in args]
def case(calls,p=(),label='objective',b=None):
 stages=oracle.case(calls,(b.patches() if b else [])+list(p));labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original objective cases:',len(labels),flush=True)
 return stages
rng=random.Random(0x559150)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={}
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert at+len(data)<BASE+SIZE;return at
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2,0,0,key,value&0xffffffff,0)) for key,kind,value in entries]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<II',0,nodes[0] if nodes else 0))
 def symbol(self,key,kind,value):
  bucket=SYMBOLS+(key&4095)*4;previous=self.buckets.get(bucket,0)
  at=self.alloc(struct.pack('<BBHIIII',0,kind,0,key,0,value&0xffffffff,previous));self.buckets[bucket]=at
 def array(self,entries):
  value=entries[0] if len(entries)==1 else self.alloc(struct.pack('<'+'I'*len(entries),*entries))
  return self.alloc(struct.pack('<III',12,len(entries),value))
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(at,'<I',v) for at,v in self.buckets.items()]
# Pure accessors, byte return and exact retained ring bytes.
for value in [0,1,0xffffffff,0x80000000,MANAGER,GRAPH]:
 case([call(0x588180,RING)]*2,[patch(RING+0x800,'<I',value)],label='clear count retains every notification entry')
 case([call(0x584130,FLAGS)],[patch(FLAGS+0x630,'<I',value)],label='current level raw signed word')
 case([call(0x5591b0),call(0x553e90,OBJECTS)],[patch(GAME+0x38c,'<I',value),patch(OBJECTS+0x1c,'<I',value)],label='manager and parameter pointer accessors')
# Masked shifts, collision chains, duplicate keys, null values and null bucket.
for shift in [0,1,4,32,33,36,0xffffffff]:
 for key in [0,1,15,16,0xffffffff,0x80000000]:
  slot=key&((1<<(shift&31))-1)
  # The original computes a uint32 byte address, including multiplication wrap.
  bucket=(BUCKETS-slot*12)&0xffffffff
  for kind in range(4):
   p=[patch(TABLE+0x20,'<2I',shift,bucket),patch(BUCKETS,'<3I',key,OBJECTS if kind==0 else 0,BUCKETS+0x200),patch(BUCKETS+0x200,'<3I',key if kind!=3 else key^1,OBJECTS+0x100 if kind!=2 else 0,0)]
   case([call(0x588380,TABLE,[key])],p,label='direct hash masked shift and duplicate null collisions')
case([call(0x588380,TABLE,[0])],[patch(TABLE+0x20,'<2I',0,0)],label='zero computed bucket pointer')
# Indexed lookup moves forward, restarts backward and stores negative indices
# without traversing. Optional output aliases cache state and node fields.
for cached in [-1,0,1,3,7]:
 for wanted in [-3,-1,0,1,3,7]:
  p=[patch(MANAGER+0xc,'<Ii',LINKS+cached*16 if cached>=0 else 0,cached),patch(INDEX,'<i',wanted)]
  case([call(0x557f10,MANAGER,[INDEX,OUTPUT]),call(0x557f10,MANAGER,[INDEX,0])],p,label='cached indexed traversal and negative indices')
for target in [MANAGER+0x10,INDEX,LINKS+4,MANAGER+0xc]:
 p=[patch(INDEX,'<I',0),patch(LINKS,'<I',LINKS+16 if target==MANAGER+0xc else 0x12345678)]
 case([call(0x557f10,MANAGER,[INDEX,target])],p,label='key output mutation before final cached value read')
# With the input index pointing into the cache, its value is reread as specified.
for cached in [0,1,3,7]:
 p=[patch(MANAGER+0xc,'<Ii',LINKS+cached*16,cached)]
 case([call(0x557f10,MANAGER,[MANAGER+0x10,OUTPUT])],p,label='index aliases cached index')
for key in [0,0x100,0x103,0x107,0xffffffff]:
 for start in [0,LINKS]:
  p=[patch(MANAGER+4,'<I',start),patch(INDEX,'<I',key),patch(MANAGER+0xc,'<Ii',LINKS+16,99)]
  case([call(0x561430,MANAGER,[INDEX])]*2,p,label='key lookup hit miss and retained traversed count')
for at in [MANAGER+0xc,MANAGER+0x10,LINKS,LINKS+4]:
 case([call(0x561430,MANAGER,[at])],[patch(LINKS,'<I',0),patch(LINKS+16,'<I',1)],label='lookup key pointer aliases cleared or incremented fields')
for i in range(64):
 order=[rng.randrange(8) for _ in range(4)];p=[];calls=[]
 # Distinct index slots permit forward/backward sequences without an external write.
 for j,index in enumerate(order):
  p.append(patch(INDEX+j*4,'<I',index));calls.append(call(0x557f10,MANAGER,[INDEX+j*4,OUTPUT+j*4]))
 case(calls,p,label='sequential list cache movement')
# Both availability paths use original level and manager getters. Signed
# indices and levels are exercised where the resulting address remains mapped.
for level in [-2,-1,0,1,2,3]:
 for index in [-1,0,1,9,10,19]:
  for value in [0,1,0xffffffff]:
   effective=2 if level==-1 else level;address=MANAGER+0x4c+4*(index+effective*10)
   p=[patch(FLAGS+0x630,'<I',2),patch(address,'<I',value)] if index!=-1 else []
   case([call(0x559110,MANAGER,[index,level])],p,label='availability grid signed indices and current level')
for flags in [0,1,0x20,0x21,0xff]:
 for index in [-1,0,5]:
  for level in [-1,0,1]:
   for value in [0,1]:
    p=[patch(OBJECTS+0x34,'<ii',level,index),patch(OBJECTS+0x6c,'<B',flags),patch(MANAGER+0x4c+4*(index+(1 if level==-1 else level)*10),'<I',value)]
    case([call(0x554220,OBJECTS)],p,label='explicit disabled bit and availability composition')
# Real QB structures and inclusion aliases control values, IDs and event lists.
for kind in [0,1,2,13]:
 for value in [0,1,0xffffffff,0x80000000]:
  for nested in [False,True]:
   b=Build();name=0xa1234567;entries=[] if kind==0 else [(name,kind,value)];state=b.structure(entries);parent=b.structure([(0xb1234567,10,state)]) if nested else state
   p=[patch(OBJECTS+0x20,'<I',parent)]
   case([call(0x5541e0,OBJECTS,[name,0xb1234567 if nested else 0])],p,label='objective state integer missing wrong type and nested data',b=b)
# Missing nested output keeps its name word. Use a mapped empty structure for
# that word so the retained-pointer behavior has defined downstream reads.
b=Build();empty=b.structure([]);state=b.structure([])
case([call(0x5541e0,OBJECTS,[0x12345678,empty])],[patch(OBJECTS+0x20,'<I',state)],label='missing nested structure retains incoming pointer word',b=b)
for i,text in enumerate([b'goal_id',b'GOAL_ID',b'Goal_Id',b'path/to/node',b'path\\to\\node',b'',b'\xffname']):
 for kind in [0,1,2,13]:
  b=Build();key=crc(text);data=b.structure([] if kind==0 else [(key,kind,0x89abcdef)]);p=[patch(OBJECTS+0x1c,'<I',data),raw(TEXT,text+b'\0'),patch(OUTPUT,'<I',0x13572468)]
  case([call(0x476a00,data,[TEXT,OUTPUT,1]),call(0x554280,OBJECTS)],p,label='text checksum wrapper and goal ID default',b=b)
# The first matching event entry wins; a missing checksum preserves either the
# requested event (first entry) or the prior entry's checksum.
for count in [0,1,2,5]:
 for found in [-1,0,1,4]:
  for missing in [-1,0,1]:
   b=Build();event=0x12345678;entries=[]
   for j in range(count):entries.append(b.structure([] if j==missing else [(0x3c95ccd7,13,event if j==found else j+1)]))
   array=b.array(entries);params=b.structure([(0x3cce31f0,12,array)]);p=[patch(OBJECTS+0x1c,'<I',params)]
   case([call(0x5764b0,OBJECTS,[event]),call(0x5764b0,OBJECTS,[1])],p,label='event parameter array order inline storage and missing checksums',b=b)
# Anonymous structure inclusion and checksum aliases use actual symbol lookup.
for i in range(16):
 b=Build();event=0xabcdef01;alias=0xabcdef02;item=b.structure([(0x3c95ccd7,13,alias)]);b.symbol(alias,13,event)
 array=b.array([item]);included=b.structure([(0x3cce31f0,12,array),(crc(b'goal_id'),13,event)]);symbol=0xeeeee000+i;b.symbol(symbol,10,included)
 params=b.structure([(0,13,symbol)]);state=b.structure([(0,13,symbol)])
 case([call(0x5764b0,OBJECTS,[event]),call(0x554280,OBJECTS)],[patch(OBJECTS+0x1c,'<I',params)],label='recursive QB inclusion and checksum symbol aliases',b=b)
# Local skater selection must stop at its sentinel and return the first flagged
# body, including non-one flag bytes, regardless of sentinel back-links.
for count in range(9):
 for selected in [-1,0,1,3,7]:
  for flag in [1,255]:
   p=[patch(GAME+0x34,'<I',SKATERS)]
   for j in range(count):p += [patch(SKATERS+j*16,'<4I',0,BODIES+j*0x200,0,SKATERS+(j+1)*16),patch(BODIES+j*0x200+0xbc,'<B',flag if j==selected else 0)]
   p.append(patch(SKATERS+count*16,'<4I',0,0xffffffff,0,SKATERS))
   case([call(0x566520,GAME)],p,label='sentinel local skater first flagged body')
assert not oracle.heap_events
assert all(outcomes[k] for k in branches.values())
scope='Fourteen original objective-state prerequisites: hash lookup588380, notification reset588180, manager5591b0, parameters553e90, cached indexed lookup557f10, key lookup561430, level584130, availability559110, disabled predicate554220, state flag5541e0, goal ID554280, event parameters5764b0, local skater566520 and text checksum wrapper476a00. Original QB getters, CRC, symbol/inclusion resolution and context accessor execute unchanged. Full arena bytes, cache/output ordering and global words compare exactly, including missing-output retention and aliases. Internal indexed lists, required arrays and sentinel lists satisfy the original valid-memory preconditions. No native callback or allocator substitution is exercised. Objective-specific virtual actions, notification delivery, enclosing state/floor/ground updates and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'objective-state-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'objective-state-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_state_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
