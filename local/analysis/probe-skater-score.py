"""Compare original Score startup and continue the real skater constructor."""
from pathlib import Path
source=Path('local/analysis/probe-skater-construction.py').read_text().split('for value in [0,1,0x7fffffff,0xfffffffe,0xffffffff]:')[0]
old='if oracle.word(node+8)!=0xd262802f:return'
assert old in source
source=source.replace(old,'if oracle.word(node+8) not in [0xbf518e27,0x850eef66]:return')
exec(compile(source,'<preserved skater startup oracle, later explicit boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for args in [(0x4a0710,6,'thug_score_get_split_layout_draft',0,'word',False,False,False),
 (0x561290,12,'thug_score_set_player_draft',1,'void',False,False,True),
 (0x561470,70,'thug_score_array_construct_draft',2,'word',True,False,True),
 (0x561730,348,'thug_score_configure_balance_draft',0,'void',False,False,True),
 (0x563440,312,'thug_score_construct_draft',0,'word',True,True,True),
 (0x518b60,114,'thug_score_component_create_draft',0,'word',True,False,False),
 (0x518660,118,'thug_score_component_initialize_draft',1,'void',True,True,True)]:bind_new(*args)
bind(0x45e510,'thug_composite_initialize_draft',0,'word')
bind(0x582d90,'thug_skater_construct_score_prefix_draft',6,'void',True,True)
assert 0x70134c not in index
glob('thug_score_split_layout_draft',0x70134c,0)
exports.append([0x64c090,'thug_score_pending_methods_draft'])
function_exports.append([0x518b60,'thug_score_component_create_draft'])
initial=bytes(memory);oracle.initial=initial
class ScoreGraph(SkaterGraph):
 def __init__(self,count=3,fill=0,players=1,mode=0,network=False):
  super().__init__();self.image[P-BASE:P-BASE+0x1550]=bytes([fill])*0x1550
  self.put(SETTINGS+4,'<2I',0,self.word(self.structure([(0x6dc3d6f1,1,players),(0xa1dc81f9,13,mode)])+4))
  if network:
   connection=self.alloc(0x1e88);self.put(connection+0x1e84,'<I',0);self.put(NET,'<3I',4,connection,0)
  curves=[]
  for i in range(count):
   pair=self.alloc(12);self.put(pair,'<3I',0x11223300+i,bits(-2.25+i),bits(.125+i));curves.append(pair)
  self.curve=self.array(5,curves);fields_=[(0xf716442a,12,self.curve)];self.position_arrays=[]
  for j,key in enumerate([0xf314312a,0x44e39bb5,0xbeeca6d6]):
   values=[]
   for i in range(2):
    pair=self.alloc(12);self.put(pair,'<3I',0xaabbcc00+j*2+i,bits(j*10+i+.5),bits(-j*10-i));values.append(pair)
   array=self.array(5,values);self.position_arrays.append(array);fields_.append((key,12,array))
  self.symbol(0x91cb3c33,10,self.structure(fields_))
  self.symbol(0x1edc33f1,1,0);self.symbol(0x59b9a85e,2,bits(1.25));self.symbol(0xb33d71c0,1,0x81234567)
 def skater(self,kind):
  if kind=='absent':return []
  node=self.alloc(16);self.put(node,'<4I',0,OBJ,0,GAME+0x28);self.put(GAME+0x34,'<I',node)
  self.put(OBJ+0x14,'<I',0 if kind=='matching' else 7)
  return [call(0x45e510,OBJ)]
for value in [0,1,2,255,0x80000000,0xffffffff]:
 g=ScoreGraph();g.run([call(0x4a0710)]*2,f'split layout/{value}',{0x70134c:value})
for fill,value in itertools.product([0,0xa5,255],[0,1,0x7fff,0x8000,0xffff,0x10000,0x12345678,0xffffffff]):
 g=ScoreGraph(fill=fill);g.run([call(0x561290,P,[value])]*2,f'player lowword/{fill}/{value}')
for fill,capacity,growth in itertools.product([0,0xa5,255],[0,1,2,8,16],[0,1,8,0xffffffff]):
 g=ScoreGraph(fill=fill);g.run([call(0x561470,P,[capacity,growth])]*2,f'array/{fill}/{capacity}/{growth}')
scenarios=[(1,0,False,1),(2,0,False,0),(2,0,False,1),(2,0,False,0xffffffff),
 (2,0x9d65d0e7,False,1),(2,0xb239668f,False,1),(2,0,True,1),(0xffffffff,0,False,2)]
for count,fill,scenario in itertools.product([0,1,2,7,19],[0,0xa5],scenarios):
 players,mode,network,layout=scenario;g=ScoreGraph(count,fill,players,mode,network)
 g.run([call(0x561730,P)]*2,f'curve/{count}/{fill}/{scenario}',{0x70134c:layout})
for offset in [-8,-4,0,4,8]:
 g=ScoreGraph(1,0xa5);g.put(g.curve+8,'<I',P+0x94+offset)
 g.run([call(0x561730,P)],f'curve overlapping source/{offset}')
for fill,special,body in itertools.product([0,0xa5,255],[0,1,255],['absent','wrong','matching']):
 g=ScoreGraph(fill=fill);g.put(P+0x74,'<B',special)
 g.run(g.skater(body)+[call(0x563440,P)],f'constructor fields/event/{fill}/{special}/{body}')
for kind,value in [(1,0),(1,0x01000001),(1,0x7fffffff),(1,0xffffffff),(2,bits(-0.0)),(2,bits(.125)),(2,bits(-512.25))]:
 g=ScoreGraph();g.symbol(0x59b9a85e,kind,value);g.symbol(0x1edc33f1,1,value)
 g.run([call(0x563440,P)],f'constructor global number/{kind}/{value}')
for count in [1,2,4]:
 g=ScoreGraph();g.run([call(0x518b60)]*count,f'component factory/{count}')
for fill,existing,id_ in itertools.product([0,0xa5],[False,True],[0,1,0xffff,0x10000,0x12345678,0xffffffff]):
 g=ScoreGraph(fill=fill);component=g.alloc(0x1c);g.put(component+12,'<I',OBJ);g.put(component+0x18,'<I',P if existing else 0)
 g.put(OBJ+0x14,'<I',id_);g.run([call(0x518660,component,[0])]*2,f'component init/{fill}/{existing}/{id_}')

# Original582d90 continues through Score and records the next actual factory call.
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Score/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]
 component=chain[-1][0];score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0xbf518e27 if local&255 else 0x850eef66)
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_score_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Seven complete original Score startup routines: layout getter, player-ID setter, array/Score constructors, balance configuration and component factory/initializer. Actual582d90 skater construction continues through Score, stores its component and player ID, then stops before localbf518e27 or nonlocal850eef66 creation. Configuration graph is explicit test input, not an original asset loader. Whole arena/globals/heap and completed-call registers compare. Debug output uses the preserved argument boundary. Score disposal, frame and commands explicitly trap and are not claimed recovered. Full skater/camera/rendering and playability remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-score',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-score-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
