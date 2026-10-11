#include "execute.h"
#include "tokens.h"
#include "load.h"
#include "events.h"
#include "delivery.h"
#include "../game/skater.h"
#include <stddef.h>
/* 0x004747a0. Resolve the named cached program through the full setup path. */
void thug_script_setup_named(ThugScriptInstance *script, uint32_t name,
    const ThugScriptStructure *arguments, ThugReferencedObject *owner,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_setup(script, name, NULL, arguments, owner, diagnostics, memory);
}

char thug_script_unknown_name[20];
const char thug_script_missing_format[] = "WARNING: script %s not found, ignoring in default level.\n";
_Static_assert(offsetof(ThugScriptObjectMethods, descriptor) == 8, "Object descriptor slot");
_Static_assert(offsetof(ThugScriptObjectMethods, checksum) == 12, "Object member slot");
_Static_assert(offsetof(ThugScriptComponentMethods, descriptor) == 44, "Component descriptor slot");
/* 0x0046d0c0. Read at most ten names in the checksum's debug bucket. */
const char *thug_script_debug_name(uint32_t name) {
    if (!thug_script_debug_enabled) return NULL;
    ThugScriptDebugName *entry = thug_script_debug_names + (name & 0xffff) * 10;
    for (uint32_t i = 0; i < 10; ++i, ++entry) {
        if (!entry->text) return NULL;
        if (entry->name == name) return entry->text;
    }
    return NULL;
}
/* 0x0046d110. The fixed original sprintf format produces exactly 19 bytes and
 * a NUL. Preserve its shared overwrite-on-miss buffer, without a Windows CRT. */
const char *thug_script_name_text(uint32_t name) {
    const char *text = thug_script_debug_name(name);
    if (text) return text;
    const char prefix[] = "Unknown(0x";
    for (uint32_t i = 0; i < 10; ++i) thug_script_unknown_name[i] = prefix[i];
    for (uint32_t i = 0; i < 8; ++i) thug_script_unknown_name[10+i] = "0123456789abcdef"[(name >> (28-i*4)) & 15];
    thug_script_unknown_name[18] = ')'; thug_script_unknown_name[19] = 0;
    return thug_script_unknown_name;
}
/* 0x00460ad0. Unlike 4619f0, this wrapper has no unused this argument. */
void *thug_script_find_object(uint32_t name) { return thug_object_manager_find(thug_object_lookup_manager, name); }
/* 0x00472950. Parameter storage is reused for every command. */
void thug_script_read_parameters(ThugScriptInstance *script, const ThugMemory *memory) {
    thug_script_structure_clear(script->parameters, memory);
    script->instruction = thug_script_parse_parameters(script->parameters, script->instruction, script->arguments, memory);
}
/* 0x004729e0. An unsupported token returns zero without moving the cursor. */
uint32_t thug_script_read_name(ThugScriptInstance *script) {
    const uint8_t *p = script->instruction; uint32_t name = 0;
    if (*p == 0x16) { script->instruction = p+1; name = thug_script_read_word(script->instruction); script->instruction += 4; }
    else if (*p == 0x2c) { ++script->instruction; thug_script_get_checksum(script->arguments, 0, &name, 0); }
    else if (*p == 0x2d) {
        script->instruction += 2; uint32_t argument = thug_script_read_word(script->instruction); script->instruction += 4;
        thug_script_get_checksum(script->arguments, argument, &name, 0);
    }
    return name;
}
/* 0x00472980. Object handlers return a byte; component handlers return a word.
 * Missing required components retain the original unchecked contract. */
uint8_t thug_script_dispatch_descriptor(const ThugScriptCommand *command, ThugScriptStructure *parameters, void *owner, ThugScriptInstance *script) {
    if (command->component_type == 0x57525413 || command->component_type == 0x0ada4e74)
        return (uint8_t)(*(const ThugScriptObjectMethods **)owner)->descriptor(owner, command, parameters, script) != 0;
    ThugObjectComponent *component = thug_object_find_component(owner, command->component_type);
    return (*(const ThugScriptComponentMethods **)component)->descriptor(component, command, parameters, script) != 0;
}
/* 0x004731a0, 0x004731e0. A null explicit target falls back to the script owner. */
uint8_t thug_script_call_descriptor(ThugScriptInstance *script, const ThugScriptCommand *command, void *owner) {
    if (!owner) owner = script->owner.object;
    if (owner) return thug_script_dispatch_descriptor(command, script->parameters, owner, script);
    thug_network_is_active(thug_network_state); return 0;
}
uint8_t thug_script_call_member(ThugScriptInstance *script, uint32_t name, void *owner) {
    if (!owner) owner = script->owner.object;
    if (owner) return (*(const ThugScriptObjectMethods **)owner)->checksum(owner, name, script->parameters, script);
    thug_network_is_active(thug_network_state); return 0;
}
/* 0x00473880. Clear each deferred name before running it. Suspended callers
 * execute in reverse order, using the initially captured depth. */
void thug_script_run_deferred(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint32_t name = script->unknown_e8;
    if (name) { script->unknown_e8 = 0; thug_script_run_immediate(script, name, NULL, diagnostics, memory); }
    for (uint32_t i = script->call_depth; i; --i) {
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + (i-1)*48);
        name = frame->deferred_checksum;
        if (name) { frame->deferred_checksum = 0; thug_script_run_immediate(script, name, NULL, diagnostics, memory); }
    }
}
static void destroy_structure(ThugScriptStructure *s, const ThugMemory *memory) {
    if (s) { thug_script_structure_destroy(s, memory); thug_script_structure_free(s, memory); }
}
/* 0x00473a80. Deferred scripts run before owned state or stack storage is freed. */
void thug_script_cleanup(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_run_deferred(script, diagnostics, memory);
    if (script->unknown_8) { memory->release(memory->context, (void *)(uintptr_t)script->unknown_8); script->unknown_8 = 0; }
    if (script->instruction) thug_script_cache_release(thug_script_cache, script->checksum, memory);
    script->instruction = NULL;
    destroy_structure(script->arguments, memory); script->arguments = NULL;
    destroy_structure(script->parameters, memory); script->parameters = NULL;
    for (uint32_t i = 0; (int32_t)i < (int32_t)script->call_depth; ++i) {
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + i*48);
        thug_script_cache_release(thug_script_cache, frame->checksum, memory);
        if (frame->arguments) { destroy_structure(frame->arguments, memory); ((ThugScriptCallFrame *)(script->call_storage + i*48))->arguments = NULL; }
    }
    script->call_depth = 0;
    if (script->call_storage != script->local_call_storage && script->call_storage) memory->release(memory->context, script->call_storage);
    script->call_storage = script->local_call_storage; script->loop = NULL;
    if (script->control_storage != script->local_control_storage && script->control_storage) memory->release(memory->context, script->control_storage);
    script->control_storage = script->local_control_storage;
    script->wait_frames = 0; script->wait_type = 0; script->wait_owner = NULL; script->wait_argument = 0;
    if (script->owner.object) thug_object_reference_unlink(script->owner.object, &script->owner);
    script->owner.object = NULL; script->checksum = 0; script->flags &= 0xfc;
}
/* 0x00474540. Aliased arguments are copied before cleaning up the old script. */
void thug_script_setup(ThugScriptInstance *script, uint32_t name, const uint8_t *program,
    const ThugScriptStructure *arguments, ThugReferencedObject *owner, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptStructure *snapshot = thug_script_snapshot_arguments(script, arguments, memory);
    thug_script_cleanup(script, diagnostics, memory);
    script->parameters = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
    script->checksum = name;
    if (script->owner.object) { thug_object_reference_unlink(script->owner.object, &script->owner); script->owner.object = NULL; }
    script->owner.object = owner;
    if (owner) thug_object_reference_link(owner, &script->owner);
    script->arguments = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
    script->instruction = program ? program : thug_script_cache_acquire(thug_script_cache, name, memory);
    if (!program && !script->instruction) {
        destroy_structure(snapshot, memory); thug_script_cleanup(script, diagnostics, memory); thug_script_clear_events(script, memory); return;
    }
    script->instruction = thug_script_parse_parameters(script->arguments, script->instruction, NULL, memory);
    thug_script_structure_merge_optional(script->arguments, snapshot ? snapshot : arguments, memory);
    destroy_structure(snapshot, memory);
}
/* 0x004748e0. The third suspended call spills two inline frames into sixteen
 * heap frames. Preserve packed wait/flag padding and raw floating-point bits. */
void thug_script_push_call(ThugScriptInstance *script, uint32_t name, const uint8_t *program,
    const ThugScriptStructure *arguments, ThugReferencedObject *owner, uint32_t immediate,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!script->instruction) thug_script_setup(script, name, program, arguments, owner, diagnostics, memory);
    else {
        if (script->call_storage == script->local_call_storage && script->call_depth == 2) {
            memory->temp_scope(memory->context, 1); script->call_storage = memory->allocate(memory->context, 768, 0); memory->temp_scope(memory->context, 0);
            for (uint32_t i = 0; i < 96; ++i) script->call_storage[i] = script->local_call_storage[i];
        }
        ThugScriptCallFrame *frame = (ThugScriptCallFrame *)(script->call_storage + script->call_depth*48);
        ++script->call_depth;
        frame->checksum = script->checksum; frame->arguments = script->arguments; frame->instruction = script->instruction;
        frame->owner = script->owner.object; frame->loop = script->loop; frame->deferred_checksum = script->unknown_e8;
        frame->wait_type_bits = (frame->wait_type_bits & ~15u) | (script->wait_type & 15);
        frame->wait_owner = script->wait_owner; frame->wait_argument = script->wait_argument; frame->wait_frames = script->wait_frames;
        frame->wait_remaining_bits = thug_script_read_word((const uint8_t *)&script->wait_remaining);
        frame->flags = (frame->flags & ~3u) | (script->waited & 1) | ((script->flags & 1) << 1);
        script->checksum = name; script->instruction = program;
        script->arguments = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
        script->instruction = thug_script_parse_parameters(script->arguments, script->instruction, NULL, memory);
        if (arguments) thug_script_structure_merge(script->arguments, arguments, memory);
        if (script->owner.object) { thug_object_reference_unlink(script->owner.object, &script->owner); script->owner.object = NULL; }
        script->owner.object = owner;
        if (owner) thug_object_reference_link(owner, &script->owner);
        script->wait_type = 0; script->unknown_e8 = 0;
    }
    script->flags = (script->flags & ~1u) | (immediate & 1);
}
/* 0x00475750. An immediate call runs through the same executor, stopping when
 * its returning flag produces result 5. A wait may return earlier. */
void thug_script_run_immediate(ThugScriptInstance *script, uint32_t name, const ThugScriptStructure *arguments,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const uint8_t *program = thug_script_cache_acquire(thug_script_cache, name, memory);
    thug_script_push_call(script, name, program, arguments, script->owner.object, 1, diagnostics, memory);
    thug_script_execute(script, diagnostics, memory);
}
/* 0x00474b40. Native and virtual calls use actual relocated function pointers.
 * Object-qualified missing commands retain the original invalid-symbol contract
 * outside the special default-level script; no fallback command is invented. */
static uint8_t invoke_command(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t token = *script->instruction;
    if (token == 0x43 || token == 0x44 || token == 0x46) {
        ++script->instruction; uint32_t value = thug_script_read_word(script->instruction); script->instruction += 4;
        thug_script_read_parameters(script, memory);
        if (token == 0x43) return ((ThugScriptNativePredicate)(uintptr_t)value)(script->parameters, script);
        if (token == 0x44) return thug_script_call_member(script, value, NULL);
        return thug_script_call_descriptor(script, (const ThugScriptCommand *)(uintptr_t)value, NULL);
    }
    uint32_t name = 0;
    if (token == 0x0e) {
        ThugScriptComponent *value = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
        script->instruction = thug_script_parse_expression(script->instruction, script->arguments, value, memory);
        uint8_t checksum = (value->type_and_flags & 0xfe) == 26;
        name = value->value; thug_script_component_clear(value, memory); memory->release(memory->context, value);
        if (!checksum) return name != 0;
    }
    if (!name) name = thug_script_read_name(script);
    if (*script->instruction == 0x42) {
        ThugReferencedObject *owner = thug_script_find_object(name);
        if (!owner) return 1;
        script->instruction = thug_script_resolve_branches(script->instruction + 1, memory);
        if (*script->instruction == 0x44) {
            ++script->instruction; name = thug_script_read_word(script->instruction); script->instruction += 4;
            thug_script_read_parameters(script, memory); return thug_script_call_member(script, name, owner);
        }
        name = thug_script_read_name(script); thug_script_read_parameters(script, memory);
        const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
        if (!symbol && script->checksum == 0xfb11e6cd) return 0;
        if (symbol->type == 9) return symbol->value ? thug_script_call_descriptor(script, (const ThugScriptCommand *)(uintptr_t)symbol->value, owner)
            : thug_script_call_member(script, name, owner);
        if (symbol->type != 7) return 0;
        const uint8_t *program = thug_script_cache_acquire(thug_script_cache, symbol->name, memory);
        thug_script_push_call(script, name, program, script->parameters, owner, 0, diagnostics, memory); return 1;
    }
    if (*script->instruction == 7) {
        script->instruction -= 4; name = thug_script_read_word(script->instruction); script->instruction += 5;
        script->instruction = thug_script_resolve_branches(script->instruction, memory);
        ThugScriptComponent *value = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
        script->instruction = *script->instruction == 0x0e ? thug_script_parse_expression(script->instruction, script->arguments, value, memory)
            : thug_script_parse_component_value(script->instruction, script->arguments, value, memory);
        if (!(value->type_and_flags & 0xfe)) memory->release(memory->context, value);
        else { value->name = name; thug_script_structure_insert(script->arguments, value, memory); }
        return 1;
    }
    thug_script_read_parameters(script, memory);
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (!symbol) {
        if (script->checksum != 0xfb11e6cd) diagnostics->print(diagnostics->context, thug_script_missing_format, thug_script_name_text(name));
        return 0;
    }
    if (symbol->type == 8) return ((ThugScriptNativePredicate)(uintptr_t)symbol->value)(script->parameters, script);
    if (symbol->type == 9) return symbol->value ? thug_script_call_descriptor(script, (const ThugScriptCommand *)(uintptr_t)symbol->value, NULL)
        : thug_script_call_member(script, name, NULL);
    if (symbol->type != 7) return 0;
    const uint8_t *program = thug_script_cache_acquire(thug_script_cache, symbol->name, memory);
    thug_script_push_call(script, name, program, script->parameters, script->owner.object, 0, diagnostics, memory); return 1;
}
/* Port service binding for native QB commands, including predicates parsed
 * inside arguments. Nesting restores the caller's binding, as event delivery
 * does for the same original fixed-argument virtual ABI. */
uint8_t thug_script_invoke_command(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const ThugEventServices services = {diagnostics, memory}, *previous = thug_event_services;
    thug_event_services = &services;
    uint8_t result = invoke_command(script, diagnostics, memory);
    thug_event_services = previous;
    return result;
}
/* 0x00475050. Keep the original operand address even if the command changes the
 * instruction pointer. An interrupted/null script must not take the false jump. */
void thug_script_conditional(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ++script->instruction; uint32_t offset = thug_script_read_half(script->instruction);
    const uint8_t *operand = script->instruction; script->instruction += 2;
    uint8_t invert = *script->instruction == 0x39;
    if (invert) ++script->instruction;
    uint8_t result = thug_script_invoke_command(script, diagnostics, memory);
    if (script->instruction && !(invert ? !result : result)) script->instruction = operand + offset;
}
/* 0x004750b0. Result 0=end, 1=wait kinds 3/4, 2=other wait, 5=immediate return.
 * Current-script is cleared on end/wait, but deliberately retained on result 5. */
uint32_t thug_script_execute(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    script->flags &= 0xfd;
    for (;;) {
        if (!script->instruction) { thug_current_script = NULL; script->flags &= 0xfe; return 0; }
        thug_current_script = script;
        if (!(script->flags & 2)) thug_script_update_wait(script);
        if (script->wait_type) {
            script->flags = (script->flags & 0xfe) | 2; thug_current_script = NULL;
            return script->wait_type == 3 || script->wait_type == 4 ? 1 : 2;
        }
        switch (*script->instruction) {
        case 1: case 0x28: case 0x3d: ++script->instruction; break;
        case 2: script->instruction += 5; break;
        case 0x20: thug_script_begin_loop(script, memory); break;
        case 0x21: thug_script_repeat_loop(script, memory); break;
        case 0x22: thug_script_break_loop(script, memory); break;
        case 0x24: case 0x29: {
            uint8_t returning = *script->instruction == 0x29;
            if (script->unknown_e8) {
                uint32_t name = script->unknown_e8; script->unknown_e8 = 0;
                thug_script_run_immediate(script, name, NULL, diagnostics, memory);
            }
            if (returning) { ++script->instruction; thug_script_read_parameters(script, memory); }
            if (thug_script_return(script, returning ? script->parameters : NULL, memory)) return 5;
            break;
        }
        case 0x25: case 0x26: case 0x3e: case 0x3f: break;
        case 0x2e: case 0x2f: case 0x37: case 0x40: case 0x41: case 0x49:
            script->instruction = thug_script_resolve_branches(script->instruction, memory); break;
        case 0x3c: thug_script_select_case(script, memory); break;
        case 0x47: thug_script_conditional(script, diagnostics, memory); break;
        case 0x48: ++script->instruction; script->instruction += thug_script_read_half(script->instruction); break;
        default: thug_script_invoke_command(script, diagnostics, memory); break;
        }
    }
}
