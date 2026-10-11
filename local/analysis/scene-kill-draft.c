#include "../../src/game/nodes.h"
#include "../../src/game/stats.h"
#include "../../src/game/object_registry.h"
#include "../../src/collision/scene.h"
#include "../../src/script/schedule.h"
#include "../../src/core/checksum.h"
#include <stddef.h>

/* Original static storage 00787360..00792360 is 512 records. The boundary
 * comes from the adjacent work array, not a recovered capacity check. Valid
 * callers keep count within that storage, just as in the original engine. */
typedef struct {
    uint8_t unknown_0,enabled,padding[2];
    uint32_t name;
    uint8_t unknown_8[0x50];
} AuxiliaryGeometryDraft;
_Static_assert(sizeof(AuxiliaryGeometryDraft)==0x58,"Original auxiliary stride");
AuxiliaryGeometryDraft thug_aux_geometry_draft[512];
uint32_t thug_aux_geometry_count_draft; /* 00787350 */
/* 004d8c90. Change every matching record, retaining the low byte verbatim. */
void thug_aux_geometry_set_enabled_draft(uint32_t name,uint32_t enabled) {
    uint32_t count=thug_aux_geometry_count_draft;
    for(uint32_t i=0;i<count;++i)
        if(thug_aux_geometry_draft[i].name==name)
            thug_aux_geometry_draft[i].enabled=(uint8_t)enabled;
}
/* 004b22f0 and 0048bf90 are separate original tail-jump entry points. */
void thug_aux_geometry_set_enabled_forward_draft(uint32_t name,uint32_t enabled) {
    thug_aux_geometry_set_enabled_draft(name,enabled);
}
void thug_scene_aux_geometry_set_enabled_draft(uint32_t name,uint32_t enabled) {
    thug_aux_geometry_set_enabled_forward_draft(name,enabled);
}

extern ThugCollisionSceneNode *thug_scene_first_draft(void);
extern void thug_rail_set_enabled_draft(ThugObjectTransform *,uint32_t,uint32_t,uint32_t);
extern void thug_emitter_set_enabled_draft(uint32_t,uint32_t);
extern void thug_scene_remove_light_draft(uint32_t,const ThugMemory *);
extern void thug_geometry_set_enabled_draft(void *,uint32_t);
extern void thug_proximity_set_named_draft(uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
extern void thug_object_manager_visit_draft(ThugObjectManager *,ThugObjectVisitor,void *);
extern void thug_scene_kill_object_draft(void *,void *);
extern uint32_t thug_network_scene_mode_draft(const ThugNetworkState *);
extern uint8_t thug_script_get_scene_name_draft(const ThugScriptStructure *,uint32_t,uint32_t *,uint32_t);
extern uint32_t *thug_node_prefix_find_global_draft(uint32_t,uint16_t *);

/* 005a32c0, complete class dispatch. Native/event services are scoped by the
 * existing dispatcher, including when object destruction invokes callbacks. */
uint8_t thug_scene_kill_named_draft(uint32_t name,ThugScriptInstance *script) {
    ThugObjectTransform *rails=thug_game_context->rail_transform;
    ThugScriptStructure *node=thug_node_find(name,1);
    if(!node)return 0;
    uint32_t kind=0;
    thug_script_get_checksum(node,0x12b4e660,&kind,0);
    switch(kind) {
    case 0x08470f2e:
        thug_proximity_set_named_draft(name,0,thug_event_services->diagnostics,thug_event_services->memory);
        return 1;
    case 0x30c19600:case 0x8e6b02ad:
        thug_rail_set_enabled_draft(rails,name,0,
            thug_script_has_flag(node,thug_crc32_string("FLAG_WHOLE_RAIL")));
        return 1;
    case 0xa0e52802:
        thug_scene_remove_light_draft(name,thug_event_services->memory);
        return 1;
    case 0xd64dc7c2:
        thug_emitter_set_enabled_draft(name,0);
        return 1;
    case 0xbf4d3536: {
        uint32_t actual_name=0;
        if(!thug_script_get_checksum(node,0xa1dc81f9,&actual_name,0))return 1;
        ThugCollisionSceneNode *entry=thug_scene_first_draft();
        while(entry) {
            ThugCollisionSceneNode *following=entry->next;
            if((uintptr_t)following->scene==UINT32_MAX)following=0;
            void *geometry=thug_scene_find_object(entry->scene,actual_name);
            if(geometry) {
                thug_geometry_set_enabled_draft(geometry,0);
                if(thug_script_has_flag(node,0x4e549fe1))
                    thug_scene_aux_geometry_set_enabled_draft(actual_name,0);
                break;
            }
            entry=following;
        }
        thug_scene_aux_geometry_set_enabled_draft(actual_name,0);
        return 1;
    }
    case 0x061a741e:case 0x5b8ab877:case 0x9e7d469e:case 0xa0dfac98:
    case 0xb7b3bd86:case 0xe47f1b79:case 0xef59c100: {
        uintptr_t context[2]={name,(uintptr_t)script->owner.object};
        thug_object_manager_visit_draft((void *)thug_component_type_registry,
            thug_scene_kill_object_draft,context);
        return 1;
    }
    default:return 0;
    }
}

/* The two shared helpers 005a4da0/005a4ef0 support eight operations. Only
 * their constant operation=1 specialization belongs to native Kill. The
 * pure local-owner qualification feeds operations 2/3/4 alone and is dead
 * for Kill; omitting those reads changes no valid-input observable state.
 * This does not claim the other seven operations or the whole shared helpers. */
static uint8_t scene_kill_selected(uint32_t name,ThugScriptInstance *script) {
    if(thug_network_scene_mode_draft(thug_network_state)&&
       thug_script_multiplayer_gate(thug_node_find(name,1)))return 0;
    return thug_scene_kill_named_draft(name,script);
}
/* 005a5030, complete native Kill behavior including shared-helper selection.
 * Prefix wins over Name. Every prefix result is read live after the previous
 * deletion; per-name failures are ignored on that path, even an empty prefix.
 * The original third prefix-lookup argument has no effect in 0045bf90. */
uint8_t thug_script_kill_draft(const ThugScriptStructure *params,ThugScriptInstance *script) {
    if(thug_script_has_flag(params,0x2e7d5ee7)||thug_script_has_flag(params,0xbceb479a))return 1;
    uint32_t name=0;
    if(thug_script_get_scene_name_draft(params,0x6c4e7971,&name,0)) {
        uint16_t count=0;
        (void)thug_script_has_flag(params,0x80804991);
        uint32_t *names=thug_node_prefix_find_global_draft(name,&count);
        for(uint32_t i=0;i<count;++i)scene_kill_selected(names[i],script);
        return 1;
    }
    if(thug_script_get_scene_name_draft(params,0xa1dc81f9,&name,0))
        return scene_kill_selected(name,script);
    return 0;
}
