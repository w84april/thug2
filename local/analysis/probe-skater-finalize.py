"""Original FinalizePhysics, matrix repair and real skater startup comparisons."""
from pathlib import Path
source=Path('local/analysis/probe-skater-adjust.py').read_text().split('# Exact lifecycle')[0]
source=source.replace('0xe594f0a2','0xd8cc3428')
exec(compile(source,'<preserved startup oracle; CleanupState boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x405480,377,'thug_matrix_repair_basis_draft',0,'byte',False,False,True),
 (0x5138b0,40,'thug_skater_animation_speed_draft',1,'void',False,False,True),
 (0x511280,121,'thug_skater_finalize_create_draft',0,'word',True,False,False),
 (0x511010,11,'thug_skater_finalize_destroy_draft',0,'void',False,False,True),
 (0x511020,33,'thug_skater_finalize_delete_draft',1,'word',True,False,True),
 (0x511050,37,'thug_skater_finalize_bind_draft',0,'void',False,False,True),
 (0x511080,511,'thug_skater_finalize_update_draft',0,'void',True,True,True)]
for row in specs:bind_new(*row)
functions['0x5138b0']['float_args']=[0]
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d920,'thug_object_update_components',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_finalize_prefix_draft',6,'void',True,True)]:bind(*args)
exports.extend([[0x64bdec,'thug_skater_finalize_methods_draft'],[0x646648,'thug_trigger_methods_draft']])
function_exports.extend([[0x511280,'thug_skater_finalize_create_draft'],[0x434b90,'thug_trigger_create_draft']])
for at in [0x405170,0x41a640,0x402550,0x4023f0,0x404090,0x580790,0x5805b0,0x45db90]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
PH,STATE,SOUND,ANIM,MATRIX,OTHER=[P+x for x in [0x2000,0x4000,0x4200,0x4400,0x4600,0x4800]]
class FinalizeGraph(AdjustGraph):
 def __init__(self,limit=100):
  super().__init__()
  for at,n in [(P,0x80),(PH,0x1540),(STATE,0x128),(SOUND,0x24),(ANIM,0x110),(OTHER,0x324)]:self.image[at-BASE:at-BASE+n]=bytes(n)
  self.put(OBJ,'<I',0x647650);fields.add(OBJ);self.put(OBJ+0x14,'<I',0x100)
  self.put(EM+8,'<2I',self.table([(0x100,OBJ)]),self.table([]))
  self.put(P,'<8I',0x64bdec,0x9b373e58,0,OBJ,0,0,PH,STATE);fields.add(P)
  for at,kind,next_,table in [(PH,0x5bd63b29,STATE,0x64bc48),(STATE,0x43686585,SOUND,0x64c140),(SOUND,0x187574fa,ANIM,0x647618),(ANIM,0xb5f1e9d2,0,0x647618)]:
   self.put(at,'<6I',table,kind,0,OBJ,next_,0);fields.add(at)
  self.put(OBJ+0x100,'<I',PH);self.put(OBJ+0x280,'<I',PH);self.put(PH+0x1528,'<I',STATE)
  self.put(OBJ+0x6c,'<16f',*IDENTITY);self.put(PH+0x18,'<16f',*IDENTITY);self.put(MATRIX,'<16f',*IDENTITY);self.put(OTHER+0x6c,'<16f',*IDENTITY)
  self.put(PH+0x58,'<8I',1,2,3,4,0x7fc12345,0x7f812345,0x80000000,0xffffffff)
  self.put(OBJ+0xac,'<4f',3,99,4,1)
  difficulty=self.alloc(0x3ac);self.image[difficulty-BASE:difficulty-BASE+0x3ac]=bytes(0x3ac)
  self.put(GAME+0x38c,'<I',difficulty);self.put(difficulty+0x398,'<I',self.structure([(0,1,1)]))
  self.symbol(0x8cbc89dd,10,self.structure([]));pair=self.alloc(12);self.put(pair,'<I2f',0,limit,limit)
  self.symbol(0xcc5f87aa,10,self.structure([(0,5,pair)]))
  self.symbol(0x78f80ec4,2,bits(.125))
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%40==0:print('Finalize cases',len(labels),flush=True)
  return result

for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=FinalizeGraph();g.run([call(0x511280),call(0x511020,HEAP,[flags])],f'factory/delete/{flags}')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=FinalizeGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80;fields.add(P+offset)
 g.run([call(0x511010,P+offset)]*2,f'destroy/{fill}/{offset}')
for shape in ['empty','all','reversed','duplicate','missing physics','missing state']:
 g=FinalizeGraph();types=[] if shape=='empty' else [0x43686585,0x5bd63b29] if shape=='reversed' else [0x5bd63b29,0x43686585]*2 if shape=='duplicate' else [0x43686585] if shape=='missing physics' else [0x5bd63b29] if shape=='missing state' else [0x5bd63b29,0x43686585]
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x511050,P)]*2,f'bind/{shape}')
 assert [oracle.word(P+0x18+i*4) for i in range(2)]==[nodes[types.index(t)] if t in types else 0 for t in [0x5bd63b29,0x43686585]]
# Full repair tree, threshold neighbors and untouched raw W/translation words.
for lengths in itertools.product([0,0.5,1,2],repeat=3):
 g=FinalizeGraph()
 for i,value in enumerate(lengths):g.put(MATRIX+i*20,'<f',value)
 for i in [3,7,11,12,13,14,15]:g.put(MATRIX+i*4,'<I',0x7f812345+i)
 g.run([call(0x405480,MATRIX)]*2,f'basis lengths/{lengths}')
for axis,raw in itertools.product(range(3),[bits(.99)-1,bits(.99),bits(.99)+1,1,0x80000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345]):
 g=FinalizeGraph();g.put(MATRIX+axis*20,'<I',raw);g.run([call(0x405480,MATRIX)]*2,f'basis threshold/raw/{axis}/{raw:x}')
for axis in range(3):
 for scale in [.25,1,1e-20,1e20]:
  g=FinalizeGraph();rows=[[0,0,0,1],[2*scale,3*scale,4*scale,2],[-scale,5*scale,2*scale,3]]
  for i in range(3):g.put(MATRIX+((axis+i)%3)*16,'<4f',*rows[i])
  g.run([call(0x405480,MATRIX)]*2,f'rebuild cross/{axis}/{scale}')
for raw in [0,0x80000000,1,0x80000001,bits(-10),bits(.5),bits(1)-1,bits(1),bits(1)+1,bits(10),0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xffffffff]:
 g=FinalizeGraph();g.run([call(0x5138b0,ANIM,[raw])]*2,f'animation speed bits/{raw:x}')
# Real stat lookup, matrix helpers, byte/dirty propagation and repeated frames.
frame_records=[]
for enabled,state,velocity in itertools.product([0,1,255],[0,1,2,3,0xffffffff],[(0,0),(.999,0),(1,0),(-1,0),(0,.999),(0,1),(3,4)]):
 g=FinalizeGraph();g.put(PH+0x256,'<B',enabled);g.put(STATE+0x18,'<I',state);g.put(STATE+0xf4,'<B',0xa5)
 g.put(OBJ+0xac,'<f',velocity[0]);g.put(OBJ+0xb4,'<f',velocity[1]);g.run([call(0x511080,P,[Q])]*2,f'frame gate/{enabled}/{state}/{velocity}')
 frame_records.append({'enabled':enabled,'state':state,'velocity':velocity,'stationary':oracle.cpu.mem_read(STATE+0xf4,1)[0],'speed':oracle.word(ANIM+0x104)})
for dirty,changed in itertools.product([0,2,128,255],range(8)):
 g=FinalizeGraph();g.put(STATE+0x58,'<B',0x81);g.put(STATE+0xe1,'<B',0x42);g.put(STATE+0x70,'<B',0xfe);g.put(STATE+0x18,'<I',1)
 g.put(ANIM+0xfd,'<B',dirty);g.put(ANIM+0x100,'<B',0x81^bool(changed&1));g.put(ANIM+0x60,'<B',0x42^bool(changed&2));g.put(ANIM+0x74,'<I',1^bool(changed&4))
 g.run([call(0x511080,P,[Q])]*2,f'frame dirty/{dirty}/{changed}')
 assert oracle.cpu.mem_read(ANIM+0xfd,1)[0]==dirty|bool(changed)
for limit,velocity in itertools.product([-10,0,.5,1,100,1e-20,1e20],[(0,0),(3,4),(1e-30,-1e-30),(1e20,-1e20)]):
 g=FinalizeGraph(limit);g.put(OBJ+0xac,'<f',velocity[0]);g.put(OBJ+0xb4,'<f',velocity[1]);g.run([call(0x511080,P,[Q])],f'frame speed/{limit}/{velocity}')
for basis,other in itertools.product(['identity','zero','fixed zero','parallel','scaled'],[False,True]):
 g=FinalizeGraph();values=[0]*16 if basis=='zero' else IDENTITY[:]
 if basis=='fixed zero':values[5]=0
 if basis=='parallel':values[4:8]=[1,0,0,0]
 if basis=='scaled':values[0]=2;values[5]=.5;values[10]=3
 g.put(OBJ+0x6c,'<16f',*values)
 if other:g.put(PH+12,'<I',OTHER);g.put(OTHER+0x6c,'<16f',*[float(i) for i in range(16)])
 g.run([call(0x511080,P,[Q])]*2,f'frame matrix recovery/{basis}/{other}')
# The actual owner dispatcher visits this component and leaves suspended siblings.
for reverse in [False,True]:
 g=FinalizeGraph();chain=[PH,STATE,SOUND,ANIM]
 if reverse:chain.reverse()
 g.put(OBJ+0x100,'<I',P);g.put(P+16,'<I',chain[0])
 for i,node in enumerate(chain):g.put(node+8,'<I',1);g.put(node+16,'<I',chain[i+1] if i+1<len(chain) else 0)
 g.run([call(0x45d920,OBJ,[Q])]*2,f'owner frame/{reverse}')
shared_records=[]
for reverse in [False,True]:
 g=FinalizeGraph();registry=[(0x9b373e58,0x511280),(0x43686585,0x519740),(0x5bd63b29,0x505440)];g.registry(registry)
 order=registry[::-1] if reverse else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reverse}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 component=components[0x9b373e58];assert oracle.word(component+0x18)==components[0x5bd63b29] and oracle.word(component+0x1c)==components[0x43686585]
 desc=g.alloc(16);g.put(desc,'<4I',0x12345678,0,0,0)
 g.run(calls+[call(0x45d720,component,[desc,0,0]),call(0x45d890,OBJ)],f'shared disposal/{reverse}')
 shared_records.append({'reverse':reverse,'components':{hex(k):v for k,v in components.items()}})

prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90),(0x9b373e58,0x511280)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through FinalizePhysics/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2,0x9b373e58] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0xd8cc3428 if local&255 else 0x850eef66)
 if local&255:
  links={t:c for c,t in chain}
  assert oracle.word(OBJ+0x258)==links[0x270f56e1] and oracle.word(OBJ+0x284)==links[0xd9151d4d] and oracle.word(OBJ+0x280)==links[0x5bd63b29]
  assert oracle.cpu.mem_read(links[0xd9151d4d]+0x18,1)==b'\x00'
  assert oracle.word(OBJ+0x270)==links[0x11b4c67f]
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_finalize_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})

scope='Seven complete original routines recover FinalizePhysics creation, disposal, dependency binding and full frame, plus degenerate matrix repair and animation speed clamp. Real stat lookup, matrix operations and component lookup run without game-call substitutions. Shared creation/finalization/disposal and actual owner dispatch execute. Whole arena, globals, heap and completed-call preserved registers compare. The constructor continues through FinalizePhysics and explicitly stops before CleanupState d8cc3428; remote850eef66 unchanged. Partial construction is not a completed routine. Initialized dependencies and successful allocation are internal contracts. Remaining startup/frames, later score linkage, camera/rendering and original playable training remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved=coverage.copy();coverage.clear();finish('skater-finalize',scope,{},extra);coverage.update(saved)
p=folder/'skater-finalize-original.json';report=json.loads(p.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records;report['frame_records']=frame_records
p.write_text(json.dumps(report,indent=2)+'\n')
(folder/'skater-finalize-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
