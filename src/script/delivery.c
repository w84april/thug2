#include "delivery.h"
#include "operators.h"
#include "schedule.h"
#include "../core/checksum.h"
#include "../core/vector.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(sizeof(ThugEvent) == 20, "Original event");
_Static_assert(offsetof(ThugEventLog, names) == 0x7005, "Unaligned event names");
_Static_assert(offsetof(ThugEventLog, name_table) == 0xb008, "Event name table");
_Static_assert(sizeof(ThugEventLog) == 0xb014, "Original event log");
_Static_assert(offsetof(ThugEventManager, log) == 0x20, "Event log offset");
_Static_assert(offsetof(ThugEventManager, waiters) == 0xb038, "Event waiters");
_Static_assert(offsetof(ThugScriptObjectMethods, receive_event) == 0x14, "Object event method");

const char thug_event_log_separator[] = "========================================================\n";
const char thug_event_log_title[] = "PRINTING EVENT LOG\n\n";
const char thug_event_log_new_title[] = "PRINTING EVENT LOG (ONLY NEW ENTRIES)\n\n";
const ThugEventServices *thug_event_services;
const ThugEventReceiverMethods thug_event_receiver_methods = {.dispose = thug_event_receiver_delete};
/* 0x0045faa0. The next pointer and high bytes of the active word are retained. */
ThugEventReceiver *thug_event_receiver_initialize(ThugEventReceiver *receiver) {
    receiver->methods = &thug_event_receiver_methods;
    thug_object_reference_initialize(&receiver->owner);
    receiver->unknown_14 &= 0xffffff00;
    receiver->active_calls = 0;
    return receiver;
}
/* 0x00461fe0 and 0x00462000. Unregistration leaves the removed next link intact. */
void thug_event_receiver_register(ThugEventManager *manager, ThugEventReceiver *receiver) {
    receiver->next = manager->receivers; manager->receivers = receiver;
    receiver->unknown_14 = (receiver->unknown_14 & 0xffffff00) | 1;
}
void thug_event_receiver_unregister(ThugEventManager *manager, ThugEventReceiver *receiver) {
    ThugEventReceiver **link = &manager->receivers;
    while (*link && *link != receiver) link = &(*link)->next;
    if (*link) *link = receiver->next;
    receiver->unknown_14 &= 0xffffff00;
}
/* 0x0045fb30, 0x0045fac0 and 0x00460170. */
void thug_event_receiver_set_owner(ThugEventReceiver *receiver, ThugReferencedObject *owner) {
    thug_object_reference_assign(&receiver->owner, owner);
    thug_event_receiver_register((ThugEventManager *)thug_object_lookup_manager, receiver);
}
void thug_event_receiver_destroy(ThugEventReceiver *receiver) {
    receiver->methods = &thug_event_receiver_methods;
    thug_event_receiver_unregister((ThugEventManager *)thug_object_lookup_manager, receiver);
    thug_object_reference_destroy(&receiver->owner);
}
void *thug_event_receiver_delete(ThugEventReceiver *receiver, uint32_t flags, const ThugMemory *memory) {
    thug_event_receiver_destroy(receiver);
    if ((uint8_t)flags & 1) memory->release(memory->context, receiver);
    return receiver;
}
/* 0x00462b40 and 0x0045f980. Stop and handled are distinct flags/log phases. */
void thug_event_record_stopped(ThugEventManager *manager, const ThugEvent *event,
    uint32_t kind, uint32_t script, const ThugMemory *memory) {
    thug_event_log_record(&manager->log,event->name,event->target,event->source,script,kind,2,memory);
}
void thug_event_stop_propagation(ThugEvent *event, uint32_t kind, uint32_t script, const ThugMemory *memory) {
    thug_event_record_stopped((ThugEventManager *)thug_object_lookup_manager,event,kind,script,memory);
    event->flags |= 1;
}
/* 0x0045f9e0. */
uint32_t thug_ui_event_controller_index(const ThugEvent *event) {
    uint32_t controller = 0;
    if (event->parameters) thug_script_get_integer(event->parameters,0xb30d9965,&controller,0);
    return controller;
}

/* 0x0045f7f0. Parameters are borrowed unless a recipient sets flag 4. */
void thug_event_initialize(ThugEvent *event, uint32_t name, uint32_t source,
    uint32_t target, ThugScriptStructure *parameters) {
    event->name = name; event->source = source; event->target = target;
    event->flags = 0; event->parameters = parameters;
}
/* 0x00460150. Retain the original fields after releasing owned parameters. */
void thug_event_destroy(ThugEvent *event, const ThugMemory *memory) {
    if ((event->flags & 4) && event->parameters) {
        thug_script_structure_destroy(event->parameters, memory);
        thug_script_structure_free(event->parameters, memory);
    }
}
/* 0x004627c0. Lazy names, ring wrap, signed previous-index fallback and phase-3
 * coalescing are separate from handled-event kind. Depth can underflow. */
void thug_event_log_record(ThugEventLog *log, uint32_t event, uint32_t target, uint32_t source,
    uint32_t script, uint32_t kind, uint32_t phase, const ThugMemory *memory) {
    if (!log->name_table) {
        ThugObjectLookupTable *table = memory->allocate(memory->context, sizeof(*table), 1);
        if (table) thug_object_table_initialize(table, 8, memory);
        log->name_table = table;
        ThugScriptArray *names = thug_script_get_global_array(0x08114f90, 1);
        for (uint32_t i = 0; (int32_t)i < (int32_t)names->count; ++i) {
            const char *source_name = thug_script_array_text(names, i);
            char *out = log->names[i];
            do { *out++ = *source_name; } while (*source_name++);
            uint32_t key = thug_crc32_string(thug_script_array_text(names, i));
            thug_object_table_insert(log->name_table, &key, log->names[i], memory);
        }
    }
    uint32_t previous = log->next_index - 1;
    if ((int32_t)previous < 0) previous = 1023;
    if (phase == 3 && log->entries[previous].phase == 3) { ++log->entries[previous].event; return; }
    if (phase == 1) --log->depth;
    ThugEventLogEntry *entry = &log->entries[log->next_index];
    entry->phase = phase; entry->event = phase == 3 ? 0 : event;
    entry->target = target; entry->source = source; entry->script = script;
    entry->kind = kind; entry->depth = log->depth;
    if (++log->next_index == 1024) { log->next_index = 0; log->wrapped = 1; }
    if (phase == 0) ++log->depth;
    ++log->new_count;
}
/* 0x004620a0. This specimen prints only the headers; entry formatting was
 * compiled out. Its unused second argument remains part of the calling ABI. */
void thug_event_log_print(ThugEventLog *log, uint32_t new_only, uint32_t unused, const ThugDiagnostics *diagnostics) {
    (void)unused;
    diagnostics->print(diagnostics->context, thug_event_log_separator);
    diagnostics->print(diagnostics->context, (uint8_t)new_only ? thug_event_log_new_title : thug_event_log_title);
    diagnostics->print(diagnostics->context, thug_event_log_separator);
    log->new_count = 0;
}
/* 0x00462b10 and 0x0045f9b0. Recording precedes the handled-bit write. */
void thug_event_record_handled(ThugEventManager *manager, const ThugEvent *event,
    uint32_t kind, uint32_t script, const ThugMemory *memory) {
    thug_event_log_record(&manager->log, event->name, event->target, event->source, script, kind, 1, memory);
}
void thug_event_mark_handled(ThugEvent *event, uint32_t kind, uint32_t script, const ThugMemory *memory) {
    thug_event_record_handled((ThugEventManager *)thug_object_lookup_manager, event, kind, script, memory);
    event->flags |= 2;
}
/* 0x004a1090. The receiver's concrete virtual handler belongs to the engine. */
void thug_event_receiver_dispatch(ThugEventReceiver *receiver, ThugEvent *event) { receiver->methods->receive(receiver, event); }

static ThugScriptStructure *new_parameters(const ThugMemory *memory) {
    ThugScriptStructure *structure = thug_script_structure_allocate(8, memory);
    if (structure) thug_script_structure_initialize(structure);
    return structure;
}
static void dispose_parameters(ThugScriptStructure *structure, const ThugMemory *memory) {
    if (structure) { thug_script_structure_destroy(structure, memory); thug_script_structure_free(structure, memory); }
}
/* 0x00460470. A callback may disable handlers, stop iteration, or retire the
 * table. Keep the entry cursor but re-read count, flags and script names at the
 * same points as the original; nested deliveries retain the stop flag. */
void thug_script_events_deliver(ThugScriptEventTable *table, ThugEvent *event,
    ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t old_stop = table->stop_iteration;
    ThugScriptEventEntry *entry = table->entries;
    table->stop_iteration = 0; ++table->active_calls;
    for (uint32_t i = 0; (int32_t)i < (int32_t)table->count; ++i) {
        if (entry->event == event->name && entry->script != 0xc377c572) {
            ThugScriptStructure *merged = NULL, *arguments = entry->parameters;
            if (event->parameters) {
                arguments = merged = new_parameters(memory);
                if (entry->parameters) thug_script_structure_merge(arguments, entry->parameters, memory);
                thug_script_structure_merge(arguments, event->parameters, memory);
            }
            if (!(entry->flags & 1)) {
                ThugReferencedObject *owner = script->owner.object;
                if (!owner || !(owner->unknown_8_to_10[0] & 0x10000))
                    thug_script_run_immediate(script, entry->script, arguments, diagnostics, memory);
                else {
                    ThugScriptInstance *spawned = thug_script_spawn(entry->script, arguments, 0, NULL, 0, 0, 0, 0, 0, 0, diagnostics, memory);
                    thug_object_reference_destroy(&spawned->owner);
                    spawned->owner.object = script->owner.object;
                    if (spawned->owner.object) thug_object_reference_link(spawned->owner.object, &spawned->owner);
                    thug_script_execute(spawned, diagnostics, memory);
                }
            } else {
                if (thug_script_get_interrupt_checksum(script)) {
                    ThugScriptStructure *interrupt = new_parameters(memory);
                    thug_script_set_scalar(interrupt, 0, 13, entry->flags & 1, memory);
                    uint32_t name = thug_script_get_interrupt_checksum(script);
                    thug_script_set_interrupt_checksum(script, 0);
                    thug_script_run_immediate(script, name, interrupt, diagnostics, memory);
                    dispose_parameters(interrupt, memory);
                }
                if (entry->script != 0xc377c572) {
                    thug_script_setup_named(script, entry->script, arguments, script->owner.object, diagnostics, memory);
                    thug_script_execute(script, diagnostics, memory);
                }
            }
            dispose_parameters(merged, memory);
            thug_event_record_handled((ThugEventManager *)thug_object_lookup_manager, event, 0, entry->script, memory);
            event->flags |= 2;
        }
        ++entry;
        if (!table->alive) {
            if (!--table->active_calls) { thug_script_events_destroy(table, memory); memory->release(memory->context, table); }
            return;
        }
        if (table->stop_iteration) break;
    }
    table->stop_iteration = !!(table->stop_iteration || old_stop);
    --table->active_calls;
}
/* 0x00473800. Wake event waits in the active frame and every saved frame,
 * preserving the high 28 bits of each saved wait-type word. */
uint32_t thug_script_receive_event(ThugScriptInstance *script, ThugEvent *event,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (script->wait_type == 3 && script->wait_argument && script->wait_argument == event->name) script->wait_type = 0;
    for (uint32_t i = 0; (int32_t)i < (int32_t)script->call_depth; ++i) {
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + i * 48);
        if ((frame->wait_type_bits & 15) == 3 && frame->wait_argument && frame->wait_argument == event->name)
            frame->wait_type_bits &= 0xfffffff0;
    }
    if (script->events) thug_script_events_deliver(script->events, event, script, diagnostics, memory);
    return 1;
}
static uint8_t within_radius(ThugScriptInstance *script, float radius, const float source[4]) {
    ThugReferencedObject *owner = script->owner.object;
    if (!(radius >= 0) || !owner || !(owner->unknown_8_to_10[0] & 0x20)) return 1;
    return thug_vector_distance_squared(source, (const float *)((const uint8_t *)owner + 0x4c)) <
        thug_platform_round_x87_single((double)radius * radius);
}
/* 0x00462f00. Broadcast snapshots protect each script with the original
 * intrusive reference, so earlier handlers may delete later recipients. The
 * one-recipient fast path intentionally avoids snapshot allocations. */
uint8_t thug_event_emit(ThugEventManager *manager, uint32_t name, uint32_t target, uint32_t source,
    ThugScriptStructure *parameters, uint32_t broadcast, float radius,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const ThugEventServices services = {diagnostics, memory}, *previous_services = thug_event_services;
    thug_event_services = &services;
    ++manager->dispatch_depth;
    thug_event_log_record(&manager->log, name, target, source, manager->source_script, 0, 0, memory);
    manager->source_script = 0;
    ThugEvent event; thug_event_initialize(&event, name, source, target, parameters);
    if (!(uint8_t)broadcast) {
        for (ThugEventReceiver *receiver = manager->receivers; receiver; receiver = receiver->next) {
            ++receiver->active_calls; thug_event_receiver_dispatch(receiver, &event); --receiver->active_calls;
        }
        if (event.target != 0x36b2ee74 && !(event.flags & 2)) {
            void *object = thug_object_manager_find(&manager->objects, event.target);
            if (object) (*(const ThugScriptObjectMethods **)object)->receive_event(object, &event);
            else {
                ThugScriptInstance *script = thug_script_find_spawned(event.target);
                if (!script) thug_event_log_print(&manager->log, 1, 1024, diagnostics);
                thug_script_receive_event(script, &event, diagnostics, memory);
            }
        }
    } else {
        ThugScriptListener *list = thug_object_table_find(manager->objects.listeners, &name, 1);
        if (list) {
            float position[4];
            if (radius >= 0) {
                const uint32_t *original = (const uint32_t *)((const uint8_t *)thug_object_find_global(NULL, source) + 0x4c);
                for (unsigned i = 0; i < 4; ++i) __builtin_memcpy(&position[i], &original[i], 4);
            }
            uint32_t count = 0;
            for (ThugScriptListener *node = list->next; node->value != UINT32_MAX; node = node->next) ++count;
            if (count == 1) {
                ThugScriptInstance *script = (ThugScriptInstance *)(uintptr_t)list->next->value;
                if (within_radius(script, radius, position)) thug_script_receive_event(script, &event, diagnostics, memory);
            } else {
                ThugScriptInstance **scripts = memory->allocate(memory->context, count * 4, 1);
                uint32_t *allocation = memory->allocate(memory->context, count * 12 + 4, 1);
                ThugObjectReference *references = NULL;
                if (allocation) {
                    *allocation = count; references = (ThugObjectReference *)(allocation + 1);
                    for (uint32_t i = 0; i < count; ++i) thug_object_reference_initialize(references + i);
                }
                uint32_t i = 0;
                for (ThugScriptListener *node = list->next; node->value != UINT32_MAX; node = node->next, ++i) {
                    scripts[i] = (ThugScriptInstance *)(uintptr_t)node->value;
                    thug_object_reference_destroy(references + i);
                    references[i].object = (ThugReferencedObject *)&scripts[i]->reference_target;
                    thug_object_reference_link(references[i].object, references + i);
                }
                for (i = 0; (int32_t)i < (int32_t)count; ++i)
                    if (references[i].object && within_radius(scripts[i], radius, position))
                        thug_script_receive_event(scripts[i], &event, diagnostics, memory);
                if (references) {
                    for (i = *allocation; i; --i) thug_object_reference_destroy(references + i - 1);
                    memory->release(memory->context, allocation);
                }
                memory->release(memory->context, scripts);
            }
        }
    }
    for (uint32_t i = 0; i < 40; ++i) {
        ThugEventWaiter *waiter = manager->waiters + i;
        if (waiter->event == name && (waiter->target == target || !waiter->target || target == 0x36b2ee74 || (uint8_t)broadcast)) {
            waiter->event = 0;
            ThugScriptInstance *script = thug_script_find_serial(waiter->serial);
            if (script) { thug_script_clear_wait(script); thug_event_mark_handled(&event, 2, script->checksum, memory); break; }
        }
    }
    if (!(event.flags & 2)) thug_event_log_record(&manager->log, event.name, event.target, event.source, 0, 3, 1, memory);
    --manager->dispatch_depth;
    thug_event_destroy(&event, memory);
    thug_event_services = previous_services;
    return (event.flags >> 1) & 1;
}
/* 0x004609f0. Object events use the same identity for source and target. */
void thug_object_emit_event(ThugReferencedObject *owner, uint32_t name, ThugScriptStructure *parameters,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_event_emit((ThugEventManager *)thug_object_lookup_manager, name, owner->id, owner->id, parameters, 0, -1, diagnostics, memory);
}
/* 0x00460a20. The original consumes three arguments but ignores the third. */
void thug_object_broadcast_event(ThugReferencedObject *owner, uint32_t name, ThugScriptStructure *parameters,
    uint32_t unused, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)unused;
    thug_event_emit((ThugEventManager *)thug_object_lookup_manager, name, UINT32_MAX, owner->id, parameters, 1, -1, diagnostics, memory);
}
