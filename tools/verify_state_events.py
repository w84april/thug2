"""State setters and object broadcasts through the original event executor."""
import hashlib,json,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
import verify_wall_response as w
from specimen import ROOT,SHA256

out=w.out;report_path=out.parent/'state-events.json';report_path.unlink(missing_ok=True)
patch=w.patch;oracle=w.oracle;cpu=w.cpu;fields=w.fields
SCRIPT,EVENTS,ENTRIES=0x1944000,0x1942000,0x1942400
LTABLE,LBUCKETS,LIST,LISTNODES=0x1940200,0x1940300,0x1941300,0x1941400
PARAMS=w.VECTORS+0x100
for state,body in [(w.STATE,w.BODY),(w.STATE2,w.BODY2)]:
 w.put(state+12,'<I',body);w.put(state+0x18,'<I',0);w.put(state+0xe1,'<B',0)
w.put(PARAMS,'<2I',0,0)
initial=bytes(w.memory);oracle.initial=initial
w.functions.clear()
for at,name,argc in [(0x519660,'thug_skater_state_set_mode',1),(0x5196a0,'thug_skater_state_set_material',1),(0x460a20,'thug_object_broadcast_event',3)]:
 w.functions[hex(at)]={'name':name,'this':True,'result':'void','cleanup':argc*4,'stack_args':list(range(argc)),'memory':True,'diagnostics':True}
 cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
for at in [0x4750b0,0x475750,0x462f00,0x460470,0x473800]:cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
labels=[];outcomes=Counter();known={entry[0] for entry in w.exports}
def call(fn,this,*args):return fn,this,[*args,w.PRINT]
def case(calls,p=(),changes=None,label='state event'):
 if len(labels)%40==0:print('Original state-event cases:',len(labels),label,flush=True)
 labels.append(label);stages=oracle.case(calls,p,{w.index[k]:v for k,v in (changes or {}).items()});callbacks=0
 for step in stages:
  merged=[]
  for at,data in step['outputs']:
   if at==w.CALLBACK:
    count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-callbacks;callbacks=count
   raw=bytes.fromhex(data)
   for i in range(0,len(raw),4):
    if int.from_bytes(raw[i:i+4],'little') in known:fields.add(at+i)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  step['outputs']=merged
  outcomes['event_callbacks']+=step['callbacks'];outcomes['calls_with_callbacks' if step['callbacks'] else 'calls_without_callbacks']+=1
 return stages

# Repeat setters, including all-byte material coercion and poisoned neighbours.
for fn,event,offset,width,values in [
 (0x519660,0xa7662059,0x18,4,[0,1,2,3,4,0x7fffffff,0x80000000,0xffffffff]),
 (0x5196a0,0xd3fde02a,0xe1,1,[0,1,7,127,128,255,256,0xdeadbeef])]:
 for body in [w.BODY,w.BODY2]:
  for value in values:
   for same in [False,True]:
    initial_value=(value&((1<<(width*8))-1)) if same else ((value+1)&((1<<(width*8))-1))
    p=[patch(w.STATE+12,'<I',body),[w.STATE+offset,initial_value.to_bytes(width,'little').hex()]]
    stages=case([call(fn,w.STATE,value)]*2,p,label='changed value followed by idempotent repeat')
    assert bool(stages[0]['callbacks']) != same and stages[1]['callbacks']==0
 # Equal values return before reading the otherwise invalid owner.
 case([call(fn,w.STATE,0)],[patch(w.STATE+12,'<I',0)],label='equal value does not dereference owner')
 # Observe store-before-callback, callback mutation, and subsequent notifications.
 for mode,at,value in [(1,w.STATE+offset,77),(2,w.STATE+offset,0x12345678),(2,w.STATE+12,w.BODY2),(3,0,w.BODY2),(4,0,w.STATE2),(5,0,0xffffffff)]:
  p=[patch(w.CALLBACK+4,'<3I',mode,at,value)]
  case([call(fn,w.STATE,7)]*2,p,label='callback mutation survives setter and affects next delivery')
 # A receiver reroutes to a real cached QB handler, whose native command mutates state.
 p=[patch(w.EM+0x14,'<I',w.RECEIVER),patch(w.CALLBACK+4,'<3I',6,w.STATE+offset,9),patch(ENTRIES,'<I',event)]
 case([call(fn,w.STATE,7)]*2,p,label='receiver redirects to actual QB handler')

def subscribe(event,count):
 nodes=[LISTNODES+i*20 for i in range(count)]
 p=[patch(LTABLE+8,'<I',1),patch(LBUCKETS+(event&3)*12,'<3I',event,LIST,0),
    patch(LIST,'<5I',0x6478dc,0xffffffff,0,nodes[0] if nodes else LIST,nodes[-1] if nodes else LIST)]
 for i,node in enumerate(nodes):
  p.append(patch(node,'<5I',0x6478d8,SCRIPT,0,nodes[i+1] if i+1<count else LIST,nodes[i-1] if i else LIST))
 return p

# Zero, one and repeated subscriptions exercise fast and reference-snapshot paths.
# Parameters are borrowed, and the original third argument is ignored completely.
for event in [0xa7662059,0xd3fde02a,0x12345678,0xffffffff]:
 for count in [-1,0,1,2,3]:
  for params in [0,PARAMS]:
   p=[patch(ENTRIES,'<I',event)]+(subscribe(event,count) if count>=0 else [])
   for body,unused in [(w.BODY,0),(w.BODY2,0xdeadbeef)]:
    case([call(0x460a20,body,event,params,unused)],p,label='broadcast listener fast path or protected snapshot')
for mode,at,value in [(1,w.STATE+0xe1,13),(2,w.BODY+0x14,2),(3,0,w.BODY2),(4,0,w.STATE2)]:
 event=0xa7662059
 p=subscribe(event,2)+[patch(ENTRIES,'<I',event),patch(w.CALLBACK+4,'<3I',mode,at,value)]
 case([call(0x460a20,w.BODY,event,PARAMS,0xffffffff)]*2,p,label='broadcast callbacks mutate source after its identity was captured')
print('Observed callees:',dict(oracle.coverage),'heap:',dict(oracle.heap_events),flush=True)
assert oracle.coverage['0x4750b0'] and oracle.coverage['0x462f00'] and oracle.heap_events
scope='Complete original state-mode setter 00519660, material-byte setter 005196a0 and object broadcast wrapper 00460a20. Actual event routing, object ID lookup, cached QB handler execution, one-listener delivery and reference-protected listener snapshots execute unchanged. Tests cover repeated values, low-byte arguments, null owner on no-op paths, callback mutations, borrowed parameters and the unused third broadcast argument. All arena/global bytes and callback/heap ordering compare exactly. Native gameplay handlers and successful heap allocation are instrumented boundaries; full floor/ground updates and playable integration remain incomplete.'
fixture={'base':w.BASE,'memory':'state-events-memory.bin','memory_adapter':w.ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':w.prior['memory_exports'],
 'globals':w.globals_,'functions':w.functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'callback_counter':'event_and_command_callbacks',
 'pointer_symbols':w.prior['pointer_symbols'],'pointer_exports':w.exports,'pointer_fields':sorted(fields),'pointer_globals':sorted(w.pointer_globals),
 'native_callbacks':w.prior['native_callbacks']+[dict(spec,module='wall-audio-callbacks.wasm') for spec in w.audio['native_callbacks']]}
path=out/'state-events-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_state_events_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/'rebound-callbacks.wasm',out/'wall-audio-callbacks.wasm',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
