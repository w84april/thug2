"""Original Walk lifecycle/common frame and explicitly interrupted state dispatch."""
from pathlib import Path
# Extend only the test heap boundary with an explicit allocation-failure switch.
# The game's allocation wrapper and factory instructions still execute unchanged.
from script_heap_oracle import ScriptHeapOracle
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EAX,UC_X86_REG_EIP
original_heap=ScriptHeapOracle.heap
def walk_heap(self,cpu,address,size,user):
 if address in [0x5bbae0,0x5bafc0] and self.word(self.context+32)==1:
  sp=cpu.reg_read(UC_X86_REG_ESP);route=int(address==0x5bafc0)
  if route:assert self.word(sp+8)==1 and self.word(sp+12)==0
  self.record(1,self.word(sp+4),route,0);self.heap_events[hex(address)]+=1
  cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,self.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+(12 if route else 0));return
 original_heap(self,cpu,address,size,user)
ScriptHeapOracle.heap=walk_heap
source=Path('local/analysis/probe-skater-cleanup.py').read_text().split('# Lifecycle')[0]
source=source.replace("source=source.replace('0xe594f0a2','0x726e85aa')","source=source.replace('0xe594f0a2','0x7cd3e6d5')")
exec(compile(source,'<preserved startup oracle; next component boundary>','exec'))
put(CONTEXT+32,'<I',0);initial=bytes(memory);oracle.initial=initial
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x528880,15,'thug_walk_contact_construct_draft',0,'word',False,False,True),
 (0x528890,27,'thug_walk_contact_destroy_draft',0,'void',False,False,True),
 (0x52a190,247,'thug_walk_construct_draft',0,'word',False,False,True),
 (0x52a5c0,89,'thug_walk_create_draft',0,'word',True,False,False),
 (0x5288b0,149,'thug_walk_destroy_draft',0,'void',False,False,True),
 (0x52a290,33,'thug_walk_delete_draft',1,'word',True,False,True),
 (0x526060,82,'thug_walk_initialize_draft',1,'void',False,False,True),
 (0x525fb0,176,'thug_walk_bind_draft',0,'void',False,False,True),
 (0x527f20,508,'thug_walk_read_input_draft',0,'void',False,False,True),
 (0x527db0,360,'thug_walk_read_owner_draft',0,'void',False,False,True),
 (0x528370,141,'thug_walk_score_decay_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x52d4b0,'thug_walk_update_prefix_draft',0,'void',True,True),
 (0x582d90,'thug_skater_construct_walk_prefix_draft',6,'void',True,True)]:bind(*args)
exports.append([0x64c75c,'thug_walk_pending_methods_draft']);function_exports.append([0x52a5c0,'thug_walk_create_draft'])
for a in [0x62388b,0x62382b,0x417760,0x40ab50,0x40ab40,0x4637e0,0x4619f0,0x46c370,0x43da70,0x6236fc]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
CAMERA,INPUT,SCORECOMP,SCORE,REFOWNER=P+0x4000,P+0x5000,P+0x5600,P+0x5800,P+0x6000
class WalkGraph(AdjustGraph):
 def __init__(self):
  super().__init__()
  for at,n in [(P,0x1960),(CAMERA,0x110),(INPUT,0x4a0),(SCORECOMP,0x20),(SCORE,0x64),(REFOWNER,0x110)]:self.image[at-BASE:at-BASE+n]=bytes(n)
  self.put(P,'<6I',0x64c75c,0x726e85aa,0,OBJ,0,0);fields.add(P)
  self.put(OBJ,'<I',0x647650);fields.add(OBJ);self.put(OBJ+0x6c,'<16f',*IDENTITY)
  self.put(OBJ+0x4c,'<4f',10,20,30,1);self.put(OBJ+0xac,'<4f',3,4,5,1)
  self.put(CAMERA+0x6c,'<16f',*IDENTITY);self.put(P+0x175c,'<I',CAMERA);self.put(P+0x1770,'<I',INPUT)
  self.put(SCORECOMP,'<7I',0x647618,0xd262802f,1,OBJ,0,0,SCORE);fields.add(SCORECOMP);self.put(OBJ+0x100,'<I',SCORECOMP)
  self.put(SCORE+0x14,'<i',100);self.put(SCORE+0x60,'<f',1.25);self.put(P+0x1868,'<f',.5)
  self.put(P+0x48,'<4f',2,3,4,1);self.put(P+0x84,'<4f',0,0,0,1);self.put(P+0x714,'<f',.75)
  self.parameters()
 def parameters(self,dead=10,walk=.4,decay=.25):self.symbol(0x6775e538,10,self.structure([(0x4676a268,2,bits(dead)),(0xc1528f7f,2,bits(walk)),(0x3fb31dfc,2,bits(decay))]))
 def references(self,offsets,external=2):
  refs=[P+o for o in offsets]+[self.alloc(12) for _ in range(external)];self.put(REFOWNER+4,'<I',refs[0] if refs else 0)
  for i,ref in enumerate(refs):self.put(ref,'<3I',REFOWNER,refs[i-1] if i else 0,refs[i+1] if i+1<len(refs) else 0)
  return refs
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%40==0:print('Walk cases',len(labels),flush=True)
  return result
# Real original CRT eight-element construction and reverse destruction execute.
for fill,alignment,mask in itertools.product([0,0xa5,255],[0,1,4],[0,0x55,255,0xffffff00]):
 g=WalkGraph();g.image[P-BASE:P-BASE+0x1a00]=bytes([fill])*0x1a00;fields.add(P+alignment)
 g.run([call(0x52a190,P+alignment),call(0x5288b0,P+alignment)],f'construct/destroy/cache/{fill}/{alignment}/{mask:x}',{0x69190c:mask})
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=WalkGraph();g.run([call(0x52a5c0),call(0x52a290,HEAP,[flags])],f'factory/delete/{flags}')
g=WalkGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x52a5c0)]*2,'factory allocation failure')
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=WalkGraph();g.image[P-BASE:P-BASE+0x100]=bytes([fill])*0x100
 g.run([call(0x528880,P+alignment),call(0x528890,P+alignment)]*2,f'contact lifetime/{fill}/{alignment}')
# Existing references are valid intrusive chains; deleting record references
# must leave unrelated links intact, including an attached final probe.
for order in ['forward','reverse','scrambled']:
 g=WalkGraph();offsets=[0xa0+i*0xcc+0xb4 for i in range(8)]+[0x184c]
 if order=='reverse':offsets.reverse()
 if order=='scrambled':offsets=offsets[::2]+offsets[1::2]
 refs=g.references(offsets);g.run([call(0x5288b0,P)]*2,'destroy retained refs/'+order)
 assert oracle.word(REFOWNER+4)==refs[-2] and oracle.word(refs[-2]+4)==0 and oracle.word(refs[-2]+8)==refs[-1]
for mode in ['absent','camera','missing camera','secondary','collision','indirect']:
 g=WalkGraph();camera_component=g.component(0xc7d37ec2);g.put(CAMERA+0x100,'<I',0 if mode=='missing camera' else camera_component)
 key=0x42424242;entries=[(key,CAMERA)]
 if mode=='collision':entries=[(key^4,REFOWNER),(key,0),(key,CAMERA)]
 g.put(EM+8,'<2I',g.table([] if mode=='secondary' else entries),g.table(entries if mode=='secondary' else []))
 params=g.structure([] if mode=='absent' else [(0xc4e311fa,13,key)])
 if mode=='indirect':g.symbol(0x71234567,10,params);params=g.structure([(0,13,0x71234567)])
 g.put(P+0x710,'<I',0xffffffff);g.run([call(0x526060,P,[params])]*2,'initialize/'+mode)
links=[0x27d7cd28,0x7149b753,0x286a8d26,0xe594f0a2,0xd9151d4d,0x408d2aa9,0x43686585,0x5bd63b29,0x380d909a]
for shape in ['empty','all','reversed','duplicate']+[f'missing{i}' for i in range(9)]:
 g=WalkGraph();types=[] if shape=='empty' else links[::-1] if shape=='reversed' else links*2 if shape=='duplicate' else [t for i,t in enumerate(links) if shape!=f'missing{i}']
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x525fb0,P)]*2,'bind/'+shape)
 assert [oracle.word(P+0x1770+i*4) for i in range(9)]==[nodes[types.index(t)] if t in types else 0 for t in links]
# Camera-relative analog/digital input, deadzone and retained facing direction.
for analog,digital,pressed,state,retained in itertools.product([(0,0),(64,0),(0,-128),(80,80),(-128,127)],[0,1],[0,1],[0,1,4],[0,1]):
 g=WalkGraph();g.put(INPUT+0x228,'<2f',*analog);g.put(INPUT+0x24c,'<f',digital);g.put(INPUT+0x1c0,'<B',pressed);g.put(P+0x18,'<I',state);g.put(P+0x70c,'<B',retained)
 g.run([call(0x527f20,P)]*2,f'input selection/{analog}/{digital}/{pressed}/{state}/{retained}')
for camera,angle,dead in itertools.product([(0,0),(1,0),(1,2),(1e-30,-1e-30),(1e20,-1e20)],[-3,-1,-.17453292,0,.17453292,1,3],[0,10,180]):
 g=WalkGraph();g.parameters(dead);g.put(CAMERA+0x8c,'<f',camera[0]);g.put(CAMERA+0x94,'<f',camera[1]);g.put(INPUT+0x248,'<f',angle)
 g.put(INPUT+0x228,'<2f',80,-64);g.run([call(0x527f20,P)],f'input orientation/{camera}/{angle}/{dead}')
# Owner state reads, near-vertical fallback and normalization's four-lane path.
for forward,up in itertools.product([(0,1,0,1),(0,0,0,1),(.0005,9,0,2),(.001,7,0,2),(2,3,4,5),(1e-30,0,1e-30,1),(1e20,0,-1e20,2)],[(0,1,0,0),(1,0,2,1),(0,-.01,0,3)]):
 g=WalkGraph();g.put(OBJ+0x8c,'<4f',*forward);g.put(OBJ+0x7c,'<4f',*up);g.run([call(0x527db0,P)]*2,f'owner basis/{forward}/{up}')
for owner in [P-0x10,P,P+0x40]:
 g=WalkGraph();g.put(P+12,'<I',owner);g.put(owner+0x4c,'<4f',2,3,4,1);g.put(owner+0xac,'<4f',1,2,3,1);g.put(owner+0x7c,'<4f',0,1,0,0);g.put(owner+0x8c,'<4f',1,0,2,1)
 g.run([call(0x527db0,P)],f'owner overlap/{owner:x}')
for score,multiplier,charge,scale in itertools.product([-100,0,1,100,0x7fffffff],[-1,0,.5,1.25,1e20],[-1,0,.001,.5,1],[0,1,30]):
 g=WalkGraph();g.put(SCORE+0x14,'<i',score);g.put(SCORE+0x60,'<f',multiplier);g.put(P+0x1868,'<f',charge)
 g.run([call(0x528370,P)]*2,f'score decay/{score}/{multiplier}/{charge}/{scale}',{0x684fc8:bits(scale)})

# The actual shared component builder allocates, initializes, links and disposes
# Walk with another concrete component in both registry orders.
shared_records=[]
for reverse in [False,True]:
 g=WalkGraph();registry=[(0x726e85aa,0x52a5c0),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reverse}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 component=components[0x726e85aa];assert oracle.word(component+0x1788)==components[0x43686585]
 desc=g.alloc(16);g.put(desc,'<4I',0x12345678,0,0,0)
 g.run(calls+[call(0x45d720,component,[desc,0,0]),call(0x45d890,OBJ)],f'shared disposal/{reverse}')
 shared_records.append({'reverse':reverse,'components':{hex(k):v for k,v in components.items()}})

# Execute all original common frame instructions and callees, stopping before
# each unresolved state handler; the hook supplies no gameplay return value.
frame_hits=Counter();frame_active=False
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:frame_hits.update([at]),begin=0x52d4b0,end=0x52d67e)
def frame_boundary(cpu,at,size,user):
 if not frame_active:return
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,0,P,1));cpu.emu_stop()
for at in [0x52d300,0x52cef0,0x440bf0,0x4425b0,0x52ad10,0x52d563]:oracle.cpu.hook_add(UC_HOOK_CODE,frame_boundary,begin=at,end=at)
frame_records=[]
for state,latched,held,analog,score in itertools.product([0,1,2,3,4,5,0xffffffff],[0,1],[0,1],[False,True],[-100,100]):
 g=WalkGraph();g.put(P+0x18,'<I',state);g.put(P+0x9a,'<B',latched);g.put(INPUT+0x100,'<B',held)
 g.put(P+0x78,'<I',0x12345678);g.put(P+0x718,'<B',1);g.put(SCORE+0x14,'<i',score)
 if analog:g.put(INPUT+0x228,'<2f',80,-64);g.put(INPUT+0x248,'<f',.5)
 stages=g.run([],f'frame prefix/{state}/{latched}/{held}/{analog}/{score}')
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,P);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 frame_active=True
 try:cpu.emu_start(0x52d4b0,oracle.stop,count=500000)
 finally:frame_active=False
 boundary_at=[0x52d300,0x52cef0,0x440bf0,0x4425b0,0x52ad10][state] if state<5 else 0x52d563
 assert cpu.reg_read(UC_X86_REG_EIP)==boundary_at and oracle.word(BOUNDARY)==boundary_at
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:outputs.append([BASE+j,after[j:j+4].hex()])
 stages.append({'fn':'0x52d4b0','this':P,'args':[Q,DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True,'boundary_factory':boundary_at})
 oracle.counts['thug_walk_update_prefix_draft']+=1
 frame_records.append({'state':state,'latched':latched,'held':held,'analog':analog,'score':score,'boundary':hex(boundary_at)})
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280),(0xd8cc3428,0x4fbe20),(0x726e85aa,0x52a5c0)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Walk/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58,0xd8cc3428,0x726e85aa] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x7cd3e6d5 if local&255 else 0x850eef66)
 if local&255:
  links={t:c for c,t in chain}
  assert oracle.word(OBJ+0x258)==links[0x270f56e1] and oracle.word(OBJ+0x284)==links[0xd9151d4d] and oracle.word(OBJ+0x280)==links[0x5bd63b29]
  assert oracle.cpu.mem_read(links[0xd9151d4d]+0x18,1)==b'\x00'
  assert oracle.word(OBJ+0x270)==links[0x11b4c67f] and oracle.word(OBJ+0x288)==links[0x726e85aa]
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_walk_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})

scope='Eleven complete original routines recover Walk allocation, construction, embedded collision-contact lifetime, disposal, optional camera initialization, dependency linking, camera-relative input, owner-vector loading and score-dependent decay. Actual CRT loops, collision references/cache, QB lookup, input magnitude and timing callees execute. Whole arena/globals/heap and completed-call preserved registers compare. Initialized graphs with required QB parameters are contracts; factory allocation failure is also exercised at the explicit test-heap boundary. Shared builder startup/disposal executes. Original skater construction continues through Walk to local7cd3e6d5 or remote850eef66. The Walk frame executes common setup and explicitly stops before each of five state handlers (or the remaining common tail for an invalid state); neither partial parent counts as recovered. State behavior, remaining startup/frames, rendering and original playable training remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'memory_fixture':'skater-walk-memory.wasm','native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
finish('skater-walk',scope,{},extra)
p=folder/'skater-walk-original.json';report=json.loads(p.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x12d4b0,463),0x52d4b0))
report['partial_frame']={'address':'0x52d4b0','covered':sum(bool(frame_hits[i.address]) for i in code),'total':len(code),'interrupted_calls':len(frame_records),'records':frame_records}
report['shared_startup_records']=shared_records
p.write_text(json.dumps(report,indent=2)+'\n')
(folder/'skater-walk-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
