"""All original TR mesh records, after original complete textures and materials.
Only serialized slices are concatenated; no decoded game state is imported.
Scene/sector assembly is deliberately outside this comparison.
"""
from pathlib import Path
src=Path('local/analysis/probe-training-level-material.py').read_text().split('oracle.scope_entries[MANAGER+0x200]=1;oracle.initial=initial=bytes(memory)')[0]
exec(compile(src.replace('i<70000','i<100000'),'<preserved recorded texture/material platform setup>','exec'))
manifest=json.loads((folder/'training-level-mesh-flow-trace.json').read_text());meshes=manifest['meshes'];assert len(meshes)==2269
assert manifest['scene_sha256']==hashlib.sha256(scn).hexdigest()
blob=scn[12:110338]+b''.join(scn[m['position']:m['end_position']] for m in meshes)
IOLOG,GPULOG=BASE+0x7b0000,BASE+0xa00000
HEAP=BASE+0xb00000;MESHBASE=BASE+0xa70000;HEADER=BASE+0x4000;MESHCTL=BASE+0x1200;BVT=BASE+0x3000
put(CONTEXT,'<2I',HEAP,0x2000000);oracle.event_limit=15000
assert LOG+oracle.event_limit*48<TEXDATA and IOLOG+100000*24<GPULOG
assert GPULOG+7000*64<MESHBASE and MESHBASE+len(meshes)*216<HEAP
memory[SCNDATA-BASE:SCNDATA-BASE+len(scn)]=bytes(len(scn));memory[SCNDATA-BASE:SCNDATA-BASE+len(blob)]=blob
put(FILE,'<2I',SCNDATA,SCNDATA+len(blob));put(MESHCTL,'<6I',0x2000000,0x2400000,0,0,0,0)
memory[MESHBASE-BASE:MESHBASE-BASE+len(meshes)*216]=b'\xa5'*(len(meshes)*216)
BCREATE,BLOCK,BUNLOCK=oracle.stop+0x200,oracle.stop+0x210,oracle.stop+0x220
put(DVT+0x68,'<2I',BCREATE,BCREATE);put(BVT+0x2c,'<2I',BLOCK,BUNLOCK)
for name,at,value,width,off in [('thug_mesh_index_registry',0x7865e8,0,4,0),('thug_mesh_vertex_registry',0x7865e4,0,4,0),('thug_mesh_shader_conversion_enabled_draft',0x786ab8,0,1,0)]:globals_.append([name,at,width,off]);defaults.append(value)
pe=load()
for name,at,n in [('thug_mesh_shader_handles_draft',0x7ca920,18),('thug_mesh_vertex_formats_draft',0x775b64,6)]:
 for i in range(n):globals_.append([name,at+i*4,4,i*4]);defaults.append(int.from_bytes(pe.get_data(at+i*4-0x400000,4),'little'))
buffers=[]
def crt(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);n=oracle.word(sp+4);p=oracle.word(MESHCTL);end=(p+n+19)&~3;assert end<=0x2400000
 oracle.setword(MESHCTL,end);oracle.setword(MESHCTL+8,oracle.word(MESHCTL+8)+1)
 if n:cpu.mem_write(p,b'\xa5'*n)
 finish(p)
cpu.hook_add(UC_HOOK_CODE,crt,begin=0x624031,end=0x624031)
def buffer_gpu(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);arg=lambda i:oracle.word(sp+4+i*4)
 if at==BCREATE:
  dev,n,usage,fmt,pool,out,shared=[arg(i) for i in range(7)];assert dev==DEVICE and pool==shared==0
  p=oracle.word(MESHCTL+4);end=(p+256+n+15)&~15;assert end<=0x2800000
  oracle.setword(MESHCTL+4,end);oracle.setword(MESHCTL+12,oracle.word(MESHCTL+12)+1);cpu.mem_write(p,struct.pack('<4I',BVT,n,usage,fmt));oracle.setword(out,p)
  buffers.append({'pointer':p,'bytes':n,'usage':usage,'format':fmt});finish(0,7)
 elif at==BLOCK:
  p,off,n,out,flags=[arg(i) for i in range(5)];assert off+n<=oracle.word(p+4) and not flags
  oracle.setword(out,p+256+off);oracle.setword(MESHCTL+16,oracle.word(MESHCTL+16)+1);finish(0,5)
 else:
  assert oracle.word(arg(0))==BVT;oracle.setword(MESHCTL+20,oracle.word(MESHCTL+20)+1);finish(0,1)
for at in [BCREATE,BLOCK,BUNLOCK]:cpu.hook_add(UC_HOOK_CODE,buffer_gpu,begin=at,end=at)
functions['0x4d4be0']={'name':'thug_render_mesh_initialize','this':True,'result':'word','cleanup':0,'memory':False}
functions['0x4d6100']={'name':'thug_mesh_file_parse_draft','this':True,'result':'void','cleanup':20,'memory':True}
code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0xd6100,1038),0x4d6100));hits=Counter()
cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=0x4d6100,end=0x4d650d)
get=(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0]);oracle.initial=bytes(memory)
steps=oracle.case([get]);dictionary=steps[-1]['result'];texture_table=oracle.word(dictionary+12)
steps=oracle.case([get,(0x4d3390,0,[FILE,texture_table])]);table=steps[-1]['result'];assert oracle.word(table+8)==870
put(HEADER+0x18,'<I',table);oracle.initial=initial=bytes(memory)
oracle.cases.clear();oracle.counts.clear();resources.clear();gpu_calls.clear();io_calls.clear();buffers.clear();hits.clear()
calls=[get,(0x4d3390,0,[FILE,texture_table])]
for i,m in enumerate(meshes):
 addr=MESHBASE+i*216;calls += [(0x4d4be0,addr,[]),(0x4d6100,addr,[FILE,int(m['args'][1],16),HEADER,0,int(m['args'][4],16)])]
print('ORIGINAL',len(calls),'calls',len(blob),'serialized bytes',flush=True)
steps=oracle.case(calls);assert oracle.word(FILE)==SCNDATA+len(blob)
assert oracle.word(texture_table+8)==596 and len(resources)==596
vertices=indices=0
for i,m in enumerate(meshes):
 a=MESHBASE+i*216;n=int.from_bytes(cpu.mem_read(a+0x22,2),'little');counts=list(struct.unpack('<8H',cpu.mem_read(a+0x24,16)))
 assert n==m['vertices'] and counts==m['index_counts'] and cpu.mem_read(a+0x18,1)[0]==m['stride']
 assert hex(oracle.word(a+0x38))==m['formats'][0] and oracle.word(oracle.word(a+0x14))==int(m['args'][1],16)
 vertices+=n;indices+=sum(counts)
 # All CPU and GPU vertex copies must agree; shader/material fields and each
 # actual source record additionally compare through the full arena fixture.
 v=oracle.word(a+0xcc);nbytes=oracle.word(v);assert bytes(cpu.mem_read(oracle.word(v+12),nbytes))==bytes(cpu.mem_read(oracle.word(v+8)+256,nbytes))
 for slot,count in enumerate(counts):
  if count:
   v=oracle.word(a+0x54+slot*4);assert bytes(cpu.mem_read(oracle.word(v+16),count*2))==bytes(cpu.mem_read(oracle.word(v+12)+256,count*2))
for s in steps:
 merged=[];chunks=[];start=end=0
 for at,data in s['outputs']:
  if len(data)==8 and int(data[6:8]+data[4:6]+data[2:4]+data[0:2],16) in {e[0] for e in exports}:fields.add(at)
  if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
  if not chunks:start=at
  chunks.append(data);end=at+len(data)//2
 if chunks:merged.append([start,''.join(chunks)])
 s['outputs']=merged
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'training-level-mesh-ports.c';output=folder/'training-level-mesh-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
prior=json.loads((folder/'training-level-material-fixtures.json').read_text());callbacks=[{**c,'module':'training-level-mesh-ports.wasm'} for c in prior['native_callbacks']]
callbacks += [{'module':'training-level-mesh-ports.wasm','export':'fixture_training_crt','original':0x624031}]+[{'module':'training-level-mesh-ports.wasm','export':'fixture_training_buffer_'+n,'slots':slots} for n,slots in [('create',[DVT+0x68,DVT+0x6c]),('lock',[BVT+0x2c]),('unlock',[BVT+0x30])]]
scope='All2269 raw mesh records from790 original training sectors, concatenated without decoded state, follow the full original596 textures/870 materials. Each mesh is initialized by original4d4be0 and parsed by4d6100. Whole arena, file reads/seeks, heap, CRT, material references and all vertex/index CPU/GPU storage compare. This isolates mesh loading; sector assembly, drawing and gameplay remain incomplete.'
fixture={**prior,'memory':'training-level-mesh-memory.bin','memory_fixture':'training-level-mesh-ports.wasm','globals':globals_,'functions':functions,'cases':oracle.cases,'case_labels':['every training mesh after full textures and materials'],'pointer_fields':sorted(fields),'native_callbacks':callbacks,'pointer_initializers':prior['pointer_initializers']+[['thug_mesh_crt_allocate_draft',0x624031]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-level-mesh-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'scene_sha256':hashlib.sha256(scn).hexdigest(),'texture_sha256':hashlib.sha256(tex).hexdigest(),'serialized_mesh_bytes':len(blob)-110326,'serialized_input_sha256':hashlib.sha256(blob).hexdigest(),'meshes':len(meshes),'vertices':vertices,'indices':indices,'textures':len(resources),'materials':870,'cases':1,'calls':len(steps),'buffers':buffers,'buffer_calls':[oracle.word(MESHCTL+o) for o in [12,16,20]],'crt_calls':oracle.word(MESHCTL+8),'file_calls':dict(io_calls),'gpu_calls':dict(gpu_calls),'heap_events':oracle.word(CONTEXT+8),'file_position':oracle.word(FILE)-SCNDATA,'instruction_coverage':{'covered':sum(bool(hits[i.address]) for i in code),'total':len(code)},'scope':scope}
(folder/'training-level-mesh-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='buffers'}),flush=True)
