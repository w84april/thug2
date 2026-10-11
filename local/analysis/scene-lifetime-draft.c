#include "../../src/game/object_registry.h"
#include "../../src/script/schedule.h"
#include <stddef.h>

typedef struct {
    ThugObjectManager base;
    ThugQueueNode dead;
} SceneObjectManagerDraft;
typedef struct {
    uint32_t unavailable_0[2];
    void (*remove)(ThugObjectManager *,ThugUiObjectBase *,const ThugMemory *);
    uint32_t unavailable_c[2];
    void (*enqueue_dead)(SceneObjectManagerDraft *,ThugUiObjectBase *);
} SceneManagerMethodsDraft;
typedef struct {
    uint32_t unavailable[6];
    void (*defer_delete)(ThugUiObjectBase *,const ThugDiagnostics *,const ThugMemory *);
} SceneObjectMethodsDraft;
_Static_assert(offsetof(SceneObjectManagerDraft,dead.previous)==0x34,"Dead-object list head");

/* 00460930. Bit 1 suppresses direct destruction, including all other flag bits. */
void thug_object_delete_unless_deferred_draft(ThugUiObjectBase *object,
        const ThugDiagnostics *d,const ThugMemory *m) {
    if(!(object->object.unknown_8_to_10[0]&2)) {
        const ThugUiObjectMethods *methods=(const void *)(uintptr_t)object->object.unknown_0;
        methods->dispose(object,1,d,m);
    }
}
/* 0059fb10. The original callback context's second word (script owner) is
 * intentionally unused. Fixed-argument callbacks use the existing scoped
 * native/event service binding, which is restored by the outer dispatcher. */
void thug_scene_kill_object_draft(void *value,void *context) {
    ThugUiObjectBase *object=value;
    if(object->object.id==*(const uint32_t *)context)
        thug_object_delete_unless_deferred_draft(object,thug_event_services->diagnostics,thug_event_services->memory);
}
/* 00461b00. Insert at the head of the dead list; read its head again after the
 * first link store, as the original does. Caller supplies an unlinked object. */
void thug_object_enqueue_dead_draft(SceneObjectManagerDraft *manager,ThugUiObjectBase *object) {
    ThugQueueNode *node=&object->queue_node,*sentinel=&manager->dead;
    node->next=sentinel;
    node->previous=sentinel->previous;
    sentinel->previous->next=node;
    sentinel->previous=node;
}
/* 00461ab0. Snapshot the next list node before unlinking and destruction.
 * Do not re-read the manager head after callbacks; additions wait for a later
 * flush. Unlike guarded direct deletion, every nonnull queued value is deleted. */
void thug_dead_objects_flush_draft(SceneObjectManagerDraft *manager,
        const ThugDiagnostics *d,const ThugMemory *m) {
    ThugQueueNode *node=manager->dead.previous;
    if((uintptr_t)node->value==UINT32_MAX)return;
    while(node) {
        ThugQueueNode *next=node->previous;
        if((uintptr_t)next->value==UINT32_MAX)next=0;
        node->next->previous=node->previous;
        node->previous->next=node->next;
        node->previous=node;node->next=node;
        ThugUiObjectBase *object=node->value;
        if(object) {
            const ThugUiObjectMethods *methods=(const void *)(uintptr_t)object->object.unknown_0;
            methods->dispose(object,1,d,m);
        }
        node=next;
    }
}
/* 005b0a40. Native ABI arguments are ignored; the shared manager is 006f0fb8. */
uint8_t thug_flush_dead_objects_draft(void *params,void *script) {
    (void)params;(void)script;
    thug_dead_objects_flush_draft((void *)thug_component_type_registry,
        thug_event_services->diagnostics,thug_event_services->memory);
    return 1;
}
/* 00462620. Append a unique value. Allocate within a temporary heap scope;
 * leaving that scope occurs before reading the list's current tail. */
void thug_script_listener_add_draft(ThugScriptListener *list,uint32_t value,const ThugMemory *m) {
    ThugScriptListener *node=list->next;
    if(node->value!=UINT32_MAX)
        for(;node&&node->value!=UINT32_MAX;node=node->next)
            if(node->value==value)return;
    m->temp_scope(m->context,1);
    node=thug_allocate_zeroed(20,m);
    if(node) {
        node->value=value;node->methods=&thug_script_listener_methods;node->unknown_8=0;
        node->next=node;node->previous=node;
    }
    m->temp_scope(m->context,0);
    node->previous=list->previous;node->next=list;
    list->previous->next=node;list->previous=node;
}
/* 00463370. Existing subscriptions deduplicate by script identity. List
 * sentinels use the selected listener pool; ordinary links use zeroed heap. */
void thug_script_subscribe_draft(ThugObjectLookupManager *manager,uint32_t event,
                                ThugScriptInstance *script,const ThugMemory *m) {
    m->temp_scope(m->context,1);
    ThugScriptListener *list=thug_object_table_find(manager->listeners,&event,0);
    if(!list) {
        ThugFixedPool *pool=thug_script_listener_pools[thug_script_listener_pool_index];
        list=pool?thug_pool_allocate(pool):m->allocate(m->context,20,1);
        if(list) {
            list->value=UINT32_MAX;list->unknown_8=0;list->next=list;list->previous=list;
            list->methods=&thug_script_listener_list_methods;
        }
        thug_object_table_insert(manager->listeners,&event,list,m);
    }
    thug_script_listener_add_draft(list,(uintptr_t)script,m);
    m->temp_scope(m->context,0);
}
/* 00472fd0. A zero event still selects wait type 3, without subscribing. */
void thug_script_set_event_wait_draft(ThugScriptInstance *script,uint32_t event,const ThugMemory *m) {
    script->wait_type=3;script->wait_argument=event;
    if(event) {
        thug_script_subscribe_draft(thug_object_lookup_manager,event,script,m);
        script->flags_cc|=0x10;
    }
}
/* 00460a50. Script stopping can mutate the object's manager, so read it only
 * afterward. Removing clears manager ownership; capture the manager across
 * that call and re-read its methods before enqueuing. */
void thug_object_defer_delete_draft(ThugUiObjectBase *object,
        const ThugDiagnostics *d,const ThugMemory *m) {
    ThugScriptInstance *script=(void *)(uintptr_t)object->object.unknown_8_to_10[2];
    if(script)thug_script_set_event_wait_draft(script,0,m);
    thug_script_stop_all_for_owner(&object->object,d,m);
    object->object.unknown_8_to_10[0]&=~2u;
    SceneObjectManagerDraft *manager=(void *)(uintptr_t)object->object.unknown_8_to_10[1];
    ((const SceneManagerMethodsDraft *)manager->base.methods)->remove(&manager->base,object,m);
    ((const SceneManagerMethodsDraft *)manager->base.methods)->enqueue_dead(manager,object);
    object->object.unknown_8_to_10[0]|=1;
    thug_object_references_clear(&object->secondary_target);
}
typedef struct ProximityNodeDraft {
    uint32_t name;
    uint8_t unknown_4[0x50];
    uint8_t active,padding_55[3];
    uint32_t object_base,object_mask,script_mask,last_object;
    uint8_t unknown_68[0x38];
    uint32_t exit_script;
    struct ProximityNodeDraft *next;
} ProximityNodeDraft;
typedef struct {ProximityNodeDraft *first;uint8_t flag_4,dispatching;} ProximityManagerDraft;
ProximityManagerDraft *thug_proximity_manager_draft; /* 006f2268 */
_Static_assert(offsetof(ProximityNodeDraft,exit_script)==0xa0,"Proximity exit script");
/* 0046abc0. Masks are consumed by shifting live storage after every callback.
 * A missing proximity manager leaves script_mask untouched. */
void thug_proximity_set_active_draft(ProximityNodeDraft *node,uint32_t active,
        const ThugDiagnostics *d,const ThugMemory *m) {
    if(node->active==(uint8_t)active)return;
    if(node->active) {
        if(node->object_base) {
            uint32_t index=0;
            while(node->object_mask) {
                if(node->object_mask&1) {
                    ThugUiObjectBase *object=thug_object_find_global(thug_component_type_registry,node->object_base+index);
                    if(object)((const SceneObjectMethodsDraft *)(uintptr_t)object->object.unknown_0)->defer_delete(object,d,m);
                }
                node->object_mask>>=1;++index;
            }
        } else {
            ProximityManagerDraft *manager=thug_proximity_manager_draft;
            if(manager) {
                uint32_t index=0;
                while(node->script_mask) {
                    if(node->script_mask&1) {
                        ThugReferencedObject *owner=thug_object_find_global(thug_component_type_registry,index);
                        manager->flag_4=0;manager->dispatching=1;
                        if(owner)thug_object_spawn_script(owner,node->exit_script,node->name,0,0,0,d,m);
                        manager->dispatching=0;
                    }
                    node->script_mask>>=1;++index;
                }
            }
        }
    }
    node->last_object=UINT32_MAX;node->active=(uint8_t)active;
}
/* 0046acb0. By-name lookup normalizes the entire enabled word to a boolean. */
void thug_proximity_set_named_draft(uint32_t name,uint32_t active,
        const ThugDiagnostics *d,const ThugMemory *m) {
    ProximityManagerDraft *manager=thug_proximity_manager_draft;
    if(!manager)return;
    for(ProximityNodeDraft *node=manager->first;node;node=node->next)
        if(node->name==name){thug_proximity_set_active_draft(node,active!=0,d,m);return;}
}
