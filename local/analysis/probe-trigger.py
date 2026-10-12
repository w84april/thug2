"""Original Trigger lifecycle, event masks, movement callbacks and skater creation."""
from pathlib import Path
source=Path('local/analysis/probe-skater-adjust.py').read_text().split('# Exact lifecycle')[0]
source=source.replace('0xe594f0a2','0x9b373e58')
exec(compile(source,'<preserved Adjust oracle; next construction boundary>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
specs=[(0x434b90,87,'thug_trigger_create_draft',0,'word',True,False,False),
 (0x434900,11,'thug_trigger_destroy_draft',0,'void',False,False,True),
 (0x434910,33,'thug_trigger_delete_draft',1,'word',True,False,True),
 (0x434940,33,'thug_trigger_initialize_draft',1,'void',False,False,True),
 (0x434970,225,'thug_trigger_command_draft',3,'word',False,False,True),
 (0x434ce0,135,'thug_trigger_from_records_draft',2,'void',True,True,True),
 (0x434d70,22,'thug_trigger_probe_callback_draft',1,'void',False,False,False),
 (0x434d90,360,'thug_trigger_update_draft',0,'void',True,True,True)]
for row in specs:bind_new(*row)
for args in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x45d920,'thug_object_update_components',0,'void',True,True),
 (0x45d720,'thug_component_descriptor_base',3,'word',False,False),
 (0x582d90,'thug_skater_construct_trigger_prefix_draft',6,'void',True,True)]:bind(*args)
exports.append([0x646648,'thug_trigger_methods_draft']);function_exports.append([0x434b90,'thug_trigger_create_draft'])
for at in [0x434a60,0x434bf0,0x417760,0x4170f0,0x4172f0,0x476860,0x46cc30,0x476950,0x565bb0,0x461480,0x4750b0,0x474540,0x4637e0]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
RECORDS,EVENTS,CBSTATE,ALTOWNER=[BASE+x for x in [0x220000,0x221000,0x222000,0x223000]]
CBNATIVE=oracle.stop+0x400
# Explicit terminal QB observer; every event, lookup, spawn and script operation
# before this user-defined native callback runs the original game code.
def trigger_native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8);n=oracle.word(CBSTATE);assert n<32
 oracle.setword(CBSTATE,n+1);row=CBSTATE+128+n*48
 cpu.mem_write(row,struct.pack('<12I',params,oracle.word(script+0xb8),oracle.word(P+0x28),oracle.word(P+12),*[oracle.word(P+0x18+i*4) for i in range(4)],*[oracle.word(oracle.word(P+12)+0x4c+i*4) for i in range(4)]))
 if not oracle.word(CBSTATE+4) or not n:
  count=oracle.word(CBSTATE+8);assert count<=12
  for i in range(count):oracle.setword(oracle.word(CBSTATE+16+i*8),oracle.word(CBSTATE+20+i*8))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,trigger_native,begin=CBNATIVE,end=CBNATIVE)
oldcase=case

def case(calls,patches=(),changes=None,label='Trigger'):
 stages=oldcase(calls,patches,changes,label);previous=0
 for step in stages:
  for at,data in step['outputs']:
   if at<=CBSTATE and at+len(data)//2>=CBSTATE+4:
    n=int.from_bytes(bytes.fromhex(data)[CBSTATE-at:CBSTATE-at+4],'little');step['callbacks']+=n-previous;previous=n
 return stages

class TriggerGraph(AdjustGraph):
 def __init__(self):
  super().__init__();self.image[P-BASE:P-BASE+0x80]=bytes(0x80);self.put(P,'<6I',0x646648,0xe594f0a2,0,OBJ,0,0);fields.add(P)
  self.put(OBJ,'<I',0x647650);fields.add(OBJ);self.put(OBJ+0x14,'<I',0x100);self.put(OBJ+0x100,'<2I',P,0)
  self.put(P+0x18,'<4f',0,4,0,1);self.put(OBJ+0x4c,'<4f',0,-4,0,1)
  self.image[RECORDS-BASE:ALTOWNER-BASE+0x324]=bytes(ALTOWNER-RECORDS+0x324)
  self.put(EVENTS,'<3I',1,2,2);self.put(ALTOWNER,'<I',0x647650);fields.add(ALTOWNER);self.put(ALTOWNER+0x4c,'<4f',7,8,9,1)
  self.cached(5)
 def cached(self,name,code=b'\x01\x24'):
  program=self.alloc(len(code));self.image[program-BASE:program-BASE+len(code)]=code;self.symbol(name,7,program)
  if code.startswith(b'\x01\x43'):fields.add(program+2)
  entry=self.alloc(20);self.put(entry,'<5I',name,program,1,0,0);slot=self.word(CACHETABLE+4)+(name&3)*12
  if self.word(slot+4):node=self.alloc(12);self.put(node,'<3I',name,entry,self.word(slot+8));self.put(slot+8,'<I',node)
  else:self.put(slot,'<3I',name,entry,0)
  self.put(CACHETABLE+8,'<I',self.word(CACHETABLE+8)+1)
 def level_nodes(self,rows):
  nodes=[self.structure([(0xa1dc81f9,13,name),*items]) for name,items in rows];self.put(NODETABLE+0x10004,'<3I',0,0,self.array(10,nodes))
  for i,(name,_) in enumerate(rows):
   slot=name&0x3fff
   while self.word(NODETABLE+slot*4)>>16!=0xffff:slot=(slot+1)&0x3fff
   self.put(NODETABLE+slot*4,'<HH',0,i)
  return nodes
 def callback(self,writes=(),once=True):
  self.cached(6,b'\x01\x43'+struct.pack('<I',CBNATIVE)+b'\x01\x24');self.put(CBSTATE,'<3I',0,int(once),len(writes))
  for i,(address,value) in enumerate(writes):self.put(CBSTATE+16+i*8,'<2I',address,value)
 def trigger_plane(self,height=0,moving=False,flags=0x50,script=5):
  owner=None
  if moving:
   owner=self.alloc(0x120);self.image[owner-BASE:owner-BASE+0x120]=bytes(0x120);self.put(owner+0x14,'<I',0x55510000+len(self.actors))
  actor,owner=self.plane(height,moving=moving,flags=flags,owner=owner)
  return actor,owner,(self.word(actor+4),[(0x2ca8a299,13,script)]),((self.word(owner+0x14),[]) if owner else None)
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%40==0:print('Trigger cases',len(labels),flush=True)
  return result

for flags in [0,1,2,3,255,256,257,0xffffffff]:
 g=TriggerGraph();g.run([call(0x434b90),call(0x434910,HEAP,[flags])],f'factory/delete/{flags}')
for fill,offset in itertools.product([0,0xa5,255],[0,1,4]):
 g=TriggerGraph();g.image[P-BASE:P-BASE+0x80]=bytes([fill])*0x80;fields.add(P+offset)
 g.run([call(0x434900,P+offset)]*2,f'destroy writes/{fill}/{offset}')
for offset,raw in itertools.product([-0x34,-0x30,-0x2c,-0x28,0],[0,0x80000000,0x7fc12345,0x7f812345,0xffffffff]):
 g=TriggerGraph();owner=P+offset if offset else OBJ;g.put(owner+0x4c,'<4I',*[raw^i for i in range(4)]);g.put(P+12,'<I',owner)
 g.run([call(0x434940,P,[0])]*2,f'initialize overlap/raw/{offset}/{raw:x}')
# Required array forms, signed entries, duplicate addition and masked shifts.
commands=[]
for values,mask in itertools.product([[],[0],[1],[1,1],[1,2],[31],[32],[63],[0xffffffff],[0x80000000],[0x7fffffff],[0xffffffff,0,31,32]],[0,1,2,4,8,0x80000000,0xffffffff]):
 g=TriggerGraph();g.put(P+0x28,'<I',mask);params=g.structure([(0,12,g.array(1,values))]);g.run([call(0x434970,P,[0x3a717382,params,0])]*2,f'event mask/{values}/{mask:x}')
for groups in [[],[[]],[[1],[2]],[[1,2],[3]],[[1,1],[1]],[[31],[0xffffffff]]]:
 for mask in [0,2,4,6,8,0x80000000,0xffffffff]:
  g=TriggerGraph();g.put(P+0x28,'<I',mask);params=g.structure([(0,12,g.array(12,[g.array(1,v) for v in groups]))])
  descriptor=g.alloc(16);g.put(descriptor,'<4I',0x3a717382,0,0,0)
  g.run([call(0x45d720,P,[descriptor,params,0])],f'alternative event masks/{groups}/{mask:x}')
for kind,outer in itertools.product([0,2,3,10,13],[False,True]):
 g=TriggerGraph();a=g.array(kind,[]);params=g.structure([(0,12,g.array(12,[a]) if outer else a)])
 g.run([call(0x434970,P,[0x3a717382,params,0])],f'wrong event array type/{kind}/{outer}')
for value in [0,1,0x80000000,0xffffffff]:
 g=TriggerGraph();g.run([call(0x434970,P,[value,0,0])],f'unknown command/{value}')
# Position equality and teleport gate require no geometry answer substitutions.
for coordinate,raw,teleport in itertools.product(range(4),[0,0x80000000,0x3f800000,0x7f800000,0x7fc12345,0x7f812345],[0,8]):
 g=TriggerGraph();g.put(P+0x18,'<4I',0,0,0,0);g.put(OBJ+0x4c,'<4I',0,0,0,0);g.put(OBJ+0x4c+4*coordinate,'<I',raw);g.put(OBJ+0x104,'<I',teleport)
 g.run([call(0x434d90,P,[Q])]*2,f'frame equality/gate/{coordinate}/{raw:x}/{teleport}')
for moving,flags in itertools.product([False,True],[0,0x10,0x40,0x50,0x51,0xffff]):
 g=TriggerGraph();actor,owner,node,onode=g.trigger_plane(moving=moving,flags=flags);g.level_nodes([node]+([onode] if onode else []))
 g.run([call(0x434d90,P,[Q])]*2,f'frame real geometry/{moving}/{flags}')
# Native QB callbacks mutate the owner and saved/live position during collision.
frame_records=[]
for moving,mutation,dispatch in itertools.product([False,True],['observe','position','owner','saved position'],[False,True]):
 g=TriggerGraph();actor,owner,node,onode=g.trigger_plane(moving=moving,script=6);g.level_nodes([node]+([onode] if onode else []))
 writes=[] if mutation=='observe' else [(OBJ+0x50,bits(23))] if mutation=='position' else [(P+12,ALTOWNER)] if mutation=='owner' else [(P+0x18,bits(99))]
 g.callback(writes);fn=0x45d920 if dispatch else 0x434d90;g.run([call(fn,OBJ if dispatch else P,[Q])]*2,f'frame QB mutation/{moving}/{mutation}/{dispatch}')
 assert oracle.word(CBSTATE)>0,(moving,mutation,dispatch)
 frame_records.append({'moving':moving,'mutation':mutation,'owner_dispatch':dispatch,'callbacks':oracle.word(CBSTATE),'saved_position':[oracle.word(P+0x18+i*4) for i in range(4)]})
# Reverse collision-record traversal uses later names for deduplication, even
# if their active flag is clear. Index zero is deliberately outside this loop.
for names,active in [([],[]),([1],[1]),([1],[0]),([1,2,3],[1,1,1]),([1,2,1],[1,1,1]),([1,2,1],[1,1,0]),([1,1,1],[1,1,1]),([1,2,3],[0,1,0])]:
 for mutation in [False,True]:
  g=TriggerGraph();g.level_nodes([(n,[(0x2ca8a299,13,6)]) for n in sorted(set(names))]);g.put(RECORDS+0xc30,'<I',len(names))
  for i,(name,flag) in enumerate(zip(names,active),1):g.put(RECORDS+0x28+i*0x60,'<IB',name,flag)
  g.callback([(RECORDS+0xc30,1)] if mutation else [])
  g.run([call(0x434ce0,P,[EVENTS,RECORDS])],f'collision records/{names}/{active}/{mutation}')
# Concrete factory through the shared builder, full frame and destruction.
shared_records=[]
for flags in [0]:
 g=TriggerGraph();g.registry([(0xe594f0a2,0x434b90)]);desc=g.structure([(0xb6015ea8,13,0xe594f0a2)])
 calls=[call(0x45e510,OBJ),call(0x45ee20,OBJ,[desc,0]),call(0x45db30,OBJ),call(0x45d920,OBJ,[Q]),call(0x45d890,OBJ)]
 g.run(calls,f'shared Trigger lifetime/{flags}')
 shared_records.append({'flags':flags,'calls':len(calls)})

prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=ScoreGraph();g.symbol(0x78f80ec4,2,bits(.125));g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0),(0xd262802f,0x518b60),(0xbf518e27,0x514430),(0x270f56e1,0x523490),(0xd9151d4d,0x517830),(0x5bd63b29,0x505440),(0x52d61a0d,0x517d40),(0x11b4c67f,0x512c60),(0x9f9cc949,0x4f80e0),(0xe594f0a2,0x434b90)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater through Trigger/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])+[0xd262802f]+([0xbf518e27,0x270f56e1,0xd9151d4d,0x5bd63b29,0x52d61a0d,0x11b4c67f,0x9f9cc949,0xe594f0a2] if local&255 else [])
 component=next(c for c,t in chain if t==0xd262802f);score=oracle.word(component+0x18);player=int.from_bytes(cpu.mem_read(score+8,2),'little')
 assert oracle.word(OBJ+0x278)==component and player==(oracle.word(OBJ+0x14)&65535)
 params=oracle.word(BOUNDARY+4);next_type=oracle.word(oracle.word(params+4)+8)
 assert next_type==(0x9b373e58 if local&255 else 0x850eef66)
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
 oracle.counts['thug_skater_construct_trigger_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),
  'next_type':hex(next_type),'score':{'component':component,'state':score,'player_id':player},'diagnostics_mutate_id':mutate})

scope='Eight complete original routines recover Trigger creation, initialization, disposal, event-mask command, collision-record dispatch, probe callback and full movement frame. Real static/moving geometry, node lookup, script spawning and QB run before explicit terminal test callbacks. Duplicate masks add rather than OR; list scans and owner/position reads preserve callback ordering. Shared construction and real owner frame dispatch execute. Skater constructor continues through Trigger, then stops before9b373e58; remote850eef66 unchanged. Whole arena/globals/heap and completed-call registers compare, without numeric masks. Initialized graphs, required command arrays and successful allocations are original internal contracts. Remaining skater startup/frames, camera/rendering and original playable training remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]},
 {'module':'trigger-callback.wasm','export':'fixture_trigger_native','original':CBNATIVE}]}
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(folder/'trigger-callback.c'),'-o',str(folder/'trigger-callback.wasm')],check=True)
saved=coverage.copy();coverage.clear();finish('trigger',scope,{},extra);coverage.update(saved)
p=folder/'trigger-original.json';report=json.loads(p.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report['shared_startup_records']=shared_records;report['frame_records']=frame_records
p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
