#include "../../src/game/components.h"
#include "../../src/game/nodes.h"
#include "../../src/game/grind.h"
#include "../../src/script/delivery.h"
#include "../../src/script/values.h"
#include "../../src/script/schedule.h"
void *thug_gameobject_create_prefix_draft(ThugScriptStructure *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void *thug_composite_create_draft(void *,const ThugMemory *);
void thug_composite_apply_node_draft(void *,const ThugScriptStructure *,const ThugMemory *);
/* 00468b60. The common path finalizes before assigning the owned trigger;
 * optional color runs afterwards. It does not send a model-moved notification. */
void thug_level_object_finalize_draft(void *object,ThugScriptStructure *node,const ThugDiagnostics *d,const ThugMemory *m){
 typedef struct{uintptr_t unused[8];void(*finalize)(void *,const ThugDiagnostics *,const ThugMemory *);} Methods;
 ((const Methods **)(object))[0]->finalize(object,d,m);
 uint32_t trigger=0;ThugScriptStructure *params=0;
 if(thug_script_get_checksum(node,0x2ca8a299,&trigger,0)){thug_script_get_structure(node,0x7031f10c,&params,0);thug_object_set_script(object,trigger,params,d,m);}
 uint32_t color;
 if(thug_script_get_integer(node,0x99a9b716,&color,0)){
  uint32_t name=thug_node_name(node);ThugScriptStructure *s=thug_script_structure_allocate(8,m);if(s)s=thug_script_structure_initialize(s);
  thug_script_set_checksum(s,0xa1dc81f9,name,m);thug_script_set_integer(s,0x99a9b716,color,m);thug_script_run_sync(0x413b766d,s,object,0,d,m);
  if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
 }
}
/* 00468ec0, now including the original bouncyobj_add_components script. */
void thug_level_object_create_prefix_draft(ThugScriptStructure *node){
 const ThugDiagnostics *d=thug_event_services->diagnostics;const ThugMemory *m=thug_event_services->memory;
 if(thug_script_has_flag(node,0x69c257e9)){
  void *object=thug_composite_create_draft(thug_component_type_registry,m);thug_composite_apply_node_draft(object,node,m);
  thug_script_run_sync(0xa98f5c63,node,object,0,d,m);thug_level_object_finalize_draft(object,node,d,m);
 }else thug_gameobject_create_prefix_draft(node,1,d,m);
}
