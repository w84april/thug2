"""All factory branches with instrumented class virtuals; no gameplay stubs."""
from pathlib import Path
prefix=Path('local/analysis/probe-skeleton-asset.py').read_text().split('labels=[];assets=[]')[0]
exec(compile(prefix,'<preserved asset oracle setup>','exec'))
import itertools,zlib
AM,TABLE,AB,CONTROL,CBLOG,NODES,SB,SYM,PARAMS,ITEMS=BASE+0x6000,BASE+0x6100,BASE+0x6200,BASE+0x6500,BASE+0x30000,BASE+0x90000,BASE+0xb0000,BASE+0x7000,BASE+0x7100,BASE+0x7200
memory=bytearray(initial)
def init(at,fmt,*v):struct.pack_into(fmt,memory,at-BASE,*v)
memory[AM-BASE:AM-BASE+0x38]=bytes(0x38);init(AM+0x1c,'<I',TABLE)
init(TABLE,'<6I',4,AB,0,0,0,0);memory[AB-BASE:AB-BASE+192]=bytes(192)
memory[SB-BASE:SB-BASE+16388]=bytes(16388)
init(SYM,'<BBH4I',0x91,1,0,0x25dc7904,0,0,0);init(SB+(0x25dc7904&4095)*4,'<I',SYM)
init(CONTROL,'<11I',0,CBLOG,0,DATA+0x5000,0,0,0,0,0x7cf180,AM,CONTEXT)
DIAG=CONTROL+0x200
init(CONTROL+44,'<I',0);init(DIAG,'<2I',CONTROL,0)
memory[NAME-BASE:NAME-BASE+8]=b'x.SkE\0\0\0'
initial=bytes(memory);oracle.initial=initial
defaults=[IO]
def glob(name,at,value=0,width=4,offset=0):globals_.append([name,at,width,offset]);defaults.append(value)
glob('thug_asset_manager',0x6918dc,AM);glob('thug_node_table',0x6f0d84,NODES)
glob('thug_script_symbol_buckets',0x6f3624,SB);glob('thug_lookup_node_pool',0x7d1808)
glob('thug_async_pending',0x7cf17c);glob('thug_async_completed',0x7cf180,width=1);glob('thug_async_write_buffer',0x7cf18c)
glob('thug_async_completion_counts',0x7cf184);glob('thug_async_completion_counts',0x7cf188,offset=4)
oracle.globals=globals_;oracle.defaults=defaults
NEW=[
 (0x409220,'thug_scene_asset_initialize_draft',0,'word',False,False,25),
 (0x40a580,'thug_texture_asset_initialize_draft',0,'word',False,False,25),
 (0x4095f0,'thug_collision_asset_initialize_draft',0,'word',False,False,25),
 (0x409c40,'thug_model_asset_initialize_draft',0,'word',False,False,32),
 (0x40a210,'thug_animation2_asset_initialize_draft',0,'word',False,False,25),
 (0x407a30,'thug_cutscene_asset_initialize_draft',0,'word',False,False,18),
 (0x408bb0,'thug_qb_asset_initialize_draft',0,'word',False,False,25),
 (0x45d140,'thug_node_table_set_asset_draft',1,'void',False,False,13),
 (0x408bf0,'thug_qb_asset_register_draft',0,'void',False,False,17),
 (0x407810,'thug_asset_destroy_base_draft',0,'void',False,False,40),
 (0x4093e0,'thug_asset_destroy_forward_draft',0,'void',False,False,5),
 (0x407af0,'thug_asset_delete_draft',1,'word',True,False,33),
 (0x4075d0,'thug_asset_set_metadata_draft',3,'void',False,False,24),
 (0x4076f0,'thug_asset_set_dependency_draft',1,'word',False,False,10),
 (0x407700,'thug_asset_set_key_draft',1,'word',False,False,10),
 (0x407840,'thug_asset_add_dependent_draft',1,'void',True,False,72),
 (0x4079c0,'thug_asset_type_draft',1,'word',False,False,110),
 (0x407a60,'thug_asset_manager_flags_draft',0,'byte',False,False,4),
 (0x407b90,'thug_asset_find_object_draft',2,'word',False,True,112),
 (0x408440,'thug_asset_create_draft',9,'word',True,True,826),
 (0x4087b0,'thug_asset_get_or_load_draft',9,'word',True,True,191),
 (0x445640,'thug_load_skeleton_draft',2,'byte',True,True,95)]
for a,n,argc,result,heap,diag,size in NEW:
    f={'name':n,'result':result,'cleanup':argc*4,'memory':heap,'stack_args':list(range(argc))}
    if a==0x445640:f.update(this=False,cleanup=0)
    functions[hex(a)]=f
    instructions[a]=list(md.disasm(pe.get_data(a-0x400000,size),a))
    oracle.cpu.hook_add(UC_HOOK_CODE,trace,begin=a,end=a+size-1)
    oracle.cpu.hook_add(UC_HOOK_CODE,oracle.observe,begin=a,end=a)
# Original CRT extension comparisons run unchanged, with C-locale TLS services.
TLS,LOCALE=BASE+0xc0000,BASE+0xc0200
memory=bytearray(initial);memory[TLS-BASE:TLS-BASE+0x400]=bytes(0x400);struct.pack_into('<I',memory,TLS-BASE+0x64,LOCALE)
initial=bytes(memory);oracle.initial=initial
GET,GET_TLS,SET=oracle.stop+0x100,oracle.stop+0x110,oracle.stop+0x120
for slot,target in [(0x6450d4,GET),(0x7db10c,GET_TLS),(0x64516c,SET)]:oracle.setword(slot,target)
oracle.setword(0x68ef14,7);oracle.setword(0x68ecfc,LOCALE);last_error=0x12345678
for at,n in [(GET,0),(GET_TLS,4),(SET,4)]:oracle.cpu.mem_write(at,b'\xc2'+struct.pack('<H',n))
def os(cpu,at,size,user):
    global last_error
    sp=cpu.reg_read(UC_X86_REG_ESP)
    if at==GET:cpu.reg_write(UC_X86_REG_EAX,last_error)
    elif at==GET_TLS:assert oracle.word(sp+4)==7;cpu.reg_write(UC_X86_REG_EAX,TLS)
    else:last_error=oracle.word(sp+4)
for at in [GET,GET_TLS,SET]:oracle.cpu.hook_add(UC_HOOK_CODE,os,begin=at,end=at)
exports=[[0x645568,'thug_asset_base_methods'],[0x6455c0,'thug_asset_link_methods'],[0x645564,'thug_asset_detached_link_methods_draft'],[0x7cf180,'thug_async_completed']]
tables={2:(0x645700,'thug_scene_asset_methods_draft'),3:(0x6459a8,'thug_texture_asset_methods_draft'),4:(0x645778,'thug_collision_asset_methods_draft'),
 5:(0x6454b0,'thug_animation_asset_methods'),6:(0x645810,'thug_skeleton_asset_methods_draft'),7:(0x645888,'thug_model_asset_methods_draft'),
 8:(0x645928,'thug_animation2_asset_methods_draft'),9:(0x645600,'thug_cutscene_asset_methods_draft'),10:(0x645698,'thug_qb_asset_methods_draft')}
exports+=list(tables.values());fields.add(CONTROL+32)
fields.update(CBLOG+i*80+32 for i in range(128))
virtuals={};callback_counts=Counter()
for orig,name in tables.values():
    for offset,kind in [(0x14,1),(0xc,2),(4,3),(0x20,4)]:
        at=int.from_bytes(pe.get_data(orig-0x400000+offset,4),'little')
        assert at not in virtuals or virtuals[at]==kind;virtuals[at]=kind
def virtual(cpu,at,size,user):
    kind=virtuals[at];sp=cpu.reg_read(UC_X86_REG_ESP);a=cpu.reg_read(UC_X86_REG_ECX)
    # Direct destructor comparisons execute the actual body; only calls via
    # the factory's disposal virtual are instrumentation witnesses.
    if at==0x407af0 and oracle.word(sp)==oracle.stop:return
    argc=5 if kind==1 else 1 if kind==2 else 0;args=[oracle.word(sp+4+i*4) for i in range(argc)]
    cfg=[oracle.word(CONTROL+4*i) for i in range(11)];assert cfg[0]<128
    row=[kind,a,*args,*([0]*(5-len(args))),0,*[oracle.word(a+i*4) for i in range(8)],oracle.word(AM+0x28),oracle.word(AM+0x34),oracle.word(CONTEXT+8),oracle.word(a+0x34)]
    assert len(row)==20;cpu.mem_write(CBLOG+cfg[0]*80,struct.pack('<20I',*row));oracle.setword(CONTROL,cfg[0]+1)
    if kind==1:oracle.setword(a+16,cfg[3]);oracle.setword(a+8,4);result=cfg[2]
    elif kind==2:oracle.setword(a+0x18,oracle.word(a+0x18)^0x55aa55aa);result=a
    elif kind==3:result=oracle.word(a+16)
    else:
        oracle.setword(CONTROL+24,cfg[6]+1)
        if cfg[7]:oracle.setword(a+16,cfg[7])
        cpu.mem_write(cfg[8],b'\1');result=int(cfg[6]+1>cfg[5])
    callback_counts[kind]+=1;cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+argc*4)
for at in virtuals:oracle.cpu.hook_add(UC_HOOK_CODE,virtual,begin=at,end=at)
def diagnostic(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP)
    message=bytes(cpu.mem_read(oracle.word(sp+4),100)).split(b'\0',1)[0]
    assert message in [b'CAsyncFileLoader waiting for io completion: busy count %d completion %d\n',b'CAsyncFileLoader got completion: busy count %d completion %d\n']
    kind=1 if message.startswith(b'CAsyncFileLoader waiting ') else 2
    count=oracle.word(CONTROL+44);assert count<32
    cpu.mem_write(CONTROL+0x300+count*16,struct.pack('<4I',kind,oracle.word(sp+8),oracle.word(sp+12),0))
    oracle.setword(CONTROL+44,count+1)
    cpu.reg_write(UC_X86_REG_EAX,0);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,diagnostic,begin=0x401c30,end=0x401c30)
def base_identity(cpu,at,size,user):
    p=cpu.reg_read(UC_X86_REG_ECX);fields.update([p,p+0x38])
oracle.cpu.hook_add(UC_HOOK_CODE,base_identity,begin=0x407910,end=0x407910)
def link_identity(cpu,at,size,user):fields.add(oracle.word(CONTEXT))
oracle.cpu.hook_add(UC_HOOK_CODE,link_identity,begin=0x407840,end=0x407840)
labels=[]
spec={a:(argc,heap,diag) for a,_,argc,_,heap,diag,_ in NEW}
def call(fn,this=ASSET,args=()):
    argv=list(args)
    if fn in spec and spec[fn][2]:argv.append(DIAG)
    return fn,this,argv
def run(calls,p=(),label='factory'):
    labels.append(label);r=oracle.case(calls,p);assert last_error==0x12345678;return r
ctor=[r[0] for r in NEW[:7]]
for fn in ctor:run([call(fn)]*2,label=f'constructor{fn:x} untouched bytes')
for flag in range(256):run([call(0x407a60,AM)],[patch(AM+0x14,'<B',flag)],f'manager flag{flag}')
for ext in [b'BIN',b'COL',b'SCN',b'GEOM',b'MDL',b'SKA',b'FAM',b'SKE',b'SKIN',b'TEX',b'CUT',b'QB',b'',b'NONE',b'ske.xbx',b'SKE/',b'\xff\xfe']:
    for form in [ext,ext.lower(),ext[:1].lower()+ext[1:]]:
        for prefix in [b'a.',b'.',b'a.b.',b'a/.']:
            run([call(0x4079c0,AM,[NAME])],[[NAME,(prefix+form+b'\0').hex()]],f'extension {prefix+form!r}')
for name in [b'',b'SKE',b'a/b',b'a\\b']:
    run([call(0x4079c0,AM,[NAME])],[[NAME,(name+b'\0').hex()]],f'no extension {name!r}')
for flag in [0,1,2,3,256,257,0xffffffff]:
    run([call(0x409970),call(0x407af0,args=[flag]),call(0x407810),call(0x4093e0)],label=f'base destruction flags{flag:x}')
run([call(0x4075d0,args=[1,0x80000000,0xffffffff]),call(0x4076f0,args=[ASSET+0x100]),call(0x407700,args=[0x87654321]),
     call(0x45d140,NODES,[ASSET]),call(0x408bf0)],label='metadata and node registration')
run([call(0x409970),call(0x407840,args=[ASSET+0x100]),call(0x407840,args=[ASSET+0x200]),call(0x407810)],label='dependent link insertion and nonempty detach')
def factory(fn=0x408440,kind=6,key=0x123,dependency=0,async_=0):return call(fn,AM,[NAME,kind,key,dependency,async_,0x12121212,0x87654321,0x34343434,0x56565656])
for kind,result,retain,async_ in itertools.product(range(2,12),[0,1,0xffffffff],[0,1],[0,1,256,257]):
    p=[patch(CONTROL+8,'<I',result),patch(SYM+12,'<I',retain),patch(AM+0x28,'<4I',0x71717171,0x82828282,0x93939393,0xaabbcc01)]
    run([factory(kind=kind,async_=async_)],p,f'type{kind} result{result:x} retain{retain} async{async_:x}')
# Insertion order, duplicate keys, hash collisions, captured data, dependencies,
# and both manager lists use real lookup insertion/allocation and list methods.
for fn in [0x408440,0x4087b0]:
    for async_ in [0,1]:
        run([factory(fn,key=k,async_=async_) for k in [0x101,0x111,0x121,0x101]],label=f'linked collision sequence {fn:x}/{async_}')
run([factory(key=0x101),factory(key=0x111,dependency=0x101),factory(key=0x121,dependency=0x101)],label='real dependency list')
for fn in [0x407b90,0x4087b0]:
    for waits in [0,1,2,4]:
        p=[patch(AB+12,'<3I',0x101,ASSET,0),patch(ASSET,'<5I',0x645810,0,0,0,0x77777777),patch(CONTROL+20,'<3I',waits,0,0x88888888)]
        r=run([call(fn,AM,[0x101,1]) if fn==0x407b90 else factory(fn,key=0x101)],p,f'ready calls and captured data {fn:x}/{waits}')
        assert r[0]['result']==(ASSET if fn==0x407b90 else 0x77777777)
for null_head in [False,True]:
    p=[patch(AB+12,'<3I',0x101,0 if null_head else ASSET,ASSET+0x100),patch(ASSET+0x100,'<3I',0x101,ASSET,0),patch(ASSET,'<5I',0x645810,0,4,0,0x77777777)]
    run([call(0x407b90,AM,[0x101,0]),call(0x407b90,AM,[0x888,1])],p,f'null-valued collision {null_head}')
run([factory(kind=0,key=0)],label='extension and filename checksum selection')
run([factory(0x4087b0,kind=0,key=0)]*2,label='resolver selects filename checksum for miss and hit')
init_params=[patch(PARAMS,'<2I',0,ITEMS),patch(ITEMS,'<4I',6,0xa1dc81f9,NAME,ITEMS+16),patch(ITEMS+16,'<4I',26,0,0x123,0)]
run([call(0x445640,0,[PARAMS,0])],init_params,label='native script ABI invokes factory')

coverage={hex(a):{'total':len(instructions[a]),'covered':sum(bool(hits[i.address]) for i in instructions[a]),'missing':[hex(i.address) for i in instructions[a] if not hits[i.address]]} for a,_,_,_,_,_,_ in NEW}
missing={a for c in coverage.values() for a in c['missing']}
assert missing=={'0x40786d','0x408598','0x40863c'},missing
for c in coverage.values():
    if c['missing']:c['excluded']={a:'allocation failure leads to an original null write; outside the successful-allocation internal contract' for a in c['missing']}
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang'
subprocess.run([str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(folder/'asset-factory-callbacks.c'),'-o',str(folder/'asset-factory-callbacks.wasm')],check=True)
callback_specs=[{'module':'asset-factory-callbacks.wasm','export':'fixture_asset_'+name,'original':0x3e00100+i*16} for i,name in enumerate(['load','dispose','data','ready'])]
callback_specs.append({'module':'asset-factory-callbacks.wasm','export':'fixture_asset_diagnostic','slots':[DIAG+4]})
initializers=[[name,0x3e00100+i*16,offset] for orig,name in tables.values() for i,offset in enumerate([0x14,0xc,4,0x20])]
scope='Twenty-two original routines recover all asset factory type branches, seven constructors, node registration, metadata/dependency links, base destruction, extension matching, asset-object lookup/waits, get-or-load and native LoadSkeleton. Class virtuals are instrumented witnesses in this suite, including currently unrecovered non-skeleton loaders; they are test-only and never supplied as gameplay implementations. Original table insertion, allocation, CRC, C-locale comparison and async wait/completion code execute. Full arena/globals/heap/callback effects compare exactly. Separate unchanged TR_startup comparison uses the real skeleton class, file-loader/parser and original asset bytes. Valid types, initialized services, bounded paths and successful allocations are internal contracts.'
fixture={'base':BASE,'memory':'asset-factory-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'script-values-memory.wasm','memory_exports':['fixture_values_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'pointer_exports':exports,'pointer_fields':sorted(fields),'pointer_initializers':initializers,
 'native_callbacks':callback_specs,'cases':oracle.cases,'case_labels':labels,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'asset-factory-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'new_functions':22,'instruction_coverage':coverage,
 'virtual_callbacks':dict(callback_counts),'callee_calls':dict(oracle.coverage),'heap_events':dict(oracle.heap_events),'scope':scope}
(folder/'asset-factory-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['scope','callee_calls','heap_events']}))
