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
source=source.replace("source=source.replace('0xe594f0a2','0x726e85aa')","source=source.replace('0xe594f0a2','0xb5f1e9d2')")
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

functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
bind(0x582d90,"thug_skater_construct_balance_prefix_draft",6,"void",True,True)
exports.extend([[0x64bef0,"thug_local_net_pending_methods_draft"],[0x64bdb8,"thug_end_run_methods_draft"]])
function_exports.extend([[0x513630,"thug_local_net_create_draft"],[0x510f90,"thug_end_run_create_draft"],[0x4f9170,"thug_balance_component_create_draft"]])
exports.extend([[0x64ba30,"thug_balance_component_pending_methods_draft"],[0x64ed24,"thug_balance_record_methods_draft"]])
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280),(0xd8cc3428,0x4fbe20),(0x726e85aa,0x52a5c0),(0x7cd3e6d5,0x513630),(0xb1d5a3e1,0x510f90),(0x589e5fb3,0x4f9170)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through BalanceTrick/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58,0xd8cc3428,0x726e85aa,0x7cd3e6d5,0xb1d5a3e1,0x589e5fb3] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0xb5f1e9d2 if local&255 else 0x850eef66)
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
 oracle.counts['thug_skater_construct_balance_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})

scope='Original skater construction proceeds through BalanceTrick creation and stops beforeb5f1e9d2; nonlocal850eef66 is unchanged. Constructor remains partial and receives no completion credit. No component frame, cold boot, rendering or playable-level claim.'
finish('skater-balance-startup',scope,{}, {**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,'memory_fixture':'skater-walk-memory.wasm','native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]})
path=folder/'skater-balance-startup-original.json';report=json.loads(path.read_text())
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records,'counted_complete':False}
path.write_text(json.dumps(report,indent=2)+'\n')
print('Partial constructor:',report['partial_constructor']['covered'],'/',len(code))
