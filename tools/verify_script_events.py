"""Original event unsubscription, listener destruction and script-event cleanup."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-events.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x20000
CONTEXT,ADAPTER,MANAGER,OBJECTS,TABLE,BUCKETS,COLLISIONS=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x500,BASE+0x800,BASE+0xa00,BASE+0xe00
SENTINELS,NODES,POOL0,POOL1,EVENTS,ENTRIES,SCRIPT,OTHER=BASE+0x1000,BASE+0x2000,BASE+0x5100,BASE+0x5200,BASE+0x6000,BASE+0x6020,BASE+0x6800,BASE+0x6c00
LOG,HEAP=BASE+0x8000,BASE+0xa000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def call(at,this,*args):return (at,this,list(args))
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,ENTRIES+4,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(OBJECTS,'<5I',0xcccc,0xdddd,0,0,TABLE)
put(TABLE,'<6I',3,BUCKETS,0,0xffffffff,0,0xadadad02)
memory[BUCKETS-BASE:BUCKETS-BASE+96]=bytes(96)
put(POOL0,'<6I',SENTINELS,SENTINELS+0x1000,0x11111111,0x22222222,50,BASE+0x5300)
put(POOL1,'<6I',NODES,NODES+0x3000,0x11111111,0x22222222,50,BASE+0x5400)
put(EVENTS,'<2I',ENTRIES,0)
put(SCRIPT+0xe0,'<I',EVENTS);put(SCRIPT+0xcc,'<B',0x90)
for i in range(16):
 s=SENTINELS+i*0x100;put(s,'<5I',0x6478dc,0xffffffff,0x12345678,s,s)
 for j in range(8):
  n=NODES+i*0x100+j*20;put(n,'<5I',0x6478d8 if j&1 else 0x6478dc,SCRIPT,0x98765432,n,n)
# Distinct owned parameter graphs let the clear-group tests observe deep cleanup.
for i in range(16):
 params=BASE+0x7000+i*0x60;component=params+8;text=params+32
 put(params,'<2I',0xabcdef01,component);put(component,'<BBHIII',7,0x75,0x9876,100+i,text,0)
 data=b'event parameters '+str(i).encode()+b'\0';memory[text-BASE:text-BASE+len(data)]=data
 put(ENTRIES+i*20,'<5I',1+i*8,0xbeef0000+i,i%3,params,0x11223344+i)
initial=bytes(memory);(out/'script-events-memory.bin').write_bytes(initial)
globals_=[['thug_script_listener_pool_index',0x6f0fc8,4],['thug_script_listener_pools',0x6f0fd0,4,0],['thug_script_listener_pools',0x6f0fd4,4,4],
 ['thug_object_lookup_manager',0x6f0fc0,4],['thug_lookup_node_pool',0x7d1808,4],['thug_script_string_pool',0x6f3574,4],
 ['thug_script_string_pool_size',0x6f357c,4],['thug_script_string_interning',0x6f3570,1]]
defaults=[0,0,0,OBJECTS,0,0,0,0];functions={}
def bind(at,n,cleanup=0,this=True,heap=True,result='void'):
 functions[hex(at)]={'name':n,'this':this,'memory':heap,'result':result,'cleanup':cleanup}
bind(0x588190,'thug_object_table_next',heap=False,result='byte')
bind(0x4624d0,'thug_script_listener_free',this=False)
bind(0x462530,'thug_script_listener_destroy',heap=False)
bind(0x462550,'thug_script_listener_delete',4,result='word');bind(0x462710,'thug_script_listener_list_delete',4,result='word')
bind(0x4626b0,'thug_script_listener_remove',4);bind(0x463450,'thug_script_unsubscribe',8)
bind(0x462b90,'thug_script_unsubscribe_all',4);bind(0x45fa60,'thug_script_events_unsubscribe',4)
bind(0x45fe60,'thug_script_events_clear_group',4);bind(0x473010,'thug_script_clear_events')
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,
 observe=[int(k,16) for k in functions]+[0x5ba3b0,0x5ba400,0x5b80d0,0x477130,0x409070])
labels=[]
def case(calls,patches=(),changes=None,label='synthetic'):
 labels.append(label);return oracle.case(calls,patches,changes)
# Scan empty/inline/collision buckets and preserve the iterator after exhaustion.
for shift in [0,1,2,3,32,33,34,35,31,63,255]:
 for layout in range(5):
  size=1<<(shift&31);patches=[patch(TABLE,'<5I',shift,BUCKETS,3,0xffffffff,0)]
  if size<=8:
   if layout==1:patches+=[patch(BUCKETS,'<3I',0,OTHER,0)]
   if layout==2:patches+=[patch(BUCKETS+(size-1)*12,'<3I',size-1,OTHER,0)]
   if layout>=3:patches+=[patch(BUCKETS,'<3I',0,OTHER if layout==3 else 0,COLLISIONS),patch(COLLISIONS,'<6I',8,SCRIPT,COLLISIONS+12,16,OTHER,0)]
  case([call(0x588190,TABLE)]*6,patches,label='iterator start and exhaustion')
for bucket in [0,7,8,0xffffffff,0xfffffffe,0x80000000]:
 if bucket not in [0xfffffffe,0x80000000]:case([call(0x588190,TABLE)],[patch(TABLE+12,'<2I',bucket,0)])
 for next_ in [0,COLLISIONS+12]:
  case([call(0x588190,TABLE)],[patch(TABLE+12,'<2I',bucket,COLLISIONS),patch(COLLISIONS,'<6I',8,0,next_,16,0,0)]) if bucket not in [0xfffffffe,0x80000000] or next_ else None
# Pool membership, selected/alternate ordering, null fallback and count wrap.
for selected in [0,1]:
 for pools in [(0,0),(POOL0,0),(0,POOL1),(POOL0,POOL1),(POOL0,POOL0)]:
  for at in [0,SENTINELS-4,SENTINELS,SENTINELS+4,NODES,NODES+0x3000,BASE+0x5500]:
   case([call(0x4624d0,0,at)],changes={0:selected,1:pools[0],2:pools[1]})
# Link layouts for deleting destructors and first-match removal.
def ring(values,slot=0):
 s=SENTINELS+slot*0x100;nodes=[NODES+slot*0x100+j*20 for j in range(len(values))]
 chain=[s,*nodes];p=[patch(s,'<5I',0x6478dc,0xffffffff,0x12345678,nodes[0] if nodes else s,nodes[-1] if nodes else s)]
 for j,(n,v) in enumerate(zip(nodes,values)):
  p.append(patch(n,'<5I',0x6478d8 if j&1 else 0x6478dc,v,0x98765432,chain[(j+2)%len(chain)],chain[j]))
 return p
for length in [0,1,3]:
 for target in range(max(length,1)):
  node=SENTINELS if not length else NODES+20*target
  for fn in [0x462530,0x462550,0x462710]:
   for flags in ([0] if fn==0x462530 else [0,1,2,255,256,257]):
    case([call(fn,node,*([] if fn==0x462530 else [flags]))],ring([SCRIPT]*length))
for values in [[],[SCRIPT],[OTHER],[SCRIPT,OTHER],[OTHER,SCRIPT],[SCRIPT,SCRIPT],[OTHER,SCRIPT,OTHER], [OTHER]*7+[SCRIPT]]:
 for value in [SCRIPT,OTHER,0xdeadbeef,0xffffffff]:
  case([call(0x4626b0,SENTINELS,value)]*2,ring(values))
# Build lookup buckets with several independent lists, including hash collisions.
def subscriptions(entries):
 patches=[];buckets={};cursor=COLLISIONS
 for i,(key,values) in enumerate(entries):
  patches+=ring(values,i);slot=key&7;s=SENTINELS+i*0x100
  if slot not in buckets:buckets[slot]=[key,s,0]
  else:
   patches.append(patch(cursor,'<3I',key,s,buckets[slot][2]));buckets[slot][2]=cursor;cursor+=12
 for slot,data in buckets.items():patches.append(patch(BUCKETS+slot*12,'<3I',*data))
 patches.append(patch(TABLE+8,'<I',len(entries)));return patches
layouts=[[],[(1,[])],[(1,[SCRIPT])],[(1,[OTHER])],[(1,[SCRIPT,OTHER,SCRIPT])],
 [(1,[SCRIPT]),(9,[SCRIPT]),(17,[SCRIPT]),(2,[OTHER]),(7,[SCRIPT])],
 [(1,[OTHER]),(9,[SCRIPT]),(17,[OTHER,SCRIPT]),(25,[]),(2,[SCRIPT,SCRIPT])]]
rng=random.Random(0x462b90)
for _ in range(30):layouts.append([(i*8+rng.randrange(8),[rng.choice([SCRIPT,OTHER,0xdeadbeef]) for _ in range(rng.randrange(5))]) for i in range(rng.randrange(1,13))])
for entries in layouts:
 for pool in [0,POOL0]:
  patches=subscriptions(entries)
  for event in [1,9,17,2,7,0xdeadbeef]:
   case([call(0x463450,OBJECTS,event,SCRIPT)]*2,patches,changes={1:pool},label='single event unsubscribe')
  case([call(0x462b90,OBJECTS,SCRIPT)]*2,patches,changes={1:pool},label='all event unsubscribe')
# Explicit event table, wildcard/group disposal, and the script-wide cleanup path.
for count in [0,1,3,8,16,0x80000000,0xffffffff]:
 for group in [0,1,2,0x8b713e0e,0xdeadbeef]:
  case([call(0x45fe60,EVENTS,group)]*2,[patch(EVENTS+4,'<I',count)])
for entries in layouts[:7]:
 for count in [0,1,3,8,16,0xffffffff]:
  patches=subscriptions(entries)+[patch(EVENTS+4,'<I',count)]
  case([call(0x45fa60,EVENTS,SCRIPT)]*2,patches,label='event table unsubscribe')
  for flags in [0,0x10,0x90,255]:
   for events in [0,EVENTS]:
    case([call(0x473010,SCRIPT)]*2,patches+[patch(SCRIPT+0xcc,'<B',flags),patch(SCRIPT+0xe0,'<I',events)],label='script cleanup')
# Relocate only known vtable fields and the corresponding release snapshots.
fields=[SENTINELS+i*0x100 for i in range(16)]+[NODES+i*0x100+j*20 for i in range(16) for j in range(8)]
fields += [LOG+i*48+offset for i in range((HEAP-LOG)//48) for offset in [16,20,24,28]]
scope='Eleven original routines: stateful lookup iteration, two-pool listener release, concrete deleting destructors, first-match listener removal, single/all-event unsubscription, event-group parameter disposal and script-event cleanup. Original virtual listener destructors execute, with their tables relocated in WebAssembly; no handler is stubbed. Generic heap release is instrumented and script-value pools are disabled. Synthetic valid circular lists cover collisions, duplicate listeners, empty sentinels, iteration before deletion, signed counts, wildcard groups, deep parameter disposal and idempotent cleanup. Every fixture/global byte and heap event is compared. Event registration, script setup and the command executor remain separate work.'
fixture={'base':BASE,'memory':'script-events-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'case_labels':labels,'pointer_fields':fields,
 'pointer_exports':[[0x6478d8,'thug_script_listener_methods'],[0x6478dc,'thug_script_listener_list_methods']]}
path=out/'script-events-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_events_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-events-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
