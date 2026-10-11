"""Initialized real object/registry state shared by lifetime/proximity probes."""
from pathlib import Path
exec(compile(Path('local/analysis/scene-lifetime-oracle.py').read_text(),'<registry helper>','exec'))
SERVICES,MANAGER_METHODS,OBJECT_METHODS,KILL_CONTEXT=BASE+0x15e00,BASE+0x15c00,BASE+0x15d00,BASE+0x15f00
put(SERVICES,'<2I',0,ADAPTER)
put(MANAGER_METHODS+8,'<I',0x461a50);put(MANAGER_METHODS+0x14,'<I',0x461b00)
put(OBJECT_METHODS,'<I',0x461900);put(OBJECT_METHODS+0x18,'<I',0x460a50)
put(MANAGER,'<I',MANAGER_METHODS)
put(MANAGER+0x28,'<5I',0x6477e4,0xffffffff,0,MANAGER+0x28,MANAGER+0x28)
initial=bytes(memory);oracle.initial=initial
fields.update([MANAGER_METHODS+8,MANAGER_METHODS+0x14,OBJECT_METHODS,OBJECT_METHODS+0x18,MANAGER+0x28])
glob('thug_component_type_registry',0x6f0fb8,MANAGER)
function_exports=[[0x461a50,'thug_object_manager_remove'],[0x461b00,'thug_object_enqueue_dead_draft'],
                  [0x461900,'thug_ui_object_delete'],[0x460a50,'thug_object_defer_delete_draft'],[0x59fb10,'thug_scene_kill_object_draft']]
extra={'function_exports':function_exports,'scoped_event_services':{'symbol':'thug_event_services','pointer':SERVICES}}
def ready_object(i=0,flags=0):
    o=OBJ+i*512
    return [patch(o,'<I',OBJECT_METHODS),patch(o+8,'<I',flags)]
