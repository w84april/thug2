"""Original QB parser call chains, synthetic grammar and archived training data."""
import hashlib,json,random,struct,subprocess
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-parser.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x700000
CONTEXT,ADAPTER,MANAGER,CALLBACK,SCRIPT=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x400,BASE+0x600
PROGRAM,BUCKETS,POOL,TABLE,LOG,HEAP=BASE+0xd000,BASE+0x10000,BASE+0x100000,BASE+0x120000,BASE+0x180000,BASE+0x500000
memory=bytearray(b'\xad'*SIZE);cursor=0x800;rng=random.Random(0x471860)
def alloc(size):
    global cursor
    at=BASE+cursor;cursor=(cursor+size+19)&~3;assert cursor<0xc000;return at
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(value):return struct.pack('<I',value&0xffffffff)
def scalar(token,value):return bytes([token])+word(value)
def text_token(token,text):return bytes([token])+word(len(text)+1)+text+b'\0'
def name(n):return scalar(0x16,n)
def number(n):return scalar(0x17,n)
def member(n,v):return name(n)+b'\x07'+v
def structure_token(*values):return b'\x03'+b'\x01'.join(values)+b'\x04'
def array_token(*values):return b'\x05'+b'\x09'.join(values)+b'\x06'
def expression(*values):return b'\x0e'+b''.join(values)+b'\x0f'
def argument(n):return b'\x2d'+name(n)
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x124,'<I',MANAGER+0x200);put(CALLBACK,'<4I',0,0xabcdef01,0x1234,0)
memory[BUCKETS-BASE:BUCKETS-BASE+0x4000]=bytes(0x4000)
def string(data):
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
pair=alloc(12);put(pair,'<3I',0xabcdef00,0x3f800000,0x40000000)
vector=alloc(16);put(vector,'<4I',0xabcdef01,0x3f800000,0x40000000,0x40400000)
string_a=string(b'parser text');nested=structure([(11,1,17),(22,3,string_a)])
values={0:0,1:17,2:0x3fc00000,3:string_a,4:string_a,5:pair,6:vector,7:string(b'1234567890123456789'),
 8:0x3f00100,9:0x3f00200,10:nested,11:77,12:array(1,[10,20,30]),13:0xeeee1111,20:nested,21:array(2,[0x3f800000])}
symbols=[];native_slots=[]
for kind,value in values.items():
    n=0xabc00001+kind*0x1000;at=alloc(20);bucket=BUCKETS+(n&0xfff)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
    put(at,'<BBHIIII',0x91,kind,0x1234,n,0x98765432,value,previous);put(bucket,'<I',at);symbols.append((n,kind,value))
    if kind==8:native_slots.append(at+12)
args=structure([(k+1,k,v) for k,v in values.items() if k!=8 and k!=9]+[(100,13,symbols[1][0]),(101,13,0xdead1234)])
target=structure([(77,1,9),(0,13,0xface)]);output=alloc(16);arrayout=alloc(12)
put(output,'<BBHIII',1,0x75,17,0x11223344,0,0x55667788);put(arrayout,'<BBHII',0x55,0,0x9876,0,0)
put(CONTEXT+24,'<I',target+4)
# Reuse archived bytes only after checking their hashes against the token oracle.
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());token_bytes=(out/tokens['memory']).read_bytes()
assets=[];asset_cursor=BASE+0x20000
for a in tokens['assets']:
    data=token_bytes[a['address']-tokens['base']:a['address']-tokens['base']+a['size']]
    assert hashlib.sha256(data).hexdigest()==a['sha256']
    memory[asset_cursor-BASE:asset_cursor-BASE+len(data)]=data
    assets.append({**a,'original_address':a['address'],'address':asset_cursor})
    asset_cursor=(asset_cursor+len(data)+19)&~3
assert asset_cursor<POOL
initial=bytes(memory);(out/'script-parser-memory.bin').write_bytes(initial)
globals_=[['thug_script_string_pool',0x6f3574,4],['thug_script_string_pool_size',0x6f357c,4],
 ['thug_script_string_interning',0x6f3570,1],['thug_script_string_cursor',0x6f3578,4],
 ['thug_script_string_entries',0x6f3580,4],['thug_script_string_count',0x6f3584,4],['thug_script_symbol_buckets',0x6f3624,4]]
defaults=[POOL,0x20000,0,POOL,TABLE,0,BUCKETS]
for export,original,size,fill in [('thug_expression_temporary',0x6f2348,16,0),('thug_script_parser_expression',0x6f2370,504,0),('thug_script_parser_value',0x6f2568,16,0)]:
    for offset in range(0,size,4):globals_.append([export,original+offset,4,offset]);defaults.append(fill)
for export,original in [('thug_random_state',0x690fd4),('thug_random_alternate_state',0x690fc8)]:
    for offset,value in zip(range(0,12,4),[0x12345678,0x98765432,0x31415926]):globals_.append([export,original+offset,4,offset]);defaults.append(value)
for export,original,value in [('thug_current_script',0x6f3530,SCRIPT),('thug_script_branch_first',0x6f2358,0),('thug_script_branch_last',0x6f235c,0),('thug_script_branch_count',0x6f2360,0)]:
    globals_.append([export,original,4]);defaults.append(value)
global_index={g[1]:i for i,g in enumerate(globals_)};functions={}
def bind(at,name,heap=True):functions[hex(at)]={'name':'thug_script_'+name,'this':False,'result':'word','cleanup':0,'memory':heap}
bind(0x470130,'parse_named_value');functions['0x470130'].update(register_args={'ecx':0,'edx':1},stack_args=[2,3])
bind(0x4706f0,'parse_component_value');bind(0x470f30,'parse_parameters');bind(0x4712b0,'parse_expression')
bind(0x471860,'parse_structure');bind(0x471b00,'parse_array');bind(0x479730,'component_resolve',False);functions['0x479730']['result']='void'
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=60000000,
 observe=[0x470130,0x4706f0,0x470f30,0x4712b0,0x471860,0x471b00,0x479730,0x470c60,0x46d450,0x46fbd0,0x477920,0x478cf0,0x6236fc])
oracle.cpu.mem_write(0x6f2578,bytes(4));oracle.cpu.mem_write(0x6f2580,bytes(8))
def callback(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);parameters=oracle.word(sp+4);script=oracle.word(sp+8);first=oracle.word(parameters+4)
    count=oracle.word(CALLBACK);kind=cpu.mem_read(first,1)[0]>>1 if first else 0
    data=[parameters,script,first,oracle.word(first+4) if first else 0,kind,oracle.word(first+8) if first else 0]
    cpu.mem_write(CALLBACK+16+count*24,struct.pack('<6I',*data));oracle.setword(CALLBACK,count+1)
    if kind==1:oracle.setword(first+8,data[5]^oracle.word(CALLBACK+8))
    cpu.reg_write(UC_X86_REG_EAX,oracle.word(CALLBACK+4));cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,callback,begin=0x3f00100,end=0x3f00100)
case_labels=[]
def case(calls,patches=(),changes=None,label='synthetic'):
    steps=oracle.case(calls,patches,changes);case_labels.append(label)
    # Observe callback counts and typed global float fields, not arbitrary words.
    previous=0
    for step in steps:
        for a,data in step['outputs']:
            if a==CALLBACK:
                count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-previous;previous=count
        step['global_float_indices']=[]
        for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
            if step['globals'][global_index[base]]&0xfe==4:step['global_float_indices'].append(global_index[base+8])
    return steps
def run(fn,code,arguments=args,name_value=55,extra=(),changes=None,label='synthetic'):
    assert len(code)<0x3000
    a=[PROGRAM,name_value,target,arguments] if fn==0x470130 else [PROGRAM,arguments,output] if fn in [0x4706f0,0x4712b0] else [arrayout if fn==0x471b00 else target,PROGRAM,arguments]
    return case([(fn,0,a)],[[PROGRAM,code.hex()],*extra],changes,label)
# Every unsupported single-value token has a defined cursor/unchanged-output rule.
handled=[3,5,0x16,0x17,0x1a,0x1b,0x1c,0x1e,0x1f,0x23,0x2c,0x2d,0x30,0x38]
for token in range(256):
    if token not in handled:
        for fn in [0x470130,0x4706f0]:run(fn,bytes([token])+bytes(20))
words=[0,1,0xffffffff,0x80000000,0x7fffffff,16777217,0x3c23d709,0x3c23d70a,0xbc23d709,0x7f800000,0x7f812345,0x7fc12345]
for fn in [0x470130,0x4706f0]:
    for token in [0x16,0x17,0x1a]:
        for value in words:run(fn,scalar(token,value))
    for token in [0x1b,0x1c]:
        for text in [b'',b'hello',b'\xffhello',b'a'*199]:
            for intern in [0,1]:run(fn,text_token(token,text),changes={2:intern})
    for token in [0x1e,0x1f]:
        for value in words:
            for n in [55,0x9d2d0915]:run(fn,bytes([token])+word(value)*(3 if token==0x1e else 2),name_value=n)
    for arg in [0,args]:
        for n in [0,55]:
            run(fn,b'\x2c',arguments=arg,name_value=n)
            for key in [1,2,4,11,13,21,100,101,999]:run(fn,argument(key),arguments=arg,name_value=n)
    for stream in [0x30,0x38]:
        for lo,hi in [(0,0x41200000),(0x3fa00000,0x411c0000),(0xc0a00000,0x40a00000)]:
            run(fn,bytes([stream,0x1f])+word(lo)+word(hi))
    for suffix in [b'',b'\x01',b'\x02'+word(123)]:
        run(fn,b'\x23'+name(0x12345678)+number(17)+text_token(0x1b,b'script')+b'\x24'+suffix)
# In-place symbol resolution preserves metadata and ignores unsupported types.
for n,k,v in symbols:
    for tag in [0,1,2,26,27,255]:
        case([(0x479730,0,[output])],[patch(output,'<BBHIII',tag,0x75,17,7,n,0xabcdef01)])
# All array categories, inline/multiple/empty values, mixed numeric conversion,
# nested containers, line tokens and preservation of old storage for empty input.
literals=[name(7),number(-3),scalar(0x18,0xffffffff),scalar(0x1a,0x3fc00000),text_token(0x1b,b'abc'),text_token(0x1c,b'local'),
 b'\x1e'+word(0x7f812345)+word(0x40000000)+word(0x40400000),b'\x1f'+word(0x3f800000)+word(0x40000000),
 structure_token(member(1,number(17)),name(7)),array_token(number(1),number(2))]
for literal in literals:
    for count in [0,1,3]:run(0x471b00,array_token(*([literal]*count)))
for values_ in [(number(16777217),scalar(0x1a,0x3fc00000)),(scalar(0x1a,0x7f812345),number(-2147483648)),(scalar(0x18,0xffffffff),scalar(0x1a,0))]:run(0x471b00,array_token(*values_))
run(0x471b00,b'\x05\x01\x02'+word(777)+number(1)+b'\x09\x01'+number(2)+b'\x06')
run(0x471b00,array_token(),extra=[patch(arrayout,'<BBHII',0x55,1,0x9876,1,17)])
# Structures/parameter lists exercise named values, flags, splicing, replacement,
# anonymous braces and expressions. The two parsers treat line breaks differently.
body=member(1,number(17))+name(7)+member(1,scalar(0x1a,0x3fc00000))+member(2,array_token(number(1),number(2)))
for code in [body,structure_token(member(5,number(3)))+body,member(3,structure_token(body)),
 member(4,expression(number(3),b'\x0b',number(4))),expression(b'\x2c'),b'\x2c'+argument(11),argument(100),b'\x09'+body]:
    for fn in [0x470130,0x4706f0,0x471860]:run(fn,structure_token(code))
    run(0x470f30,code+b'\x01')
run(0x471860,b'\x03'+name(123)+b'\x01\x07\x02'+word(777)+number(42)+b'\x04')
for end in [b'\0',b'\x01',b'\x02'+word(99),b'\x0f']:run(0x470f30,body+end)
# Complete expressions: globals, borrowed arguments, member names, indexing,
# adjacent negative literals, early termination and nested shared scratch state.
for n,k,v in symbols:
    if k!=8:run(0x4712b0,expression(name(n)))
for key in [2,3,4,6,7,11,13,21,22,100,101,999]:run(0x4712b0,expression(argument(key)))
for op in [7,8,10,11,12,13,18,20,50,51]:run(0x4712b0,expression(number(17),bytes([op]),number(3)))
for code in [expression(number(3),number(-2)),expression(number(3),number(2)),expression(number(3),scalar(0x1a,0xbf000000)),
 expression(number(3),scalar(0x1a,0x7fc12345)),expression(number(3),expression(number(2))),
 expression(number(3),b'\x0b',expression(number(4),b'\x0d',number(5))),expression(b'\x2c'),
 expression(argument(11),b'\x08',name(11)),expression(name(next(n for n,k,v in symbols if k==12)),b'\x05',number(1),b'\x06'),
 expression(structure_token(member(1,expression(number(2),b'\x0b',number(3))))),expression(number(4),b'\x01\x02'+word(77),b'\x0b',number(5))]:
 run(0x4712b0,code)
# Native predicates are an explicit callback boundary. They receive the actual
# parsed parameter graph and current script; high return bits must be discarded.
native_name=next(n for n,k,v in symbols if k==8)
for code in [expression(name(native_name)),expression(name(native_name),member(1,number(17))),
 expression(name(native_name),member(1,expression(number(2),b'\x0b',number(3))))]:
    for returned in [0,1,0xff,0xabcdef00,0xabcdef01]:run(0x4712b0,code,extra=[patch(CALLBACK+4,'<I',returned)])
# Long/short jump resolution reaches the same real parser, including lookahead.
run(0x471860,b'\x03\x2e'+word(3)+b'xxx'+member(1,number(17))+b'\x04')
run(0x470f30,b'\x49'+struct.pack('<H',4)+b'xx'+member(1,number(17))+b'\x01')
# Array sizing and construction independently revisit each random choice. Use
# equal-sized alternatives with a shared terminator, including cached choices,
# so every generated program stays valid even when the two passes disagree.
def choice(token,alternatives):
    count=len(alternatives);data=bytearray(5+count*6);jumps=[]
    struct.pack_into('<BI',data,0,token,count)
    struct.pack_into('<'+'h'*count,data,5,*range(1,count+1))
    for i,alternative in enumerate(alternatives):
        offset=5+count*2+i*4
        struct.pack_into('<I',data,offset,len(data)-offset-4)
        data.extend(alternative);jumps.append(len(data)+1);data.extend(b'\x2e'+bytes(4))
    for offset in jumps:struct.pack_into('<I',data,offset,len(data)-offset-4)
    return bytes(data)
for token in [0x2f,0x37,0x40,0x41]:
    for alternatives in [[number(i) for i in [11,22,33]],
      [scalar(0x1a,i) for i in [0x3f800000,0x40000000,0x40400000]],
      [structure_token(member(1,number(i))) for i in [11,22,33]],
      [array_token(number(i),number(i+1)) for i in [11,22,33]]]:
        for _ in range(4):
            changes={global_index[at]:rng.randrange(2**32) for at in [0x690fd4,0x690fd8,0x690fdc,0x690fc8,0x690fcc,0x690fd0]}
            run(0x471b00,b'\x05'+choice(token,alternatives)+b'\x06',changes=changes,label='two-pass array random choices')
# Top-level training definitions and complete script bodies. Expected boundaries
# come from the independent original-instruction token oracle. This constructs
# parameter graphs, not the game's global registration/loading path.
next_tokens={p:n for fn,p,n in tokens['cases'] if fn=='0x46f690'}
skips={p:n for fn,p,n in tokens['cases'] if fn=='0x46fd60'}
script_ends={p:n for fn,p,n in tokens['cases'] if fn=='0x46f920'}
real_definitions=[]
for asset in assets:
    old=asset['original_address'];end=old+asset['size'];p=old;calls=[];expected=[];definitions=[]
    while p<end:
        token=token_bytes[p-tokens['base']]
        if token==0:assert p==end-1;break
        if token==0x23:
            next_p=script_ends[p];n=int.from_bytes(token_bytes[p-tokens['base']+2:p-tokens['base']+6],'little')
            calls.append((0x470130,0,[asset['address']+p-old,0,target,args]));expected.append(asset['address']+next_p-old)
            definitions.append({'offset':p-old,'name':n,'token':token,'bytes':next_p-p});p=next_p;continue
        if token==0x16:
            equals=next_tokens[p]
            while token_bytes[equals-tokens['base']] in [1,2]:equals=next_tokens[equals]
            assert token_bytes[equals-tokens['base']]==7,(asset['member'],p-old)
            value=next_tokens[equals]
            while token_bytes[value-tokens['base']] in [1,2]:value=next_tokens[value]
            vt=token_bytes[value-tokens['base']]
            assert vt in [3,5,0x16,0x17,0x1a,0x1b,0x1c,0x1e,0x1f],(asset['member'],value-old,vt)
            next_p=skips[value] if vt in [3,5] else next_tokens[value]
            n=int.from_bytes(token_bytes[p-tokens['base']+1:p-tokens['base']+5],'little')
            calls.append((0x470130,0,[asset['address']+value-old,n,target,args]));expected.append(asset['address']+next_p-old)
            definitions.append({'offset':p-old,'name':n,'token':vt,'bytes':next_p-p});p=next_p;continue
        assert token in [1,2,0x2b],(asset['member'],p-old,token)
        p=next_tokens[p]
    if calls:
        print('Training definitions:',asset['member'],len(calls),flush=True)
        stages=case(calls,label=asset['member'])
        assert [s['result'] for s in stages]==expected,asset['member']
        real_definitions.append({'member':asset['member'],'sha256':asset['sha256'],'definitions':definitions})

scope='Six original mutually recursive QB parsers plus in-place checksum resolution. Complete value, structure, array, parameter and expression paths, shared expression globals, both random-range streams, native predicate dispatch and archived training definitions/script bodies. Real concrete callees; generic successful heap/predicate callbacks instrument platform boundaries. Full fixture/global bytes, return cursors and heap events compared; typed global NaNs by classification. This does not recover global symbol registration, script command execution, input or rendering. Valid terminating grammar and successful allocation are required.'
previous=json.loads((out/'script-expression-fixtures.json').read_text())
fixture={'base':BASE,'memory':'script-parser-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,
 'functions':functions,'float_fields':[],'cases':oracle.cases,'scope':scope,'pointer_symbols':previous['pointer_symbols'],
 'pointer_globals':[global_index[0x6f2560]],'native_callback':{'module':'script-parser-callback.wasm','export':'fixture_parser_predicate','slots':native_slots},
 'callback_counter':'native_predicate_callbacks','training_definitions':real_definitions,'case_labels':case_labels}
path=out/'script-parser-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-parser-callback.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_parser_callback.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_parser_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,'training_definitions':real_definitions,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-parser-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
