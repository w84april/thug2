#include "../../src/game/nodes.h"
#include "../../src/game/stats.h"
#include "../../src/script/schedule.h"
#include "../../src/script/delivery.h"
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/game/drawing.h"
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
void *thug_proximity_find_draft(uint32_t);
void thug_component_suspend_update_draft(void *);
extern const ThugComponentMethods thug_simple_sound_methods_draft;
/* 00433d90. The constructor is inlined in this 44-byte component factory. */
void *thug_simple_sound_create_draft(const ThugMemory *m){
    void *p=thug_allocate_zeroed(0x2c,m);
    if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_simple_sound_methods_draft);
        put(p,4,0x0f1641e3);put(p,0x24,0);put(p,0x28,0);}
    return p;
}
/* 00433900. Missing ProximNode retains the existing pointer. */
void thug_simple_sound_initialize_draft(void *p,const ThugScriptStructure *s){
    uint32_t name;if(thug_script_get_checksum(s,0x08470f2e,&name,0))put(p,0x28,(uintptr_t)thug_proximity_find_draft(name));
}
static void empty(void *p){thug_draw_style_noop(p);}
static void suspend_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
static uint32_t unhandled(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *script){return thug_animation_unhandled_command(p,n,s,script,0,0);}
/* Actual646594 table. Destruction433c40/433890 and sound-command members
 * remain unavailable; construction does not claim audio playback support. */
const ThugComponentMethods thug_simple_sound_methods_draft={
    .update=suspend_frame,.initialize=thug_simple_sound_initialize_draft,.finalize=empty,
    .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,
    .suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,
    .moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
    .descriptor=thug_component_descriptor,.checksum=unhandled
};
/* Partial class construction. The original GameObject branch is available;
 * other recognized classes stop before their unrecovered creation routines. */
void *thug_gameobject_create_prefix_draft(ThugScriptStructure *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_flush_dead_objects_draft(void *,void *);
uint32_t thug_network_scene_mode_draft(const ThugNetworkState *);
uint8_t thug_script_get_scene_name_draft(const ThugScriptStructure *,uint32_t,uint32_t *,uint32_t);
uint32_t *thug_node_prefix_find_global_draft(uint32_t,uint16_t *);
/* 00468eb0. The original wrapper passes zero and preserves the object return. */
void *thug_gameobject_create_node_prefix_draft(ThugScriptStructure *node){
    return thug_gameobject_create_prefix_draft(node,0,thug_event_services->diagnostics,thug_event_services->memory);
}
/* Partial005a2e50. The initial name getter and multiplayer gate are original.
 * Captured rail-context reads have no side effects on these branches. */
void thug_level_object_create_prefix_draft(ThugScriptStructure *);
uint8_t thug_scene_create_node_prefix_draft(ThugScriptStructure *node){
    (void)thug_node_name(node);
    if((uint8_t)thug_script_multiplayer_gate(node))return 1;
    uint32_t kind=0;thug_script_get_checksum(node,0x12b4e660,&kind,0);
    if(kind==0xe594f0a2){uint32_t name=0;thug_script_get_checksum(node,0xa1dc81f9,&name,1);}
    switch(kind){
    case 0xef59c100:thug_gameobject_create_node_prefix_draft(node);return 1;
    case 0xb7b3bd86:thug_level_object_create_prefix_draft(node);return 1;
    case 0x061a741e:case 0x08470f2e:case 0x30c19600:case 0x8e6b02ad:
    case 0x9e7d469e:case 0xa0dfac98:case 0xbf4d3536:
    case 0xd64dc7c2:case 0xe47f1b79:__builtin_trap();
    default:return 0;
    }
}
/* 005a32a0 and005a34d0, with the above partial dependency. */
uint8_t thug_scene_create_named_prefix_draft(uint32_t name){return thug_scene_create_node_prefix_draft(thug_node_find(name,1));}
uint8_t thug_script_create_structure_prefix_draft(ThugScriptStructure *node,ThugScriptInstance *script){(void)script;return thug_scene_create_node_prefix_draft(node);}
/* Operation0 of005a4da0. The shared local-owner qualification is pure and only
 * affects operations2/3/4; preserve the actual network gate for Create. */
static uint8_t selected(uint32_t name){
    if(thug_network_scene_mode_draft(thug_network_state)&&thug_script_multiplayer_gate(thug_node_find(name,1)))return 0;
    return thug_scene_create_named_prefix_draft(name);
}
/* Partial005a4ff0: actual dead-object flush, then full operation0 selection from
 * 005a4ef0. Prefix precedes Name and ignores per-name return values. */
uint8_t thug_script_create_prefix_draft(const ThugScriptStructure *params,ThugScriptInstance *script){
    (void)script;thug_flush_dead_objects_draft(0,0);
    if(thug_script_has_flag(params,0x2e7d5ee7)||thug_script_has_flag(params,0xbceb479a))return 1;
    uint32_t name=0;
    if(thug_script_get_scene_name_draft(params,0x6c4e7971,&name,0)){
        uint16_t count=0;(void)thug_script_has_flag(params,0x80804991);
        uint32_t *names=thug_node_prefix_find_global_draft(name,&count);
        for(uint32_t i=0;i<count;i++)selected(names[i]);
        return 1;
    }
    if(thug_script_get_scene_name_draft(params,0xa1dc81f9,&name,0))return selected(name);
    return 0;
}
