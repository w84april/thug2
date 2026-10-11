"""Original score insertion, with explicit tracking of indeterminate stack tails."""
from pathlib import Path
import importlib.util,sys,itertools
spec=importlib.util.spec_from_file_location('score_insert_oracle',Path('local/analysis/gap-end-oracle-derived.py'))
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

