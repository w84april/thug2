"""Complete cache/registration chain against original instructions and WASM.

The original fixed-pool and lookup implementations execute unchanged. Generic
heap storage is instrumented; a finite release schedule changes the arena gap
to exercise trimming without claiming the complete PC heap implementation.
"""
import hashlib,json,random,struct,subprocess,zlib
from unicorn.x86_const import UC_X86_REG_ESP
from specimen import ROOT,SHA256
from script_heap_oracle import ScriptHeapOracle
out=ROOT/'local/validation/collision';report_path=out.parent/'script-cache.json';report_path.unlink(missing_ok=True)
BASE,SIZE=0x1800000,0x200000
CONTEXT,ADAPTER,MANAGER=BASE+0x20,BASE+0x50,BASE+0x100
P0,P1,PN=BASE+0x1000,BASE+0x1100,BASE+0x1200
E0,E1,N0=BASE+0x2000,BASE+0x3000,BASE+0x4000
CACHE,TABLE,TBUCKETS,KEYS=BASE+0x5000,BASE+0x5100,BASE+0x5200,BASE+0x5500
HSTATE,GAP,FREELIST,LOWER,UPPER,FREEBLOCKS,SCHEDULE=BASE+0x6000,BASE+0x6100,BASE+0x6200,BASE+0x6300,BASE+0x6400,BASE+0x6500,BASE+0x6600
BUCKETS,BINDINGS,SOURCE,BLOB,PROGRAM,LOG,HEAP=BASE+0x10000,BASE+0x20000,BASE+0x35000,BASE+0x36000,BASE+0x40000,BASE+0x60000,BASE+0x80000
FILENAME=SOURCE+0x100;memory=bytearray(b'\xad'*SIZE);rng=random.Random(0x475e80)
def put(at,fmt,*values):struct.pack_into(fmt,memory,at-BASE,*values)
def patch(at,fmt,*values):return [at,struct.pack(fmt,*values).hex()]
def word(value):return struct.pack('<I',value&0xffffffff)
def token_name(n):return b'\x16'+word(n)
def crc(data):return zlib.crc32(data.lower().replace(b'/',b'\\'))^0xffffffff
put(CONTEXT,'<11I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,CACHE+0x1c,0,SCHEDULE,0,GAP+12)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x110,'<I',MANAGER+0x300);put(MANAGER+0x124,'<I',HSTATE)
for pool,blocks,size,count in [(P0,E0,20,100),(P1,E1,20,100),(PN,N0,12,128)]:
    put(pool,'<6I',blocks,blocks+size*count,0xadadadad,0xadadadad,0,blocks);put(pool+0x58,'<I',0)
    for i in range(count):put(blocks+i*size,'<I',blocks+(i+1)*size if i+1<count else 0)
put(CACHE+0x14,'<3IB',TABLE,0,0,0);put(TABLE,'<3I',4,TBUCKETS,0)
memory[TBUCKETS-BASE:TBUCKETS-BASE+16*12]=bytes(16*12)
keys=[5,21,37,53,0,0xffffffff,0x12345000,0x12345001,0x12345002,0x12345003,0x12345004,0x12345005,0x12345006,0x12345007]
for i,n in enumerate(keys):put(KEYS+4*i,'<I',n)
put(HSTATE+0x24,'<I',GAP);put(HSTATE+0x30,'<I',FREELIST)
put(GAP,'<6I',0xadadadad,1000,0xadadadad,1001000,0,0);put(FREELIST+20,'<I',0)
put(LOWER+44,'<I',2000);put(UPPER+44,'<I',9000)
memory[BUCKETS-BASE:BUCKETS-BASE+0x4004]=bytes(0x4004)
binding_cursor=BINDINGS
def symbol(n,kind,value):
    global binding_cursor
    at=binding_cursor;binding_cursor+=20;bucket=BUCKETS+(n&0xfff)*4
    previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
    put(at,'<BBHIIII',0x91,kind,0x1234,n,0xdeadbeef,value,previous);put(bucket,'<I',at);return at
bindings=json.loads((ROOT/'local/analysis/script-bindings.json').read_text())
for binding in bindings:symbol(crc(binding['name'].encode()),8,int(binding['address'],16))
# These addresses are data used in bytecode preparation, never fake implementations
# of the 1,254 native bindings. Execution requires target function relocation.
NATIVE,MEMBER,MEMBERPTR,OTHER,ALIAS,DANGLING,SCRIPT,ALIAS_SCRIPT=range(0x12345000,0x12345008)
symbol(NATIVE,8,0x44332211);symbol(MEMBER,9,0);symbol(MEMBERPTR,9,0x88776655);symbol(OTHER,1,5)
symbol(ALIAS,13,NATIVE);symbol(DANGLING,13,0x87650000)
source=symbol(SCRIPT,7,BLOB);symbol(ALIAS_SCRIPT,13,SCRIPT)
filename=b'levels/TR/TR_scripts.qb\0';memory[FILENAME-BASE:FILENAME-BASE+len(filename)]=filename
basic=b'\x01'+token_name(NATIVE)+b'\x01\x24'
put(BLOB,'<3I',0x87654321,len(basic),len(basic));memory[BLOB-BASE+12:BLOB-BASE+12+len(basic)]=basic
assert binding_cursor<SOURCE
initial=bytes(memory);(out/'script-cache-memory.bin').write_bytes(initial)
globals_=[['thug_script_symbol_buckets',0x6f3624,4],['thug_lookup_node_pool',0x7d1808,4],
 ['thug_script_cache',0x6f3558,4],['thug_script_cache_pool_index',0x6f3560,4],
 ['thug_script_cache_pools',0x6f3568,4,0],['thug_script_cache_pools',0x6f356c,4,4],
 ['thug_script_cache_heap',MANAGER+0x124,4]]
defaults=[BUCKETS,PN,0,0,P0,P1,HSTATE]
globals_ += [['thug_lzss_encoder',0x690f7c+i,4,i] for i in range(0,36,4)]
defaults += [0,0,0,0,0x12345678,0x87654321,0,0,0]
globals_ += [['thug_script_decoder',0x68ff68+i,4,i] for i in range(0,4096,4)]
defaults += [rng.getrandbits(32) for _ in range(1024)]
functions={}
def bind(at,name,argc=0,this=True,heap=False,result='void'):
    functions[hex(at)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
bind(0x5ba3b0,'thug_pool_contains',1,result='byte');bind(0x5ba3d0,'thug_pool_allocate',result='word');bind(0x5ba400,'thug_pool_release',1)
bind(0x5bc530,'thug_heap_gap',result='word');bind(0x5ba4f0,'thug_heap_largest_free',result='word')
bind(0x49fd90,'thug_object_table_initialize',1,heap=True,result='word');bind(0x462740,'thug_object_table_insert',2,heap=True,result='byte')
bind(0x5b80d0,'thug_object_table_remove',1,heap=True);bind(0x462050,'thug_object_table_find',2,result='word')
bind(0x46fb30,'thug_script_skip_line',this=False,result='word');bind(0x46ff00,'thug_script_prepare_bytecode',this=False)
for at,name,args,heap,result in [(0x475a40,'prepend',1,False,'void'),(0x475a70,'unlink',1,False,'void'),
 (0x475b60,'evict',1,True,'void'),(0x475bd0,'trim',2,True,'void'),(0x475d60,'release',1,True,'void'),
 (0x475e80,'acquire',1,True,'word'),(0x475fd0,'reload',1,True,'void')]:bind(at,'thug_script_cache_'+name,args,heap=heap,result=result)
bind(0x475ac0,'thug_script_cache_allocate',this=False,heap=True,result='word');bind(0x475b00,'thug_script_cache_free',this=False,heap=True)
bind(0x46fe40,'thug_script_register_script',this=False,heap=True,result='word')
functions['0x46fe40'].update(register_args={'ebx':0,'eax':1},stack_args=[2,3,4])
class CacheOracle(ScriptHeapOracle):
    def heap(self,cpu,address,size,user):
        released=self.word(cpu.reg_read(UC_X86_REG_ESP)+4) if address in [0x5ba0b0,0x5baba0] else None
        super().heap(cpu,address,size,user)
        if released is not None:
            for i in range(self.word(CONTEXT+36)):
                at=self.word(CONTEXT+32)+i*8
                if self.word(at)==released:
                    gap=self.word(CONTEXT+40);self.setword(gap,self.word(gap)+self.word(at+4));self.setword(at+4,0)
oracle=CacheOracle(initial,BASE,CONTEXT,MANAGER,globals_,defaults,functions,event_limit=(HEAP-LOG)//48,instruction_limit=20000000,
 observe=[int(k,16) for k in functions]+[0x4014f0,0x401700,0x479110,0x478cf0],scope_entries={HSTATE:1,MANAGER+0x300:2})
# Symbol entries use the generic heap, as in the existing symbol oracle.
oracle.cpu.mem_write(0x6f362c,bytes(4));oracle.cpu.mem_write(0x6f3634,bytes(8))
labels=[]
def call(fn,this,*args):return (fn,this,list(args))
def static(fn,*args):return call(fn,0,*args)
def case(calls,patches=(),changes=None,label='synthetic'):
    stages=oracle.case(calls,patches,changes);labels.append(label)
    for step in stages:
        merged=[]
        for at,data in step['outputs']:
            if merged and merged[-1][0]+len(merged[-1][1])//2==at:merged[-1][1]+=data
            else:merged.append([at,data])
        step['outputs']=merged
    return stages
# Pool boundaries are unsigned and do not test alignment; counters wrap and
# high-bit peaks use signed comparison. Empty allocation preserves every byte.
for start,end in [(E0,E0+2000),(0,0xffffffff),(0xffffffff,0xffffffff),(100,20),(0,0)]:
    for p in dict.fromkeys([0,1,0xffffffff,start,(start-1)&0xffffffff,(start+1)&0xffffffff,(end-1)&0xffffffff,end]):
        case([call(0x5ba3b0,P0,p)],[patch(P0,'<II',start,end)])
for count in [0,1,99,0x7ffffffe,0x7fffffff,0x80000000,0xffffffff]:
    for peak in [0,100,0x7fffffff,0x80000000,0xffffffff]:
        case([call(0x5ba3d0,P0),call(0x5ba400,P0,E0),call(0x5ba3d0,P0)],
             [patch(P0+16,'<I',count),patch(P0+88,'<I',peak)])
case([call(0x5ba3d0,P0)],[patch(P0+20,'<I',0)])
case([call(0x5ba3d0,P0)]*101)
# Gap endpoints and free-list maxima, including unsigned wrap.
for low,high in [(0,0),(1000,3000),(3000,1000),(0,0xffffffff),(0x80000000,127)]:
    for lower in [0,LOWER]:
        for upper in [0,UPPER]:
            for sizes in [[],[1],[0xffffffff,3],[2000,7000,0]]:
                patches=[patch(GAP+4,'<I',low),patch(GAP+12,'<3I',high,lower,upper),patch(FREELIST+20,'<I',FREEBLOCKS if sizes else 0)]
                patches += [patch(FREEBLOCKS+i*8,'<II',FREEBLOCKS+(i+1)*8 if i+1<len(sizes) else 0,n) for i,n in enumerate(sizes)]
                case([call(0x5bc530,GAP),call(0x5ba4f0,HSTATE)],patches)
# Constructor preserves opaque fields. Collisions, duplicate keys, head holes,
# null-valued insertions and removals exercise both node allocator routes.
for shift in [0,1,2,4,8,32,33,36]:case([call(0x49fd90,TABLE,shift)])
for node_pool in [0,PN]:
    for shift in [0,4,32,36]:
        calls=[call(0x49fd90,TABLE,shift)]
        for k,v in [(0,111),(1,222),(2,333),(0,444),(3,0),(3,555),(4,0),(4,666)]:calls.append(call(0x462740,TABLE,KEYS+k*4,v))
        for k in [0,2,0,3,4,1,0,5]:
            calls.extend([call(0x462050,TABLE,KEYS+k*4,1),call(0x5b80d0,TABLE,KEYS+k*4)])
        case(calls,changes={1:node_pool})
case([call(0x5b80d0,TABLE,0)],[patch(TABLE+4,'<I',0)])
# Line skipping treats payload bytes as data and balances all three delimiter
# classes independently, including newlines within those compound values.
for end in [b'\0',b'\x01',b'\x02'+word(999)]:
    for prefix in [b'',token_name(0x020124),b'\x1b'+word(7)+b'\x01\x02\x03\x04\x24\0\0',
                   b'\x03\x01\x05\x02'+word(2)+b'\x0e\x01\x0f\x06\x04',b'\x04\x03']:
        case([static(0x46fb30,PROGRAM)],[[PROGRAM,(prefix+end+b'\xad'*8).hex()]])
for n in [NATIVE,MEMBER,MEMBERPTR,OTHER,ALIAS,DANGLING,0x77777777]:
    for condition in [b'',b'\x47\x00\x00',b'\x47\x00\x00\x39']:
        for defaults_line in [b'\x01',token_name(NATIVE)+b'\x07\x17'+word(1)+b'\x01']:
            code=defaults_line+condition+token_name(n)+b'\x03'+token_name(NATIVE)+b'\x04\x01\x24'
            case([static(0x46ff00,PROGRAM)],[[PROGRAM,code.hex()]])
# Idle-list links: empty, singleton, head/middle/tail, and active unlinked node.
for removal in [0,1,2,3]:
    calls=[call(0x475a40,CACHE,E0+i*20) for i in range(3)]
    calls += [call(0x475a70,CACHE,E0+removal*20)]
    patches=[patch(E0+i*20,'<5I',5+i,0,0,0,0) for i in range(4)]
    case(calls,patches)
case([call(0x475a40,CACHE,E0),call(0x475a70,CACHE,E0)],[patch(E0,'<5I',5,0,0,0,0)])
# Cache entry allocation and return to either pool, including missing pools and
# generic null release. Standalone allocation can return null on exhaustion.
for index in [0,1]:
    for current in [0,1]:
        changes={3:index,4+index:[0,[P0,P1][index]][current]}
        for size in [0,20,128]:case([static(0x475ac0,size)],changes=changes)
    for p in [E0,E1,PROGRAM,0]:case([static(0x475b00,p)],changes={3:index})
case([static(0x475ac0,20)],[patch(P0+20,'<I',0)])
for p in [PROGRAM,0]:case([static(0x475b00,p)],changes={4:0,5:0})
def cached(count=3,references=0,immediate=0,node_pool=True):
    patches=[patch(CACHE+24,'<2IB',E0 if count else 0,E0+(count-1)*20 if count else 0,immediate),
             patch(P0+16,'<II',count,E0+count*20),patch(TABLE+8,'<I',count),patch(PN+16,'<II',max(0,count-1),N0+max(0,count-1)*12)]
    for i in range(count):
        patches.append(patch(E0+i*20,'<5I',5+i*16,PROGRAM+0x2000+i*256,references,E0+(i+1)*20 if i+1<count else 0,E0+(i-1)*20 if i else 0))
        patches.append(patch(TBUCKETS+5*12 if not i else N0+(i-1)*12,'<3I',5+i*16,E0+i*20,N0+i*12 if i+1<count else 0))
    return patches
for n in [1,3]:
    for i in range(n):
        for payload in [0,PROGRAM+0x2000+i*256]:
            case([call(0x475b60,CACHE,E0+i*20)],cached(n)+[patch(E0+i*20+4,'<I',payload)])
for count in [99,100,101,103,0x7fffffff,0x80000000,0xffffffff]:
    case([call(0x475bd0,CACHE,100,0xabcdef)],cached()+[patch(P0+16,'<I',count)])
for count in [0,100]:case([call(0x475bd0,CACHE,100,0)],cached(0)+[patch(P0+16,'<I',count)])
for required in [0,1,127,128,129,255,256,257,512,0x80000000,0xffffffff]:
    # Initial available bytes=128; each discarded body returns 256 more.
    patches=cached()+[patch(GAP+12,'<I',1256),patch(CONTEXT+36,'<I',3)]
    patches += [patch(SCHEDULE+i*8,'<II',PROGRAM+0x2000+i*256,256) for i in range(3)]
    case([call(0x475bd0,CACHE,required,5)],patches)
for refs in [0,1,2,0xffffffff]:
    for immediate in [0,1,255]:
        for n in [5,21,37,53]:
            patches=cached(references=refs,immediate=immediate)
            # Referenced entries are not idle: use unlinked list state.
            if refs:patches += [patch(CACHE+24,'<2I',0,0)]+[patch(E0+i*20+12,'<2I',0,0) for i in range(3)]
            case([call(0x475d60,CACHE,n)],patches)
# Acquisition rejects non-scripts before consulting a cache; missing symbol
# with a cached entry succeeds. Alias names resolve only on acquisition.
for n in [5,21,37,53,NATIVE,DANGLING,0x76543210]:case([call(0x475e80,CACHE,n)],cached())
case([call(0x475e80,CACHE,5)],cached()+[patch(BUCKETS+5*4,'<I',SOURCE),patch(SOURCE,'<BBHIIII',1,1,0,5,0,0,0)])
for n in [SCRIPT,ALIAS_SCRIPT]:
    case([call(0x475e80,CACHE,n),call(0x475e80,CACHE,n),call(0x475d60,CACHE,n),call(0x475d60,CACHE,SCRIPT),call(0x475fd0,CACHE,SCRIPT)])
for refs in [0,1,17,0xffffffff]:
    patches=cached(1,references=refs)+[patch(E0,'<I',SCRIPT),patch(TBUCKETS+5*12,'<3I',0,0,0),patch(TBUCKETS+(SCRIPT&15)*12,'<3I',SCRIPT,E0,0)]
    if refs:patches += [patch(CACHE+24,'<2I',0,0),patch(E0+12,'<2I',0,0)]
    steps=case([call(0x475fd0,CACHE,SCRIPT)],patches)
    assert oracle.word(E0+8)==refs and oracle.word(CACHE+24)==0 and oracle.word(CACHE+28)==0
case([call(0x475fd0,CACHE,0xabcdef00)])
# Raw storage uses raw_size bytes even if stored_size is larger.
case([call(0x475e80,CACHE,SCRIPT)],[patch(BLOB+8,'<I',len(basic)+10)])
# Register synthetic raw/compressible inputs; only complete valid bytecode is
# passed to cache preparation. Empty registration is tested without acquisition.
for code in [b'',basic,b'\x01'+(token_name(NATIVE)+b'\x01')*100+b'\x24']:
    for active_cache in [0,CACHE]:
        calls=[static(0x46fe40,PROGRAM,len(code),SCRIPT,0x44332211,FILENAME)]
        if code:calls += [call(0x475e80,CACHE,SCRIPT),static(0x46fe40,PROGRAM,len(code),SCRIPT,0x88776655,FILENAME)]
        case(calls,[[PROGRAM,code.hex()]],{2:active_cache})
print('Synthetic cache/pool checks:',len(oracle.cases),flush=True)
# Each body independently shadows the binding table, avoiding accidental
# cross-file overrides. Reuse previously verified compression bytes and hashes.
compression=json.loads((out/'compression-fixtures.json').read_text())
real=compression['training'];roundtrips=compression['roundtrips'][-len(real):]
checksums={(a['member'],s['name']):s['checksum'] for a in json.loads((out.parent/'script-symbols.json').read_text())['training'] for s in a['scripts']}
training=[]
for index,(entry,data) in enumerate(zip(real,roundtrips)):
    raw=bytes.fromhex(data['original']);encoded=bytes.fromhex(data['encoded']);name=entry['name']
    assert hashlib.sha256(raw).hexdigest()==entry['body_sha256'] and hashlib.sha256(encoded).hexdigest()==entry['encoded_sha256']
    bucket=BUCKETS+(name&0xfff)*4;previous=struct.unpack_from('<I',initial,bucket-BASE)[0]
    stored=encoded if len(encoded)<len(raw) else raw
    patches=[patch(bucket,'<I',SOURCE),patch(SOURCE,'<BBHIIII',1,7,0x1234,name,0,BLOB,previous),
             [BLOB,(word(checksums[entry['member'],name])+word(len(raw))+word(len(stored))+stored).hex()]]
    # Test loading, cache hit, idle transition, reactivation, and final eviction.
    calls=[call(0x475e80,CACHE,name),call(0x475e80,CACHE,name),call(0x475d60,CACHE,name),call(0x475d60,CACHE,name),
           call(0x475e80,CACHE,name),call(0x475b60,CACHE,E0)]
    stages=case(calls,patches,label=data['label']+' cached lifecycle')
    assert stages[0]['result']==HEAP and stages[1]['result']==HEAP and stages[4]['result']==HEAP
    prepared=bytes(oracle.cpu.mem_read(HEAP,len(raw)))
    # Registration plus active reload and final acquisition, using the same
    # original code. The cache flag makes reload run inside registration.
    register_patches=[[PROGRAM,raw.hex()],[FILENAME,(entry['member'].encode()+b'\0').hex()]]
    call_register=static(0x46fe40,PROGRAM,len(raw),name,checksums[entry['member'],name],FILENAME)
    stages=case([call_register,call(0x475e80,CACHE,name),call_register,call(0x475e80,CACHE,name)],register_patches,{2:CACHE},data['label']+' registration/reload')
    symbol_at=stages[2]['result'];storage=oracle.word(symbol_at+12)
    assert bytes(oracle.cpu.mem_read(storage+12,len(stored)))==stored
    assert bytes(oracle.cpu.mem_read(stages[3]['result'],len(raw)))==prepared
    assert oracle.word(symbol_at+8)==crc(entry['member'].encode())
    training.append({**entry,'prepared_sha256':hashlib.sha256(prepared).hexdigest(),'compressed':len(encoded)<len(raw)})
    if index%100==0:print('Training cache/registration:',index+1,'/',len(real),flush=True)
scope='Twenty original routines: five fixed-pool/heap-metric helpers, three lookup constructor/insertion/removal methods, line skipping and bytecode preparation, nine cache lifetime methods and complete compressed-script registration. Existing table lookup is also tested. All concrete script-symbol, codec, lookup and pool callees execute. Generic successful heap/temporary-scope services are instrumented; a test-only release schedule adjusts the gap to exercise trim policy. Every fixture/global byte and allocation event is compared. All 651 archived training script bodies run cache lifecycles plus registration, compression, preparation and active reload. Native-binding addresses remain data and are not executed. Cache construction/destruction, complete file loading and script execution are not recovered here. Valid initialized instances, successful allocation, sufficient idle entries, bounded scratch and terminating bytecode are required.'
fixture={'base':BASE,'memory':'script-cache-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-cache-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_cache_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'scope':scope,'training':training,'case_labels':labels}
path=out/'script-cache-fixtures.json';path.write_text(json.dumps(fixture,separators=(',',':')))
sdk=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';adapter=out/'script-cache-memory.wasm'
subprocess.run([str(sdk),'--target=wasm32-unknown-unknown','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib',
 '-Wl,--no-entry,--import-memory,--export-all,--global-base=58720256',str(ROOT/'tools/script_cache_memory.c'),'-o',str(adapter)],check=True)
print('x86 complete:',len(oracle.cases),'cases',sum(oracle.counts.values()),'calls',flush=True)
subprocess.run(['node',str(ROOT/'tools/verify_script_cache_wasm.mjs'),str(out)],check=True)
report={'result':'pass','specimen_sha256':SHA256,'counts':dict(oracle.counts),'callee_coverage':dict(oracle.coverage),
 'heap_events':dict(oracle.heap_events),'scope':scope,'training':training,
 'wasm_sha256':hashlib.sha256((ROOT/'local/build/thug-core.wasm').read_bytes()).hexdigest(),
 'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [path,out/'script-cache-memory.bin',adapter]},
 'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*')) if p.is_file()}}
report_path.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',dict(oracle.counts))
