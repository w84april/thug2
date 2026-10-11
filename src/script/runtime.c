#include "runtime.h"
/* 0x00473be0. Saved frame owners are raw pointers; only the current owner is
 * an intrusive reference. A null argument does not clear the wait. */
void thug_script_detach_owner(ThugScriptInstance *script, const ThugReferencedObject *owner) {
    if (!owner) return;
    if (script->owner.object == owner) thug_object_reference_destroy(&script->owner);
    for (uint32_t i = 0; (int32_t)i < (int32_t)script->call_depth; ++i) {
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + i * 48);
        if (frame->owner == owner) frame->owner = 0;
    }
    script->wait_type = 0;
}
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>
/* 0x00472f00. Cancel deferred calls in the active and every saved frame. */
void thug_script_clear_deferred(ThugScriptInstance *script) {
    uint32_t count = script->call_depth;
    script->unknown_e8 = 0;
    while (count) {
        --count;
        ((ThugScriptCallFrame *)script->call_storage)[count].deferred_checksum = 0;
    }
}
/* 0x00472e20 and 0x004734b0. Return the first list match. */
ThugScriptInstance *thug_script_find_spawned(uint32_t user_value) {
    for (ThugScriptInstance *script = thug_script_list; script; script = script->next)
        if ((script->flags_cc & 1) && script->unknown_d4 == user_value) return script;
    return NULL;
}
ThugScriptInstance *thug_script_find_serial(uint32_t serial) {
    for (ThugScriptInstance *script = thug_script_list; script; script = script->next)
        if (script->serial == serial) return script;
    return NULL;
}
/* 0x00472ed0 and 0x00472ee0. Event replacement consumes this pending name. */
void thug_script_set_interrupt_checksum(ThugScriptInstance *script, uint32_t name) { script->unknown_e4 = name; }
uint32_t thug_script_get_interrupt_checksum(const ThugScriptInstance *script) { return script->unknown_e4; }

_Static_assert(sizeof(ThugScriptInstance) == 0xf4, "Script instance layout");
_Static_assert(offsetof(ThugScriptInstance, instruction) == 0xc, "Script instruction offset");
_Static_assert(offsetof(ThugScriptInstance, control_storage) == 0x2c, "Script control storage");
_Static_assert(offsetof(ThugScriptInstance, call_storage) == 0x94, "Script call storage");
_Static_assert(offsetof(ThugScriptInstance, wait_type) == 0xa4, "Script wait type");
_Static_assert(offsetof(ThugScriptInstance, owner) == 0xbc, "Script owner reference");
_Static_assert(offsetof(ThugScriptWaitMethods, update_wait) == 0x18, "Wait method slot");
ThugScriptInstance *thug_current_script, *thug_script_list;
uint32_t thug_script_count, thug_script_next_serial;
uint8_t thug_script_wait_gate;

/* 0x004728c0, 0x004728d0. A null iterator starts at the list head. */
ThugScriptInstance *thug_script_current(void) { return thug_current_script; }
ThugScriptInstance *thug_script_next(const ThugScriptInstance *script) {
    return script ? script->next : thug_script_list;
}

/* 0x004738e0. The original initializes two embedded objects, then REP STOSD
 * clears all 244 bytes, including their temporary vtable/reference writes.
 * This is a constructor for an unlinked instance, not a reset of a live script. */
ThugScriptInstance *thug_script_initialize(ThugScriptInstance *script) {
    uint8_t *bytes = (uint8_t *)script;
    for (unsigned i = 0; i < sizeof(*script); ++i) bytes[i] = 0;
    script->next = thug_script_list;
    if (thug_script_list) thug_script_list->previous = script;
    script->serial = thug_script_next_serial;
    ++thug_script_count;
    ++thug_script_next_serial;
    script->call_storage = script->local_call_storage;
    script->control_storage = script->local_control_storage;
    thug_script_list = script;
    return script;
}

/* 0x00472940, 0x004728f0. Clearing the wait does not reset its other fields. */
uint8_t thug_script_has_instruction(const ThugScriptInstance *script) {
    return script->instruction != NULL;
}
void thug_script_clear_wait(ThugScriptInstance *script) { script->wait_type = 0; }

/* 0x004739a0. The owner is required. Preserve the order of the three script
 * writes and the final owner flag, including overlapping input objects. */
void thug_script_set_object_wait(ThugScriptInstance *script, uint32_t type,
    ThugScriptWaitOwner *owner, uint32_t argument) {
    script->wait_type = type;
    script->wait_owner = owner;
    script->wait_argument = argument;
    owner->flags |= 2;
}

/* 0x00473050. This updates wait state; it does not execute a script token. */
void thug_script_update_wait(ThugScriptInstance *script) {
    switch (script->wait_type) {
    case 1:
    case 11:
        if (script->wait_frames) { --script->wait_frames; return; }
        if (script->wait_type == 11) {
            if (thug_script_wait_gate) return;
            thug_script_wait_gate = 1;
        }
        script->wait_type = 0;
        return;
    case 2: {
        double duration = thug_frame_duration();
        /* FCOM's equality OR unordered test takes the subtraction branch. */
        if (!(duration > script->wait_remaining)) {
            script->waited = 1;
            script->wait_remaining = (float)thug_platform_round_x87_single(
                (double)script->wait_remaining - duration);
        } else if (!script->waited) {
            script->wait_remaining = 0;
            script->waited = 1;
        } else {
            script->wait_type = 0;
            script->waited = 1;
        }
        return;
    }
    case 4: {
        uint32_t elapsed = thug_elapsed_time() + thug_timer_offset - script->wait_argument;
        double number = (int32_t)elapsed;
        if ((int32_t)elapsed < 0)
            number = thug_platform_round_x87_single(number + 0x1p32);
        if (number >= script->wait_remaining) script->wait_type = 0;
        return;
    }
    case 5: case 6: case 7: case 8: case 9: case 10:
        script->wait_owner->methods->update_wait(script->wait_owner, script, script->wait_argument);
        return;
    default:
        return;
    }
}
