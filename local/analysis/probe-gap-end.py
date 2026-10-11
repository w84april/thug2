"""Compare original EndGap with real score, history, QB and event dependencies."""
from pathlib import Path
exec(compile(Path('local/analysis/gap-end-score-setup.py').read_text(),'<preserved score insertion setup>','exec'))
import zlib
coverage.clear();hits.clear();oracle.end_labels=set()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:oracle.end_labels.add(oracle.word(cpu.reg_read(UC_X86_REG_ESP))),begin=0x51293f,end=0x51293f)
specs=[(0x512770,1253,'thug_skater_gap_end_draft',2,True),(0x512cc0,356,'thug_skater_gap_command_prefix_draft',3,False)]
for a,size,name,argc,diag in specs:
 bind(a,name,argc,'void' if diag else 'word',diag,diag)
 coverage[a]=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,size),a))
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+size-1)
for a,name,argc,result,heap,diag in [(0x45d720,'thug_component_descriptor_base',3,'word',False,False),(0x45e510,'thug_composite_initialize_draft',0,'void',False,False),(0x512360,'thug_skater_gap_start_draft',2,'void',True,False),(0x512030,'thug_skater_gap_clear_draft',0,'void',True,False),(0x512140,'thug_skater_gap_check_tricks_draft',1,'void',True,True)]:bind(a,name,argc,result,heap,diag)
for a in [0x4752f0,0x578bc0,0x578c70,0x512360,0x512030,0x461480,0x462f00,0x562510,0x5624c0,0x49f4c0,0x578670]:
 if a not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a);observe.append(a)
for a in [0x578740,0x5787f0]:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:fields.add(cpu.reg_read(UC_X86_REG_ECX)),begin=a,end=a)
P,WALK,WSTATE,WALKMODE,BALANCE,MODE,REFERENCE=[BASE+x for x in [0x129000,0x129100,0x129200,0x129400,0x129500,0x129600,0x129700]]
NODETABLE,FLAGS,HISTORY=BASE+0x170000,BASE+0x182000,BASE+0x183000
KEY,OTHER,SOURCE,TARGET=0x12345678,0x87654321,0x11223344,0x55667788
for name,at,value,offset in [('thug_gap_array_pool_index_draft',0x6f22b4,0,0),('thug_gap_array_pools_draft',0x6f22bc,0,0),('thug_gap_array_pools_draft',0x6f22c0,0,4),('thug_skater_serial_draft',0x690fa0,0,0),('thug_skater_orientation_context',0x7ce5d8,MODE,0),('thug_node_table',7277956,NODETABLE,0),('thug_network_state',0x7cce14,BASE+0x184000,0)]:
 if at in index:defaults[index[at]]=value
 else:index[at]=len(globals_);globals_.append([name,at,4,offset]);defaults.append(value)
exports += [[0x647650,'thug_composite_methods_draft'],[0x64be90,'thug_skater_gap_pending_methods_draft'],[0x64bec4,'thug_gap_primary_sentinel_methods_draft'],[0x64bec8,'thug_gap_secondary_sentinel_methods_draft'],[0x64ec80,'thug_gap_primary_node_methods_draft'],[0x64ec84,'thug_gap_secondary_node_methods_draft'],[0x64be88,'thug_trick_primary_methods'],[0x64be8c,'thug_trick_secondary_methods']]
for at,n in [(NODETABLE,0x10020),(FLAGS,0x680),(HISTORY,0x20),(BASE+0x184000,0x200)]:memory[at-BASE:at-BASE+n]=bytes(n)
memory[NODETABLE-BASE:NODETABLE-BASE+0x10000]=b'\xff'*0x10000
put(SERVICES,'<2I',PRINT,ADAPTER);put(GAME+0x20,'<I',FLAGS);put(FLAGS+0x630,'<I',0);put(FLAGS+0x63c,'<I',HISTORY)
initial=bytes(memory);oracle.initial=initial
def stack_texts(self,fn):
 if fn not in [0x512770,0x512cc0,0x45d720]:return []
 at=self.word(TIMED+0xa10)
 if not self.stack<=at<self.stack+0x18000:return []
 assert at in self.end_labels,hex(at)
 text=cstring(at)+b'\0';assert len(text)<=256
 return [{'slot':TIMED+0xa10,'original':at,'text':text.hex(),'buffer_capacity':256,'observed_formatter_destination':True}]
oracle.stack_texts=MethodType(stack_texts,oracle)
CBSTATE,CBNATIVE=BASE+0x185000,oracle.stop+0x400
def end_native(cpu,address,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);params,script=oracle.word(sp+4),oracle.word(sp+8);n=oracle.word(CBSTATE);assert n<32
 oracle.setword(CBSTATE,n+1);cpu.mem_write(CBSTATE+128+n*16,struct.pack('<4I',params,oracle.word(script+0xc8),oracle.word(P+0x24),oracle.word(P+0x38)))
 if not oracle.word(CBSTATE+4) or not n:
  count=oracle.word(CBSTATE+8);assert count<=12
  for i in range(count):oracle.setword(oracle.word(CBSTATE+16+i*8),oracle.word(CBSTATE+20+i*8))
 cpu.reg_write(UC_X86_REG_EAX,1);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,end_native,begin=CBNATIVE,end=CBNATIVE)
before_end_callback_case=case
def case(calls,patches=(),changes=None,label='EndGap'):
 stages=before_end_callback_case(calls,patches,changes,label);previous=0
 for step in stages:
  for at,data in step['outputs']:
   if at<=CBSTATE and at+len(data)//2>=CBSTATE+4:
    n=int.from_bytes(bytes.fromhex(data)[CBSTATE-at:CBSTATE-at+4],'little');step['callbacks']+=n-previous;previous=n
 return stages
class EndGraph(InsertGraph):
 def __init__(self,count=0,multiplier=2):
  super().__init__(count,multiplier)
  self.put(P,'<6I',0x64be90,0x11b4c67f,0,BODIES,0,0);fields.add(P)
  self.put(P+0x40,'<6I',7,SCORE,PHYS,BALANCE,WALK,WALKMODE);self.put(WALK+0x2c,'<I',WSTATE)
  self.put(MODE+0x40,'<I',0xd443a2bc);self.put(SCRIPTS+0xb8,'<I',TARGET)
  self.put(BODIES,'<I',0x647650);self.put(BODIES+8,'<I',0x20);self.put(BODIES+0x28,'<5I',0x6477e4,BODIES,0,BODIES+0x28,BODIES+0x28);self.put(BODIES+0x40,'<3I',0x6477e0,0,BODIES);fields.update([BODIES,BODIES+0x28,BODIES+0x40]);self.put(BODIES+0xbc,'<B',1);self.put(BODIES+0x2bc,'<I',0)
  self.put(REFERENCE+0x4c,'<4f',1,2,3,1);self.put(REFERENCE+0x8c,'<4f',0,0,1,0)
  self.put(EM+8,'<I',self.table([(0x967c138c,REFERENCE),(0xe17b231a,REFERENCE)]))
  self.nodes(0);self.nodes(0,True);self.gap_history([b'Unnamed Gap',b'Test Gap'])
  self.cached(0x541a2485);self.cached(5)
  self.symbol(0xfcfacab8,1,10)
 def array(self,kind,values):
  p=self.alloc(12);items=values[0] if len(values)==1 else 0
  if len(values)>1:items=self.alloc(len(values)*4);self.put(items,'<'+'I'*len(values),*values)
  self.put(p,'<BBHII',0,kind,0,len(values),items);return p
 def table(self,rows):
  p=self.alloc(24);b=self.alloc(48);self.put(p,'<6I',2,b,len(rows),0xffffffff,0,0);self.image[b-BASE:b-BASE+48]=bytes(48)
  for key,value in rows:
   slot=b+(key&3)*12
   if self.word(slot+4):node=self.alloc(12);self.put(node,'<3I',key,value,self.word(slot+8));self.put(slot+8,'<I',node)
   else:self.put(slot,'<3I',key,value,0)
  return p
 def cached(self,name,code=b'\x01\x24'):
  program=self.alloc(len(code));self.image[program-BASE:program-BASE+len(code)]=code;self.symbol(name,7,program)
  entry=self.alloc(20);self.put(entry,'<5I',name,program,1,0,0);slot=self.word(CACHETABLE+4)+(name&3)*12
  if self.word(slot+4):node=self.alloc(12);self.put(node,'<3I',name,entry,self.word(slot+8));self.put(slot+8,'<I',node)
  else:self.put(slot,'<3I',name,entry,0)
  self.put(CACHETABLE+8,'<I',self.word(CACHETABLE+8)+1)
  return program
 def nodes(self,count,secondary=False):
  sentinel=P+(0x2c if secondary else 0x18);nodes=[self.alloc(0x34 if secondary else 0x64) for _ in range(count)]
  self.put(sentinel,'<5I',0x64bec8 if secondary else 0x64bec4,0xffffffff,0,nodes[0] if nodes else sentinel,nodes[-1] if nodes else sentinel);fields.add(sentinel)
  for i,node in enumerate(nodes):
   size=0x34 if secondary else 0x64;self.image[node-BASE:node-BASE+size]=bytes(size)
   self.put(node,'<5I',0x64ec84 if secondary else 0x64ec80,node,0,nodes[i+1] if i+1<count else sentinel,nodes[i-1] if i else sentinel);fields.add(node)
   if secondary:self.put(node+0x20,'<5I',KEY,SOURCE,5,0,7)
   else:
    self.put(node+0x14,'<3I',KEY,0,SOURCE);self.put(node+0x60,'<I',self.array(13,[]))
    self.put(node+0x40,'<8I',*[0x10000000+i*16+j for j in range(8)])
  return nodes
 def gap_history(self,names):
  sentinel=self.alloc(0x50);self.put(sentinel+4,'<I',0xffffffff);nodes=[self.alloc(0x50) for _ in names];self.put(HISTORY+0x10,'<I',nodes[0] if nodes else sentinel)
  for i,node in enumerate(nodes):
   self.image[node-BASE:node-BASE+0x50]=bytes(0x50);self.put(node+4,'<I',i);self.put(node+12,'<I',nodes[i+1] if i+1<len(nodes) else sentinel);self.put(node+0x48,'<I',self.text(names[i]))
  return nodes
 def level_nodes(self,rows):
  nodes=[self.structure([(0xa1dc81f9,13,name),*items]) for name,items in rows];self.put(NODETABLE+0x10004,'<3I',0,0,self.array(10,nodes))
  for i,(name,_) in enumerate(rows):
   slot=name&0x3fff
   while self.word(NODETABLE+slot*4)>>16!=0xffff:slot=(slot+1)&0x3fff
   self.put(NODETABLE+slot*4,'<HH',0,i)
  return nodes
 def pool(self,count=32):
  pool=self.alloc(0x5c);blocks=self.alloc(count*16);self.image[pool-BASE:pool-BASE+0x5c]=bytes(0x5c)
  self.put(pool,'<6I',blocks,blocks+count*16,0,0,0,blocks)
  for i in range(count):self.put(blocks+i*16,'<I',blocks+(i+1)*16 if i+1<count else 0)
  return pool
 def run(self,calls,label,ui=False,poison=0,changes=None):
  regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];before=[oracle.cpu.reg_read(r) for r in regs]
  oracle.cpu.mem_write(oracle.stack,bytes([poison])*0x18000)
  try:stages=case((setup()+numeric_setup() if ui else [])+calls,self.patches(),changes,label)
  except Exception:print('FAILED',label,flush=True);raise
  assert before==[oracle.cpu.reg_read(r) for r in regs],label
  return stages

for gate,count,key in itertools.product([0,1],[0,1,3],[KEY,OTHER]):
 g=EndGraph();g.nodes(count);g.put(STATE+0x70,'<B',gate);params=g.structure([(0x3b442e26,13,key)])
 g.run([call(0x512770,P,[params,SCRIPTS])],f'EndGap gate/list/key/{gate}/{count}/{key:x}')
for flags in [1,0x8000,0x10000,0x80000000,0xffffffff]:
 g=EndGraph();nodes=g.nodes(3)
 for node in nodes:g.put(node+0x18,'<I',flags)
 g.run([call(0x512770,P,[g.structure([(0x3b442e26,13,KEY)]),SCRIPTS])],f'EndGap mask/{flags}')
for points,local,name in itertools.product([None,0,123,0xffffffff],[0,1],[None,b'',b'Test Gap']):
 g=EndGraph();g.nodes(1);g.put(BODIES+0xbc,'<B',local);items=[(0x3b442e26,13,KEY)]
 if points is not None:items.append((0xcd66c8ae,1,points))
 if name is not None:items.append((0xc4745838,3,g.text(name)))
 g.run([call(0x512770,P,[g.structure(items),SCRIPTS])],f'EndGap score/{points}/{local}/{name}',ui=points is not None and bool(local))

# Unnamed gaps require an actual level-node link to the current script node.
for links in [[],[TARGET],[SOURCE],[OTHER,TARGET]]:
 g=EndGraph();nodes=g.nodes(3)
 for node in nodes:g.put(node+0x14,'<I',0)
 g.level_nodes([(SOURCE,[(0x2e7d5ee7,12,g.array(13,links))]),(TARGET,[]),(OTHER,[])])
 g.run([call(0x512770,P,[g.structure([]),SCRIPTS])],f'EndGap unnamed link/{links}')
# The required boolean is supplied by a real return statement in cached QB.
for answer,pooled in itertools.product([0,1,2,0xffffffff],[None,0,1]):
 g=EndGraph();g.nodes(2)
 code=b'\x01\x29\x16'+struct.pack('<I',0x1c39f1b9)+b'\x07\x17'+struct.pack('<I',answer)+b'\x01\x24'
 g.cached(0x35b75889,code);params=g.structure([(0x3b442e26,13,KEY),(0,13,0x687e2c25)])
 changes={} if pooled is None else {0x6f3614:pooled,0x6f361c+4*pooled:g.pool()}
 g.run([call(0x512770,P,[params,SCRIPTS])],f'EndGap predicate/{answer}/{pooled}',changes=changes)
for kind,baseline,secondary,matching in itertools.product(['none','bound','named','both','array'],[-1,0,3],[0,1,3],[False,True]):
 g=EndGraph(3);node=g.nodes(1)[0];others=g.nodes(secondary,True);g.put(node+0x28,'<I',5);g.put(node+0x24,'<i',baseline)
 if secondary:
  for other in others:g.put(other+0x20,'<I',OTHER)
  if matching:g.put(others[-1]+0x20,'<I',KEY)
 checksum=zlib.crc32(b'ollie')^0xffffffff
 for i in range(3):g.put(RECORDS+i*256+0x10,'<I',checksum)
 if kind in ['bound','both']:
  definition=g.structure([(0x7031f10c,10,g.structure([(0xa1dc81f9,3,g.text(b'Ollie'))]))]);g.symbol(0x81100000,10,definition)
  bindings=g.structure([(KEY,13,0x81100000)]);profile=g.structure([(0xa1dc81f9,13,0x0a7be964),(0xd544aa2d,10,bindings)])
  g.header(PROFILE+0x5c,profile);g.put(node+0x20,'<I',KEY)
 if kind in ['named','both']:g.put(node+0x2c,'<I',checksum)
 if kind=='array':g.put(node+0x60,'<I',g.array(13,[checksum]))
 g.run([call(0x512770,P,[g.structure([(0x3b442e26,13,KEY)]),SCRIPTS])],f'EndGap requirement/{kind}/{baseline}/{secondary}/{matching}')
for network,argument in itertools.product([False,True],[False,True]):
 g=EndGraph();g.nodes(1);params=g.structure([(0x3b442e26,13,KEY),(0x7c9e51ab,13,5)]+([(0,13,0x20209c31)] if network else [])+([(0,13,0x23627fd7)] if argument else []))
 g.run([call(0x512770,P,[params,SCRIPTS])],f'EndGap spawned success/{network}/{argument}')
# Nested StartGap prepends a different-key node, so final deletion must search
# past it and then restart the outer scan at the fresh live head.
for existing in [1,3]:
 g=EndGraph();g.nodes(existing);nested=g.structure([(0x3b442e26,13,OTHER)])
 params=g.structure([(0x3b442e26,13,KEY),(0xec1cd520,10,nested)])
 g.run([call(0x512770,P,[params,SCRIPTS]),call(0x512030,P)],f'EndGap nested StartGap/{existing}')
for name in [0xe5399fb2,0x65b9ec39,0x0196772b,0x42f80e5e,0xfc4f2009,0x4562e4a6,0,0xffffffff]:
 for descriptor in [False,True]:
  g=EndGraph();g.nodes(1);params=g.structure([(0x3b442e26,13,KEY),(0xa26994e6,13,5)])
  g.level_nodes([(TARGET,[(0x2e7d5ee7,12,g.array(13,[SOURCE]))]),(SOURCE,[(0x2ca8a299,13,5)])])
  desc=g.alloc(16);g.put(desc,'<4I',name,0,0,0)
  invoke=call(0x45d720,P,[desc,params,SCRIPTS]) if descriptor else call(0x512cc0,P,[name,params,SCRIPTS])
  g.run([invoke,call(0x512030,P)],f'Full Gap command/{name:x}/{descriptor}')

# Cover the linked-script loop's continue and exhausted-list exits as well.
for script_at in [None,1]:
 g=EndGraph();g.level_nodes([(TARGET,[(0x2e7d5ee7,12,g.array(13,[SOURCE,OTHER]))]),(SOURCE,[]),(OTHER,[] if script_at is None else [(0x2ca8a299,13,5)])])
 g.run([call(0x512cc0,P,[0x4562e4a6,g.structure([]),SCRIPTS])],f'Full Gap linked scan/{script_at}')
for mutation in ['remove current','remove successor','replace head','prepend other','change remaining guards']:
 g=EndGraph();nodes=g.nodes(1 if mutation in ['remove current','prepend other'] else 3);sentinel=P+0x18
 if mutation=='remove current':
  n=nodes[0];writes=[(sentinel+12,sentinel),(sentinel+16,sentinel),(n+12,n),(n+16,n)]
 elif mutation=='remove successor':
  a,b,c=nodes;writes=[(a+12,c),(c+16,a),(b+12,b),(b+16,b)]
 elif mutation=='replace head':
  a,b,c=nodes;writes=[(sentinel+12,b),(b+16,sentinel),(a+12,a),(a+16,a),(b+0x14,OTHER)]
 elif mutation=='prepend other':
  n=g.alloc(0x64);g.image[n-BASE:n-BASE+0x64]=bytes(0x64);g.put(n,'<5I',0x64ec80,n,0,n,n);fields.add(n);g.put(n+0x14,'<I',OTHER);g.put(n+0x60,'<I',g.array(13,[]))
  writes=[(n+12,nodes[0]),(n+16,sentinel),(nodes[0]+16,n),(sentinel+12,n)]
 else:writes=[(nodes[1]+0x18,0x10000),(nodes[2]+0x14,OTHER)]
 event=zlib.crc32(b'_success',KEY^0xffffffff)^0xffffffff
 for at,data in event_handler(event,0,0):g.image[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
 code=b'\x01\x43'+struct.pack('<I',CBNATIVE)+b'\x01\x24';g.image[PROGRAM-BASE:PROGRAM-BASE+len(code)]=code
 g.image[CBSTATE-BASE:CBSTATE-BASE+1024]=bytes(1024);g.put(CBSTATE,'<3I',0,1,len(writes))
 for i,(target,value) in enumerate(writes):g.put(CBSTATE+16+i*8,'<2I',target,value)
 params=g.structure([(0x3b442e26,13,KEY)])
 g.run([call(0x512770,P,[params,SCRIPTS])],f'EndGap live event mutation/{mutation}')
 assert oracle.word(CBSTATE)>0

# An actual start -> trick insertion -> end -> secondary script flow, using the
# recovered constructors/owned strings, score queries and UI rather than a
# prebuilt active node. Zero, one and two new tricks test the saved count gate.
for tricks,points,descriptor in itertools.product([0,1,2],[0,500],[False,True]):
 g=EndGraph();trick_name=g.text(b'Ollie');start=g.structure([(0x3b442e26,13,KEY),(0xa26994e6,13,5),(0x3eafa520,3,trick_name)])
 end=g.structure([(0x3b442e26,13,KEY),(0xc4745838,3,g.text(b'Test Gap')),(0xcd66c8ae,1,points)])
 desc=g.alloc(16);g.put(desc,'<4I',0xe5399fb2,0,0,0)
 complete=call(0x45d720,P,[desc,end,SCRIPTS]) if descriptor else call(0x512770,P,[end,SCRIPTS])
 calls=[call(0x512360,P,[start,SCRIPTS])]+[call(0x563990,SCORE,[trick_name,100,0])]*tricks+[complete,call(0x512140,P,[0]),call(0x512030,P)]
 g.run(calls,f'Actual StartGap score EndGap flow/{tricks}/{points}/{descriptor}',ui=True)

scope='Full original EndGap and all six Gap command routes, including score/history awards, predicate QB, required tricks, secondary marking, success scripts, nested StartGap and callback-visible live-list cleanup. Actual StartGap -> trick insertion -> EndGap -> secondary script flows compare. All arena bytes, globals, heap effects and preserved registers compare without numeric masks or uninitialized-byte allowances. The retained pointer to EndGap temporary text is relocated only after proving the original formatter destination, Wasm stack bounds and exact text including NUL; this preserves the original dangling-pointer behavior, not a safe text lifetime. Initialized graphs, fitting strings, required predicate output and successful allocations remain caller contracts. Full skater startup, camera/rendering and playable training are unfinished.'
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'gap-end-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_event','original':NATIVE},{'module':'gap-end-callback.wasm','export':'fixture_gap_end_native','original':CBNATIVE}]}
subprocess.run([str(ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(folder/'gap-end-callback.c'),'-o',str(folder/'gap-end-callback.wasm')],check=True)
(folder/'gap-end-memory.bin').write_bytes(initial);(folder/'gap-end-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'scope':scope,'instruction_coverage':{hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}}
(folder/'gap-end-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
