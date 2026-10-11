#include "object_registry.h"
#include "objectives.h"
#include "../core/checksum.h"
#include "../script/values.h"
#include <stddef.h>
_Static_assert(sizeof(ThugObjectManager) == 0x28, "Object manager prefix");
_Static_assert(offsetof(ThugObjectManager, renaming) == 0x24, "Rename flag");
const ThugObjectManagerMethods thug_object_manager_methods = {
    thug_object_manager_delete, thug_object_manager_add, thug_object_manager_remove,
    thug_object_manager_rename, thug_object_manager_set_priority, 0, 0
};
const ThugQueueMethods thug_object_manager_queue_methods = {thug_object_manager_queue_delete};
/* 0x00461b20. The embedded queue returns to its base node's methods. */
ThugQueueNode *thug_object_manager_queue_delete(ThugQueueNode *node, uint32_t flags, const ThugMemory *memory) {
    thug_ui_object_queue_destroy(node);
    if ((uint8_t)flags & 1) memory->release(memory->context, node);
    return node;
}
/* 0x00461b50 and 0x00461b80. Object disposal is not this base's responsibility. */
void thug_object_manager_destroy(ThugObjectManager *manager) {
    manager->methods = &thug_object_manager_methods;
    thug_ui_object_queue_destroy(&manager->objects);
}
ThugObjectManager *thug_object_manager_delete(ThugObjectManager *manager, uint32_t flags, const ThugMemory *memory) {
    thug_object_manager_destroy(manager);
    if ((uint8_t)flags & 1) memory->release(memory->context, manager);
    return manager;
}
/* 0x00461bc0. replacement_id and the trailing padding are untouched. */
ThugObjectManager *thug_object_manager_initialize(ThugObjectManager *manager) {
    manager->methods = &thug_object_manager_methods;
    manager->objects.methods = &thug_object_manager_queue_methods;
    manager->objects.value = (void *)(uintptr_t)UINT32_MAX;
    manager->objects.priority = 0;
    manager->objects.previous = manager->objects.next = &manager->objects;
    manager->unknown_18 = manager->cached_id = 0;
    manager->renaming = 0;
    return manager;
}
/* The original uses CRT sprintf("autoid%d", signed_counter). This bounded
 * formatting adapter needs no locale, width, varargs or floating-point support. */
static void auto_id_text(char *out, uint32_t word) {
    const char prefix[] = "autoid";
    for (unsigned i = 0; i < 6; ++i) *out++ = prefix[i];
    uint32_t magnitude = word;
    if ((int32_t)word < 0) { *out++ = '-'; magnitude = 0u - word; }
    char digits[10]; unsigned count = 0;
    do { digits[count++] = (char)('0' + magnitude % 10); magnitude /= 10; } while (magnitude);
    while (count) *out++ = digits[--count];
    *out = 0;
}
/* 0x004621d0. Global registry counter, not the local manager's queue field. */
uint32_t thug_object_registry_next_id(ThugObjectLookupManager *manager) {
    for (;;) {
        uint32_t counter = manager->unknown_4;
        manager->unknown_4 = counter + 1;
        char text[64]; auto_id_text(text, counter);
        if ((int32_t)manager->unknown_4 >= 1000000) manager->unknown_4 = 0;
        uint32_t name = thug_crc32_string(text);
        if (!thug_object_table_find(manager->primary, &name, 1)) return name;
    }
}
/* 0x00462590. Restart the shared iterator after each removal. Match the
 * referenced object's ID, which can differ from its alias table key. */
void thug_object_registry_clear_aliases(ThugObjectLookupManager *manager,
    const ThugUiObjectBase *object, const ThugMemory *memory) {
    for (;;) {
        manager->secondary->iteration_bucket = UINT32_MAX;
        manager->secondary->iteration_node = NULL;
        ThugUiObjectBase *found; uint32_t key;
        for (;;) {
            ThugObjectLookupTable *table = manager->secondary;
            if (!thug_object_table_next(table) || !table->iteration_node) return;
            key = table->iteration_node->key;
            found = table->iteration_node->value;
            if (!found) return;
            if (found->object.id == object->object.id) break;
        }
        if ((int32_t)found->alias_count > 0) --found->alias_count;
        thug_object_table_remove(manager->secondary, &key, memory);
    }
}
/* 0x00462980. Lifecycle notifications are log entries, not event dispatch. */
void thug_object_registry_add(ThugEventManager *manager, ThugUiObjectBase *object, const ThugMemory *memory) {
    uint32_t name = object->object.id;
    ThugUiObjectBase *old = thug_object_table_find(manager->objects.secondary, &name, 1);
    if (old) {
        if ((int32_t)old->alias_count > 0) --old->alias_count;
        name = object->object.id;
        thug_object_table_remove(manager->objects.secondary, &name, memory);
    }
    name = object->object.id;
    thug_object_table_insert(manager->objects.primary, &name, object, memory);
    thug_event_log_record(&manager->log, 0, object->object.id, 0x36b2ee74, 0, 0, 4, memory);
}
/* 0x00462a20. Renaming retargets waits; ordinary removal clears aliases. */
void thug_object_registry_remove(ThugEventManager *manager, ThugUiObjectBase *object,
    uint32_t replacement, uint32_t renaming, const ThugMemory *memory) {
    uint32_t name = object->object.id;
    thug_object_table_remove(manager->objects.primary, &name, memory);
    if (!(uint8_t)renaming) thug_object_registry_clear_aliases(&manager->objects, object, memory);
    else for (unsigned i = 0; i < 40; ++i)
        if (manager->waiters[i].target == object->object.id) manager->waiters[i].target = replacement;
    thug_event_log_record(&manager->log, 0, object->object.id, 0x36b2ee74, 0, 0, 5, memory);
}
/* 0x00461930. The old ID's registry entry is changed before writing parameters. */
void thug_ui_object_set_id(ThugUiObjectBase *object, uint32_t name, const ThugMemory *memory) {
    if (object->object.id != thug_object_default_id) {
        ThugObjectManager *manager = (ThugObjectManager *)(uintptr_t)object->object.unknown_8_to_10[1];
        if (manager) manager->methods->rename(manager, object, name, memory);
    }
    object->object.id = name;
    thug_ui_object_ensure_parameters(object, memory);
    thug_script_set_checksum(object->parameters, 0x40c698af, name, memory);
}
/* 0x00461a00. Keep the global manager snapshot across ID assignment. */
void thug_object_manager_add(ThugObjectManager *manager, ThugUiObjectBase *object, const ThugMemory *memory) {
    ThugEventManager *registry = (ThugEventManager *)thug_object_lookup_manager;
    object->object.unknown_8_to_10[1] = (uintptr_t)manager;
    thug_objective_queue_insert(&manager->objects, &object->queue_node);
    manager->cached_id = UINT32_MAX;
    if (object->object.id == UINT32_MAX)
        thug_ui_object_set_id(object, thug_object_registry_next_id(&registry->objects), memory);
    thug_object_registry_add(registry, object, memory);
}
/* 0x00461a50. An already-unlinked node retains manager/cached-ID fields. */
void thug_object_manager_remove(ThugObjectManager *manager, ThugUiObjectBase *object, const ThugMemory *memory) {
    thug_object_registry_remove((ThugEventManager *)thug_object_lookup_manager,
        object, manager->replacement_id, manager->renaming, memory);
    ThugQueueNode *node = &object->queue_node;
    if (node->next != node) {
        node->next->previous = node->previous;
        node->previous->next = node->next;
        node->previous = node->next = node;
        object->object.unknown_8_to_10[1] = 0;
        manager->cached_id = UINT32_MAX;
    }
}
/* 0x004619a0. Both virtual calls execute the concrete manager implementation. */
void thug_object_manager_rename(ThugObjectManager *manager, ThugUiObjectBase *object,
    uint32_t name, const ThugMemory *memory) {
    manager->replacement_id = name; manager->renaming = 1;
    manager->methods->remove(manager, object, memory);
    object->object.id = name;
    manager->methods->add(manager, object, memory);
    manager->renaming = 0;
}
/* 0x004619d0. Re-register with the same ID after changing queue priority. */
void thug_object_manager_set_priority(ThugObjectManager *manager, ThugUiObjectBase *object,
    uint32_t priority, const ThugMemory *memory) {
    uint32_t name = object->object.id;
    object->queue_node.priority = priority;
    manager->methods->rename(manager, object, name, memory);
}
