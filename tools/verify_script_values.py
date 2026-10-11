"""Script value ownership, recursive disposal, insertion and containment oracle.

Concrete script callees execute unchanged. Heap release is instrumented, including
payload snapshots and a watched list link at the point of release. Pool routing
is disabled; shared string address-range decisions remain original game code.
"""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_ECX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
out=ROOT/'local/validation/collision';report_path=out.parent/'script-values.json';report_path.unlink(missing_ok=True)
BASE,SIZE,STACK,STOP=0x1800000,0x30000,0x3000000,0x3f00000
CONTEXT,ADAPTER,POOL,LOG,HEAP=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x18000,BASE+0x20000
memory=bytearray(b'\xad'*SIZE);cursor=0x200;rng=random.Random(0x4772a0)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0x17000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
def component(kind,value,name=0):
    at=alloc(16);put(at,'<BBHIII',kind*2+(at&4!=0),0x75,0x9876,name,value,0);return at
def structure(entries):
    at=alloc(8);nodes=[component(kind,value,name) for name,kind,value in entries]
    put(at+4,'<I',nodes[0] if nodes else 0)
    for i,node in enumerate(nodes):put(node+12,'<I',nodes[i+1] if i+1<len(nodes) else 0)
    return at,nodes
def array(kind,values):
    at=alloc(12);put(at,'<BBHII',0x57,kind,0x6789,len(values),0)
    if len(values)==1:put(at+8,'<I',values[0])
    elif values:
        items=alloc(len(values)*4);put(items,'<'+'I'*len(values),*values);put(at+8,'<I',items)
    return at
def payload(kind,depth=0):
    if kind in [3,4]:
        at=alloc(24);memory[at-BASE:at-BASE+12]=b'hello-world\0';return at
    if kind in [5,6,7]:
        at=alloc(32);put(at,'<8I',*(rng.randrange(2**32) for _ in range(8)));return at
    if kind==10:
        return structure([(1,1,0x12345678),(2,3,payload(3)),(3,20,POOL)])[0]
    if kind==12:
        return array(12,[array(3,[payload(3),0,payload(3)]),array(10,[payload(10)])])
    return rng.randrange(2**32)

owned=[3,4,5,6,7,10,12]
values={kind:[payload(kind) for _ in range(4)] for kind in owned}
empty,_=structure([])
leaf,leaf_nodes=structure([(3,3,payload(3)),(5,5,payload(5))])
borrowed,_=structure([(9,6,payload(6))])
array_child,_=structure([(10,1,17)])
middle,middle_nodes=structure([(1,10,leaf),(2,20,borrowed),(3,12,array(10,[array_child]))])
root,root_nodes=structure([(5,1,7),(6,10,middle),(7,7,payload(7)),(8,4,POOL+4),(9,21,values[12][0])])
c_target,a_target,items=alloc(16),alloc(12),alloc(32)
insert_root,insert_nodes=structure([(0x1122,1,1),(0x3344,13,5),(0x1122,1,2),(0x5566,1,3)])
incoming=component(1,123,0x1122)
put(CONTEXT+24,'<I',insert_root+4)
initial=bytes(memory);(out/'script-values-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4]]
defaults=[POOL,32]
functions={}
def bind(at,name,this=True,result='void',cleanup=0,heap=True):
    functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':cleanup,'memory':heap}
bind(0x476410,'thug_script_structure_initialize',result='word',heap=False)
bind(0x46d140,'thug_script_component_initialize',result='word',heap=False)
bind(0x46caa0,'thug_script_array_initialize',result='word',heap=False)
bind(0x46cb00,'thug_script_array_items',result='word',heap=False)
bind(0x476340,'thug_script_string_release',False)
bind(0x46cab0,'thug_script_array_clear_storage')
bind(0x477140,'thug_script_array_clear',False)
bind(0x4772a0,'thug_script_component_clear',False)
bind(0x477090,'thug_script_structure_clear')
bind(0x477130,'thug_script_structure_destroy')
bind(0x477920,'thug_script_structure_insert',cleanup=4)
bind(0x476bc0,'thug_script_structure_contains',result='byte',cleanup=4,heap=False)

pe=load();cpu=Uc(UC_ARCH_X86,UC_MODE_32)
cpu.mem_map(0x400000,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);cpu.mem_write(0x400000,pe.get_memory_mapped_image())
for at,size in [(0,4096),(BASE,SIZE),(STACK,0x20000),(STOP,4096)]:cpu.mem_map(at,size)
for index,table in [(0x6f2338,0x6f2340),(0x6f3644,0x6f364c),(0x6f3654,0x6f365c),(0x6f3614,0x6f361c),(0x6f22b4,0x6f22bc)]:
    cpu.mem_write(index,bytes(4));cpu.mem_write(table,bytes(8))
cpu.mem_write(0x7d1800,struct.pack('<I',BASE+0x80))
cases=[];counts=Counter();coverage=Counter();heap_events=Counter()
def word(at):return struct.unpack('<I',cpu.mem_read(at,4))[0]
def setword(at,value):cpu.mem_write(at,struct.pack('<I',value&0xffffffff))
def heap_release(uc,address,size,user):
    sp=uc.reg_read(UC_X86_REG_ESP);pointer=word(sp+4);index=word(CONTEXT+8);assert index<512
    log=word(CONTEXT+12)+index*48;setword(CONTEXT+8,index+1)
    valid=int(BASE<=pointer<=BASE+SIZE-16);snapshot=list(struct.unpack('<4I',uc.mem_read(pointer,16))) if valid else [0]*4
    watch=word(CONTEXT+24)
    uc.mem_write(log,struct.pack('<12I',2,pointer,0,0,*snapshot,valid,watch,word(watch) if watch else 0,0))
    heap_events[hex(address)]+=1
    uc.reg_write(UC_X86_REG_EAX,0);uc.reg_write(UC_X86_REG_EIP,word(sp));uc.reg_write(UC_X86_REG_ESP,sp+4+(4 if address==0x5baba0 else 0))
for at in [0x5ba0b0,0x5baba0]:cpu.hook_add(UC_HOOK_CODE,heap_release,begin=at,end=at)
def observe(uc,address,size,user):coverage[hex(address)]+=1
for at in [0x4772a0,0x477140,0x477090,0x46cab0,0x476340,0x44c1d0,0x44c230,0x409070,0x408fd0,0x44c170]:
    cpu.hook_add(UC_HOOK_CODE,observe,begin=at,end=at)

def case(calls,patches=(),changes=None):
    expected=bytearray(initial);global_values=list(defaults)
    for k,value in (changes or {}).items():global_values[k]=value
    for at,text in patches:
        data=bytes.fromhex(text);expected[at-BASE:at-BASE+len(data)]=data
    cpu.mem_write(BASE,bytes(expected));cpu.mem_write(0,b'\xa5'*4)
    for entry,value in zip(globals_,global_values):setword(entry[1],value)
    stages=[]
    for fn,this,args in calls:
        f=functions[hex(fn)];sp=STACK+0x18000;cpu.mem_write(sp,struct.pack('<'+'I'*(len(args)+1),STOP,*args))
        cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_EAX,0xadadadad)
        cpu.emu_start(fn,STOP,count=2000000)
        assert cpu.reg_read(UC_X86_REG_EIP)==STOP and cpu.reg_read(UC_X86_REG_ESP)==sp+4+f['cleanup'],(len(cases),hex(fn))
        assert bytes(cpu.mem_read(0,4))==b'\xa5'*4
        after=bytes(cpu.mem_read(BASE,len(initial)));outputs=[]
        if after!=expected:
            for i in range(0,len(initial),4):
                if after[i:i+4]!=expected[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
        expected=bytearray(after)
        result=None if f['result']=='void' else cpu.reg_read(UC_X86_REG_EAX)&(255 if f['result']=='byte' else 0xffffffff)
        stages.append({'fn':hex(fn),'this':this,'args':args,'result':result,'outputs':outputs,
                       'globals':[word(g[1]) for g in globals_],'callbacks':0})
        counts[f['name']]+=1
    cases.append({'patches':list(patches),'globals':global_values,'steps':stages});return stages

# Constructor poison and every untouched padding byte. Reinitialization is
# confined to objects that do not own live payloads or belong to linked lists.
for fn,size in [(0x476410,8),(0x46d140,16),(0x46caa0,12)]:
    for i in range(64):
        case([(fn,c_target,[])],[[c_target,bytes(rng.randrange(256) for _ in range(size)).hex()]])
for count in [0,1,2,3,0x7fffffff,0x80000000,0xffffffff]:
    for value in [0,items,0xffffffff]:
        case([(0x46cb00,a_target,[])],[patch(a_target+4,'<2I',count,value)])
# Pool comparisons include half-open boundaries and unsigned end wrap. Null
# reaches the original heap wrapper, which correctly suppresses a free call.
for start in [0,POOL,0xfffffff0]:
    for size in [0,1,16,0xffffffff]:
        for pointer in [0,(start-1)&0xffffffff,start,(start+size-1)&0xffffffff,(start+size)&0xffffffff]:
            case([(0x476340,0,[pointer])],changes={0:start,1:size})
for count in [0,1,2,4,0xffffffff]:
    for value in [0,items]:
        case([(0x46cab0,a_target,[])]*2,[patch(a_target+4,'<2I',count,value)])

# All 256 stored component tag/flag bytes with null and non-null values.
for tag in range(256):
    kind=tag>>1
    for null in [False,True]:
        value=0 if null else values[kind][0] if kind in values else rng.randrange(2**32)
        p=[patch(c_target,'<BBHIII',tag,0x56,0x7788,rng.randrange(2**32),value,0xabcdef01)]
        case([(0x4772a0,0,[c_target])]*2,p)
# Arrays use a raw type byte, not the component's shifted type encoding.
for kind in range(256):
    for count in [0,1,4]:
        payloads=values[kind][:] if kind in [3,4,5,6,10,12] else [rng.randrange(2**32) for _ in range(4)]
        if count==4:payloads[1]=0
        value=payloads[0] if count==1 else items
        p=[patch(a_target,'<BBHII',0x57,kind,0x6789,count,value),patch(items,'<4I',*payloads)]
        case([(0x477140,0,[a_target])]*2,p)

# Recursion across owning arrays/structures, borrowed references and pooled
# strings; repeat the clear to prove that no payload is released twice.
for s in [empty,leaf,borrowed,array_child,middle,root]:
    for fn in [0x477090,0x477130]:case([(fn,s,[])]*2,[patch(CONTEXT+24,'<I',s+4)])
# Containment follows direct owned structures only, including self identity.
for s in [empty,leaf,borrowed,array_child,middle,root]:
    for target in [0,empty,leaf,borrowed,array_child,middle,root]:case([(0x476bc0,s,[target])])
assert case([(0x476bc0,0,[0])])[0]['result']==1

# Replacement in list head/middle, multiple matching members, unmatched types,
# numeric type coercion and literal equality for unnamed checksum flags.
for i in range(512):
    old=i%128;new=old if i<128 else [1,2,13][(i//128)-1]
    name=0 if i&1 else 0x1122
    old_values=values[old][:2] if old in values else [0xabcdef01,0xabcdef02]
    new_value=values[new][2] if new in values else old_values[i%2]
    p=[patch(insert_nodes[0],'<BBHIII',old*2+(i&1),0x72,0x3344,name,old_values[0],insert_nodes[1]),
       patch(insert_nodes[2],'<BBHIII',old*2+((i>>1)&1),0x72,0x3344,name,old_values[1],insert_nodes[3]),
       patch(incoming,'<BBHIII',new*2+(i&1),0x51,0x6688,name,new_value,0xdeadbeef)]
    case([(0x477920,insert_root,[incoming]),(0x477090,insert_root,[])],p)
case([(0x477920,empty,[incoming]),(0x477090,empty,[])],[patch(CONTEXT+24,'<I',empty+4)])

scope='Original script value constructors, item storage, recursive ownership cleanup, structure insertion/replacement and containment. Acyclic constructed owned graphs, borrowed references and pooled strings; original concrete callees with heap release instrumentation. Pool allocator routing and full QB execution remain unrecovered.'
fixture={'base':BASE,'memory':'script-values-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release'],'globals':globals_,'functions':functions,'float_fields':[],
 'cases':cases,'scope':scope}
path=out/'script-values-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-values-memory.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=33554432',str(ROOT/'tools/script_values_memory.c'),'-o',str(adapter)],check=True)
print('x86 complete:',dict(counts),'heap releases',sum(heap_events.values()),flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_values_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(counts),'callee_coverage':dict(coverage),'heap_events':dict(heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-values-memory.bin',adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(counts))
