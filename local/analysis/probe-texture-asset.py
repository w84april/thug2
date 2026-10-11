"""Original texture asset I/O and option management with actual buffer parser."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned texture GPU/heap comparison setup>','exec'))
import zlib
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x407730,53,'asset_options_allocate',1,'word',False,False),
 (0x407770,61,'asset_options_release',1,'void',False,False),
 (0x40a620,146,'texture_asset_options',2,'void',False,True),
 (0x49ef90,30,'texture_filename',2,'void',False,False),
 (0x40a5a0,120,'texture_asset_parse',2,'void',True,True),
 (0x40a720,287,'texture_asset_load_file',5,'word',True,True),
 (0x40a840,198,'texture_asset_load_buffer',5,'word',True,True),
 (0x48bfe0,78,'model_base_path',2,'byte',False,False),
 (0x409e90,19,'model_asset_options_initialize',0,'word',False,True)]
for a,n,name,argc,result,heap,this in specs:
    functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap}
    code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
functions['0x407730']['pointer_result']=True;functions['0x407770']['pointer_args']=[0]
for a,name,argc,result,heap,this in [(0x40a580,'thug_texture_asset_initialize_draft',0,'word',False,True),
 (0x407620,'thug_asset_process_loaded_draft',0,'void',True,True),
 (0x407710,'thug_asset_read_callback',5,'void',False,False),
 (0x4087b0,'thug_asset_get_or_load_draft',9,'word',True,True)]:
    functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap,'stack_args':list(range(argc))}
POOL=0x691758;MASK=0x6918d8
for i in range(96):globals_.append(['thug_asset_options_storage_draft',POOL+i*4,4,i*4]);defaults.append(0xa5a5a5a5)
globals_.append(['thug_asset_options_mask_draft',MASK,4]);defaults.append(0)
for i in range(4):exports.append([POOL+i*96,'thug_asset_options_storage_draft',i*96])
exports += [[0x6459a8,'thug_texture_asset_methods_draft'],[0x6455c0,'thug_asset_link_methods']]
NAME,FILE,IO,IOC,IOLOG,SB,AM,TLS,LOCALE= [BASE+x for x in [0x8800,0x8500,0x13000,0x13200,0x18000,0x30000,0x35000,0x37000,0x37200]]
memory=bytearray(initial)
put(IO,'<5I',IOC,0,0,0,0);put(IOC,'<8I',INPUT,88,FILE,0,IOLOG,0,CONTEXT,P)
memory[FILE-BASE:FILE-BASE+0x3c]=bytes(0x3c);memory[SB-BASE:SB-BASE+16384]=bytes(16384)
memory[AM-BASE:AM-BASE+0x38]=bytes(0x38);memory[TLS-BASE:TLS-BASE+0x400]=bytes(0x400);put(TLS+0x64,'<I',LOCALE)
initial=bytes(memory);oracle.initial=initial
for n,a,v in [('thug_asset_io_draft',0x300,IO),('thug_script_symbol_buckets',0x6f3624,SB),('thug_asset_manager',0x6918dc,AM)]:globals_.append([n,a,4]);defaults.append(v)
oracle.globals=globals_;oracle.defaults=defaults
for a in [0x407910,0x40a580]:
    oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:fields.update([cpu.reg_read(UC_X86_REG_ECX),cpu.reg_read(UC_X86_REG_ECX)+0x38,cpu.reg_read(UC_X86_REG_ECX)+0x4c]),begin=a,end=a)
fields.update([P+0x4c,FILE+8,*[IOLOG+i*320+32 for i in range(32)]])
# Reuse the same real CRT setup as pinned file/factory comparisons.
setup=Path('local/analysis/probe-asset-factory.py').read_text()
setup=setup[setup.index('GET,GET_TLS,SET='):setup.index('exports=[[0x645568')]
exec(compile(setup,'<pinned CRT OS port setup>','exec'))
oracle.setword(0x684fe4,0x5df4ac)
io_calls=Counter()
def record_io(op,a,b,d,name=b''):
    c=[oracle.word(IOC+i*4) for i in range(8)];assert c[3]<32
    f,asset=c[2],c[7];oracle.setword(IOC+12,c[3]+1)
    values=[op,a,b,d,c[0],c[1],f,oracle.word(f+20),oracle.word(f+8),oracle.word(f+12),oracle.word(f+16),oracle.word(asset+8),oracle.word(asset+0x24),oracle.word(CONTEXT+8),oracle.word(asset+0x20),oracle.word(asset+0x10)]
    assert len(name)<256;oracle.cpu.mem_write(c[4]+c[3]*320,struct.pack('<16I',*values)+name+bytes(256-len(name)))
def io_boundary(cpu,at,size,user):
    sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);c=[oracle.word(IOC+i*4) for i in range(8)];cleanup=0
    if at==0x5b6c60:
        name=bytes(cpu.mem_read(arg(0),256)).split(b'\0',1)[0];record_io(1,arg(1)&255,arg(2),0,name);result=0 if c[5] else c[2]
    elif at==0x5b63a0:
        assert cpu.reg_read(UC_X86_REG_ECX)==c[2];record_io(2,c[2],0,0);result=c[1]
    elif at==0x5b6740:
        assert cpu.reg_read(UC_X86_REG_ECX)==c[2] and arg(1)==1 and arg(2)==c[1]
        record_io(3,arg(0),arg(1),arg(2));cpu.mem_write(arg(0),bytes(cpu.mem_read(c[0],c[1])));result=c[1];cleanup=12
    else:assert at==0x5b68a0;record_io(4,arg(0),0,0);result=1
    io_calls[hex(at)]+=1;cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for a in [0x5b6c60,0x5b63a0,0x5b6740,0x5b68a0]:oracle.cpu.hook_add(UC_HOOK_CODE,io_boundary,begin=a,end=a)
old_run=run
def run(g,calls,label,cache=None,registry=0,mask=0):
    # Original fixed storage is external to the arena; every word is watched.
    defaults[len(defaults)-4]=mask
    return old_run(g,calls,label,cache,registry)
class AssetGraph(Graph):
    def structure(self,items):
        s=self.alloc(8);nodes=[self.alloc(16) for _ in items];self.put(s,'<2I',0,nodes[0] if nodes else 0)
        for i,(key,kind,value) in enumerate(items):self.put(nodes[i],'<4I',kind*2,key,value,nodes[i+1] if i+1<len(nodes) else 0)
        return s
    def text(self,text):
        v=text.encode('latin1')+b'\0';p=self.alloc(len(v));self.data[p-BASE:p-BASE+len(v)]=v;return p
    def prepared(self,data,key=0x12345678):
        self.file(data);self.put(IOC+4,'<I',len(data));t=self.table();self.put(AM+0x1c,'<I',self.table());self.put(P+4,'<I',key)
        return t
for mask in [0,1,3,7,15,0xfffffff0,0xffffffff]:
    g=AssetGraph();calls=[call(0x407730,args=[n]) for n in [0,76,0xffffffff,96,1]]
    calls += [call(0x407770,args=[POOL+96*i]) for i in [2,0,3,1,1]]+[call(0x407730,args=[76])]
    run(g,calls,f'option pool mask{mask:x}',mask=mask)
for p in [0,POOL-4,POOL+1,POOL+384,P]:run(AssetGraph(),[call(0x407770,args=[p])],f'foreign option release{p:x}',mask=15)
for explicit in [False,True]:
    for flags in range(8):
        g=AssetGraph();options=g.alloc(76) if explicit else 0
        if options:g.put(options,'<19I',*[0x11223340+i for i in range(19)])
        params=g.structure([(0,13,k) for i,k in enumerate([0xe6237329,0x6875b9c0,0x86b52462]) if flags&(1<<i)]+([(0xbf34d221,1,0xffffffff)] if flags&1 else []))
        run(g,[call(0x40a620,P,[options,params])],f'options explicit{explicit}/flags{flags}')
for explicit in [False,True]:
    g=AssetGraph();options=g.alloc(76) if explicit else 0
    run(g,[call(0x40a620,P,[options,0])],f'options no script explicit{explicit}')
for text in ['', 'a','Letter_S.tex','models\\gameobjects\\skate\\letter_s\\letter_s.tex','x'*65,'A\xffZ']:
    g=AssetGraph();name=g.text(text);run(g,[call(0x49ef90,args=[P,name])],f'filename {text!r}')
for text in ['', 'a.skin','a.mdl','a.skin.mdl','a.mdl.skin','A.SKIN','path.skinny\\model.mdl','.skin','.mdl','a.ski','a.md','a.mdl.mdl']:
    for alias in [False,True]:
        g=AssetGraph();name=g.text(text);run(g,[call(0x48bfe0,args=[name,name if alias else P])],f'base path {text!r}/alias{alias}')
for fill in [0,0xa5,0xff]:
    g=AssetGraph();g.data[P-BASE:P-BASE+20]=bytes([fill])*20;run(g,[call(0x409e90,P)]*2,f'model options poison{fill}')
letter=ROOT/'local/game-files/Game/Data/models/GameObjects/SKATE/Letter_S/Letter_S.tex.xbx';data=letter.read_bytes()
assert hashlib.sha256(data).hexdigest()=='66bc9d8ac9cf881dbe381764e02fb4cd86976de99ae2fecfc5842d62a10406b3'
for mode in ['direct','borrowed','owned','sync','async']:
    for extra in range(4):
        g=AssetGraph();payload=data+bytes(range(extra));t=g.prepared(payload);name=g.text('models\\gameobjects\\skate\\letter_s\\letter_s.tex');options=g.alloc(76);g.put(options,'<3I',0xaabbcc00,0x87654321,0x12345678)
        calls=[call(0x40a580,P)]
        if mode=='direct':calls += [call(0x40a620,P,[options,0]),call(0x40a5a0,P,[INPUT,len(payload)])]
        elif mode in ['borrowed','owned']:calls += [call(0x40a840,P,[INPUT,len(payload),0x100 if mode=='borrowed' else 0x101,options,0])]
        else:
            calls += [call(0x40a720,P,[name,int(mode=='async'),17,options,0])]
            if mode=='async':calls += [call(0x407710,args=[FILE,3,len(payload),P,0]),call(0x407620,P)]
        run(g,calls,f'actual Letter S {mode}/trailing{extra}',cache=t)
        assert oracle.word(P+8)==4 and oracle.word(P+0x4c)==0 and oracle.word(P+0x20)==0
        assert bytes(oracle.cpu.mem_read(TEXTURES+0x100,32))==data[44:76] and bytes(oracle.cpu.mem_read(TEXTURES+0x200,8))==data[80:88]
        if mode in ['owned','sync','async']:assert bytes(oracle.cpu.mem_read(oracle.word(P+0x24),len(payload)))==payload
        assets.append({'mode':mode,'trailing':extra,'state':oracle.word(P+8),'gpu_events':oracle.word(CONTROL)})
for async_ in [0,1,255,256,257,0xffffffff]:
    g=AssetGraph();g.put(IOC+20,'<I',1);name=g.text('a'*61+'.tex')
    run(g,[call(0x40a580,P),call(0x40a720,P,[name,async_,0,0,0])],f'open failure async{async_:x}/max name')
    assert oracle.word(P+8)==1 and oracle.word(P+0x4c)==POOL and oracle.word(MASK)==1
# Actual factory load/cache hit, without substituting asset virtuals.
for async_ in [0,1]:
    g=AssetGraph();t=g.prepared(data);name=g.text('Letter_S.tex');g.put(IOC+28,'<I',HEAP)
    calls=[call(0x4087b0,AM,[name,0,0,0,async_,0,0x5a,0,0,0])]
    if async_:calls += [call(0x407710,args=[FILE,3,len(data),HEAP,0]),call(0x407620,HEAP)]
    calls += [call(0x4087b0,AM,[name,0,0,0,0,0,0x5a,0,0,0])]
    run(g,calls,f'actual factory file load and cachehit async{async_}',cache=t)
    assert oracle.word(HEAP+8)==4 and oracle.word(CONTROL+4)==1
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()};print('MISSING',json.dumps(missing),flush=True)
assert not any(missing.values()),missing
coverage={hex(a):{'total':len(c),'covered':len(c),'missing':[],'excluded':{}} for a,c in code.items()}
scope='Nine additional asset/option/path routines execute real texture dictionary parsing through direct, borrowed, copied, synchronous and asynchronous I/O paths using the unchanged Letter S texture. The real asset manager factory and cache are exercised with actual class virtuals. Missing files retain the original options and loading state. Entire arena, fixed options globals, heap logs, file calls and exact mip uploads compare with zero float allowances. Resident file and GPU providers are explicit comparison ports; texture destruction/unload, full model loading and playable rendering remain unavailable.'
fixture={'base':BASE,'memory':'texture-asset-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm',
 'memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],
 'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'function_exports':[[0x407710,'thug_asset_read_callback']],
 'pointer_initializers':[['thug_texture_allocation_scope_draft',oracle.stop+0x330]],
 'native_callbacks':[{'module':'texture-buffer-ports.wasm','export':'fixture_texture_'+name,'slots':slots,**({'original':oracle.stop+0x330} if name=='scope' else {})} for name,slots in [('create',[DVT+0x5c]),('lock',[TVT+0x4c]),('unlock',[TVT+0x50]),('scope',[])]]+
 [{'module':'skeleton-asset-io.wasm','export':'fixture_io_'+name,'slots':[IO+(i+1)*4]} for i,name in enumerate(['open','size','read','close'])],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'texture-asset-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'assets':assets,'io_calls':dict(io_calls),'gpu_calls':dict(gpu_counts),'scope':scope}
(folder/'texture-asset-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['scope','assets','instruction_coverage']}))
