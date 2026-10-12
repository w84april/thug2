"""Original balance records and BalanceTrick lifecycle; checksum remains pending."""
from pathlib import Path
source=Path('local/analysis/probe-skater-walk.py').read_text().split('# Real original CRT')[0]
exec(compile(source,'<preserved isolated component oracle>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.counts.clear();oracle.cases.clear();oracle.coverage.clear()
specs=[(0x579950,80,'thug_balance_record_construct_draft',0,'word',True,True,True),
 (0x579850,7,'thug_balance_record_destroy_draft',0,'void',False,False,True),
 (0x5799a0,34,'thug_balance_record_delete_draft',1,'word',True,False,True),
 (0x579860,59,'thug_balance_record_bind_draft',1,'void',False,False,True),
 (0x4f8f80,143,'thug_balance_component_construct_draft',0,'word',True,True,True),
 (0x4f9170,89,'thug_balance_component_create_draft',0,'word',True,False,False),
 (0x4f8cf0,127,'thug_balance_component_destroy_draft',0,'void',False,False,True),
 (0x4f9010,33,'thug_balance_component_delete_draft',1,'word',True,False,True),
 (0x4f9040,61,'thug_balance_component_initialize_draft',1,'void',False,False,True),
 (0x4f9080,24,'thug_balance_component_bind_draft',0,'void',False,False,True)]
for row in specs:bind_new(*row)
for row in [(0x401cc0,'thug_allocate_zeroed',1,'word',True,False,False),
 (0x51b970,'thug_component_suspend_update_draft',0,'void',False,False),
 (0x45e510,'thug_composite_initialize_draft',0,'word',False,False),
 (0x45ee20,'thug_composite_add_parameters_draft',2,'void',True,True),
 (0x45db30,'thug_composite_finalize_draft',0,'void',True,True),
 (0x45d890,'thug_composite_destroy_draft',0,'void',True,True)]:bind(*row)
exports.extend([[0x64ed24,'thug_balance_record_methods_draft'],[0x64ba30,'thug_balance_component_pending_methods_draft']]);function_exports.append([0x4f9170,'thug_balance_component_create_draft'])
CBSTATE=BASE+0x224000;CBNATIVE=oracle.stop+0x500
assert CBSTATE==0x1a24000
def balance_native(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8);n=oracle.word(CBSTATE);assert n<32
 target=oracle.word(CBSTATE+12);oracle.setword(CBSTATE,n+1)
 cpu.mem_write(CBSTATE+128+n*32,struct.pack('<8I',params,oracle.word(script+0xb8),target,oracle.word(target),oracle.word(target+0x24),oracle.word(target+0x50),oracle.word(target+0x38),oracle.word(target+0x34)))
 if not oracle.word(CBSTATE+4) or not n:
  for i in range(oracle.word(CBSTATE+8)):oracle.setword(oracle.word(CBSTATE+16+i*8),oracle.word(CBSTATE+20+i*8))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,balance_native,begin=CBNATIVE,end=CBNATIVE)
oldcase=case
def case(calls,patches=(),changes=None,label='Balance lifecycle'):
 stages=oldcase(calls,patches,changes,label);previous=0
 for step in stages:
  for at,data in step['outputs']:
   if at<=CBSTATE and at+len(data)//2>=CBSTATE+4:
    n=int.from_bytes(bytes.fromhex(data)[CBSTATE-at:CBSTATE-at+4],'little');step['callbacks']+=n-previous;previous=n
 return stages
class BalanceGraph(WalkGraph):
 def __init__(self,toggle=0,target=P):
  super().__init__();self.image[CBSTATE-BASE:CBSTATE-BASE+0x500]=bytes(0x500)
  self.put(CBSTATE+12,'<I',target);self.symbol(0x5d07e2be,1,toggle)
  self.toggle_value=self.word(SYMBOLS+(0x5d07e2be&4095)*4)+12
  for i in range(32):fields.add(CBSTATE+128+i*32+12)
  self.cached(0x18f77ea1)
 def cached(self,name,code=b'\x01\x24'):
  program=self.alloc(len(code));self.image[program-BASE:program-BASE+len(code)]=code;self.symbol(name,7,program)
  if code.startswith(b'\x01\x43'):fields.add(program+2)
  slot=self.word(CACHETABLE+4)+(name&3)*12
  if self.word(slot+4) and self.word(slot)==name:
   self.put(self.word(slot+4)+4,'<I',program);return
  entry=self.alloc(20);self.put(entry,'<5I',name,program,1,0,0)
  if self.word(slot+4):node=self.alloc(12);self.put(node,'<3I',name,entry,self.word(slot+8));self.put(slot+8,'<I',node)
  else:self.put(slot,'<3I',name,entry,0)
  self.put(CACHETABLE+8,'<I',self.word(CACHETABLE+8)+1)
 def callback(self,writes=(),once=True):
  self.cached(0x18f77ea1,b'\x01\x43'+struct.pack('<I',CBNATIVE)+b'\x01\x24')
  self.put(CBSTATE,'<3I',0,int(once),len(writes))
  for i,(address,value) in enumerate(writes):self.put(CBSTATE+16+i*8,'<2I',address,value)
for fn,size in [(0x579950,0x58),(0x4f8f80,0x188)]:
 for fill,offset,toggle in itertools.product([0,0xa5,255],[0,1,4],[0,1,0xffffffff]):
  g=BalanceGraph(toggle,P+offset);g.image[P-BASE:P-BASE+size+16]=bytes([fill])*(size+16)
  fields.add(P+offset)
  if fn==0x4f8f80:fields.update(P+offset+0x24+i*0x58 for i in range(4))
  g.run([call(fn,P+offset)]*2+[call(0x579850 if fn==0x579950 else 0x4f8cf0,P+offset)],f'raw balance lifetime {fn:x}/{fill}/{offset}/{toggle:x}')
for flags,toggle in itertools.product([0,1,2,3,255,256,257,0xffffffff],[0,1]):
 g=BalanceGraph(toggle,HEAP+0x24);g.run([call(0x4f9170),call(0x4f9010,HEAP,[flags])],f'balance factory/delete {flags}/{toggle}')
 g=BalanceGraph(toggle,HEAP);g.run([call(0x401cc0,args=[0x58]),call(0x579950,HEAP),call(0x5799a0,HEAP,[flags])],f'record allocate/construct/delete {flags}/{toggle}')
g=BalanceGraph();g.put(CONTEXT+32,'<I',1);g.run([call(0x4f9170)]*2,'balance factory allocation failure')
for shape in ['empty','all','reverse','duplicate','missing balance','missing score','missing input','missing rail']:
 g=BalanceGraph();types=[0x589e5fb3,0xd262802f,0x27d7cd28,0x7149b753]
 if shape=='empty':types=[]
 if shape=='reverse':types.reverse()
 if shape=='duplicate':types*=2
 if shape.startswith('missing'):types.remove({'missing balance':0x589e5fb3,'missing score':0xd262802f,'missing input':0x27d7cd28,'missing rail':0x7149b753}[shape])
 nodes=[g.component(t) for t in types]
 for i,node in enumerate(nodes):g.put(node+16,'<I',nodes[i+1] if i+1<len(nodes) else 0)
 g.put(OBJ+0x100,'<I',nodes[0] if nodes else 0);g.put(P+12,'<I',OBJ)
 g.run([call(0x579860,P+0x7000,[OBJ]),call(0x4f9040,P,[0]),call(0x4f9080,P)]*2,f'balance dependencies {shape}')
for toggle,once in itertools.product([1,0xffffffff],[False,True]):
 for fn,target in [(0x579950,P),(0x4f8f80,P+0x24),(0x4f9170,HEAP+0x24)]:
  g=BalanceGraph(toggle,target)
  g.callback([(target+0x24,0x12345678),(target+0x50,7),(target+0x14,0xabcdef01),(g.toggle_value,0)],once)
  g.run([call(fn,0 if fn==0x4f9170 else P)],f'balance QB ordering {fn:x}/{toggle:x}/{once}')
  assert oracle.word(CBSTATE)==1 and oracle.word(target+0x24)==0 and oracle.word(target+0x50)==0xffffffff and oracle.word(target+0x14)==0xabcdef01,(hex(fn),toggle,once,[hex(oracle.word(x)) for x in [CBSTATE,target+0x24,target+0x50,target+0x14]])
for once in [False,True]:
 for fn,target in [(0x4f8f80,P+0x24),(0x4f9170,HEAP+0x24)]:
  g=BalanceGraph(1,target)
  parent=P if fn==0x4f8f80 else HEAP
  g.callback([(target+0x24,0x12345678),(target+0x50,7),(parent+0x20,0xdeadbeef),(parent+0x184,0xabcdef01)],once)
  g.run([call(fn,0 if fn==0x4f9170 else P)],f'four balance QB callbacks {fn:x}/{once}')
  assert oracle.word(CBSTATE)==4 and oracle.word(target+0x24)==(0 if once else 0x12345678) and oracle.word(target+0x50)==(0xffffffff if once else 7)
  assert oracle.word(parent+0x20)==0 and oracle.word(parent+0x184)==0
for reverse,toggle in itertools.product([False,True],[0,1]):
 g=BalanceGraph(toggle,HEAP+0x24);registry=[(0x589e5fb3,0x4f9170),(0x43686585,0x519740)];g.registry(registry)
 order=registry[::-1] if reverse else registry;params=[g.structure([(0xb6015ea8,13,t)]) for t,_ in order]
 calls=[call(0x45e510,OBJ)]+[call(0x45ee20,OBJ,[s,0]) for s in params]+[call(0x45db30,OBJ),call(0x45d890,OBJ)]
 g.run(calls,f'shared balance lifecycle {reverse}/{toggle}')
scope='Ten complete original routines recover balance record construction/destruction/delete/dependency binding and BalanceTrick constructor/factory/destruction/delete/initialization/final dependency. Conditional real QB executes before selected zero writes, including terminal test native callbacks that mutate fields and disable later constructor scripts. Raw unaligned writes, allocation failure, low-byte delete flags, missing/duplicate dependencies and shared lifecycle are compared through original instructions. Whole arena/globals/heap and preserved registers compare exactly. Shared suspend update51b970 is reused and earns no new count. Checksum4f9420, full skater startup, renderer and playable level remain unfinished.'
extra={**extra,'function_exports':function_exports,'memory_fixture':'skater-walk-memory.wasm','native_callbacks':[{'module':'balance-construction-callback.wasm','export':'fixture_balance_construct_native','original':CBNATIVE}]}
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(folder/'balance-construction-callback.c'),'-o',str(folder/'balance-construction-callback.wasm')],check=True)
finish('skater-balance-lifecycle',scope,{},extra)
(folder/'skater-balance-lifecycle-routines.json').write_text(json.dumps({hex(a):{'bytes':n,'instructions':len(coverage[a]),'name':name} for a,n,name,*_ in specs},indent=2)+'\n')
