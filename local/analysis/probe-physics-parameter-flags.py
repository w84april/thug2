"""Original parameter-driven members, retaining real QB lookup implementations."""
import itertools,json,random,re,struct
from collections import Counter
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import ROOT,SHA256,load
folder=ROOT/'local/analysis';pe=load();rng=random.Random(0x4fd140)
BASE,SIZE,PHYS,STATE=0x1800000,0x10000,0x1805000,0x1807000
STACK,STOP=0x3000000,0x3f00000
initial=bytearray(rng.randrange(256) for _ in range(SIZE));initial[:0x4000]=bytes(0x4000)
struct.pack_into('<I',initial,PHYS-BASE+0x1528,STATE);initial=bytes(initial)
cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
members={0x4fbfe0:'set_skater_vehicle',0x4fc040:'lock_velocity_direction',0x4fc060:'set_grind_tweak',0x4fc180:'set_ammo_type',0x4fd140:'last_spin_was'}
functions={hex(at):{'name':'thug_physics_'+name+'_member_draft','this':True,'result':'word'} for at,name in members.items()}
cases=[];labels=[];counts=Counter();hits=Counter();callee_hits=Counter()
def trace(uc,at,size,user):hits[at]+=1
cpu.hook_add(UC_HOOK_CODE,trace,begin=0x4fbfe0,end=0x4fd1b9)
def callee(uc,at,size,user):callee_hits[hex(at)]+=1
for at in [0x476630,0x476950,0x476b40]:cpu.hook_add(UC_HOOK_CODE,callee,begin=at,end=at)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
class Graph:
 def __init__(self):self.image=bytearray(initial);self.cursor=BASE+0x9000
 def put(self,at,fmt,*values):struct.pack_into(fmt,self.image,at-BASE,*values)
 def alloc(self,n):at=self.cursor;self.cursor+=n;assert self.cursor<BASE+SIZE;return at
 def structure(self,items):
  at=self.alloc(8);nodes=[self.alloc(16) for _ in items];self.put(at,'<2I',0, nodes[0] if nodes else 0)
  for i,(name,kind,value) in enumerate(items):self.put(nodes[i],'<4I',(kind<<1)|(i&1),name,value,nodes[i+1] if i+1<len(nodes) else 0)
  return at
 def symbol(self,name,kind,value):
  at=self.alloc(20);bucket=BASE+(name&4095)*4;old=struct.unpack_from('<I',self.image,bucket-BASE)[0]
  self.put(at,'<BBH4I',0,kind,0,name,0,value,old);self.put(bucket,'<I',at)
 def patches(self):return [[BASE+i,self.image[i:i+4].hex()] for i in range(0,SIZE,4) if self.image[i:i+4]!=initial[i:i+4]]
def run(address,graph,params,extra=(),label='parameter flags',repeat=2):
 patches=graph.patches()+list(extra);expected=bytearray(initial)
 for at,data in patches:expected[at-BASE:at-BASE+len(data)//2]=bytes.fromhex(data)
 cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0x6f3624,struct.pack('<I',BASE));stages=[]
 for iteration in range(repeat):
  args=[params,rng.randrange(2**32)];sp=STACK+0x10000;cpu.mem_write(sp,struct.pack('<3I',STOP,*args))
  cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,PHYS);cpu.reg_write(UC_X86_REG_EAX,0xfeedfeed)
  guards={UC_X86_REG_EBX:0xeeeeffff,UC_X86_REG_ESI:0x1234ffff,UC_X86_REG_EDI:0xabcdefaa,UC_X86_REG_EBP:0xeebbcccc}
  for reg,value in guards.items():cpu.reg_write(reg,value)
  cpu.emu_start(address,STOP,count=100000)
  assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+12
  assert all(cpu.reg_read(reg)==v for reg,v in guards.items())
  after=bytes(cpu.mem_read(BASE,SIZE));outputs=[[BASE+i,after[i:i+4].hex()] for i in range(0,SIZE,4) if after[i:i+4]!=expected[i:i+4]]
  stages.append({'fn':hex(address),'this':PHYS,'args':args,'result':cpu.reg_read(UC_X86_REG_EAX),'outputs':outputs,'globals':[int.from_bytes(cpu.mem_read(0x6f3624,4),'little')],'callbacks':0})
  expected=bytearray(after);counts[functions[hex(address)]['name']]+=1
 cases.append({'patches':patches,'globals':[BASE],'steps':stages});labels.append(label)

for at,offset,kind in [(0x4fbfe0,0x2f0,13),(0x4fc060,0x3a8,1),(0x4fc180,0x2fc,13)]:
 for value in [0,1,0x7fffffff,0x80000000,0xffffffff,0xdeadbeef]:
  for items in [[],[(0,kind,value)],[(1,kind,value)],[(0,kind,value),(0,kind,value^0xffffffff)],[(0,kind,value),(0,4,0xdeadbeef)],[(0,4,0xdeadbeef),(0,kind,value)],[(0,2,0x3f800000)],[(0,13,0x71665544)]]:
   for previous in [0,0x12345678,0xffffffff]:
    g=Graph();g.symbol(0x71665544,1,value);params=g.structure(items)
    run(at,g,params,[patch(PHYS+offset,'<I',previous)],label=f'{members[at]}, fields {items}, old {previous:x}')
 # Real included structures and aliases are followed by the original accessors.
 for levels in [1,2,4]:
  g=Graph();nested=g.structure([(0,kind,0xdeadbeef)])
  for depth in range(levels):
   name=0x71660000+depth;g.symbol(name,10,nested);nested=g.structure([(0,13,name)])
  run(at,g,nested,label=f'{members[at]} nested depth {levels}')

patterns=[[],[(0,13,0xf649d637)],[(0xf649d637,13,0x12345678)],[(0,1,0xf649d637)],[(0,13,0x47953f00)],[(0,13,0x996d5512)],[(0,13,0x47953f00),(0,13,0x996d5512)],[(0,13,0x996d5512),(0,13,0x47953f00)]]
for at in [0x4fc040,0x4fd140]:
 for items,flip,last in itertools.product(patterns,[0,1,127,128,255],[0,1,127,128,255]):
  g=Graph();params=g.structure(items)
  run(at,g,params,[patch(STATE+0x28,'<B',flip),patch(PHYS+0x3a5,'<B',last),patch(PHYS+0x388,'<B',255)],label=f'{members[at]}, fields {items}, flipped {flip}, last {last}')
 for name in [0xf649d637,0x47953f00,0x996d5512]:
  for value in range(256):
   g=Graph();included=g.structure([(0,13,name)]);g.symbol(0x71667700,10,included);params=g.structure([(0,13,0x71667700)])
   run(at,g,params,[patch(STATE+0x28,'<B',value),patch(PHYS+0x3a5,'<B',255-value)],label=f'{members[at]} included flag {name:x}, raw boolean {value}')
blocks=(folder/'physics-command-path-instructions.txt').read_text().split('\n\n');coverage={};md=Cs(CS_ARCH_X86,CS_MODE_32)
for at in members:
 block=next(b for b in blocks if b.startswith(f'{at:08x} '));addresses=[int(line[:8],16) for line in block.splitlines()[1:] if re.match(r'^[0-9a-f]{8} ',line)]
 decoded={i.address for i in md.disasm(pe.get_data(at-0x400000,max(addresses)+3-at),at)};assert set(addresses)<=decoded
 missing=[hex(address) for address in addresses if not hits[address]];assert not missing,(hex(at),missing)
 coverage[hex(at)]={'total':len(addresses),'covered':len(addresses),'missing':[]}
scope='Five original fixed-ABI parameter commands with actual QB checksum/integer/flag lookups, missing and mistyped parameters, last match, alias and nested structures, retained calls, all byte booleans, direction priority and unchanged guards. All fixture memory, globals, return values, callee-saved registers and stack cleanup compare. Mapped terminating structures remain contracts. Isolated direct comparison only; no named integration or gameplay claim.'
fixture={'base':BASE,'memory':'physics-parameter-flags-memory.bin','globals':[['thug_script_symbol_buckets',0x6f3624,4]],'functions':functions,'float_fields':[],'cases':cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'physics-parameter-flags-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(cases),'calls':sum(counts.values()),'counts':dict(counts),'instruction_coverage':coverage,'callee_calls':dict(callee_hits),'scope':scope}
(folder/'physics-parameter-flags-original.json').write_text(json.dumps(report,indent=2)+'\n')
print('Parameter flags',len(cases),sum(counts.values()),sum(v['covered'] for v in coverage.values()),flush=True)
