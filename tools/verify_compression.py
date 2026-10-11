"""Original LZSS encoder trees, complete compressed bytes and heap/global state."""
import hashlib,json,random,struct,subprocess
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'compression.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x180000
CONTEXT,ADAPTER,MANAGER,DIAGNOSTICS,PRINT=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x400,BASE+0x600
INPUT,OUTPUT=BASE+0x1000,BASE+0x22000
PARENT,RIGHT,LEFT,WINDOW=BASE+0x80000,BASE+0x85000,BASE+0x8a000,BASE+0x8f000
LOG,HEAP=BASE+0xc0000,BASE+0xd0000
memory=bytearray(b'\xad'*SIZE);rng=random.Random(0x401700)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x110,'<I',MANAGER+0x300);put(MANAGER+0x124,'<I',MANAGER+0x200)
put(DIAGNOSTICS,'<I',0);put(PRINT,'<II',DIAGNOSTICS,0)
for i in range(4096):put(PARENT+i*4,'<I',4096)
for i in range(4097,4353):put(RIGHT+i*4,'<I',4096)
initial=bytes(memory);(out/'compression-memory.bin').write_bytes(initial)
globals_=[['thug_lzss_encoder',0x690f7c+offset,4,offset] for offset in range(0,36,4)]
defaults=[PARENT,RIGHT,LEFT,WINDOW,0x12345678,0x87654321,0xabcdef00,0xabcdef01,0xabcdef02]
functions={hex(fn):{'name':name,'this':False,'result':result,'cleanup':0,'memory':heap} for fn,name,result,heap in [
 (0x401600,'thug_lzss_initialize_encoder','void',True),(0x401290,'thug_lzss_insert','void',False),
 (0x4013e0,'thug_lzss_remove','void',False),(0x401700,'thug_lzss_encode_unchecked','word',True)]}
functions['0x401700']['stack_args']=[0,1,2,3]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=30000000,
 observe=[0x401600,0x401290,0x4013e0,0x401700],scope_entries={MANAGER+0x200:1,MANAGER+0x300:2})
pe=load();pointer_symbols=[]
for at,name,text in [(0x645378,'thug_lzss_format_input','     In : %ld bytes\n'),(0x645360,'thug_lzss_format_output','     Out: %ld bytes\n'),
 (0x645340,'thug_lzss_format_ratio','     Out/In: %.3f\n')]:
    assert pe.get_data(at-0x400000,len(text)+1)==text.encode()+b'\0';pointer_symbols.append([at,name,text])
def diagnostic(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);fmt=oracle.word(sp+4);count=oracle.word(DIAGNOSTICS)
    assert count<16 and fmt in [p[0] for p in pointer_symbols]
    kind=2 if fmt==0x645340 else 1
    cpu.mem_write(DIAGNOSTICS+16+count*16,struct.pack('<4I',fmt,kind,oracle.word(sp+8),oracle.word(sp+12) if kind==2 else 0))
    oracle.setword(DIAGNOSTICS,count+1)
    cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
labels=[];roundtrips=[]
def call(fn,*args):return (fn,0,list(args))
def case(calls,patches=(),changes=None,label='synthetic'):
    stages=oracle.case(calls,patches,changes);labels.append(label);previous=0
    for step in stages:
        # Losslessly coalesce adjacent changed words: tree allocations generate
        # many contiguous writes, which need not become separate JSON records.
        merged=[]
        for at,data in step['outputs']:
            if at==DIAGNOSTICS:
                count=int.from_bytes(bytes.fromhex(data),'little');step['callbacks']=count-previous;previous=count
            if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
            else:merged.append([at,data])
        step['outputs']=merged
    return stages
def encode(data,verbose=0,label='synthetic',offset=0):
    assert len(data)<0x20000 and len(data)+(len(data)+7)//8<0x25000
    stages=case([call(0x401700,INPUT+offset,OUTPUT+offset,len(data),verbose,PRINT)],[[INPUT+offset,data.hex()]],label=label)
    size=stages[0]['result'];assert size<=len(data)+(len(data)+7)//8
    assert bytes(oracle.cpu.mem_read(INPUT+offset,len(data)))==data
    roundtrips.append({'original':data.hex(),'encoded':bytes(oracle.cpu.mem_read(OUTPUT+offset,size)).hex(),'label':label})
# Initialization, mixed tree shapes, equal strings and replacement of full
# matches. Every insertion/removal compares the whole tree, sentinel and globals.
case([call(0x401600)])
patterns=[bytes(rng.randrange(256) for _ in range(4113)),b' '*4113,b'\xff'*4113,
 (bytes(range(256))*17)[:4113],(b'abababac'*515)[:4113],(b'abcdefghijklmnopqr'*229)[:4113]]
for index,data in enumerate(patterns):
    positions=list(dict.fromkeys([0,1,2,16,17,18,19,200,1000,4077,4078,4095]+[rng.randrange(4096) for _ in range(32)]))
    removals=positions[:];rng.shuffle(removals)
    calls=[call(0x401290,p) for p in positions]+[call(0x4013e0,p) for p in removals]+[call(0x4013e0,p) for p in positions[:4]]
    case(calls,[[WINDOW,data.hex()]],label='tree pattern '+str(index))
# Token groups, 18-byte match limit, ring wrap, incompressible input and long
# repetitions. Vary alignment and verbose's high bits as well as its low byte.
lengths=[0,1,2,3,7,8,9,17,18,19,31,127,255,256,257,4095,4096,4097,8192,20000,65536]
for n in lengths:
    for kind in range(5):
        data=bytes(rng.randrange(256) for _ in range(n)) if kind==0 else bytes([0x20 if kind==1 else 0xff])*n if kind<3 else (bytes(range(256))*((n+255)//256))[:n] if kind==3 else (b'abcdefabcdeabcab'*((n+14)//15))[:n]
        encode(data,[0,1,0x100,0x101,0xffffffff][kind],f'size {n} pattern {kind}',offset=kind%4)
# Repeated calls retain dangling addresses and old match-position state between
# operations; an empty call allocates/frees but emits no diagnostic messages.
blocks=[b'',b'A'*200,bytes(rng.randrange(256) for _ in range(999)),b'',b'BC']
patches=[];calls=[]
for i,data in enumerate(blocks):
    patches.append([INPUT+i*2048,data.hex()]);calls.append(call(0x401700,INPUT+i*2048,OUTPUT+i*2048,len(data),1,PRINT))
stages=case(calls,patches,label='repeated encoder lifecycle')
for i,(data,stage) in enumerate(zip(blocks,stages)):
    roundtrips.append({'original':data.hex(),'encoded':bytes(oracle.cpu.mem_read(OUTPUT+i*2048,stage['result'])).hex(),
                      'label':'repeated encoder lifecycle '+str(i)})
# Compress the exact script bodies the existing loader passes to registration:
# after SCRIPT/name through END_SCRIPT and its optional numbered-line token.
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());token_bytes=(out/tokens['memory']).read_bytes()
symbols=json.loads((out.parent/'script-symbols.json').read_text());ends={p:n for fn,p,n in tokens['cases'] if fn=='0x46f920'}
assets={a['member']:a for a in tokens['assets']};real=[]
for asset in symbols['training']:
    original=assets[asset['member']];start=original['address']
    assert hashlib.sha256(token_bytes[start-tokens['base']:start-tokens['base']+original['size']]).hexdigest()==asset['sha256']
    for script in asset['scripts']:
        p=start+script['offset'];body=token_bytes[p+6-tokens['base']:ends[p]-tokens['base']]
        encode(body,1 if len(real)%37==0 else 0,asset['member']+' '+hex(script['name']))
        real.append({'member':asset['member'],'name':script['name'],'input_size':len(body),'encoded_size':len(roundtrips[-1]['encoded'])//2,
                     'body_sha256':hashlib.sha256(body).hexdigest(),'encoded_sha256':hashlib.sha256(bytes.fromhex(roundtrips[-1]['encoded'])).hexdigest()})
    print('Training compression:',asset['member'],len(asset['scripts']),flush=True)
scope='Four original LZSS encoder routines: allocation/initialization, tree insertion/removal and complete encoding, including empty input and verbose low-byte behavior. Original concrete codec callees execute unchanged; successful heap/temporary-scope services and formatted diagnostic output are instrumented platform boundaries. Output bytes, all tree/window/fixture bytes, globals, allocation/release order and raw diagnostic arguments compared exactly. All 651 archived training script bodies included, with decoder roundtrips in WebAssembly. Diagnostic string formatting/OS output, allocator pools/failures, invalid buffers and concurrent calls are outside scope. This is a dependency of compressed script registration, not a completed QB loader or script executor.'
fixture={'base':BASE,'memory':'compression-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'pointer_symbols':pointer_symbols,
 'pointer_fields':[DIAGNOSTICS+16+i*16 for i in range(16)],
 'native_callback':{'module':'compression-diagnostics.wasm','export':'fixture_compression_print','slots':[PRINT+4]},
 'callback_counter':'diagnostic_callbacks','roundtrips':roundtrips,'training':real,'case_labels':labels}
path=out/'compression-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'compression-diagnostics.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/compression_diagnostics.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_compression_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,'training':real,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'compression-memory.bin',adapter,out/'script-values-memory.wasm']},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
