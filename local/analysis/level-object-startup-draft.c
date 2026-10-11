#include "../../src/game/components.h"
#include "../../src/script/delivery.h"
void *thug_gameobject_create_prefix_draft(ThugScriptStructure *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
/* Partial00468ec0. The original ordinary LevelObject path passes1 to468cb0.
 * Flag69c257e9 enters bouncyobj_add_components and requires the unrecovered
 * Rigidbody factory42ef00. It remains an explicit unavailable path. */
void thug_level_object_create_prefix_draft(ThugScriptStructure *node){
    if(thug_script_has_flag(node,0x69c257e9))__builtin_trap();
    thug_gameobject_create_prefix_draft(node,1,thug_event_services->diagnostics,thug_event_services->memory);
}
