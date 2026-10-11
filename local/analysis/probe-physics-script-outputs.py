"""Original script output members with real construction and disposal callees."""
import hashlib,itertools,json,random,struct,subprocess
from collections import Counter
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/analysis';pe=load();rng=random.Random(0x4fd580)
BASE,SIZE=0x1800000,0x100000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
PHYS,STATE,BODY,BODY2,SCRIPT,CONTROL=BASE+0x1000,BASE+0x3000,BASE+0x4000,BASE+0x5000,BASE+0x6000,BASE+0x6400
BUCKETS,LOG,HEAP=BASE+0x8000,BASE+0x40000,BASE+0x60000
initial=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,initial,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);put(PHYS+0xc,'<I',BODY);put(PHYS+0x1528,'<I',STATE)
initial[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000);initial[CONTROL-BASE:CONTROL-BASE+32]=bytes(32)
initial=bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],['thug_script_string_interning',0x6f3570,1],['thug_script_symbol_buckets',0x6f3624,4],['thug_frame_counter',0x7d1ec8,4],['thug_frame_rate',0x684fd0,4],['thug_timer_origin',0x696d64,4],['thug_timer_offset',0x696d60,4],['thug_time_scale',0x67d7c0,4]]
defaults=[0,0,0,BUCKETS,100,bits(60),0,0,bits(1)]
members={0x4fc940:'get_airtime',0x4fd580:'get_matrix_normal',0x4fd5e0:'get_last_ground_pos',0x4fd610:'get_last_ground_heading',0x4fdc30:'get_ammo',0x4fdc50:'get_ammo_type',0x4fdc70:'get_pitch_bail_dir'}
functions={hex(at):{'name':'thug_physics_'+n+'_draft','this':True,'result':'word','cleanup':8,'memory':True} for at,n in members.items()}
functions['0x477090']={'name':'thug_script_structure_clear','this':True,'result':'void','cleanup':0,'memory':True}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,observe=[0x477b80,0x477c60,0x477d40,0x477e20,0x477920,0x477140,0x4772a0,0x477090,0x44ece0,0x5be970])
hits=Counter();guards={};returns={};md=Cs(CS_ARCH_X86,CS_MODE_32)
lengths={0x4fc940:109,0x4fd580:84,0x4fd5e0:46,0x4fd610:32,0x4fdc30:32,0x4fdc50:32,0x4fdc70:32}
decoded={}
for at,n in lengths.items():
 ins=list(md.disasm(pe.get_data(at-0x400000,n),at));ins=ins[:next(i for i,x in enumerate(ins) if x.mnemonic=='ret')+1]
 decoded[at]=ins
 for i in ins:
  if i.mnemonic=='ret':returns[i.address]=at
def observe(cpu,at,size,user):
 hits[at]+=1
 if at in members:guards[at]=[cpu.reg_read(r) for r in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]]
 if at in returns:assert guards[returns[at]]==[cpu.reg_read(r) for r in [UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]]
for at,n in lengths.items():oracle.cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at+n-1)
old_record=oracle.record
def record(kind,a,b,c):
 old_record(kind,a,b,c)
 if kind==1 and oracle.word(CONTROL):
  count=oracle.word(CONTROL+4)+1;oracle.setword(CONTROL+4,count)
  if count==oracle.word(CONTROL):
   for off in [8,16]:
    address=oracle.word(CONTROL+off)
    if address:oracle.setword(address,oracle.word(CONTROL+off+4))
oracle.record=record
class Graph:
 def __init__(self):self.image=bytearray(initial);self.cursor=BASE+0xc000
 def put(self,at,fmt,*v):struct.pack_into(fmt,self.image,at-BASE,*v)
 def alloc(self,n):at=self.cursor;self.cursor=(at+n+3)&~3;assert self.cursor<BASE+0x30000;return at
 def text(self):
  at=self.alloc(16);self.image[at-BASE:at-BASE+8]=b'owned-qb';self.image[at-BASE+8]=0;return at
 def structure(self,items):
  at=self.alloc(8);nodes=[self.alloc(16) for _ in items];self.put(at,'<2I',0,nodes[0] if nodes else 0)
  for i,(name,kind,value) in enumerate(items):self.put(nodes[i],'<4I',kind*2+(i&1),name,value,nodes[i+1] if i+1<len(nodes) else 0)
  return at
 def patches(self):return [[BASE+i,self.image[i:i+4].hex()] for i in range(0,0x30000,4) if self.image[i:i+4]!=initial[i:i+4]]
labels=[]
def run(at,g,target,p=(),changes=None,label='script output',repeat=2,clear=True):
 patches=g.patches()+[patch(SCRIPT+0x14,'<I',target)]+list(p)
 calls=[(at,PHYS,[0xdeadbeef,SCRIPT])]*repeat
 if clear:calls.append((0x477090,target,[]))
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 stages=oracle.case(calls,patches,changes);labels.append(label);return stages
keys={0x4fc940:[0xad6bcdb4],0x4fd580:[0x7323e97c,0x0424d9ea,0x9d2d8850],0x4fd5e0:[0x7f261953],0x4fd610:[0x9bc7fc76],0x4fdc30:[0x107081d5],0x4fdc50:[0x1d1a8b59],0x4fdc70:[0xd65efde5]}
words=[0,1,0x80000000,0x7fffffff,0xffffffff,0x3f800000,0x7f800000,0xff800000,0x7f812345,0xff812345,0x7fc12345]+[rng.randrange(2**32) for _ in range(16)]
for at,value,kind in itertools.product([k for k in members if k!=0x4fc940],words,['empty','duplicate','owned']):
 g=Graph();items=[]
 for key in keys[at]:
  if kind=='duplicate':items += [(key,1,0x12345678),(0x11223344,13,0x12345678),(key,13,0x87654321)]
  elif kind=='owned':items += [(key,3,g.text())]
 target=g.structure(items)
 p=[patch(PHYS+off,'<I',value) for off in [0x2f8,0x2fc,0x2d4,0x348]]
 p += [patch(PHYS+0x338,'<3I',value,value^0x80000000,value^0x12345678),patch(BODY+0x7c,'<3I',value,value^0x80000000,value^0x12345678)]
 run(at,g,target,p,label=f'{members[at]},bits{value:x},target{kind}')
for mode,delta in itertools.product([0,3,4,5,6,0xffffffff],[0,1,999,1000,1001,16777215,16777216,16777217,0x7fffffff,0x80000000,0x80000001,0xffffffff]):
 g=Graph();target=g.structure([(0xad6bcdb4,3,g.text())]);start=0xfffffff0
 run(0x4fc940,g,target,[patch(STATE+0x18,'<I',mode),patch(PHYS+0x380,'<2I',start,(start+delta)&0xffffffff)],label=f'airtime completed mode{mode:x},delta{delta:x}')
for mode,frame,offset in itertools.product([1,2],[0,1,100,0x80000000,0xffffffff],[0,0x80000000,0xffffffff]):
 g=Graph();target=g.structure([])
 run(0x4fc940,g,target,[patch(STATE+0x18,'<I',mode),patch(PHYS+0x380,'<2I',0xffffffff,0)],{4:frame,7:offset},label=f'airtime live mode{mode},frame{frame:x},offset{offset:x}')
# Mutation after allocation is test instrumentation, not a substituted game callee.
# Original getters must reload live body/script pointers between scalar insertions.
for which,allocation in itertools.product(['body','arguments','both','source'],[1,2]):
 g=Graph();target=g.structure([]);other=g.structure([])
 a,v=(PHYS+0xc,BODY2) if which in ['body','both'] else ((SCRIPT+0x14,other) if which=='arguments' else (BODY+0x80,0x7f812345))
 a2,v2=(SCRIPT+0x14,other) if which=='both' else (0,0)
 p=[patch(BODY+0x7c,'<3I',0x3f800000,0x40000000,0x40400000),patch(BODY2+0x7c,'<3I',0x41000000,0x41100000,0x41200000),patch(CONTROL,'<6I',allocation,0,a,v,a2,v2)]
 run(0x4fd580,g,target,p,label=f'matrix normal reload {which} at allocation{allocation}',repeat=1,clear=False)
for at,offset in [(0x4fd5e0,0x338),(0x4fd610,0x348),(0x4fdc30,0x2f8),(0x4fdc50,0x2fc),(0x4fdc70,0x2d4)]:
 g=Graph();target=g.structure([]);other=g.structure([])
 p=[patch(PHYS+offset,'<3I',0x7f812345,0xff812345,0x80000000),patch(CONTROL,'<6I',1,0,PHYS+offset,0x12345678,SCRIPT+0x14,other)]
 run(at,g,target,p,label='source captured before allocation and argument-pointer mutation',repeat=1,clear=False)
coverage={}
for at,ins in decoded.items():
 missing=[hex(i.address) for i in ins if not hits[i.address]];assert not missing,(hex(at),missing)
 coverage[hex(at)]={'total':len(ins),'covered':len(ins),'missing':[]}
scope='Seven complete original script-output members: GetAirtime, GetMatrixNormal, GetLastGroundPos, GetLastGroundHeading, GetAmmo, GetAmmoType and GetPitchBailDir. Actual numeric/vector construction, duplicate replacement, owned-string disposal, retained calls and cleanup run. Raw float/NaN payloads are copied exactly; airtime retains uint32 signed-load correction and PC24 scaling. Instrumented allocator changes body pointers, source values and script output structures during insertion to verify captures and reload order. All fixture memory, heap event order, globals, return values and callee-saved registers compare. Successful allocation, valid owned graphs and positive frame-rate contracts remain; not actual level startup.'
fixture={'base':BASE,'memory':'physics-script-outputs-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'physics-script-outputs-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'physics-script-outputs-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'counts':dict(oracle.counts),'instruction_coverage':coverage,'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'physics-script-outputs-original.json').write_text(json.dumps(report,indent=2)+'\n');print('Script outputs',len(labels),sum(oracle.counts.values()),sum(v['covered'] for v in coverage.values()),flush=True)
