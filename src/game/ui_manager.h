#ifndef THUG_GAME_UI_MANAGER_H
#define THUG_GAME_UI_MANAGER_H
#include "object_registry.h"
typedef struct ThugUiSubscription {
    ThugObjectReference widget;
    uint32_t widget_id;
    struct ThugUiSubscription *next;
    uint8_t handled, disabled, padding[2];
} ThugUiSubscription;
typedef struct {
    ThugObjectReference widget;
    uint32_t unknown_c, priority;
    uint8_t active, padding[3];
} ThugUiFocusRecord;
typedef struct {
    ThugObjectManager base;
    ThugEventReceiver receiver;
    ThugObjectReference root, unknown_50;
    ThugUiSubscription subscriptions[48];
    ThugUiSubscription *lists[2];
    uint8_t dirty[2], padding_4e6[2];
    uint32_t focus_count;
    ThugUiFocusRecord focus[10];
    uint32_t pad_event_types[48], pad_event_count;
    uint8_t filter_input_device, padding_6a1[3];
} ThugUiManager;
extern ThugUiManager *thug_ui_manager;
extern const ThugObjectManagerMethods thug_ui_manager_methods;
extern const ThugEventReceiverMethods thug_ui_manager_receiver_methods;
ThugUiManager *thug_ui_manager_initialize(ThugUiManager *);
void thug_ui_manager_destroy(ThugUiManager *);
ThugObjectManager *thug_ui_manager_delete(ThugObjectManager *, uint32_t, const ThugMemory *);
void thug_ui_manager_subscribe(ThugUiManager *, const ThugObjectReference *, uint32_t);
void thug_ui_manager_detach_subscriptions(ThugUiManager *, const ThugObjectReference *, uint32_t ancestors_only, uint32_t disable_only);
void thug_ui_manager_reenable(ThugUiManager *, const ThugObjectReference *);
uint8_t thug_ui_manager_matches_focus(ThugUiManager *, uint32_t);
void thug_ui_manager_remove(ThugObjectManager *, ThugUiObjectBase *, const ThugMemory *);
void thug_ui_manager_attach(ThugUiManager *, const ThugObjectReference *parent, const ThugObjectReference *child, uint32_t);
void thug_ui_manager_delete_tree(ThugUiManager *, uint32_t keep_self, const ThugObjectReference *, ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_manager_delete_id(ThugUiManager *, uint32_t id, uint32_t recursive, uint32_t keep_self, ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_manager_receive_event(ThugEventReceiver *, ThugEvent *, const ThugDiagnostics *, const ThugMemory *);
#endif
