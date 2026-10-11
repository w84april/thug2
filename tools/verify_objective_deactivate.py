"""Original goal deactivation, recursive uninitialization and reset chains."""
import hashlib,json,struct,subprocess,sys
from collections import Counter
from unicorn import UC_HOOK_CODE
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'objective-deactivate.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'objective-initialize-fixtures.json').read_text());BASE=prior['base']
memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
CONTEXT,ADAPTER,ALLOCATOR=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,PRINT,LOG,HEAP=BASE+0x10000,BASE+0x35f00,BASE+0x60000,BASE+0x80000
OBJECT,GAME,MANAGER,QUEUE,LINKS,PARENTS,CHILDREN,GRAPH=[BASE+x for x in [0x180000,0x181000,0x182000,0x180800,0x180900,0x180a00,0x180b00,0x190000]]
objects=[OBJECT+i*256 for i in range(8)]
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def raw(at,data):return [at,bytes(data).hex()]
put(MANAGER,'<5I',8,LINKS,0,0,0)
for i,o in enumerate(objects):
 put(o,'<5I',0x64ddd0 if i&1 else 0x64ea30,o,0,o,o)
 put(o+0x28,'<2I',0,0);put(o+0x6c,'<2B',0xff,0xf1)
 put(LINKS+i*16,'<3I',0x100+i,o,LINKS+(i+1)*16 if i<7 else 0)
put(QUEUE,'<5I',0x6474cc,0xffffffff,0,QUEUE,QUEUE)
initial=bytes(memory);globals_=prior['globals'][:];defaults=prior['cases'][0]['globals'][:];index={g[1]:i for i,g in enumerate(globals_)}
functions={}
def bind(at,name,argc=0,result='void',this=True,heap=False,diag=False):
 f={'name':name,'this':this,'result':result,'cleanup':4*argc if this else 0,'memory':heap}
 if diag:f.update(stack_args=list(range(argc)),diagnostics=True)
 functions[hex(at)]=f
bind(0x554030,'thug_objective_clear_members',1,this=False)
bind(0x554070,'thug_objective_clear_state',heap=True)
bind(0x553e50,'thug_objective_reset_children')
bind(0x554bd0,'thug_objective_uninitialize',2,heap=True,diag=True)
bind(0x557560,'thug_objective_deactivate',2,'byte',heap=True,diag=True)
for at in ['0x557270','0x471b00']:functions[at]=prior['functions'][at]
bind(0x553f50,'thug_objective_mark_active')
exports=dict(prior['pointer_exports']);exports.update({0x64ddd0:'thug_objective_base_methods',0x64ea30:'thug_objective_event_methods'})
# Confirm every concrete virtual slot against both actual executable tables.
pe=load().get_memory_mapped_image()
virtuals={0xc:0x553f90,0x30:0x553f50,0x34:0x557560,0x38:0x553f60,0x54:0x555590,0x60:0x5519f0,0x64:0x554460}
for table in [0x64ddd0,0x64ea30]:
 for slot,fn in virtuals.items():assert struct.unpack_from('<I',pe,table-0x400000+slot)[0]==fn
observe=list(map(lambda x:int(x,16),functions))+[0x553f90,0x553f60,0x555590,0x557f90,0x476b40,0x4776b0,0x477860,0x475790,0x474540,0x4750b0,0x474420,0x5566d0,0x556a00]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,ALLOCATOR,globals_,defaults,functions,observe=observe,event_limit=(HEAP-LOG)//48,instruction_limit=10000000,
 scope_entries={BASE+0x6000:1,ALLOCATOR+0x300:2,ALLOCATOR+0x400:4,ALLOCATOR+0x500:5})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
oracle.setword(0x68ecfc,BASE+0x9600)
labels=[];fields=set(prior['pointer_fields']);outcomes=Counter()
branches={0x5576c0:'inactive_return',0x557582:'special_remove_bindings',0x5575a7:'clear_state',0x5575cd:'deactivate_script',0x5575f5:'remove_testing_flag',0x557628:'early_end_script',0x557653:'uninitialize_before_root',0x557698:'root_initialize',0x5576a1:'queue_unlink',0x554bde:'uninitialize_active',0x554c01:'uninitialize_script',0x554c46:'recursive_child',0x553e7a:'reset_child',0x5540aa:'clear_group'}
def branch(cpu,address,size,user):outcomes[branches[address]]+=1
for at in branches:oracle.cpu.hook_add(UC_HOOK_CODE,branch,begin=at,end=at)
class Build:
 def __init__(self):self.data=bytearray();self.buckets={};self.extra=[]
 def alloc(self,data):
  at=GRAPH+len(self.data);self.data.extend(data);self.data.extend(bytes((-len(self.data))%4));assert GRAPH+len(self.data)<BASE+SIZE;return at
 def text(self,s):return self.alloc(s+b'\0')
 def structure(self,entries):
  nodes=[self.alloc(struct.pack('<BBHIII',kind*2+(i&1),0x5a,0,name,value&0xffffffff,0)) for i,(name,kind,value) in enumerate(entries)]
  for a,b in zip(nodes,nodes[1:]):struct.pack_into('<I',self.data,a-GRAPH+12,b)
  return self.alloc(struct.pack('<II',0xabcdef01,nodes[0] if nodes else 0))
 def array(self,kind,items):
  value=items[0] if len(items)==1 else self.alloc(struct.pack('<'+'I'*len(items),*items)) if items else 0
  return self.alloc(struct.pack('<BBHII',0x91,kind,0x2345,len(items),value))
 def header(self,at,source):self.extra.append(raw(at,self.data[source-GRAPH:source-GRAPH+8]))
 def symbol(self,name,kind,value):
  bucket=BUCKETS+(name&4095)*4;old=self.buckets.get(bucket,struct.unpack_from('<I',initial,bucket-BASE)[0])
  self.buckets[bucket]=self.alloc(struct.pack('<BBHIIII',0,kind,0,name,0,value,old))
 def patches(self):return [raw(GRAPH,self.data)]+[patch(at,'<I',v) for at,v in self.buckets.items()]+self.extra
 def goal(self,i,params=(),state=None,flags=0xff,active=0xf1):
  p=self.structure(params);s=self.structure([(0x700+i,1,7)]) if state is None else state
  self.extra += [patch(objects[i]+0x1c,'<2I',p,s),patch(objects[i]+0x6c,'<2B',flags,active)]
  return p,s
 def children(self,i,ids):
  links=[self.alloc(struct.pack('<2IB3x',id_,0,0xff)) for id_ in ids]
  for a,b in zip(links,links[1:]):struct.pack_into('<I',self.data,a-GRAPH+4,b)
  self.extra.append(patch(objects[i]+0x28,'<I',links[0] if links else 0))
 def parent(self,i,parent):
  self.extra += [patch(objects[i]+0x2c,'<I',PARENTS+i*4),patch(PARENTS+i*4,'<I',parent)]
 def queue(self,indices):
  nodes=[objects[i] for i in indices]
  for j,node in enumerate(nodes):self.extra.append(patch(node+12,'<2I',nodes[j-1] if j else QUEUE,nodes[j+1] if j+1<len(nodes) else QUEUE))
  self.extra.append(patch(QUEUE+12,'<2I',nodes[-1] if nodes else QUEUE,nodes[0] if nodes else QUEUE))

def call(fn,this=OBJECT,args=()):return fn,this,[x&0xffffffff for x in args]+([PRINT] if functions[hex(fn)].get('diagnostics') else [])
def case(b,calls,p=(),label='objective deactivation',changes=None):
 stages=oracle.case(calls,b.patches()+list(p),changes);labels.append(label)
 for s in stages:
  merged=[]
  for at,data in s['outputs']:
   if int.from_bytes(bytes.fromhex(data),'little') in exports:fields.add(at)
   if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
   else:merged.append([at,data])
  s['outputs']=merged
 if len(labels)%100==0:print('Original deactivation cases:',len(labels),flush=True)
 return stages
# Raw clear writes every member's value irrespective of type, and never frees.
for count in [0,1,3,8]:
 for kind in [0,1,2,3,4,10,12,13]:
  b=Build();s=b.structure([(0x1234+i,kind,0xdead0000+i) for i in range(count)])
  case(b,[call(0x554030,args=[s])]*2,label='raw member zeroing preserves type names links and storage')
# Full reset: grouped paths preserve unrelated outer members, skip nonstructures,
# capture next before clearing each group and finally reset parameter/count state.
for grouped in [False,True]:
 for count in [0,1,3]:
  for existing in [False,True]:
   b=Build();entries=[]
   if grouped:
    entries=[(0,13,0xe462e527),(0x8000,1,123)]
    for i in range(count):entries.append((0x9000+i,10,b.structure([(0x700+j,1,11+j) for j in range(i+1)])))
   else:entries=[(0x700+i,1,7+i) for i in range(count)]
   state=b.structure(entries);b.goal(0,[(0xcf6cd3c1,1,123)] if existing else [],state)
   case(b,[call(0x554070)]*2,label='flat or grouped state clearing and parameter replacement')
# Descendant reset tolerates missing IDs and stops at a zero ID even with a next.
for depth in [0,1,3,6]:
 for missing in [False,True]:
  for stop in [False,True]:
   b=Build()
   for i in range(8):b.goal(i)
   for i in range(depth):b.children(i,[0 if stop and i==depth-1 else 0x101+i,0xdeadbeef if missing else 0])
   case(b,[call(0x553e50)]*2,label='descendant reset depth missing lookup and zero-key termination')
# All four behavioral flags together, both original concrete vtables, active/noop,
# real owned binding deletion, testing flag deletion and actual QB script calls.
for bits in range(16):
 for active in [0,1,0xf0,0xff]:
  b=Build();params=[(0x79704516,12,b.array(3,[b.text(b'owned binding')])),(0,13,0x54d3cac1),(0x01c92cac,13,7),(0xd4e0306a,13,6)]
  for j,name in enumerate([0xb394c01c,0xa36700ef,0x38221df4,0xc309cad1]):
   if bits&(1<<j):params.append((0,13,name))
  b.symbol(0x719ae783,13,6);b.goal(0,params,active=active);b.queue([0])
  case(b,[call(0x557560,args=[0xdeadbeef,1])]*2,p=[patch(OBJECT,'<I',0x64ddd0 if bits&1 else 0x64ea30)],label='deactivation flags, original virtual methods, owned deletion and repeated no-op')
# Reset-root behavior follows all parent IDs; root beaten mode gates actual init.
for depth in [0,1,3]:
 for argument in [0,1,256,257,0xffffffff]:
  for beaten in [False,True]:
   b=Build();b.symbol(0x719ae783,13,7)
   for i in range(8):
    fields_=[(0x01c92cac,13,6),(0xd4e0306a,13,7),(0x398b1b8b,13,6)]
    b.goal(i,fields_,flags=4 if beaten else 0x41)
   for i in range(depth):b.parent(i,0x101+i)
   b.parent(depth,0);b.queue([0,1,2,3])
   case(b,[call(0x557560,args=[argument^0x5a,argument]),call(0x554bd0,args=[0,0])],label='low-byte root reinitialization, parent traversal and concrete beaten gate')
# Recursive uninitialization exercises the mutual recursion through deactivation;
# children share a real intrusive queue, and depth increment wraps as a word.
for pattern in [0,0x55,0xaa,0xff]:
 for recursive in [0,1,256,257,0xffffffff]:
  for depth in [0,0xffffffff]:
   b=Build();b.symbol(0x719ae783,13,5)
   for i in range(8):b.goal(i,[(0x01c92cac,13,6),(0xd4e0306a,13,7)],active=1 if pattern&(1<<i) else 0)
   b.children(0,[0x101,0x102]);b.children(1,[0x103,0x104]);b.children(2,[0x105,0x106,0,0x107])
   for i in range(1,7):b.parent(i,0x100+(i-1)//2)
   b.queue(list(range(8)))
   case(b,[call(0x554bd0,args=[recursive,depth])]*2,label='recursive uninitialize and active deactivation with ancestor reinitialization')
# Original init/deactivate/uninitialize script fields can resolve aliases or be
# absent. These are real scheduler decisions, not callback substitution.
for script in [None,0,5,6,7,0x12340007,0xeeeeeeee]:
 b=Build();params=[] if script is None else [(n,13,script) for n in [0x01c92cac,0xd4e0306a]]
 b.goal(0,params);b.queue([0]);case(b,[call(0x554bd0,args=[1,0])],label='optional script resolution and full active uninitialization')
# Replay each exact archived training flag-array fixture through a complete
# initialize -> deactivate -> initialize -> active uninitialize lifecycle.
for old,label in zip(prior['cases'],prior['case_labels']):
 if not label.startswith('archived '):continue
 b=Build();b.queue([0]);p=old['patches']+b.extra
 calls=[(s['fn'],s['this'],s['args']) for s in old['steps'][:2]]
 calls=[(int(fn,16),this,args) for fn,this,args in calls]
 calls += [call(0x553f50),call(0x557560,args=[0,1]),call(0x557270),call(0x553f50),call(0x554bd0,args=[1,0])]
 case(b,calls,p=p,label=label+' lifecycle',changes={i:v for i,v in enumerate(old['globals'])})
fields.update(at for at in range(BASE,BASE+SIZE,4) if int.from_bytes(initial[at-BASE:at-BASE+4],'little') in exports)
scope='Five original routines: complete deactivation557560, recursive uninitialize554bd0, descendant reset553e50, flat-member clear554030 and full state clear554070. Actual recovered base/event virtual methods, cache lookup, synchronous QB execution, root initialization and owned parameter disposal execute. Full arena/global bytes, returns and heap/scope order compare, with no native gameplay callback substitutions or arithmetic/padding exceptions. Includes repeated calls, all behavioral flag combinations, byte-only arguments, child/parent trees, missing-child reset, queue unlinking, concrete beaten gates and full lifecycle runs using all30 original archived training flag arrays. Original reserved num_flags member loops remain nonterminating and are checked separately in bounded processes, never on the browser main thread. Valid acyclic graphs, resolved required children/parents, successful allocation and terminating scripts retain original contracts. Activation/score/UI/movement/rendering integration remains incomplete.'
fixture={'base':BASE,'memory':'objective-deactivate-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':list(exports.items()),'pointer_fields':sorted(fields),'pointer_globals':prior['pointer_globals']}
path=out/'objective-deactivate-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
print('x86 complete:',len(labels),dict(oracle.counts),dict(outcomes),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_objective_deactivate_wasm.mjs'),str(out)],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/verify_objective_reset_loop.py')],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'outcomes':dict(outcomes),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'virtual_tables':{'0x64ddd0':virtuals,'0x64ea30':virtuals},'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/fixture['memory'],out/prior['memory'],out/'objective-initialize-fixtures.json']},'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
