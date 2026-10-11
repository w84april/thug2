"""Original score insertion, with explicit tracking of indeterminate stack tails."""
from pathlib import Path
import importlib.util,sys,itertools
spec=importlib.util.spec_from_file_location('score_insert_oracle',Path('local/analysis/score-insert-oracle-derived.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
import script_heap_oracle
script_heap_oracle.ScriptHeapOracle=module.ScriptHeapOracle
exec(compile(Path('local/analysis/score-insert-ui-setup.py').read_text(),'<preserved score UI setup>','exec'))
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
from types import MethodType
folder=ROOT/'local/analysis';pe=load();oracle.cpu.hook_del(debug_hook)
# A typed diagnostic boundary already used by maintained score comparisons.
src=(ROOT/'tools/verify_balance_score.py').read_text()
src=src[src.index('def hash_text'):src.index('oracle.cpu.hook_add(UC_HOOK_CODE,score_output')]
src=src.replace("b'   total %d\\n']","b'   total %d\\n',b'Trick Limit (%d) Reached\\n']")
exec(compile(src,'<score diagnostics>','exec'));oracle.cpu.hook_add(UC_HOOK_CODE,score_output,begin=0x401c30,end=0x401c30)
DIAG=BASE+0x118000;put(PRINT,'<I',DIAG);memory[DIAG-BASE:DIAG-BASE+0x5000]=bytes(0x5000);put(DIAG+4,'<I',SCORE)
TRICK,PHYS,STATE,TIMED,ADJUST,DIFFICULTY,PROFILE_MANAGER,PROFILE=[BASE+x for x in [0x120000,0x122000,0x124000,0x125000,0x126000,0x127000,0x128000,0x128100]]
RECORDS,DATA=BASE+0x210000,BASE+0x130000
put(CONTEXT,'<I',BASE+0x280000);put(CONTEXT+20,'<I',BASE+SIZE)
memory[TRICK-BASE:DATA-BASE]=bytes(DATA-TRICK)
for at,kind,next_ in [(COMPONENT,0x8bce7e66,TRICK),(TRICK,0x270f56e1,PHYS),(PHYS,0x5bd63b29,TIMED),(TIMED,0x4ff8dac6,ADJUST),(ADJUST,0x9f9cc949,0)]:put(at+4,'<4I',kind,0,BODIES,next_)
put(PHYS+0x1528,'<I',STATE);put(BODIES+0x280,'<I',PHYS);put(GAME+0x38c,'<I',DIFFICULTY)
put(PROFILE_MANAGER+0x14,'<3I',PROFILE,PROFILE+0x100,0)
if 0x7ce4b4 in index:defaults[index[0x7ce4b4]]=PROFILE_MANAGER
else:index[0x7ce4b4]=len(globals_);globals_.append(['thug_profile_manager',0x7ce4b4,4,0]);defaults.append(PROFILE_MANAGER)
initial=bytes(memory);oracle.initial=initial
specs=[(0x5629d0,330,'thug_score_compress_history_draft',0,False),(0x563990,1433,'thug_score_insert_draft',3,True)]
coverage={};hits=Counter()
for a,size,name,argc,diag in specs:
 bind(a,name,argc,'void',True,diag);coverage[a]=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,size),a))
 oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+size-1)
# Heap scope+11c is the existing UI scope, already initialized by UI fixtures.
oracle.indeterminate=set();oracle.compressions=[]
def indeterminate_ranges(self):
 result=[]
 for at in sorted(self.indeterminate):
  if result and result[-1][0]+result[-1][1]==at:result[-1][1]+=1
  else:result.append([at,1])
 return result
oracle.indeterminate_ranges=MethodType(indeterminate_ranges,oracle)
def compression_copy(cpu,at,size,user):
 destination=cpu.reg_read(UC_X86_REG_EDI)-0x9c
 assert BASE<=destination and destination+0x9c<BASE+SIZE
 assert bytes(cpu.mem_read(destination+0x1c,7))==b'... + \0'
 assert bytes(cpu.mem_read(destination+0x5c,9))==b'...\\_+\\_\0'
 ranges=[[destination+0x23,57],[destination+0x65,55]]
 oracle.compressions.append({'destination':destination,'indeterminate_tails':ranges})
 for start,length in ranges:oracle.indeterminate.update(range(start,start+length))
def written(cpu,access,at,size,value,user):
 if oracle.indeterminate:oracle.indeterminate.difference_update(range(at,at+size))
oracle.cpu.hook_add(UC_HOOK_CODE,compression_copy,begin=0x562afa,end=0x562afa)
oracle.cpu.hook_add(UC_HOOK_MEM_WRITE,written,begin=BASE,end=BASE+SIZE-1)
for a in [0x5629d0,0x563990,0x561550,0x5614d0,0x5628b0,0x51c9d0,0x5638a0,0x580790,0x4750b0]:
 if a not in observe:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a);observe.append(a)
# Reuse the existing terminal-native observation boundary inside real QB delivery.
EXTRA=GRAPH+0x8000
NATIVE,NATIVE_STATE,PROGRAM=oracle.stop+0x300,EXTRA+0x200,EXTRA+0x600
assert NATIVE_STATE==0x18f8200
balance=(ROOT/'tools/verify_balance_score.py').read_text()
exec(compile(balance[balance.index('def event_native'):balance.index('new_branches=')],'<score QB observation>','exec'))
fields.update([SCRIPTS+0xec,PROGRAM+2])
exec(compile(balance[balance.index('def event_handler'):balance.index('event_cases=0')],'<score event fixture>','exec'))
class InsertGraph:
 def __init__(self,count=0,multiplier=0):
  self.image=bytearray(initial);self.cursor=DATA
  self.put(SCORE+0x38,'<5I',0,0,0,0,0);self.put(SCORE+0x4c,'<5I',ITEMS,250,count,16,count)
  self.put(SCORE+0x60,'<fIii',multiplier,0,-1,-1);self.put(SCORE+0x14,'<I',0)
  for i in range(251):
   self.put(ITEMS+i*4,'<I',RECORDS+i*256);self.image[RECORDS+i*256-BASE:RECORDS+i*256-BASE+256]=b'\xa5'*256
   self.put(RECORDS+i*256,'<7I',100+i,0,0,0,0xabc00000+i,0,2 if i==0 else 0)
   self.text_at(RECORDS+i*256+0x1c,b'Old');self.text_at(RECORDS+i*256+0x5c,b'Old ')
  self.symbol(0xfd4625cd,1,3);self.symbol(0xb23d1fb5,1,0);self.symbol(0x59b9a85e,2,bits(1.5));self.symbol(0xb33d71c0,1,100)
  self.header(DIFFICULTY+0x398,self.structure([]),pointer=True)
  self.header(SETTINGS+4,self.structure([(0xa1dc81f9,13,0),(0x1ded1ea4,1,1)]))
  self.header(PROFILE+0x5c,self.structure([(0xa1dc81f9,13,0x0a7be964)]))
  pair=self.alloc(12);self.put(pair,'<I2f',0,7,7);self.symbol(0x0b84f532,10,self.structure([(0,5,pair)]))
  self.put(TIMED+0xa90,'<I',1);self.put(TIMED+0x9f4,'<B',1)
 def put(self,p,fmt,*v):struct.pack_into(fmt,self.image,p-BASE,*v)
 def word(self,p):return struct.unpack_from('<I',self.image,p-BASE)[0]
 def alloc(self,n):p=self.cursor;self.cursor=(p+n+3)&~3;assert self.cursor<BASE+0x170000;return p
 def text_at(self,p,s):self.image[p-BASE:p-BASE+len(s)+1]=s+b'\0'
 def text(self,s):p=self.alloc(len(s)+1);self.text_at(p,s);return p
 def header(self,p,s,pointer=False):
  if pointer:self.put(p,'<I',s)
  else:self.image[p-BASE:p-BASE+8]=self.image[s-BASE:s-BASE+8]
 def structure(self,items):
  nodes=[self.alloc(16) for _ in items]
  for i,(name,kind,value) in enumerate(items):self.put(nodes[i],'<4I',kind*2,name,value,nodes[i+1] if i+1<len(nodes) else 0)
  p=self.alloc(8);self.put(p,'<2I',0,nodes[0] if nodes else 0);return p
 def symbol(self,name,kind,value):
  bucket=SYMBOLS+(name&4095)*4;p=self.alloc(20);self.put(p,'<BBH4I',0,kind,0,name,0,value,self.word(bucket));self.put(bucket,'<I',p)
 def patches(self):
  result=[]
  for i in range(0,len(initial),4096):
   if self.image[i:i+4096]!=initial[i:i+4096]:result.append([BASE+i,bytes(self.image[i:i+4096]).hex()])
  return result
 def run(self,calls,label,ui=False,poison=0):
  regs=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP];before=[oracle.cpu.reg_read(r) for r in regs]
  oracle.cpu.mem_write(oracle.stack,bytes([poison])*0x18000)
  try:stages=case((setup()+numeric_setup() if ui else [])+calls,self.patches(),label=label)
  except Exception:print('FAILED',label,flush=True);raise
  assert before==[oracle.cpu.reg_read(r) for r in regs],label
  return stages

# Compression requires a surviving first entry. Early guards, delimiter scans,
# repeated compaction, signed nonpositive counts and poisoned stack tails.
for count,cut in [(0,0),(1,None),(2,1),(3,1),(4,2),(12,1),(12,7)]:
 for gate in ['first','second','pass']:
  for poison in [0,0xa5,0xff]:
   g=InsertGraph(count,2)
   if cut is not None and cut>0:g.text_at(RECORDS+cut*256+0x1c,b'')
   n=cut if cut is not None else count
   g.put(SCORE+0x68,'<2I',(n-1 if gate=='second' else n)&0xffffffff,(n-1 if gate=='first' else n)&0xffffffff)
   # Removing the entire nonempty array violates the caller's surviving-entry contract.
   if gate=='pass' and count and n==count:continue
   g.run([call(0x5629d0,SCORE)],f'compression/{count}/{cut}/{gate}/{poison}',poison=poison)
for name,flags,count,multiplier in itertools.product([b'',b'Ollie',b'Kick flip'],[0,2,0x10,0x20,0x50,0x80,0x200],[0,1,3],[0,2]):
 g=InsertGraph(count,multiplier);text=g.text(name)
 g.run([call(0x563990,SCORE,[text,123,flags])],f'insert/{name}/{flags}/{count}/{multiplier}',ui=True)

# Exercise repeat-map hits and all raw stance selectors with sufficient storage.
# The original indexes past its 36-byte freshly allocated record for variants
# four/six; these cases provide a larger existing payload instead of inventing
# bounds checks or relying on an allocation overrun.
import zlib
for flags,previous,threshold,multiplier in itertools.product([0,4,8,12,0x404,0x408,0x200],[0,1,2,3,7],[0,3],[0.5,2]):
 g=InsertGraph(3,multiplier);name=g.text(b'Ollie');repeat=g.alloc(64);node=g.alloc(12)
 g.put(repeat,'<16I',*([0]*16));variant=(flags>>1)&(4 if flags&0x400 else 6)
 g.put(repeat+4+variant*4,'<I',2);g.put(repeat+0x14+variant*4,'<I',previous)
 g.put(node,'<3I',zlib.crc32(b'ollie')^0xffffffff,repeat,0);g.put(SCORE+0x38,'<5I',1,node,node,0,0)
 g.symbol(0xfd4625cd,1,threshold);g.put(BODIES+0x110,'<B',1);g.put(STATE+0x28,'<B',2)
 g.run([call(0x563990,SCORE,[name,101,flags])],f'repeat/{flags}/{previous}/{threshold}/{multiplier}',ui=True)
for count,flags,adjust in itertools.product([10,11,12],[0,2,0x200],[0,1]):
 g=InsertGraph(count,2);g.put(ADJUST+0x1c,'<B',adjust);name=g.text(b'Ollie')
 g.run([call(0x563990,SCORE,[name,0xffffffff,flags])],f'consecutive/{count}/{flags}/{adjust}',ui=True)
for text in [b'',b'...',b'Old',b'Old ']:
 g=InsertGraph(3,2);name=g.text(b'Ollie')
 for i in range(3):g.text_at(RECORDS+i*256+0x5c,text)
 g.run([call(0x563990,SCORE,[name,321,0])],f'prior-label/{text}',ui=True)
for empty,flags,compress in itertools.product([False,True],[0,0x200],[False,True]):
 g=InsertGraph(250,2);name=g.text(b'' if empty else b'Ollie')
 # Short UI output still retains the 250 real score records and array slots.
 for i in range(250):g.text_at(RECORDS+i*256+0x5c,b'')
 if compress:
  g.text_at(RECORDS+200*256+0x1c,b'');g.put(SCORE+0x68,'<2I',200,200)
 g.run([call(0x563990,SCORE,[name,123,flags])],f'full/{empty}/{flags}/{compress}',ui=compress,poison=0xa5)
# Distinct text/storage counts trigger the original full-array reuse path.
g=InsertGraph(250,2);g.put(SCORE+0x5c,'<I',3)
for i in range(250):g.text_at(RECORDS+i*256+0x5c,b'')
g.run([call(0x563990,SCORE,[g.text(b'Ollie'),44,2])],'full storage retains existing last allocation',ui=True)
# Missing registration returns before touching components or score state.
g=InsertGraph();g.put(SCORE+8,'<h',-17)
g.run([call(0x563990,SCORE,[g.text(b'Ollie'),123,0])],'missing registered skater')
# The limit diagnostic may change which entry receives the additional points.
for target,value in [(SCORE+0x54,2),(SCORE+0x60,bits(4.5))]:
 g=InsertGraph(250,2);g.put(DIAG+8,'<3I',target,value,1)
 g.run([call(0x563990,SCORE,[g.text(b'Ollie'),123,0])],'limit diagnostic mutation before score rereads')

for target,value in [(SCORE+0x60,bits(3.5)),(SCORE+0x14,600),(ADJUST+0x1c,1),(SCORE+0x68,0)]:
 g=InsertGraph(0,0)
 for at,data in event_handler(0x670fda8c,target,value):g.image[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
 g.run([call(0x563990,SCORE,[g.text(b'Ollie'),123,0])],'combo-start event and UI QB mutation before later score reads',ui=True)
 assert oracle.word(NATIVE_STATE)==2
for flags in [0,2,0x200,0x50]:
 g=InsertGraph(1,0);name=g.text(b'Ollie')
 g.run([call(0x563990,SCORE,[name,123,flags])]*7,f'seven consecutive inserts/{flags}',ui=True)
# Compression leaves uncertain padding only until real text writes define it.
g=InsertGraph(250,2)
for i in range(250):g.text_at(RECORDS+i*256+0x5c,b'')
g.text_at(RECORDS+200*256+0x1c,b'');g.put(SCORE+0x68,'<2I',200,200)
g.run([call(0x563990,SCORE,[g.text(b'Ollie'),123,2]),call(0x563990,SCORE,[g.text(b'Kick flip'),101,0])],'compression followed by another full insertion',ui=True,poison=0xff)

scope='Full original score insertion and history compression with real score/UI/parameter/event callees. Only the two uninitialized string tails copied by5629d0 are compared by definedness; later original writes remove bytes from that allowance. All defined score/text fields, arena bytes, globals, heap effects and preserved registers compare. Full EndGap and playable browser training remain unfinished.'
used={s['fn'] for c in oracle.cases for s in c['steps']}
fixture={'base':BASE,'memory':'score-insert-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope,'pointer_exports':exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'native_callbacks':[{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_score_print','slots':[PRINT+4]},{'module':'balance-score-diagnostics.wasm','export':'fixture_balance_event','original':NATIVE}]}
(folder/'score-insert-memory.bin').write_bytes(initial);(folder/'score-insert-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'callees':dict(oracle.coverage),'scope':scope,'instruction_coverage':{hex(a):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for a,code in coverage.items()}}
(folder/'score-insert-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k in ['cases','calls','instruction_coverage']}),flush=True)
