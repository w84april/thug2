"""Objective state construction and concrete action prerequisites, original x86."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-actions.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x80000
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
GAME,MANAGER,OBJECTS,LINKS,NETWORK,CONNECTION,PLAYERS,NODES,ITER,SETTINGS,PARENTS,QUEUE,NEWNODE,SYMBOLS,GRAPH,LOG,HEAP=[BASE+x for x in [0x1000,0x2000,0x3000,0x4000,0x5000,0x6000,0x9000,0xb000,0xb200,0xc000,0xd000,0xe000,0xf000,0x14000,0x20000,0x40000,0x60000]]
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def crc(s):return zlib.crc32(s.lower().replace(b'/',b'\\'))^0xffffffff
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(ALLOCATOR+0x124,'<I',ALLOCATOR+0x200)
put(GAME+0x38c,'<I',MANAGER);put(MANAGER,'<5I',8,LINKS,0,0,0)
put(NETWORK,'<3I',0,CONNECTION,0);put(CONNECTION+0x1e84,'<I',0)
put(NETWORK+0x128,'<I',NODES)
for i in range(8):
 put(LINKS+i*16,'<3I',0x100+i,OBJECTS+i*0x100,LINKS+(i+1)*16 if i<7 else 0)
 put(OBJECTS+i*0x100+0x2c,'<I',0)
 put(NODES+i*16,'<4I',0,PLAYERS+i*0x200,0,NODES+(i+1)*16)
 put(PLAYERS+i*0x200+0x1d0,'<I',0)
put(NODES+128,'<4I',0,0xffffffff,0,NODES+128)
put(ITER,'<2I',0x12345678,0);put(QUEUE,'<5I',0,0xffffffff,0,QUEUE,QUEUE)
put(MANAGER+0x18,'<5I',0,0xffffffff,0,MANAGER+0x18,MANAGER+0x18)
memory[SYMBOLS-BASE:SYMBOLS-BASE+4096*4]=bytes(4096*4)
initial=bytes(memory)
globals_=[['thug_game_context',0x7ce478,4],['thug_network_state',0x7cce14,4],['thug_game_settings',0x7ce470,4],['thug_script_symbol_buckets',0x6f3624,4],['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],['thug_script_string_interning',0x6f3570,1],['thug_script_structure_pool_index',0x6f3614,4]]
defaults=[GAME,NETWORK,SETTINGS,SYMBOLS,0,0,0,0];functions={}
def bind(at,name,argc=0,result='byte',heap=False):functions[hex(at)]={'name':name,'this':True,'result':result,'cleanup':argc*4,'memory':heap}
for at,name in [(0x553f90,'is_active'),(0x5519f0,'is_initialized'),(0x554460,'has_selection_flag'),(0x555590,'is_beaten'),(0x554110,'is_complete')]:bind(at,'thug_objective_'+name)
for at,name in [(0x553f50,'mark_active'),(0x553f60,'mark_inactive'),(0x553ea0,'reset_timer')]:bind(at,'thug_objective_'+name,result='void')
bind(0x557f90,'thug_objective_get',2,'word');bind(0x555540,'thug_objective_root_id',result='word')
bind(0x5372c0,'thug_player_first',2,'word');bind(0x533070,'thug_network_slot')
bind(0x45a540,'thug_objective_queue_insert',1,'void');bind(0x55dbe0,'thug_objective_manager_enqueue',1,'void')
bind(0x5566d0,'thug_objective_initialize_state',1,'void',True);bind(0x478670,'thug_script_set_structure_copy',2,'void',True)
observe=set(int(k,16) for k in functions)|{0x44e4f0,0x5532a0,0x537010,0x543320,0x476630,0x476950,0x476860,0x476b40,0x476490,0x477090,0x477130,0x477b80,0x477d40,0x477920,0x478480,0x409070,0x561430,0x5591b0}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=sorted(observe),event_limit=2500)
labels=[];outcomes=Counter()
branches={0x556724:'grouped_states',0x556854:'flat_states',0x556750:'groups_initialized',0x5567e6:'group_flags_initialized',0x556860:'flat_flags_initialized',0x5541ab:'incomplete_group',0x5541a2:'complete_groups',0x553f02:'timer_exit',0x55555b:'parent_steps',0x45a562:'priority_insert',0x45a578:'sentinel_insert'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
def call(fn,this=OBJECTS,args=()):return fn,this,[x&0xffffffff for x in args]
def case(calls,p=(),b=None,label='objective actions'):
 stages=oracle.case(calls,(b.patches() if b else [])+list(p));labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original objective action cases:',len(labels),flush=True)
 return stages
class Build:
 def __init__(self):self.data=bytearray();self.buckets={}
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GRAPH+len(self.data)<LOG;return at
 def text(self,data):return self.alloc(data+b'\0')
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2+(i&1),0x5a,0,key,value&0xffffffff,0)) for i,(key,kind,value) in enumerate(entries)]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<II',0xabcdef01,nodes[0] if nodes else 0))
 def array(self,kind,items,count=None):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items)) if items else 0
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items) if count is None else count,value))
 def symbol(self,name,kind,value):
  bucket=SYMBOLS+(name&4095)*4;at=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,self.buckets.get(bucket,0)));self.buckets[bucket]=at
 def patches(self):return [[GRAPH,self.data.hex()]]+[patch(at,'<I',v) for at,v in self.buckets.items()]
rng=random.Random(0x5566d0)
# All flag bits, mutation order and byte-only returns. Concrete virtual methods.
for flags in range(256):
 case([call(0x553f90),call(0x5519f0),call(0x553f50),call(0x553f90),call(0x553f60),call(0x553f90)],
  [patch(OBJECTS+0x6c,'<2B',flags,flags^0x96)],label='all flag bits and active setter preservation')
for flags in [0,4,8,12,0xff]:
 for network in [0,4,8,12]:
  for mode in [None,0,0xec200eaa,0x1c471c60,0xffffffff]:
   b=Build();settings=b.structure([] if mode is None else [(0xa1dc81f9,13,mode)])
   case([call(0x555590)],b=b,p=[patch(SETTINGS+4,'<II',0,struct.unpack_from('<I',b.data,settings-GRAPH+4)[0]),patch(NETWORK,'<I',network),patch(OBJECTS+0x6c,'<B',flags)],label='network and mode flag selection')
for form in range(6):
 b=Build();nested=b.structure([(0,13,0xdbeb46e2)]);b.symbol(0x1234,10,nested)
 entries=[[],[(0,13,0xdbeb46e2)],[(0xdbeb46e2,1,1)],[(0,13,0x1234)],[(0,13,0)],[(1,13,0xdbeb46e2)]][form]
 params=b.structure(entries)
 case([call(0x554460)],b=b,p=[patch(OBJECTS+0x1c,'<I',params)],label='selection flag includes actual symbol inclusion')
# Timers: signed values and integer wrap; flag preservation; optional alias.
for untimed in [None,0,1,2,0xffffffff]:
 for duration in [None,0,1,120,0xffffffff,0x80000000,0x7fffffff]:
  b=Build();entries=[]
  if untimed is not None:entries.append((0xf0e712d2,1,untimed))
  if duration is not None:entries.append((0x906b67ba,1,duration))
  params=b.structure(entries)
  case([call(0x553ea0)]*2,b=b,p=[patch(OBJECTS+0x1c,'<I',params),patch(OBJECTS+0x50,'<I',0x87654321),patch(OBJECTS+0x6d,'<B',0xff)],label='timer default override wrap and untimed preservation')
# Scalar completion, optional override, irrelevant type and signed comparisons.
words=[0,1,2,0xffffffff,0x80000000,0x7fffffff]
for target in words:
 for done in words:
  for override in [None,0,2,0xffffffff]:
   b=Build();params=b.structure([] if override is None else [(0x1171a555,1,override)]);state=b.structure([])
   case([call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state),patch(OBJECTS+0x58,'<2I',target,done)],label='flat completion signed thresholds and overrides')
for group_count in [0,1,2,4]:
 for incomplete in [-1,0,1,3]:
  for target in [0,1,0xffffffff,0x80000000,0x7fffffff]:
   b=Build();entries=[(0,13,0xe462e527),(9,1,777)]
   for i in range(group_count):
    done=(target-1)&0xffffffff if i==incomplete else target
    nested=b.structure([(0xcf6cd3c1,1,done),(0xb3790f33,1,target)])
    entries.append((0x100+i,10,nested))
   state=b.structure(entries);params=b.structure([])
   case([call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state)],label='grouped completion skips unrelated members and short circuits')
# Value-key wrapper and real parent lookup/cache mutation.
for key in [0,0x100,0x103,0x107,0xffffffff]:
 for ignored in [0,1,0xffffffff]:case([call(0x557f90,MANAGER,[key,ignored])],label='get by value unused argument and misses')
for depth in range(8):
 for terminator in [0,1]:
  b=Build();p=[]
  for i in range(8):
   params=b.structure([(crc(b'goal_id'),13,0x12340000+i)])
   p.extend([patch(OBJECTS+i*0x100+0x1c,'<I',params),patch(OBJECTS+i*0x100+0x2c,'<I',PARENTS+i*4 if i<depth or terminator else 0),patch(PARENTS+i*4,'<I',0x101+i if i<depth else 0)])
  case([call(0x555540)],b=b,p=p,label='root identifier through nullable and zero parent termination')
# First-player iteration, low-byte argument, all-hidden and sentinel/null values.
for hidden in [0,1,7,0xff]:
 for include in [0,1,0x100,0x101,0xffffffff]:
  for stop in [0,1,8]:
   p=[patch(PLAYERS+i*0x200+0x1d0,'<I',4 if hidden&(1<<i) else 0) for i in range(8)]
   if stop<8:p.append(patch(NODES+stop*16+4,'<I',0xffffffff))
   case([call(0x5372c0,NETWORK,[ITER,include])],p,label='first player list visibility and byte argument')
case([call(0x5372c0,NETWORK,[ITER,0])],[patch(NODES+4,'<I',0)],label='null player retains first node')
for value in [0,1,0x7f,0xff]:case([call(0x533070,NETWORK)],[patch(NETWORK+0x38,'<B',value)],label='network slot byte')
# Concrete descending-priority insertion plus the manager wrapper.
for priorities in [[],[0],[10,0,-10],[0,0,0],[0x7fffffff,0,-0x80000000]]:
 for priority in [-0x80000000,-11,-10,-1,0,1,10,11,0x7fffffff]:
  for wrapper in [0,1]:
   head=MANAGER+0x18 if wrapper else QUEUE;p=[];nodes=[QUEUE+0x40+i*0x20 for i in range(len(priorities))]
   p.append(patch(head,'<5I',0,0xffffffff,0,nodes[0] if nodes else head,nodes[-1] if nodes else head))
   for i,node in enumerate(nodes):p.append(patch(node,'<IIiII',0,node,priorities[i],nodes[i+1] if i+1<len(nodes) else head,nodes[i-1] if i else head))
   p.append(patch(OBJECTS if wrapper else NEWNODE,'<IIiII',0,OBJECTS,priority,0,0))
   case([call(0x55dbe0 if wrapper else 0x45a540,MANAGER if wrapper else head,[OBJECTS if wrapper else NEWNODE])],p,label='signed queue order ties and both insertion exits')
# Full state builder then completion then repeat builder, including owned cleanup.
for grouped in [False,True]:
 for count in [0,1,2,5]:
  for duplicate in [False,True]:
   b=Build();items=[]
   for i in range(count):
    names=[0x700+(0 if duplicate else j) for j in range(i%4)]
    if grouped:items.append(b.structure([(0x5b8ab877,13,0x500+(0 if duplicate else i)),(0xcc3c4cc4,12,b.array(13,names))]))
    else:items.append(0x500+(0 if duplicate else i))
   arr=b.array(10 if grouped else 13,items)
   params=b.structure([(0xcc3c4cc4,12,arr),(0x906b67ba,1,60)])
   oldnested=b.structure([(7,1,77)]);state=b.structure([(0,13,0x9876),(22,10,oldnested),(33,3,b.text(b'old state'))])
   case([call(0x5566d0,args=[params]),call(0x554110),call(0x5566d0,args=[params]),call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state),patch(OBJECTS+0x5c,'<I',0)],label='full objective state rebuild flat grouped repeated names and ownership')
# The grouped branch captures signed counts; high-bit counts skip iteration.
for count in [0xffffffff,0x80000000,0x80000001]:
 for inner in [False,True]:
  b=Build();arr=b.array(10,[],count)
  if inner:
   group=b.structure([(0x5b8ab877,13,0x1234),(0xcc3c4cc4,12,b.array(13,[],count))])
   arr=b.array(10,[group])
  params=b.structure([(0xcc3c4cc4,12,arr)]);state=b.structure([])
  case([call(0x5566d0,args=[params]),call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state)],label='signed grouped counts with high bits skip item loops')
# Reserved/duplicate names are replaced in the same order as ordinary setters.
for grouped in [False,True]:
 b=Build();names=[0xb3790f33,0xcf6cd3c1,0,0xb3790f33]
 arr=b.array(13,names)
 if grouped:arr=b.array(10,[b.structure([(0x5b8ab877,13,0x1234),(0xcc3c4cc4,12,arr)])])
 params=b.structure([(0xcc3c4cc4,12,arr)]);state=b.structure([])
 case([call(0x5566d0,args=[params]),call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state),patch(OBJECTS+0x5c,'<I',4)],label='reserved state names and duplicate setter replacement')
# No-array case and distinct input/output parameter objects.
for missing in [False,True]:
 b=Build();params=b.structure([]);state=b.structure([]);supplied=b.structure([] if missing else [(0xcc3c4cc4,12,b.array(13,[0,1,2]))])
 case([call(0x5566d0,args=[supplied]),call(0x554110)],b=b,p=[patch(OBJECTS+0x1c,'<2I',params,state),patch(OBJECTS+0x5c,'<I',3)],label='supplied parameters differ from objective output parameters')
# Deep-copy setter: source may be the old member, and old state is freed after copy.
for kind in ['empty','integers','nested','array','text']:
 for replace in [False,True]:
  b=Build();value=[]
  if kind=='integers':value=[(1,1,1),(2,2,0x7f812345),(0,13,0x456)]
  if kind=='nested':value=[(3,10,b.structure([(1,1,123)]))]
  if kind=='array':value=[(4,12,b.array(13,[1,2,3]))]
  if kind=='text':value=[(5,3,b.text(b'objective/text'))]
  source=b.structure(value);destination=b.structure([(99,10,source)] if replace else [(98,1,77)])
  case([call(0x478670,destination,[99,source])],b=b,label='owned deep copy before replacement with aliased old payload')
scope='Sixteen original objective-action prerequisites including complete state builder5566d0 and owned structure-copy setter478670, concrete activity/initialization/selection/beaten methods553f90/553f50/553f60/5519f0/554460/555590, completion predicate554110, timer553ea0, get557f90/rootID555540, ordered insertion45a540/enqueue55dbe0, firstplayer5372c0 and networkbyte533070. Actual QB access, construction, copying, cleanup, parent cache traversal and network/mode getters execute. Entire arena, global bytes, heap event order and returns compare exactly. Indexed arrays, required group fields, acyclic valid parents and sentinel lists retain original internal preconditions; successful allocation uses the existing memory adapter with original value pools disabled. No gameplay/native callback or derived-float normalization. Full activation/completion actions, notification/state parents and playable integration remain unfinished.'
fixture={'base':BASE,'memory':'objective-actions-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
path=out/'objective-actions-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),dict(oracle.heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_actions_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory']]},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
