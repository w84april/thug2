"""Original loop/switch handlers and script-return state restoration."""
import hashlib,json,random,struct,subprocess
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-control.json';report_path.unlink(missing_ok=True)
prior=json.loads((out/'script-cache-fixtures.json').read_text());parser=json.loads((out/'script-parser-fixtures.json').read_text())
BASE=prior['base'];memory=bytearray((out/prior['memory']).read_bytes());SIZE=len(memory)
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
POOL,ENTRY,CACHE,CTABLE,CBUCKETS=BASE+0x1000,BASE+0x2000,BASE+0x5000,BASE+0x5100,BASE+0x5200
SCRIPT,PARAMS,ARGS,RETURNS=BASE+0x5800,BASE+0x5a00,BASE+0x5a10,BASE+0x5a20
FRAMES,CONTROL,OWNER,OTHER,PREVIOUS,NEXT,OTHERREF=BASE+0x6800,BASE+0x7000,BASE+0x8000,BASE+0x8100,BASE+0x8200,BASE+0x8220,BASE+0x8240
PROGRAM,LOG,HEAP,BUCKETS=BASE+0x40000,BASE+0x60000,BASE+0x80000,BASE+0x10000
rng=random.Random(0x473c60);cursor=BASE+0x9000
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(v):return struct.pack('<I',v&0xffffffff)
def half(v):return struct.pack('<H',v&0xffff)
def name(n):return b'\x16'+word(n)
def number(n):return b'\x17'+word(n)
def floating(n):return b'\x1a'+word(n)
def text_token(text,kind=0x1b):return bytes([kind])+word(len(text)+1)+text+b'\0'
def allocate(size):
    global cursor
    p=cursor;cursor=(cursor+size+19)&~3;assert cursor<BASE+0x10000;return p
def string(text):
    p=allocate(len(text)+1);memory[p-BASE:p-BASE+len(text)+1]=text+b'\0';return p
def component(kind,n,value,next=0):
    p=allocate(16);put(p,'<BBHIII',kind*2+1,0x75,0x9876,n,value,next);return p
COUNT=0xabcdef01
param_member=component(3,77,string(b'old parameters'));arg_member=component(1,COUNT,3)
return_member=component(3,COUNT,string(b'returned text'))
for at,first in [(PARAMS,param_member),(ARGS,arg_member),(RETURNS,return_member)]:put(at,'<II',0xabcdef01,first)
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244)
put(SCRIPT+12,'<3I',PROGRAM,PARAMS,ARGS);put(SCRIPT+0x2c,'<I',SCRIPT+0x1c);put(SCRIPT+0x94,'<I',SCRIPT+0x34)
put(SCRIPT+0x98,'<IB3sIIIII',0x11223344,0x9b,b'\x98\x76\x54',0x7f812345,3,0x55667788,OWNER,0x12345678)
put(SCRIPT+0xb4,'<B',0xa5);put(SCRIPT+0xc8,'<I',5)
put(OWNER,'<6I',0x12345000,0,0,0,0,1);put(OTHER,'<6I',0x12345001,OTHERREF,0,0,0,2)
put(OTHERREF,'<3I',OTHER,0,0)
put(FRAMES,'<12I',0xeeee0000,RETURNS,PROGRAM+0x100,OTHER,CONTROL,0x12345678,OTHER,0xff812345,0x87654321,0xaabbccdd,0xabcdef03,0xadadad03)
put(CONTEXT+24,'<I',SCRIPT+0xc)
initial=bytes(memory);(out/'script-control-memory.bin').write_bytes(initial)
globals_=parser['globals'][:];defaults=parser['cases'][0]['globals'][:]
defaults[:7]=[BASE+0x100000,0x20000,0,BASE+0x100000,BASE+0x120000,0,BUCKETS]
for g,v in zip(prior['globals'],prior['cases'][0]['globals']):
    if g[0]!='thug_script_symbol_buckets':globals_.append(g);defaults.append(v)
index={g[1]:i for i,g in enumerate(globals_)}
defaults[index[0x6f3558]]=CACHE;defaults[index[0x6f3530]]=SCRIPT
functions={}
def bind(at,n,this=True,heap=True,result='void',cleanup=0):functions[hex(at)]={'name':'thug_script_'+n,'this':this,'memory':heap,'result':result,'cleanup':cleanup}
bind(0x46f800,'read_half',False,False,'half');bind(0x46f850,'skip_lines',False,False,'word')
bind(0x472a70,'skip_switch',heap=False);bind(0x473220,'begin_loop');bind(0x472ab0,'repeat_loop');bind(0x472b50,'break_loop')
bind(0x473c60,'select_case');bind(0x473e70,'return',result='byte',cleanup=4)
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=30000000,
 observe=[int(k,16) for k in functions]+[0x470f30,0x476630,0x477090,0x4773e0,0x4791a0,0x475d60,0x4637c0,0x4637e0,0x478540],
 scope_entries={BASE+0x6000:1,MANAGER+0x300:2})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
labels=[]
def call(fn,*args):return (fn,SCRIPT,list(args))
def static(fn,*args):return (fn,0,list(args))
def case(calls,patches=(),changes=None,label='synthetic'):
    stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
    for step in stages:
        step['global_float_indices']=[]
        for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
            if step['globals'][index[base]]&0xfe==4:step['global_float_indices'].append(index[base+8])
    return stages
# Unaligned halfword reads do not promise EAX's upper half. Line tokens are
# consumed without interpreting numbered-line payloads or any following token.
for offset in range(4):
    for value in [0,1,255,256,32767,32768,65535,*[rng.randrange(65536) for _ in range(12)]]:
        case([static(0x46f800,PROGRAM+offset)],[[PROGRAM+offset,half(value).hex()]])
for following in [0,3,0x16,0x20,0x21,0x24,0x3c,0x49,255]:
    for prefix in [b'',b'\x01',b'\x02'+word(0x020101),b'\x01\x02'+word(777)+b'\x01\x01']:
        code=prefix+bytes([following])+bytes(16)
        steps=case([static(0x46f850,PROGRAM)],[[PROGRAM,code.hex()]])
        assert steps[0]['result']==PROGRAM+len(prefix)
for code in [b'\x3d',number(0x3d3c)+b'\x3d',b'\x3c\x01\x3c\x3d\x3d\x3d',text_token(b'\x3c\x3d')+b'\x3c\x3d\x3d']:
    case([call(0x472a70)],[[PROGRAM,code.hex()]])
# Inline first loop, second-loop spill, heap reuse and saved-loop relocation.
# Misaligned saved pointers exercise the original round-down address arithmetic.
for depth in [0,1,2,16,0x80000000]:
    patches=[patch(SCRIPT+0x18,'<I',SCRIPT+0x1c),patch(SCRIPT+0x30,'<I',depth),patch(SCRIPT+0x94,'<I',FRAMES)]
    patches += [patch(FRAMES+i*48+16,'<I',p) for i,p in enumerate([0,SCRIPT+0x1c,SCRIPT+0x1d,SCRIPT+0x1b]*4)]
    case([call(0x473220)],patches)
for top in [0,CONTROL,CONTROL+16,CONTROL+128]:case([call(0x473220)],[patch(SCRIPT+0x18,'<I',top),patch(SCRIPT+0x2c,'<I',CONTROL)])
case([call(0x473220)]*10,[[PROGRAM,bytes([0x20]*10).hex()]])
# Empty loop bodies allow real begin/repeat calls in sequence. Count is evaluated
# once; zero and negative counts retain unsigned decrement behavior.
for operand in [b'',*[number(v) for v in [0,1,2,3,0xffffffff,0x80000000]],floating(0x40000000),
                b'\x2d'+name(COUNT),b'\x0e'+number(2)+b'\x0b'+number(3)+b'\x0f',text_token(b'no count')]:
    code=b'\x20\x21'+operand+b'\x01\x24'
    repeat_count=1 if operand in [number(1)] else 2 if operand in [number(2),floating(0x40000000)] else 3
    case([call(0x473220)]+[call(0x472ab0)]*repeat_count,[[PROGRAM,code.hex()]])
for finite in [0,1,255]:
    for count in [0,1,2,0xffffffff]:
        for top in [CONTROL,CONTROL+16]:
            patches=[patch(SCRIPT+0x18,'<I',top),patch(SCRIPT+0x2c,'<I',CONTROL),patch(top,'<2IBBH I',PROGRAM+100,PROGRAM+200,finite,0,0x7654,count)]
            case([call(0x472ab0)],patches)
for nested in [b'',b'\x20\x21'+number(7)+b'\x01',b'\x20\x20\x21\x21',text_token(b'\x20\x21')]:
    for operand in [b'',number(5),b'\x2d'+name(COUNT)]:
        code=b'\x22'+nested+b'\x21'+operand+b'\x01\x24'
        for top in [CONTROL,CONTROL+16]:
            case([call(0x472b50)],[[PROGRAM,code.hex()],patch(SCRIPT+0x18,'<I',top),patch(SCRIPT+0x2c,'<I',CONTROL)])
def switch(selector,values,default=True,chain=False,nested=False):
    code=bytearray(b'\x3c'+selector+b'\x01');headers=[];bodies=[]
    if nested:code+=b'\x3c'+number(123)+b'\x01\x3c\x3d\x3d\x01'
    for i,value in enumerate(values):
        headers.append(len(code));code+=b'\x3e\x49\0\0'+value+b'\x02'+word(i+10)
        if not chain or i+1==len(values):
            bodies.append(len(code));code+=name(0xeeee0000+i)+b'\x01'
        else:bodies.append(None)
        code+=b'\x49\0\0'
    end=len(code)
    if default:code+=b'\x3f\x49\0\0'+name(0xdddd0000)+b'\x01'
    code+=b'\x3d\x24'
    for i,h in enumerate(headers):struct.pack_into('<H',code,h+2,(headers[i+1] if i+1<len(headers) else end)-(h+2))
    return bytes(code),bodies,end
# Switch matching uses real component ownership/copy/equality. Equal-looking
# arrays/structures remain distinct objects in this executable's comparison.
values=[number(1),number(2),floating(0x40000000),text_token(b'text'),text_token(b'text',0x1c),
 b'\x1f'+word(0x3f800000)+word(0x40000000),b'\x1e'+word(0x3f800000)+word(0x40000000)+word(0x40400000),
 b'\x05'+number(1)+b'\x06',b'\x03'+name(COUNT)+b'\x07'+number(3)+b'\x04',name(0xeeee9999),b'']
for selector in values:
    for default in [False,True]:
        code,_,_=switch(selector,values[:],default,nested=True)
        case([call(0x473c60)],[[PROGRAM,code.hex()]])
for selector in [number(1),number(2),number(3),number(4),b'\x2d'+name(COUNT)]:
    code,bodies,end=switch(selector,[number(1),number(2),number(3)],chain=True)
    case([call(0x473c60)],[[PROGRAM,code.hex()]])
    assert oracle.word(SCRIPT+12)==PROGRAM+(end+4 if selector==number(4) else bodies[-1])
for bits in [0,0x80000000,0x7f800000,0xff800000,0x7fc12345,0x7f812345]:
    code,_,_=switch(floating(bits),[floating(bits),number(0)])
    case([call(0x473c60)],[[PROGRAM,code.hex()]])
# Return restores a suspended frame, including owner reference lists, caller
# arguments and wait bits. Zero wait kind preserves the callee's other wait data.
def return_patches(depth=1,old_owner=OWNER,new_owner=OTHER):
    p=[patch(SCRIPT+0x30,'<I',depth),patch(SCRIPT+0x94,'<I',FRAMES),patch(SCRIPT+0xbc,'<3I',old_owner,0,0)]
    if old_owner:p.append(patch(old_owner+4,'<I',SCRIPT+0xbc))
    if depth:
        at=FRAMES+(depth-1)*48
        p.append([at,initial[FRAMES-BASE:FRAMES-BASE+48].hex()]);p.append(patch(at+12,'<I',new_owner))
    p += [patch(POOL+16,'<II',1,ENTRY+20),patch(ENTRY,'<5I',5,PROGRAM+0x1000,1,0,0),patch(CTABLE+8,'<I',1),patch(CBUCKETS+5*12,'<3I',5,ENTRY,0)]
    return p
for depth in [0,1,2,16]:
    for old_owner,new_owner in [(0,0),(OWNER,0),(0,OTHER),(OWNER,OTHER),(OWNER,OWNER)]:
        for immediate in [0,1]:
            case([call(0x473e70,0)],return_patches(depth,old_owner,new_owner)+[patch(CACHE+32,'<B',immediate)])
for wait in range(16):
    for flags in [0,1,2,255]:
        case([call(0x473e70,0)],return_patches()+[patch(FRAMES+40,'<IB',0x12345670|wait,flags),patch(SCRIPT+0xb4,'<B',flags)])
for bits in [0,0x80000000,0x7f812345,0xff812345,0x7fc12345,0x3f800000]:
    case([call(0x473e70,0)],return_patches()+[patch(FRAMES+28,'<I',bits)])
for depth in [0,1]:
    # Distinct return structure merges into the surviving caller arguments.
    returned=RETURNS if not depth else PARAMS
    case([call(0x473e70,returned)],return_patches(depth))
case([call(0x473e70,0)],return_patches()+[patch(OWNER+4,'<I',PREVIOUS),patch(PREVIOUS,'<3I',OWNER,0,SCRIPT+0xbc),
     patch(SCRIPT+0xc0,'<2I',PREVIOUS,NEXT),patch(NEXT,'<3I',OWNER,SCRIPT+0xbc,0)])
print('Synthetic script-control checks:',len(oracle.cases),flush=True)
# Use original archived token offsets for nested-switch skipping and actual
# literal repeat-count handlers. No native game command is executed here.
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());raw=(out/tokens['memory']).read_bytes()
next_tokens={p:n for fn,p,n in tokens['cases'] if fn=='0x46f690'};ends={p:n for fn,p,n in tokens['cases'] if fn=='0x46f920'}
symbol_report=json.loads((out.parent/'script-symbols.json').read_text());asset_map={a['member']:a for a in tokens['assets']}
training=[]
for asset in symbol_report['training']:
    a=asset_map[asset['member']];start=a['address'];switches=0;repeats=0;begins=0
    for script_entry in asset['scripts']:
        p=start+script_entry['offset'];body_start=p+6;end=ends[p];body=raw[body_start-tokens['base']:end-tokens['base']]
        p=body_start
        while p<end:
            token=raw[p-tokens['base']]
            if token==0x3c:
                case([call(0x472a70)],[[PROGRAM,body.hex()],patch(SCRIPT+12,'<I',PROGRAM+p-body_start+1)],label=asset['member']+' nested switch skip')
                switches+=1
            if token==0x20:
                case([call(0x473220)],[[PROGRAM,body.hex()],patch(SCRIPT+12,'<I',PROGRAM+p-body_start)],label=asset['member']+' loop begin')
                begins+=1
            if token==0x21:
                q=next_tokens[p]
                if raw[q-tokens['base']]==0x17 and raw[next_tokens[q]-tokens['base']] in [1,2,0x24]:
                    patches=[[PROGRAM,body.hex()],patch(SCRIPT+12,'<I',PROGRAM+p-body_start),patch(SCRIPT+0x18,'<I',CONTROL),
                             patch(SCRIPT+0x2c,'<I',CONTROL),patch(CONTROL,'<2IBBH I',PROGRAM,0,0,1,0x7654,0)]
                    case([call(0x472ab0)],patches,label=asset['member']+' literal repeat count');repeats+=1
            p=next_tokens[p]
    training.append({'member':asset['member'],'sha256':asset['sha256'],'switch_skips':switches,'loop_begins':begins,'literal_repeats':repeats})
    print('Archived control tokens:',asset['member'],switches,begins,repeats,flush=True)
scope='Eight original routines: unaligned halfword/line-token helpers, nested-switch skipping, loop begin/repeat/break, switch selection and script return. Complete concrete parser, value ownership/equality, cache release and object-reference callees execute; successful generic heap/scopes are instrumented, with script-value pools disabled. Tests cover inline-to-heap loop relocation and suspended frames, first-visit count evaluation, unsigned count wrap, nested break scanning, grouped switch labels, selector lifetime, wait-state/raw-float restoration, owner relinking and return values. Archived switch/loop tokens are included without executing native commands; repeat-count parsing is covered by synthetic cases. Every fixture byte/global and heap event is compared; verified error literals are relocated and only typed global NaNs permit classification. Requires valid initialized frames, bounded stacks, terminating grammar and successful allocation. This does not yet recover call setup, command dispatch or the complete executor.'
fixture={'base':BASE,'memory':'script-control-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'case_labels':labels,'training':training,'pointer_symbols':parser['pointer_symbols'],
 'pointer_globals':[index[0x6f2560]]}
path=out/'script-control-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_control_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),
 'scope':scope,'training':training,'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-control-memory.bin',out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
