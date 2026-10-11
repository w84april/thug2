"""Actual complete training barrel update and active particle attachment."""
from pathlib import Path
source=Path('local/analysis/particle-image-training-setup.py').read_text().split('frame_hits=Counter()')[0]
import ast
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_text','write_bytes','unlink'] for n in ast.walk(ast.parse(source)))
exec(compile(source,'<preserved full scene and archived particle setup>','exec'))
from unicorn.x86_const import *
BASELINE=json.loads((folder/'rigidbody-initialize-training-fixtures.json').read_text())
functions['0x45d920']={'name':'thug_object_update_components','this':True,'result':'void','cleanup':0,'stack_args':[],'memory':True}
calls[-1]=(calls[-1][0],calls[-1][1],[0,0])
BOUNDARY=0x5f31000;memory[BOUNDARY-BASE:BOUNDARY-BASE+16]=bytes(16)
glob('thug_particle_image_boundary_draft',0x360,BOUNDARY)
for name,a,v in [('thug_frame_counter',0x7d1ec8,60),('thug_frame_rate',0x684fd0,0x42700000)]:
 if a in index:defaults[index[a]]=v
 else:glob(name,a,v)
for i,v in enumerate([0x12345678,0x98765432,0x31415926]):
 a=0x690fd4+4*i
 if a in index:defaults[index[a]]=v
 else:glob('thug_random_state',a,v,offset=4*i)
entry_names=['thug_script_global_exists_draft','thug_script_mangle_checksums_entry_draft','thug_script_object_exists_draft','thug_script_cutscene_destroy_list_active_draft','thug_script_structure_contains_draft','thug_script_create_composite_entry_draft']
for i,name in enumerate(entry_names):
 address=int.from_bytes(memory[NSLOTS+i*20+12-BASE:NSLOTS+i*20+16-BASE],'little');function_exports.append([address,name]);fields.add(NSLOTS+i*20+12)
function_exports += [[0x460940,'thug_object_get_id_entry_draft'],[0x4619d0,'thug_object_manager_set_priority'],[0x41ff20,'thug_lockobj_create_draft'],[0x41e1e0,'thug_flexparticle_setup_versioned_draft']]
fields.update([GETID+8,object_methods+0x10,OBJECTS+0x4c+component_count*8,OBJECTS+0x4c+(component_count+1)*8])
exports += [[0x6460e4,'thug_lockobj_methods_draft'],[0x645fe4,'thug_flexparticle_setup_methods_draft']]
for at in [0x41f500,0x41da00]:cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
# The original native parser embeds relocated callback identities in script code.
native_addresses={a for a,_ in function_exports}
def prepared_particle(cpu,at,size,user):
 if cpu.reg_read(UC_X86_REG_EAX) in native_addresses:fields.add(cpu.reg_read(UC_X86_REG_ESI)-4)
cpu.hook_add(UC_HOOK_CODE,prepared_particle,begin=0x46ff81,end=0x46ff81)
boundary_hits=[];initializer_args=[];point_entries=[]
def initializer(cpu,at,size,user):initializer_args.append((cpu.reg_read(UC_X86_REG_ECX),oracle.word(cpu.reg_read(UC_X86_REG_ESP)+4)))
cpu.hook_add(UC_HOOK_CODE,initializer,begin=0x41db00,end=0x41db00)
def point(cpu,at,size,user):point_entries.append(cpu.reg_read(UC_X86_REG_ECX))
cpu.hook_add(UC_HOOK_CODE,point,begin=0x4c21a0,end=0x4c21a0)
def register_heap(cpu,at,size,user):
 heap=cpu.reg_read(UC_X86_REG_ECX);oracle.scope_entries[heap]=heap
cpu.hook_add(UC_HOOK_CODE,register_heap,begin=0x5ba520,end=0x5ba520)
unit=json.loads((folder/'particle-create-fixtures.json').read_text())
exports.extend(e for e in unit['pointer_exports'] if e[0] in {0x649428,0x649424,0x649504,0x649500,0x64a5ac,0x64a5a8})
glob('thug_particle_allocation_mode_draft',0x658555,0,1)
def stop_particle(cpu,at,size,user):
 receiver,params=initializer_args[-1]
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,receiver,1));boundary_hits.append(at);cpu.emu_stop()
glob('thug_particle_parameter_scale_draft',0x67d6d0,0xdeadbeef)
glob('thug_particle_setup_motion_boundary_draft',0x364,0)
glob('thug_motion_frame_boundary_draft',0x368,0)
glob('thug_proximity_frame_boundary_draft',0x36c,0)
glob('thug_lock_frame_boundary_draft',0x370,BOUNDARY)
def stop_motion(cpu,at,size,user):
 receiver=cpu.reg_read(UC_X86_REG_ECX);cpu.mem_write(BOUNDARY,struct.pack('<4I',at,receiver,oracle.word(receiver+12),1));boundary_hits.append(at);cpu.emu_stop()
cpu.hook_add(UC_HOOK_CODE,stop_motion,begin=0x430e20,end=0x430e20)
command_stop=cpu.hook_add(UC_HOOK_CODE,stop_motion,begin=0x497b00,end=0x497b00)
lock_entries=[];lock_returns=[]
def lock_entry(cpu,at,size,user):lock_entries.append(cpu.reg_read(UC_X86_REG_ECX))
def lock_return(cpu,at,size,user):lock_returns.append(at)
cpu.hook_add(UC_HOOK_CODE,lock_entry,begin=0x41ff90,end=0x41ff90)
cpu.hook_add(UC_HOOK_CODE,lock_return,begin=0x41ff9e,end=0x41ff9e)
cpu.hook_add(UC_HOOK_CODE,lock_return,begin=0x41ff14,end=0x41ff14)
motion_entries=[];motion_returns=[]
def motion_entry(cpu,at,size,user):motion_entries.append(cpu.reg_read(UC_X86_REG_ECX))
def motion_return(cpu,at,size,user):motion_returns.append(at)
cpu.hook_add(UC_HOOK_CODE,motion_entry,begin=0x4270e0,end=0x4270e0)
cpu.hook_add(UC_HOOK_CODE,motion_return,begin=0x4272c3,end=0x4272c3)
proximity_entries=[];proximity_returns=[]
def proximity_entry(cpu,at,size,user):proximity_entries.append(cpu.reg_read(UC_X86_REG_ECX))
def proximity_return(cpu,at,size,user):proximity_returns.append(at)
cpu.hook_add(UC_HOOK_CODE,proximity_entry,begin=0x4ec560,end=0x4ec560)
cpu.hook_add(UC_HOOK_CODE,proximity_return,begin=0x4ec95f,end=0x4ec95f)
# Initialize the same manager used by the real FlexParticle initializer.
engine_fixture=json.loads((folder/'particle-engine-fixtures.json').read_text())
engine_ids={0x658a5c,0x65845c,0x658480,0x658458,0x65848c,0x6494b0,0x6494c4,0x6494c8}
exports.extend(e for e in engine_fixture['pointer_exports'] if e[0] in engine_ids)
glob('thug_allocator_registry_draft',0x7d1800,oracle.manager)
glob('thug_particle_time_scale_draft',0x700ef4,0xdeadbeef)
put(oracle.manager+0xc0,'<I',0)
functions['0x49af20']={'name':'thug_particle_manager_construct_draft','this':True,'result':'word','cleanup':0,'memory':True}
calls.insert(-1,(0x49af20,CUTSCENE,[]))
# Real level texture-loading script plus the real static particle dictionary.
FLAMEDATA,FLAMEFILE,FLAMENAME=0x5f40000,0x5f41000,0x5f41100
flame_path=ROOT/'local/game-files/Game/Data/images/particles/apm_flameQUAD_01.img.xbx';flame_bytes=flame_path.read_bytes()
assert hashlib.sha256(flame_bytes).hexdigest()=='95fc1e0fadf8bde5012ad18fabd8056953a858a8a9afee65662523003b36f2bf'
flame_filename=b'images/particles\\apm_flamequad_01.img.xbx\0'
memory[FLAMEDATA-BASE:FLAMEDATA-BASE+len(flame_bytes)]=flame_bytes;memory[FLAMENAME-BASE:FLAMENAME-BASE+len(flame_filename)]=flame_filename
put(FLAMEFILE,'<2I',FLAMEDATA,FLAMEDATA+len(flame_bytes))
glob('thug_decal_texture_dictionary',0x700f20,0)
PTLS=0x7d2100;cpu.mem_write(PTLS,bytes(0x100));glob('thug_crt_random_state',PTLS+0x14,1)
def random_tls(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);ret=oracle.word(sp)
 if 0x623ba3<=ret<0x623bc4:
  cpu.reg_write(UC_X86_REG_EAX,PTLS);cpu.reg_write(UC_X86_REG_EIP,ret);cpu.reg_write(UC_X86_REG_ESP,sp+4)
cpu.hook_add(UC_HOOK_CODE,random_tls,begin=0x629be5,end=0x629be5)
key=crc(b'LoadParticleTexture');slot=NSLOTS+8*20;bucket=BUCKETS+(key&4095)*4
put(slot,'<BBH4I',0,8,0,key,0,0x5aa7b0,int.from_bytes(memory[bucket-BASE:bucket-BASE+4],'little'));put(bucket,'<I',slot)
function_exports.append([0x5aa7b0,'thug_script_load_particle_texture_entry_draft']);fields.add(slot+12);native_addresses.add(0x5aa7b0)
functions['0x640c60']={'name':'thug_particle_dictionary_initialize_draft','this':False,'result':'void','cleanup':0,'memory':True}
functions['0x475790']={'name':'thug_script_run_sync','this':False,'result':'void','cleanup':0,'memory':True,'diagnostics':True,'stack_args':[0,1,2,3]}
load_texture_key=crc(b'load_level_particle_textures');calls[-1:-1]=[(0x640c60,0,[]),(0x475790,0,[load_texture_key,0,0,0,0])]
for at in [0x49f200,0x4c8070]:cpu.hook_add(UC_HOOK_CODE,identities,begin=at,end=at)
# Register after the preserved startup calls, whose object addresses are fixed by their recorded allocation order. Registration precedes effect creation and setup-script lookup.
functions['0x642fe0']={'name':'original_particle_descriptor_initializer','this':False,'result':'void','cleanup':0}
functions['0x41d6e0']={'name':'original_particle_descriptor_register','this':False,'result':'void','cleanup':0,'memory':True}
calls[-1:-1]=[(0x642fe0,0,[]),(0x41d6e0,0,[])]
initial=bytes(memory);oracle.initial=initial
print('Original training startup, flame image and full particle initializer',flush=True)
steps=oracle.case(calls[:-1]);assert len(steps)==50 and not boundary_hits
manager_gap=oracle.word(CUTSCENE+4);manager_heap=oracle.word(CUTSCENE+8);manager_list=oracle.word(CUTSCENE+20)
assert oracle.word(CUTSCENE)==0x6494b0 and oracle.word(manager_gap)==0x658a5c
assert oracle.word(manager_heap)==0x65848c and oracle.word(manager_heap+0x24)==manager_gap
assert oracle.word(manager_gap+0x10)==manager_heap and oracle.word(oracle.manager+0xc0)==1 and oracle.word(oracle.manager)==manager_heap
assert oracle.word(manager_list)==0x6494c4 and oracle.word(manager_list+4)==0xffffffff
assert oracle.word(manager_list+12)==manager_list==oracle.word(manager_list+16)
manager_state={'address':CUTSCENE,'gap':manager_gap,'heap':manager_heap,'list':manager_list,'raw_bytes':oracle.word(manager_gap+8),'time_scale_bits':hex(oracle.word(0x700ef4))}
before=bytes(cpu.mem_read(BASE,SIZE));fn,this,args=calls[-1];sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,this);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
cpu.emu_start(fn,oracle.stop,count=oracle.instruction_limit)
print('BARREL FRAME',list(map(hex,boundary_hits)),hex(cpu.reg_read(UC_X86_REG_EIP)),flush=True)
assert boundary_hits in [[],[0x430e20]] and cpu.reg_read(UC_X86_REG_EIP)==(0x430e20 if boundary_hits else oracle.stop),(boundary_hits,hex(cpu.reg_read(UC_X86_REG_EIP)))
barrel_interrupted=bool(boundary_hits)
assert not barrel_interrupted
assert len(initializer_args)==len(point_entries)==len(motion_entries)==len(motion_returns)==len(proximity_entries)==len(proximity_returns)==1
assert oracle.word(motion_entries[0]+12)==this
component=initializer_args[0][0];owner=oracle.word(component+12);chain=[];c=oracle.word(owner+0x100)
while c:
 assert len(chain)<16;chain.append({'address':c,'type':hex(oracle.word(c+4))});c=oracle.word(c+16)
assert [c['type'] for c in chain]==['0x5cb5cb7e','0xc5bceb9e'] and chain[-1]['address']==component
assert oracle.word(component)==0x645fe4 and oracle.word(component+0x18)==point_entries[0]
params=initializer_args[0][1];param_rows=[];item=oracle.word(params+4)
while item:
 assert len(param_rows)<200;param_rows.append({'name':hex(oracle.word(item+4)),'type':cpu.mem_read(item,1)[0]>>1,'value':hex(oracle.word(item+8))});item=oracle.word(item+12)
effect=point_entries[0];assert oracle.word(effect)==0x64a5ac and oracle.word(effect+12)==0x64a5a8
assert oracle.word(effect+0x7c)==70 and oracle.word(effect+0x120)&4 and oracle.word(effect+0xf0)==component
assert oracle.word(component+0x24)==component and oracle.word(CONTEXT+28)==0
assert oracle.word(BOUNDARY)==(0x430e20 if barrel_interrupted else 0)
assert len(lock_entries)==len(lock_returns)==1
wrapper=oracle.word(effect+0x134);material=oracle.word(wrapper);resource=oracle.word(material+0x30);texture=oracle.word(resource+16);pixels=oracle.word(texture+16)
assert oracle.word(material+0x20)==0x44
assert oracle.word(manager_list+12)==effect+12 and oracle.word(manager_list+16)==effect+12
assert oracle.word(effect+4)==component+0x18
setup_script=oracle.word(effect+0xfc);assert setup_script and not oracle.word(effect+0x100)
assert oracle.word(setup_script+0xbc)==owner and oracle.word(effect+0x104)
assert oracle.word(setup_script+0xc8)==0xcd1e6836,(hex(setup_script),hex(oracle.word(setup_script+0xc8)),hex(oracle.word(setup_script+0xcc)))
script_state={'setup':setup_script,'update':oracle.word(effect+0x100),'parameters':oracle.word(effect+0x104),'instruction':oracle.word(setup_script+0xc),'name':'0xcd1e6836','owner':owner}
rgba_sha=hashlib.sha256(bytes(cpu.mem_read(pixels,4096))).hexdigest()
unit_image=json.loads((folder/'particle-image-original.json').read_text());assert rgba_sha==unit_image['assets'][0]['rgba_sha256']
effect_state={'address':effect,'class':'point-sprite','capacity':70,'records':oracle.word(effect+0xf8),'positions':oracle.word(effect+0x11c),'color_buffers':[oracle.word(effect+o) for o in [0x10c,0x110,0x114]],'flags':hex(oracle.word(effect+0x120)),'material_wrapper':wrapper,'material':material,'texture_resource':resource,'texture':texture,'rgba_sha256':rgba_sha,'reference':oracle.word(component+0x18),'manager_listed':True}

after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
for page in range(0,SIZE,4096):
 if before[page:page+4096]!=after[page:page+4096]:
  for i in range(page,min(page+4096,SIZE),4):
   if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
steps.append({'fn':hex(fn),'this':this,'args':args,'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':barrel_interrupted})
steps[-1]['boundary_factory']=0x430e20
barrel_rigidbody=oracle.word(BOUNDARY+4)
# Exercise the actual active LockObj on the new particle owner, then stop at
# its unrecovered FlexParticle update. This is a second partial object update.
before=bytes(cpu.mem_read(BASE,SIZE));sp=oracle.stack+0x18000
cpu.mem_write(sp,struct.pack('<I',oracle.stop));cpu.reg_write(UC_X86_REG_ESP,sp);cpu.reg_write(UC_X86_REG_ECX,owner);cpu.reg_write(UC_X86_REG_FPCW,0x7f)
from collections import deque
recent=deque(maxlen=48)
def recent_code(cpu,at,size,user):recent.append(at)
cpu.hook_add(UC_HOOK_CODE,recent_code,begin=0x400000,end=0x680000)
try:cpu.emu_start(0x45d920,oracle.stop,count=oracle.instruction_limit)
except Exception as error:
 sp=cpu.reg_read(UC_X86_REG_ESP)
 report={'error':str(error),'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'recent':list(map(hex,recent)),'stack':[hex(oracle.word(sp+i)) for i in range(0,32,4)]}
 (folder/'particle-frame-discovery-error.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True);raise

assert boundary_hits==([0x430e20] if barrel_interrupted else [])+[0x497b00] and cpu.reg_read(UC_X86_REG_EIP)==0x497b00,(boundary_hits,hex(cpu.reg_read(UC_X86_REG_EIP)))
assert len(lock_entries)==len(lock_returns)==2 and oracle.word(lock_entries[1]+12)==owner
assert oracle.word(lock_entries[1]+0x8c)&4 and oracle.word(lock_entries[1]+0x1c)==oracle.word(this+0x14)
after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
for page in range(0,SIZE,4096):
 if before[page:page+4096]!=after[page:page+4096]:
  for i in range(page,min(page+4096,SIZE),4):
   if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
steps.append({'fn':'0x45d920','this':owner,'args':[0,0],'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True,'boundary_factory':0x41df80})
attachment_state={'barrel_lock':lock_entries[0],'particle_lock':lock_entries[1],'entry_count':len(lock_entries),'return_count':len(lock_returns),'particle_position':list(struct.unpack('<4f',cpu.mem_read(owner+0x4c,16))),'barrel_position':list(struct.unpack('<4f',cpu.mem_read(this+0x4c,16))),'particle_matrix':cpu.mem_read(owner+0xc0,64).hex(),'particle_velocity':cpu.mem_read(owner+0xac,16).hex()}
# Preserve the prior whole-scene comparison convention and all live identities.
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

sp=cpu.reg_read(UC_X86_REG_ESP)
result={'boundary':hex(cpu.reg_read(UC_X86_REG_EIP)),'receiver':cpu.reg_read(UC_X86_REG_ECX),'stack':[hex(oracle.word(sp+i)) for i in range(0,20,4)],'effect':effect_state,'scope':'Original-only discovery: preserved training startup, then real642fe0 descriptor initialization and41d6e0 registration, then barrel update and active particle update. Stops at497b00 particle command dispatcher. No C/Wasm or completed particle-frame claim','registered_table':cpu.mem_read(0x683ac0,26*24).hex()}
(folder/'particle-frame-discovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

# Continue the same original frame after recording the exact first command.
# This is exploration only, not a recovered C implementation or browser claim.
cpu.hook_del(command_stop)
try:
 cpu.emu_start(0x497b00,oracle.stop,count=oracle.instruction_limit)
 completion={'result':'returned' if cpu.reg_read(UC_X86_REG_EIP)==oracle.stop else 'stopped','eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'stack_pointer':hex(cpu.reg_read(UC_X86_REG_ESP)),'effect':effect,'particle_count':oracle.word(effect+0x8c),'setup_script':oracle.word(effect+0xfc),'rate_bits':hex(oracle.word(effect+0x70)),'effect_bytes':cpu.mem_read(effect,0x138).hex(),'component_bytes':cpu.mem_read(component,0x3c).hex(),'scope':'Original-only continuation through one actual particle-owner update; no C/Wasm or game playability claim.'}
except Exception as error:
 sp=cpu.reg_read(UC_X86_REG_ESP)
 completion={'result':'failed','error':str(error),'eip':hex(cpu.reg_read(UC_X86_REG_EIP)),'recent':list(map(hex,recent)),'stack':[hex(oracle.word(sp+i)) for i in range(0,32,4)]}
(folder/'particle-frame-continuation.json').write_text(json.dumps(completion,indent=2)+'\n');print(json.dumps(completion),flush=True)
