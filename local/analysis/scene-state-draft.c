#include "../../src/collision/scene.h"
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/graphics/decal.h"
#include "../../src/game/object_registry.h"
#include <stddef.h>

/* 0048c7f0. The engine always supplies its sentinel head, even when empty. */
ThugCollisionSceneNode *thug_scene_first_draft(void) {
    ThugCollisionSceneNode *head=thug_collision_scene_list;
    return (uintptr_t)head->scene==UINT32_MAX?0:head;
}
/* 0044e4e0. This predicate is distinct from the existing network flag getter. */
uint32_t thug_network_scene_mode_draft(const ThugNetworkState *state) {
    return (state->flags&12)!=0;
}
/* 0057d7c0. First matching array entry; optionally follow its linked rail chain.
 * Recursive is a byte argument; enabled uses the entire argument word. */
void thug_rail_set_enabled_draft(ThugObjectTransform *manager,uint32_t name,
                               uint32_t enabled,uint32_t recursive) {
    int32_t count=manager->rail_count;
    ThugRailNode *node=manager->rail_nodes;
    for(int32_t i=0;i<count;++i,++node) {
        if(node->name!=name)continue;
        do {
            node->flags=enabled?node->flags|4:node->flags&~4u;
            if(!(uint8_t)recursive)break;
            node=node->next;
        } while(node);
        return;
    }
}
ThugObjectLookupTable *thug_emitter_table_draft; /* 006f2260 */
/* 00468340. A null iterator value terminates, including in collision chains. */
void thug_emitter_set_enabled_draft(uint32_t name,uint32_t enabled) {
    ThugObjectLookupTable *table=thug_emitter_table_draft;
    table->iteration_bucket=UINT32_MAX;table->iteration_node=0;
    for(;;) {
        table=thug_emitter_table_draft;
        if(!thug_object_table_next(table)||!table->iteration_node)return;
        uint8_t *emitter=table->iteration_node->value;
        if(!emitter)return;
        if(*(uint32_t *)emitter==name) { emitter[0x24]=enabled!=0;return; }
    }
}
/* 0049fd30. Preserve iteration fields; do not release the bucket array.
 * Capture the next collision before release, and the bucket base/limit once. */
void thug_object_table_clear_draft(ThugObjectLookupTable *table,const ThugMemory *memory) {
    ThugObjectLookupNode *head=table->buckets;
    if(!head)return;
    uint32_t count=1u<<(table->shift&31);
    do {
        for(ThugObjectLookupNode *node=head->next,*next;node;node=next) {
            next=node->next;
            if(thug_lookup_node_pool)thug_pool_release(thug_lookup_node_pool,node);
            else memory->release(memory->context,node);
        }
        head->key=0;head->value=0;head->next=0;++head;
    } while(--count);
    table->count=0;
}
/* 006faaf0..006faef0 is the original 256-pointer light array. The separate
 * 150-record decal light array is already shared with recovered lighting. */
void *thug_scene_lights_draft[256];
int32_t thug_scene_light_count_draft; /* 006faef0 */
/* 0048fca0. Remove the first match in EACH collection. Destruction precedes
 * reloading the live count and swap-removal. Decal light tail is not cleared. */
void thug_scene_remove_light_draft(uint32_t name,const ThugMemory *memory) {
    int32_t count=thug_scene_light_count_draft;
    for(int32_t i=0;i<count;++i) {
        uint8_t *light=thug_scene_lights_draft[i];
        if(*(uint32_t *)(light+0x28)!=name)continue;
        memory->release(memory->context,thug_scene_lights_draft[i]);
        uint32_t last=(uint32_t)thug_scene_light_count_draft-1;
        thug_scene_lights_draft[i]=thug_scene_lights_draft[last];
        thug_scene_light_count_draft=(int32_t)last;
        thug_scene_lights_draft[last]=0;
        break;
    }
    count=thug_decal_light_count;
    for(int32_t i=0;i<count;++i) {
        if(thug_decal_lights[i].name!=name)continue;
        thug_object_table_clear_draft(thug_decal_lights[i].owner,memory);
        uint32_t last=(uint32_t)thug_decal_light_count-1;
        thug_decal_light_count=(int32_t)last;
        /* Integer copies preserve every original bit, including float NaNs. */
        uint8_t *to=(uint8_t *)&thug_decal_lights[i];
        const uint8_t *from=(const uint8_t *)&thug_decal_lights[last];
        for(unsigned k=0;k<36;++k)to[k]=from[k];
        break;
    }
}
typedef struct RenderEnabledDraft RenderEnabledDraft;
typedef struct {
    uint32_t unavailable[13];
    void (*set_enabled)(RenderEnabledDraft *,uint32_t);
} RenderEnabledMethodsDraft;
struct RenderEnabledDraft { const RenderEnabledMethodsDraft *methods; };
typedef struct {
    uint8_t unknown_0_to_13[0x14];
    RenderEnabledDraft *render;
    ThugCollisionInstance *collision;
} SceneGeometryDraft;
_Static_assert(offsetof(SceneGeometryDraft,collision)==0x18,"Original geometry prefix");
/* 0048de60. Recovered virtual forwarding, not a renderer implementation. */
void thug_render_set_enabled_draft(RenderEnabledDraft *render,uint32_t enabled) {
    render->methods->set_enabled(render,enabled);
}
/* 0049e9b0. Collision flag changes occur before renderer dispatch. */
void thug_geometry_set_enabled_draft(SceneGeometryDraft *geometry,uint32_t enabled) {
    ThugCollisionInstance *collision=geometry->collision;
    if(collision) {
        uint8_t *flags=(uint8_t *)collision+8;
        *flags=(uint8_t)enabled?*flags&~4u:*flags|4u;
    }
    RenderEnabledDraft *render=geometry->render;
    if(render)thug_render_set_enabled_draft(render,enabled);
}
/* 00461cc0. Each active traversal owns a visited bit. Changes to the manager
 * can request a restart; already visited objects must not receive it twice.
 * The node AND its following object are captured before invoking a callback.
 * Callbacks return normally; PC structured exception unwinding is host ABI. */
static ThugQueueNode *scene_list_node(ThugQueueNode *node) {
    return (uintptr_t)node->value==UINT32_MAX?0:node;
}
void thug_object_manager_visit_draft(ThugObjectManager *manager,
                                     ThugObjectVisitor visit,void *context) {
    uint32_t used=manager->unknown_18,bit=1;
    while(used&bit)bit<<=1;
    manager->unknown_18=used|bit;
    ThugQueueNode *node=scene_list_node(manager->objects.previous);
    while(node&&node->value) {
        ((ThugUiObjectBase *)node->value)->unknown_1c&=~bit;
        node=scene_list_node(node->previous);
    }
    do {
        manager->cached_id&=~bit;
        node=scene_list_node(manager->objects.previous);
        ThugUiObjectBase *object=node?node->value:0;
        while(object) {
            ThugUiObjectBase *current=object;
            node=scene_list_node(node->previous);
            object=node?node->value:0;
            if(current->unknown_1c&bit)continue;
            current->unknown_1c|=bit;
            visit(current,context);
            if(manager->cached_id&bit)break;
        }
    } while(manager->cached_id&bit);
    manager->unknown_18&=~bit;
}
