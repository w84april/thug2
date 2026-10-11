"""Expression stack lifecycle against the original instructions and heap events."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-expression.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x40000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
POOL,TABLE,LOG,HEAP=BASE+0x14000,BASE+0x16000,BASE+0x18000,BASE+0x28000
memory=bytearray(b'\xad'*SIZE);cursor=0x400;rng=random.Random(0x46d380)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xf000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200)
memory[0x10000:0x14000]=bytes(0x4000)
def string(data):
    at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def component(kind,value):
    at=alloc(16);put(at,'<BBHIII',kind*2+1,0x65,17,0x11223344,value,0x55667788);return at
def payload(kind):
    if kind in [3,4]:return string(b'Expression test')
    if kind in [5,6,7]:
        at=alloc(64);put(at,'<4I',0x98765431,0x3f800000,0x40000000,0x40400000);return at
    if kind in [10,20]:
        node=component(3,payload(3));put(node+12,'<I',0);at=alloc(8);put(at+4,'<I',node);return at
    if kind in [12,21]:
        at=alloc(12);put(at,'<BBHII',0x75,10,0x9876,1,payload(10));return at
    return rng.randrange(2**32)
kinds=[0,1,2,3,4,5,6,7,10,12,13,20,21,127]
values={k:payload(k) for k in kinds};sources={k:component(k,values[k]) for k in kinds}
e=alloc(504);raw=alloc(504);external_error=string(b'Caller-supplied error')
for i in range(20):
    kind=kinds[i%len(kinds)];put(e+i*16,'<BBHIII',kind*2+(i&1),0x65,17,0x1000+i,values[kind],0x55667788)
put(e+0x140,'<I',3)
for i in range(20):put(e+0x144+i*8,'<II',11,i+1)
put(e+0x1e4,'<IB3sIIB3s',2,1,b'ABC',0xabcdef01,external_error,0x77,b'XYZ')
put(CONTEXT+24,'<I',e+0x140)
def structure(entries):
    at=alloc(8);nodes=[component(k,v) for n,k,v in entries];put(at+4,'<I',nodes[0] if nodes else 0)
    for i,(n,k,v) in enumerate(entries):put(nodes[i]+4,'<III',n,v,nodes[i+1] if i+1<len(nodes) else 0)
    return at
def array(kind,values):
    at=alloc(12);put(at,'<BBHII',0x57,kind,0x6789,len(values),0)
    if len(values)==1:put(at+8,'<I',values[0])
    elif values:
        items=alloc(len(values)*4);put(items,'<'+'I'*len(values),*values);put(at+8,'<I',items)
    return at
output=component(0,0)
structs=[structure([]),structure([(1,1,17),(2,2,0x40000000),(0,13,7),(7,3,values[3])]),
 structure([(1,2,0x41880000),(0,13,7),(0,1,2)]),structure([(1,1,18),(2,2,0x40000000)])]
arrays=[array(13,[]),array(13,[1,7]),array(1,[1,2]),array(2,[0x3f800000]),
 array(3,[values[3]]),array(4,[values[4]]),array(5,[values[5]]),array(6,[values[6]]),
 array(10,[structs[1]]),array(12,[array(1,[17])]),array(0,[1,7])]
strings={n:string(b'x'*n) for n in [0,1,98,99,100,198,199,200]}
initial=bytes(memory);(out/'script-expression-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
 ['thug_script_string_interning',0x6f3570,1],['thug_script_string_cursor',0x6f3578,4],
 ['thug_script_string_entries',0x6f3580,4],['thug_script_string_count',0x6f3584,4]]
globals_.append(['thug_script_symbol_buckets',0x6f3624,4])
defaults=[POOL,0x2000,0,POOL,TABLE,0,BASE+0x10000]
for i,value in enumerate([0xadadadab,0x12345678,0xaabbccdd,0x55667788]):
    globals_.append(['thug_expression_temporary',0x6f2348+i*4,4,i*4]);defaults.append(value)
functions={} 
def bind(at,name,cleanup=0,result='void',heap=True):functions[hex(at)]={'name':'thug_script_expression_'+name,'this':True,'result':result,'cleanup':cleanup,'memory':heap}
bind(0x46d1c0,'clear');bind(0x46d220,'clear_if_needed');bind(0x46d250,'set_origin',4,heap=False)
bind(0x46d260,'set_error',4);bind(0x46d2b0,'push_operator',4);bind(0x46d310,'push_value',4)
bind(0x46d370,'open_parenthesis',heap=False);bind(0x46d380,'initialize',result='word');bind(0x46d3c0,'destroy')
functions['0x46d260']['pointer_args']=[0]
bind(0x46d450,'execute');bind(0x46eb70,'accept_operator',4)
bind(0x46ebf0,'close_parenthesis');bind(0x46ec40,'finish',4,'byte')
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[0x46d140,0x4772a0,0x4773e0,0x478540,0x478a60,0x46d1c0,0x46d450,0x47a910,0x4791a0,0x479410,0x4795a0])
case=oracle.case
for byte in [0,1,0x55,0xaa,0xad,0xff]:
    case([(0x46d380,raw,[]),(0x46d220,raw,[]),(0x46d3c0,raw,[])],[[raw,(bytes([byte])*504).hex()]])
for fn in [0x46d1c0,0x46d220,0x46d260,0x46d3c0]:
    for index in [0,1,19,20,0xffffffff]:
        args=[external_error] if fn==0x46d260 else []
        case([(fn,e,args),(0x46d220,e,[])],[patch(e+0x140,'<I',index)])
# Exact cleanup gate: all four trigger fields independently, even with stale
# owners elsewhere and a nonzero has_operator flag.
for tag in [0,1,2,3]:
    for index,opindex,error in [(0,0,0),(1,0,0),(0,1,0),(0,0,external_error)]:
        case([(0x46d220,e,[])],[patch(e,'<B',tag),patch(e+0x140,'<I',index),patch(e+0x1e4,'<I',opindex),patch(e+0x1f0,'<I',error)])
for origin in [0,e,e+0x1ec,external_error,0xffffffff]:case([(0x46d250,e,[origin])])
for error in [0,external_error,0x647b50,0x647b68]:case([(0x46d260,e,[error])])
# Operator sentinel, overflow boundary, and uint32 wrap into slot zero.
for index in [0,1,18,19,20,0xffffffff]:
    for opcode in [0,5,7,8,10,11,12,13,18,20,50,51,0xffffffff]:
        case([(0x46d2b0,e,[opcode])],[patch(e+0x1e4,'<I',index)])
for index in [0,1,19]:
    for count in [0,1,0x7fffffff,0xffffffff]:
        case([(0x46d370,e,[]),(0x46d370,e,[])],[patch(e+0x1e4,'<I',index),patch(e+0x148+index*8,'<I',count)])
for kind,source in sources.items():
    for index,first_tag in [(0,0),(0,1),(0,2),(1,0),(18,2),(19,2),(20,0),(0xffffffff,0)]:
        case([(0x46d310,e,[source]),(0x46d1c0,e,[])],[patch(e,'<B',first_tag),patch(e+0x140,'<I',index)])
# Source aliasing reaches the same component-copy implementation as normal use.
for source_index,index,tag in [(0,0,0),(0,0,2),(1,0,2),(19,18,2)]:
    case([(0x46d310,e,[e+source_index*16])],[patch(e,'<B',tag),patch(e+0x140,'<I',index)])
# A realistic sequence fills each stack, then exercises the original overflow
# cleanup and the ability to construct a fresh expression after the error.
for kind in [1,3,10,12]:
    calls=[(0x46d380,raw,[]),(0x46d250,raw,[external_error])]
    for i in range(21):calls.append((0x46d310,raw,[sources[kind]]))
    calls.extend([(0x46d220,raw,[]),(0x46d310,raw,[sources[1]]),(0x46d3c0,raw,[])])
    case(calls)
calls=[(0x46d380,raw,[])]
for i in range(21):calls.append((0x46d2b0,raw,[11]))
calls.extend([(0x46d260,raw,[external_error]),(0x46d220,raw,[])])
case(calls)

# The initialized expression representation, with poisoned untouched metadata.
blank=bytearray(b'\xad'*504)
for i in range(20):struct.pack_into('<BBHIII',blank,i*16,i&1,0x75,17,0x1000+i,0,0x55667788)
struct.pack_into('<I',blank,0x140,0);blank[0x144:0x1e4]=bytes(160)
struct.pack_into('<IB3sIIB3s',blank,0x1e4,0,0,b'ABC',0xabcdef01,0,1,b'XYZ')
# Track typed arithmetic results, including heap coordinates that survive a
# later cleanup. Other memory words, tags, integers and pointers remain exact.
def execute_case(calls,patches,changes=None):
    stages=case(calls,patches,changes);state=bytearray(initial);heap_float_fields=set()
    for a,data in patches:state[a-BASE:a-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
    for step in stages:
        float_fields=set()
        for a,data in step['outputs']:state[a-BASE:a-BASE+len(bytes.fromhex(data))]=bytes.fromhex(data)
        for c in [*[e+i*16 for i in range(20)],output]:
            k=state[c-BASE]>>1;value=struct.unpack_from('<I',state,c-BASE+8)[0]
            if k==2:float_fields.add(c+8)
            elif k in [5,6] and HEAP<=value<BASE+SIZE:
                heap_float_fields.update(value+i*4 for i in range(1,3 if k==5 else 4))
        step['float_fields']=sorted(float_fields|heap_float_fields)
    return stages
def binary(ka,a,kb,b,op,extra=(),calls=None,vi=1,oi=1,changes=None):
    patches=[[e,blank.hex()],patch(e+0x140,'<I',vi),patch(e+0x1e4,'<IB',oi,1),patch(e+0x144+oi*8,'<I',op),
     patch(e+(vi-1)*16,'<BBHIII',ka*2+1,0x75,17,0x12345678,a,0x55667788),
     patch(e+vi*16,'<BBHIII',kb*2,0x75,17,0x87654321,b,0x11223344),*extra]
    return execute_case(calls or [(0x46d450,e,[])],patches,changes)
operators=[5,7,8,10,11,12,13,18,20,50,51]
for op in operators:
    for ka in kinds:
        for kb in kinds:binary(ka,values[ka],kb,values[kb],op)
# Numeric edge cases and full integer truth words. The x86 IDIV overflow trap is
# outside these returning-call fixtures; the port explicitly traps that input.
words=[0,1,0x80000000,0x7fffffff,0xffffffff,16777217,0x4b800001,0x3f800000,0xbf800000,
 0x358637bc,0x358637bd,0x358637be,0x7f7fffff,0x00800001,0x00000001,0x7f800000,0xff800000,0x7fc12345,0x7f812345]
for op in [10,11,12,13,50,51]:
    for ka,kb in [(1,1),(1,2),(2,1),(2,2)]:
        for i,a in enumerate(words):
            for b in [words[(i+3)%len(words)],words[(i+7)%len(words)],0,1]:
                if op==12 and ka==kb==1 and a==0x80000000 and b==0xffffffff:continue
                binary(ka,a,kb,b,op)
# Random mixed FILD/float operations target lost low-product and quotient bits.
for i in range(240):
    ka,kb=[(1,2),(2,1),(2,2)][i%3]
    a,b=rng.randrange(2**32),rng.randrange(2**32)
    for op in [10,11,12,13]:binary(ka,a,kb,b,op)
for op in [8,10,11,12,13]:
    for kind in [5,6]:
        for word in words:
            extra=[patch(values[kind]+4,'<3I',word,word,word)]
            binary(kind,values[kind],kind if op!=12 else 2,values[kind] if op!=12 else 0x3f800001,op,extra)
# All string length boundaries, separately for normal/local strings and interning.
for kind in [3,4]:
    for na,nb in [(0,0),(1,0),(98,100),(99,100),(100,100),(198,1),(199,0),(199,1),(200,0)]:
        for intern in [0,1]:
            # No need for changes to source pointers: strings are copied first.
            binary(kind,strings[na],kind,strings[nb],11,changes={2:intern})
for ka in [10,20]:
    for kb in [10,20]:
        for a in structs:
            for b in structs:
                for op in [10,11,7,18,20]:binary(ka,a,kb,b,op)
    for a in structs:
        for name in [0,1,2,7,0xffffffff]:
            for op in [8,10]:binary(ka,a,13,name,op)
        for b in arrays:
            for kb in [12,21]:binary(ka,a,kb,b,10)
for ka in [12,21]:
    for a in arrays:
        for index in [0,1,2,0xffffffff]:binary(ka,a,1,index,5)
        for kb in [12,21]:
            # Same-type concatenation plus empty arrays. Incompatible pointer
            # array types can make the original dereference invalid memory.
            for b in [arrays[0],a]:binary(ka,a,kb,b,11)
# Different scalar array kinds still use the left kind for both copies.
for a in arrays[:4]:
    for b in arrays[:4]:binary(12,a,12,b,11)
for op in [0,1,6,9,19,21,52,53,54,63,0xffffffff]:binary(1,17,1,3,op)
for vi,oi in [(1,0),(1,19),(19,1),(19,19)]:binary(1,17,1,3,11,vi=vi,oi=oi)
# Guard errors occur before temporary-value initialization.
for vi,op,parens in [(0,11,0),(0xffffffff,11,0),(1,11,1),(1,0,0)]:
    patches=[[e,blank.hex()],patch(e+0x140,'<I',vi),patch(e+0x144,'<II',op,parens)]
    execute_case([(0x46d450,e,[])],patches)
# Precedence is checked through original execution, including unsupported tokens
# that have nontrivial precedence entries.
for old in [*operators,19,21,52,53,54]:
    for new in range(64):
        binary(1,17,1,3,old,calls=[(0x46eb70,e,[new])])
# Complete expressions, nested parentheses, missing values/operators, and finish.
for kind,source in sources.items():
    for k in [kind]:
        execute_case([(0x46ec40,e,[output])],[[e,blank.hex()],patch(e,'<BBHIII',k*2+1,0x75,17,7,values[k],0)])
for parens,op,index in [(1,0,0),(0,11,0),(0,0,1)]:
    execute_case([(0x46ec40,e,[output])],[[e,blank.hex()],patch(e+0x144,'<II',op,parens),patch(e+0x1e4,'<I',index)])
execute_case([(0x46ebf0,e,[])],[[e,blank.hex()]])
for i in range(3):
    calls=[(0x46d250,e,[external_error]),(0x46d370,e,[]),(0x46d310,e,[sources[1]]),
      (0x46eb70,e,[11]),(0x46d370,e,[]),(0x46d310,e,[sources[1]]),(0x46eb70,e,[13]),
      (0x46d310,e,[sources[1]]),(0x46ebf0,e,[]),(0x46ebf0,e,[]),(0x46ec40,e,[output]),(0x46d3c0,e,[])]
    execute_case(calls,[[e,blank.hex()],patch(sources[1]+8,'<I',[3,16777217,0xffffffff][i])])
for old in operators:
    for new in operators:
        calls=[(0x46d310,e,[sources[1]]),(0x46eb70,e,[old]),(0x46d310,e,[sources[1]]),
          (0x46eb70,e,[new]),(0x46d310,e,[sources[1]]),(0x46ec40,e,[output])]
        execute_case(calls,[[e,blank.hex()],patch(sources[1]+8,'<I',3)])
for op in operators:
    binary(1,17,1,3,op,calls=[(0x46ec40,e,[output])])

scope='Thirteen original expression routines, including complete binary execution, precedence, parentheses, finish and stack lifecycle. Eleven supported operator tokens cover scalar arithmetic, comparisons/bitwise truth, string concatenation, pair/vector math, array access/concatenation and structure member/merge/subtraction behavior. Original concrete callees and successful generic heap events run unchanged. Complete fixture memory is compared, with classification-only checks for typed arithmetic NaNs and text-verified relocation of error literals. The original switch-error index underflow and distinct guard-error path are retained. Invalid pointers, out-of-range stack/table indices, allocation failures and IDIV overflow are outside returning fixtures. QB bytecode parsing and script execution remain separate work.'
fixture={'base':BASE,'memory':'script-expression-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope,
 'pointer_symbols':[[0x647b50,'thug_expression_error_operator_overflow','Operator stack overflow'],[0x647b68,'thug_expression_error_value_overflow','Value stack overflow']],
 'pointer_fields':[e+0x1f0,raw+0x1f0]}
# Read literals from the specimen, independently of recovered C definitions.
from specimen import load
image=load().get_memory_mapped_image()
for address in [0x6482c8, 0x6482ac, 0x648288, 0x64825c, 0x648234, 0x648208, 0x6481e0, 0x6481b8, 0x648194, 0x64816c, 0x648140, 0x648110, 0x6480d4, 0x648098, 0x648070, 0x648040, 0x648010, 0x647fe0, 0x647fb4, 0x647f58, 0x647f00, 0x647ed8, 0x647ea8, 0x647e7c, 0x647e50, 0x647e28, 0x647dfc, 0x647de0, 0x647dc4, 0x647d9c, 0x647d74, 0x647d4c, 0x647d24, 0x647cfc, 0x647cc4, 0x647c90, 0x647c58, 0x647c30, 0x647bfc, 0x647be0, 0x647bc8, 0x647b98, 0x647b80, 0x64831c, 0x6482f8]:
    text=image[address-0x400000:].split(b'\0',1)[0].decode('ascii')
    fixture['pointer_symbols'].append([address,'thug_expression_error_'+format(address,'x'),text])
path=out/'script-expression-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_expression_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-expression-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
