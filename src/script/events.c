#include "events.h"
#include "values.h"
#include <stddef.h>

uint32_t thug_script_listener_pool_index;
ThugFixedPool *thug_script_listener_pools[2];
const ThugScriptListenerMethods thug_script_listener_methods = { thug_script_listener_delete };
const ThugScriptListenerMethods thug_script_listener_list_methods = { thug_script_listener_list_delete };
_Static_assert(sizeof(ThugScriptListener) == 20, "Original event listener node");
_Static_assert(sizeof(ThugScriptEventEntry) == 20, "Original script event entry");
_Static_assert(offsetof(ThugObjectLookupManager, listeners) == 0x10, "Original listener table");
_Static_assert(offsetof(ThugScriptInstance, events) == 0xe0, "Original event handlers");

/* 0x004624d0. Test both pools before falling back to the generic heap. */
void thug_script_listener_free(void *node, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_listener_pools[thug_script_listener_pool_index];
    if (pool && thug_pool_contains(pool, node)) { thug_pool_release(pool, node); return; }
    pool = thug_script_listener_pools[thug_script_listener_pool_index ^ 1];
    if (pool && thug_pool_contains(pool, node)) thug_pool_release(pool, node);
    else memory->release(memory->context, node);
}
/* 0x00462530. Restore the base methods, unlink, and leave a self-linked node. */
void thug_script_listener_destroy(ThugScriptListener *node) {
    node->methods = &thug_script_listener_methods;
    node->previous->next = node->next;
    node->next->previous = node->previous;
    node->next = node; node->previous = node;
}
/* 0x00462550 and 0x00462710. Deleting destructors use the generic heap,
 * not the two-pool free routine used for empty list sentinels. */
ThugScriptListener *thug_script_listener_delete(ThugScriptListener *node, uint32_t flags, const ThugMemory *memory) {
    thug_script_listener_destroy(node);
    if (flags & 1) memory->release(memory->context, node);
    return node;
}
ThugScriptListener *thug_script_listener_list_delete(ThugScriptListener *node, uint32_t flags, const ThugMemory *memory) {
    thug_script_listener_destroy(node);
    if (flags & 1) memory->release(memory->context, node);
    return node;
}
/* 0x004626b0. Only the first matching listener is removed. A -1 value marks
 * the sentinel; the list is circular and internal callers provide valid links. */
void thug_script_listener_remove(ThugScriptListener *list, uint32_t value, const ThugMemory *memory) {
    ThugScriptListener *node = list->next;
    if (node->value == UINT32_MAX) return;
    for (;;) {
        if (node->value == value) break;
        node = node->next;
        if (node->value == UINT32_MAX) return;
    }
    node->previous->next = node->next;
    node->next->previous = node->previous;
    node->next = node; node->previous = node;
    node->methods->dispose(node, 1, memory);
}
/* 0x00463450. An already empty list is removed even if no listener matched. */
void thug_script_unsubscribe(ThugObjectLookupManager *manager, uint32_t event, ThugScriptInstance *script, const ThugMemory *memory) {
    ThugScriptListener *list = thug_object_table_find(manager->listeners, &event, 0);
    if (!list) return;
    thug_script_listener_remove(list, (uintptr_t)script, memory);
    if (list->previous == list) {
        thug_object_table_remove(manager->listeners, &event, memory);
        thug_script_listener_destroy(list);
        thug_script_listener_free(list, memory);
    }
}
/* 0x00462b90. Advance the shared iterator BEFORE deleting the current bucket
 * or collision node. Duplicate listener values lose only their first entry. */
void thug_script_unsubscribe_all(ThugObjectLookupManager *manager, ThugScriptInstance *script, const ThugMemory *memory) {
    ThugObjectLookupTable *table = manager->listeners;
    table->iteration_bucket = UINT32_MAX; table->iteration_node = NULL;
    if (!thug_object_table_next(table) || !table->iteration_node) return;
    uint32_t event = table->iteration_node->key;
    ThugScriptListener *list = table->iteration_node->value;
    while (list) {
        table = manager->listeners;
        ThugScriptListener *next = NULL;
        uint32_t next_event = event;
        if (thug_object_table_next(table) && table->iteration_node) {
            next_event = table->iteration_node->key; next = table->iteration_node->value;
        }
        thug_script_listener_remove(list, (uintptr_t)script, memory);
        if (list->previous == list) {
            thug_object_table_remove(manager->listeners, &event, memory);
            thug_script_listener_destroy(list); thug_script_listener_free(list, memory);
        }
        event = next_event; list = next;
    }
}
/* 0x0045fa60. Event-table order and repeated event keys are significant. */
void thug_script_events_unsubscribe(ThugScriptEventTable *table, ThugScriptInstance *script, const ThugMemory *memory) {
    ThugScriptEventEntry *entry = table->entries;
    for (uint32_t i = 0; (int32_t)i < (int32_t)table->count; ++i, ++entry)
        if (entry->event) thug_script_unsubscribe(thug_object_lookup_manager, entry->event, script, memory);
}
/* 0x0045fe60. The wildcard clears every handler but retains event/group keys.
 * Disabling precedes parameter disposal, and the pointer is cleared afterward. */
void thug_script_events_clear_group(ThugScriptEventTable *table, uint32_t group, const ThugMemory *memory) {
    for (uint32_t i = 0; (int32_t)i < (int32_t)table->count; ++i) {
        if (table->entries[i].group == group || group == 0x8b713e0e) {
            table->entries[i].script = 0xc377c572;
            ThugScriptStructure *parameters = table->entries[i].parameters;
            if (parameters) {
                thug_script_structure_destroy(parameters, memory);
                thug_script_structure_free(parameters, memory);
                table->entries[i].parameters = NULL;
            }
        }
    }
}
/* 0x00473010. Also remove subscriptions outside the explicit event table when
 * bit 0x10 is set. The table pointer and that flag remain unchanged. */
void thug_script_clear_events(ThugScriptInstance *script, const ThugMemory *memory) {
    if (script->events) {
        thug_script_events_unsubscribe(script->events, script, memory);
        thug_script_events_clear_group(script->events, 0x8b713e0e, memory);
    }
    if (script->flags_cc & 0x10) thug_script_unsubscribe_all(thug_object_lookup_manager, script, memory);
}
/* 0x0045fb70. Dispose owned entries without clearing their now-dangling fields.
 * The caller controls the table allocation's lifetime. */
void thug_script_events_destroy(ThugScriptEventTable *table, const ThugMemory *memory) {
    if (!table->entries) return;
    for (uint32_t i = 0; (int32_t)i < (int32_t)table->count; ++i) {
        ThugScriptStructure *parameters = table->entries[i].parameters;
        if (parameters) {
            thug_script_structure_destroy(parameters, memory);
            thug_script_structure_free(parameters, memory);
        }
    }
    memory->release(memory->context, table->entries);
}

/* 0x0045fdf0. Disable all matching entries before destroying their parameters.
 * Reload the entry array and signed count after each allocator call. */
void thug_script_events_remove(ThugScriptEventTable *table, uint32_t event, const ThugMemory *memory) {
    for (uint32_t i=0;(int32_t)i<(int32_t)table->count;++i) {
        if (table->entries[i].event==event) {
            table->entries[i].event=0;
            table->entries[i].script=0xc377c572;
            ThugScriptStructure *parameters=table->entries[i].parameters;
            if (parameters) {
                thug_script_structure_destroy(parameters,memory);
                thug_script_structure_free(parameters,memory);
                table->entries[i].parameters=NULL;
            }
        }
    }
}
/* 0x00473690. A missing event table also suppresses listener removal. */
void thug_script_remove_event(ThugScriptInstance *script,uint32_t event,const ThugMemory *memory) {
    if (script->events) {
        thug_script_events_remove(script->events,event,memory);
        thug_script_unsubscribe(thug_object_lookup_manager,event,script,memory);
    }
}
/* 0x004607a0. Object script pointer is shared with the recovered runtime prefix. */
void thug_object_remove_event(ThugReferencedObject *object,uint32_t event,const ThugMemory *memory) {
    ThugScriptInstance *script=(ThugScriptInstance *)(uintptr_t)object->unknown_8_to_10[2];
    if (script) thug_script_remove_event(script,event,memory);
}
