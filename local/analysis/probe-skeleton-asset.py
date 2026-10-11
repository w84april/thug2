"""Original skeleton asset class with explicit heap/resident-file port boundaries."""
import hashlib,json,struct,subprocess
from collections import Counter
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
from specimen import ROOT,SHA256,load
from script_heap_oracle import ScriptHeapOracle
folder=ROOT/'local/analysis';BASE,SIZE=0x1800000,0x100000
CONTEXT,ADAPTER,MANAGER,FILE,IO,IOC=BASE+0x20,BASE+0x50,BASE+0x100,BASE+0x1000,BASE+0x2000,BASE+0x2100
ASSET,NAME,DATA,IOLOG,LOG,HEAP=BASE+0x8000,BASE+0x9000,BASE+0x10000,BASE+0x20000,BASE+0x40000,BASE+0x60000
initial=bytearray(b'\xad'*SIZE)
def put(at,fmt,*v):struct.pack_into(fmt,initial,at-BASE,*v)
def patch(at,fmt,*v):return [at,struct.pack(fmt,*v).hex()]
put(CONTEXT,'<8I',HEAP,BASE+SIZE,0,LOG,BASE,BASE+SIZE,ASSET+8,0)
put(ADAPTER,'<4I',CONTEXT,0,0,0);put(MANAGER+0x124,'<I',MANAGER+0x200);put(MANAGER+0x110,'<I',MANAGER+0x204)
put(IO,'<5I',IOC,0,0,0,0);put(IOC,'<8I',DATA,0,FILE,0,IOLOG,0,CONTEXT,ASSET)
initial=bytes(initial)
specs=[(0x4075f0,'thug_asset_begin_load_draft',5,'word',False,10),
 (0x407600,'thug_asset_finish_unload_draft',0,'word',False,8),
 (0x407620,'thug_asset_process_loaded_draft',0,'void',True,14),
 (0x407630,'thug_asset_finish_parse_draft',2,'byte',False,10),
 (0x407670,'thug_asset_loading_draft',0,'word',False,9),
 (0x4076b0,'thug_asset_unloaded_draft',0,'byte',False,10),
 (0x4076e0,'thug_asset_set_data_draft',1,'word',False,10),
 (0x409970,'thug_skeleton_asset_initialize_draft',0,'word',False,18),
 (0x409990,'thug_skeleton_asset_load_buffer_draft',5,'word',True,72),
 (0x4099e0,'thug_skeleton_asset_unload_draft',0,'word',True,44),
 (0x409a10,'thug_skeleton_asset_release_buffer_draft',0,'void',True,28),
 (0x409a50,'thug_skeleton_asset_load_file_draft',5,'word',True,294),
 (0x409b80,'thug_skeleton_asset_parse_draft',2,'void',True,184)]
functions={hex(a):{'name':name,'result':result,'cleanup':argc*4,'memory':heap} for a,name,argc,result,heap,_ in specs}
functions['0x407710']={'name':'thug_asset_read_callback','this':False,'result':'void','cleanup':0}
globals_=[['thug_asset_io_draft',0x300,4]]
oracle=ScriptHeapOracle(initial,BASE,CONTEXT,MANAGER,globals_,[IO],functions,
 observe=[0x407910,0x4a2c20,0x4a39c0,0x4a3950,0x401cc0,0x5bbb60,0x6234fe,0x5b6380],
 scope_entries={MANAGER+0x200:1,MANAGER+0x204:2})
oracle.setword(0x684fe4,0x5df4ac)
pe=load();md=Cs(CS_ARCH_X86,CS_MODE_32)
instructions={a:list(md.disasm(pe.get_data(a-0x400000,n),a)) for a,_,_,_,_,n in specs}
hits=Counter();saved={};registers=[UC_X86_REG_EBX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
def trace(cpu,at,size,user):
    hits[at]+=1
    for fn,insns in instructions.items():
        if at==fn:saved[fn]=[cpu.reg_read(r) for r in registers]
        # Tail jumps legitimately leave preservation checking to the target.
        if at in {i.address for i in insns if i.mnemonic=='ret'}:assert saved[fn]==[cpu.reg_read(r) for r in registers],hex(fn)
for a,insns in instructions.items():oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=a,end=insns[-1].address)
fields={ASSET,ASSET+0x38,FILE+8,*[IOLOG+i*320+32 for i in range(64)]}
def identity(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX))
oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=0x4a2c20,end=0x4a2c20)
record_heap=oracle.record
def heap_record(kind,a,b,c):
    ptr=a if kind==2 else c;record_at=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48
    for i in range(4):
        if ptr+i*4 in fields:fields.add(record_at+16+i*4)
    record_heap(kind,a,b,c)
oracle.record=heap_record
io_calls=Counter();raw_open_sync=Counter()
def record_io(op,a,b,d,name=b''):
    c=[oracle.word(IOC+i*4) for i in range(8)];assert c[3]<64
    file,asset=c[2],c[7];oracle.setword(IOC+12,c[3]+1)
    values=[op,a,b,d,c[0],c[1],file,oracle.word(file+0x14),oracle.word(file+8),oracle.word(file+12),oracle.word(file+16),
            oracle.word(asset+8),oracle.word(asset+0x24),oracle.word(CONTEXT+8),oracle.word(asset+0x20),oracle.word(asset+0x10)]
    assert len(name)<256
    oracle.cpu.mem_write(c[4]+c[3]*320,struct.pack('<16I',*values)+name+bytes(256-len(name)))
def io_boundary(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
    c=[oracle.word(IOC+i*4) for i in range(8)];cleanup=0
    if at==0x5b6c60:
        # The original pushes a register with only its low byte defined by
        # SETE. 5b67b0 consumes that byte as its bool (file+21), not the other
        # 24 caller-scratch bits. Preserve raw observations separately.
        raw_open_sync[hex(arg(1))]+=1
        name=bytes(cpu.mem_read(arg(0),256)).split(b'\0',1)[0];record_io(1,arg(1)&255,arg(2),0,name)
        result=0 if c[5] else c[2]
    elif at==0x5b63a0:
        file=cpu.reg_read(UC_X86_REG_ECX);assert file==c[2];record_io(2,file,0,0);result=c[1]
    elif at==0x5b6740:
        assert cpu.reg_read(UC_X86_REG_ECX)==c[2] and arg(1)==1 and arg(2)==c[1]
        record_io(3,arg(0),arg(1),arg(2));cpu.mem_write(arg(0),bytes(cpu.mem_read(c[0],c[1])));result=c[1];cleanup=12
    else:assert at==0x5b68a0;record_io(4,arg(0),0,0);result=1
    io_calls[hex(at)]+=1;cpu.reg_write(UC_X86_REG_EAX,result)
    cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for a in [0x5b6c60,0x5b63a0,0x5b6740,0x5b68a0]:oracle.cpu.hook_add(UC_HOOK_CODE,io_boundary,begin=a,end=a)
labels=[];assets=[]
def call(a,args=()):return a,ASSET,list(args)
def run(calls,p=(),label='asset'):
    labels.append(label);return oracle.case(calls,list(p))
for path in sorted((ROOT/'local/game-files/Game/Data').rglob('*.ske.xbx')):
    data=path.read_bytes();name=str(path.relative_to(ROOT/'local/game-files/Game/Data'))[:-4]
    p=[[DATA,data.hex()],[NAME,(name.encode()+b'\0').hex()],patch(IOC+4,'<I',len(data)),patch(ASSET+0x10,'<I',0)]
    for mode in ['direct','borrowed','owned','sync','async']:
        calls=[call(0x409970)]
        if mode in ['owned','direct']:p2=p+[patch(ASSET+0x24,'<I',DATA),patch(ASSET+0x20,'<I',FILE)]
        else:p2=p
        if mode=='direct':calls.append(call(0x409b80,[DATA,len(data)]))
        elif mode in ['borrowed','owned']:calls.append(call(0x409990,[DATA,len(data),0x12345678,0xffffffff,0]))
        else:
            calls.append(call(0x409a50,[NAME,int(mode=='async'),17,23,0xffffffff]))
            if mode=='async':
                calls.extend([(0x407710,0,[FILE,3,len(data),ASSET,0]),call(0x407620)])
        calls.extend([call(0x4099e0),call(0x4099e0)])
        # Initialization clears file and buffer: install owned fields after
        # construction by entering directly with its exact initialized image.
        if mode in ['owned','direct']:
            a=bytearray(b'\xad'*0x50)
            for off,value in [(0,0x645810),(8,0),(0x10,0),(0x14,0),(0x20,FILE),(0x24,DATA),(0x28,0),(0x34,0),(0x38,0x6455c0),(0x3c,0xffffffff),(0x40,0),(0x44,ASSET+0x38),(0x48,ASSET+0x38)]:struct.pack_into('<I',a,off,value)
            p2=p+[[ASSET,a.hex()]];calls=calls[1:]
        result=run(calls,p2,name+' '+mode)
        assert oracle.word(ASSET+8)==0 and oracle.word(ASSET+0x10)==0
        parsed_step=next(s for s in result if s['fn'] in ['0x409b80','0x409990','0x409a50'])
        if mode!='async':
            changes={at:int.from_bytes(bytes.fromhex(v),'little') for at,v in parsed_step['outputs']}
            assert changes[ASSET+8]==4,(name,mode)
        else:
            observed=[]
            for step in result:
                for at,value in step['outputs']:
                    if at==ASSET+8:observed.append(int.from_bytes(bytes.fromhex(value),'little'))
            assert observed==[0,1,2,4,0],(name,observed)
    assets.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
for flags in [0,1,2,255,256,257,0xffffffff]:
    run([call(0x409970),call(0x409a50,[NAME,flags,0,0,0])],
        [[NAME,(b'a'*251+b'\0').hex()],patch(IOC+20,'<I',1)],f'open failure asyncword{flags:x} maxpath')
# Standalone lifecycle helpers, untouched storage, no-data unload retaining a
# scratch buffer, and direct buffer releases are observable independently.
run([call(0x409970)]*2,label='constructor preserves unspecified bytes')
for state in [0,1,2,3,4,5,0xffffffff]:
    run([call(0x4075f0,[DATA,3,4,5,6]),call(0x407630,[DATA,0]),call(0x407600),call(0x407670),call(0x4076b0)],
        [patch(ASSET,'<I',0x645810),patch(ASSET+8,'<I',state)],f'state transitions {state}')
for data in [0,DATA,0xffffffff]:run([call(0x4076e0,[data])],label=f'set opaque data {data:x}')
for buffer in [0,DATA]:
    run([call(0x4099e0),call(0x409a10),call(0x409a10)],
        [patch(ASSET,'<I',0x645810),patch(ASSET+0x10,'<I',0),patch(ASSET+0x24,'<I',buffer)],f'empty unload scratch{buffer:x}')

coverage={hex(a):{'total':len(insns),'covered':sum(bool(hits[i.address]) for i in insns),
 'missing':[hex(i.address) for i in insns if not hits[i.address]]} for a,insns in instructions.items()}
missing={a for c in coverage.values() for a in c['missing']}
assert missing=={hex(a) for a in [0x409bdf,0x409be0,0x409be1,0x409be2,0x409be3,0x409be7,0x409bee,0x409bf1]}
coverage['0x409b80']['excluded']={a:'parser failure return is unreachable with the complete original parser and valid successful-allocation inputs' for a in sorted(missing)}
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(folder/'skeleton-asset-io.c'),'-o',str(folder/'skeleton-asset-io.wasm')],check=True)
scope='Thirteen asset routines, including complete original skeleton file/buffer load, parse, unload and state transitions, with original constructor/parser/math/destructor callees. All58 extracted skeletons follow direct, borrowed, owned, synchronous and asynchronous asset paths; asynchronous reading first returns state1, the real completion callback marks2, and real parsing marks4. Heap and open/size/read/close are explicit port interfaces. A comparison-only resident provider supplies original file bytes and records I/O arguments, file callbacks, state and allocation order. It does not implement the original Windows handle pool, archive resolver or a production browser filesystem. Entire arena, heap logs, I/O logs, returns and preserved registers compare exactly; no NaN allowances. Generic asset-manager miss construction and LoadSkeleton/script integration remain pending.'
fixture={'base':BASE,'memory':'skeleton-asset-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm',
 'memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'pointer_fields':sorted(fields),'pointer_exports':[[0x645810,'thug_skeleton_asset_methods_draft'],[0x6455c0,'thug_asset_link_methods'],[0x649f48,'thug_skeleton_methods_draft']],
 'function_exports':[[0x407710,'thug_asset_read_callback']],
 'native_callbacks':[{'module':'skeleton-asset-io.wasm','export':'fixture_io_'+name,'slots':[IO+4*(i+1)]} for i,name in enumerate(['open','size','read','close'])],
 'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial)
(folder/'skeleton-asset-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,
 'assets':assets,'io_calls':dict(io_calls),'raw_open_sync_words':dict(raw_open_sync),'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'skeleton-asset-original.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['scope','assets','callee_calls','heap_events']}))
