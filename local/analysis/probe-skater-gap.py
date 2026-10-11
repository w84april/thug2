"""Original SkaterGap startup, state masks, cancellation and extended constructor."""
from pathlib import Path
source=Path('local/analysis/probe-skater-rotate.py').read_text().split('# Math helpers:')[0]
old="source=source.replace(old,\"source=source.replace(old,'if oracle.word(node+8) not in [0x11b4c67f,0x850eef66]:return')\")"
assert old in source
source=source.replace(old,old.replace('0x11b4c67f','0x9f9cc949'))
exec(compile(source,'<preserved Rotate oracle; later skater boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x512240,33,'thug_gap_primary_sentinel_delete_draft',1,'word',True,False,True),
 (0x512270,33,'thug_gap_secondary_sentinel_delete_draft',1,'word',True,False,True),
 (0x5122a0,79,'thug_skater_gap_construct_draft',0,'word',False,False,True),
 (0x512c60,86,'thug_skater_gap_create_draft',0,'word',True,False,False),
 (0x511bb0,10,'thug_skater_gap_initialize_draft',1,'void',False,False,True),
 (0x511bc0,69,'thug_skater_gap_finalize_draft',0,'void',False,False,True),
 (0x511f10,80,'thug_skater_gap_destroy_draft',0,'void',False,False,True),
 (0x5122f0,33,'thug_skater_gap_delete_draft',1,'word',True,False,True),
 (0x511c80,412,'thug_skater_gap_state_masks_draft',2,'void',False,False,True),
 (0x512320,52,'thug_skater_gap_update_draft',0,'void',True,False,True),
 (0x5121a0,148,'thug_skater_gap_clear_secondary_draft',1,'void',True,False,True)]
for row in specs:bind_new(*row)
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x511f60,'thug_tricks_cancel',2,'void',True,False),
 (0x582d90,'thug_skater_construct_gap_prefix_draft',6,'void',True,True)]:bind(*args)
exports += [[0x64be90,'thug_skater_gap_pending_methods_draft'],[0x64bec4,'thug_gap_primary_sentinel_methods_draft'],
 [0x64bec8,'thug_gap_secondary_sentinel_methods_draft'],[0x64be88,'thug_trick_primary_methods'],[0x64be8c,'thug_trick_secondary_methods']]
function_exports.append([0x512c60,'thug_skater_gap_create_draft'])
initial=bytes(memory);oracle.initial=initial
PH=P+0x2000;BAL=P+0x4000;CTRL=P+0x4400;STATE=P+0x4800;WALK=P+0x5000;VEH=P+0x5200;VO=P+0x5400;OUT=P+0x5600
LINKS=[0x5bd63b29,0x589e5fb3,0xd9151d4d,0x726e85aa]
class GapGraph(ScoreGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x58]=bytes(0x58);self.put(P,'<6I',0x64be90,0x11b4c67f,0,OBJ,0,0);fields.add(P)
  for at,n in [(PH,0x1540),(BAL,0x28),(CTRL,0x30),(STATE,0x128),(WALK,0x20),(VEH,0x120),(VO,0x108)]:self.image[at-BASE:at-BASE+n]=bytes(n)
  self.put(P+0x48,'<4I',PH,BAL,CTRL,WALK);self.put(PH+0x1528,'<I',STATE);self.put(CTRL+0x2c,'<I',STATE)
  self.put(VO+0x100,'<I',VEH);self.put(VEH+4,'<I',0xe47f1b79);self.put(EM+8,'<2I',self.table([(0x824c6a24,VO)]),self.table([]))
  self.ring([]);self.ring([],True)
 def ring(self,values,secondary=False):
  sentinel=P+(0x2c if secondary else 0x18);nodes=[self.alloc(0x40) for _ in values];chain=[sentinel,*nodes]
  table=0x64be8c if secondary else 0x64be88
  self.put(sentinel,'<5I',0x64bec8 if secondary else 0x64bec4,0xffffffff,0,nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel);fields.add(sentinel)
  for i,(node,value) in enumerate(zip(nodes,values)):
   self.put(node,'<11IB3xI',table,i,0xabcdef00+i,chain[(i+2)%len(chain)],chain[i],*value)
   fields.add(node)
  return nodes
 def mode(self,kind,state=0,rail=0,balance=0,balance_byte=0,vehicle=0):
  self.put(STATE+0x118,'<B',255 if kind=='vehicle' else 0);self.put(STATE+0x1c,'<I',1 if kind=='walk' else 0)
  self.put(STATE+0x18,'<I',state);self.put(STATE+0x90,'<B',rail);self.put(BAL+0x18,'<IB',balance,balance_byte)
  self.put(WALK+0x18,'<I',state);self.put(VEH+0x114,'<I',vehicle)
 def run(self,calls,label,changes=None):
  try:result=super().run(calls,label,changes)
  except Exception:print('FAILED',label,flush=True);raise
  if len(labels)%40==0:print('Gap cases',len(labels),flush=True)
  return result
# Selective constructor/initializer writes, including unaligned storage.
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=GapGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80
 fields.update([P+offset,P+offset+0x18,P+offset+0x2c])
 g.run([call(0x5122a0,P+offset)]*2+[call(0x511bb0,P+offset,[0])]*2+[call(0x511f10,P+offset)],f'construct/initialize/destroy/{fill}/{offset}')
for fill,flags in itertools.product([0,0xa5,255],[0,2,3,0xffffffff]):
 g=GapGraph();g.image[P-BASE:P-BASE+0x58]=bytes([fill])*0x58;g.put(P+8,'<I',flags)
 g.run([call(0x511bb0,P,[0])]*2,f'initialize untouched fields/{fill}/{flags}')
for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=GapGraph();g.run([call(0x512c60),call(0x5122f0,HEAP,[flags])],f'factory/delete/{flags}')
for shape in ['empty','all','reversed','duplicates']+[f'missing{i}' for i in range(4)]:
 g=GapGraph();types=[] if shape=='empty' else LINKS[::-1] if shape=='reversed' else LINKS*2 if shape=='duplicates' else [t for i,t in enumerate(LINKS) if shape!=f'missing{i}']
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.run([call(0x511bc0,P)]*2,'dependency lookup/'+shape)
 assert [oracle.word(P+0x48+4*i) for i in range(4)]==[nodes[types.index(t)] if t in types else 0 for t in LINKS]
# Real node destructors preserve unlink ordering; component destruction detaches
# sentinels and leaves nodes allocated, as the original does.
sample=(7,1,9,7,9,12,0,0)
for primary,secondary,flags in itertools.product([0,1,3],[0,1,3],[0,1,256,257]):
 g=GapGraph();g.ring([sample]*primary);g.ring([sample]*secondary,True);g.put(P+8,'<I',2)
 g.run([call(0x5122f0,P,[flags])],f'detach embedded sentinels/{primary}/{secondary}/{flags}')
for secondary,length,flags in itertools.product([False,True],[0,1,3],[0,1,2,255,256,257,0xffffffff]):
 g=GapGraph();nodes=g.ring([sample]*length,secondary);node=nodes[length//2] if length else P+(0x2c if secondary else 0x18)
 g.run([call(0x512270 if secondary else 0x512240,node,[flags])],f'sentinel wrapper/{secondary}/{length}/{flags}')
# All state paths plus output aliasing and valid input-field overlaps.
modes=[('skate',state,0,0,0,0) for state in [0,1,2,3,4,5,6,0xffffffff]]
modes += [('skate',0,rail,bal,flag,0) for rail,bal,flag in itertools.product([0,1,255],[0,1,0xffffffff],[0,1,255])]
modes += [('walk',state,0,0,0,0) for state in [0,1,2,3,4,0xffffffff]]
modes += [('vehicle',0,0,0,0,value) for value in [0,1,0x80000000,0xffffffff]]
for args in modes:
 for output in ['separate','same']:
  g=GapGraph();g.mode(*args);g.run([call(0x511c80,P,[OUT,OUT if output=='same' else OUT+4])]*2,f'state masks/{args}/{output}')
for args in [('skate',0,0,0,0,0),('walk',3,0,0,0,0),('vehicle',0,0,0,0,1)]:
 for select,clear in [(STATE+0x18,OUT),(STATE+0x1c,OUT),(STATE+0x118,OUT),(OUT,STATE+0x18),(BAL+0x18,OUT),(OUT,BAL+0x18),(OUT,VEH+0x114),(P+0x40,P+0x44),(OUT+1,OUT+3)]:
  g=GapGraph();g.mode(*args);g.run([call(0x511c80,P,[select,clear])]*2,f'mask input/output aliases/{args}/{select:x}/{clear:x}')
# Frame cancellation uses actual original node virtual destructors and heap logs.
frame_records=[]
for i,args in enumerate(modes):
 g=GapGraph();g.mode(*args);primary=[(7,flag,9,0,0,12 if j%2 else 0,0,0) for j,flag in enumerate([0,1,2,4,8,16,32,64,128,256,0x200,0x400,0x800,0x1234ffff,0xffffffff])]
 secondary=[(0,0,0,7,9,12,disabled,0) for disabled in [1,0,0]]
 g.ring(primary);g.ring(secondary,True);g.put(P+0x40,'<I',0xffffffff if i%2 else 123)
 g.run([call(0x512320,P)]*3,f'frame cancellation/{args}')
 frame_records.append({'state':args,'counter':oracle.word(P+0x40),'primary_head':oracle.word(P+0x24),'secondary_head':oracle.word(P+0x38)})
for kind in ['skate','walk','vehicle']:
 g=GapGraph();g.mode(kind);g.run([call(0x512320,P)]*2,'empty lists/'+kind)
# Clear all secondary entries, or retain only entries from the current frame.
for mode,timestamp in itertools.product(['absent','present','included','wrong named'],[0,1,0xffffffff]):
 for times in [[],[timestamp],[(timestamp+1)&0xffffffff],[timestamp,0,1,0xffffffff,timestamp]]:
  g=GapGraph();g.put(P+0x40,'<I',timestamp);g.ring([(0,0,0,7,9,12,j%2,t) for j,t in enumerate(times)],True)
  params=g.structure([] if mode=='absent' else [(0x97975226 if mode=='wrong named' else 0,13,0x97975226)])
  if mode=='included':g.symbol(0x75553331,10,params);params=g.structure([(0,13,0x75553331)])
  g.run([call(0x5121a0,P,[params])]*2,f'clear secondary/{mode}/{timestamp}/{times}')
# The existing shared builder creates and finalizes the real dependencies in
# either order. Balance/Walk are absent here; no frame uses absent dependencies.
shared_records=[]
registry=[(0x11b4c67f,0x512c60),(0x43686585,0x519740),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440)]
for reverse in [False,True]:
 g=GapGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry(registry)
 order=registry[::-1] if reverse else registry;descriptors=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in descriptors]+[call(0x45db30,OBJ)]
 g.run(calls,f'shared startup/{reverse}');components={};node=oracle.word(OBJ+0x100)
 while node:components[oracle.word(node+4)]=node;node=oracle.word(node+16)
 gap=components[0x11b4c67f];assert oracle.word(gap+0x48)==components[0x5bd63b29] and oracle.word(gap+0x50)==components[0xd9151d4d]
 assert oracle.word(gap+0x4c)==oracle.word(gap+0x54)==0
 g.run(calls+[call(0x45d890,OBJ)],f'shared startup/disposal/{reverse}')
 shared_records.append({'reverse_order':reverse,'components':{hex(k):v for k,v in components.items()}})

prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Gap/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x9f9cc949 if local&255 else 0x850eef66)
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
 oracle.counts['thug_skater_construct_gap_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})
scope='Eleven complete original routines recover SkaterGap constructor/factory, initialization, four dependency links, destruction/delete, both embedded-sentinel delete wrappers, state-derived cancellation masks, full per-frame cancellation and secondary-list cleanup. State cases cover skating, walking and vehicle paths, exact output alias writes, real object lookup, frame-counter wrap, real node virtual destructors and heap effects. Shared builder creates Gap, State, PhysicsControl and Physics in both orders, finalizes and destroys them. Original582d90 now creates Gap, stores owner270 and stops before9f9cc949 SkaterAdjustPhysics; nonlocal850eef66 is unchanged. Whole arena/globals/heap and completed-call registers compare without NaN or bit masks. Successful allocation, valid internal graphs and valid circular lists are original contracts. Gap start/end scoring, script commands, full skater assembly, cold boot, rendering and playable training remain unfinished; the unknown command slot explicitly traps.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-gap',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-gap-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records
report['frame_records']=frame_records
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
