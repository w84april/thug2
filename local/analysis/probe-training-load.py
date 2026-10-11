"""Execute the real training startup through its recovered native asset load."""
from pathlib import Path
source=Path('local/analysis/probe-training-startup.py').read_text()
prefix=source[:source.index('native_hits=Counter();boundary_args=None')]
assert "'training-startup-original.json'" not in prefix
exec(compile(prefix,'<preserved training setup>','exec'))
import subprocess

AM,ATABLE,ABUCKETS,FILE,IO,IOC,IOLOG,SKE=BASE+0xe000,BASE+0xe080,BASE+0xe100,BASE+0xe200,BASE+0xe300,BASE+0xe400,BASE+0xf000,BASE+0x90000
memory=bytearray(initial)
write(AM,bytes(0x38));write(AM+0x1c,word(ATABLE));write(AM+0x14,bytes([0x5a]))
write(ATABLE,struct.pack('<6I',4,ABUCKETS,0,0,0,0));write(ABUCKETS,bytes(192))
write(FILE,bytes(0x3c));write(IO,struct.pack('<5I',IOC,0,0,0,0))
ske_path=ROOT/'local/game-files/Game/Data/skeletons/CS_Cardboard.ske.xbx';ske=ske_path.read_bytes()
write(SKE,ske);write(IOC,struct.pack('<6I',SKE,len(ske),FILE,0,IOLOG,CONTEXT))
initial=bytes(memory);oracle.initial=initial
for name,at,value in [('thug_asset_manager',0x6918dc,AM),('thug_asset_io_draft',0x300,IO)]:
    index[at]=len(globals_);globals_.append([name,at,4]);defaults.append(value)
oracle.globals=globals_;oracle.defaults=defaults;oracle.setword(0x684fe4,0x5df4ac)
functions['0x4750b0']['result']='word'
native_hits=Counter();native_arguments=[];observations={};io_calls=Counter()
def symbol(name):
    at=oracle.word(BUCKETS+(name&4095)*4)
    while at and oracle.word(at+4)!=name:at=oracle.word(at+16)
    assert at,hex(name);return at
def native_observer(cpu,address,size,user):
    native_hits[hex(address)]+=1
    if address==0x445640:
        sp=cpu.reg_read(UC_X86_REG_ESP);params=oracle.word(sp+4);assert oracle.word(sp+8)==SCRIPT
        args=[];item=oracle.word(params+4)
        while item:
            kind=cpu.mem_read(item,1)[0]>>1;name=oracle.word(item+4);value=oracle.word(item+8)
            text=bytes(cpu.mem_read(value,100)).split(b'\0',1)[0].decode() if kind in [3,4] else None
            args.append({'name':hex(name),'type':kind,'value':hex(value),'text':text});item=oracle.word(item+12)
        native_arguments.extend(args)
for at in native_names.values():oracle.cpu.hook_add(UC_HOOK_CODE,native_observer,begin=at,end=at)
def execute_entry(cpu,address,size,user):
    before=symbol(crc(b'tod_manager_inactive'));observations['tod_before']=oracle.word(before+12)
    stored=oracle.word(symbol(crc(b'TR_startup'))+12);n=oracle.word(stored+4);program=oracle.word(ENTRIES+4)
    prepared=bytes(cpu.mem_read(program,n));observations['prepared']={'address':program,'bytes':n,'sha256':hashlib.sha256(prepared).hexdigest()}
    for name,at in native_names.items():
        positions=[i for i in range(n-4) if prepared[i:i+5]==b'\x43'+word(at)]
        assert len(positions)==1;(pointer_fields.add(program+positions[0]+1))
oracle.cpu.hook_add(UC_HOOK_CODE,execute_entry,begin=0x4750b0,end=0x4750b0)
def identity(cpu,address,size,user):
    at=cpu.reg_read(UC_X86_REG_ECX);pointer_fields.add(at)
    if address==0x409970:pointer_fields.add(at+0x38);observations['asset']=at
    else:observations['skeleton']=at
for at in [0x409970,0x4a2c20]:oracle.cpu.hook_add(UC_HOOK_CODE,identity,begin=at,end=at)
record_original=oracle.record
def record_heap(kind,a,b,c):
    ptr=a if kind==2 else c;dest=oracle.word(CONTEXT+12)+oracle.word(CONTEXT+8)*48
    for i in range(4):
        if ptr+i*4 in pointer_fields:pointer_fields.add(dest+16+i*4)
    record_original(kind,a,b,c)
oracle.record=record_heap
def io(cpu,address,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);cleanup=0
    if address==0x5b6c60:
        actual=bytes(cpu.mem_read(arg(0),256)).split(b'\0',1)[0]
        assert actual==b'skeletons/CS_Cardboard.ske.Xbx';op,a,b,c=1,arg(1)&255,arg(2),0;result=FILE
    elif address==0x5b63a0:assert cpu.reg_read(UC_X86_REG_ECX)==FILE;op,a,b,c=2,FILE,0,0;result=len(ske)
    elif address==0x5b6740:
        assert cpu.reg_read(UC_X86_REG_ECX)==FILE and arg(1)==1 and arg(2)==len(ske)
        op,a,b,c=3,arg(0),arg(1),arg(2);result=len(ske);cleanup=12
        cpu.mem_write(a,ske)
    else:assert address==0x5b68a0 and arg(0)==FILE;op,a,b,c=4,FILE,0,0;result=1
    i=oracle.word(IOC+12);assert i<8;oracle.setword(IOC+12,i+1)
    cpu.mem_write(IOLOG+i*32,struct.pack('<8I',op,a,b,c,FILE,len(ske),oracle.word(CONTEXT+8),SKE))
    io_calls[hex(address)]+=1;cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for at in [0x5b6c60,0x5b63a0,0x5b6740,0x5b68a0]:oracle.cpu.hook_add(UC_HOOK_CODE,io,begin=at,end=at)
for at in [0x445640,0x408440,0x4087b0,0x409a50,0x409b80,0x4a39c0,0x462740,0x4750b0,0x473a70]:oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=at,end=at)
training=next(a for a in assets if a['member'].lower()=='levels\\tr\\tr_scripts.qb')
calls=[(0x472420,0,[TOD_FILENAME,TOD_DATA,0,0,0]),(0x472420,0,[training['filename'],training['address'],0,0,0]),
       (0x4738e0,SCRIPT,[]),(0x474540,SCRIPT,[crc(b'TR_startup'),0,0,0,0]),(0x4750b0,SCRIPT,[0])]
steps=oracle.case(calls)
assert steps[-1]['result']==0 and oracle.word(SCRIPT+12)==0
assert native_hits=={'0x449d00':1,'0x445640':1}
assert observations['tod_before']==0 and oracle.word(symbol(crc(b'tod_manager_inactive'))+12)==1
a=observations['asset'];s=observations['skeleton'];key=crc(b'CS_Cardboard')
assert oracle.word(AM+0x20)==a and oracle.word(AM+0x24)==0 and oracle.word(ATABLE+8)==1
bucket=ABUCKETS+(key&15)*12
assert oracle.word(bucket)==key and oracle.word(bucket+4)==a
assert oracle.word(a+8)==4 and oracle.word(a+16)==s and oracle.word(s+4)==34
assert oracle.word(a+0x20)==0 and oracle.word(a+0x24)==0 and oracle.word(a+0x28)==len(ske)
assert oracle.word(a+0x2c)==a and oracle.word(a+0x30)==a
assert oracle.cpu.mem_read(a+12,1)==b'\x5a'
assert io_calls=={'0x5b6c60':1,'0x5b63a0':1,'0x5b6740':1,'0x5b68a0':1}
for i in range(oracle.word(CONTEXT+8)):pointer_fields.add(LOG+i*48+36)
for step in steps:
    step['global_float_indices']=[]
    for at in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
        if step['globals'][index[at]]&0xfe==4:step['global_float_indices'].append(index[at+8])
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(folder/'training-load-io.c'),'-o',str(folder/'training-load-io.wasm')],check=True)
scope='The unchanged original68-byte TR_startup script completes after two original whole-file QB loads. Real Change and LoadSkeleton execute, including factory miss, extension selection, constructor, file/buffer loader,34-bone parser, lookup insertion and manager linking. Interpreter returns0 with null instruction pointer; tod_manager_inactive becomes1 and the original CS_Cardboard skeleton is ready in the manager. Heap and four file operations are explicit port services with exact resident original bytes. Full arena/globals/heap/I/O effects compare. This starts from an initialized script runtime/asset manager, not a cold engine boot; production archive/filesystem, level/skater creation, rendering and playable training remain incomplete.'
fixture={'base':BASE,'memory':'training-load-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-loader-memory.wasm',
 'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':functions,
 'float_fields':[],'cases':oracle.cases,'case_labels':['unchanged TR_startup completes real skeleton load'],'scope':scope,
 'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]],
 'pointer_exports':[[0x6f2364,'thug_script_loading_file'],[0x645810,'thug_skeleton_asset_methods_draft'],[0x6455c0,'thug_asset_link_methods'],[0x649f48,'thug_skeleton_methods_draft']],
 'pointer_fields':sorted(pointer_fields),'function_exports':[[0x449d00,'thug_script_change_native_draft'],[0x445640,'thug_load_skeleton_native_draft']],
 'native_callbacks':[{'module':'training-load-io.wasm','export':'fixture_training_'+n,'slots':[IO+4*(i+1)]} for i,n in enumerate(['open','size','read','close'])]}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-load-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original startup script completed; Wasm pending','specimen_sha256':SHA256,'cases':1,'completed_calls':5,'execute_result':steps[-1]['result'],
 'final_instruction':oracle.word(SCRIPT+12),'native_entries':dict(native_hits),'io_calls':dict(io_calls),
 'sources':[{'path':str(tod_path.relative_to(ROOT)),'sha256':hashlib.sha256(tod).hexdigest()},{'member':training['member'],'sha256':training['sha256']},{'path':str(ske_path.relative_to(ROOT)),'sha256':hashlib.sha256(ske).hexdigest()}],
 'prepared_program':observations['prepared'],'native_arguments':native_arguments,'tod_value_before':0,'tod_value_after':1,
 'asset':{'address':a,'key':hex(key),'state':4,'skeleton':s,'bones':34,'table_count':1,'file_closed':True,'read_buffer_released':True},
 'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'training-load-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['callee_calls','heap_events','scope']}))
