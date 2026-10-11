"""Original complete TR file-to-scene load, including billboard registration."""
from pathlib import Path
sector_source=Path('local/analysis/probe-training-level-material.py').read_text().split('oracle.scope_entries[MANAGER+0x200]=1;oracle.initial=initial=bytes(memory)')[0]
sector_source=sector_source.replace("exec(compile(setup,", "setup=setup.replace('BASE,SIZE=0x1000000,0x1e00000','BASE,SIZE=0x800000,0x2600000')\nexec(compile(setup,").replace('i<70000','i<125000')
exec(compile(sector_source,'<preserved texture and stream callbacks, expanded bounded arena>','exec'))
IOLOG,GPULOG,HEAP,LOG=BASE+0x800000,BASE+0xb00000,BASE+0x1000000,BASE+0xc00000
MESHCTL,BVT,TABLE=BASE+0x1200,BASE+0x3000,BASE+0x4000
put(CONTEXT,'<8I',HEAP,0x2000000,0,LOG,BASE,BASE+SIZE,0,0);put(CONTROL,'<3I',0x2800000,0,0)
put(FILE,'<2I',SCNDATA,SCNDATA+len(scn));put(MESHCTL,'<8I',0x2000000,0x2400000,0,0,0,0,0,0);oracle.event_limit=60000;oracle.instruction_limit=100000000
assert SCNDATA+len(scn)<IOLOG and IOLOG+125000*24<GPULOG and GPULOG+7000*64<LOG and LOG+60000*48<HEAP
buffer_setup=Path('local/analysis/probe-training-level-mesh.py').read_text().split('BCREATE,BLOCK,BUNLOCK=')[1].split("functions['0x4d4be0']")[0]
exec(compile('BCREATE,BLOCK,BUNLOCK='+buffer_setup,'<preserved bounded CRT and buffer ports>','exec'))
OPEN_INDEX=len(globals_);globals_ += [['thug_scene_file_open_draft',0x348,4],['thug_scene_file_close_draft',0x34c,4]];defaults += [0x5b9e60,0x5b9ea0]
TABLE_INDEX=len(globals_)
for i in range(33):globals_.append(['thug_mesh_material_table',0x775b80+i*4,4,i*4]);defaults.append(0);put(TABLE+i*4,'<I',0)
def file_lifetime(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x5b9e60:
  name,mode=oracle.word(sp+4),oracle.word(sp+8);assert bytes(cpu.mem_read(name,len(filename)))==filename and bytes(cpu.mem_read(mode,3))==b'rb\0'
  oracle.setword(FILE,SCNDATA);oracle.setword(MESHCTL+24,oracle.word(MESHCTL+24)+1);finish(FILE)
 else:
  assert oracle.word(sp+4)==FILE;oracle.setword(MESHCTL+28,oracle.word(MESHCTL+28)+1);finish(1)
for at in [0x5b9e60,0x5b9ea0]:cpu.hook_add(UC_HOOK_CODE,file_lifetime,begin=at,end=at)
functions={'0x49f050':{'name':'thug_texture_dictionary_get_buffer_draft','this':False,'result':'word','cleanup':0,'memory':True},'0x4b36d0':{'name':'thug_model_scene_file_load_draft','this':False,'result':'word','cleanup':0,'memory':True}}
oracle.functions=functions
exports += [[0x6499e0,'thug_model_scene_base_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft'],[0x6499dc,'thug_model_scene_list_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft'],[0x649a40,'thug_model_sector_base_methods_draft'],[0x64a718,'thug_model_sector_pc_methods_draft'],[0x64a368,'thug_model_geometry_lights_methods_draft'],[0x64a434,'thug_model_mesh_node_methods_draft'],[0x64a894,'thug_material_node_methods'],[0x64a898,'thug_material_sentinel_methods']]
functions_code={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x4b36d0,693),(0x4c6b10,1332),(0x4d7580,1373),(0x4cebe0,193)]};hits=Counter()
for a,c in functions_code.items():cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:hits.update([at]),begin=a,end=c[-1].address)
get=(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0]);oracle.initial=initial=bytes(memory)
steps=oracle.case([get]);dictionary=steps[-1]['result']
oracle.cases.clear();oracle.counts.clear();resources.clear();gpu_calls.clear();io_calls.clear();buffers.clear();hits.clear()
steps=oracle.case([get,(0x4b36d0,0,[NAME,dictionary,1,0,0,0])]);scene=steps[-1]['result'];header=oracle.word(scene+0x280)
assert oracle.word(FILE)==SCNDATA+len(scn) and oracle.word(MESHCTL+24)==oracle.word(MESHCTL+28)==1
assert oracle.word(oracle.word(header+0x18)+8)==870 and oracle.word(oracle.word(scene+0xd0)+8)==790
# Mirror the original embedded material table into the explicitly relocated
# host-owned table, preserving every compared word and original instruction.
for s in steps:
 data=struct.pack('<33I',*s['globals'][TABLE_INDEX:TABLE_INDEX+33]);s['outputs'].append([TABLE,data.hex()])
cpu.mem_write(TABLE,struct.pack('<33I',*steps[-1]['globals'][TABLE_INDEX:TABLE_INDEX+33]))
assert oracle.word(TABLE)==7
sectors=[];mesh_records=[];billboards=[]
table=oracle.word(scene+0xd0);buckets=oracle.word(table+4)
for i in range(1<<oracle.word(table)):
 entry=buckets+i*12
 while entry:
  sector=oracle.word(entry+4)
  if sector:
   geometry=oracle.word(sector+0x14);head=oracle.word(geometry+0x38);node=oracle.word(head+12);values=[]
   while node!=head:
    mesh=oracle.word(node+4);values.append(mesh);mat=oracle.word(mesh+0x14);v=oracle.word(mesh+0xcc)
    record={'mesh':mesh,'material':mat,'key':oracle.word(mat),'vertices':int.from_bytes(cpu.mem_read(mesh+0x22,2),'little'),'stride':cpu.mem_read(mesh+0x18,1)[0],'flags':oracle.word(mesh),'index_counts':list(struct.unpack('<8H',cpu.mem_read(mesh+0x24,16))),'vertex_buffer':v}
    mesh_records.append(record)
    if record['flags']&0x10:billboards.append({'mesh':mesh,'record':list(struct.unpack('<9I',cpu.mem_read(oracle.word(mesh+0x4c),36)))})
    node=oracle.word(node+12)
   assert len(values)==oracle.word(geometry+0x40)
   sectors.append({'sector':sector,'key':oracle.word(sector+4),'geometry':geometry,'meshes':values})
  entry=oracle.word(entry+8)
assert len(sectors)==790 and len(mesh_records)==2269 and len(billboards)==56
assert sum(v['vertices'] for v in mesh_records)==50814 and sum(sum(v['index_counts']) for v in mesh_records)==77029
for s in steps:
 for at,data in s['outputs']:
  raw=bytes.fromhex(data)
  for i in range(0,len(raw),4):
   if int.from_bytes(raw[i:i+4],'little') in {e[0] for e in exports}:fields.add(at+i)
 merged=[];chunks=[];start=end=0
 for at,data in s['outputs']:
  if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
  if not chunks:start=at
  chunks.append(data);end=at+len(data)//2
 if chunks:merged.append([start,''.join(chunks)])
 s['outputs']=merged
clang=ROOT/'.tools/wasi-sdk-34.0-arm64-macos/bin/clang';port=folder/'training-level-sector-ports.c';output=folder/'training-level-sector-ports.wasm'
cmd=[str(clang),'--target=wasm32-unknown-unknown','-O2','-nostdlib','-Wl,--no-entry,--export-all,--import-memory',str(port),'-o',str(output)];subprocess.run(cmd,check=True)
output.with_suffix('.build.json').write_text(json.dumps({'command':cmd,'source_sha256':hashlib.sha256(port.read_bytes()).hexdigest(),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+'\n')
prior=json.loads((folder/'training-level-material-fixtures.json').read_text());callbacks=[{**c,'module':'training-level-sector-ports.wasm'} for c in prior['native_callbacks']]
callbacks += [{'module':'training-level-sector-ports.wasm','export':'fixture_training_crt','original':0x624031}]+[{'module':'training-level-sector-ports.wasm','export':'fixture_training_buffer_'+n,'slots':slots} for n,slots in [('create',[DVT+0x68,DVT+0x6c]),('lock',[BVT+0x2c]),('unlock',[BVT+0x30])]]
# Previous callback addresses were expressed relative to its other arena.
for c in callbacks:
 if c.get('export')=='fixture_training_create':c['slots']=[DVT+0x5c]
 if c.get('export')=='fixture_training_lock':c['slots']=[TVT+0x4c]
 if c.get('export')=='fixture_training_unlock':c['slots']=[TVT+0x50]
callbacks += [{'module':'training-level-sector-ports.wasm','export':'fixture_training_'+n,'original':a} for n,a in [('open',0x5b9e60),('close',0x5b9ea0)]]
scope='Actual untouched TR.tex.xbx and TR.scn.xbx through original49f050 then entire4b36d0 file-to-scene load.790 registered sectors2269 meshes,56 billboard transforms and7 material groups, all bounds/file/heap/CRT/GPU storage compared. Original embedded material table explicitly relocated. No decoded scene records injected. Platform GPU storage is a test provider, not drawing or gameplay.'
fixture={**prior,'base':BASE,'memory':'training-level-sector-memory.bin','memory_adapter':ADAPTER,'memory_fixture':'training-level-sector-ports.wasm','globals':globals_,'functions':functions,'cases':oracle.cases,'case_labels':['complete training scene file load'],'pointer_fields':sorted(fields),'pointer_exports':exports,'native_callbacks':callbacks,
 'indirect_globals':['thug_mesh_material_table'],'pointer_globals':prior['pointer_globals']+[OPEN_INDEX,OPEN_INDEX+1],
 'pointer_initializers':prior['pointer_initializers']+[['thug_mesh_crt_allocate_draft',0x624031],['thug_scene_file_open_draft',0x5b9e60],['thug_scene_file_close_draft',0x5b9ea0],['thug_mesh_material_table',TABLE]],'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'training-level-sector-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'scene_sha256':hashlib.sha256(scn).hexdigest(),'texture_sha256':hashlib.sha256(tex).hexdigest(),'cases':1,'calls':2,'textures':len(resources),'materials':870,'scene':scene,'header':header,'sectors':sectors,'meshes':mesh_records,'billboards':billboards,'material_groups':oracle.word(TABLE),'buffers':buffers,'buffer_calls':[oracle.word(MESHCTL+o) for o in [12,16,20]],'crt_calls':oracle.word(MESHCTL+8),'file_calls':dict(io_calls),'gpu_calls':dict(gpu_calls),'heap_events':oracle.word(CONTEXT+8),'heap_end':hex(oracle.word(CONTEXT)),'file_position':oracle.word(FILE)-SCNDATA,'bounds':list(struct.unpack('<12I',cpu.mem_read(header+0x44,48))),
 'instruction_coverage':{hex(a):{'covered':sum(bool(hits[i.address]) for i in c),'total':len(c),'missing':[hex(i.address) for i in c if not hits[i.address]]} for a,c in functions_code.items()},'scope':scope}
(folder/'training-level-sector-original.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v if k not in ['sectors','meshes','billboards','buffers'] else len(v) for k,v in report.items()}),flush=True)
