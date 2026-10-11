#include "ui_manager.h"
#include "skater.h"
#include <stddef.h>
ThugUiManager *thug_ui_manager;
_Static_assert(sizeof(ThugUiManager) == 0x6a4, "UI manager allocation");
_Static_assert(offsetof(ThugUiManager, receiver) == 0x28, "Secondary receiver base");
_Static_assert(offsetof(ThugUiManager, lists) == 0x4dc, "Controller subscription lists");
_Static_assert(offsetof(ThugUiManager, focus) == 0x4ec, "Focus records");
_Static_assert(offsetof(ThugUiManager, pad_event_count) == 0x69c, "Pad event count");
static ThugUiManager *receiver_manager(ThugEventReceiver *receiver) {
    return (ThugUiManager *)((uint8_t *)receiver - 0x28);
}
/* Secondary-base adjustment and service bridges retain the original virtual
 * table layout. They do not add recovered game behavior. */
static void *receiver_delete(ThugEventReceiver *receiver, uint32_t flags, const ThugMemory *memory) {
    return thug_ui_manager_delete(&receiver_manager(receiver)->base,flags,memory);
}
static void receiver_event(ThugEventReceiver *receiver, ThugEvent *event) {
    thug_ui_manager_receive_event(receiver,event,thug_event_services->diagnostics,thug_event_services->memory);
}
const ThugObjectManagerMethods thug_ui_manager_methods = {
    thug_ui_manager_delete,thug_object_manager_add,thug_ui_manager_remove,
    thug_object_manager_rename,thug_object_manager_set_priority,0,0
};
const ThugEventReceiverMethods thug_ui_manager_receiver_methods = {.dispose=receiver_delete,.receive=receiver_event};
/* 0x004ab990. Constructors initialize reference members, not entire records. */
ThugUiManager *thug_ui_manager_initialize(ThugUiManager *manager) {
    thug_object_manager_initialize(&manager->base);
    thug_event_receiver_initialize(&manager->receiver);
    manager->receiver.methods = &thug_ui_manager_receiver_methods;
    manager->base.methods = &thug_ui_manager_methods;
    thug_object_reference_initialize(&manager->root);
    thug_object_reference_initialize(&manager->unknown_50);
    for (uint32_t i = 0; i < 48; ++i) thug_object_reference_initialize(&manager->subscriptions[i].widget);
    for (uint32_t i = 0; i < 10; ++i) thug_object_reference_initialize(&manager->focus[i].widget);
    thug_event_receiver_set_owner(&manager->receiver,NULL);
    for (uint32_t i = 0; i < 2; ++i) { manager->lists[i] = NULL; manager->dirty[i] = 0; }
    for (uint32_t i = 0; i < 48; ++i) manager->subscriptions[i].next = NULL;
    manager->pad_event_count = 0;
    for (uint32_t i = 0; i < 48; ++i) manager->pad_event_types[i] = 0;
    manager->filter_input_device = 0; manager->focus_count = 0;
    for (uint32_t i = 0; i < 10; ++i) manager->focus[i].active = 0;
    return manager;
}
/* 0x004abb00 and 0x004acb40. Widgets are not destroyed by manager teardown. */
void thug_ui_manager_destroy(ThugUiManager *manager) {
    manager->base.methods = &thug_ui_manager_methods;
    manager->receiver.methods = &thug_ui_manager_receiver_methods;
    for (uint32_t i = 10; i; --i) thug_object_reference_destroy(&manager->focus[i-1].widget);
    for (uint32_t i = 48; i; --i) thug_object_reference_destroy(&manager->subscriptions[i-1].widget);
    thug_object_reference_destroy(&manager->unknown_50);
    thug_object_reference_destroy(&manager->root);
    thug_event_receiver_destroy(&manager->receiver);
    thug_object_manager_destroy(&manager->base);
}
ThugObjectManager *thug_ui_manager_delete(ThugObjectManager *manager, uint32_t flags, const ThugMemory *memory) {
    thug_ui_manager_destroy((ThugUiManager *)manager);
    if ((uint8_t)flags & 1) memory->release(memory->context,manager);
    return manager;
}
/* 0x004ab250. The original retains the tail across BOTH lists. Preserve that
 * behavior even when appending a different controller's first subscription. */
void thug_ui_manager_subscribe(ThugUiManager *manager, const ThugObjectReference *widget, uint32_t controller) {
    ThugUiSubscription *last = NULL;
    for (uint32_t i = 0; i < 2; ++i) {
        for (ThugUiSubscription *record = manager->lists[i]; record; record = record->next) {
            if (record->widget.object == widget->object && controller == i) { record->disabled = 0; return; }
            last = record;
        }
    }
    for (uint32_t i = 0; i < 48; ++i) {
        ThugUiSubscription *record = &manager->subscriptions[i];
        if (record->widget.object) continue;
        thug_object_reference_assign(&record->widget,widget->object);
        record->widget_id = widget->object->id; record->next = NULL; record->disabled = 0;
        if (last) last->next = record; else manager->lists[controller] = record;
        manager->dirty[controller] = 1;
        return;
    }
}
static void reference_start(ThugObjectReference *ref, ThugReferencedObject *object) {
    *ref = (ThugObjectReference){object,NULL,NULL};
    if (object) thug_object_reference_link(object,ref);
}
static void reference_parent(ThugObjectReference *ref) {
    ThugUiElement *old = (ThugUiElement *)ref->object;
    thug_object_reference_destroy(ref);
    ref->object = old->parent_reference.object;
    if (ref->object) thug_object_reference_link(ref->object,ref);
}
/* 0x004ab330. Capture the next record before changing either list or references. */
void thug_ui_manager_detach_subscriptions(ThugUiManager *manager, const ThugObjectReference *target,
    uint32_t ancestors_only, uint32_t disable_only) {
    for (uint32_t i = 0; i < 2; ++i) {
        ThugUiSubscription *previous = NULL, *record = manager->lists[i];
        while (record) {
            ThugUiSubscription *next = record->next, *kept = record;
            ThugObjectReference current; reference_start(&current,record->widget.object);
            if ((uint8_t)ancestors_only && current.object) reference_parent(&current);
            while (current.object && current.object != target->object) reference_parent(&current);
            if (current.object) {
                if (!(uint8_t)disable_only) {
                    if (previous) previous->next = next; else manager->lists[i] = next;
                    thug_object_reference_destroy(&record->widget);
                    manager->dirty[i] = 1; kept = previous;
                } else record->disabled = 1;
            }
            thug_object_reference_destroy(&current);
            previous = kept; record = next;
        }
    }
}
/* 0x004ab4d0. Reenabling does not dirty the lists. */
void thug_ui_manager_reenable(ThugUiManager *manager, const ThugObjectReference *target) {
    for (uint32_t i = 0; i < 2; ++i) {
        for (ThugUiSubscription *record = manager->lists[i]; record; record = record->next) {
            if (!record->disabled) continue;
            ThugObjectReference current; reference_start(&current,record->widget.object);
            while (current.object && current.object != target->object) reference_parent(&current);
            if (current.object) record->disabled = 0;
            thug_object_reference_destroy(&current);
        }
    }
}
/* 0x004ab7c0. Focus compares unsigned priorities, including inactive padding. */
uint8_t thug_ui_manager_matches_focus(ThugUiManager *manager, uint32_t id) {
    ThugObjectReference widget; thug_ui_find(&widget,id,1);
    uint32_t owner = thug_ui_owner((ThugUiLayout *)widget.object), maximum = 0;
    for (uint32_t i = 0; i < 10; ++i)
        if (manager->focus[i].active && manager->focus[i].priority > maximum) maximum = manager->focus[i].priority;
    thug_object_reference_destroy(&widget);
    return owner == maximum;
}
/* 0x004aaff0. Search the queue backwards for a replacement root. */
void thug_ui_manager_remove(ThugObjectManager *base, ThugUiObjectBase *object, const ThugMemory *memory) {
    ThugUiManager *manager = (ThugUiManager *)base;
    ThugObjectReference original; reference_start(&original,(ThugReferencedObject *)object);
    if (original.object && manager->root.object == original.object) {
        thug_object_reference_destroy(&manager->root);
        ThugQueueNode *node = base->objects.previous;
        while (node->value != (void *)(uintptr_t)UINT32_MAX) {
            ThugObjectReference candidate; reference_start(&candidate,node->value);
            if (!((ThugUiElement *)candidate.object)->parent && candidate.object != original.object) {
                thug_object_reference_assign_reference(&manager->root,&candidate);
                thug_object_reference_destroy(&candidate); break;
            }
            node = node->previous;
            thug_object_reference_destroy(&candidate);
        }
    }
    thug_object_manager_remove(base,object,memory);
    thug_object_reference_destroy(&original);
}
/* 0x004abbe0. Subscription removal precedes the actual tree attachment. */
void thug_ui_manager_attach(ThugUiManager *manager, const ThugObjectReference *parent,
    const ThugObjectReference *child, uint32_t argument) {
    ThugObjectReference old_parent;
    reference_start(&old_parent,((ThugUiElement *)child->object)->parent_reference.object);
    ThugReferencedObject *new_parent = parent->object;
    if (new_parent && (manager->root.object == child->object || !manager->root.object)) {
        thug_object_reference_assign(&manager->root,new_parent);
        while (((ThugUiElement *)manager->root.object)->parent) reference_parent(&manager->root);
    }
    thug_ui_manager_detach_subscriptions(manager,child,0,0);
    thug_ui_set_parent((ThugUiLayout *)child->object,parent,argument);
    thug_object_reference_destroy(&old_parent);
}
/* 0x004ac400. keep_self retains only the selected widget; all descendants go. */
void thug_ui_manager_delete_tree(ThugUiManager *manager, uint32_t keep_self, const ThugObjectReference *target,
    ThugScriptInstance *caller, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_ui_set_events_enabled((ThugUiElement *)target->object,0,diagnostics,memory);
    ThugObjectReference child; reference_start(&child,((ThugUiElement *)target->object)->children.object);
    while (child.object) {
        ThugObjectReference next; reference_start(&next,((ThugUiElement *)child.object)->next_sibling.object);
        thug_ui_manager_delete_tree(manager,0,&child,caller,diagnostics,memory);
        thug_object_reference_assign_reference(&child,&next);
        thug_object_reference_destroy(&next);
    }
    if (!keep_self) {
        if (caller && target->object) thug_script_detach_owner(caller,target->object);
        ThugObjectReference parent = {0}; thug_ui_manager_attach(manager,&parent,target,1);
        thug_object_reference_destroy(&parent);
        manager->base.methods->remove(&manager->base,(ThugUiObjectBase *)target->object,memory);
        if (target->object) ((const ThugUiObjectMethods *)(uintptr_t)target->object->unknown_0)->dispose(target->object,1,diagnostics,memory);
    }
    thug_object_reference_destroy(&child);
}
/* 0x004ad100. A recursive request disables its parent before descending. */
void thug_ui_manager_delete_id(ThugUiManager *manager, uint32_t id, uint32_t recursive, uint32_t keep_self,
    ThugScriptInstance *caller, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugObjectReference target; thug_ui_find(&target,id,1);
    thug_ui_manager_detach_subscriptions(manager,&target,0,0);
    if (!recursive) {
        if (caller && target.object) thug_script_detach_owner(caller,target.object);
        manager->base.methods->remove(&manager->base,(ThugUiObjectBase *)target.object,memory);
        if (target.object) ((const ThugUiObjectMethods *)(uintptr_t)target.object->unknown_0)->dispose(target.object,1,diagnostics,memory);
    } else {
        ThugUiElement *parent = ((ThugUiElement *)target.object)->parent;
        if (parent) thug_ui_set_events_enabled(parent,0,diagnostics,memory);
        thug_ui_manager_delete_tree(manager,keep_self,&target,caller,diagnostics,memory);
    }
    thug_object_reference_destroy(&target);
}
static uint8_t is_pad_event(const ThugUiManager *manager, uint32_t name) {
    for (uint32_t i = 0; (int32_t)i < (int32_t)manager->pad_event_count; ++i)
        if (manager->pad_event_types[i] == name) return 1;
    return 0;
}
/* 0x004abd40. This entry receives the secondary-base pointer, not the manager.
 * Nested script delivery may mutate lists; dirty lists restart with per-record
 * handled bits. Focus-rejected records bypass the intermediate dirty check. */
void thug_ui_manager_receive_event(ThugEventReceiver *receiver, ThugEvent *event,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugUiManager *manager = receiver_manager(receiver);
    if (!manager->pad_event_count) {
        ThugScriptArray *types = thug_script_get_global_array_text("pad_event_types",1);
        manager->pad_event_count = types->count;
        for (uint32_t i = 0; (int32_t)i < (int32_t)manager->pad_event_count; ++i)
            manager->pad_event_types[i] = (uintptr_t)thug_script_array_structure(types,i);
    }
    uint8_t gated = (int32_t)manager->focus_count > 0 && is_pad_event(manager,event->name);
    uint32_t device;
    if (manager->filter_input_device && event->parameters &&
        thug_script_get_integer(event->parameters,0xc9428a08,&device,0) && device != thug_input_device_id(thug_input_manager,0)) return;
    ThugEventManager *events = (ThugEventManager *)thug_object_lookup_manager;
    if (event->name == 0x9d3fb516 && event->target != 0x36b2ee74) {
        ThugObjectReference target; thug_ui_find(&target,event->target,0);
        if (target.object && !thug_ui_is_input_disabled((ThugUiElement *)target.object)) {
            thug_ui_manager_subscribe(manager,&target,thug_ui_event_controller_index(event));
            thug_event_stop_propagation(event,1,0,memory);
        }
        thug_object_reference_destroy(&target);
    }
    if (event->name == 0x4adf0cd3 && event->target != 0x36b2ee74) {
        ThugObjectReference target; thug_ui_find(&target,event->target,0);
        if (target.object && !thug_ui_is_input_disabled((ThugUiElement *)target.object)) {
            thug_ui_manager_detach_subscriptions(manager,&target,0,0);
            thug_event_stop_propagation(event,1,0,memory);
        }
        thug_object_reference_destroy(&target);
    }
    if (event->name == 0x4a57316b) {
        ThugObjectReference target; thug_ui_find(&target,event->target,0);
        thug_ui_manager_detach_subscriptions(manager,&target,1,1);
        thug_event_stop_propagation(event,1,0,memory);
        thug_object_reference_destroy(&target);
    }
    if (event->name == 0x3056434f) {
        ThugObjectReference target; thug_ui_find(&target,event->target,0);
        thug_ui_manager_reenable(manager,&target);
        thug_event_stop_propagation(event,1,0,memory);
        thug_object_reference_destroy(&target);
    }
    if (!is_pad_event(manager,event->name) || event->target != 0x36b2ee74) return;
    uint32_t controller = thug_ui_event_controller_index(event);
    for (ThugUiSubscription *record = manager->lists[controller]; record; record = record->next) record->handled = 0;
    manager->dirty[controller] = 1;
    do {
        manager->dirty[controller] = 0;
        for (ThugUiSubscription *record = manager->lists[controller]; record; record = record->next) {
            if (!record->handled && !record->disabled && !thug_ui_is_input_disabled((ThugUiElement *)record->widget.object)) {
                if (gated && (!thug_ui_has_inherited_owner((ThugUiElement *)record->widget.object) ||
                    !thug_ui_manager_matches_focus(manager,record->widget_id))) continue;
                if (thug_event_emit(events,event->name,record->widget.object->id,event->source,event->parameters,0,-1,diagnostics,memory)) {
                    thug_event_mark_handled(event,1,0,memory); return;
                }
                record->handled = 1;
            }
            if (manager->dirty[controller]) break;
        }
    } while (manager->dirty[controller]);
}
