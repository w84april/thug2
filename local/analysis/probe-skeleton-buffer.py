"""Execute original skeleton parsing/lifetime and quaternion matrix instructions."""
import hashlib,json,math,random,struct
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/analysis';rng=random.Random(0x4a39c0)
BASE,SIZE=0x1800000,0x100000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
OBJ,Q,T,OUT,DATA,LOG,HEAP=BASE+0x8000,BASE+0x9000,BASE+0x9200,BASE+0x9400,BASE+0x10000,BASE+0x40000,BASE+0x60000
initial=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,initial,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200)
initial=bytes(initial)
functions={
 '0x463aa0':{'name':'thug_quaternion_translation_matrix_draft','this':False,'result':'word','cleanup':0},
 '0x4a2c20':{'name':'thug_skeleton_initialize_draft','result':'word','cleanup':0},
 '0x4a3950':{'name':'thug_skeleton_destroy_draft','result':'word','cleanup':4,'memory':True},
 '0x4a39c0':{'name':'thug_skeleton_parse_draft','result':'byte','cleanup':12,'memory':True}}
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,[],[],functions,observe=[0x463aa0,0x416df0,0x5df4ac])
# Same recovered SSE implementation selected in the browser; dispatcher CPU
# detection is outside this already-initialized internal loading contract.
oracle.setword(0x684fe4,0x5df4ac)
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32);hits=Counter();saved={}
instructions={a:list(md.disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x463aa0,248),(0x4a2c20,42),(0x4a3950,98),(0x4a39c0,876)]}
registers=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
def trace(cpu,at,size,user):
    hits[at]+=1
    for fn,insns in instructions.items():
        if at==fn:saved[fn]=[cpu.reg_read(r) for r in registers]
        if at==insns[-1].address:assert saved[fn]==[cpu.reg_read(r) for r in registers],hex(fn)
for a,insns in instructions.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=a,end=insns[-1].address)
labels=[];files=[]
def run(calls,patches,label):
    result=oracle.case(calls,patches);labels.append(label);return result

# Constructor preserves every unspecified byte, including +590.
run([(0x4a2c20,OBJ,[])]*2,[], 'constructor retains unspecified storage')
for flags in [0,1,2,3,0x100,0xffffffff]:
    for mask in range(4):
        run([(0x4a3950,OBJ,[flags])]*2,
            [patch(OBJ+0x58c,'<2I',DATA if mask&1 else 0,DATA+0x100 if mask&2 else 0)],
            f'destruction flags{flags:x} buffers{mask}')

# All original loose skeletons, including the 34-bone training prop. Full input
# bytes and checksums are retained; inputs must remain unchanged by parsing.
def parse(data,label,at=DATA,repeat=1):
    count=struct.unpack_from('<I',data,8)[0];assert count<=64 and len(data)==12+count*44
    p=[[at,data.hex()],patch(OBJ+0x590,'<I',0)]
    calls=[]
    if at==DATA:calls.append((0x4a2c20,OBJ,[]))
    for _ in range(repeat):calls.extend([(0x4a39c0,OBJ,[at,len(data),1]),(0x4a3950,OBJ,[0])])
    result=run(calls,p,label)
    if at!=DATA:
        # Aliased object writes can corrupt later quaternion inputs, yielding
        # arithmetic NaNs. Only computed matrix lanes (and their release-log
        # snapshots) accept NaN classification; raw file/translation bits do not.
        typed=[HEAP+i*64+j*4 for i in range(count) for j in [0,1,2,4,5,6,8,9,10,12,13,14]]
        typed += [LOG+2*48+16+j*4 for j in [0,1,2]]
        for stage in result:stage['float_fields']=typed
    if at==DATA:assert bytes(oracle.cpu.mem_read(at,len(data)))==data
    return result
for path in sorted((ROOT/'local/game-files/Game/Data').rglob('*.ske.xbx')):
    data=path.read_bytes();count=struct.unpack_from('<I',data,8)[0]
    parse(data,str(path.relative_to(ROOT)),repeat=2)
    files.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'bones':count})

def make(count,mode):
    names=[0x71710000+i for i in range(count)]
    if mode=='duplicate':names=[0x71710000+(i%3) for i in range(count)]
    parents=[names[rng.randrange(i)] if i else 0 for i in range(count)]
    if mode=='missing':parents=[0xeeeeeeee]*count
    if mode=='future' and count:parents=[names[-1]]*count
    mirrors=[0]*count
    if mode=='cross':mirrors=[names[count-1-i] for i in range(count)]
    if mode=='missing':mirrors=[0xfefefefe]*count
    if mode=='overwrite':mirrors=[names[0] if i%2 else 0 for i in range(count)]
    if mode=='duplicate':mirrors=names[:]
    out=bytearray(struct.pack('<3I',rng.getrandbits(32),rng.getrandbits(32),count))
    for values in [names,parents,mirrors]:out.extend(struct.pack('<'+'I'*count,*values))
    for i in range(count):
        q=[rng.uniform(-1,1) for _ in range(4)];length=math.sqrt(sum(v*v for v in q));q=[v/length for v in q]
        out.extend(struct.pack('<8f',*q,*[rng.uniform(-500,500) for _ in range(3)],rng.choice([0,1,-1])))
    return bytes(out)
for count in [0,1,2,3,17,63,64]:
    for mode in ['chain','cross','missing','future','overwrite','duplicate']:
        parse(make(count,mode),f'synthetic {count}/{mode}')
# File data can overlap object storage: retain forward-copy and live-field order.
for count in [0,1,3,17,64]:parse(make(count,'cross'),f'in-place object/file {count}',at=OBJ-4)

# The helper mutates its quaternion, permits overlapping inputs/output and
# copies translation bits after basis stores. No JavaScript float arguments.
values=[[0,0,0,1],[1,0,0,0],[-0.0,0,-0.0,-1],
        [2**-120,-2**-100,2**-70,2**100],[2**70,-2**80,2**60,2**-100]]
values += [[rng.uniform(-3,3) for _ in range(4)] for _ in range(60)]
for i,q in enumerate(values):
    for off in [None,0,4,12,-4]:
        out=OUT if off is None else Q+off
        run([(0x463aa0,0,[Q,T,out])],
            [patch(Q,'<4f',*q),patch(T,'<4I',0x3fa00000,0xff812345,0x80000000,0x7f812345)],
            f'matrix {i}, quaternion overlap {off}')
for off in [-48,-44,-40,0,4,12,48,52]:
    run([(0x463aa0,0,[Q,OUT+off,OUT])],
        [patch(Q,'<4f',.1,.2,.3,.4),patch(OUT+off,'<4I',0x7f812345,0x80000000,0xff812345,0x7fffffff)],
        f'translation overlap {off}')

coverage={hex(a):{'total':len(insns),'covered':sum(bool(hits[i.address]) for i in insns),
                 'missing':[hex(i.address) for i in insns if not hits[i.address]]} for a,insns in instructions.items()}
excluded={'0x4a3a4c':'allocator already initialized by the host contract',
          '0x4a3a76':'allocator already initialized by the host contract',
          '0x4a3ced':'unreachable alignment instruction: both loop edges target 004a3cf0'}
assert {a for c in coverage.values() for a in c['missing']}==set(excluded)
coverage['0x4a39c0']['excluded']=excluded
scope='Four recovered original routines: skeleton constructor, destructor, full buffer parser and mutating quaternion/translation matrix conversion. All 58 loose game skeletons are parsed twice with lifetime checks, including CS_Cardboard used by TR_startup, with exact arithmetic bits. Original callees execute; all arena bytes, heap records, return values and preserved registers are compared. Complete buffers with 0..64 bones, initialized allocator, successful allocations and selected SSE matrix backend form the internal contract; external file validation/loading and actual LoadSkeleton command are not yet implemented. Only computed matrix NaNs from deliberately overlapping object/file buffers use classification; raw file/translation NaN payloads remain exact.'
fixture={'base':BASE,'memory':'skeleton-buffer-memory.bin','memory_adapter':ADAPTER,
 'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':[],'functions':functions,'float_fields':[],
 'pointer_exports':[[0x649f48,'thug_skeleton_methods_draft']],
 'pointer_fields':[OBJ,*[LOG+i*48+16 for i in range(30)]],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial)
(folder/'skeleton-buffer-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),
 'instruction_coverage':coverage,'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'assets':files,'scope':scope}
(folder/'skeleton-buffer-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['scope','assets','callee_calls','heap_events']}),flush=True)
