/* Private integration candidate. ZERO recovery credit until full verification.
 * Original native/member registration and sound storage factory; audio commands
 * outside the observed unhandled path trap. Host service bridges are authored.
 */
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/script/load.h"
#include "../../src/core/checksum.h"
#include <stddef.h>
void thug_script_register_natives_v1(const uint32_t *table,uint32_t count,const ThugMemory *m){
 for(uint32_t i=0;i<count;i++){
  uint32_t name=thug_crc32_string((const char *)(uintptr_t)table[i*2]);
  thug_script_add_debug_name(name,(const char *)(uintptr_t)table[i*2]);
  ThugScriptSymbol *s=thug_script_symbol_create(name,m);s->type=8;s->value=table[i*2+1];
 }
}
void thug_script_register_members_v1(const uint32_t *table,uint32_t count,const ThugMemory *m){
 for(uint32_t i=0;i<count;i++){
  uint32_t name=thug_crc32_string((const char *)(uintptr_t)table[i]);
  thug_script_add_debug_name(name,(const char *)(uintptr_t)table[i]);
  thug_script_symbol_create(name,m)->type=9;
 }
}
uint8_t thug_script_native_missing_v1(ThugScriptStructure *p,ThugScriptInstance *s){(void)p;(void)s;__builtin_trap();}
extern uint8_t thug_collision_accepts_light_draft(const void *);
/* ABI adapter for the AL=1 body already recovered at005b9760, actual Printf. */
uint8_t thug_script_printf_binding_v1(ThugScriptStructure *p,ThugScriptInstance *s){(void)s;return thug_collision_accepts_light_draft(p);}
static void *pending_delete(void *p,uint32_t flags,const ThugMemory *m){(void)p;(void)flags;(void)m;__builtin_trap();}
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static void pending_initialize(void *p,const ThugScriptStructure *s){(void)p;(void)s;__builtin_trap();}
static void idle(void *p){thug_animation_controller_idle(p,NULL,NULL);}
/* Original518fd0 default branch only; recognized audio cases are unavailable. */
uint32_t thug_skater_sound_command_unhandled_v1(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *i){
 (void)p;(void)s;(void)i;
 if(name==0x2c779f22||name==0x0069e457||name==0x0e338369||name==0x6f5e9124)__builtin_trap();
 return 2;
}
const ThugComponentMethods thug_skater_sound_pending_methods_v1={
 .dispose=pending_delete,.update=pending_frame,.initialize=pending_initialize,
 .finalize=idle,.unknown_10=idle,.refresh=thug_component_refresh,
 .unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,
 .unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,
 .checksum=thug_skater_sound_command_unhandled_v1
};
void *thug_skater_sound_create_storage_v1(const ThugMemory *m){
 uint32_t *p=thug_allocate_zeroed(0x28,m);
 if(p){thug_component_construct(p);p[8]=0x3f800000;p[9]=0x3f800000;
  p[0]=(uintptr_t)&thug_skater_sound_pending_methods_v1;p[1]=0x187574fa;((uint8_t *)p)[0x1e]=0;}
 return p;
}
/* Scope host services for original fixed-argument component calls. */
void thug_skater_grounded_frame_scoped_v1(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 const ThugComponentServices services={q,d,m},*previous=thug_component_services;
 thug_component_services=&services;thug_skater_update_grounded(p,q,d,m);thug_component_services=previous;
}

/* Observed original518760/523560/517c80/4f9420 EndGap and StartGap default paths ONLY.
 * Native v10 and jump-action-live-v1 prove return2, unchanged full receiver
 * and original RET12 for the bounded EndGap/StartGap calls. This partial integration earns zero function/byte credit.
 */
uint32_t thug_component_endgap_unhandled_v1(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *i){
 (void)p;(void)s;(void)i;if(name!=0xe5399fb2&&name!=0x65b9ec39)__builtin_trap();return 2;
}

/* Original005594f0 native QB predicate. Required Name is an internal caller
 * contract. The existing original manager lookup owns cache side effects.
 * An absent goal returns false; present goals use the original active slot. */
#include "../../src/game/objectives.h"
uint8_t thug_script_goal_is_active_v1(ThugScriptStructure *parameters,ThugScriptInstance *script){
 (void)script;
 ThugObjectiveManager *manager=thug_game_difficulty_settings(thug_game_context);
 uint32_t name;
 if(!thug_script_get_checksum(parameters,0xa1dc81f9,&name,1))__builtin_trap();
 ThugObjective *goal=thug_objective_find(manager,&name);
 return goal?((const ThugObjectiveMethods *)goal->queue_node.methods)->is_active(goal):0;
}
