"""Original texture asset I/O and option management with actual buffer parser."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned texture GPU/heap comparison setup>','exec'))
import zlib
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
specs=[(0x409e10,122,'model_asset_options',2,'void',False,True),
 (0x409c60,13,'model_asset_read_finished',0,'byte',False,True),
 (0x409da0,75,'model_asset_release_buffer',0,'void',True,True),
 (0x409eb0,645,'model_asset_load_file',5,'word',True,True),
 (0x40a140,208,'model_asset_load_buffer',5,'word',True,True)]
for a,n,name,argc,result,heap,this in specs:
 functions[hex(a)]={'name':'thug_'+name+'_draft','this':this,'result':result,'cleanup':argc*4,'memory':heap}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
for a,name,argc,result,heap,this in [(0x409c40,'thug_model_asset_initialize_draft',0,'word',False,True),
 (0x407620,'thug_asset_process_loaded_draft',0,'void',True,True),(0x407710,'thug_asset_read_callback',5,'void',False,False)]:
 functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4 if this else 0,'memory':heap,'stack_args':list(range(argc))}
functions['0x409e10']['pointer_args']=[0]
POOL=0x691758;MASK=0x6918d8
for i in range(96):globals_.append(['thug_asset_options_storage_draft',POOL+i*4,4,i*4]);defaults.append(0xa5a5a5a5)
globals_.append(['thug_asset_options_mask_draft',MASK,4]);defaults.append(0)
for i in range(4):exports.append([POOL+i*96,'thug_asset_options_storage_draft',i*96])
exports.append([POOL+4,'thug_asset_options_storage_draft',4])
exports += [[0x645888,'thug_model_asset_methods_draft'],[0x6455c0,'thug_asset_link_methods']]
NAME,FILE,IO,IOC,IOLOG,SB,AM,TLS,LOCALE= [BASE+x for x in [0x8800,0x8500,0x13000,0x13200,0x18000,0x30000,0x35000,0x37000,0x37200]]
memory=bytearray(initial)
put(IO,'<5I',IOC,0,0,0,0);put(IOC,'<8I',INPUT,88,FILE,0,IOLOG,0,CONTEXT,P)
memory[FILE-BASE:FILE-BASE+0x3c]=bytes(0x3c);memory[SB-BASE:SB-BASE+16384]=bytes(16384)
memory[AM-BASE:AM-BASE+0x38]=bytes(0x38);memory[TLS-BASE:TLS-BASE+0x400]=bytes(0x400);put(TLS+0x64,'<I',LOCALE)
initial=bytes(memory);oracle.initial=initial
for n,a,v in [('thug_asset_io_draft',0x300,IO),('thug_script_symbol_buckets',0x6f3624,SB),('thug_asset_manager',0x6918dc,AM)]:globals_.append([n,a,4]);defaults.append(v)
oracle.globals=globals_;oracle.defaults=defaults
for a in [0x407910,0x409c40]:
    oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:fields.update([cpu.reg_read(UC_X86_REG_ECX),cpu.reg_read(UC_X86_REG_ECX)+0x38,cpu.reg_read(UC_X86_REG_ECX)+0x4c]),begin=a,end=a)
fields.update([P+0x4c,FILE+8,*[IOLOG+i*320+32 for i in range(32)]])
# Reuse the same real CRT setup as pinned file/factory comparisons.
setup=Path('local/analysis/probe-asset-factory.py').read_text()
setup=setup[setup.index('GET,GET_TLS,SET='):setup.index('exports=[[0x645568')]
exec(compile(setup,'<pinned CRT OS port setup>','exec'))
oracle.setword(0x684fe4,0x5df4ac)
CACHE_IO=BASE+0x13600;PARSE=oracle.stop+0x340;PARSELOG=BASE+0x24000
memory=bytearray(initial)
put(CACHE_IO,'<4I',IOC,0,0,0);put(IOC,'<12I',INPUT,13,FILE,0,IOLOG,CONTEXT,INPUT+0x800,7,FILE+0x80,0,0,0)
memory[FILE+0x80-BASE:FILE+0x80-BASE+0x3c]=bytes(0x3c);memory[PARSELOG-BASE:PARSELOG-BASE+32]=bytes(32)
initial=bytes(memory);oracle.initial=initial
for n,a,v in [('thug_model_file_cache_draft',0x304,CACHE_IO)]:globals_.append([n,a,4]);defaults.append(v)
oracle.setword(0x645888+0x34,PARSE)
io_calls=Counter()
def event(op,a,b,d,name=b''):
 c=[oracle.word(IOC+i*4) for i in range(12)];assert c[3]<32 and len(name)<512;oracle.setword(IOC+12,c[3]+1)
 oracle.cpu.mem_write(c[4]+c[3]*544,struct.pack('<8I',op,a,b,d,oracle.word(c[5]+8),c[9],c[0],c[1])+name+bytes(512-len(name)))
def io_boundary(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4);c=[oracle.word(IOC+i*4) for i in range(12)];cleanup=0
 if at in [0x5b6c60,0x5b7c00,0x5b72e0]:
  name=bytes(cpu.mem_read(arg(0),512)).split(b'\0',1)[0];second=name.endswith(b'.cas.Xbx')
  if at==0x5b6c60:event(1,arg(1)&255,arg(2),int(second),name);result=0 if c[9]&(1<<second) else c[8 if second else 2]
  elif at==0x5b7c00:
   assert [arg(i) for i in range(1,5)]==[0]*4;event(5,0,0,0,name);result=c[0]
  else:event(6,0,0,0,name);result=c[1]
 elif at in [0x5b63a0,0x5b6740]:
  file=cpu.reg_read(UC_X86_REG_ECX);assert file in [c[2],c[8]];second=file==c[8]
  if at==0x5b63a0:event(2,file,0,0);result=c[7 if second else 1]
  else:
   assert arg(1)==1 and arg(2)==c[7 if second else 1];event(3,arg(0),file,arg(2));result=arg(2);cleanup=12
   cpu.mem_write(arg(0),bytes(cpu.mem_read(c[6 if second else 0],result)))
 elif at==0x5b68a0:event(4,arg(0),0,0);result=1
 elif at==0x5b7200:event(7,arg(0),0,0);result=0
 else:
  assert at==PARSE;p=cpu.reg_read(UC_X86_REG_ECX);cpu.mem_write(PARSELOG,struct.pack('<6I',oracle.word(PARSELOG)+1,p,arg(0),arg(1),oracle.word(p+8),oracle.word(p+0x5c)));result=0;cleanup=8
 io_calls[hex(at)]+=1;cpu.reg_write(UC_X86_REG_EAX,result);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4+cleanup)
for a in [0x5b6c60,0x5b63a0,0x5b6740,0x5b68a0,0x5b7c00,0x5b72e0,0x5b7200,PARSE]:oracle.cpu.hook_add(UC_HOOK_CODE,io_boundary,begin=a,end=a)
fields.update([FILE+0x80+8,P+0x50])
old_run=run
def run(g,calls,label,cache=None,registry=0,mask=0):
    # Original fixed storage is external to the arena; every word is watched.
    defaults[next(i for i,g in enumerate(globals_) if g[0]=='thug_asset_options_mask_draft')]=mask
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

for explicit in [False,True]:
 for flags in range(4):
  g=AssetGraph();options=g.alloc(20) if explicit else 0
  if options:g.put(options,'<5I',0x11223344,0x55667788,0x99aabbcc,0xddeeff00,0xabcdef01)
  params=g.structure(([(0,13,0x01a1482e)] if flags&1 else [])+([(0xbf34d221,1,0xffffffff)] if flags&2 else []))
  run(g,[call(0x409e10,P,[options,params])],f'model options explicit{explicit} flags{flags}')
for opts in [0,POOL,POOL+4]:
 g=AssetGraph();run(g,[call(0x409e10,P,[opts,0])],f'model options no script overlap{opts:x}')
for count in [0,1,2,0xffffffff]:
 g=AssetGraph();g.put(P+0x5c,'<I',count);run(g,[call(0x409c60,P)]*3,f'read completions count{count:x}')
for companion in [0,P+0x200]:
 for primary in [0,P+0x100]:
  for cached in [0,0x98765432]:
   g=AssetGraph();g.put(P+0x24,'<I',primary);g.put(P+0x4c,'<I',cached);g.put(P+0x58,'<I',companion)
   run(g,[call(0x409da0,P)]*2,f'release companion{bool(companion)} primary{bool(primary)} cached{bool(cached)}')
for copy in [0,1,256,257]:
 for no_copy in [0,1]:
  for length in [0,1,2,3,4,13]:
   g=AssetGraph();options=g.alloc(20);g.data[options-BASE:options-BASE+20]=bytes(20);g.data[options+17-BASE]=no_copy
   run(g,[call(0x409c40,P),call(0x40a140,P,[INPUT,length,copy,options,0])],f'buffer copy{copy} retained{no_copy} length{length}')
for name in ['MODELS\\Test.mdl','MODELS\\Test.skin','A.SKIN','a.mdl.skin','x'*502+'.mdl']:
 for async_ in [0,1,256,257]:
  for fail in [0,1,2]:
   g=AssetGraph();np=g.text(name);g.put(IOC+36,'<I',fail);g.put(P+0x4c,'<I',0)
   calls=[call(0x409c40,P),call(0x409eb0,P,[np,async_,0,0,0])]
   run(g,calls,f'file {name[:24]} async{async_} fail{fail}')
# Real two-file async completion order: first callback keeps state1, second sets2.
for reverse in [False,True]:
 g=AssetGraph();np=g.text('a.skin');g.put(P+0x4c,'<I',0)
 files=[(FILE,13),(FILE+0x80,7)];files=files[::-1] if reverse else files
 calls=[call(0x409c40,P),call(0x409eb0,P,[np,1,0,0,0])]+[call(0x407710,args=[f,3,n,P,0]) for f,n in files]+[call(0x407620,P)]
 run(g,calls,f'async completion reversed{reverse}');assert oracle.word(P+8)==2 and oracle.word(P+0x5c)==0
missing={hex(a):[hex(i.address) for i in c if not hits[i.address]] for a,c in code.items()};print('MISSING',json.dumps(missing),flush=True)
# options[17] is forced0 before any I/O. These two instructions require an
# external provider to mutate engine options, outside the file-provider contract.
excluded={'0x409eb0':{'0x40a0eb':'options17 reset0; file provider does not mutate options','0x40a0f1':'same unreachable scope-exit branch'}}
for a,v in missing.items():assert set(v)==set(excluded.get(a,{})),(a,v)
coverage={hex(a):{'total':len(c),'covered':len(c)-len(missing[hex(a)]),'missing':missing[hex(a)],'excluded':excluded.get(hex(a),{})} for a,c in code.items()}
scope='Five model asset routines: option preparation, read-completion counting, buffer release, buffer loading and full file orchestration. Ordinary and cached skin files, companion files, failures, low-byte flags, copies and asynchronous completion order compare exact arena/globals/heap/I-O effects. The parse virtual is explicitly instrumented in this unit suite; actual geometry is not manufactured. The separate training suite reaches the real model-parser boundary.'
fixture={'base':BASE,'memory':'model-asset-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,'function_exports':[[0x407710,'thug_asset_read_callback']],
 'pointer_initializers':[['thug_model_asset_methods_draft',PARSE,0x34]],'native_callbacks':[{'module':'model-asset-ports.wasm','export':'fixture_model_parse','original':PARSE}]+[{'module':'model-asset-ports.wasm','export':'fixture_model_'+name,'slots':[IO+(i+1)*4]} for i,name in enumerate(['open','size','read','close'])]+[{'module':'model-asset-ports.wasm','export':'fixture_model_'+name,'slots':[CACHE_IO+(i+1)*4]} for i,name in enumerate(['acquire','cached_size','cached_release'])],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'model-asset-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(oracle.counts.values()),'instruction_coverage':coverage,'io_calls':dict(io_calls),'scope':scope}
(folder/'model-asset-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
