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
src=src.replace('elif at in [a for _,a in newtypes if a!=0x421490]:','elif at in [a for _,a in newtypes if a not in (0x421490,0x433d90,0x41c920)]:')
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
# Original file resident at a distinct, bounded address; game parser relocates it.
from collision_file import layout
COLLDATA=BASE+0x1b00000;collision=(data_root/'TR.col.xbx').read_bytes();collision_layout=layout(collision)
assert GPULOG+7000*64<COLLDATA and COLLDATA+len(collision)<HEAP
memory[COLLDATA-BASE:COLLDATA-BASE+len(collision)]=collision
oracle.initial=initial=bytes(memory)
glob('thug_collision_load_observer_draft',0x6fa7c8,0)
exports.append([0x645c18,'thug_static_collision_methods'])
functions['0x49d590']={'name':'thug_scene_collision_load_draft','this':True,'result':'byte','cleanup':8,'memory':True}
collision_code={a:list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(a-0x400000,n),a)) for a,n in [(0x49d590,483),(0x49e890,15),(0x49eaa0,40),(0x48df10,10)]};collision_hits=Counter()
for a,c in collision_code.items():cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:collision_hits.update([at]),begin=a,end=c[-1].address)

glob('thug_asset_manager',0x6918dc,0);glob('thug_asset_manager_references_draft',0x6918e0,0)
functions['0x4088e0']={'name':'thug_asset_manager_acquire_draft','this':False,'result':'void','cleanup':0,'memory':True}
extra=[]
REG_MOV=len(globals_)
for i,v in enumerate([0x645d34,0xffffffff,0,0x691978,0x691978]):glob('thug_moving_collision_sentinel_draft',0x691978+i*4,v,offset=i*4)
MOV_HEAD=len(globals_);globals_.append(['thug_moving_collision_list',0x691984,4]);defaults.append(0x691978)
registry_pointer_globals += [REG_MOV,REG_MOV+3,REG_MOV+4,MOV_HEAD]
exports += [[0x691978,'thug_moving_collision_sentinel_draft'],[0x645d34,'thug_collision_sentinel_methods_draft'],[0x645aa0,'thug_collision_node_methods_draft'],[0x645ce0,'thug_moving_collision_methods'],[0x645bc0,'thug_box_collision_methods_draft'],[0x645aa8,'thug_compound_collision_methods_draft'],[0x645b00,'thug_rigid_collision_base_methods_draft'],[0x645eec,'thug_collision_component_methods_draft'],[0x645658,'thug_asset_manager_methods_draft'],[0x64728c,'thug_module_base_methods_draft'],[0x647284,'thug_module_node_methods_draft'],[0x64548c,'thug_task_base_methods_draft'],[0x64549c,'thug_task_node_methods_draft'],[0x6476f0,'thug_asset_task_methods_draft']]
function_exports += [[0x41c920,'thug_collision_component_create_draft'],[0x407eb0,'thug_asset_task_pending_draft']]
count=int.from_bytes(memory[OBJECTS+0x44-BASE:OBJECTS+0x48-BASE],'little');assert count==10
put(OBJECTS+0x44,'<I',11);slot=OBJECTS+0x48+count*8;put(slot,'<2I',0xffb39248,0x42ef00);fields.add(slot+4)
function_exports.append([0x42ef00,'thug_rigidbody_create_draft']);exports.append([0x6463f8,'thug_rigidbody_methods_draft'])
glob('thug_rigidbody_initialization_constant_draft',0x6939d0,0)
oracle.initial=initial=bytes(memory)
f=json.loads((folder/'level-collision-load-fixtures.json').read_text());old=f['cases'][0]['steps'];selected=json.loads((folder/'level-collision-load-trace.json').read_text())['selected']
selected+= [n for n in json.loads((folder/'level-collision-load-trace.json').read_text())['all_startup'] if n['alternate']]
calls=[(int(s['fn'],16),s['this'],s['args']) for s in old[:10]]+[(0x4088e0,0,[1]),(0x4738e0,SCRIPT,[])]+[(0x5a4ff0,0,[n['node'],SCRIPT]) for n in selected]
print('Original real manager and all31 startup LevelObjects',flush=True)
try:steps=oracle.case(calls)
except Exception as e:print('FAILED',repr(e),'EIP',hex(cpu.reg_read(UC_X86_REG_EIP)),'created',len(created),'factory',factory_hit,flush=True);raise
assert len(steps)==43 and len(created)==31 and not factory_hit
objects=[]
for n,obj in zip(selected,created):
 chain=[];component=oracle.word(obj+0x100);model=0;collision_component=0
 while component:
  kind=oracle.word(component+4);chain.append({'address':component,'type':kind})
  if kind==0x286a8d26:model=component
  if kind==0xa432dc41:collision_component=component
  component=oracle.word(component+16)
 assert model and (collision_component or n['alternate']) and oracle.word(obj+0x14)==int(n['name'],16)
 renderer=oracle.word(model+0x208);head=oracle.word(renderer+0x10);parts=[];link=oracle.word(head+4)
 while link!=head:
  part=oracle.word(link);geometry=oracle.word(part);instance=oracle.word(geometry+0x4c)
  parts.append({'part':part,'geometry':geometry,'instance':instance});link=oracle.word(link+4)
 inner=oracle.word(collision_component+0x18) if collision_component else 0
 objects.append({**n,'object':obj,'components':chain,'model':model,'renderer':renderer,'collision_component':collision_component,'collision':inner,'collision_kind':hex(oracle.word(inner)) if inner else None,'parts':parts,'flags':oracle.word(obj+0x104),'script':oracle.word(obj+0x10),'complete':True})
print('Completed',[(o['text'],len(o['components']),bool(o['collision'])) for o in objects],flush=True)
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
callbacks=[row for row in f['native_callbacks'] if row.get('original')!=0x41c920]
scope='Original full training startup: all31 CreatedAtStart LevelObjects, including19 bouncing props using recovered Rigidbody factory/initializer/finalizer and actual QB script. Ordinary12 prior path preserved. Whole memory, globals and heap compare through43 completed original calls. File/GPU ports remain explicit comparison storage; no actual rendering or playable claim.'
used={s['fn'] for s in steps}
fixture={**f,'memory':'rigidbody-initialize-training-memory.bin','functions':{k:v for k,v in functions.items() if k in used},'globals':globals_,'cases':oracle.cases,'case_labels':['full training scene and all31 startup LevelObjects'],'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'pointer_globals':f['pointer_globals']+registry_pointer_globals,'native_callbacks':callbacks,'scope':scope}
for key in ['boundary_address','boundary_factory']:fixture.pop(key,None)
(folder/fixture['memory']).write_bytes(initial);(folder/'rigidbody-initialize-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
prior=json.loads((folder/'level-collision-load-original.json').read_text())
report={**prior,'result':'original pass; Wasm pending','cases':1,'calls':43,'completed_calls':43,'interrupted_calls':0,'completed_objects':31,'objects':objects,'asset_manager':oracle.word(0x6918dc),'asset_manager_refs':oracle.word(0x6918e0),'heap_events':oracle.word(CONTEXT+8),'heap_end':hex(oracle.word(CONTEXT)),'scope':scope,'instruction_coverage':{}}
report.pop('boundary',None);(folder/'rigidbody-initialize-training-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED full43 completedcalls',flush=True)
