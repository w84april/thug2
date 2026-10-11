#ifndef THUG_GAME_OBJECT_REGISTRY_H
#define THUG_GAME_OBJECT_REGISTRY_H
#include "ui.h"
#include "../script/delivery.h"
typedef struct ThugObjectManager ThugObjectManager;
typedef struct {
    ThugObjectManager *(*dispose)(ThugObjectManager *, uint32_t, const ThugMemory *);
    void (*add)(ThugObjectManager *, ThugUiObjectBase *, const ThugMemory *);
    void (*remove)(ThugObjectManager *, ThugUiObjectBase *, const ThugMemory *);
    void (*rename)(ThugObjectManager *, ThugUiObjectBase *, uint32_t, const ThugMemory *);
    void (*set_priority)(ThugObjectManager *, ThugUiObjectBase *, uint32_t, const ThugMemory *);
    uint32_t unavailable_14, unavailable_18;
} ThugObjectManagerMethods;
struct ThugObjectManager {
    const ThugObjectManagerMethods *methods;
    ThugQueueNode objects;
    uint32_t unknown_18, cached_id, replacement_id;
    uint8_t renaming, padding[3];
};
extern const ThugObjectManagerMethods thug_object_manager_methods;
extern const ThugQueueMethods thug_object_manager_queue_methods;
ThugObjectManager *thug_object_manager_initialize(ThugObjectManager *);
void thug_object_manager_destroy(ThugObjectManager *);
ThugObjectManager *thug_object_manager_delete(ThugObjectManager *, uint32_t, const ThugMemory *);
ThugQueueNode *thug_object_manager_queue_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
uint32_t thug_object_registry_next_id(ThugObjectLookupManager *);
void thug_object_registry_clear_aliases(ThugObjectLookupManager *, const ThugUiObjectBase *, const ThugMemory *);
void thug_object_registry_add(ThugEventManager *, ThugUiObjectBase *, const ThugMemory *);
void thug_object_registry_remove(ThugEventManager *, ThugUiObjectBase *, uint32_t replacement, uint32_t renaming, const ThugMemory *);
void thug_object_manager_add(ThugObjectManager *, ThugUiObjectBase *, const ThugMemory *);
void thug_object_manager_remove(ThugObjectManager *, ThugUiObjectBase *, const ThugMemory *);
void thug_object_manager_rename(ThugObjectManager *, ThugUiObjectBase *, uint32_t, const ThugMemory *);
void thug_object_manager_set_priority(ThugObjectManager *, ThugUiObjectBase *, uint32_t, const ThugMemory *);
void thug_ui_object_set_id(ThugUiObjectBase *, uint32_t, const ThugMemory *);
#endif
