"""Original AdjustPhysics startup and moving-geometry containment/escape."""
from pathlib import Path
source=Path('local/analysis/probe-skater-gap.py').read_text().split('# Selective constructor/initializer')[0]
assert source.count('0x9f9cc949')==1
source=source.replace('0x9f9cc949','0xe594f0a2')
exec(compile(source,'<preserved Gap oracle; later boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x4f80e0,123,'thug_skater_adjust_create_draft',0,'word',True,False,False),
 (0x4f8040,11,'thug_skater_adjust_destroy_draft',0,'void',False,False,True),
 (0x4f8050,33,'thug_skater_adjust_delete_draft',1,'word',True,False,True),
 (0x4f8080,85,'thug_skater_adjust_finalize_draft',0,'void',False,False,True),
 (0x417190,29,'thug_collision_probe_start_draft',1,'void',False,False,True),
 (0x4171b0,30,'thug_collision_probe_end_draft',1,'void',False,False,True),
 (0x427700,757,'thug_moving_contact_enclosing_draft',2,'word',False,False,True),
 (0x427b30,320,'thug_moving_contact_escape_draft',2,'word',False,False,True)]
for row in specs:bind_new(*row)
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_adjust_prefix_draft',6,'void',True,True)]:bind(*args)
Q=0x1ff0000;SCROOT=BASE+0x1e0000;MOVROOT=SCROOT+32;POS=SCROOT+64;PREV=POS+32;OUT=POS+64
exports += [[0x64b964,'thug_skater_adjust_pending_methods_draft'],[Q,'thug_sphere_query_fixture_state'],[0x645c18,'thug_static_collision_methods'],[0x645ce0,'thug_moving_collision_methods']]
function_exports.append([0x4f80e0,'thug_skater_adjust_create_draft'])
template=json.loads((folder/'contact-assembly-fixtures.json').read_text())
for row,value in zip(template['globals'],template['cases'][0]['globals']):
 name,at,width,offset=row
 if not name.startswith(('thug_collision_','thug_moving_collision_','thug_sphere_query_fixture_state')):continue
 value=(offset//4*2)|((offset//4*2+1)<<16) if name=='thug_collision_fallback_indices' else 0
 if at not in index:glob(name,at,value,width,offset)
 else:defaults[index[at]]=value
defaults[index[0x6fa7ec]]=SCROOT;defaults[index[0x691984]]=MOVROOT
put(SCROOT,'<4I',0,0xffffffff,0,SCROOT);put(MOVROOT,'<4I',0,0xffffffff,0,MOVROOT)
initial=bytes(memory);oracle.initial=initial;oracle.instruction_limit=12000000
for at in [0x417760,0x4172f0,0x417210,0x417240,0x4637e0,0x5beaa0,0x4118c0,0x414460,0x418710]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
class AdjustGraph(ScoreGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x80]=bytes(0x80);self.put(P,'<6I',0x64b964,0x9f9cc949,0,OBJ,0,0);fields.add(P)
  self.put(POS,'<4f',0,0,0,1);self.put(PREV,'<4f',1000,0,0,1);self.put(OUT,'<4I',0x11111111,0x22222222,0x33333333,0x44444444)
  self.actors=[];self.owners=[];self.statics=[];self.movnodes=[]
 def plane(self,height,moving=True,up=True,x=0,half=32,flags=0,velocity=(0,0,0,0),owner=None):
  geo=self.alloc(64);face=self.alloc(12);verts=self.alloc(36);actor=self.alloc(0xd4);aux=self.alloc(4)
  self.image[geo-BASE:geo-BASE+64]=bytes(64);self.image[actor-BASE:actor-BASE+0xd4]=bytes(0xd4)
  self.put(geo,'<IHHHBBI',0x71700000+len(self.actors),0,3,1,0,0,face)
  self.put(geo+16,'<8f',-half,height,-half,1,half,height,half,1);self.put(geo+48,'<4I',verts,0,aux,0)
  self.put(face,'<5H',flags,0,0,2 if up else 1,1 if up else 2)
  self.put(verts,'<9f',-half,height,-half,half,height,-half,0,height,half)
  self.put(aux,'<3B',10,128,255);self.put(actor,'<I',0x645ce0 if moving else 0x645c18);fields.add(actor)
  self.put(actor+4,'<I',0x71700000+len(self.actors));self.put(actor+12,'<I',geo)
  if moving:
   if owner is None:
    owner=self.alloc(0x100);self.image[owner-BASE:owner-BASE+0x100]=bytes(0x100);self.put(owner+0x14,'<I',0x18100000+len(self.owners));self.put(owner+0xac,'<4f',*velocity);self.owners.append(owner)
   self.put(actor+16,'<4f',x,0,0,1);self.put(actor+32,'<16f',*IDENTITY);self.put(actor+96,'<16f',*IDENTITY)
   self.put(actor+0xa0,'<IfB',owner,500,1)
   node=self.alloc(16);self.put(node,'<4I',0,actor,0,MOVROOT);self.put((self.movnodes[-1] if self.movnodes else MOVROOT)+12,'<I',node)
   if not self.movnodes:self.put(MOVROOT,'<4I',0,actor,0,node);self.put(node,'<4I',0,0xffffffff,0,node)
   else:
    # Keep a stable sentinel, append by replacing the old sentinel's record.
    prev=self.movnodes[-1];self.put(prev,'<4I',0,actor,0,node);self.put(node,'<4I',0,0xffffffff,0,node)
   self.movnodes.append(node)
  else:
   # Static geometry already uses world coordinates.
   self.statics.append(actor);self.static_scene()
  self.actors.append(actor);return actor,owner
 def static_scene(self):
  scene=self.alloc(0xd8);grid=self.alloc(0x4b30);array=self.alloc(len(self.statics)*4)
  self.image[grid-BASE:grid-BASE+0x4b30]=bytes(0x4b30);self.put(SCROOT,'<4I',0,scene,0,0);self.put(scene+0xd4,'<I',grid)
  self.put(grid,'<10f2I',-1000,-1000,-1000,1,1000,1000,1000,1,2000,2000,1,1)
  self.put(grid+0x54,'<I',len(self.statics));self.put(grid+0x5c,'<I',array)
  for i,a in enumerate(self.statics):self.put(array+4*i,'<I',a)
 def run(self,calls,label,changes=None):
  for reg,value in [(UC_X86_REG_FPSW,0),(UC_X86_REG_FPTAG,0xffff),(UC_X86_REG_MXCSR,0x1f80)]:oracle.cpu.reg_write(reg,value)
  try:result=super().run(calls,label,changes)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%25==0:print('Adjust cases',len(labels),flush=True)
  return result
# Exact lifecycle, dependency searches and byte flags.
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=AdjustGraph();g.run([call(0x4f80e0),call(0x4f8050,HEAP,[flags])],f'factory/delete/{flags}')
for fill,flags in itertools.product([0,0xa5,255],[0,1,2,255,256,257,0xffffffff]):
 g=AdjustGraph();g.image[P-BASE:P-BASE+0x34]=bytes([fill])*0x34;g.put(P+8,'<I',flags)
 g.run([call(0x4f8040,P)]*2,f'destroy writes/{fill}/{flags}')
links=[0x5bd63b29,0x286a8d26,0x8a897dd2,0x408d2aa9,0x43686585]
for shape in ['empty','all','reversed','duplicates']+[f'missing{i}' for i in range(5)]:
 g=AdjustGraph();types=[] if shape=='empty' else links[::-1] if shape=='reversed' else links*2 if shape=='duplicates' else [t for i,t in enumerate(links) if shape!=f'missing{i}']
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x4f8080,P)]*2,'dependency lookup/'+shape)
 assert [oracle.word(P+0x20+i*4) for i in range(5)]==[nodes[types.index(t)] if t in types else 0 for t in links]
for fn,offset,raw in itertools.product([0x417190,0x4171b0],[-4,0,1,4,8,12,16,20,32,64],[0,0x80000000,0x7f812345,0x7fc12345,0xffffffff]):
 g=AdjustGraph();g.put(P+0x80,'<20I',*[raw^i for i in range(20)]);g.run([call(fn,P+0x90,[P+0x90+offset])]*2,f'probe forward words/{fn:x}/{offset}/{raw:x}')
# Original geometry queries only: no collision answers are hooked or replaced.
collision_records=[]
for kind in ['empty','one top','static top','one bottom','both faces','excluded','nine shells','ten shells','top then static','top then miss']:
 g=AdjustGraph()
 if kind!='empty':
  if kind in ['nine shells','ten shells']:
   for i in range(9 if kind=='nine shells' else 10):
    _,owner=g.plane(300-i*20);g.plane(299-i*20,up=False,owner=owner)
  else:
   _,owner=g.plane(40,moving=kind!='static top',up=kind!='one bottom',flags=0x10 if kind=='excluded' else 0)
   if kind in ['both faces','top then static','top then miss']:g.plane(39,up=False,owner=owner)
   if kind=='top then static':g.plane(20,moving=False)
 stages=g.run([call(0x427700,P,[POS,OUT,Q])]*2,'containment/'+kind)
 collision_records.append({'kind':kind,'owner':stages[0]['result'],'actors':g.actors})
for height in [5.9,6,6.1,20,399.9,400,400.1]:
 for x in [0,8,31,33]:
  g=AdjustGraph();g.plane(height,x=x);g.run([call(0x427700,P,[POS,OUT,Q])],'height/bounds/'+str((height,x)))
for velocity in [(0,0,0,0),(3000,0,0,0),(-3000,0,0,0),(0,3000,0,0),(0,0,3000,0),(1,-2,3,4)]:
 for old in [(1000,0,0,1),(0,0,0,1),(0,100,0,1)]:
  for scale in [0,1,30,-1]:
   g=AdjustGraph();g.plane(40,velocity=velocity);g.put(PREV,'<4f',*old)
   g.run([call(0x427b30,P,[POS,PREV,Q])]*2,f'escape/{velocity}/{old}/{scale}',{0x684fc8:bits(scale)})
g=AdjustGraph();g.run([call(0x427b30,P,[POS,PREV,Q])],'escape empty')
# Stack probes must leave external live references intact on every exit.
for kind in ['one top','both faces','nine shells']:
 for count in [1,3]:
  g=AdjustGraph();_,owner=g.plane(40)
  if kind=='both faces':g.plane(39,up=False,owner=owner)
  if kind=='nine shells':
   g.plane(39,up=False,owner=owner)
   for i in range(8):g.plane(300-i*20,owner=owner);g.plane(299-i*20,up=False,owner=owner)
  refs=[g.alloc(12) for _ in range(count)];g.put(owner+4,'<I',refs[0])
  for i,a in enumerate(refs):g.put(a,'<3I',owner,refs[i-1] if i else 0,refs[i+1] if i+1<count else 0)
  g.run([call(0x427700,P,[POS,OUT,Q])]*3,f'external references/{kind}/{count}')
  assert oracle.word(owner+4)==refs[0]
  for i,a in enumerate(refs):assert list(struct.unpack('<3I',oracle.cpu.mem_read(a,12)))==[owner,refs[i-1] if i else 0,refs[i+1] if i+1<count else 0]
for off in [0,1,4,8,12,32]:
 g=AdjustGraph();g.plane(40);g.run([call(0x427700,P,[POS,POS+off,Q])],f'containment aliased output/{off}')
for off in [0,4,8,12]:
 g=AdjustGraph();g.plane(40);g.put(POS,'<8f',0,0,0,1,0,0,0,1)
 g.run([call(0x427b30,P,[POS,POS+off,Q])],f'escape overlapping positions/{off}')
for velocity,scale in itertools.product([1e-30,1e20,1e30,-1e30],[1e-20,1,1e20]):
 g=AdjustGraph();g.plane(40,velocity=(velocity,-velocity,velocity,velocity));g.put(PREV,'<4f',0,0,0,1)
 g.run([call(0x427b30,P,[POS,PREV,Q])],f'escape wide exponent/{velocity}/{scale}',{0x684fc8:bits(scale)})
# Reporting and original skater-constructor cases are appended below.
shared_records=[]
for reversed_ in [False,True]:
 g=AdjustGraph();registry=[(0x9f9cc949,0x4f80e0),(0x43686585,0x519740),(0x5bd63b29,0x505440)];g.registry(registry)
 order=registry[::-1] if reversed_ else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reversed_}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 adjust=components[0x9f9cc949];assert oracle.word(adjust+0x20)==components[0x5bd63b29] and oracle.word(adjust+0x30)==components[0x43686585]
 desc=g.alloc(24);g.put(desc,'<6I',0xdeadbeef,0x9f9cc949,0,0,0,0)
 g.run(calls+[call(0x45d720,adjust,[desc,g.structure([]),0]),call(0x45d890,OBJ)],f'shared command/disposal/{reversed_}')
 shared_records.append({'reverse_order':reversed_,'components':{hex(k):v for k,v in components.items()}})
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Adjust/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0xe594f0a2 if local&255 else 0x850eef66)
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
 oracle.counts['thug_skater_construct_adjust_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Eight complete original routines recover SkaterAdjustPhysics factory/destruction/delete/finalization, standalone probe endpoint copies and427700/427b30 moving-geometry containment and escape. Real one-sided triangle, static/moving scene, intrusive reference and timing callees execute without substituted collision answers. Full arena/globals/heap and completed-call registers compare exactly; endpoint copies preserve arbitrary raw words and overlap. Successful allocation, initialized internal graphs and finite geometry are contracts. Shared builder creates Adjust/Physics/State in both orders, runs the existing return2 command and disposes them. Original582d90 now creates Adjust and stops before Trigger e594f0a2; remote850eef66 unchanged. Full Adjust frame/ground/light work explicitly traps and is not claimed recovered; Gap commands, skater assembly, cold boot, rendering and playability remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-adjust',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-adjust-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records;report['collision_records']=collision_records
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage','collision_records']}),flush=True)
