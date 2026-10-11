"""Compare original skater registration and component creation up to Score."""
from pathlib import Path
source=Path('local/analysis/probe-input-lifecycle.py').read_text().split('for fill in [0,0xa5,255]:')[0]
exec(compile(source,'<preserved object/input oracle setup>','exec'))
from unicorn.x86_const import *
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
for args in [(0x401d80,24,'thug_skater_handle_construct_draft',0,'word',False,False,True),
 (0x57b250,148,'thug_skater_add_base_components_draft',1,'void',True,False,False),
 (0x462a90,115,'thug_object_registry_set_alias_draft',2,'void',True,False,True),
 (0x519740,117,'thug_skater_state_create_draft',0,'word',True,False,False),
 (0x519460,10,'thug_skater_state_initialize_draft',1,'void',False,False,True),
 (0x519450,11,'thug_skater_state_destroy_draft',0,'void',False,False,True),
 (0x519620,33,'thug_skater_state_delete_draft',1,'word',True,False,True),
 (0x51bd80,121,'thug_skater_attachment_create_draft',0,'word',True,False,False)]:bind_new(*args)
for a,name,argc,result,heap,diag in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True),
 (0x582d90,'thug_skater_construct_prefix_draft',6,'void',True,True)]:bind(a,name,argc,result,heap,diag)
glob('thug_skater_serial_draft',0x690fa0,0)
BOUNDARY,DIAG,DLOG=BASE+0xcd000,BASE+0xce000,BASE+0xce100
assert 0x390 not in index
glob('thug_skater_construction_boundary_draft',0x390,BOUNDARY) # Test-only mapped global.
put(DIAG,'<2I',DLOG,0)
for a,name in [(0x6465c8,'thug_suspend_methods_draft'),(0x645dc4,'thug_component_b87c8e43_methods_draft'),
 (0x64ef48,'thug_skater_pending_methods_draft'),(0x64e544,'thug_skater_node_pending_methods_draft'),
 (0x64c140,'thug_skater_state_methods_draft'),(0x64c250,'thug_skater_attachment_pending_methods_draft')]:
 if not any(row[0]==a for row in exports):exports.append([a,name])
function_exports.extend([[0x519740,'thug_skater_state_create_draft'],[0x51bd80,'thug_skater_attachment_create_draft']])
def call(a,this=0,args=()):return a,this,[v&0xffffffff for v in args]+([DIAG] if functions[hex(a)].get('diagnostics') else [])
def debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0];file=bytes(cpu.mem_read(oracle.word(sp+8),48)).split(b'\0')[0]
 assert fmt in [b'D:%s:%i: m_skater_number = %i\n',b'D:%s:%i: m_id = %i\n'] and file==b'jects\\skater.cpp'
 count=oracle.word(DLOG);oracle.setword(DLOG,count+1);row=bytearray(128);row[:len(fmt)]=fmt;row[64:64+len(file)]=file
 row[112:120]=cpu.mem_read(sp+12,8);cpu.mem_write(DLOG+16+128*count,bytes(row))
 if oracle.word(DLOG+4):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,debug,begin=0x401c30,end=0x401c30)
prefix_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:prefix_hits.update([at]),begin=0x582d90,end=0x5833f6)
def boundary(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);receiver=cpu.reg_read(UC_X86_REG_ECX)
 node=oracle.word(params+4)
 if oracle.word(node+8)!=0xd262802f:return
 assert oracle.word(sp+8)==0
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,receiver,1));cpu.emu_stop()
oracle.cpu.hook_add(UC_HOOK_CODE,boundary,begin=0x45ee20,end=0x45ee20)
initial=bytes(memory);oracle.initial=initial
class SkaterGraph(CompositeGraph):
 def __init__(self):
  super().__init__();self.symbol(0xad501995,2,bits(50));self.image[OBJ-BASE:OBJ-BASE+0x324]=bytes(0x324)
  self.image[BOUNDARY-BASE:BOUNDARY-BASE+16]=bytes(16);self.image[DLOG-BASE:DLOG-BASE+0x1000]=bytes(0x1000)
  self.put(SERVICES,'<2I',DIAG,ADAPTER)
 def run(self,calls,label,changes=None):return case(calls,self.patches(),changes,label)
for value in [0,1,0x7fffffff,0xfffffffe,0xffffffff]:
 for fill in [0,0xa5,255]:
  g=SkaterGraph();g.image[P-BASE:P-BASE+16]=bytes([fill])*16
  g.run([call(0x401d80,P)]*3,f'serial wrap/{value}/{fill}',{0x690fa0:value})
for flags in [0,1,2,255,256,257,0xffffffff]:
 g=SkaterGraph();g.run([call(0x519740),call(0x519460,HEAP,[0]),call(0x519620,HEAP,[flags])],f'State factory/init/delete/{flags}')
for fill in [0,0xa5,255]:
 g=SkaterGraph();g.image[P-BASE:P-BASE+0x128]=bytes([fill])*0x128;g.put(P+8,'<I',0)
 g.run([call(0x519460,P,[0])]*2+[call(0x519450,P)],f'State fields/{fill}')
for count in [1,2,4]:
 g=SkaterGraph();g.run([call(0x51bd80)]*count,f'attachment factory/{count}')
for existing in [False,True]:
 for registered in [False,True]:
  g=SkaterGraph();g.registry([(0xce0ca665,0),(0xb87c8e43,0)] if registered else [])
  calls=[call(0x45e510,OBJ)]
  if existing:
   c=g.component();g.put(OBJ+0x100,'<I',c);calls=[]
  calls += [call(0x57b250,args=[OBJ]),call(0x57b250,args=[OBJ]),call(0x45d890,OBJ)]
  g.run(calls,f'original two base components/{existing}/{registered}')
for shape in ['empty','same','other','collision','null head']:
 for oldcount,newcount in itertools.product([0,1,0x7fffffff,0x80000000,0xffffffff],[0,0xffffffff]):
  g=SkaterGraph();old=OBJ+0x400;name=0x12345678
  g.put(old+0x3c,'<I',oldcount);g.put(OBJ+0x3c,'<I',newcount)
  entries=[] if shape=='empty' else [(name,OBJ if shape=='same' else old)]
  if shape in ['collision','null head']:entries=[(name^4,old),(name,OBJ)]
  table=g.table(entries);g.put(EM+12,'<I',table)
  if shape=='null head':g.put(g.word(table+4)+(name&3)*12+4,'<I',0)
  g.run([call(0x462a90,EM,[name,OBJ])]*2,f'alias/{shape}/{oldcount}/{newcount}')
# The actual skater entry executes unchanged and halts before creating Score.
# Earlier component calls execute; no return value or game callee is fabricated.
prefix_records=[]
for heap_index,local,id_ in itertools.product([0,1,2,0xffffffff],[0,1,256,257],[0,0xffffffff]):
 g=SkaterGraph();g.registry([(0xce0ca665,0),(0xb87c8e43,0),(0x43686585,0x519740),(0xf27a294d,0x51bd80),(0x27d7cd28,0x41eec0)])
 mutate=bool(len(prefix_records)%2)
 if mutate:g.put(DLOG+4,'<2I',OBJ+0x14,0x77700000+len(prefix_records))
 stages=g.run([],f'skater constructor/{heap_index}/{local}/{id_}',{0x690fa0:0xfffffffe})
 before=bytes(oracle.cpu.mem_read(BASE,len(initial)));cpu=oracle.cpu;sp=oracle.stack+0x18000
 args=[17,MANAGER,local,id_,heap_index,0x12345678]
 cpu.mem_write(sp,struct.pack('<7I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,OBJ);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
 try:cpu.emu_start(0x582d90,oracle.stop,count=500000)
 except Exception:print('PREFIX FAILED',hex(cpu.reg_read(UC_X86_REG_EIP)),args,flush=True);raise
 assert cpu.reg_read(UC_X86_REG_EIP)==0x45ee20 and oracle.word(BOUNDARY+8)==OBJ
 assert oracle.word(DLOG)==2 and oracle.word(OBJ+0x15c)==0xfffffffe
 chain=[];c=oracle.word(OBJ+0x100)
 while c:chain.append((c,oracle.word(c+4)));c=oracle.word(c+16)
 assert [t for _,t in chain]==[0xce0ca665,0xb87c8e43,0x43686585,0xf27a294d]+([0x27d7cd28] if local&255 else [])
 assert oracle.word(chain[2][0]+0x18)==1
 assert oracle.word(OBJ+0x264)==(chain[4][0] if local&255 else 0)
 after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[];known={row[0] for row in exports}
 for page in range(0,len(initial),4096):
  if before[page:page+4096]!=after[page:page+4096]:
   for j in range(page,min(page+4096,len(initial)),4):
    if before[j:j+4]!=after[j:j+4]:
     outputs.append([BASE+j,after[j:j+4].hex()])
     if int.from_bytes(after[j:j+4],'little') in known:fields.add(BASE+j)
 stages.append({'fn':'0x582d90','this':OBJ,'args':args+[DIAG],'result':None,'outputs':outputs,'globals':[oracle.global_read(x) for x in globals_],'callbacks':0,'expected_trap':True})
 oracle.counts['thug_skater_construct_prefix_draft']+=1
 prefix_records.append({'arguments':args,'components':chain,'boundary':list(struct.unpack('<4I',cpu.mem_read(BOUNDARY,16))),'diagnostics_mutate_id':mutate})
scope='Eight original skater startup routines: serial handle, two base component construction, secondary aliases, State factory/init/destroy/delete and attachment factory. Original582d90 constructor executes registration and real Suspend, bounds, State, attachment and local Input component creation, then stops before45ee20 creates Score. No creation return or game callee is fabricated. Whole arena/globals/heap and completed-call registers compare. Debug output is a host argument boundary, including mutation between prints. Skater/node vtables are identity storage only. Attachment disposal/commands explicitly trap and are not exercised or claimed recovered. State command registration, remaining constructor, camera/rendering and playable training remain unfinished.'
extra={**extra,'direct_initializer_prefix':True,'boundary_address':BOUNDARY,'boundary_factory':0x45ee20,
 'native_callbacks':[{'module':'skater-construction-diagnostic-fixture.wasm','export':'fixture_skater_print','slots':[DIAG+4]}]}
saved_coverage=coverage.copy();coverage.clear();finish('skater-construction',scope,{},extra);coverage.update(saved_coverage)
report_path=folder/'skater-construction-original.json';report=json.loads(report_path.read_text())
report['instruction_coverage']={hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x182d90,1639),0x582d90))
report['partial_constructor']={'address':'0x582d90','covered':sum(bool(prefix_hits[i.address]) for i in code),'total':len(code),'boundary':'0x45ee20','interrupted_calls':len(prefix_records),'records':prefix_records}
report_path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
