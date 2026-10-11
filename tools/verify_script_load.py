"""Whole QB-buffer loading, name tables and reversible symbol replacement."""
import hashlib,json,random,struct,subprocess,zlib
from collections import Counter
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EIP,UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-load.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1000000,0x1e00000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x60,BASE+0x100
POOL,ENTRIES,CACHE,CTABLE,CBUCKETS,HSTATE,GAP,FREELIST=BASE+0x1000,BASE+0x2000,BASE+0x5000,BASE+0x5100,BASE+0x5200,BASE+0x6000,BASE+0x6100,BASE+0x6200
TLS,LOCALE,FILENAME,TEXT,SYMBOL,OLD,STORAGE=BASE+0x7000,BASE+0x7200,BASE+0x7400,BASE+0x7800,BASE+0x7c00,BASE+0x7c20,BASE+0x7d00
BUCKETS,PROGRAM,LOCAL,DEBUG,ASSETS,STRINGS,LOG,HEAP=BASE+0x10000,BASE+0x20000,BASE+0x30000,BASE+0x100000,BASE+0x600000,BASE+0x690000,BASE+0x700000,BASE+0xb00000
memory=bytearray(b'\xad'*SIZE)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(n):return struct.pack('<I',n&0xffffffff)
def name(n):return b'\x16'+word(n)
def number(n):return b'\x17'+word(n)
def definition(n,value):return name(n)+b'\x07'+value+b'\x01'
def script(n,body):return b'\x23'+name(n)+body
def name_record(n,text):return b'\x2b'+word(n)+text+b'\0'
def directive(n):return b'\x45'+name(n)
def crc(data):return zlib.crc32(data.lower().replace(b'/',b'\\'))^0xffffffff
put(CONTEXT,'<9I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,0x6f2364,0,0);put(ADAPTER,'<4I',CONTEXT,0,0,0)
put(MANAGER+0x110,'<I',MANAGER+0x300);put(MANAGER+0x124,'<I',HSTATE);put(MANAGER+0x154,'<I',MANAGER+0x400)
put(POOL,'<6I',ENTRIES,ENTRIES+2000,0,0,0,ENTRIES);put(POOL+88,'<I',0)
for i in range(100):put(ENTRIES+i*20,'<I',ENTRIES+(i+1)*20 if i<99 else 0)
put(CACHE+20,'<3IB',CTABLE,0,0,0);put(CTABLE,'<3I',4,CBUCKETS,0);memory[CBUCKETS-BASE:CBUCKETS-BASE+192]=bytes(192)
put(HSTATE+36,'<I',GAP);put(HSTATE+48,'<I',FREELIST);put(GAP,'<6I',0,0,0,0x1000000,0,0);put(FREELIST+20,'<I',0)
for at,size in [(BUCKETS,16388),(LOCAL,49152),(DEBUG,65536*80),(TLS,256),(LOCALE,256)]:memory[at-BASE:at-BASE+size]=bytes(size)
put(TLS+0x64,'<I',LOCALE)
memory[FILENAME-BASE:FILENAME-BASE+len(b'LEVELS/TR/test.qb\0')]=b'LEVELS/TR/test.qb\0'
texts=[b'',b'Alpha',b'aLPHA',b'different',b'\xff\xfeName']
for i,t in enumerate(texts):memory[TEXT-BASE+i*64:TEXT-BASE+i*64+len(t)+1]=t+b'\0'
A,B,S=0x12345001,0x12346001,0xabcdefff
body=b'\x01'+name(0x11223344)+b'\x01\x24'
put(SYMBOL,'<BBHIIII',0x91,1,0x1234,A,0x88776655,123,0)
put(OLD,'<BBHIIII',0x91,7,0x4321,S,0x55667788,STORAGE,0)
put(STORAGE,'<3I',0x12345678,len(body),len(body));memory[STORAGE-BASE+12:STORAGE-BASE+12+len(body)]=body
tokens=json.loads((out/'script-tokens-fixtures.json').read_text());token_bytes=(out/tokens['memory']).read_bytes()
assets=[];cursor=ASSETS
for entry in tokens['assets']:
    raw=token_bytes[entry['address']-tokens['base']:entry['address']-tokens['base']+entry['size']]
    assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    memory[cursor-BASE:cursor-BASE+len(raw)]=raw
    filename=cursor+len(raw)+16;encoded=entry['member'].encode()+b'\0'
    memory[filename-BASE:filename-BASE+len(encoded)]=encoded
    assets.append({**entry,'address':cursor,'filename':filename});cursor=(filename+len(encoded)+19)&~3
assert cursor<STRINGS
initial=bytes(memory);(out/'script-load-memory.bin').write_bytes(initial)
parser=json.loads((out/'script-parser-fixtures.json').read_text());cache=json.loads((out/'script-cache-fixtures.json').read_text())
globals_=parser['globals'][:];defaults=parser['cases'][0]['globals'][:]
defaults[:7]=[BASE+0x50000,0x20000,0,BASE+0x50000,BASE+0x80000,0,BUCKETS]
for g,v in zip(cache['globals'],cache['cases'][0]['globals']):
    if g[0]=='thug_script_symbol_buckets':continue
    globals_.append(g[:]);defaults.append(v)
index={g[1]:i for i,g in enumerate(globals_)}
for address,value in [(0x7d1808,0),(0x6f3558,0),(0x6f3560,0),(0x6f3568,POOL),(0x6f356c,0)]:defaults[index[address]]=value
heap_index=next(i for i,g in enumerate(globals_) if g[0]=='thug_script_cache_heap');globals_[heap_index][1]=MANAGER+0x124;defaults[heap_index]=HSTATE
for export,original,width,value in [('thug_script_debug_enabled',0x7cefac,1,0),('thug_script_debug_names',0x6f232c,4,DEBUG),
 ('thug_script_debug_cursor',0x6f2334,4,STRINGS),('thug_script_local_names',0x6f2368,4,0),('thug_script_loading_file',0x6f2364,4,0),('thug_script_journal_count',0x6f3528,4,0)]:
    globals_.append([export,original,width]);defaults.append(value)
for i in range(0,4000,4):globals_.append(['thug_script_journal',0x6f2588+i,4,i]);defaults.append(0xadadadad)
index={g[1]:i for i,g in enumerate(globals_)}
functions={}
def bind(at,name,heap=True):functions[hex(at)]={'name':'thug_script_'+name,'this':False,'result':'void','cleanup':0,'memory':heap}
for at,n,heap in [(0x46cf60,'add_debug_name',False),(0x470010,'local_names_initialize',True),(0x46f9f0,'local_names_clear',True),
 (0x46fa60,'add_local_name',True),(0x4727b0,'journal_created',True),(0x4727f0,'journal_replaced',True),(0x472830,'journal_undo',True),(0x472420,'load_qb',True)]:bind(at,n,heap)
functions['0x475e80']=cache['functions']['0x475e80'];functions['0x478cc0']={'name':'thug_script_symbol_find','this':False,'result':'word','cleanup':0,'memory':False}
class LoaderOracle(ScriptHeapOracle):
    def heap(self,cpu,address,size,user):
        if address not in [0x5bbae0,0x5bafc0,0x5ba0b0,0x5baba0]:return super().heap(cpu,address,size,user)
        sp=cpu.reg_read(UC_X86_REG_ESP);cleanup=0;result=0
        if address in [0x5bbae0,0x5bafc0]:
            size=self.word(sp+4);route=int(address==0x5bafc0)
            if route:assert self.word(sp+8)==1 and self.word(sp+12)==0;cleanup=12
            header=self.word(CONTEXT);result=header+16;assert result+size+16<=self.word(CONTEXT+4),(len(self.cases),size)
            cpu.mem_write(header,struct.pack('<4I',self.word(CONTEXT+32),size,route,0xabcdef01))
            self.setword(CONTEXT+32,result);self.setword(CONTEXT,(result+size+3)&~3)
            if size:cpu.mem_write(result,b'\xa5'*size)
            self.record(1,size,route,result)
        else:
            pointer=self.word(sp+4);self.record(2,pointer,0,0);cleanup=4 if address==0x5baba0 else 0
            if pointer and pointer==self.word(CONTEXT+32):self.setword(CONTEXT,pointer-16);self.setword(CONTEXT+32,self.word(pointer-16))
        self.heap_events[hex(address)]+=1
        cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,self.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
oracle=LoaderOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=150000000,
 observe=[int(k,16) for k in functions]+[0x472240,0x46fe40,0x401700,0x4711d0,0x478dc0,0x478d60,0x475fd0,0x626efb,0x631b80],
 scope_entries={HSTATE:1,MANAGER+0x300:2,MANAGER+0x400:3})
for at in [0x6f362c,0x6f3634,0x6f3638,0x6f2578,0x6f2580,0x6f2584]:oracle.cpu.mem_write(at,bytes(4))
# Real CRT comparison executes on duplicate names. Only initialized Windows TLS
# and last-error services are modeled; its discarded result affects no game data.
os_calls=Counter();last_error=0x12345678
GET_ERROR,GET_TLS,SET_ERROR=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET_ERROR),(0x7db10c,GET_TLS),(0x64516c,SET_ERROR)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7);oracle.setword(0x68ecfc,LOCALE)
for at,n in [(GET_ERROR,0),(GET_TLS,4),(SET_ERROR,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
def os_service(cpu,address,size,user):
    global last_error
    sp=cpu.reg_read(UC_X86_REG_ESP)
    if address==GET_ERROR:cpu.reg_write(UC_X86_REG_EAX,last_error);os_calls['GetLastError']+=1
    elif address==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS);os_calls['TLS_read']+=1
    else:last_error=oracle.word(sp+4);os_calls['SetLastError']+=1
for at in [GET_ERROR,GET_TLS,SET_ERROR]:oracle.cpu.hook_add(UC_HOOK_CODE,os_service,begin=at,end=at)
labels=[];max_heap=HEAP;max_events=0
def call(fn,*args):return (fn,0,list(args))
def load(code,local=0,journal=0,line=0,filename=FILENAME):return call(0x472420,filename,code,line,local,journal)
def case(calls,patches=(),changes=None,label='synthetic'):
    global max_heap,max_events
    stages=oracle.case(calls,patches,{index[k]:v for k,v in (changes or {}).items()});labels.append(label)
    assert last_error==0x12345678
    max_heap=max(max_heap,oracle.word(CONTEXT));max_events=max(max_events,oracle.word(CONTEXT+8))
    for step in stages:
        merged=[];chunks=[];start=0;end=0
        for at,data in step['outputs']:
            if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
            if not chunks:start=at
            chunks.append(data);end=at+len(data)//2
        if chunks:merged.append([start,''.join(chunks)])
        step['outputs']=merged;step['global_float_indices']=[]
        for base in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
            if step['globals'][index[base]]&0xfe==4:step['global_float_indices'].append(index[base+8])
    return stages
# Debug map preserves its first spelling, including mismatched duplicates. Low
# 16-bit collisions occupy adjacent slots; no string/slot capacity is invented.
case([call(0x46cf60,0xffffffff,0)])
for flag in [1,255]:
    calls=[call(0x46cf60,0x10001+i*0x10000,TEXT+(i%5)*64) for i in range(10)]
    calls += [call(0x46cf60,0x10001+i*0x10000,TEXT+((i+1)%5)*64) for i in range(10)]
    calls += [call(0x46cf60,0,TEXT),call(0x46cf60,0xffffffff,TEXT+256)]
    case(calls,changes={0x7cefac:flag})
for flag in [0,1,0x100,0x101,0xffffffff]:
    calls=[call(0x470010,flag)]
    calls += [call(0x46fa60,0xfff+i*0x1000,TEXT+(i%5)*64) for i in range(6)]
    calls += [call(0x46fa60,0xfff,TEXT+192),call(0x46f9f0),call(0x46f9f0)]
    case(calls,changes={0x7cefac:1})
case([call(0x46f9f0)])
# Both journal append routines preserve padding and trigger script-cache reload
# only for type 7. Include the final legal slot in the fixed 500-entry array.
for at in [0x4727b0,0x4727f0]:
    for start in [0,17,499]:
        for symbol in [SYMBOL,OLD]:case([call(at,symbol)],changes={0x6f3528:start,0x6f3558:CACHE})
for count in [0,0x80000000,0xffffffff]:case([call(0x472830)],changes={0x6f3528:count})
# File grammar includes all ordinary value families, duplicate/replaced names,
# script checksum reuse (line numbering ignored), and conditional debug regions.
types=[number(42),b'\x1a'+word(0x3fc00000),b'\x1b'+word(6)+b'hello\0',b'\x1c'+word(4)+b'loc\0',
 b'\x1f'+word(0x3f800000)+word(0x40000000),b'\x1e'+word(0x3f800000)+word(0x40000000)+word(0x40400000),
 b'\x03'+definition(B,number(77))+b'\x04',b'\x05'+number(1)+b'\x09'+number(2)+b'\x06',name(B),
 b'\x0e'+number(2)+b'\x0b'+number(3)+b'\x0f']
for value in types:
    code=definition(B,number(11))+definition(A,value)+script(S,body)+name_record(A,b'alpha')+name_record(A,b'different')+b'\0'
    for debug,local in [(0,0),(0,1),(1,0),(1,1)]:
        case([load(PROGRAM,local),load(PROGRAM,local,line=1)],[[PROGRAM,code.hex()]],{0x7cefac:debug},'typed value replacement')
for local in [0,1]:
    initial_code=definition(A,number(1))+script(S,body)+b'\0'
    replacement_code=definition(A,number(2))+definition(B,number(3))+script(S,b'\x01'+name(0x55667788)+b'\x01\x24')+b'\0'
    steps=case([load(PROGRAM,local),load(PROGRAM+4096,local,1),call(0x472830),call(0x478cc0,A),call(0x478cc0,B),call(0x478cc0,S)],
               [[PROGRAM,initial_code.hex()],[PROGRAM+4096,replacement_code.hex()]],{0x7cefac:1},'journal replacement and undo')
    assert oracle.word(steps[3]['result']+12)==1 and steps[4]['result']==0
    # A pre-existing cached script reloads before unlink and after replacement,
    # then returns to the old body when journal undo restores its symbol.
    case([load(PROGRAM), (0x475e80,CACHE,[S]),load(PROGRAM+4096,local,1),call(0x472830)],
         [[PROGRAM,initial_code.hex()],[PROGRAM+4096,replacement_code.hex()]],{0x6f3558:CACHE},'cached journal replacement')
for debug in [0,1,255]:
    code=definition(A,number(1))+directive(0x70cb0238)+definition(B,number(2))+directive(0x0fa33d9b)+definition(S,number(3))+b'\0'
    stages=case([load(PROGRAM),call(0x478cc0,B)],[[PROGRAM,code.hex()]],{0x7cefac:debug})
    assert bool(stages[-1]['result'])==bool(debug)
case([load(PROGRAM)],[[PROGRAM,(directive(0x70cb0238)+definition(A,number(1))+b'\0').hex()]])
case([load(PROGRAM)],[[PROGRAM,(directive(0x77777777)+definition(A,number(1))+b'\0').hex()]])
for line in [0,1,0xffffffff]:
    code=name(A)+b'\x02'+word(18)+b'\x07\x02'+word(19)+number(5)+b'\x02'+word(20)+b'\0'
    case([load(PROGRAM,line=line)],[[PROGRAM,code.hex()]])
# Same script hash with different line tokens/filename retains the old storage
# and source CRC, while a script replacing a scalar takes the full create path.
original=script(S,body)+b'\0';numbered=script(S,b'\x02'+word(999)+name(0x11223344)+b'\x02'+word(1000)+b'\x24')+b'\0'
stages=case([load(PROGRAM),call(0x478cc0,S),load(PROGRAM+4096,filename=TEXT+64),call(0x478cc0,S)],[[PROGRAM,original.hex()],[PROGRAM+4096,numbered.hex()]])
assert stages[1]['result']==stages[3]['result'] and oracle.word(stages[3]['result']+8)==crc(b'LEVELS/TR/test.qb')
case([load(PROGRAM)],[[PROGRAM,(definition(S,number(1))+script(S,body)+b'\0').hex()]])
print('Synthetic whole-loader checks:',len(oracle.cases),flush=True)
training=[]
definitions={a['member']:a for a in json.loads((out.parent/'script-symbols.json').read_text())['training']}
def loaded_symbols():
    found={}
    for i in range(4096):
        p=oracle.word(BUCKETS+i*4)
        while p:
            n=oracle.word(p+4);assert n not in found;found[n]=p;p=oracle.word(p+16)
    return found
for asset in assets:
    # Complete file, then repeated load, and separately a journaled load/undo.
    # Each file has fewer than 500 definitions, within the original journal.
    for local,debug in [(0,0),(1,1)]:
        case([load(asset['address'],local,filename=asset['filename'])],changes={0x7cefac:debug},label=asset['member']+' full load')
        found=loaded_symbols();expected=definitions[asset['member']]
        assert set(found)=={d['name'] for d in expected['definitions']+expected['scripts']}
        for d in expected['scripts']:
            p=found[d['name']];assert oracle.cpu.mem_read(p+1,1)[0]==7
            assert oracle.word(oracle.word(p+12))==d['checksum']
        assert all(oracle.word(p+8)==crc(asset['member'].encode()) for p in found.values())
    case([load(asset['address'],1,1,filename=asset['filename']),call(0x472830),call(0x46f9f0)],changes={0x7cefac:1},label=asset['member']+' load and undo')
    assert all(oracle.word(BUCKETS+i*4)==0 for i in range(4096))
    training.append({'member':asset['member'],'sha256':asset['sha256'],'size':asset['size'],
                     'ordinary_definitions':len(expected['definitions']),'script_definitions':len(expected['scripts'])})
    print('Whole archived QB verified:',asset['member'],flush=True)
case([load(a['address'],1,filename=a['filename']) for a in assets]+[call(0x46f9f0)],changes={0x7cefac:1},label='all eight archived files in sequence')
scope='Eight recovered routines: complete two-pass QB-buffer loader, global/local readable-name maps, local-map initialization/disposal, journal append for creations/replacements and forward undo. All concrete parser/symbol/codec/cache callees execute. Whole loads of eight archived training files cover 815 definitions, including 651 scripts; individual journal undo and one combined load sequence included. Generic successful heap and temporary-heap scopes are instrumented, with top-of-arena scratch reuse. Original CRT duplicate-name comparison executes with initialized C-locale TLS and modeled Windows TLS/last-error services; its discarded comparison and platform bookkeeping are omitted in the port. Every fixture byte, global, heap event and in-flight filename checksum is compared, with relocated global/error pointers and typed NaNs as documented. File I/O, startup, cache construction, command execution, malformed grammar, capacity exhaustion and locale changes are outside scope.'
fixture={'base':BASE,'memory':'script-load-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'case_labels':labels,'training':training,'pointer_symbols':parser['pointer_symbols'],
 'pointer_globals':[index[0x6f2560]],'pointer_exports':[[0x6f2364,'thug_script_loading_file']],
 'pointer_fields':[CONTEXT+24]+[LOG+i*48+36 for i in range(max_events)]}
path=out/'script-load-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
adapter=out/'script-loader-memory.wasm';sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_loader_memory.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls; max heap bytes',max_heap-HEAP,'events',max_events,flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_load_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),
 'os_service_calls':dict(os_calls),'max_heap_bytes':max_heap-HEAP,'max_heap_events':max_events,'scope':scope,'training':training,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-load-memory.bin',adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
