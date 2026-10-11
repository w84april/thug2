#include "runtime.h"
#include "parser.h"
#include "tokens.h"
#include "cache.h"
#include <stddef.h>

_Static_assert(sizeof(ThugScriptLoop) == 16, "Original loop frame");
_Static_assert(sizeof(ThugScriptCallFrame) == 48, "Original call frame");
_Static_assert(offsetof(ThugScriptInstance, loop) == 0x18, "Original loop top");

/* 0x00472a70. Input is inside a switch, after its opening token. Nested
 * switches are skipped recursively, through their matching END_SWITCH. */
void thug_script_skip_switch(ThugScriptInstance *script) {
    while (*script->instruction != 0x3d) {
        if (*script->instruction == 0x3c) { ++script->instruction; thug_script_skip_switch(script); }
        else script->instruction = thug_script_next_token(script->instruction);
    }
    ++script->instruction;
}
/* 0x00473220. The second active loop spills the one-frame inline storage into
 * ten heap frames and relocates loop pointers saved by suspended callers. */
void thug_script_begin_loop(ThugScriptInstance *script, const ThugMemory *memory) {
    ++script->instruction;
    if ((uint8_t *)script->loop == script->local_control_storage) {
        memory->temp_scope(memory->context, 1);
        script->control_storage = memory->allocate(memory->context, 160, 0);
        memory->temp_scope(memory->context, 0);
        for (uint32_t i = 0; i < 16; ++i) script->control_storage[i] = script->local_control_storage[i];
        script->loop = (ThugScriptLoop *)script->control_storage;
        for (uint32_t i = 0; (int32_t)i < (int32_t)script->call_depth; ++i) {
            ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + i * 48);
            if (frame->loop) {
                uint32_t relative = (uintptr_t)frame->loop - (uintptr_t)script->local_control_storage;
                frame->loop = (ThugScriptLoop *)((uintptr_t)script->control_storage + (relative & ~15u));
            }
        }
    }
    script->loop = script->loop ? script->loop + 1 : (ThugScriptLoop *)script->control_storage;
    script->loop->start = script->instruction; script->loop->end = NULL;
    script->loop->finite = 0; script->loop->first_repeat = 1; script->loop->remaining = 0;
}
/* 0x00472ab0. Parse the repeat count only on the first visit. An absent count
 * repeats indefinitely; a literal zero underflows to 0xffffffff on that visit. */
void thug_script_repeat_loop(ThugScriptInstance *script, const ThugMemory *memory) {
    if (script->loop->first_repeat) {
        ++script->instruction;
        thug_script_structure_clear(script->parameters, memory);
        script->loop->end = thug_script_parse_parameters(script->parameters, script->instruction, script->arguments, memory);
        script->loop->finite = thug_script_get_integer(script->parameters, 0, &script->loop->remaining, 0);
        script->loop->first_repeat = 0;
    }
    ThugScriptLoop *loop = script->loop;
    if (!loop->finite || --loop->remaining) { script->instruction = loop->start; return; }
    script->instruction = loop->end;
    script->loop = (uint8_t *)loop == script->control_storage ? NULL : loop - 1;
}
/* 0x00472b50. Skip nested BEGIN/REPEAT pairs, then parse the matching REPEAT's
 * parameters without argument substitution and pop one loop frame. */
void thug_script_break_loop(ThugScriptInstance *script, const ThugMemory *memory) {
    uint32_t depth = 0;
    for (;;) {
        uint8_t token = *script->instruction;
        uint8_t done = token == 0x21 && !depth;
        if (token == 0x20) ++depth;
        else if (token == 0x21 && depth) --depth;
        script->instruction = thug_script_next_token(script->instruction);
        if (done) break;
    }
    thug_script_structure_clear(script->parameters, memory);
    script->instruction = thug_script_parse_parameters(script->parameters, script->instruction, NULL, memory);
    script->loop = (uint8_t *)script->loop == script->control_storage ? NULL : script->loop - 1;
}
/* 0x00473c60. Snapshot the selector before case parsing clears parameters.
 * Case offsets are unsigned 16-bit displacements from their operand address.
 * A selected group still parses subsequent labels before reaching its body. */
void thug_script_select_case(ThugScriptInstance *script, const ThugMemory *memory) {
    ++script->instruction;
    thug_script_structure_clear(script->parameters, memory);
    script->instruction = thug_script_parse_parameters(script->parameters, script->instruction, script->arguments, memory);
    ThugScriptComponent *selector = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
    ThugScriptComponent *first = thug_script_next_component(script->parameters, NULL);
    if (first) thug_script_component_copy(selector, first, 0, memory);
    for (;;) {
        const uint8_t *p = script->instruction;
        if (*p == 0x3c) { ++script->instruction; thug_script_skip_switch(script); }
        else if (*p == 0x3e) {
            script->instruction += 2;
            const uint8_t *next_case = script->instruction + thug_script_read_half(script->instruction);
            script->instruction += 2;
            thug_script_structure_clear(script->parameters, memory);
            script->instruction = thug_script_parse_parameters(script->parameters, script->instruction, script->arguments, memory);
            first = thug_script_next_component(script->parameters, NULL);
            if (first && thug_script_component_equal(selector, first)) {
                script->instruction = thug_script_skip_lines(script->instruction);
                while (*script->instruction == 0x49 && script->instruction[3] == 0x3e) {
                    script->instruction += 7;
                    thug_script_structure_clear(script->parameters, memory);
                    script->instruction = thug_script_parse_parameters(script->parameters, script->instruction, script->arguments, memory);
                    script->instruction = thug_script_skip_lines(script->instruction);
                }
                break;
            }
            script->instruction = next_case;
        } else if (*p == 0x3f) { script->instruction += 4; break; }
        else if (*p == 0x3d) { ++script->instruction; break; }
        else if (*p != 0x24) script->instruction = thug_script_next_token(p);
    }
    thug_script_component_clear(selector, memory);
    memory->release(memory->context, selector);
}
/* 0x00473e70. Release the callee's cache reference, restore a caller if one
 * exists, then merge returned values. With no caller, only instruction is
 * cleared. Return the callee's incoming flag bit 0, not the restored flag. */
uint8_t thug_script_return(ThugScriptInstance *script, const ThugScriptStructure *values, const ThugMemory *memory) {
    thug_script_cache_release(thug_script_cache, script->checksum, memory);
    uint8_t result = script->flags & 1;
    if (!script->call_depth) script->instruction = NULL;
    else {
        ThugScriptStructure *arguments = script->arguments;
        --script->call_depth;
        if (arguments) { thug_script_structure_destroy(arguments, memory); thug_script_structure_free(arguments, memory); }
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + script->call_depth * 48);
        script->checksum = frame->checksum; script->arguments = frame->arguments; script->instruction = frame->instruction;
        ThugReferencedObject *owner = frame->owner;
        if (script->owner.object) { thug_object_reference_unlink(script->owner.object, &script->owner); script->owner.object = NULL; }
        script->owner.object = owner;
        if (owner) thug_object_reference_link(owner, &script->owner);
        script->loop = frame->loop; script->unknown_e8 = frame->deferred_checksum;
        script->wait_type = frame->wait_type_bits & 15;
        if (script->wait_type) {
            script->wait_frames = frame->wait_frames;
            uint8_t *bits = (uint8_t *)&script->wait_remaining;
            for (uint32_t i = 0; i < 4; ++i) bits[i] = frame->wait_remaining_bits >> (i * 8);
            script->waited = frame->flags & 1;
            script->wait_owner = frame->wait_owner; script->wait_argument = frame->wait_argument;
        }
        script->flags = (script->flags & ~1u) | ((frame->flags >> 1) & 1);
    }
    if (values) thug_script_structure_merge_optional(script->arguments, values, memory);
    return result;
}
