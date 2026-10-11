import hashlib,json,subprocess
"""Isolated original jump steering, with real scalar lookup and SSE matrices."""
from pathlib import Path
prefix=Path('tools/verify_contact_nodes.py').read_text().split('initial=bytes(memory);')[0]
prefix=prefix.replace("out=ROOT/'local/validation/collision';report_path=out.parent/'contact-nodes.json'", "out=ROOT/'local/validation/collision';report_path=out.parent/'jump-turn.json'")
exec(compile(prefix,'<read-only fixture prerequisites>','exec'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from script_heap_oracle import ScriptHeapOracle
from unicorn.x86_const import UC_X86_REG_FPSW,UC_X86_REG_FPTAG,UC_X86_REG_MXCSR
import math
def bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]
PHYS=alloc(0x1540);BODY=alloc(0x300);INPUT=alloc(0x300)
CONTEXT=alloc(32);MANAGER=alloc(0x500);LOG=alloc(512);HEAP=alloc(256)
put(CONTEXT,'<8I',HEAP,HEAP+256,0,LOG,BASE,BASE+len(memory),0,0)
put(PHYS+12,'<I',BODY);put(PHYS+0x150c,'<I',INPUT)
symbol(0x38505ef3,2,bits(15));PARAM=word(BASE+(0x38505ef3&4095)*4)
identity=[1. if i%5==0 else 0. for i in range(16)]
put(BODY+0x6c,'<16f',*identity);put(PHYS+0x18,'<16f',*identity)
put(BODY+0xac,'<4f',100,7,200,1);put(INPUT+0x60,'<B',0);put(INPUT+0x80,'<B',0)
globals_=[['thug_script_symbol_buckets',0x6f3624,4]]
functions={'0x5002d0':{'name':'thug_skater_jump_turn','this':True,'result':'void','cleanup':0}}
initial=bytes(memory);oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,[BASE],functions,observe=[0x478f00,0x404e20,0x5df4ac])
oracle.setword(0x684fe4,0x5df4ac);hits=Counter();labels=[]
def trace(cpu,at,size,user):hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=0x5002d0,end=0x500392)
def case(left,right,value=15,velocity=(100,7,200,1),basis=None,cached=None,kind=2,extra=(),label='jump steering'):
 oracle.cpu.reg_write(UC_X86_REG_FPSW,0);oracle.cpu.reg_write(UC_X86_REG_FPTAG,0xffff);oracle.cpu.reg_write(UC_X86_REG_MXCSR,0x1f80)
 p=[patch(INPUT+0x60,'<B',left),patch(INPUT+0x80,'<B',right),patch(PARAM+1,'<B',kind),patch(PARAM+12,'<I',bits(value) if kind==2 else value&0xffffffff),patch(BODY+0xac,'<4f',*velocity)]
 if basis is not None:p.append(patch(BODY+0x6c,'<16f',*basis))
 if cached is not None:p.append(patch(PHYS+0x18,'<16f',*cached))
 oracle.case([(0x5002d0,PHYS,[])]*2,p+list(extra));labels.append(label)
for left,right in [(0,0),(1,0),(0,1),(1,1),(255,0),(0,128),(2,255)]:
 for angle in [0.,-0.,15.,-15.,90.,-180.,.000001,10000.,1e6]:
  case(left,right,angle,label='button priority, nonboolean flags and finite angles')
for kind,values in [(1,[0,1,-1,16777217,2147483647,-2147483648]),(2,[0.125,-.5,1e-35,-1e-35])]:
 for value in values:
  for left,right in [(1,0),(0,1)]:case(left,right,value,kind=kind,label='real integer FILD or float parameter, unspilled product')
for _ in range(60):
 case(rng.choice([1,255]),rng.choice([0,1]),rng.uniform(-400,400),
      tuple(rng.uniform(-1000,1000) for _ in range(4)),
      [rng.uniform(-2,2) for _ in range(16)],[rng.uniform(-2,2) for _ in range(16)],
      label='independent non-orthogonal bases and retained velocity')
for vector in [(0.,-0.,-0.,1.),(-0.,0.,0.,-0.),(1e-38,7,-1e-38,1),(1e30,-17,-1e30,1)]:
 for value in [0.,-0.,15.,-90.]:case(1,1,value,vector,label='velocity numeric lanes and unchanged vertical/padding')
case(0,0,extra=[patch(BASE+(0x38505ef3&4095)*4,'<I',0)],label='no held inputs returns before required parameter lookup')
pe=load();decoder=Cs(CS_ARCH_X86,CS_MODE_32);rows=list(decoder.disasm(pe.get_data(0x1002d0,195),0x5002d0))
missing=[f'{i.address:08x}' for i in rows if not hits[i.address]]
assert len(rows)==70 and not missing
scope='Complete5002d0 jump-direction steering: left-input priority, real integer/float global parameter lookup, horizontal velocity rotation and separate owner/cache SSE basis premultiplication. Finite and signed-zero inputs, tiny/large velocities, nonboolean flags, no-input early return, independent non-orthogonal matrices and retained calls. Exact memory and globals;70/70instructions; no NaN allowances. Existing x87 transcendental adapter limits apply. Integrated into the main module; complete playable-level integration remains unfinished.'
fixture={'base':BASE,'memory':'jump-turn-memory.bin','globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'scope':scope}
(out/'jump-turn-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')));(out/fixture['memory']).write_bytes(initial)
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'counts':dict(oracle.counts),'instruction_coverage':{'total':len(rows),'covered':len(rows),'missing':missing},'callee_coverage':dict(oracle.coverage),'scope':scope}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('Original jump turn',len(labels),sum(oracle.counts.values()),report['instruction_coverage'],flush=True)

subprocess.run(['node',str(ROOT/'tools/verify_jump_turn_wasm.mjs')],check=True)
report['result']='pass';report['wasm_sha256']=hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest()
report['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}
report['artifact_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'jump-turn-fixtures.json',out/fixture['memory']]}
(out.parent/'jump-turn.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS jump-turn',len(fixture['cases']),sum(oracle.counts.values()))
