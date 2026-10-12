"""Original remaining component startup; no fake game callee or parent credit."""
from pathlib import Path
from unicorn import Uc
# Replace only the inherited external printf boundary using public hook handles.
hook_add=Uc.hook_add;captured=[]
def capture(self,kind,callback,*args,**kwargs):
 handle=hook_add(self,kind,callback,*args,**kwargs)
 begin=kwargs.get('begin',args[1] if len(args)>1 else 1)
 if (getattr(callback,'__name__',''),begin) in [('debug',0x401c30),('boundary',0x45ee20)]:captured.append((self,handle))
 return handle
Uc.hook_add=capture
try:
 source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
 exec(compile(source,'<preserved isolated component oracle>','exec'))
finally:Uc.hook_add=hook_add
assert len(captured)==2,captured
for cpu,handle in captured:cpu.hook_del(handle)
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear();prefix_hits.clear()
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ESP,UC_X86_REG_EIP
def startup_debug(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);fmt=bytes(cpu.mem_read(oracle.word(sp+4),64)).split(b'\0')[0];skater=fmt.startswith(b'D:')
 assert skater or fmt==b'STATSManager: difficulty ====================== %i\n'
 n=oracle.word(DLOG);assert n<30;oracle.setword(DLOG,n+1);row=bytearray(128);row[:len(fmt)]=fmt
 if skater:
  file=bytes(cpu.mem_read(oracle.word(sp+8),48)).split(b'\0')[0];assert file==b'jects\\skater.cpp';row[64:64+len(file)]=file;row[112:120]=cpu.mem_read(sp+12,8)
 else:row[112:116]=cpu.mem_read(sp+8,4)
 cpu.mem_write(DLOG+16+128*n,bytes(row));mode=oracle.word(DLOG+12)
 if oracle.word(DLOG+4) and (not mode or mode==(2 if skater else 1)):oracle.setword(oracle.word(DLOG+4),oracle.word(DLOG+8))
 cpu.reg_write(UC_X86_REG_EAX,0xffffffff);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,startup_debug,begin=0x401c30,end=0x401c30)
discovery=json.loads((folder/'skater-final-components-discovery.json').read_text());components=[c for c in discovery['components'] if c['type'] not in ['0x5b512edc','0xd1515392']]
names={0x850eef66:'nonlocal_net',0x18223fd6:'state_history',0x4ff8dac6:'stats_manager'}
specs=[]
for c in components:
 t=int(c['type'],16);name=names.get(t,'component_'+f'{t:08x}');c['name']=name
 specs.append((int(c['factory'],16),c['factory_body_bytes'],'thug_'+name+'_create_draft',0,'word',True,False,False))
 if c['constructor']:
  spans=discovery['functions'][c['constructor']]['ranges'].split(';');end=max(int(span.split(':')[1],16) for span in spans)
  specs.append((int(c['constructor'],16),end-int(c['constructor'],16)+1,'thug_'+name+'_construct_draft',0,'word',False,False,True))
 exports.append([int(c['vtable'],16),'thug_'+name+'_startup_methods_draft']);function_exports.append([int(c['factory'],16),'thug_'+name+'_create_draft'])
specs += [(0x511780,98,'thug_component_125044e2_initialize_draft',1,'void',False,False,True),
 (0x4fbda0,10,'thug_component_8bce7e66_initialize_draft',1,'void',False,False,True),
 (0x51ae60,21,'thug_component_1859f772_initialize_draft',1,'void',False,False,True),
 (0x51c670,734,'thug_stats_manager_initialize_draft',1,'void',False,True,True)]
for row in specs:bind_new(*row)
for row in [(0x45e510,'thug_composite_initialize_draft',0,'word',False,False),(0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True)]:bind(*row)
ORIENT=BASE+0x226000;global_default('thug_skater_orientation_context',0x7ce5d8,ORIENT)
oracle.globals=globals_;oracle.defaults=defaults
exports.extend([[0x64c2c8,'thug_stats_manager_difficulty_format_draft'],[0x6469b4,'thug_stats_manager_empty_text_draft']])
oldcase=case
def case(calls,patches=(),changes=None,label='startup tail'):
 stages=oldcase(calls,patches,changes,label);previous=0
 for s in stages:
  n=previous
  for at,data in s['outputs']:
   if at<=DLOG and at+len(data)//2>=DLOG+4:n=int.from_bytes(bytes.fromhex(data)[DLOG-at:DLOG-at+4],'little')
  s['callbacks']+=n-previous;previous=n
 return stages
class TailGraph(ScoreGraph):
 def __init__(self,fill=0,difficulty=1,toggle=0,lookup='empty'):
  super().__init__();self.image[P-BASE:P-BASE+0x1800]=bytes([fill])*0x1800;self.put(P+12,'<I',OBJ)
  self.put(OBJ+0x14,'<I',42);self.put(ORIENT+0x40,'<I',0)
  diff=self.alloc(0x39c);self.put(GAME+0x38c,'<I',diff);self.put(diff+0x398,'<I',self.structure([] if difficulty is None else [(0x4da4937b,1,difficulty)]))
  self.symbol(0xb8688a8a,1,toggle);self.records([])
  if lookup!='empty':
   target=OBJ if lookup in ['owner','secondary'] else self.alloc(0x110)
   state=self.component(0x43686585);trick=self.component(0xd9151d4d);self.put(state+16,'<I',trick)
   self.put(target+0x100,'<I',0 if lookup=='missing components' else state)
   table=self.table([(42,target)]);self.put(EM+8,'<2I',self.table([]) if lookup=='secondary' else table,table if lookup=='secondary' else self.table([]))
 def records(self,records,signed_count=None):
  a=self.array(10,records)
  if signed_count is not None:self.put(a+4,'<I',signed_count&0xffffffff)
  self.symbol(0x4e46cc28,12,a)
 def stats_record(self,keys):
  entries=[]
  for i,key in enumerate(keys):
   if key in [0x0ffd7bbe,0xc2455018]:value=0x12340000+i;kind=13
   elif key==0xc4745838:value=self.text('retained stats label');kind=3
   elif key==0xbd982fdc:value=0xabcdef12;kind=1
   elif key==0xcd021293:value=self.array(3,[self.text('easy'),self.text('normal'),self.text('hard')]);kind=12
   else:value=self.array(10,[self.structure([(0x11220000+j,1,i*10+j)]) for j in range(3)]);kind=12
   entries.append((key,kind,value))
  return self.structure(entries)
 def run(self,calls,label,changes=None):
  result=super().run(calls,label,changes)
  if len(labels)%25==0:print('Tail cases',len(labels),flush=True)
  return result
# Complete-function behavioral cases.
for c in components:
 if c['constructor']:
  for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
   g=TailGraph(fill);fields.add(P+alignment);g.run([call(int(c['constructor'],16),P+alignment)]*2,f"raw {c['type']}/{fill}/{alignment}")
 for count in [1,2,4]:
  g=TailGraph();g.run([call(int(c['factory'],16))]*count,f"factory {c['type']}/{count}")
 g=TailGraph();g.put(CONTEXT+32,'<I',1);g.run([call(int(c['factory'],16))]*2,f"factory failure {c['type']}")
for fill,id in itertools.product([0,0xa5,255],list(range(9))+[255,0x80000000,0xffffffff]):
 g=TailGraph(fill);g.put(OBJ+0x14,'<I',id);g.run([call(0x511780,P,[0xffffffff])]*2,f'ID lookup {fill}/{id:x}')
for fill,alignment in itertools.product([0,0xa5,255],[0,1,4]):
 g=TailGraph(fill);g.run([call(0x4fbda0,P+alignment,[0xffffffff])]*2,f'word18 init {fill}/{alignment}')
for fill,id in itertools.product([0,0xa5,255],[0,0xd443a2bc,0xffffffff]):
 g=TailGraph(fill);g.put(ORIENT+0x40,'<I',id);g.run([call(0x51ae60,P,[0xffffffff])]*2,f'orientation context init {fill}/{id:x}')
keys=[0x0ffd7bbe,0xc2455018,0xe288a7cb,0xcd021293,0xc4745838,0xbd982fdc,0xd8a9d3ca,0x3c2fb496]
for fill,toggle,difficulty,lookup in itertools.product([0,0xa5],[0,1,2,0xffffffff],[None,0,1,2,3,0xffffffff],['empty','owner','secondary','missing components']):
 g=TailGraph(fill,difficulty,toggle,lookup);g.run([call(0x51c670,P,[0xffffffff])]*2,f'stats defaults {fill}/{toggle:x}/{difficulty}/{lookup}')
for profile,difficulty in itertools.product([[],keys,*[[k] for k in keys]],[0,1,2]):
 g=TailGraph(0xa5,difficulty);g.records([g.stats_record(profile)]);g.run([call(0x51c670,P,[0])]*2,f'stats optional {profile}/{difficulty}')
for count in [2,5,70]:
 g=TailGraph(0xa5,2);g.records([g.stats_record(keys if i%2 else []) for i in range(count)]);g.run([call(0x51c670,P,[0])],f'stats records {count}')
for count in [0,-1,-2147483648]:
 g=TailGraph(0xa5);g.records([],count);g.run([call(0x51c670,P,[0])],f'stats signed count {count}')
for target,value in [(P+0xa18,0),(P+0xa18,2),(P+0x9f4,0xaabbccdd),(P+0x24,0xdeadbeef)]:
 g=TailGraph(0xa5,1,2,'owner');g.records([g.stats_record(keys)]);g.put(DLOG+4,'<3I',target,value,1)
 g.run([call(0x51c670,P,[0])],f'stats callback writes {target:x}/{value:x}')
for c in components:
 g=TailGraph(0,2,1);g.registry([(int(c['type'],16),int(c['factory'],16))]);s=g.structure([(0xb6015ea8,13,int(c['type'],16))])
 g.run([call(0x45e510,OBJ),call(0x45ee20,OBJ,[s,0])],f"shared builder {c['type']}")
scope='Seventeen complete startup routines for nine concrete skater component types. Original required QB contracts, allocation failure, raw/unaligned fields, all eight ID cases, retained toggle byte, signed array length and native diagnostic mutation compare exactly. Shared callees reused, no additional recovery credit. Component frame/finalization/disposal/commands and full skater constructor remain incomplete. Ghidra511780 body union21bytes is conservatively distinguished from98bytes of executed inline ID cases.'
extra={**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm','callback_counter':'startup_diagnostic_callbacks','native_callbacks':[{'module':'skater-startup-tail-diagnostic-fixture.wasm','export':'fixture_startup_print','slots':[DIAG+4]}]}
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(folder/'skater-startup-tail-diagnostic-fixture.c'),'-o',str(folder/'skater-startup-tail-diagnostic-fixture.wasm')],check=True)
finish('skater-startup-tail',scope,{'0x51accd':'Three-byte alignment self-LEA ecx,[ecx] skipped by the unconditional original jump51accb to51acd0; no behavioral branch omitted.'},extra)
(folder/'skater-startup-tail-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
