"""Original random-range value decoding, both streams and PC24 arithmetic."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_FPCW
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'script-ranges.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP=0x1800000,4096,0x3000000,0x3f00000
PROGRAM,OUTPUT=BASE+0x103,BASE+0x200;rng=random.Random(0x46fbd0)
initial=b'\xad'*SIZE;(out/'script-ranges-memory.bin').write_bytes(initial)
globals_=[['thug_random_state',0x690fd4+i*4,4,i*4] for i in range(3)]
globals_ += [['thug_random_alternate_state',0x690fc8+i*4,4,i*4] for i in range(3)]
functions={'0x46fbd0':{'name':'thug_script_random_value','this':False,'result':'word'}}
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cases=[];types=Counter();coverage=Counter()
def observe(cpu,address,size,user):coverage[hex(address)]+=1
for a in [0x6236fc,0x403de0,0x403e30]:cpu.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
def case(a,b,selector,tag=0xa5,destination=OUTPUT,repeat=1):
    expected=bytearray(initial);expected[destination-BASE]=tag
    struct.pack_into('<BII',expected,PROGRAM-BASE,0x1f,a,b)
    cpu.mem_write(BASE,bytes(expected));values=[rng.randrange(2**32) for _ in globals_]
    for g,v in zip(globals_,values):cpu.mem_write(g[1],struct.pack('<I',v))
    patches=[[BASE+i,expected[i:i+4].hex()] for i in range(0,SIZE,4) if expected[i:i+4]!=initial[i:i+4]]
    stages=[]
    for _ in range(repeat):
        sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<II',STOP,destination))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_EAX,PROGRAM)
        cpu.reg_write(UC_X86_REG_EBX,selector);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
        cpu.emu_start(0x46fbd0,STOP,count=100000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4
        after=bytes(cpu.mem_read(BASE,SIZE));kind=after[destination-BASE]>>1;types[kind]+=1
        assert kind in [1,2]
        outputs=[[BASE+i,after[i:i+4].hex()] for i in range(0,SIZE,4) if after[i:i+4]!=expected[i:i+4]]
        stages.append({'fn':'0x46fbd0','this':0,'args':[PROGRAM,destination,selector],
            'result':cpu.reg_read(UC_X86_REG_EAX),'outputs':outputs,'globals':[int.from_bytes(cpu.mem_read(g[1],4),'little') for g in globals_],
            'callbacks':0,'float_fields':[destination+8] if kind==2 else []})
        expected=bytearray(after)
    cases.append({'patches':patches,'globals':values,'steps':stages})
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
edge=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,
      0x7f800000,0xff800000,0x7f812345,0xff812345,0x7fc34567,0xffc34567]
for value in [-2147483648,-16777217,-2,-1,-0.1,-0.00001,0.00001,0.1,1,2,16777217,2147483648,2**32,2**63]:
    word=bits(value);edge.extend([(word-1)&0xffffffff,word,(word+1)&0xffffffff])
for i,a in enumerate(edge):
    for j,b in enumerate(edge):
        case(a,b,[0,1,0x100,0xff0000ff][(i+j)%4],tag=(i+j)%256)
for i in range(1024):case(rng.randrange(2**32),rng.randrange(2**32),rng.randrange(2**32),tag=rng.randrange(256))
for destination in [PROGRAM-8,PROGRAM-3,PROGRAM,PROGRAM+1,OUTPUT]:
    for a,b in [(bits(-5),bits(5)),(bits(1.25),bits(9.75)),(0x7fc34567,0x7f812345),(0xff7fffff,0x7f7fffff)]:
        for selector in [0,1,0x100,0x101]:case(a,b,selector,destination=destination)
# Every real training random-range occurrence, both stream selectors and repeated
# calls. Preserve its original endpoint words, with fresh PRNG states per case.
token_fixture=json.loads((out/'script-tokens-fixtures.json').read_text());token_bytes=(out/token_fixture['memory']).read_bytes()
real=[]
for fn,p,next_p in token_fixture['cases']:
    offset=p-token_fixture['base']
    if fn!='0x46f690' or token_bytes[offset] not in [0x30,0x38]:continue
    asset=next((a for a in token_fixture['assets'] if a['address']<=p<a['address']+a['size']),None)
    if not asset:continue
    assert token_bytes[offset+1]==0x1f
    a,b=struct.unpack_from('<II',token_bytes,offset+2)
    real.append({'member':asset['member'],'offset':p-asset['address'],'token':token_bytes[offset],'endpoints':[a,b]})
    for selector in [0,1]:case(a,b,selector,repeat=16)
scope='Original random-range value decoder and both original PRNG callees, including the real CRT float-to-int helper. PC24 arithmetic with wider intermediate exponent; signed inclusive integer ranges, 0.1 conversion bias, unordered comparisons, swapped endpoints, selector low-byte behavior, overlapping source/output and all 19 training-script range occurrences. Exact integers/state/preserved bytes and finite float bits; only typed float NaNs compare by classification. Running-game FPU state and x87 exception flags remain unverified.'
fixture={'base':BASE,'memory':'script-ranges-memory.bin','functions':functions,'globals':globals_,'float_fields':[],
 'cases':cases,'scope':scope}
path=out/'script-ranges-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(cases),'cases',dict(types),'callee calls',dict(coverage),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_ranges_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'cases':len(cases),'types':dict(types),'callee_coverage':dict(coverage),
 'real_range_occurrences':real,'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-ranges-memory.bin']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',len(cases),'cases')
