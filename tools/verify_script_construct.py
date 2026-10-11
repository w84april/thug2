"""Script parameter construction, lookup, assignment and snapshot oracle."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-construct.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x80000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,POOL,TABLE,LOG,HEAP=BASE+0x28000,BASE+0x30000,BASE+0x34000,BASE+0x38000,BASE+0x48000
memory=bytearray(b'\xad'*SIZE);cursor=0x400;rng=random.Random(0x4779d0)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0x27000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);memory[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000)
def text(data):
    at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def component(kind,value,name=0):
    at=alloc(16);put(at,'<BBHIII',kind*2+(at&4!=0),0x75,17,name,value,0);return at
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
def payload(kind):
    if kind in [3,4]:return text(b'Hello/World-\xff')
    if kind in [5,6,7]:
        at=alloc(64);put(at,'<4I',0xabcd9876,0x7f812345,0xffc34567,0x80000000);return at
    if kind==10:return structure([(1,1,0x12345678),(2,3,payload(3)),(3,20,POOL)])[0]
    if kind==12:return array(12,[array(3,[payload(3),0,payload(3)]),array(10,[payload(10)])])
    return rng.randrange(2**32)
owned=[3,4,5,6,7,10,12];values={kind:[payload(kind) for _ in range(4)] for kind in owned}
texts=[text(s) for s in [b'',b'A',b'a',b'path/to/TR',bytes(range(1,256))]]
target,target_nodes=structure([(1,3,values[3][0]),(2,1,17),(0,13,7),(1,3,values[3][1]),(0,13,8),(3,10,values[10][0])])
empty,_=structure([]);source,source_nodes=structure([(1,12,values[12][0]),(2,2,0xff812345),(3,10,values[10][1])])
borrowed,_=structure([(1,20,source),(2,21,values[12][2])])
container,_=structure([(1,10,source),(2,12,array(10,[empty]))])
script=alloc(244);blob=alloc(65552)
memory[blob-BASE:blob-BASE+65552]=bytes(rng.randrange(256) for _ in range(65552))
def symbol(name,kind,value):
    at=alloc(20);bucket=BUCKETS+(name&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
    put(at,'<BBHIIII',0x91,kind,0x1234,name,0xabcdef01,value,previous);put(bucket,'<I',at);return at
symbol(0x12340001,10,source);symbol(0x12341001,13,0x12340001)
symbol(0x12342001,1,17);symbol(0x12343001,13,0x12349001)
lookup_roots=[]
for order in [0,1,2]:
    entries=[(2,7,values[7][0]),(0,13,0x12341001),(2,1,42)]
    entries=entries[order:]+entries[:order]
    lookup_roots.append(structure(entries+[(0,13,0x12342001),(0,13,0x12343001),(0,13,0x12349999)])[0])
put(CONTEXT+24,'<I',target+4)
initial=bytes(memory);(out/'script-construct-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
 ['thug_script_string_interning',0x6f3570,1],['thug_script_string_cursor',0x6f3578,4],
 ['thug_script_string_entries',0x6f3580,4],['thug_script_string_count',0x6f3584,4],
 ['thug_script_symbol_buckets',0x6f3624,4]]
defaults=[POOL,0x4000,0,POOL,TABLE,0,BUCKETS];functions={}
def bind(at,name,cleanup=8,result='void',heap=True):
    functions[hex(at)]={'name':name,'this':True,'result':result,'cleanup':cleanup,'memory':heap}
for at,name,cleanup in [(0x4779d0,'string',8),(0x477ac0,'local_string',8),(0x477b80,'integer',8),(0x477c60,'float_bits',8),
 (0x477d40,'checksum',8),(0x477e20,'vector_bits',16),(0x477fc0,'pair_bits',12),(0x4780d0,'array',8),
 (0x4781b0,'structure',8),(0x478290,'blob',12)]:bind(at,'thug_script_set_'+name,cleanup)
bind(0x478650,'thug_script_structure_assign',4,'word')
bind(0x476430,'thug_script_find_component',4,'word',False)
bind(0x4739d0,'thug_script_snapshot_arguments',4,'word')
bind(0x477090,'thug_script_structure_clear',0)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[0x4763a0,0x476260,0x477920,0x4772a0,0x477140,0x477090,0x478480,0x478650,0x476bc0,0x478cf0,0x476430])
case=oracle.case
# Replacement, unnamed values, duplicates and text that aliases the old payload.
for fn,kind in [(0x4779d0,3),(0x477ac0,4)]:
    for name in [0,1,2,99]:
        for value in texts+[values[3][0],values[3][1]]:
            for enabled in [0,1]:case([(fn,target,[name,value]),(0x477090,target,[])],changes={2:enabled})
words=[0,1,0xffffffff,0x80000000,0x7fffffff,0x7f800000,0xff800000,0x7f812345,0xff812345,0x7fc34567,0x3f800000]
for fn in [0x477b80,0x477c60,0x477d40]:
    for name in [0,1,2,99]:
        for value in words:case([(fn,target,[name,value]),(fn,target,[name,value]),(0x477090,target,[])])
for fn,n in [(0x477e20,3),(0x477fc0,2)]:
    for name in [0,1,2,99]:
        for i in range(32):
            value=[words[(i+j)%len(words)] for j in range(n)]
            case([(fn,target,[name,*value]),(fn,target,[name,*value]),(0x477090,target,[])])
for fn,kind in [(0x4780d0,12),(0x4781b0,10)]:
    for name in [0,1,2,99]:
        for value in [0,values[kind][2],values[kind][3]]:
            case([(fn,target,[name,value]),(0x477090,target,[])])
for name in [0,1,2,99]:
    for size in [0,1,3,16,255,256,65535,65536,65537]:
        case([(0x478290,target,[name,blob,size]),(0x477090,target,[])])
# Assignment snapshots source members, preserves destination header padding and
# is explicitly a no-op for self-assignment.
for destination in [empty,target,borrowed]:
    for original in [source,empty,destination]:
        for enabled in [0,1]:
            case([(0x478650,destination,[original]),(0x477090,destination,[])],changes={2:enabled})
for root in [empty,target,source,*lookup_roots]:
    for name in [0,1,2,3,0x12341001,0xffffffff]:case([(0x476430,root,[name])])
# Lookup through every stored component tag: only anonymous checksum kind 13
# can include a global structure, while direct names accept every value kind.
for tag in range(256):
    p=[patch(target_nodes[0],'<BBHIII',tag,0x72,0xabcd,0,0x12341001,0)]
    case([(0x476430,target,[2]),(0x476430,target,[0])],p)
# Aliased arguments are deep-copied only when contained through owned structures.
for params in [0,source,container,borrowed]:
    for arguments in [0,source,container,borrowed]:
        for original in [0,source,container,borrowed,empty]:
            p=[patch(script+16,'<2I',params,arguments)]
            steps=case([(0x4739d0,script,[original])],p)
            expected=bool(original and ((params and (original==params or params==container and original==source))
                or (arguments and (original==arguments or arguments==container and original==source))))
            assert bool(steps[0]['result'])==expected,(params,arguments,original)

scope='Thirteen original parameter setters, structure assignment/member lookup and instance argument snapshot routines. Complete concrete copying/ownership callees; successful generic heap route and temporary scopes instrumented. Exact raw coordinate words, anonymous global inclusions, aliasing text sources, nested snapshots and 16-bit blob-length truncation. No full QB parsing/execution, allocator pools or failure handling.'
fixture={'base':BASE,'memory':'script-construct-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope}
path=out/'script-construct-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_construct_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-construct-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts),'heap events',dict(oracle.heap_events))
