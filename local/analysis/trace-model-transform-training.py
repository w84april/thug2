"""Complete actual training collectible model configuration and component script."""
from pathlib import Path
source=Path('local/analysis/probe-training-prop-components.py').read_text().split('loads=')[0]
exec(compile(source,'<preserved real training component setup>','exec'))
from unicorn.x86_const import *
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
from specimen import load
pe=load()
SCRIPT,BOUNDARY,SYMBOL_AREA,DESCRIPTOR_AREA,PED,PEDNAME=BASE+0xc000,BASE+0xe000,BASE+0xa000,BASE+0xa800,BASE+0xc0000,BASE+0xef000
ped_path=ROOT/'local/game-files/Game/Data/scripts/game/ped.qb';ped=ped_path.read_bytes();assert len(ped)<PEDNAME-PED
memory[PED-BASE:PED-BASE+len(ped)]=ped;pn=b'scripts/game/ped.qb\0';memory[PEDNAME-BASE:PEDNAME-BASE+len(pn)]=pn
memory[SCRIPT-BASE:SCRIPT-BASE+244]=bytes(244);memory[BOUNDARY-BASE:BOUNDARY-BASE+576]=bytes(576)
state=json.loads((out/'script-state-fixtures.json').read_text())
for g in state['globals']:
 if g[1] not in index:glob(g[0],g[1],0,g[2],g[3] if len(g)>3 else 0)
for off in range(0,24,4):glob('thug_model_texture_table_draft',0x700f04+off,0,offset=off)
glob('thug_model_light_factor_count_draft',0x6faae0,0);glob('thug_model_directional_count_draft',0x6faae4,0)
glob('thug_script_cache',0x6f3558,CACHE);glob('thug_script_next_serial',0x6f3540,1)
functions['0x4738e0']={'name':'thug_script_initialize','this':True,'result':'word','cleanup':0,'stack_args':[]}
functions['0x474540']={'name':'thug_script_setup','this':True,'result':'void','cleanup':16,'memory':True,'stack_args':[0,1,2,3]}
functions['0x4750b0']={'name':'thug_script_execute','this':True,'result':'word','cleanup':0,'memory':True,'stack_args':[]}
# Actual native binding addresses and CRT-initialized member descriptors.
native=[('GotParam',0x44bd30,'thug_script_got_parameter_draft'),('ChecksumEquals',0x44a260,'thug_script_checksums_equal_draft'),('StringEquals',0x44a2c0,'thug_script_strings_equal_draft')]
metadata={r['name']:r for r in json.loads((folder/'script-bindings.json').read_text())}
for n,a,_ in native:assert int(metadata[n]['address'],16)==a
members=[(0x406998a5,0x45d810,'thug_composite_create_component_command_draft'),(0x2bffeaa3,0x45dbf0,'thug_composite_contains_command_draft')]
for i,(key,fn,export) in enumerate(members):
 d=DESCRIPTOR_AREA+i*24;put(d,'<6I',key,0x0ada4e74,fn,0,0,0);fields.add(d+8);function_exports.append([fn,export])
rows=[(crc(n.encode()),8,a) for n,a,_ in native]+[(key,9,DESCRIPTOR_AREA+i*24) for i,(key,*_) in enumerate(members)]
for i,(key,kind,value) in enumerate(rows):
 p=SYMBOL_AREA+i*20;bucket=BUCKETS+(key&4095)*4;previous=struct.unpack_from('<I',memory,bucket-BASE)[0]
 put(p,'<BBH4I',0x91,kind,0,key,0,value,previous);put(bucket,'<I',p)
 if kind==8:fields.add(p+12)
function_exports += [[a,e] for _,a,e in native]
exports += [[0x649348,'thug_model_renderer_base_methods_draft'],[0x64a4b4,'thug_model_renderer_methods_draft'],[0x646128,'thug_model_component_methods_draft']]
function_exports.append([0x421490,'thug_model_component_create_draft'])
for a in [0x494c40,0x4bad90,0x420bf0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
newtypes=[(0x286a8d26,0x421490),(0x222756d5,0x431f60),(0x7149b753,0x41a5b0),(0xa432dc41,0x41c920),(0x0f1641e3,0x433d90),(0x3618b878,0x4f3550)]
put(OBJECTS+0x44,'<I',4+len(newtypes))
for i,(kind,factory) in enumerate(newtypes,4):put(OBJECTS+0x48+8*i,'<2I',kind,factory);fields.add(OBJECTS+0x4c+8*i)
native_hits=Counter();factory_hit=[];active_model={}
configuration_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x20d10,1304),0x420d10));configuration_hits=Counter()
def configuration_trace(cpu,at,size,user):configuration_hits[at]+=1
oracle.cpu.hook_add(UC_HOOK_CODE,configuration_trace,begin=0x420d10,end=0x421227)
def observe(cpu,at,size,user):
 if at==0x420d10:
  active_model['component']=cpu.reg_read(UC_X86_REG_ECX);active_model['parameters']=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4)
 if at==0x421191:
  sp=cpu.reg_read(UC_X86_REG_ESP);values=[at,cpu.reg_read(UC_X86_REG_ESI),oracle.word(cpu.reg_read(UC_X86_REG_ESI)+0x208),1,active_model['parameters'],0]
  active_model['owner_flags']=oracle.word(oracle.word(values[1]+12)+0x104);assert not active_model['owner_flags']&0x20;native_hits[hex(at)]+=1
 elif at==0x4b54b0:
  active_model['render_geometry']=cpu.reg_read(UC_X86_REG_ECX);native_hits[hex(at)]+=1
 elif at==0x4d1030:
  active_model['instance']=cpu.reg_read(UC_X86_REG_ECX);native_hits[hex(at)]+=1
 elif at==0x4d5c30:
  active_model['mesh']=cpu.reg_read(UC_X86_REG_ECX);active_model['vertex_data']=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4);native_hits[hex(at)]+=1
 elif at==0x4c6650:
  active_model['sector']=cpu.reg_read(UC_X86_REG_ECX);active_model['sector_cursor']=oracle.word(oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4));native_hits[hex(at)]+=1
 elif at==0x4d5cc0:
  active_model['mesh_cursor']=oracle.word(oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4));native_hits[hex(at)]+=1
 elif at==0x4de300:
  active_model['scene_header']=cpu.reg_read(UC_X86_REG_ECX);native_hits[hex(at)]+=1
 elif at in [a for _,a in newtypes if a!=0x421490]:
  cpu.mem_write(BOUNDARY,struct.pack('<4I',at,oracle.word(SCRIPT+0x10),SCRIPT,1));factory_hit.append(at);cpu.emu_stop()
 else:native_hits[hex(at)]+=1
for a in [0x4b4760,0x48de90,0x4bae30,0x492f30,0x478f60,0x420350,0x4b2a20,0x4b4460,0x4b54b0,0x4d1030,0x492e50,0x48ddf0,0x49f3b0,0x4964a0,0x4076e0,0x407630,0x4b7eb0,0x409cb0,0x49c910,0x4c6270,0x4b5360,0x4b5e50,0x4b5e90,0x4b44d0,0x4dddf0,0x4dde20,0x4de3e0,0x4ddfa0,0x490a60,0x4b7b30,0x4b7ed0,0x4d3ce0,0x421191,0x4b52f0,0x4de340,0x4d0d30,0x49d4e0,0x4d5c30,0x4d3ff0,0x4d40e0,0x4d5760,0x4d3ed0,0x4da710,0x4d5900,0x4c6650,0x4d5cc0,0x4d4270,0x4de420,0x48c030,0x4b3ad0,0x4b3490,0x4de300,0x4d2cb0,0x4935e0,0x420d10,0x494ba0,0x487b00,0x492ee0,0x487a70,0x402080,0x4214f0,0x532eb0,0x492e90,0x420bf0,0x48bfa0,0x4b29c0,0x4bad90,0x494c40]+[a for _,a in newtypes]+[a for _,a,_ in native]+[0x45d810,0x45d850,0x45ee20,0x45f2a0]:oracle.cpu.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)
def prepared(cpu,at,size,user):
 value=cpu.reg_read(UC_X86_REG_EAX)
 if value in [a for _,a,_ in native]:fields.add(cpu.reg_read(UC_X86_REG_ESI)-4)
oracle.cpu.hook_add(UC_HOOK_CODE,prepared,begin=0x46ff81,end=0x46ff81)
def identity_script(cpu,at,size,user):fields.add(cpu.reg_read(UC_X86_REG_ECX)+0xec)
oracle.cpu.hook_add(UC_HOOK_CODE,identity_script,begin=0x4738e0,end=0x4738e0)
exec(compile(Path('local/analysis/asset-ready-training-ports-setup.py').read_text(),'<explicit texture platform ports>','exec'))
geometry_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4b3490-0x400000,567),0x4b3490));geometry_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:geometry_hits.update([at]),begin=0x4b3490,end=0x4b36c6)
exports += [[0x6499e0,'thug_model_scene_base_methods_draft'],[0x64a6b8,'thug_model_scene_pc_methods_draft'],
 [0x6499dc,'thug_model_scene_list_methods_draft'],[0x64a438,'thug_model_mesh_list_methods_draft'],
 [0x649a40,'thug_model_sector_base_methods_draft'],[0x64a718,'thug_model_sector_pc_methods_draft'],
 [0x64a368,'thug_model_geometry_lights_methods_draft'],[0x64a434,'thug_model_mesh_node_methods_draft'],[0x6492e4,'thug_model_object_base_methods_draft'],[0x64a490,'thug_model_object_pc_methods_draft']]
put(MANAGER+0x110,'<I',MANAGER+0x700);oracle.scope_entries[MANAGER+0x700]=2
CRTCTX,CRTBEGIN,CRTLIMIT,CRTLOG=BASE+0xf6000,BASE+0x1900000,BASE+0x1b00000,BASE+0xf8500
INDEXCTL,INDEXLOG,INDEXVT,INDEXDEV=BASE+0xf6100,BASE+0xf6200,BASE+0xf8400,BASE+0x1b00000
exec(compile((folder/'vertex-upload-ports-setup.py').read_text(),'<separate CRT and index GPU providers>','exec'))
glob('thug_model_render_instances_draft',0x7825c0,0)
glob('thug_mesh_index_registry',0x7865e8,0)
glob('thug_mesh_vertex_registry',0x7865e4,0)
for i in range(6):
 at=0x7865cc+i*4;glob('thug_model_render_cache_draft',at,int.from_bytes(pe.get_data(at-0x400000,4),'little'),offset=i*4)
glob('thug_mesh_shader_conversion_enabled_draft',0x786ab8,0,width=1)
for i in range(18):
 at=0x7ca920+i*4;glob('thug_mesh_shader_handles_draft',at,int.from_bytes(pe.get_data(at-0x400000,4),'little'),offset=i*4)
for i in range(6):
 at=0x775b64+i*4;glob('thug_mesh_vertex_formats_draft',at,int.from_bytes(pe.get_data(at-0x400000,4),'little'),offset=i*4)
mesh_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4d5cc0-0x400000,1054),0x4d5cc0));mesh_hits=Counter()
sector_code=list(Cs(CS_ARCH_X86,CS_MODE_32).disasm(pe.get_data(0x4c6650-0x400000,1216),0x4c6650));sector_hits=Counter()
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:mesh_hits.update([at]),begin=0x4d5cc0,end=0x4d60dd)
oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:sector_hits.update([at]),begin=0x4c6650,end=0x4c6b0f)
initial=bytes(memory);oracle.initial=initial
ped_asset={'member':'scripts/game/ped.qb','address':PED,'filename':PEDNAME,'size':len(ped),'sha256':hashlib.sha256(ped).hexdigest()}
loads=[(0x472420,0,[a['filename'],a['address'],0,1,0]) for a in [*extra_assets,ped_asset,asset]]
prefix=loads+[(0x45d370,TABLE,[]),(0x45d520,TABLE,[crc(b'TR_NodeArray'),1]),(0x479070,0,[0x735a20ba,0])]
# Each case restarts from the same untouched files and explicit service state.
functions['0x468cb0']={'name':'thug_gameobject_create_draft','this':False,'result':'word','cleanup':0,'stack_args':[0,1],'diagnostics':True,'memory':True}
track=[0x45db30,0x4204b0,0x420480,0x4219f0,0x4215f0,0x493090,0x48de60,0x4b4630,0x48df30,0x4b47b0,0x41f500,0x41aad0,0x475790,0x461350]
trace=Counter()
for a in track:oracle.cpu.hook_add(UC_HOOK_CODE,lambda cpu,at,size,user:trace.update([hex(at)]),begin=a,end=a)
steps=oracle.case(prefix);nodes=oracle.word(TABLE+0x1000c);items=oracle.word(nodes+8)
selected=[(i,oracle.word(items+i*4)) for i in [204,1289]]
for ni,node in selected:
 trace.clear();native_hits.clear();factory_hit.clear();oracle.cases.clear()
 steps=oracle.case(prefix+[(0x468cb0,0,[node,1,0])]);obj=steps[-1]['result']
 chain=[];component=oracle.word(obj+0x100)
 while component:
  chain.append([hex(component),hex(oracle.word(component+4))]);component=oracle.word(component+16)
 print('FULL CREATE',ni,hex(obj),'flags',hex(oracle.word(obj+0x104)),'components',chain,'calls',dict(trace),flush=True)
 if ni==1289:
  component=active_model['component'];renderer=oracle.word(component+0x208);instance=active_model['instance'];geometry=active_model['render_geometry']
  print('MODEL',hex(component),'renderer',hex(renderer),'instance',hex(instance),'matrix',list(struct.unpack('<16I',oracle.cpu.mem_read(instance+4,64))),'position',list(struct.unpack('<4I',oracle.cpu.mem_read(obj+0x4c,16))),'flags',oracle.cpu.mem_read(renderer+0x44,1).hex(),'enabled',oracle.cpu.mem_read(instance+0x4c,1).hex(),flush=True)
