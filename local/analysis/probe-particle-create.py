"""Particle constructors, materials and actual point-sprite manager creation."""
from pathlib import Path
import types,sys
module=types.ModuleType('script_heap_oracle');exec(compile(Path('local/analysis/particle-create-heap-oracle.py').read_text(),'<new explicit allocator port modes>','exec'),module.__dict__);sys.modules[module.__name__]=module
source=Path('local/analysis/probe-prop-lifecycle.py').read_text().split('# Constructor/reset fields')[0]
exec(compile(source,'<preserved component comparison services>','exec'))
from unicorn.x86_const import UC_X86_REG_EIP
functions.clear();coverage.clear();hits.clear();oracle.counts.clear();labels.clear()
specs=[(0x496d70,411,'particle_reset',0,'void',False,True),(0x496f10,60,'particle_base_construct',0,'word',False,True),
 (0x49b660,563,'particle_buffer_construct',8,'word',True,True),(0x4d9cf0,192,'particle_blend',1,'word',False,False),
 (0x4d9b80,324,'particle_material_construct',7,'word',True,True),(0x4c21a0,189,'particle_point_construct',5,'word',True,True),
 (0x497a70,56,'particle_emission',1,'void',False,True),(0x496ce0,42,'particle_color',1,'void',False,True),
 (0x49ac20,63,'particle_find',1,'word',False,True),(0x49ac60,254,'particle_manager_create',13,'word',True,True)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
bind(0x4bcef0,'thug_particle_factory_prefix_draft',11,'word',True,this=False)
exports += [[0x649428,'thug_particle_base_methods_draft'],[0x649424,'thug_particle_base_node_methods_draft'],
 [0x649504,'thug_particle_buffer_methods_draft'],[0x649500,'thug_particle_buffer_node_methods_draft'],
 [0x64a5ac,'thug_particle_point_methods_draft'],[0x64a5a8,'thug_particle_point_node_methods_draft']]
glob('thug_particle_allocation_mode_draft',0x658555,0,1)
PTLS=0x7d2100;oracle.cpu.mem_write(PTLS,bytes(0x100));oracle.setword(PTLS+0x64,LOCALE)
glob('thug_crt_random_state',PTLS+0x14,1)
def tls_port(cpu,at,size,user):
 sp=cpu.reg_read(UC_X86_REG_ESP);cpu.reg_write(UC_X86_REG_EAX,PTLS);cpu.reg_write(UC_X86_REG_EIP,oracle.word(sp));cpu.reg_write(UC_X86_REG_ESP,sp+4)
oracle.cpu.hook_add(UC_HOOK_CODE,tls_port,begin=0x629be5,end=0x629be5)
DICT=P+0x300;PM=P+0x400;LIST=PM+0x40
glob('thug_decal_texture_dictionary',0x700f20,DICT)
for i in range(18):glob('thug_mesh_shader_handles_draft',0x7ca920+i*4,0x12340000+i,offset=i*4)
put(DICT+12,'<I',0);put(PM+8,'<I',ALLOCATOR+0x300);put(PM+16,'<I',0);put(PM+20,'<I',LIST)
put(LIST,'<5I',0,0xffffffff,0,LIST,LIST);oracle.scope_entries[ALLOCATOR+0x300]=ALLOCATOR+0x300;oracle.scope_entries[ALLOCATOR+0x320]=ALLOCATOR+0x320
initial=bytes(memory);oracle.initial=initial
class ParticleGraph(PropGraph):
 def texture(self,shape):
  entry=self.alloc(0x30);self.put(entry+8,'<I',3 if shape=='indirect' else 2);self.put(entry+16,'<I',entry+24 if shape=='indirect' else 0x76543210);self.put(entry+24,'<I',0x76543210)
  table=0 if shape=='no-table' else self.table([] if shape=='missing' else [(0xe9d12353,entry)])
  self.put(DICT+12,'<I',table)
 def fill(self,value):self.image[P-BASE:P-BASE+0x138]=bytes([value])*0x138
def check(g,calls,label,changes=None):
 try:return case(calls,g.patches(),changes,label)
 except Exception:print('FAILED',label,flush=True);raise
for fill in [0,0xa5,0xff]:
 g=ParticleGraph();g.fill(fill);check(g,[call(0x496d70,P)]*2+[call(0x496f10,P)]*2,f'base-reset/{fill}')
for flags in [0,1,4,0x10,0x10000,0xffffffff]:
 for byte in [0,1,2,255,256,0xffffffff]:
  g=ParticleGraph();g.fill(0xa5);g.put(P+0x120,'<I',flags)
  check(g,[call(0x497a70,P,[byte])]*2,f'emission/{flags:x}/{byte:x}')
for enabled in [False,True]:
 for offset in [-4,0,4,8,16]:
  g=ParticleGraph();g.fill(0xa5);g.put(P+0x120,'<I',0x10000 if enabled else 0)
  g.put(P+0x5c,'<8I',0x7f812345,0xffc54321,0,0x80000000,1,2,3,4)
  check(g,[call(0x496ce0,P,[P+0x60+offset])],f'color-alias/{enabled}/{offset}')
blend_names=[0x02e58c18,0xa86285a1,0xa7fd7d23,0xdea7e576,0x0d7a749a,0x0eea99ff,0x54628ed7,0x18b98905,0x40f44b8a,0x90b93703,0x68e77f40,0xb8aa03c9,0x515e298e,0x806fff30]
for value in sorted({0,0xffffffff,*[n+d for n in blend_names for d in [-1,0,1]]}):
 g=ParticleGraph();check(g,[call(0x4d9cf0,args=[value])],f'blend/{value:x}')
for shape in ['no-table','missing','direct','indirect']:
 for blend in [0x02e58c18,0x68e77f40,0xb8aa03c9,0]:
  for alpha in [0,1,128,255,256,0x7fffffff,0x80000000,0xffffffff]:
   g=ParticleGraph();g.texture(shape);g.fill(0xa5)
   check(g,[call(0x4d9b80,P,[70,2,0xe9d12353,blend,alpha,0xabcdef12,0x87654321])],f'material/{shape}/{blend:x}/{alpha:x}')
for mode in [0,1,2,255]:
 for count in [0,1,2,70]:
  g=ParticleGraph();g.texture('direct');g.fill(0xa5)
  check(g,[call(0x49b660,P,[0x11223344,count,1,2,3,4,5,6]),call(0x4c21a0,P,[0x98765432,count,0xe9d12353,0x02e58c18,128])],f'buffers/{mode}/{count}',{0x658555:mode})
for alternate in [False,True]:
 for reuse in [0,1,256]:
  for inherit in [0,1,256,255]:
   g=ParticleGraph();g.texture('indirect');g.put(PM+16,'<I',ALLOCATOR+0x320 if alternate else 0)
   g.put(PM+24,'<4I',0x7f812345,0x80000000,0x3f000000,0xffc54321)
   args=[0x11223344,0xf4d8d486,70,2,0xe9d12353,0x02e58c18,128,8,0x3f000000,1,reuse,inherit,0]
   check(g,[call(0x49ac20,PM,[0x11223344]),call(0x49ac60,PM,args),call(0x49ac60,PM,args),call(0x49ac20,PM,[0x11223344]),call(0x49ac20,PM,[0x55667788])],f'manager/{alternate}/{reuse}/{inherit}')
g=ParticleGraph();g.put(PM+20,'<I',0);check(g,[call(0x49ac20,PM,[0])],'missing-list')
g=ParticleGraph();g.texture('direct');check(g,[call(0x4bcef0,args=[7,0xf4d8d486,70,2,0xe9d12353,0x02e58c18,128,8,0x3f000000,1,0])],'actual-point-factory')
missing={hex(i.address) for code in coverage.values() for i in code if not hits[i.address]};print('MISSING',sorted(missing),flush=True)
scope='Ten original particle reset/base/buffer/point/material/blend/emission/color/find/manager routines under valid linked objects, bounded nonnegative capacities and successful initialized allocations. Actual point-sprite branch of4bcef0 only; every other class explicitly traps and the factory is not counted complete. Original QB-independent constructors, reference targets, texture lookup/material initializer, CRT generator and list insertion execute. Mode-specific heap and CRT TLS are explicit host ports. Full arena/globals/heap compare; no drawing, effect script, full frame or playability claimed.'
# Fill only observed, individually justified exclusions after inspecting coverage.
excluded={**{hex(a):'successful allocation contract; failure branch retained but unverified' for a in [0x49acda,0x49acdc,0x49acde,0x49ace0,0x49ace1,0x49ace3,0x49ace4,0x49b6f5,0x49b75e,0x49b79c,0x49b7db,0x4c223e,0x4d9bfe]},**{hex(a):'initialized process allocator; cold bootstrap excluded' for a in [0x4c2204,0x4d9bca]}}
finish('particle-create',scope,excluded,extra)
