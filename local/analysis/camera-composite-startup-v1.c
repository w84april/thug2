/* 0041b7f0: real manager virtual priority, used by camera initialization.
 * The memory argument carries the maintained host ABI into the original call. */
#include "../../src/game/components.h"
#include "../../src/game/object_registry.h"
void thug_generic_camera_initialize_priority_v1(void *p,const ThugScriptStructure *params,const ThugMemory *memory){
    (void)params;
    void *owner;__builtin_memcpy(&owner,(const char *)p+12,4);
    ThugObjectManager *manager=(ThugObjectManager *)thug_component_type_registry;
    manager->methods->set_priority(manager,owner,0xfffffc18u,memory);
}
/* Only the ABI scope is authored; startup establishes it around virtual calls. */
void thug_generic_camera_initialize_bridge_v1(void *p,const ThugScriptStructure *params){
    thug_generic_camera_initialize_priority_v1(p,params,thug_component_services->memory);
}
