"""Original global QB registration, symbol lifetime and script-body checksums."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-symbols.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x700000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
PROGRAM,BUCKETS,POOL,TABLE,LOG,HEAP=BASE+0xd000,BASE+0x10000,BASE+0x100000,BASE+0x120000,BASE+0x180000,BASE+0x500000
memory=bytearray(b'\xad'*SIZE);cursor=0x800;rng=random.Random(0x479110)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xc000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(value):return struct.pack('<I',value&0xffffffff)
def number(value):return b'\x17'+word(value)
def name(value):return b'\x16'+word(value)
def string_token(kind,data):return bytes([kind])+word(len(data)+1)+data+b'\0'
def text(data):
    at=alloc(len(data)+1);memory[at-BASE:at-BASE+len(data)+1]=data+b'\0';return at
def structure(entries):
    at=alloc(8);nodes=[alloc(16) for _ in entries];put(at+4,'<I',nodes[0] if nodes else 0)
    for i,(n,k,v) in enumerate(entries):put(nodes[i],'<BBHIII',k*2+(i&1),0x75,17,n,v,nodes[i+1] if i+1<len(nodes) else 0)
    return at
def array(kind,values):
    at=alloc(12);put(at,'<BBHII',0x55,kind,0x9876,len(values),0)
    if len(values)==1:put(at+8,'<I',values[0])
    elif values:
        items=alloc(len(values)*4);put(items,'<'+'I'*len(values),*values);put(at+8,'<I',items)
    return at
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,BUCKETS+4,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);memory[BUCKETS-BASE:BUCKETS-BASE+0x4004]=bytes(0x4004)
texts=[text(s) for s in [b'',b'levels/TR/TR.qb',b'LEVELS\\tr\\TR.QB',b'filename-\xff.qb']]
string=text(b'owned text');put(POOL,'<8s',b'pooled!\0')
pair=alloc(12);put(pair,'<3I',0xabcdef00,0x7f812345,0x40000000)
vector=alloc(16);put(vector,'<4I',0xabcdef01,0x3f800000,0xff812345,0x40400000)
blob=text(b'opaque script storage');nested=structure([(1,3,string),(2,12,array(3,[text(b'array-owned text'),POOL,0])),(0,13,55)])
values={3:string,4:string,5:pair,6:vector,7:blob,10:nested,12:array(10,[nested,0]),13:0x12345001}
nodes=[]
def symbol(n,k,v,flags=0x91,insert=True):
    at=alloc(20);bucket=BUCKETS+(n&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0] if insert else 0x12345678
    put(at,'<BBHIIII',flags,k,0x1234,n,0xdeadbeef,v,previous)
    if insert:put(bucket,'<I',at)
    nodes.append(at);return at
for n in [0,1,0x1001,0x2001,0xfff,0x1fff,0x80000a55,0xffffffff]:symbol(n,1,n)
original=symbol(0x12345001,1,17);alias=symbol(0x12346001,13,0x12345001);dangling=symbol(0x12347001,13,0xeeee2222)
target=symbol(0x12348001,1,42);absent=symbol(0x12349001,1,99,insert=False)
# Archived inputs and their token offsets are supplied by the independently
# verified token oracle, not by this new registration implementation.
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());token_bytes=(out/tokens['memory']).read_bytes()
assets=[];asset_cursor=BASE+0x20000
for a in tokens['assets']:
    data=token_bytes[a['address']-tokens['base']:a['address']-tokens['base']+a['size']]
    assert hashlib.sha256(data).hexdigest()==a['sha256']
    memory[asset_cursor-BASE:asset_cursor-BASE+len(data)]=data
    assets.append({**a,'original_address':a['address'],'address':asset_cursor,'filename':text(a['member'].encode())})
    asset_cursor=(asset_cursor+len(data)+19)&~3
assert asset_cursor<POOL
initial=bytes(memory);(out/'script-symbols-memory.bin').write_bytes(initial)
parser_fixture=json.loads((out/'script-parser-fixtures.json').read_text())
globals_=parser_fixture['globals']+[['thug_script_symbol_iteration_entry',0x6f363c,4],['thug_script_symbol_iteration_bucket',0x6f3640,4]]
defaults=parser_fixture['cases'][0]['globals']+[0,0];global_index={g[1]:i for i,g in enumerate(globals_)}
assert defaults[0]==POOL and defaults[4]==TABLE and defaults[6]==BUCKETS
functions={}
def bind(at,name,heap=False,result='void'):
    functions[hex(at)]={'name':'thug_script_'+name,'this':False,'result':result,'cleanup':0,'memory':heap}
bind(0x478cc0,'symbol_find',result='word');bind(0x478d60,'symbol_unlink');bind(0x478dc0,'symbol_insert');bind(0x478e50,'symbol_iterate',result='word')
bind(0x479110,'symbol_create',True,'word');bind(0x4711d0,'symbol_destroy',True)
bind(0x472240,'register_value',True,'word');functions['0x472240'].update(register_args={'ecx':0},stack_args=[1,2])
bind(0x46f960,'body_checksum',result='word');bind(0x478cf0,'resolve_symbol',result='word')
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=60000000,
 observe=[0x478cc0,0x478d60,0x478dc0,0x478e50,0x479110,0x4711d0,0x472240,0x46f960,0x478cf0,0x471860,0x471b00,0x4712b0,0x477140,0x477130,0x401b90,0x401af0])
for index,table in [(0x6f362c,0x6f3634),(0x6f2578,0x6f2580)]:oracle.cpu.mem_write(index,bytes(4));oracle.cpu.mem_write(table,bytes(8))
labels=[]
def case(calls,patches=(),changes=None,label='synthetic'):
    stages=oracle.case(calls,patches,changes);labels.append(label)
    for step in stages:
        step['global_float_indices']=[]
        for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
            if step['globals'][global_index[base]]&0xfe==4:step['global_float_indices'].append(global_index[base+8])
    return stages
def call(fn,*args):return (fn,0,list(args))
# Direct lookup retains aliases. Removing/reinserting collision-chain entries
# checks identity, head/middle/tail order, missing nodes and preserved metadata.
for n in [0,1,0xfff,0xffffffff,0x1001,0x2001,0x12345001,0x12346001,0x12347001,0x12349001,0xdeadbeef]:
    case([call(0x478cc0,n),call(0x478cf0,n)])
for node in nodes:
    n=struct.unpack_from('<I',memory,node-BASE+4)[0]
    case([call(0x478d60,node),call(0x478d60,node),call(0x478cc0,n),call(0x478dc0,node),call(0x478cc0,n)])
# Iterate every chain and sparse bucket, then exhaust and restart. The trailing
# readable slot is deliberately nonzero and must never be returned.
order=[]
for bucket in range(4096):
    node=struct.unpack_from('<I',memory,BUCKETS-BASE+bucket*4)[0]
    while node:order.append(node);node=struct.unpack_from('<I',memory,node-BASE+16)[0]
for empty in [False,True]:
    patches=[patch(BUCKETS+4096*4,'<I',0xdeadbeef)]
    expected=[] if empty else order
    if empty:patches.append([BUCKETS,bytes(16384).hex()])
    calls=[call(0x478e50,0)]+[call(0x478e50,p) for p in expected]+[call(0x478e50,0)]
    steps=case(calls,patches)
    assert [s['result'] for s in steps]==expected+[0]+[expected[0] if expected else 0]
# Creation prepends duplicates and preserves allocator poison in header bytes.
for n in [0,1,0xfff,0xffffffff,0x12345001,0x12346001,0xdeadbeef]:
    case([call(0x479110,n),call(0x478cc0,n),call(0x479110,n),call(0x478cc0,n),call(0x4711d0,HEAP+36),call(0x478cc0,n),call(0x4711d0,HEAP)])
# Every type byte and every flag byte participates in the disposal gate. Concrete
# ownership callees run unchanged; bit 2 only unlinks, preserving owned payloads.
for kind in range(256):
    value=values.get(kind,0x87654321)
    for flags in [0x91,0x95]:case([call(0x4711d0,target)],[patch(target,'<BBHIII',flags,kind,0x8765,0x12348001,0xabcdef01,value)])
for flags in range(256):
    case([call(0x4711d0,target)],[patch(target,'<BB',flags,1)])
for kind in [3,4,5,6,7,10]:
    case([call(0x4711d0,target)],[patch(target+1,'<B',kind),patch(target+12,'<I',0)])
for kind in [3,4]:case([call(0x4711d0,target)],[patch(target+1,'<B',kind),patch(target+12,'<I',POOL)])
# Global values transfer component payload ownership, record normalized source
# filename checksums, and leave existing same-name definitions linked underneath.
handled=[3,5,14,0x16,0x17,0x1a,0x1b,0x1c,0x1e,0x1f]
for token in range(256):
    if token not in handled:
        steps=case([call(0x472240,PROGRAM,0x12345001,texts[1]),call(0x4711d0,HEAP)],[[PROGRAM,(bytes([token])+bytes(32)).hex()]])
        assert steps[0]['result']==PROGRAM
literals=[name(0x12345001),number(-2147483648),b'\x1a'+word(0x7f812345),b'\x1a'+word(0x3fc00000),
 string_token(0x1b,b'owned\xff text'),string_token(0x1c,b'local'),b'\x1e'+word(0x7f812345)+word(0x40000000)+word(0xff812345),
 b'\x1f'+word(0x80000000)+word(0x3f800000),b'\x03'+name(7)+b'\x07'+number(42)+b'\x04',
 b'\x05'+number(1)+b'\x09'+number(2)+b'\x06',b'\x05\x06',b'\x0e'+number(2)+b'\x0b'+number(3)+b'\x0f',
 b'\x0e'+name(0x12346001)+b'\x0d'+number(3)+b'\x0f',b'\x0e'+number(1)+b'\x0c'+number(0)+b'\x0f']
for code in literals:
    for filename in texts:
        for intern in [0,1]:
            case([call(0x472240,PROGRAM,0x12345001,filename),call(0x478cc0,0x12345001),call(0x4711d0,HEAP),call(0x478cf0,0x12346001)],
                 [[PROGRAM,code.hex()]],{2:intern})
# Script hashes ignore actual line tokens, but include identical byte values
# inside strings/numeric payloads. END_SCRIPT is not part of the checksum.
base_code=number(0x240201)+string_token(0x1b,b'\x01\x02\x24text')+name(0x020124)
reference=None
for prefix in [b'',b'\x01',b'\x02'+word(0xffffffff)]:
    for middle in [b'',b'\x01\x01',b'\x02'+word(777)]:
        code=prefix+base_code[:5]+middle+base_code[5:]+b'\x24'
        step=case([call(0x46f960,PROGRAM)],[[PROGRAM,code.hex()]])[0]
        if reference is None:reference=step['result']
        assert step['result']==reference
case([call(0x46f960,PROGRAM)],[[PROGRAM,'24']])
next_tokens={p:n for fn,p,n in tokens['cases'] if fn=='0x46f690'}
skips={p:n for fn,p,n in tokens['cases'] if fn=='0x46fd60'}
script_ends={p:n for fn,p,n in tokens['cases'] if fn=='0x46f920'}
real=[]
for asset in assets:
    old=asset['original_address'];end=old+asset['size'];p=old;calls=[];boundaries=[];definitions=[];scripts=[]
    while p<end:
        token=token_bytes[p-tokens['base']]
        if token==0:assert p==end-1;break
        if token==0x23:
            scripts.append({'offset':p-old,'name':int.from_bytes(token_bytes[p-tokens['base']+2:p-tokens['base']+6],'little')})
            p=script_ends[p];continue
        if token==0x16:
            equals=next_tokens[p]
            while token_bytes[equals-tokens['base']] in [1,2]:equals=next_tokens[equals]
            assert token_bytes[equals-tokens['base']]==7
            value=next_tokens[equals]
            while token_bytes[value-tokens['base']] in [1,2]:value=next_tokens[value]
            vt=token_bytes[value-tokens['base']];next_p=skips[value] if vt in [3,5] else next_tokens[value]
            n=int.from_bytes(token_bytes[p-tokens['base']+1:p-tokens['base']+5],'little')
            calls.extend([call(0x472240,asset['address']+value-old,n,asset['filename']),call(0x478cc0,n)])
            boundaries.append(asset['address']+next_p-old);definitions.append({'name':n,'offset':p-old,'token':vt});p=next_p;continue
        assert token in [1,2,0x2b];p=next_tokens[p]
    if calls:
        stages=case(calls,label=asset['member']+' registration')
        assert [s['result'] for s in stages[::2]]==boundaries
        created=[s['result'] for s in stages[1::2]]
        case(calls+[call(0x4711d0,p) for p in reversed(created)],label=asset['member']+' registration and disposal')
    if scripts:
        stages=case([call(0x46f960,asset['address']+s['offset']+6) for s in scripts],label=asset['member']+' script checksums')
        for entry,stage in zip(scripts,stages):entry['checksum']=stage['result']
    real.append({'member':asset['member'],'sha256':asset['sha256'],'definitions':definitions,'scripts':scripts})
    print('Training globals/checksums:',asset['member'],len(definitions),len(scripts),flush=True)
scope='Eight original symbol-table/registration/checksum routines plus existing alias resolution. Direct lookup, prepend/unlink, shared iteration, allocation metadata, full typed disposal, global QB value registration and script-body hashing. Original concrete parsers/ownership/checksum callees execute; only successful generic heap services are instrumented. All 164 non-script definitions registered and disposed from eight archived training files; all 651 script bodies checksummed. Complete fixture/global memory and heap events compared; error pointers relocated by verified literal text. This does not yet register compressed script bodies, run the complete QB file loader or execute script commands. Valid acyclic graphs, terminating grammar and successful allocation are required.'
fixture={'base':BASE,'memory':'script-symbols-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope,'pointer_symbols':parser_fixture['pointer_symbols'],
 'pointer_globals':[global_index[0x6f2560]],'training':real,'case_labels':labels}
path=out/'script-symbols-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_symbols_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,'training':real,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-symbols-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
