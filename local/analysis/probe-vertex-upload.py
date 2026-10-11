"""Original vertex allocation/upload and shader mapping, with explicit ports."""
from pathlib import Path
source=Path('local/analysis/probe-texture-buffer.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<pinned heap/GPU setup>','exec'))
functions.clear();code.clear();hits.clear();oracle.counts.clear();oracle.coverage.clear()
CRTCTX,CRTBEGIN,CRTLIMIT,CRTLOG=BASE+0x13000,BASE+0x120000,BASE+0x160000,BASE+0x1d000
INDEXCTL,INDEXLOG,INDEXVT,INDEXDEV=BASE+0x18000,BASE+0x19000,BASE+0x1c000,BASE+0x160000
exec(compile((folder/'vertex-upload-ports-setup.py').read_text(),'<explicit separate CRT and GPU index ports>','exec'))
REG=len(globals_);globals_.append(['thug_mesh_vertex_registry',0x7865e4,4]);defaults.append(0)
for i in range(18):globals_.append(['thug_mesh_shader_handles_draft',0x7ca920+i*4,4,i*4]);defaults.append(0xabc00000+i)
initial=bytes(memory);oracle.initial=initial
specs=[(0x4d3ff0,150,'thug_mesh_vertex_buffer_construct_draft',3,'word',True),
 (0x4d40e0,255,'thug_mesh_vertex_buffer_upload_draft',0,'word',True),
 (0x4d5760,101,'thug_mesh_vertex_buffer_create_draft',0,'word',False),
 (0x4d5c30,143,'thug_mesh_vertex_load_draft',3,'void',True),
 (0x4d3ed0,161,'thug_mesh_shader_code_draft',1,'word',False),
 (0x4da710,21,'thug_mesh_shader_skip_draft',0,'word',False)]
for a,n,name,argc,result,this in specs:
 functions[hex(a)]={'name':name,'this':this,'result':result,'cleanup':argc*4,'memory':False}
 code[a]=list(md.disasm(pe.get_data(a-0x400000,n),a));oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=a+n-1)
functions['0x4d4090']={'name':'thug_vertex_buffer_lock','this':True,'result':'word','cleanup':16,'memory':False}
instructions=[]
for a,n,*_ in specs:instructions += [f'FUNCTION {a:08x} {n} bytes']+[f'{i.address:08x} {i.mnemonic} {i.op_str}' for i in code[a]]
(folder/'vertex-upload-instructions.txt').write_text('\n'.join(instructions)+'\n')
def run_case(g,calls,label,registry=0):
 defaults[REG]=registry;return run(g,calls,label)
for size in [0,1,2,3,4,5,31,32,33,3888]:
 for flags in [0,1,4,5,2,0xffffffff]:
  g=Graph();run_case(g,[call(0x4d3ff0,P,[size,0xabcd,flags]),call(0x4d5760,0,[size,0x80000000,flags])],f'constructor size{size}/flags{flags:x}')
for fill in [0,0xa5,0xff]:
 for result,output in [(0,1),(1,1),(0xffffffff,1),(0x80000000,0)]:
  g=Graph();g.data[P-BASE:P-BASE+36]=bytes([fill])*36;g.put(INDEXCTL+8,'<I',result);g.put(INDEXCTL+20,'<I',output)
  head=g.alloc(12);g.put(head,'<3I',P+512,0,0)
  run_case(g,[call(0x4d3ff0,P,[19,0xabcd,0])],f'constructor fill{fill}/HRESULT{result:x}/output{output}',registry=head)
g=Graph();g.put(CRTCTX+32,'<I',1);run_case(g,[call(0x4d5760,0,[73,8,0])],'outer wrapper allocation failure')
for n in [0,1,2,3,4,5,17,3888]:
 for flags,mode in [(0,0),(4,0),(4,1),(0,0x10),(0,0x2000),(0,0x2010),(0,0xffffffff)]:
  for lock in [0,1,0xffffffff,0x80000000]:
   g=Graph();data=g.alloc(n+20);g.data[data-BASE:data-BASE+n]=bytes((i*19+7)&255 for i in range(n))
   device=0 if (flags==4 and mode==1) else INDEXDEV
   g.put(P,'<9I',n,0,device,data,0xfffffffd,n,mode,flags,7);g.put(INDEXDEV,'<I',INDEXVT)
   g.put(INDEXCTL+12,'<2I',lock,0x87654321);g.put(INDEXCTL+24,'<I',int(lock<0x80000000))
   run_case(g,[call(0x4d40e0,P)]*2,f'upload size{n}/flags{flags}/mode{mode:x}/lock{lock:x}')
for offset in [-4,-1,0,1,2,4]:
 g=Graph();data=INDEXDEV+0x100;g.data[data-BASE-8:data-BASE+40]=bytes(range(48));g.put(INDEXDEV,'<I',INDEXVT)
 g.put(P,'<9I',17,0,INDEXDEV,data,13,17,0,0,0);g.put(INDEXCTL+28,'<I',offset&0xffffffff)
 run_case(g,[call(0x4d40e0,P)],f'overlap forward word copy{offset}')
for mode in [0,0x2000]:
 g=Graph();a=g.alloc(32);b=g.alloc(32);g.put(a,'<4I',1,2,3,4);g.put(b,'<4I',5,6,7,8)
 g.put(P,'<9I',16,0,INDEXDEV,a,5,16,mode,0,0);g.put(INDEXDEV,'<I',INDEXVT);g.put(INDEXDEV+0x8000,'<I',INDEXVT)
 g.put(INDEXCTL+32,'<5I',P,5,b,INDEXDEV+0x8000,0x12345678)
 run_case(g,[call(0x4d40e0,P)],f'callback changes live fields mode{mode:x}')
for n in [0,1,2,3,4,5,31,32,33,3888]:
 for aux in [False,True]:
  g=Graph();data=g.alloc(n+16);g.data[data-BASE:data-BASE+n]=bytes((i*11+9)&255 for i in range(n))
  g.put(P+0x74,'<2I',0x512,0);g.put(P+0x300,'<3I',0xabcd,0x4321,0xffffffe0)
  run_case(g,[call(0x4d5c30,P,[data,n,P+0x300 if aux else 0])],f'load size{n}/aux{aux}')
for offset in [0,5]:
 for n in [0,3,16]:
  for flags in [0,0x10,0x2000]:
   g=Graph();data=g.alloc(64);g.put(P,'<9I',16,0,INDEXDEV,data,0,0,0xffffffff,0,0);g.put(INDEXDEV,'<I',INDEXVT)
   run_case(g,[call(0x4d4090,P,[offset,n,P+64,flags]),call(0x4d40e0,P)],f'lock then upload offset{offset}/size{n}/flags{flags:x}')
for value in [*range(23),0x7fffffff,0x80000000,0xffffffff]:
 g=Graph();run_case(g,[call(0x4d3ed0,0,[value])],f'shader code{value:x}')
for size in [0,1,4,16,0xffffffff,0xfffffff8,0x80000000]:
 g=Graph();g.put(INPUT,'<3I',0xabcd,size,0x12345678);g.put(CURSOR,'<I',INPUT)
 run_case(g,[call(0x4da710,0,[CURSOR])],f'skip shader size{size:x}')
# Cursor aliases packet+4: the length is read before overwriting that word.
g=Graph();g.put(INPUT,'<3I',0xabcd,INPUT,0x12345678);run_case(g,[call(0x4da710,0,[INPUT+4])],'skip shader cursor alias')
coverage={hex(a):{'total':len(c),'covered':sum(bool(hits[i.address]) for i in c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in code.items()}
print('COVERAGE',json.dumps(coverage),flush=True)
scope='Six complete routines: vertex buffer construction, allocation, upload/unlock, mesh vertex loading, shader handle lookup and PC shader record skipping. Explicit separate CRT and GPU comparison ports; no drawing or complete mesh parser claimed.'
fixture={'base':BASE,'memory':'vertex-upload-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'texture-buffer-ports.wasm','memory_exports':['fixture_texture_allocate','fixture_values_release','fixture_values_scope'],
 'globals':globals_,'functions':functions,'float_fields':[],'cases':oracle.cases,'case_labels':labels,'pointer_fields':sorted(fields),'pointer_exports':exports,
 'pointer_initializers':[['thug_mesh_crt_allocate_draft',0x624031,0]],
 'native_callbacks':[{'module':'vertex-upload-ports.wasm','export':'fixture_mesh_crt_allocate','original':0x624031}]+[{'module':'vertex-upload-ports.wasm','export':'fixture_index_'+n,'slots':slots} for n,slots in [('create',[DVT+0x68,DVT+0x6c]),('lock',[INDEXVT+0x2c]),('unlock',[INDEXVT+0x30])]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'vertex-upload-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':len(labels),'calls':sum(len(c['steps']) for c in oracle.cases),'instruction_coverage':coverage,'index_calls':dict(index_calls),'crt_calls':dict(crt_calls),'scope':scope}
(folder/'vertex-upload-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
