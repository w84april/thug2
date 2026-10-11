"""Original-instruction oracle for script copying, interning and merging.

All concrete script callees run. Only successful heap allocation, release and
temporary-heap scopes are instrumented. Full fixture memory (including padding,
source graphs and allocation-time snapshots) is compared with WebAssembly.
"""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'script-copy.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP=0x1800000,0x40000,0x3000000,0x3f00000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
POOL,TABLE,LOG,HEAP=BASE+0x10000,BASE+0x14000,BASE+0x18000,BASE+0x28000
memory=bytearray(b'\xad'*SIZE);cursor=0x400;rng=random.Random(0x4773e0)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xf000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200)
def text(data):
    at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def component(kind,value,name=0,length=0):
    at=alloc(16);put(at,'<BBHIII',kind*2+(at&4!=0),0x75,length,name,value,0);return at
def structure(entries):
    at=alloc(8);nodes=[component(kind,value,name,17 if kind==7 else 0x9876) for name,kind,value in entries]
    put(at+4,'<I',nodes[0] if nodes else 0)
    for i,node in enumerate(nodes):put(node+12,'<I',nodes[i+1] if i+1<len(nodes) else 0)
    return at,nodes
def array(kind,values):
    at=alloc(12);put(at,'<BBHII',0x57,kind,0x6789,len(values),0)
    if len(values)==1:put(at+8,'<I',values[0])
    elif values:
        items=alloc(len(values)*4);put(items,'<'+'I'*len(values),*values);put(at+8,'<I',items)
    return at
def payload(kind):
    if kind in [3,4]:return text(b'Hello/World-\xff')
    if kind in [5,6,7]:
        at=alloc(64);put(at,'<4I',0xabcd9876,0x7f812345,0xffc34567,0x80000000)
        for i in range(16,64):memory[at-BASE+i]=rng.randrange(256)
        return at
    if kind==10:return structure([(1,1,0x12345678),(2,3,payload(3)),(3,20,POOL)])[0]
    if kind==12:return array(12,[array(3,[payload(3),0,payload(3)]),array(10,[payload(10)])])
    return rng.randrange(2**32)
owned=[3,4,5,6,7,10,12]
values={kind:[payload(kind) for _ in range(4)] for kind in owned}
texts=[text(s) for s in [b'',b'A',b'a',b'path/to/TR',b'path\\to\\TR',bytes(range(1,256)),b'Hello/World-\xff']]
c_target,c_source,vector_target=alloc(16),alloc(16),alloc(16)
a_target,a_source,items_in,items_out=alloc(12),alloc(12),alloc(128),alloc(128)
empty,_=structure([])
merge_source,merge_nodes=structure([(1,3,payload(3)),(2,2,0x7f812345),(1,4,payload(4)),(0,13,3),(0,13,4),
    (7,7,payload(7)),(10,10,payload(10)),(12,12,payload(12)),(6,6,payload(6)),(5,5,payload(5))])
merge_target,target_nodes=structure([(2,1,97),(1,3,payload(3)),(0,13,3),(0,13,6),(7,7,payload(7)),(90,10,payload(10))])
put(CONTEXT+24,'<I',merge_target+4)
initial=bytes(memory);(out/'script-copy-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
 ['thug_script_string_interning',0x6f3570,1],['thug_script_string_cursor',0x6f3578,4],
 ['thug_script_string_entries',0x6f3580,4],['thug_script_string_count',0x6f3584,4]]
defaults=[POOL,0x4000,0,POOL,TABLE,0]
functions={}
def bind(at,name,this=True,result='void',cleanup=0,heap=True):
    functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':cleanup,'memory':heap}
bind(0x476260,'thug_script_string_intern',False,'word',heap=False)
bind(0x4763a0,'thug_script_string_copy',False,'word')
bind(0x47abf0,'thug_script_vector_initialize',result='word',heap=False)
bind(0x46cc50,'thug_script_array_set_size',cleanup=8)
bind(0x4773e0,'thug_script_component_copy',False)
bind(0x478480,'thug_script_structure_merge',result='word',cleanup=4)
bind(0x478540,'thug_script_structure_merge_optional',result='word',cleanup=4)
bind(0x4787a0,'thug_script_array_copy_items',False)
bind(0x478a60,'thug_script_array_copy',False)
bind(0x4772a0,'thug_script_component_clear',False)
bind(0x477140,'thug_script_array_clear',False)
bind(0x477090,'thug_script_structure_clear')

pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
for index,table in [(0x6f2338,0x6f2340),(0x6f3644,0x6f364c),(0x6f3654,0x6f365c),(0x6f3614,0x6f361c),(0x6f22b4,0x6f22bc)]:
    cpu.mem_write(index,bytes(4));cpu.mem_write(table,bytes(8))
cpu.mem_write(0x7d1800,struct.pack('<I',MANAGER));cpu.mem_write(0x7cc979,b'\x01')
cases=[];counts=Counter();coverage=Counter();heap_events=Counter()
def word(at):return struct.unpack('<I',cpu.mem_read(at,4))[0]
def setword(at,value):cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
def record(kind,a,b,c):
    index=word(CONTEXT+8);assert index<1200
    log=word(CONTEXT+12)+index*48;setword(CONTEXT+8,index+1)
    pointer=a if kind==2 else c;valid=int(BASE<=pointer<=BASE+SIZE-16)
    snapshot=list(struct.unpack('<4I',cpu.mem_read(pointer,16))) if valid else [0]*4
    watch=word(CONTEXT+24)
    cpu.mem_write(log,struct.pack('<12I',kind,a,b,c,*snapshot,valid,watch,word(watch) if watch else 0,0))
def heap(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP);cleanup=0;result=0
    if address in [0x5bbae0,0x5bafc0]:
        requested=word(sp+4);route=int(address==0x5bafc0)
        if route:assert word(sp+8)==1 and word(sp+12)==0;cleanup=12
        result=word(CONTEXT);assert result+requested+16<=word(CONTEXT+4)
        setword(CONTEXT,(result+requested+19)&~3);uc.mem_write(result,b'\xa5'*requested)
        record(1,requested,route,result)
    elif address in [0x5ba0b0,0x5baba0]:
        record(2,word(sp+4),0,0);cleanup=4 if address==0x5baba0 else 0
    else:
        enter=int(address==0x5bb0e0)
        if enter:assert word(sp+4)==MANAGER+0x200;cleanup=4
        setword(CONTEXT+28,enter);record(3,enter,0,0)
    heap_events[hex(address)]+=1
    uc.reg_write(UC_X86_REG_EAX,result);uc.reg_write(UC_X86_REG_EIP,word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x5bbae0,0x5bafc0,0x5ba0b0,0x5baba0,0x5bb0e0,0x5bb110]:cpu.hook_add(UC_HOOK_CODE,heap,begin=at,end=at)
def observe(uc,address,size,user):coverage[hex(address)]+=1
for at in [0x401aa0,0x476260,0x4763a0,0x46cc50,0x4773e0,0x478480,0x4787a0,0x478a60,0x477920,0x4772a0,0x477140,0x477090,0x47abf0,0x47ac00]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)
def global_read(entry):return int.from_bytes(cpu.mem_read(entry[1],entry[2]),'little')
def case(calls,patches=(),changes=None):
    expected=bytearray(initial);global_values=list(defaults)
    for k,value in (changes or {}).items():global_values[k]=value
    for at,data in patches:
        data=bytes.fromhex(data);expected[at-BASE:at-BASE+len(data)]=data
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0,b'\xa5'*4)
    for entry,value in zip(globals_,global_values):cpu.mem_write(entry[1],value.to_bytes(entry[2],'little'))
    stages=[]
    for fn,this,args in calls:
        f=functions[hex(fn)];sp=STACK+0x18000;stack_args=[] if fn==0x476260 else args
        cpu.mem_write(sp,struct.pack('<'+'I'*(len(stack_args)+1),STOP,*stack_args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this)
        cpu.reg_write(UC_X86_REG_EAX,args[0] if fn==0x476260 else 0xadadadad)
        try:cpu.emu_start(fn,STOP,count=2000000)
        except Exception as error:raise RuntimeError((len(cases),hex(fn),hex(cpu.reg_read(UC_X86_REG_EIP)))) from error
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+f['cleanup'],(len(cases),hex(fn))
        assert bytes(cpu.mem_read(0,4))==b'\xa5'*4
        after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
        if after!=expected:
            for i in range(0,len(initial),4):
                if after[i:i+4]!=expected[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
        expected=bytearray(after)
        stages.append({'fn':hex(fn),'this':this,'args':args,'result':None if f['result']=='void' else cpu.reg_read(UC_X86_REG_EAX),
            'outputs':outputs,'globals':[global_read(g) for g in globals_],'callbacks':0})
        counts[f['name']]+=1
    cases.append({'patches':list(patches),'globals':global_values,'steps':stages});return stages

# Raw bytes, case/slash sensitivity, the empty-string special CRC, repeated
# hits and the original CRC-only first-match behavior (no string comparison).
for fn in [0x476260,0x4763a0]:
    for enabled in [0,1,255]:
        case([(fn,0,[t]) for t in texts+texts[::-1]],changes={2:enabled})
        for index,t in enumerate(texts):
            start=t-BASE;end=initial.index(b'\0',start);data=initial[start:end]
            crc=(zlib.crc32(data)^0xffffffff) if data else 0
            p=[patch(TABLE,'<6I',0x11223344,POOL+64,crc,POOL+128,crc,POOL+256)]
            stages=case([(fn,0,[t])],p,changes={2:enabled,5:3})
            if fn==0x476260 or enabled:assert stages[0]['result']==POOL+128
for i in range(64):
    case([(0x47abf0,vector_target,[])],[[vector_target,bytes(rng.randrange(256) for _ in range(16)).hex()]])

# Storage resizing preserves header padding and never frees inline values.
for old_count in [0,1,2,4]:
    for count in [0,1,2,7]:
        for kind in [0,1,3,12,21,255,0x100]:
            p=[patch(a_target,'<BBHII',0x75,5,0x7654,old_count,items_in)]
            case([(0x46cc50,a_target,[count,kind]),(0x46cc50,a_target,[1,13]),(0x46cc50,a_target,[0,0])],p)

# Every encoded component tag; old owned destinations force cleanup before
# copying. Unknown kinds retain original behavior, including untouched padding.
for tag in range(256):
    kind=tag>>1;value=values[kind][0] if kind in values else rng.randrange(2**32)
    old_kind=owned[tag%len(owned)]
    for borrow in [0,1,0x100]:
        p=[patch(c_source,'<BBHIII',tag,0x62,tag%33,0x12345678,value,0xabcdef01),
           patch(c_target,'<BBHIII',old_kind*2+(tag&1),0x53,17,0x87654321,values[old_kind][1],0xfeed4321)]
        case([(0x4773e0,0,[c_target,c_source,borrow]),(0x4772a0,0,[c_target])],p,changes={2:tag%2})
# Self-copy clears the source too. Null scalar sources and zero-length blobs.
for tag in range(256):
    kind=tag>>1;value=values[kind][0] if kind in values else 0xfedcba98
    p=[patch(c_target,'<BBHIII',tag,0x57,17,0x12345678,value,0xfeed4321)]
    case([(0x4773e0,0,[c_target,c_target,0])],p)
for kind in [0,1,2,7,13,20,21,127]:
    p=[patch(c_source,'<BBHIII',kind*2,0x52,0,1,0,2),patch(c_target,'<BBHIII',1,0x79,0x5678,3,0,4)]
    case([(0x4773e0,0,[c_target,c_source,0])],p)

# Word-by-word scalar copies cover both overlap directions and exact NaN bits.
for kind in [1,2,13]:
    for count in [0,1,2,8]:
        for shift in [-4,0,4,32]:
            case([(0x4787a0,0,[items_in+16+shift,items_in+16,count,kind])],
                 [patch(items_in,'<16I',0,0x80000000,0x7f812345,0xff812345,*[rng.randrange(2**32) for _ in range(12)])])
# Null owned elements leave destination words untouched. Unknown types no-op.
for kind in list(range(32))+[255,256,0xffffffff]:
    payloads=values[kind][:] if kind in [3,4,5,6,10,12] else [1,2,3,4]
    payloads[1]=0
    for count in [0,1,4]:
        for enabled in [0,1]:
            p=[patch(items_in,'<4I',*payloads),patch(items_out,'<4I',0xcafe0001,0xcafe0002,0xcafe0003,0xcafe0004)]
            case([(0x4787a0,0,[items_out,items_in,count,kind])],p,changes={2:enabled})

# Complete array copies clear old owned payloads and deep-copy nested graphs.
for kind in range(32):
    for count in [0,1,4]:
        payloads=values[kind][:] if kind in [3,4,5,6,10,12] else [rng.randrange(2**32) for _ in range(4)]
        if count==4:payloads[1]=0
        for enabled in [0,1]:
            p=[patch(a_source,'<BBHII',0x53,kind,0x6789,count,payloads[0] if count==1 else items_in),
               patch(items_in,'<4I',*payloads),patch(a_target,'<BBHII',0x77,12,0x9876,1,values[12][3])]
            case([(0x478a60,0,[a_target,a_source]),(0x477140,0,[a_target])],p,changes={2:enabled})
for kind in [1,2,3,4,5,6,10,12,13]:
    value=values[kind][0] if kind in values else 0xff812345
    case([(0x478a60,0,[a_target,a_target])],[patch(a_target,'<BBHII',0x57,kind,0x1234,1,value)])
for fn in [0x478480,0x478540]:
    for source in [empty,merge_source]:
        for enabled in [0,1]:
            case([(fn,merge_target,[source]),(fn,merge_target,[source]),(0x477090,merge_target,[])],changes={2:enabled})
case([(0x478540,merge_target,[0])])

scope='Nine original script string/vector/copy/merge routines, with all concrete script callees. Successful generic heap allocations, temporary scopes and frees instrumented; full fixture memory and exact raw float words. Valid acyclic owned graphs, CRC-only interning, borrowing, padding, self-copy and scalar overlap. Pool allocator routing, full QB loading/execution and allocation failures remain outside this scope.'
fixture={'base':BASE,'memory':'script-copy-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':cases,'scope':scope}
path=out/'script-copy-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-values-memory.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=33554432',str(ROOT/'tools/script_values_memory.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(cases),'cases',dict(counts),'heap events',dict(heap_events),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_copy_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'heap_events':dict(heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-copy-memory.bin',adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',len(cases),'cases',sum(counts.values()),'calls')
