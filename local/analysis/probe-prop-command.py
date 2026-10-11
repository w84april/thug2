"""Original object command dispatch and complete parameter/event setup."""
from pathlib import Path
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved prop setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
specs=[(0x45d7f0,23,'composite_text_command',2,'byte'),(0x45d810,17,'composite_create_component_command',2,'byte'),
 (0x45d830,25,'composite_set_position_command',2,'byte'),(0x45dbc0,34,'composite_get_position_command',2,'byte'),
 (0x45dbf0,75,'composite_contains_command',2,'byte'),(0x45d850,49,'composite_descriptor',3,'byte'),
 (0x45e450,97,'composite_checksum',3,'byte'),(0x4608f0,43,'object_checksum',3,'byte'),
 (0x476420,11,'script_structure_empty',0,'byte'),(0x478ab0,66,'script_structure_copy_construct',1,'word'),
 (0x45f820,20,'script_events_initialize',0,'word'),(0x45fa10,72,'script_events_subscribe',1,'void'),
 (0x45ff50,395,'script_events_compact',0,'void'),(0x4601a0,707,'script_events_add',2,'void'),
 (0x4734e0,225,'script_set_events',2,'void'),(0x461290,191,'object_ensure_script',0,'void'),
 (0x460c20,117,'object_remove_parameters',1,'void'),(0x461710,162,'object_apply_parameters',1,'void')]
specs += [(0x476c60,20,'script_get_text_legacy',3,'byte'),(0x44bd30,45,'script_got_parameter',2,'word'),(0x44a260,82,'script_checksums_equal',2,'word'),(0x44a2c0,83,'script_strings_equal',2,'word')]
for a,n,name,argc,result in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,this=a not in [0x44bd30,0x44a260,0x44a2c0])
for a,n,argc,result,heap,diag in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),(0x461a00,'thug_object_manager_add',1,'void',True,False),
 (0x461ab0,'thug_dead_objects_flush_draft',0,'void',True,True),(0x4738e0,'thug_script_initialize',0,'word',False,False),
 (0x474420,'thug_script_destroy',0,'void',True,True),(0x473010,'thug_script_clear_events',0,'void',True,False),
 (0x472980,'thug_script_dispatch_descriptor',4,'byte',False,False)]:bind(a,n,argc,result,heap,diag,this=a!=0x472980)
for name,a in [('thug_script_copy_structure_count_draft',0x6f3610),('thug_script_copy_structure_peak_draft',0x67da30)]:global_default(name,a,0)
for a,n,*_ in specs:
 if a in [0x45d810,0x45dbf0,0x45d830,0x45dbc0,0x45d7f0]:function_exports.append([a,'thug_'+next(row[2] for row in specs if row[0]==a)+'_draft'])
# Constructor identity in dynamically allocated scripts, observed before heap snapshots.
def script_identity(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,script_identity,begin=0x4738e0,end=0x4738e0)
class CommandGraph(PropGraph):
 def __init__(self):
  super().__init__();self.put(OBJ,'<I',0x647650);self.image[SCRIPTS-BASE:SCRIPTS-BASE+0x400]=bytes(0x400)
 def descriptor(self,name,member,adjust=0,kind=0x0ada4e74):
  d=self.alloc(24);self.put(d,'<6I',name,kind,member,adjust&0xffffffff,0,0);fields.add(d+8);return d
 def event_table(self,rows):
  t=self.alloc(16);entries=self.alloc(max(20*len(rows),4));self.put(t,'<2I4BI',entries,len(rows),1,0,0xaa,0xbb,0)
  for i,(event,script,owned) in enumerate(rows):
   s=self.structure([(0x100,1,10+i),(0,13,0x88)]) if owned else 0
   self.put(entries+i*20,'<5I',event,script,0x100+i,s,0xaabbcc02|i)
  return t
 def event_array(self,rows):
  values=[]
  for event,script,options in rows:
   items=[(0,13,event),(0,13,script)]
   if options&1:items.append((0x7031f10c,10,self.structure([(0x1234,1,17),(0x1254,3,self.text('event payload'))])))
   if options&2:items.append((0x923fbb3a,13,0x12345678))
   if options&4:items.append((0,13,0x80367192))
   values.append(self.structure(items))
  return self.array(10,values)
 def cache_default(self):
  key=0x3f5cdb8a;body=self.alloc(8);self.put(body,'<2B',1,0x24)
  entry=self.alloc(20);self.put(entry,'<5I',key,body,1,0,0)
  table=self.table([(key,entry)]);self.put(CACHE+20,'<4I',table,0,0,0)
  blob=self.alloc(20);self.put(blob,'<3I2B',0,2,2,1,0x24);self.symbol(key,7,blob)
 def pool(self,size):
  t=self.alloc(96);blocks=self.alloc(size*8);self.put(t,'<6I',blocks,blocks+size*8,0,0,0,blocks);self.put(t+88,'<I',0)
  for i in range(8):self.put(blocks+i*size,'<I',blocks+(i+1)*size if i<7 else 0)
  return t

def run(g,calls,label,changes=None):
 try:s=case(calls,g.patches(),changes,label)
 except Exception:print('Failed command case:',label,flush=True);raise
 if len(labels)%25==0:print('Original command cases',len(labels),flush=True)
 return s
init=lambda:call(0x45e510,OBJ)
for fill in [0,0xa5,0xff]:
 g=CommandGraph();t=g.alloc(16);g.image[t-BASE:t-BASE+16]=bytes([fill])*16
 run(g,[call(0x45f820,t)]*2,'event ctor padding '+str(fill))
for selfcopy in [False,True]:
 for count,peak in [(0,0),(10,20),(0x7fffffff,0x7fffffff),(0xffffffff,0xffffffff),(0x80000000,0)]:
  g=CommandGraph();s=g.structure([(0x1234,3,g.text('copy')),(0x1235,12,g.array(1,[5,6]))]);to=s if selfcopy else g.alloc(8)
  run(g,[call(0x478ab0,to,[s]),call(0x476420,to)],f'copy ctor self{selfcopy}/stats{count:x}/{peak:x}',{0x6f3610:count,0x67da30:peak})
for count,key,mode in itertools.product([0,1,4],[0,2,99],['named','included','missing']):
 g=CommandGraph();comps=[g.component(i) for i in range(count)]
 for a,b in zip(comps,comps[1:]):g.put(a+16,'<I',b)
 g.put(OBJ+0x100,'<I',comps[0] if comps else 0)
 s=g.structure([] if mode=='missing' else [(0xa1dc81f9,13,key)])
 if mode=='included':g.symbol(0x10000111,10,s);s=g.structure([(0,13,0x10000111)])
 d=g.descriptor(0x2bffeaa3,0x45dbf0)
 run(g,[call(0x45dbf0,OBJ,[s,0]),call(0x45d850,OBJ,[d,s,0]),call(0x472980,args=[d,s,OBJ,0])],f'contains {count}/{key}/{mode}')
for adjust in [-64,0,64]:
 for present in [False,True]:
  g=CommandGraph();p=OBJ+adjust;s=g.structure([(0xb9d31b0a,6,g.vector([0x7f812345,0x80000000,bits(17)]))] if present else [])
  d=g.descriptor(0xf7251a64,0x45d830,adjust);g.put(SCRIPTS+20,'<I',g.structure([]))
  run(g,[call(0x45d850,OBJ,[d,s,SCRIPTS]),call(0x45dbc0,p,[s,SCRIPTS])],f'direct adjusted position {adjust}/{present}')
for mode in ['empty','text','included','wrong']:
 g=CommandGraph();s=g.structure([] if mode=='empty' else [(0,1 if mode=='wrong' else 3,g.text('optional text'))])
 if mode=='included':g.symbol(0x10000111,10,s);s=g.structure([(0,13,0x10000111)])
 run(g,[call(0x45d7f0,OBJ,[s,0])],f'actual text command {mode}')
for name,kind,size,vt,ctor,factory,destroy,delete in classes[:4]:
 g=CommandGraph();g.registry([(kind,factory)]);s=g.structure([(0xb6015ea8,13,kind),(0xa1dc81f9,13,0x12345678)])
 d=g.descriptor(0x406998a5,0x45d810)
 run(g,[init(),call(0x45d850,OBJ,[d,s,SCRIPTS]),call(0x45d810,OBJ,[s,SCRIPTS]),call(0x45d890,OBJ)],'real member factory '+name)
# Real unhandled components fall through to the base command, then actual
# parameter apply or deferred deletion. No successful checksum stub is supplied.
for components in [0,1,3]:
 for command in [0,0x12345678,0x6c63c7c5,0xc6870028]:
  g=CommandGraph();s=g.structure([]);comps=[g.component() for _ in range(components)]
  d=g.descriptor(command,0);calls=[init(),call(0x461a00,MANAGER,[OBJ])]
  # Add existing base components after init via known original append.
  bind(0x45da30,'thug_composite_add_component_draft',1)
  calls += [call(0x45da30,OBJ,[c]) for c in comps]+[call(0x45d850,OBJ,[d,s,SCRIPTS])]
  if command==0xc6870028:calls.append(call(0x461ab0,MANAGER))
  else:calls.append(call(0x45d890,OBJ))
  run(g,calls,f'checksum actual fallthrough {components}/{command:x}')
for old in [[],[(1,2,False)],[(1,0xc377c572,False)],[(1,0xc377c572,True),(2,3,True),(4,0xc377c572,True)],[(1,0xc377c572,True),(2,0xc377c572,False)]]:
 g=CommandGraph();t=g.event_table(old)
 run(g,[call(0x45ff50,t)]*2,'compact '+str(old))
# Null entries and signed nonpositive counts preserve all other table state.
for ptr_,count in [(0,0),(0,4),(1,0),(1,0xffffffff)]:
 g=CommandGraph();t=g.event_table([]);g.put(t,'<2I',g.word(t) if ptr_ else 0,count)
 run(g,[call(0x45ff50,t)],f'compact empty {ptr_}/{count}')
for replace,incoming,old in itertools.product([0,1,256,257,0xffffffff],[[],[(1,2,0)],[(1,2,7),(2,3,1),(1,4,2)]],[[],[(1,5,True),(2,6,False),(3,0xc377c572,True)]]):
 g=CommandGraph();t=g.event_table(old);a=g.event_array(incoming)
 run(g,[call(0x4601a0,t,[a,replace]),call(0x45ff50,t)],f'event add replace{replace}/new{incoming}/old{len(old)}')
for pooled in [False,True]:
 g=CommandGraph();t=g.event_table([]);a=g.event_array([(1,2,7),(3,4,1)])
 changes={0x6f361c:g.pool(16)} if pooled else None
 run(g,[call(0x4601a0,t,[a,1])],f'event parameter pool {pooled}',changes)
for old in [[],[(0,2,False),(1,0,False),(2,0xc377c572,False),(3,4,False),(3,5,False)]]:
 g=CommandGraph();t=g.event_table(old)
 run(g,[call(0x45fa10,t,[SCRIPTS])]*2,'subscribe criteria '+str(old))
for replace in [0,1,256,0xffffffff]:
 for existing in [False,True]:
  g=CommandGraph();a=g.event_array([(1,2,7),(1,3,0),(2,4,0)]);empty=g.event_array([])
  calls=[call(0x4738e0,SCRIPTS)]
  if existing:calls.append(call(0x4734e0,SCRIPTS,[a,0]))
  calls += [call(0x4734e0,SCRIPTS,[a,replace]),call(0x4734e0,SCRIPTS,[empty,replace]),call(0x474420,SCRIPTS)]
  run(g,calls,f'set events {replace}/existing{existing}')
for pooled in [False,True]:
 g=CommandGraph();g.cache_default();changes={0x6f3550:g.pool(256)} if pooled else None
 run(g,[init(),call(0x461290,OBJ),call(0x461290,OBJ),call(0x45d890,OBJ)],f'lazy owned script {pooled}',changes)
for has,keys in itertools.product([False,True],[None,[],[0x111],[0x111,0x222,0x111],[0x333]]):
 g=CommandGraph();s=g.structure([(0x111,1,7),(0,13,0x111),(0x222,3,g.text('remove'))]);g.put(OBJ+0x20,'<I',s if has else 0)
 a=0 if keys is None else g.array(13,keys)
 run(g,[call(0x460c20,OBJ,[a])]*2,f'remove parameters {has}/{keys}')
for mask in range(16):
 g=CommandGraph();g.cache_default();a=g.event_array([(1,2,7),(2,3,0)]);params=g.structure([(0x111,1,9),(0,13,0x222)]);remove=g.array(13,[0x111,0x222]);items=[]
 if mask&1:items.append((0x475bf03c,12,a))
 if mask&2:items.append((0x90436bd9,10,params))
 if mask&4:items.append((0x8225d629,12,remove))
 if mask&8:items.append((0,13,0x3f93a1ef))
 s=g.structure(items)
 run(g,[init(),call(0x461710,OBJ,[s]),call(0x461710,OBJ,[s]),call(0x45d890,OBJ)],'full object parameters mask '+str(mask))
exec(compile(Path('local/analysis/prop-command-dispatch-probes.py').read_text(),'<explicit dispatch witnesses>','exec'))
exec(compile(Path('local/analysis/prop-predicate-probes.py').read_text(),'<real native predicates>','exec'))
# Exclusions are inspected below after the initial corpus; no uncovered byte
# is silently counted as recovered execution.
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()}
print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'initialized allocator bypasses process bootstrap' for a in [0x46000d,0x460272,0x46031f,0x47351e,0x4612e6]}
excluded['0x4601ea']='unreachable alignment after an unconditional jump'
excluded.update({hex(a):'failed allocation cannot satisfy the subsequent live script/event-table contract' for a in [0x47355b,0x47355d,0x473565,0x47356b,0x461318]})
scope='Twenty-two original routines recover composite command/descriptor dispatch, direct component creation/contains and position commands, complete object parameter application and its lazy owned script, event-table construction/addition/replacement/compaction/subscription, parameter removal/copy dependencies and GotParam/ChecksumEquals/StringEquals predicates. StringEquals uses normalized checksums; missing required strings are outside its original initialized-data contract. Real original factories, registry, interpreter setup, event listeners and ownership callees execute; the fixture supplies initialized services. Full scripted prop assembly/model rendering remains.'
finish('prop-command',scope,excluded,extra)
