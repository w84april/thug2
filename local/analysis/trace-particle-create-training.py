"""Actual training barrel script to the explicit particle-engine initializer boundary."""
from pathlib import Path
source=Path('local/analysis/particle-create-training-setup.py').read_text().split('frame_hits=Counter()')[0]
import ast
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['write_text','write_bytes','unlink'] for n in ast.walk(ast.parse(source)))
exec(compile(source,'<preserved full scene and archived particle setup>','exec'))
from unicorn.x86_const import *
BASELINE=json.loads((folder/'rigidbody-initialize-training-fixtures.json').read_text())
functions['0x45d920']={'name':'thug_object_update_components','this':True,'result':'void','cleanup':0,'stack_args':[],'memory':True}
calls[-1]=(calls[-1][0],calls[-1][1],[0,0])
BOUNDARY=0x5f31000;memory[BOUNDARY-BASE:BOUNDARY-BASE+16]=bytes(16)
glob('thug_particle_create_boundary_draft',0x35c,BOUNDARY)
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
function_exports += [[0x460940,'thug_object_get_id_entry_draft'],[0x4619d0,'thug_object_manager_set_priority'],[0x41ff20,'thug_lockobj_create_draft'],[0x41e1e0,'thug_flexparticle_create_versioned_draft']]
fields.update([GETID+8,object_methods+0x10,OBJECTS+0x4c+component_count*8,OBJECTS+0x4c+(component_count+1)*8])
exports += [[0x6460e4,'thug_lockobj_methods_draft'],[0x645fe4,'thug_flexparticle_create_methods_draft']]
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
 receiver=cpu.reg_read(UC_X86_REG_ECX);params=oracle.word(cpu.reg_read(UC_X86_REG_ESP)+12)
 cpu.mem_write(BOUNDARY,struct.pack('<4I',at,params,receiver,1));boundary_hits.append(at);cpu.emu_stop()
cpu.hook_add(UC_HOOK_CODE,stop_particle,begin=0x4d9b80,end=0x4d9b80)
# Initialize the same manager used by the real FlexParticle initializer.
engine_fixture=json.loads((folder/'particle-engine-fixtures.json').read_text())
engine_ids={0x658a5c,0x65845c,0x658480,0x658458,0x65848c,0x6494b0,0x6494c4,0x6494c8}
exports.extend(e for e in engine_fixture['pointer_exports'] if e[0] in engine_ids)
glob('thug_allocator_registry_draft',0x7d1800,oracle.manager)
glob('thug_particle_time_scale_draft',0x700ef4,0xdeadbeef)
put(oracle.manager+0xc0,'<I',0)
functions['0x49af20']={'name':'thug_particle_manager_construct_draft','this':True,'result':'word','cleanup':0,'memory':True}
calls.insert(-1,(0x49af20,CUTSCENE,[]))
initial=bytes(memory);oracle.initial=initial
print('Original43prop startup, particle script/settings, real point-sprite buffers, texture lookup boundary',flush=True)
steps=oracle.case(calls[:-1]);assert len(steps)==46 and not boundary_hits
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
assert boundary_hits==[0x4d9b80] and cpu.reg_read(UC_X86_REG_EIP)==0x4d9b80
assert len(initializer_args)==len(point_entries)==1
component=initializer_args[0][0];owner=oracle.word(component+12);chain=[];c=oracle.word(owner+0x100)
while c:
 assert len(chain)<16;chain.append({'address':c,'type':hex(oracle.word(c+4))});c=oracle.word(c+16)
assert [c['type'] for c in chain]==['0x5cb5cb7e','0xc5bceb9e'] and chain[-1]['address']==component
assert oracle.word(component)==0x645fe4 and oracle.word(component+0x18)==0
params=initializer_args[0][1];param_rows=[];item=oracle.word(params+4)
while item:
 assert len(param_rows)<200;param_rows.append({'name':hex(oracle.word(item+4)),'type':cpu.mem_read(item,1)[0]>>1,'value':hex(oracle.word(item+8))});item=oracle.word(item+12)
effect=point_entries[0];assert oracle.word(effect)==0x64a5ac and oracle.word(effect+12)==0x64a5a8
assert oracle.word(effect+0x7c)==70 and oracle.word(effect+0x120)&4 and oracle.word(effect+0xf0)==component
assert oracle.word(component+0x24)==component and oracle.word(CONTEXT+28)==manager_heap
assert oracle.word(BOUNDARY+4)==0xe9d12353
sp=cpu.reg_read(UC_X86_REG_ESP);material_args=[oracle.word(sp+4+i*4) for i in range(7)]
assert material_args==[70,2,0xe9d12353,0x02e58c18,0,0,0]
effect_state={'address':effect,'class':'point-sprite','capacity':70,'records':oracle.word(effect+0xf8),'positions':oracle.word(effect+0x11c),'color_buffers':[oracle.word(effect+o) for o in [0x10c,0x110,0x114]],'flags':hex(oracle.word(effect+0x120)),'material_wrapper':oracle.word(BOUNDARY+8),'material_arguments':material_args,'active_heap':manager_heap}
after=bytes(cpu.mem_read(BASE,SIZE));outputs=[]
for page in range(0,SIZE,4096):
 if before[page:page+4096]!=after[page:page+4096]:
  for i in range(page,min(page+4096,SIZE),4):
   if before[i:i+4]!=after[i:i+4]:outputs.append([BASE+i,after[i:i+4].hex()])
steps.append({'fn':hex(fn),'this':this,'args':args,'result':None,'outputs':outputs,'globals':[oracle.global_read(g) for g in globals_],'callbacks':0,'expected_trap':True})
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
scope='Actual complete31prop training startup, archived particle QB and TR particle data, original manager and barrel-fire update. The partial FlexParticle initializer parses real parameters and reaches the selected point-sprite factory and constructors, allocating all capacity70 buffers with original allocation mode0. Explicit stop before material constructor4d9b80 and shared texture dictionary lookup; no dictionary, texture, material or successful effect is fabricated. Whole arena, globals, heap, I/O/GPU comparison storage and active component services compare. No complete frame or playable game.'
fixture={**BASELINE,'memory':'particle-create-training-memory.bin','functions':{k:v for k,v in functions.items() if k in {s['fn'] for s in steps}},'globals':globals_,'cases':oracle.cases,'case_labels':['actual barrel-fire first update to particle-engine initialization'],'pointer_exports':exports,'function_exports':function_exports,'pointer_fields':sorted(fields),'boundary_address':BOUNDARY,'boundary_factory':0x4d9b80,'component_initializer_boundary':True,'scope':scope}
(folder/fixture['memory']).write_bytes(initial);(folder/'particle-create-training-fixtures.json').write_text(json.dumps(fixture,separators=(',',':')))
report={'result':'original pass; Wasm pending','specimen_sha256':SHA256,'cases':1,'calls':len(steps),'completed_calls':46,'interrupted_calls':1,'completed_startup_objects':31,'barrel':this,'particle_manager':manager_state,'particle_object':owner,'particle_component':component,'components':chain,'initializer_parameters':param_rows,'boundary':'0x4d9b80','effect':effect_state,'heap_events':oracle.word(CONTEXT+8),'heap_end':hex(oracle.word(CONTEXT)),'scope':scope,'playable':False}
(folder/'particle-create-training-original.json').write_text(json.dumps(report,indent=2)+'\n');print('SAVED',report['completed_calls'],'complete,1interrupted,components',chain,flush=True)
