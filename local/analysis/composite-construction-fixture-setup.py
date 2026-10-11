"""New composite probes reuse immutable initialized game/heap oracle state."""
from pathlib import Path
source=Path('local/analysis/probe-node-index.py').read_text().split('for fill in [0,0xa5,0xff]:')[0]
exec(compile(source,'<preserved index setup>','exec'))
functions.clear();coverage.clear();hits.clear();labels.clear();oracle.coverage.clear()
exports += [[0x647650,'thug_composite_methods_draft'],[0x647618,'thug_component_methods'],[0x64bc48,'thug_physics_methods']]
put(MANAGER_METHODS+4,'<I',0x461a00);put(MANAGER_METHODS+12,'<I',0x4619a0)
put(ALLOCATOR+0x11c,'<I',ALLOCATOR+0x204);oracle.scope_entries[ALLOCATOR+0x204]=6
memory[MANAGER+0x3c-BASE:MANAGER+0x448-BASE]=bytes(0x40c)
fields.update([MANAGER_METHODS+4,MANAGER_METHODS+12])
function_exports += [[0x461a00,'thug_object_manager_add'],[0x4619a0,'thug_object_manager_rename'],[0x505440,'thug_physics_create']]
for j in range(128):glob('thug_component_type_heads',0x6f0db8+4*j,0,offset=4*j)
for j in range(8):glob('thug_collision_cache_registry',0x6918ec+4*j,0,offset=4*j)
glob('thug_collision_cache_mask',0x69190c,0)
for a in [0x45d730,0x500ca0]:oracle.cpu.hook_add(UC_HOOK_CODE,identities,begin=a,end=a)
initial=bytes(memory);oracle.initial=initial
extra={'function_exports':function_exports,'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES}}
class CompositeGraph(IndexGraph):
    def vector(self,words):
        v=self.alloc(16);self.put(v,'<4I',0,*words);return v
    def registry(self,types):
        self.put(MANAGER+0x44,'<I',len(types))
        for i,(kind,factory) in enumerate(types):
            at=MANAGER+0x48+8*i;self.put(at,'<2I',kind,factory);fields.add(at+4)
    def component(self,kind=0x12345678,methods=0x647618):
        p=self.alloc(0x30);self.put(p,'<6I',methods,kind,0,0,0,0);fields.add(p);return p
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
