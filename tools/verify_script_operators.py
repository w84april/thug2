"""Value operations needed by the expression evaluator, against original x86."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-operators.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x40000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
BUCKETS,POOL,TABLE,LOG,HEAP=BASE+0x10000,BASE+0x14000,BASE+0x16000,BASE+0x18000,BASE+0x28000
memory=bytearray(b'\xad'*SIZE);cursor=0x400;rng=random.Random(0x4791a0)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xf000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);memory[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000)
def text(data):
    at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def structure(entries):
    at=alloc(8);nodes=[alloc(16) for _ in entries];put(at+4,'<I',nodes[0] if nodes else 0)
    for i,(name,kind,value) in enumerate(entries):put(nodes[i],'<BBHIII',kind*2+(i&1),0x75,17,name,value,nodes[i+1] if i+1<len(nodes) else 0)
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
        at=alloc(64);put(at,'<4I',0xabcd9876,0x3f800000,0x40000000,0x40400000);return at
    if kind in [10,20]:return structure([(1,1,17),(2,3,payload(3))])[0]
    if kind in [12,21]:return array(12,[array(3,[payload(3),0,payload(3)]),array(10,[payload(10)])])
    return rng.randrange(2**32)
kinds=[0,1,2,3,4,5,6,7,10,12,13,20,21,127]
values={k:[payload(k) for _ in range(4)] for k in kinds}
left,right,result,arr,items=alloc(16),alloc(16),alloc(16),alloc(12),alloc(32)
empty,_=structure([]);one,_=structure([(1,1,17)]);same,_=structure([(1,1,17)]);dupes,_=structure([(1,1,17),(1,1,17)])
larger,_=structure([(1,1,17),(2,2,0x7fc12345)]);different,_=structure([(1,2,0x41880000)])
roots=[empty,one,same,dupes,larger,different]
target,nodes=structure([(1,3,values[3][0]),(2,1,17),(1,4,values[4][0]),(0,13,7),(1,10,values[10][0]),(0,1,7)])
strings=[text(s) for s in [b'',b'a',b'A',b'ab',b'ba',b'abc',b'\xff\x01',b'\xff\x01',b'\xff\x02']]
def symbol(name,kind,value):
    at=alloc(20);bucket=BUCKETS+(name&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
    put(at,'<BBHIIII',0x91,kind,0x1234,name,0xabcdef01,value,previous);put(bucket,'<I',at);return at
symbols=[]
for kind in kinds:
    name=0xaaa00001+kind*0x1000;symbol(name,kind,values[kind][0]);symbols.append((name,kind,values[kind][0]))
symbol(0xaab00001,13,symbols[1][0]);symbol(0xaab01001,13,0xaab00001);symbol(0xaab02001,13,0xeeee0001)
put(CONTEXT+24,'<I',target+4)
initial=bytes(memory);(out/'script-operators-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
 ['thug_script_string_interning',0x6f3570,1],['thug_script_string_cursor',0x6f3578,4],
 ['thug_script_string_entries',0x6f3580,4],['thug_script_string_count',0x6f3584,4],['thug_script_symbol_buckets',0x6f3624,4]]
defaults=[POOL,0x2000,0,POOL,TABLE,0,BUCKETS];functions={}
def bind(at,name,cleanup=0,result='void',heap=False,this=True):functions[hex(at)]={'name':'thug_script_'+name,'this':this,'result':result,'cleanup':cleanup,'memory':heap}
bind(0x476490,'next_component',4,'word')
bind(0x4776b0,'remove_name',4,heap=True);bind(0x477790,'remove_typed',8,heap=True);bind(0x477860,'remove_unnamed_value',4,heap=True)
for at,name in [(0x4791a0,'component_equal'),(0x479410,'component_less'),(0x4795a0,'component_greater'),(0x476c10,'structure_is_subset'),(0x49f4b0,'array_equal_fallback')]:bind(at,name,4,'byte')
bind(0x46cb70,'array_text',4,'word');bind(0x46cbf0,'array_number',4,'double')
bind(0x47a910,'array_component',heap=True,this=False)
bind(0x46d160,'component_is_borrowed',result='byte');bind(0x46d180,'component_borrow');bind(0x46d1a0,'component_own');bind(0x46d280,'component_truth',result='word')
bind(0x477090,'structure_clear',heap=True)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,
 observe=[0x478cf0,0x476c10,0x4791a0,0x49f4b0,0x46cbf0,0x46cc30,0x46cb70,0x4772a0,0x4763a0,0x478540,0x478a60])
case=oracle.case;quiet_differences=[]
def cpatch(at,kind,value,flag=0):return patch(at,'<BBHIII',kind*2+flag,0x75,17,0x11223344,value,0x55667788)
comparisons=[0x4791a0,0x479410,0x4795a0]
for a in kinds:
    for b in kinds:
        case([(f,left,[right]) for f in comparisons],[cpatch(left,a,values[a][0]),cpatch(right,b,values[b][1],1)])
words=[0,1,0x80000000,0x7fffffff,0xffffffff,16777216,16777217,0x3f800000,0xbf800000,0x80000001,
 0x7f800000,0xff800000,0x7f812345,0xff812345,0x7fc12345,0x4b800000,0x4b800001,0x7f7fffff]
for ka in [1,2]:
    for kb in [1,2]:
        for a in words:
            for b in words:case([(f,left,[right]) for f in comparisons],[cpatch(left,ka,a),cpatch(right,kb,b,1)])
for kind in [3,4]:
    for a in strings:
        for b in strings:case([(f,left,[right]) for f in comparisons],[cpatch(left,kind,a),cpatch(right,kind,b)])
for kind in [5,6]:
    for word in words:
        for coordinate in range(1,3 if kind==5 else 4):
            a,b=values[kind][:2]
            p=[cpatch(left,kind,a),cpatch(right,kind,b),patch(a+4*coordinate,'<I',word),patch(b+4*coordinate,'<I',word)]
            case([(0x4791a0,left,[right]),(0x4791a0,left,[left])],p)
for a in roots:
    for b in roots:
        case([(0x476c10,a,[b])])
        for ka in [10,20]:
            for kb in [10,20]:case([(f,left,[right]) for f in comparisons],[cpatch(left,ka,a),cpatch(right,kb,b)])
for name,kind,value in symbols:
    for swapped in [False,True]:
        p=[cpatch(left,13,name),cpatch(right,kind,value)]
        case([(f,right if swapped else left,[left if swapped else right]) for f in comparisons],p)
for name in [0xaab00001,0xaab01001,0xaab02001,0xeeee0001]:
    case([(f,left,[right]) for f in comparisons],[cpatch(left,13,name),cpatch(right,13,name)])
for a,b in [(0,0),(0,1),(1,0),(values[12][0],values[12][0]),(values[12][0],values[12][1])]:case([(0x49f4b0,a,[b])])
for tag in range(256):
    p=[patch(left,'<BBHIII',tag,0x52,0x1357,0x12345678,words[tag%len(words)],0x98765432)]
    case([(0x46d160,left,[]),(0x46d280,left,[]),(0x46d180,left,[]),(0x46d160,left,[]),(0x46d1a0,left,[])],p)
for root in [empty,target]:
    for c in [0,*nodes]:case([(0x476490,root,[c])])
for fn in [0x4776b0,0x477860]:
    for value in [0,1,2,3,7,8,0xffffffff]:case([(fn,target,[value]),(0x477090,target,[])])
for kind in range(256):
    for name in [0,1]:case([(0x477790,target,[name,kind]),(0x477090,target,[])])
# Every component tag can be deleted; name/value removal must not filter types.
for tag in range(256):
    k=tag>>1;value=values[k][2] if k in values and k in [3,4,5,6,7,10,12] else 7
    p=[patch(nodes[0],'<BBHIII',tag,0x51,17,0,value,nodes[1])]
    case([(0x477860,target,[value]),(0x477090,target,[])],p)
# Raw/signed numeric getters: inline values ignore even extreme indices.
for kind in [0,1,2,4,0x82,255]:
    for count,index in [(1,0),(1,0xffffffff),(1,0x80000000),(4,0),(4,2),(4,0xffffffff)]:
        for value in words:
            p=[patch(arr,'<BBHII',0x57,kind,0x1357,count,value if count==1 else items+4),patch(items,'<8I',*([value]*8))]
            case([(0x46cb70,arr,[index]),(0x46cbf0,arr,[index])],p)
# Array-to-component dispatch masks the high type bit, but numeric conversion
# still examines the full source type. Local strings deliberately yield no value.
for kind in range(256):
    effective=kind&127
    value=values[effective][0] if effective in [3,5,6,10,12] else 0x7f812345
    for count in [1,3]:
        for borrow in [0,1]:
            p=[patch(arr,'<BBHII',0x53,kind,0x9876,count,value if count==1 else items),patch(items,'<3I',value,value,value),
               cpatch(result,0,0,kind&1)]
            stages=case([(0x47a910,0,[arr,0 if count==1 else 1,result,borrow])],p,changes={2:kind&1})
            if effective==2:
                stages[0]['quiet_float_fields']=[result+8]
                raw=int.from_bytes(oracle.cpu.mem_read(result+8,4),'little')
                if raw&0x7f800000==0x7f800000 and raw&0x7fffff and not raw&0x400000:
                    quiet_differences.append({'case':len(oracle.cases)-1,'address':result+8,'oracle_word':raw,'intel_quiet_word':raw|0x400000})

scope='Sixteen original expression value helpers: exact numeric comparisons with symbol resolution, string equality/length ordering, structure member inclusion, array identity fallback, iteration/removal, array number/text/component access and ownership/truth tags. Real concrete callees with successful generic heap instrumentation. The pinned specimen array-equality fallback really returns false unconditionally. Numeric NaN returns compare by classification; signaling-NaN array stores require the exact Intel quiet bit, retaining raw emulator differences. No expression operator execution or QB parsing claimed by this suite.'
fixture={'base':BASE,'memory':'script-operators-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope}
path=out/'script-operators-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_operators_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'signaling_nan_differences':quiet_differences,'scope':scope,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-operators-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts),'signaling NaN differences',len(quiet_differences))
