"""Original controller packets, button edges, axes and suppression deadlines."""
import hashlib,itertools,json,random,struct
from pathlib import Path
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
p=ROOT/'local/analysis';BASE=0x1800000;SIZE=0x10000;PAD=BASE+0x1000;PACKET=BASE+0x2000;TEXT=BASE+0x3000
memory=bytearray(SIZE);functions={};coverage={};hits=Counter();labels=[]
specs=[(0x46b800,23,'button_name',1,'void',True),(0x57b620,10,'button_deadline',1,'void',True),
 (0x46b820,144,'button_pressure',1,'void',True),(0x46b8b0,67,'button_force',1,'void',True),
 (0x46b940,262,'pad_construct',0,'word',True),(0x46bb50,258,'pad_clear',0,'void',True),
 (0x46bc60,316,'pad_reset',0,'void',True),(0x46ba80,202,'pad_direction',4,'double',False),
 (0x46bda0,1229,'pad_update',1,'void',True)]
cs=Cs(CS_ARCH_X86,CS_MODE_32);pe=load()
for at,n,name,argc,result,this in specs:
 functions[hex(at)]={'name':'thug_input_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0}
 coverage[at]=list(cs.disasm(pe.get_data(at-0x400000,n),at))
globals_=[];defaults=[]
bits=lambda v:struct.unpack('<I',struct.pack('<f',v))[0]
def glob(name,at,value,offset=0):globals_.append([name,at,4,offset]);defaults.append(value)
for name,at,value in [('thug_frame_counter',0x7d1ec8,1000),('thug_frame_rate',0x684fd0,bits(1000)),
 ('thug_timer_origin',0x696d64,0),('thug_time_scale',0x67d7c0,bits(1)),('thug_timer_offset',0x696d60,0),
 ('thug_input_direction_initialized_draft',0x6f22b0,0)]:glob(name,at,value)
for i in range(16):glob('thug_input_direction_angles_draft',0x6f2270+4*i,0,4*i)
oracle=ScriptHeapOracle(memory,BASE,BASE+0x20,BASE+0x100,globals_,defaults,functions)
def trace(cpu,at,size,user):hits[at]+=1
for at,code in coverage.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=at,end=code[-1].address)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def call(fn,args=(),this=PAD):return (fn,this,list(args))
def case(calls,patches=(),changes=None,label='input'):
 for reg,value in [(UC_X86_REG_FPSW,0),(UC_X86_REG_FPTAG,0xffff),(UC_X86_REG_MXCSR,0x1f80)]:oracle.cpu.reg_write(reg,value)
 try:result=oracle.case(calls,patches,changes)
 except Exception:print('FAILED',label,flush=True);raise
 labels.append(label);return result
def state(fill=0,pressed=0,deadline=0):
 data=bytearray(bytes([fill])*0x238)
 for off in range(0,0x200,0x20):
  data[off]=pressed;struct.pack_into('<I',data,off+0x1c,deadline)
 return [PAD,data.hex()]
def packet(axes=(128,128,128,128),directions=0,flags=0):
 data=bytearray(32);data[:4]=bytes(axes);data[0x12:0x16]=bytes(axes)
 for i,offset in enumerate([6,7,5,4]):data[offset]=bool(directions&(1<<i))
 struct.pack_into('<I',data,28,flags);return data
for raw in [b'UP',b'up',b'Path/To\\Pad',b'',bytes(range(1,256))]:
 case([call(0x46b800,[TEXT])],[[TEXT,(raw+b'\0').hex()],state(0xa5)],label='button name '+str(raw[:16]))
for value in [0,0x80000000,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xffffffff,bits(1000)]:
 case([call(0x57b620,[value])],[state(0xa5)],label='raw deadline bits')
for pressed,pressure,deadline in itertools.product([0,1,255],[-2147483648,-1,0,64,65,255,2147483647],
 [0,0x80000000,bits(-1),bits(999),bits(1000),bits(1001),0x7f800000,0xff800000,0x7fc12345]):
 case([call(0x46b820,[pressure&0xffffffff])]*2,[state(0xa5,pressed,deadline)],label=f'pressure/{pressed}/{pressure}/{deadline:x}')
for pressed,value in itertools.product([0,1,255],[0,1,255,256,257,0xffffffff]):
 case([call(0x46b8b0,[value])]*2,[state(0xa5,pressed,bits(2000))],label=f'force/{pressed}/{value}')
for fill,pressed in itertools.product([0,0xa5,255],[0,1,255]):
 case([call(0x46b940),call(0x46bb50),call(0x46bc60),call(0x46bc60)],
  [state(fill,pressed,bits(2000))],label='construction clear reset preserve unused bytes')
for init in [0,1,0x80000000,0xffffffff]:
 for flags in range(16):
  args=[(flags>>i)&1 for i in range(4)]
  case([call(0x46ba80,args),call(0x46ba80,[a+256 for a in args])],changes={5:init},label=f'direction/{init}/{flags}')
# Every possible raw axis byte plus digital combinations; exact outputs include
# signed zero atan2, centered sticks and the original non-clamped normalization.
for value in range(256):
 data=packet((value,255-value,(value*37)%256,(value*73)%256))
 for i in range(4,16):data[i]=(value+i)%256
 case([call(0x46b940),call(0x46bda0,[PACKET])]*2,[state(),[PACKET,data.hex()]],label=f'axis byte/{value}')
for flags in range(16):
 case([call(0x46bda0,[PACKET])],[state(0xa5),[PACKET,packet(directions=flags,flags=0x700).hex()]],label=f'digital fallback/{flags}')
for position in range(4,16):
 for value in [0,1,64,65,255]:
  data=packet();data[position]=value
  case([call(0x46bda0,[PACKET]),call(0x46bb50)],[state(),[PACKET,data.hex()]],label=f'packet button/{position}/{value}')
for flags in [0,0x100,0x200,0x400,0x700,0xffffffff]:
 case([call(0x46bda0,[PACKET])],[state(),[PACKET,packet(flags=flags).hex()]],label=f'packet flags/{flags}')
for now,deadline,axes in itertools.product([0,1,999,1000,1001,0x7fffffff,0x80000000,0xffffffff],
 [1,1000,1001,0x7fffffff,0x80000000,0xffffffff],[(128,128,128,128),(128,128,128,0),(128,128,128,255),(128,128,0,128),(128,128,255,0)]):
 case([call(0x46bda0,[PACKET])],[state(),patch(PAD+0x230,'<2I',deadline,deadline),[PACKET,packet(axes).hex()]],{0:now},f'axis deadlines/{now}/{deadline}/{axes}')
rng=random.Random(0x46bda0)
for i in range(100):
 data=bytes(rng.randrange(256) for _ in range(32));at=PAD+rng.choice([0,0x80,0x180,0x200]) if i<30 else PACKET
 case([call(0x46bda0,[at]),call(0x46bc60)],[state(0xa5,i%3,0),[at,data.hex()]],
  {0:rng.getrandbits(32),2:rng.getrandbits(32),4:rng.getrandbits(32)},f'alias/random/{i}')
scope='Nine complete original controller-pad routines: naming, raw suppression deadline, pressure/forced edges, construction, clear/reset, digital direction table and full32-byte packet update. All arena bytes and globals compare exactly; no NaN/bit masks. Raw packet input is the platform boundary, not a Windows input driver, live browser controls or complete skater startup. Existing libm atan2 adapter does not claim physical x87 transcendental accuracy. Reset retains the original duplicated stick-edge clear calls.'
fixture={'base':BASE,'memory':'input-pad-memory.bin','globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
(p/fixture['memory']).write_bytes(memory);(p/'input-pad-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'counts':dict(oracle.counts),'instruction_coverage':{hex(at):{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code),
 'missing':[hex(i.address) for i in code if not hits[i.address]],'excluded':{}} for at,code in coverage.items()},'scope':scope}
(p/'input-pad-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
