"""Original jump/random-token resolution, including its complete cache chain.

Only pool/heap services are platform boundaries; the original functions and PRNGs
execute unchanged. This suite uses the PC heap route with successful allocations.
"""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP,UC_X86_REG_EBX,UC_X86_REG_EDI,UC_X86_REG_ESI
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'script-branches.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP=0x1800000,0x20000,0x3000000,0x3f00000
CONTEXT,ADAPTER,PROGRAM,NODES,LOG,HEAP=BASE+0x20,BASE+0x40,BASE+0x1000,BASE+0x3000,BASE+0x6000,BASE+0x9000
memory=bytearray(b'\xad'*0x18000);rng=random.Random(0x470c60)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<4I',HEAP,BASE+0x17800,0,LOG);put(ADAPTER,'<4I',CONTEXT,0,0,0)
for i in range(100):
    at=NODES+i*96;put(at,'<2IHHI',0,PROGRAM,2,0,0x40);put(at+0x10,'<H',0)
    put(at+0x12,'<2B',0,1);put(at+0x54,'<3I',0,at+96 if i<99 else 0,at-96 if i else 0)
initial=bytes(memory);(out/'script-branches-memory.bin').write_bytes(initial)
globals_=[['thug_random_state',0x690fd4+i*4,4,i*4] for i in range(3)]
globals_ += [['thug_random_alternate_state',0x690fc8+i*4,4,i*4] for i in range(3)]
globals_ += [['thug_current_script',0x6f3530,4],['thug_script_branch_first',0x6f2358,4],
             ['thug_script_branch_last',0x6f235c,4],['thug_script_branch_count',0x6f2360,4]]
defaults=[0x12345678,0x98765432,0x31415926,0x12345678,0x98765432,0x31415926,BASE+0x100,0,0,0]
functions={
 '0x403de0':{'name':'thug_random_range','this':False,'result':'word','cleanup':0},
 '0x403e30':{'name':'thug_random_alternate_range','this':False,'result':'word','cleanup':0},
 '0x46f7a0':{'name':'thug_script_branch_find','this':False,'result':'word','cleanup':0,'register_args':True},
 '0x46f8a0':{'name':'thug_script_branch_shuffle','this':True,'result':'void','cleanup':4},
 '0x470bb0':{'name':'thug_script_branch_allocate','this':False,'result':'word','cleanup':0,'memory':True},
 '0x470c60':{'name':'thug_script_resolve_branches','this':False,'result':'word','cleanup':0,'memory':True}}
pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
cpu.mem_write(0x6f2578,bytes(4));cpu.mem_write(0x6f2580,bytes(8));cpu.mem_write(0x7cc979,b'\1')
cpu.mem_write(0x7d1800,struct.pack('<I',BASE+0x200))
cases=[];counts=Counter();coverage=Counter();allocation_events=Counter()
def word(at):return struct.unpack('<I',cpu.mem_read(at,4))[0]
def setword(at,value):cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
def heap(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP);log=word(CONTEXT+12)+word(CONTEXT+8)*16;setword(CONTEXT+8,word(CONTEXT+8)+1)
    if address==0x5bafc0:
        size=word(sp+4);assert size==96 and word(sp+8)==1 and word(sp+12)==0
        pointer=word(CONTEXT);assert pointer+size+16<=word(CONTEXT+4);setword(CONTEXT,pointer+size+16)
        uc.mem_write(pointer,b'\xa5'*size);uc.mem_write(log,struct.pack('<4I',1,size,1,pointer))
        uc.reg_write(UC_X86_REG_EAX,pointer);cleanup=12;allocation_events['allocations']+=1
    else:
        uc.mem_write(log,struct.pack('<4I',2,word(sp+4),0,0));cleanup=4;allocation_events['releases']+=1
    uc.reg_write(UC_X86_REG_EIP,word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x5bafc0,0x5baba0]:cpu.hook_add(UC_HOOK_CODE,heap,begin=at,end=at)
def observe(uc,address,size,user):coverage[hex(address)]+=1
for at in [0x403de0,0x403e30,0x46f7a0,0x46f8a0,0x470bb0,0x470070,0x4728c0]:cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)

def case(calls,patches=(),changes=None):
    expected=bytearray(initial);values=list(defaults)
    for k,value in (changes or {}).items():values[k]=value
    for at,text in patches:
        data=bytes.fromhex(text);expected[at-BASE:at-BASE+len(data)]=data
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0,b'\xa5'*4)
    for entry,value in zip(globals_,values):setword(entry[1],value)
    stages=[]
    for fn,this,args in calls:
        f=functions[hex(fn)];stack_args=[] if f.get('register_args') else args
        sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(stack_args)+1),STOP,*stack_args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad)
        if f.get('register_args'):
            for reg,value in zip([UC_X86_REG_EBX,UC_X86_REG_EDI,UC_X86_REG_ESI],args):cpu.reg_write(reg,value)
        cpu.emu_start(fn,STOP,count=2000000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+f['cleanup'],(len(cases),hex(fn))
        assert bytes(cpu.mem_read(0,4))==b'\xa5'*4
        after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
        if after!=expected:
            for i in range(0,len(initial),4):
                if after[i:i+4]!=expected[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
        expected=bytearray(after)
        result=cpu.reg_read(UC_X86_REG_EAX) if f['result']=='word' else None
        stages.append({'fn':hex(fn),'this':this,'args':args,'result':result,'outputs':outputs,
                       'globals':[word(g[1]) for g in globals_],'callbacks':0})
        counts[f['name']]+=1
    cases.append({'patches':list(patches),'globals':values,'steps':stages});return stages

# Exact PRNG state/output, arbitrary 32-bit seeds and limits, both streams.
for i in range(1024):
    limit=[0,1,2,3,64,32767,32768,65535,65536,0x7fffffff,0x80000000,0xffffffff][i%12] if i<240 else rng.randrange(2**32)
    changes={j:rng.randrange(2**32) for j in range(6)}
    case([(0x403de0,0,[limit]),(0x403e30,0,[limit])],changes=changes)
case([(fn,0,[rng.randrange(1,65)]) for _ in range(128) for fn in [0x403de0,0x403e30]])

# Cache matches must include all keys, current ownership or owner zero.
for i in range(256):
    offsets=PROGRAM+(i%4);kind=[0x40,0x41,0,0xffffffff][(i//4)%4];count=[0,1,2,3,65535,65536,0x10002][(i//16)%7]
    p=[patch(NODES,'<I',0 if i&128 else BASE+0x100),patch(NODES+96,'<I',BASE+0x200),
       patch(NODES+2*96,'<I',0),patch(NODES+2*96+0x58,'<I',0)]
    case([(0x46f7a0,0,[offsets,kind,count])],p,{7:NODES,8:NODES+192,9:3})

# Direct shuffle, including preserved unused bytes and cycle-boundary swap.
for count in [0,1,2,3,8,16,32,64]:
    for i in range(16):
        order=list(range(66));rng.shuffle(order)
        p=[patch(NODES+8,'<H',count),patch(NODES+0x12,'<66B',*order)]
        case([(0x46f8a0,NODES,[0 if count<2 else i%2])],p,{j:rng.randrange(2**32) for j in range(3)})

# Allocate through empty/nonempty lists and at the eviction boundary. The
# allocator routes are adapters; record eviction order, counts and preserved data.
for n in [0,1,2,98,99,100]:
    for repeats in [1,3,8]:
        p=[] if not n else [patch(NODES+(n-1)*96+0x58,'<I',0)]
        case([(0x470bb0,0,[])]*repeats,p,{7:NODES if n else 0,8:NODES+(n-1)*96 if n else 0,9:n})

def branch(token,weights,at=PROGRAM):
    count=len(weights);data=bytearray(5+count*6+count*8)
    struct.pack_into('<BI',data,0,token,count);struct.pack_into('<'+'h'*count,data,5,*weights)
    for i in range(count):
        offset=5+count*2+i*4;target=5+count*6+i*8
        struct.pack_into('<I',data,offset,target-offset-4);data[target]=0x16
        struct.pack_into('<I',data,target+1,0xabcdef00+i)
    return [at,data.hex()]

# Ordinary tokens do not advance. Long/short jumps may chain or jump backward.
for token in range(256):
    if token not in [0x2e,0x2f,0x37,0x40,0x41,0x49]:
        assert case([(0x470c60,0,[PROGRAM])],[patch(PROGRAM,'<B',token)])[0]['result']==PROGRAM
for i in range(128):
    first=PROGRAM+(i%4);middle=PROGRAM+64;last=PROGRAM+32
    p=[patch(first,'<BI',0x2e,middle-first-5),patch(middle,'<BI',0x2e,(last-middle-5)&0xffffffff),patch(last,'<BH',0x49,3),patch(last+4,'<B',1)]
    assert case([(0x470c60,0,[first])],p)[0]['result']==last+4

weights_list=[[1],[1,1],[0,1],[1,0],[1,2,3],[0,0,5],[-1,3],[100,-50,100],[32767]]
for token in [0x2f,0x37]:
    for weights in weights_list:
        for i in range(8):
            case([(0x470c60,0,[PROGRAM])]*4,[branch(token,weights)],{j:rng.randrange(2**32) for j in range(6)})

# Cached random-no-repeat and shuffled choices, including first allocation,
# repeated visits, script ownership and oldest-record eviction.
for token in [0x40,0x41]:
    for count in ([1,2,3,8,16,64] if token==0x40 else [2,3,8,16,64]):
        for i in range(8):
            p=[branch(token,[1]*count)]
            changes={j:rng.randrange(2**32) for j in range(3)}
            if i>=4:
                p += [patch(NODES+4,'<I',PROGRAM+5+count*2),patch(NODES+8,'<H',count),patch(NODES+12,'<I',token),
                      patch(NODES,'<I',[0,BASE+0x100,BASE+0x200,0][i-4]),patch(NODES+0x12,'<66B',*(list(range(count))+[0]*(66-count)))]
                changes.update({7:NODES,8:NODES+99*96,9:100})
            case([(0x470c60,0,[PROGRAM])]*(count+3),p,changes)
# Jump -> weighted selection -> cached selection, and cache keys differing only
# by script ownership. The selected destination remains original bytecode.
p=[branch(0x2f,[1]),branch(0x40,[1,1,1],PROGRAM+128),patch(PROGRAM+7,'<I',128-11)]
case([(0x470c60,0,[PROGRAM])]*12,p)

scope='Original jump and random-token resolver with both PRNG streams, cache lookup/allocation/eviction and shuffle. Valid terminating constructed bytecode; real internal callees, platform heap services instrumented. No QB file parser, token command execution, or complete skating loop.'
fixture={'base':BASE,'memory':'script-branches-memory.bin','memory_adapter':ADAPTER,'globals':globals_,'functions':functions,
         'float_fields':[],'cases':cases,'scope':scope}
path=out/'script-branches-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-branch-memory.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=33554432',str(ROOT/'tools/script_branch_memory.c'),'-o',str(adapter)],check=True)
print('x86 complete:',dict(counts),dict(allocation_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_branches_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'heap_events':dict(allocation_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-branches-memory.bin',adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
