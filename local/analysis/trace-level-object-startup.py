"""Combine whole original QB startup state and complete TR scene; trace LevelObjects."""
from pathlib import Path
import types,sys
folder=Path('local/analysis')
# A separate larger comparison arena, never overlapping the original stack/stop.
raw=Path('tools/script_heap_oracle.py').read_text().replace('self.stack=0x3000000;self.stop=0x3f00000','self.stack=0x7000000;self.stop=0x7f00000')
module=types.ModuleType('level_object_oracle');exec(compile(raw,'<relocated comparison stack>','exec'),module.__dict__);sys.modules[module.__name__]=module
source=Path('tools/verify_script_load.py').read_text().split('labels=[];max_heap=HEAP')[0]
source=source.replace(';report_path.unlink(missing_ok=True)','').replace(";(out/'script-load-memory.bin').write_bytes(initial)",'')
source=source.replace('from script_heap_oracle import ScriptHeapOracle','from level_object_oracle import ScriptHeapOracle').replace('BASE,SIZE=0x1000000,0x1e00000','BASE,SIZE=0x800000,0x5800000').replace('BASE+0xb00000','BASE+0x1c00000')
source=source.replace("put(CONTEXT,'<9I',HEAP,BASE+SIZE", "put(CONTEXT,'<9I',HEAP,0x4000000")
source=source.replace('event_limit=(HEAP-LOG)//48','event_limit=180000')
assert '.write_' not in source and '.unlink(' not in source
exec(compile(source,'<original QB loader setup>','exec'))
for name,marker in [('probe-training-node-registration.py','regs='),('probe-training-prop-components.py','loads=')]:
 src=(folder/name).read_text().split(marker)[0];src=src.split("exec(compile(source,")[1].split('\n',1)[1]
 exec(compile(src,'<original '+name+' setup>','exec'))
src=(folder/'probe-training-model-transform.py').read_text().split('steps=oracle.case(prefix);array=')[0]
src=src.split("exec(compile(source,")[1].split('\n',1)[1]
src=src.replace('elif at in [a for _,a in newtypes if a!=0x421490]:','elif at in [a for _,a in newtypes if a not in (0x421490,0x433d90)]:')
src=src.replace("exec(compile(Path('local/analysis/asset-ready-training-ports-setup.py').read_text(),'<explicit texture platform ports>','exec'))",'')
src=src.replace("exec(compile((folder/'vertex-upload-ports-setup.py').read_text(),'<separate CRT and index GPU providers>','exec'))",'')
exec(compile(src,'<original component and interpreter setup>','exec'))
src=(folder/'probe-training-scene-create.py').read_text().split('initial=bytes(memory);oracle.initial=initial')[0]
src=src.split("exec(compile(source,")[1].split('\n',1)[1]
exec(compile(src,'<original single-player creation setup>','exec'))
# Metadata occupies the former isolated asset-port area. Script cache remains CACHE.
DEVICE,DVT,TVT,CONTROL,FILE,NAME,IOCTRL,MESHCTL,BVT,MTABLE,TEXCACHE,OWNER_HEADER=[BASE+n for n in [0xf1000,0xf1100,0xf1200,0xf1300,0xf2000,0xf2100,0xf2200,0xf2300,0xf2400,0xf2500,0xf2600,0xf2800]]
TEXDATA,SCNDATA,IOLOG,GPULOG=[BASE+n for n in [0x1000000,0x1400000,0x1700000,0x1a00000]]
memory[BASE+0xf1000-BASE:BASE+0xf3000-BASE]=bytes(0x2000)
put(DEVICE,'<I',DVT);put(CONTROL,'<4I',0x5000000,0,0,0);put(MESHCTL,'<9I',0x4000000,0x4800000,0,0,0,0,0,0,0);put(OWNER_HEADER,'<I',HSTATE)
data_root=ROOT/'local/game-files/Game/Data/levels/TR';tex=(data_root/'TR.tex.xbx').read_bytes();scn=(data_root/'TR.scn.xbx').read_bytes()
memory[TEXDATA-BASE:TEXDATA-BASE+len(tex)]=tex;memory[SCNDATA-BASE:SCNDATA-BASE+len(scn)]=scn
filename=b'levels\\TR\\TR.scn.Xbx\0';memory[NAME-BASE:NAME-BASE+len(filename)]=filename
SHORTNAME=NAME+0x80;memory[SHORTNAME-BASE:SHORTNAME-BASE+3]=b'TR\0';put(FILE,'<2I',SCNDATA,SCNDATA+len(scn))
for n,a,v in [('thug_texture_resource_registry_draft',0x7cc254,0),('thug_mesh_device',0x7d69e0,DEVICE),('thug_scene_file_read_draft',0x340,0x5b9ee0),('thug_scene_file_seek_draft',0x344,0x5b9fa0),('thug_scene_file_open_draft',0x348,0x5b9e60),('thug_scene_file_close_draft',0x34c,0x5b9ea0)]:glob(n,a,v)
for i,v in enumerate([4,TEXCACHE,0,0xffffffff,0,0]):glob('thug_model_texture_table_draft',0x700f04+i*4,v,offset=i*4)
TABLE_INDEX=len(globals_)
for i in range(33):glob('thug_mesh_material_table',0x775b80+i*4,0,offset=i*4)
# Use the original existing script locale; registry setup must not replace it.
src=(folder/'level-register-oracle-setup.py').read_text().split('# Ordinary narrow-string')[0];exec(compile(src,'<original scene registry setup>','exec'))
oracle.scope_entries[HSTATE]=1;oracle.instruction_limit=200000000;cpu=oracle.cpu
CREATE,LOCK,UNLOCK=oracle.stop+0x300,oracle.stop+0x310,oracle.stop+0x320
put(DVT+0x5c,'<I',CREATE);put(TVT+0x4c,'<2I',LOCK,UNLOCK)
src=(folder/'probe-training-level-material.py').read_text().split('\nresources=[];')[1].split('oracle.scope_entries[MANAGER+0x200]')[0]
saved_fields=fields.copy();saved_exports=exports[:]
src=src.replace('assert SCNDATA<=start<=start+n<=oracle.word(file+4)',"assert SCNDATA<=start<=start+n<=oracle.word(file+4),(hex(file),hex(start),width,count,hex(oracle.word(file+4)),hex(SCNDATA),dict(io_calls))")
exec(compile('resources=[];'+src.replace('i<70000','i<125000'),'<original recorded texture and scene file ports>','exec'))
fields.update(saved_fields);exports+=saved_exports
src=(folder/'probe-training-level-mesh.py').read_text().split('BCREATE,BLOCK,BUNLOCK=')[1].split("functions['0x4d4be0']")[0]
# The shader globals were already initialized by the component setup.
src=src[:src.index('for name,at,value,width,off in')]+src[src.index('buffers=[]'):]
src=src.replace('0x2400000','0x4800000').replace('0x2800000','0x5000000')
exec(compile('BCREATE,BLOCK,BUNLOCK='+src,'<original recorded CRT and buffer ports>','exec'))
def file_lifetime(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP)
 if at==0x5b9e60:
  name,mode=oracle.word(sp+4),oracle.word(sp+8);assert bytes(cpu.mem_read(name,len(filename)))==filename and bytes(cpu.mem_read(mode,3))==b'rb\0'
  oracle.setword(FILE,SCNDATA);oracle.setword(MESHCTL+24,oracle.word(MESHCTL+24)+1);finish(FILE)
 else:assert oracle.word(sp+4)==FILE;oracle.setword(MESHCTL+28,oracle.word(MESHCTL+28)+1);finish(1)
for a in [0x5b9e60,0x5b9ea0]:cpu.hook_add(UC_HOOK_CODE,file_lifetime,begin=a,end=a)
def owner_query(cpu,at,size,user):
 p=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);assert HEAP<=p<0x4000000
 oracle.setword(CONTROL+12,oracle.word(CONTROL+12)+1);finish(OWNER_HEADER)
cpu.hook_add(UC_HOOK_CODE,owner_query,begin=0x5ba090,end=0x5ba090)
for name in ['training-geometry-clone-fixtures.json','training-scene-create-fixtures.json']:
 for e in json.loads((folder/name).read_text())['pointer_exports']:
  if e not in exports:exports.append(e)
functions.update({'0x49f050':{'name':'thug_texture_dictionary_get_buffer_draft','this':False,'result':'word','cleanup':0,'memory':True},'0x48ccb0':{'name':'thug_level_scene_load_draft','this':False,'result':'word','cleanup':0,'memory':True},'0x468ec0':{'name':'thug_level_object_create_prefix_draft','this':False,'result':'void','cleanup':0,'stack_args':[0]}})
# Independent arena-capacity assertions. These are platform state, not game data.
assert STRINGS<LOG and LOG+oracle.event_limit*48<TEXDATA
assert TEXDATA+len(tex)<SCNDATA and SCNDATA+len(scn)<IOLOG and IOLOG+125000*24<GPULOG and GPULOG+7000*64<HEAP
oracle.initial=initial=bytes(memory)
trace_hits=Counter();trace=[]
from collections import deque
from unicorn import UC_HOOK_BLOCK
recent_blocks=deque(maxlen=80)
def block_trace(cpu,at,size,user):
 if trace:recent_blocks.append(hex(at))
def begin_blocks(cpu,at,size,user):
 if not trace:cpu.hook_add(UC_HOOK_BLOCK,block_trace)
cpu.hook_add(UC_HOOK_CODE,begin_blocks,begin=0x468ec0,end=0x468ec0)
for a in [0x468ec0,0x468b60,0x468cb0,0x45f330,0x45dad0,0x475790,0x420d10,0x41ffa0,0x420480,0x48e660]:
 def track(cpu,at,size,user):
  trace_hits[hex(at)]+=1
  if len(trace)<2000:trace.append([hex(at),hex(cpu.reg_read(UC_X86_REG_ECX)),hex(oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4))])
 cpu.hook_add(UC_HOOK_CODE,track,begin=a,end=a)
cpu.hook_add(UC_HOOK_CODE,created_object,begin=0x468ee1,end=0x468ee1)
wrapper_code={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x468ec0,85),(0x468b60,333)]};wrapper_hits=Counter()
for a,c in wrapper_code.items():cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:wrapper_hits.update([at]),begin=a,end=c[-1].address)
# Preparation derives live node and dictionary pointers using original loading.
get=(0x49f050,0,[0x12345678,TEXDATA,len(tex),0,0,0,0]);prefix_qb=prefix[:]
print('Preparing full QB and textures',flush=True)
steps=oracle.case(prefix_qb+[get]);dictionary=steps[-1]['result'];nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
helper=(folder/'probe-training-scene-create.py').read_text().split('def invoke(')[1].split('selected=[]')[0]
exec(compile('def invoke('+helper,'<original node getter calls>','exec'))
inventory=json.loads((folder/'training-scene-node-inventory.json').read_text())['nodes'];selected=[]
for n in inventory:
 if n['class_text']=='LevelObject' and n['created_at_start']:
  p=oracle.word(items+n['index']*4);assert checksum(p,0x12b4e660)==0xb7b3bd86 and invoke(0x476b40,p,[0x7c2552b9],4)&255
  selected.append({**n,'node':p,'alternate':bool(invoke(0x476b40,p,[0x69c257e9],4)&255)})
assert len(selected)==31
print('Selected31 LevelObjects',[(n['index'],n['text'],n['alternate']) for n in selected],flush=True)
all_startup=selected[:];selected=[n for n in all_startup if not n['alternate']];assert len(selected)==12
scene_call=(0x48ccb0,0,[SHORTNAME,dictionary,1,0,0,0]);calls=prefix_qb+[get,scene_call,(0x4738e0,SCRIPT,[])]+[(0x5a4ff0,0,[n['node'],SCRIPT]) for n in selected]
oracle.cases.clear();oracle.counts.clear();resources.clear();gpu_calls.clear();io_calls.clear();buffers.clear();created.clear();trace.clear();trace_hits.clear();factory_hit.clear()
print('Original full scene then first ordinary LevelObject to collision-factory boundary',flush=True)
steps=oracle.case(calls[:10]);scene=steps[8]['result'];header=oracle.word(scene+0x280)
assert oracle.word(oracle.word(scene+0xd0)+8)==790 and oracle.word(oracle.word(header+0x18)+8)==870
before=bytes(cpu.mem_read(BASE,SIZE));fn,this,args=calls[10];sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<3I',oracle.stop,*args));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
cpu.emu_start(fn,oracle.stop,count=oracle.instruction_limit)
assert factory_hit==[0x41c920] and cpu.reg_read(UC_X86_REG_EIP)==0x41c920
assert not created #468cb0 has not returned; no completed object claimed.
after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
for page in range(0,SIZE,4096):
 if before[page:page+4096]!=after[page:page+4096]:
  for i in range(page,min(page+4096,SIZE),4):
   if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
steps.append({'fn':hex(fn),'this':this,'args':args,'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
model=active_model['component'];obj=oracle.word(model+12);renderer=oracle.word(model+0x208);sentinel=oracle.word(renderer+0x10);part_link=oracle.word(sentinel+4)
assert oracle.word(obj+0x14)==int(selected[0]['name'],16) and oracle.word(model+4)==0x286a8d26
chain=[];c=oracle.word(obj+0x100)
while c:
 assert len(chain)<20;chain.append({'address':c,'type':oracle.word(c+4)});c=oracle.word(c+16)
assert len(chain)==6 and chain[-1]['address']==model
part=oracle.word(part_link);geometry=oracle.word(part);instance=oracle.word(geometry+0x4c)
assert part_link!=sentinel and oracle.word(part_link+4)==sentinel and oracle.word(renderer+0x14)==1
objects=[{**selected[0],'object':obj,'flags':oracle.word(obj+0x104),'script':oracle.word(obj+0x10),'components':chain,'model':model,'renderer':renderer,'bound':cpu.mem_read(model+0x235,1)[0],'complete':False,'parts':[{'part':part,'geometry':geometry,'instance':instance,'meshes':[oracle.word(oracle.word(geometry+0x3c)+i*4) for i in range(oracle.word(geometry+0x40))],'matrix':list(struct.unpack('<16I',cpu.mem_read(instance+4,64)))}]}]
assert objects[0]['bound']==1
print('Original boundary reached after real geometry binding:',selected[0]['text'],'components',len(chain),'mesh clones',len(objects[0]['parts'][0]['meshes']),flush=True)
(folder/'level-object-startup-trace.json').write_text(json.dumps({'selected':selected,'all_startup':all_startup,'created':created,'trace_counts':dict(trace_hits),'trace':trace,'heap_end':hex(oracle.word(CONTEXT)),'heap_events':oracle.word(CONTEXT+8),'completed_calls':10,'interrupted_calls':1,'boundary':'0x41c920','playable':False},indent=2)+'\n')
# Relocate identities appearing in live objects or captured allocation snapshots.
for i in range(oracle.word(CONTEXT+8)):
 for j in [4,5,6,7,9,10]:fields.add(LOG+i*48+j*4)
identities_set={e[0] for e in exports}|{e[0] for e in function_exports}
for step in steps:
 step['outputs'].append([MTABLE,struct.pack('<33I',*step['globals'][TABLE_INDEX:TABLE_INDEX+33]).hex()])
 for at,data in step['outputs']:
  raw=bytes.fromhex(data)
  for i in range(0,len(raw),4):
   if int.from_bytes(raw[i:i+4],'little') in identities_set:fields.add(at+i)
 step['global_float_indices']=[]
 for a in [0x6f2348,0x6f2568,*range(0x6f2370,0x6f24b0,16)]:
  if step['globals'][index[a]]&0xfe==4:step['global_float_indices'].append(index[a+8])
 merged=[];chunks=[];start=end=0
 for at,data in step['outputs']:
  if chunks and at!=end:merged.append([start,''.join(chunks)]);chunks=[]
  if not chunks:start=at
  chunks.append(data);end=at+len(data)//2
 if chunks:merged.append([start,''.join(chunks)])
 step['outputs']=merged
module_name='level-object-startup-ports.wasm'
callbacks=[{'module':module_name,'export':'fixture_training_'+name,**options} for name,options in [('create',{'slots':[DVT+0x5c]}),('lock',{'slots':[TVT+0x4c]}),('unlock',{'slots':[TVT+0x50]}),('scope',{'original':oracle.stop+0x330}),('read',{'original':0x5b9ee0}),('seek',{'original':0x5b9fa0}),('open',{'original':0x5b9e60}),('close',{'original':0x5b9ea0}),('crt',{'original':0x624031}),('buffer_create',{'slots':[DVT+0x68,DVT+0x6c]}),('buffer_lock',{'slots':[BVT+0x2c]}),('buffer_unlock',{'slots':[BVT+0x30]})]]
callbacks.append({'module':module_name,'export':'fixture_collision_factory_boundary','original':0x41c920})
scope='Whole original object/skutils/ped/TR QB files register1917nodes, then all596textures and the full790-sector2269-mesh training scene load and register. Native Create begins the first ordinary startup LevelObject LO_forlease03, assembles six real components and binds original scene geometry through the actual gameobj_add_components script. Execution stops before unrecovered Collision factory41c920; no factory or successful object return is substituted. Full arena/globals/heap/I-O/GPU comparison storage checked. No startup LevelObject finishes creation in this fixture. The other bouncing path needs Rigidbody42ef00. Production rendering and playable gameplay remain unavailable.'
used={s['fn'] for s in steps};fixture={'base':BASE,'memory':'level-object-startup-memory.bin','memory_adapter':ADAPTER,'memory_fixture':module_name,'memory_exports':['fixture_loader_allocate','fixture_loader_release','fixture_values_scope'],'globals':globals_,'functions':{k:v for k,v in functions.items() if k in used},'float_fields':[],'boundary_address':BOUNDARY,'boundary_factory':0x41c920,'cases':oracle.cases,'case_labels':['full original training scene and first ordinary LevelObject to actual Collision factory boundary'],'pointer_symbols':parser['pointer_symbols'],'pointer_globals':[index[0x6f2560]]+[index[a] for a in [0x340,0x344,0x348,0x34c]]+registry_pointer_globals,'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES},'indirect_globals':['thug_mesh_material_table'],'pointer_initializers':[['thug_mesh_crt_allocate_draft',0x624031],['thug_texture_allocation_scope_draft',oracle.stop+0x330],['thug_scene_file_read_draft',0x5b9ee0],['thug_scene_file_seek_draft',0x5b9fa0],['thug_scene_file_open_draft',0x5b9e60],['thug_scene_file_close_draft',0x5b9ea0],['thug_mesh_material_table',MTABLE]],'native_callbacks':callbacks,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'level-object-startup-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':len(steps),'completed_calls':10,'interrupted_calls':1,'completed_objects':0,'boundary':'0x41c920','objects':objects,'unavailable_bouncing_objects':[n for n in all_startup if n['alternate']],'scene':scene,'header':header,'dictionary':dictionary,'textures':len(resources),'resources':resources,'buffers':buffers,'buffer_calls':[oracle.word(MESHCTL+o) for o in [12,16,20]],'crt_calls':oracle.word(MESHCTL+8),'heap_events':oracle.word(CONTEXT+8),'heap_end':hex(oracle.word(CONTEXT)),'file_calls':dict(io_calls),'gpu_calls':dict(gpu_calls),'scope':scope,'playable':False,'instruction_coverage':{hex(a):{'covered':sum(bool(wrapper_hits[i.address]) for i in c),'total':len(c),'missing':[hex(i.address) for i in c if not wrapper_hits[i.address]]} for a,c in wrapper_code.items()}}
(folder/'level-object-startup-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',len(objects),'objects',sum(len(o['components']) for o in objects),'components',flush=True)
