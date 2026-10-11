"""Original lighting ownership and renderer binding dependencies."""
from pathlib import Path
source=Path('local/analysis/probe-model-component.py').read_text().split('for ctor,size')[0]
exec(compile(source,'<preserved model-construction setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
specs=[(0x532eb0,4,'model_renderer_lights',0,'word',False,True),
 (0x492e90,22,'model_renderer_flag32',1,'void',False,True),(0x48e4d0,12,'model_light_position',1,'byte',False,True),
 (0x48df20,5,'model_geometry_set_lights',1,'void',False,True),(0x492dd0,59,'model_renderer_bind_skeleton',1,'byte',False,True),
 (0x4b61f0,29,'model_light_ambient',1,'void',False,True),(0x4b6210,42,'model_light_directional',2,'void',False,True),
 (0x48de30,5,'model_light_set_ambient',1,'void',False,True),(0x48e4c0,5,'model_light_set_directional',2,'void',False,True),
 (0x48e5b0,113,'model_light_base_construct',0,'word',True,True),(0x48e630,37,'model_light_base_destroy',0,'void',True,True),
 (0x4b6270,237,'model_light_construct',0,'word',True,True),(0x4b6360,69,'model_light_destroy',0,'void',True,True),
 (0x4b67b0,33,'model_light_delete',1,'word',True,True),(0x4b6b10,107,'model_light_create',0,'word',True,False),
 (0x48ea80,5,'model_light_factory',0,'word',True,False),(0x4b6920,17,'model_virtual_delete',1,'byte',True,False),
 (0x48c080,5,'model_light_release',1,'byte',True,False),(0x493bd0,59,'model_renderer_create_lights',0,'byte',True,True),
 (0x493c10,71,'model_renderer_remove_lights',0,'byte',True,True)]
for a,n,name,argc,result,heap,this in specs:bind_new(a,n,'thug_'+name+'_draft',argc,result,heap,this=this)
exports += [[0x6491dc,'thug_model_light_base_methods_draft'],[0x64a440,'thug_model_light_methods_draft'],[0x64a368,'thug_model_geometry_lights_methods_draft']]
for a in [0x48e5b0,0x4b6270]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
for name,a in [('thug_model_light_factor_count_draft',0x6faae0),('thug_model_directional_count_draft',0x6faae4)]:global_default(name,a,0)
for a,name in [(0x494c40,'model_renderer_base_construct'),(0x4bad90,'model_renderer_construct')]:bind(a,'thug_'+name+'_draft',0,'word',True)
class LightGraph(PropGraph):
 def __init__(self):
  super().__init__();self.put(P,'<I',0x64a440);fields.add(P)
 def geometry(self):
  g=self.alloc(0x64);self.put(g,'<I',0x64a368);fields.add(g);return g
 def parts(self,count):
  if count is None:self.put(P+0x10,'<I',0);return
  head=self.alloc(12);nodes=[self.alloc(12) for _ in range(count)];self.put(P+0x10,'<I',head)
  self.put(head,'<3I',0,nodes[0] if nodes else head,nodes[-1] if nodes else head)
  for i,node in enumerate(nodes):
   part=self.alloc(24);self.put(part,'<I',self.geometry());self.put(node,'<3I',part,nodes[i+1] if i+1<len(nodes) else head,nodes[i-1] if i else head)
def run(g,calls,label,changes=None):
 try:return case(calls,g.patches(),changes,label)
 except Exception:print('Failed model initialization dependency:',label,flush=True);raise
for count,directional in [(0,0),(1,1),(3,2),(2,4)]:
 changes={0x6faae0:count,0x6faae4:directional}
 for fill in [0,0xa5,0xff]:
  for ctor,destroy in [(0x48e5b0,0x48e630),(0x4b6270,0x4b6360)]:
   g=LightGraph();g.image[P-BASE:P-BASE+48]=bytes([fill])*48
   run(g,[call(ctor,P),call(destroy,P),call(destroy,P)],f'light arrays{count}/{directional} poison{fill} ctor{ctor:x}',changes)
 for flags in [0,1,2,256,257,0xffffffff]:
  g=LightGraph();run(g,[call(0x4b6b10),call(0x4b67b0,HEAP,[flags])],f'factory/delete{flags} sizes{count}/{directional}',changes)
 g=LightGraph();run(g,[call(0x48ea80),call(0x4b6920,args=[HEAP]),call(0x48c080,args=[0])],f'factory wrapper and actual virtual cleanup{count}/{directional}',changes)
for mask in range(8):
 g=LightGraph()
 for i,offset in enumerate([0x14,0x28,0x2c]):g.put(P+offset,'<I',g.alloc(32) if mask&(1<<i) else 0)
 run(g,[call(0x4b6360,P)],f'independent owned buffers {mask}')
for bits_ in [0,1,0xa5a5a5a5,0xffffffff]:
 for value in [0,1,2,256,257,0xffffffff]:
  g=LightGraph();g.put(P+0x1c,'<I',bits_);g.put(P+0x44,'<I',bits_)
  run(g,[call(0x4b61f0,P,[value]),call(0x48de30,P,[value]),call(0x492e90,P,[value])],f'low-byte ambient and low-bit renderer {bits_:x}/{value}')
for index_ in [0,1,30,31,32,63,0xffffffff]:
 for value in [0,1,256,257]:
  g=LightGraph();g.put(P+0x1c,'<I',0xa5a5a5a5)
  run(g,[call(0x4b6210,P,[index_,value]),call(0x48e4c0,P,[index_,value])],f'masked directional shift {index_}/{value}')
for pointer_ in [0,P,0xffffffff]:
 g=LightGraph();g.put(P+0x2c,'<I',pointer_);geometry=g.geometry()
 run(g,[call(0x532eb0,P),call(0x48e4d0,P,[pointer_]),call(0x48df20,geometry,[pointer_])],f'raw pointer getters and actual geometry empty slot {pointer_:x}')
for populated in [False,True]:
 for offset in [0,4,8,64]:
  g=LightGraph();g.put(P,'<I',0x64a4b4);source=P+offset;g.put(source+4,'<I',0x10203040);g.put(source+8,'<I',0x50607080);g.put(P+12,'<I',7 if populated else 0)
  run(g,[call(0x492dd0,P,[source])]*2,f'skeleton binding existing{populated}/alias{offset}')
for count in [None,0,1,3]:
 g=LightGraph();g.parts(count);g.put(P+0x2c,'<I',0)
 run(g,[call(0x493bd0,P),call(0x532eb0,P),call(0x493c10,P),call(0x493c10,P)],f'actual lighting lifetime and geometry propagation {count}',{0x6faae0:3,0x6faae4:2})
missing={hex(a):[hex(i.address) for i in code if not hits[i.address]] for a,code in coverage.items()}
print('MISSING',json.dumps(missing),flush=True)
excluded={hex(a):'initialized allocator bypasses process bootstrap' for a in [0x48e5dc,0x4b62b2,0x4b62df,0x4b6b2f]}
excluded.update({hex(a):'successful lighting allocation contract' for a in [0x4b6b6a,0x4b6b6e,0x4b6b70,0x4b6b77,0x4b6b7a]})
excluded['0x493c3d']='unreachable alignment after unconditional jump'
scope='Twenty original routines recover lighting base/derived construction, array ownership and destruction, real generic virtual deletion, ambient/directional bit controls, renderer skeleton binding and light-list propagation, and exact pointer/flag accessors. Original callees and the PC geometry actual bare-RET4 light slot execute, with no invented lighting behavior. Whole arenas/globals/heap order/preserved registers compare exactly; bounded initialized counts and successful allocations are explicit contracts. Model initialization is separately advanced only to the unavailable420d10 configuration/loading call, not counted as a completely recovered function. Model assets and rendering remain.'
finish('model-initialize',scope,excluded,extra)
