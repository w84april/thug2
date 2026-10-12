"""Original component-loop calls through the real Walk vtable and lifecycle."""
from pathlib import Path
exec(compile(Path('local/analysis/probe-walk-complete-update.py').read_text().split('\nrecords=[]')[0],'<preserved complete walking graph>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();frame_hits.clear()
new_roots=[(0x45d920,'thug_object_update_components',0,'void',True,True),
 (0x52a190,'thug_walk_construct_draft',0,'word',False,False),
 (0x45da30,'thug_composite_add_component_draft',1,'void',False,False),
 (0x526060,'thug_walk_initialize_draft',1,'void',False,False),
 (0x525fb0,'thug_walk_bind_draft',0,'void',False,False)]
for row in [*new_roots,*extra_roots]:bind(*row)
new_entries={row[0] for row in new_roots};new_returns=set()
for at in new_entries|{0x45f3e0}:
 for ins in Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,0x1000),at):
  if ins.mnemonic=='int3':break
  if ins.mnemonic=='ret':new_returns.add(ins.address)
for at in new_entries:
 oracle.cpu.hook_add(UC_HOOK_CODE,observe_cache,begin=at,end=at)
 oracle.cpu.hook_add(UC_HOOK_CODE,payload_entry,begin=at,end=at)
loop_hits=Counter();virtual_calls=[]
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:loop_hits.update([at]),begin=0x45d920,end=0x45d989)
def object_observe(cpu,at,size,user):
 global source_probe,copy_destination
 sp=cpu.reg_read(UC_X86_REG_ESP);ret=oracle.word(sp)
 if at in new_entries and ret==oracle.stop:
  source_probe=copy_destination=0;root_records.append({'stack_pointer_fields':[]})
 elif at in new_returns and ret==oracle.stop:
  root_records[-1]['indeterminate_words']=sorted(undefined_words)
  root_records[-1]['indeterminate_provenance']=[undefined_provenance[a].copy() for a in sorted(undefined_words)]
 elif at==0x52d4b0:
  assert ret==0x45d96c;virtual_calls.append({'component':cpu.reg_read(UC_X86_REG_ECX),'vtable':oracle.word(P),'caller_return':ret})
 elif at==0x52d67e and ret==0x45d96c:
  frame_states.append({'state':oracle.word(P+0x18),'event':oracle.word(P+0x78),'position':bytes(cpu.mem_read(P+0x24,16)).hex(),'owner_position':bytes(cpu.mem_read(OBJ+0x4c,16)).hex(),'vertical_velocity':oracle.word(P+0x44)})
for at in new_entries|new_returns|{0x52d4b0,0x52d67e}:oracle.cpu.hook_add(UC_HOOK_CODE,object_observe,begin=at,end=at)
# Prove restoration of a caller's component-service scope after every root.
SERVICE_GLOBAL=0x39c
assert SERVICE_GLOBAL not in index and not any(x[0]=='thug_component_services' for x in globals_)
glob('thug_component_services',SERVICE_GLOBAL,0)
links=[(INPUT,0x27d7cd28),(AP,0x7149b753),(MODEL,0x286a8d26),(TRIGGER,0xe594f0a2),(CONTROL,0xd9151d4d),(GATE,0x408d2aa9),(STATE,0x43686585),(PHYSICS,0x5bd63b29),(HANG,0x380d909a)]
def connect(g,order='first',flags=0,walk_flags=0,include_walk=True):
 chain=[];node=g.word(OBJ+0x100)
 while node:
  assert node not in chain;chain.append(node);node=g.word(node+16)
 chain=list(dict.fromkeys([a for a,_ in links]+chain+[SCORECOMP]));chain=[a for a in chain if a!=P]
 for at,type_ in links:g.put(at+4,'<I',type_);g.put(at+12,'<I',OBJ)
 for at in chain:g.put(at+8,'<I',g.word(at+8)|1)
 if include_walk:chain.insert(0 if order=='first' else len(chain)//2 if order=='middle' else len(chain),P)
 for i,at in enumerate(chain):g.put(at+16,'<I',chain[i+1] if i+1<len(chain) else 0)
 g.put(P+8,'<I',walk_flags);g.put(OBJ+0x100,'<2I',chain[0] if chain else 0,flags);g.put(OBJ+0x10,'<I',0)
 saved=g.alloc(12);g.put(saved,'<3I',Q,DIAG,ADAPTER);fields.add(saved)
 return saved
records=[]
def run(g,calls,label,scope_pointer):
 frame_states.clear();virtual_calls.clear();completion_states.clear();commands.clear();speed_calls.clear()
 stages=g.run([call(0x417760,P+0x17b4),*calls],label,{0x7cce14:NET,0x7d1ec8:0,0x696d60:1000,0x684fc8:bits(6),SERVICE_GLOBAL:scope_pointer})
 assert len(frame_states)==len(virtual_calls)
 assert all(x['component']==P and x['vtable']==0x64c75c for x in virtual_calls)
 records.append({'label':label,'calls':len(stages),'frames':list(frame_states),'virtual_calls':list(virtual_calls),'completion_states':list(completion_states),'callbacks':oracle.word(CBSTATE),'state':oracle.word(P+0x18),'owner_flags':oracle.word(OBJ+0x104),'commands':list(commands),'speed_calls':list(speed_calls)})
 return stages
for state,order,flags,network in itertools.product([0,1,2,3,4,5,0xffffffff],['first','middle','last'],[0,2],[False,True]):
 g=HangUpdateGraph(network=network) if state==2 else RailUpdateGraph(network=network) if state==3 else AirUpdateGraph(height=20 if state==1 else 0,vertical=-40 if state==1 else 0,speed=3)
 g.put(P+0x18,'<I',state);g.put(NET,'<I',4 if network else 0);g.plane(0,half=1024,flags=0x20)
 saved=connect(g,order,flags);run(g,[call(0x45d920,OBJ,[Q])]*4,f'component frame {state}/{order}/{flags}/{network}',saved)
 assert len(frame_states)==4
for flags,walk_flags in itertools.product([0,1,2,3,8,9,10,0xffffffff],[0,1,2,3,0xfffffffe,0xffffffff]):
 g=HangUpdateGraph();saved=connect(g,flags=flags,walk_flags=walk_flags);run(g,[call(0x45d920,OBJ,[Q])]*2,f'suspension gates {flags}/{walk_flags}',saved)
 assert len(frame_states)==(0 if flags&1 or walk_flags&1 else 2)
for mutation in ['observe','owner dead','remove list','suspend walk','change state','change next','cancel walk']:
 g=HangUpdateGraph();saved=connect(g)
 writes={'observe':[],'owner dead':[(OBJ+8,1)],'remove list':[(OBJ+0x100,0)],'suspend walk':[(P+8,1)],'change state':[(P+0x18,4)],'change next':[(P+16,0)],'cancel walk':[(CONTROL+0x24,0x10000)]}[mutation]
 g.callback(writes);g.put(OBJ+0x10,'<I',SCRIPT)
 run(g,[call(0x4738e0,SCRIPT),call(0x474540,SCRIPT,[6,0,0,OBJ]),call(0x45d920,OBJ,[Q])]*1,f'pre-frame QB {mutation}',saved)
 assert oracle.word(CBSTATE)==1
 assert len(frame_states)==(0 if mutation in ['owner dead','remove list','suspend walk'] else 1)
# The owner executes the real animation-finish command before the next Walk
# frame, so completion and resumed movement share the original outer loop.
for up,present,moving,network in itertools.product([False,True],[False,True],[False,True],[False,True]):
 g=HangUpdateGraph(0 if up else 3.14159274,network=network);actors=[]
 if present:actors.append(g.plane(0 if up else -100,moving=moving,half=1024,flags=0x40)[0])
 g.scripts(actors);g.finish_script();g.put(CHANNELS+0x18,'<f',6);saved=connect(g);g.put(OBJ+0x10,'<I',SCRIPT)
 calls=[call(0x4738e0,SCRIPT),*[call(0x45d920,OBJ,[Q])]*2]
 if up:calls +=[call(0x474540,SCRIPT,[0x77123456,0,0,OBJ])]
 calls +=[call(0x45d920,OBJ,[Q])]*4
 run(g,calls,f'owner loop exit continuation {up}/{present}/{moving}/{network}',saved)
 assert len(frame_states)==6
 if up:assert len(completion_states)==1 and any(x['state']==4 for x in frame_states)
for state,moving,mutation in itertools.product([0,1],[False,True],['owner dead','sever next']):
 g=AirUpdateGraph(height=10 if state else 0,vertical=-100 if state else 0);g.put(P+0x18,'<I',state)
 actor,owner=g.plane(0,moving=moving,half=1024,flags=0x40);g.trigger('observe',g.word(actor+4));saved=connect(g)
 if moving:g.level_nodes([(0x111,[(0x2ca8a299,13,6)]),(g.word(actor+4),[(0x2ca8a299,13,6)]),(g.word(owner+0x14),[])])
 g.put(CBSTATE+8,'<I',1);g.put(CBSTATE+16,'<2I',OBJ+8 if mutation=='owner dead' else P+16,1 if mutation=='owner dead' else 0)
 run(g,[call(0x45d920,OBJ,[Q])]*2,f'nested collision QB {state}/{moving}/{mutation}',saved)
 assert oracle.word(CBSTATE)>0 and len(frame_states)==(1 if mutation=='owner dead' else 2)
# Reconstruct, attach, initialize and bind Walk before updating it. The existing
# fixture state supplies finite movement/animation data that constructor leaves
# untouched; other component frames are explicitly suspended, not substituted.
for state in [0,1,2,3,4]:
 g=HangUpdateGraph() if state==2 else RailUpdateGraph() if state==3 else AirUpdateGraph(height=20 if state==1 else 0,vertical=-40 if state==1 else 0)
 g.put(P+0x18,'<I',state);g.plane(0,half=1024,flags=0x20);saved=connect(g,include_walk=False)
 params=g.structure([(0xc4e311fa,13,0x55112233)]);g.put(EM+8,'<I',g.table([(0x1234,OBJ),(0x55112233,CAMERA)]));g.put(CAMERA+0x100,'<I',CAM);g.put(CAM+4,'<I',0xc7d37ec2);g.put(CAM+16,'<I',0)
 run(g,[call(0x52a190,P),call(0x45da30,OBJ,[P]),call(0x526060,P,[params]),call(0x525fb0,P),*[call(0x45d920,OBJ,[Q])]*4],f'construct bind update state {state}',saved)
 assert len(frame_states)==4 and [oracle.word(P+0x1770+i*4) for i in range(9)]==[a for a,_ in links]
scope='Connect the real Walk component update slot to the complete recovered dispatcher and compare original45d920 component-loop frames across all five movement states, suspension gates, real pre-frame QB mutations and constructor/attachment/initialization/binding. Other component frame methods are explicitly suspended. No new routine count; full skater startup, rendering and playable training remain unfinished.'
extra={**extra,'cache_capture':'destructor-v1','pointer_globals':sorted(set(extra.get('pointer_globals',[])+[index[0x6918ec+i*4] for i in range(8)])),
 'indeterminate_word_addresses':[a+x for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]] for x in [0x70,0xa8]],'stack_probe_pointer_fields':[a+0x64 for a in [P+0x17b4,*[P+0xbc+i*0xcc for i in range(8)]]],
 'indeterminate_byte_addresses':sorted(payload_destinations),'payload_source_stack':[oracle.stack,oracle.stack+0x20000],
 'native_callbacks':[{'module':'walk-critical-diagnostics.wasm','export':'fixture_walk_critical_print','slots':[DIAG+4]},{'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
finish('walk-component-frame',scope,{},extra)
report=json.loads((folder/'walk-component-frame-original.json').read_text());report['records']=records
report['instruction_coverage']={}
for at,n,h in [(0x45d920,106,loop_hits),(0x52d4b0,463,frame_hits)]:
 code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(at-0x400000,n),at));report['instruction_coverage'][hex(at)]={'covered':sum(bool(h[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not h[i.address]],'excluded':{}}
report['completed_component_frames']=sum(len(x['frames']) for x in records)
(folder/'walk-component-frame-original.json').write_text(json.dumps(report,indent=2)+'\n');print(report['instruction_coverage'])
