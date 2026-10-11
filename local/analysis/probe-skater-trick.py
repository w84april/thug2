"""Original Trick/PhysicsControl startup and local skater physics initialization."""
from pathlib import Path
source=Path('local/analysis/probe-skater-matrix.py').read_text().split('# Direct helper:')[0]
old='if oracle.word(node+8) not in [0x270f56e1,0x850eef66]:return';assert old in source
source=source.replace(old,'if oracle.word(node+8) not in [0x52d61a0d,0x850eef66]:return')
exec(compile(source,'<preserved MatrixQueries oracle; later skater boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x588170,13,'thug_trick_history_construct_draft',0,'word',False,False,True),
 (0x51f320,406,'thug_trick_reset_draft',0,'void',False,False,True),
 (0x522390,118,'thug_trick_construct_draft',0,'word',False,False,True),
 (0x523490,89,'thug_trick_create_draft',0,'word',True,False,False),
 (0x51f2b0,101,'thug_trick_finalize_draft',0,'void',False,False,True),
 (0x5234f0,102,'thug_trick_destroy_draft',0,'void',True,False,True),
 (0x5243f0,33,'thug_trick_delete_draft',1,'word',True,False,True),
 (0x5176c0,11,'thug_physics_control_destroy_draft',0,'void',False,False,True),
 (0x5176d0,7,'thug_physics_control_initialize_draft',1,'void',False,False,True),
 (0x517740,33,'thug_physics_control_delete_draft',1,'word',True,False,True),
 (0x517770,44,'thug_physics_control_finalize_draft',0,'void',False,False,True),
 (0x517830,114,'thug_physics_control_create_draft',0,'word',True,False,False)]
for spec in specs:bind_new(*spec)
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x514030,'thug_skater_matrix_update_draft',0,'void',False,False),
 (0x582d90,'thug_skater_construct_trick_prefix_draft',6,'void',True,True)]:bind(*args)
exports += [[0x64c508,'thug_trick_pending_methods_draft'],[0x64bfe0,'thug_physics_control_pending_methods_draft']]
function_exports += [[0x523490,'thug_trick_create_draft'],[0x517830,'thug_physics_control_create_draft']]
initial=bytes(memory);oracle.initial=initial
C=P+0x2000;H=P+0x2400
LINKS=[0x27d7cd28,0x589e5fb3,0x5bd63b29,0x488af07a,0x43686585,0x4ff8dac6]
class TrickGraph(ScoreGraph):
 def __init__(self,fill=0):
  super().__init__();self.image[P-BASE:P-BASE+0x1bc0]=bytes([fill])*0x1bc0
  self.put(P,'<6I',0x64c508,0x270f56e1,0,OBJ,0,0);fields.add(P);self.put(P+0xa28,'<I',0)
  self.image[C-BASE:C-BASE+0x30]=bytes([fill])*0x30
  self.put(C,'<6I',0x64bfe0,0xd9151d4d,0,OBJ,0,0);fields.add(C)
  self.symbol(0x78f80ec4,2,bits(.125))
 def chain(self,types):
  nodes=[self.component(t) for t in types]
  for i,node in enumerate(nodes):self.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
  self.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);return nodes
 def run(self,calls,label,changes=None):
  try:result=super().run(calls,label,changes)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%50==0:print('Trick startup cases',len(labels),flush=True)
  return result
for fill,offset in itertools.product([0,0xa5,255],[0,1,4,15]):
 g=TrickGraph();g.image[H-BASE:H-BASE+0x820]=bytes([fill])*0x820
 g.run([call(0x588170,H+offset)]*2,f'history capacity field/{fill}/{offset}')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 for fn in [0x51f320,0x522390]:
  g=TrickGraph();g.image[P-BASE:P-BASE+0x1be0]=bytes([fill])*0x1be0
  g.run([call(fn,P+offset)]*2,f'constructor/reset preserve bytes/{fn:x}/{fill}/{offset}')
rng=random.Random(0x51f320)
for i in range(12):
 g=TrickGraph();g.image[P-BASE:P-BASE+0x1bc0]=bytes(rng.getrandbits(8) for _ in range(0x1bc0))
 g.run([call(0x51f320,P)]*2+[call(0x522390,P)],f'patterned storage/{i}')
for shape in ['empty','all','reversed','duplicates']+[f'missing {i}' for i in range(6)]:
 g=TrickGraph(0xa5);types=[] if shape=='empty' else LINKS[::-1] if shape=='reversed' else LINKS*2 if shape=='duplicates' else [t for i,t in enumerate(LINKS) if shape!=f'missing {i}']
 nodes=g.chain(types);g.run([call(0x51f2b0,P)]*2,'Trick links/'+shape)
 assert [oracle.word(P+0x20+4*i) for i in range(6)]==[nodes[types.index(t)] if t in types else 0 for t in LINKS]
for fill,flag in itertools.product([0,0xa5,255],[0,1,2,3,255,256,257,0xffffffff]):
 g=TrickGraph(fill);g.put(C+8,'<I',flag)
 g.run([call(0x5176d0,C,[0])]*2+[call(0x5176c0,C)],f'PhysicsControl minimal initialize/destroy/{fill}/{flag}')
for shape in ['state only','all','reversed','duplicate physics','duplicate state']:
 g=TrickGraph(0xa5);types=[0x43686585] if shape=='state only' else [0x43686585,0x5bd63b29] if shape=='reversed' else [0x5bd63b29,0x43686585]
 if shape=='duplicate physics':types += [0x5bd63b29]
 if shape=='duplicate state':types += [0x43686585]
 nodes=g.chain(types);g.run([call(0x517770,C)]*2,'PhysicsControl finalization/'+shape)
 assert oracle.word(C+0x28)==(nodes[types.index(0x5bd63b29)] if 0x5bd63b29 in types else 0)
 assert oracle.word(C+0x2c)==nodes[types.index(0x43686585)] and oracle.word(nodes[types.index(0x43686585)]+0x1c)==0xffffffff
for factory,delete in [(0x523490,0x5243f0),(0x517830,0x517740)]:
 for flags in [0,1,2,255,256,257,0xffffffff]:
  g=TrickGraph();g.run([call(factory),call(delete,HEAP,[flags])],f'factory/delete/{factory:x}/{flags}')
# A real owned QB structure is recursively disposed, including nested values.
for shape,flags,waits in itertools.product(['absent','empty','values','nested'],[0,1,256,257],[0,2]):
 g=TrickGraph(0xa5);g.put(P+8,'<I',waits);owned=0
 if shape!='absent':
  values=[] if shape=='empty' else [(0x11,1,123),(0x12,3,g.text('owned trick mapping')),(0x13,12,g.array(1,[1,2,3]))]
  if shape=='nested':values.append((0x14,10,g.structure([(0x15,3,g.text('nested'))])))
  owned=g.structure(values)
 g.put(P+0xa28,'<I',owned)
 g.run([call(0x5243f0,P,[flags])],f'owned structure lifetime/{shape}/{flags}/{waits}')
 assert oracle.word(P+0xa28)==owned
for slot,selected in itertools.product([0,1],[0,1]):
 g=TrickGraph();g.put(POOL,'<6I',BLOCKS,BLOCKS+0x100,0,0,1,BLOCKS+16);g.put(BLOCKS,'<2I',0,0);g.put(BLOCKS+16,'<I',0);g.put(P+0xa28,'<I',BLOCKS)
 g.run([call(0x5234f0,P)],f'owned structure selected/alternate pool/{slot}/{selected}',{0x6f3614:selected,0x6f361c+4*slot:POOL})
# Real State/MatrixQueries/Trick/PhysicsControl/Physics creation, finalization,
# cross-links and cleanup. Shared builder routes to recovered virtual methods.
shared_records=[]
registry=[(0x43686585,0x519740),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440)]
for reversed_ in [False,True]:
 g=TrickGraph();g.registry(registry)
 order=registry[::-1] if reversed_ else registry
 descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[d,0]) for d in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'real shared startup and links/{reversed_}')
 components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 trick=components[0x270f56e1];control=components[0xd9151d4d];physics=components[0x5bd63b29];state=components[0x43686585];matrix=components[0xbf518e27]
 assert oracle.word(trick+0x28)==physics and oracle.word(trick+0x30)==state
 assert oracle.word(control+0x28)==physics and oracle.word(control+0x2c)==state and oracle.word(state+0x1c)==0xffffffff
 assert oracle.word(matrix+0x5c)==physics and oracle.word(physics+0x1518)==trick
 g.run(calls+[call(0x514030,matrix),call(0x45d890,OBJ)],f'real shared startup/matrix update/disposal/{reversed_}')
 shared_records.append({'reverse_order':reversed_,'components':{hex(k):v for k,v in components.items()}})
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Trick and Physics/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x52d61a0d if local&255 else 0x850eef66)
 if local&255:
  links={t:c for c,t in chain}
  assert oracle.word(OBJ+0x258)==links[0x270f56e1] and oracle.word(OBJ+0x284)==links[0xd9151d4d] and oracle.word(OBJ+0x280)==links[0x5bd63b29]
  assert oracle.cpu.mem_read(links[0xd9151d4d]+0x18,1)==b'\x00'
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_trick_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Twelve complete original routines recover Trick history initialization, selective state reset, constructor/factory, six dependency links and owned-structure destruction/delete; PhysicsControl initializer, factory, required State/Physics links and destruction/delete. The original shared builder constructs State, MatrixQueries, Trick, PhysicsControl and Physics in both orders, links them, updates the cached matrix and disposes the owner. Original582d90 local startup now creates Trick and PhysicsControl, runs existing Physics creation/initialization and stores all three links, then stops before52d61a0d; nonlocal850eef66 is unchanged. Whole arena/globals/heap and completed-call preserved registers compare exactly, without math or NaN allowances. Successful allocator and valid internal graphs, including required State on Control finalization, are original contracts. Trick and Control frame/commands explicitly trap; this is startup/lifetime recovery, not a complete skater, cold boot or playable frame. Earlier asset and scene traces remain separate.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-trick',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-trick-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
