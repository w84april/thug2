#include "../../src/script/operators.h"
#include "../../src/script/symbols.h"
#include "../../src/script/delivery.h"

/* 00449d00. Change replaces an existing data symbol, preserving its file
 * checksum. Read the source AFTER destruction/allocation, just as the original
 * does. Unsupported source types still replace the target with an empty symbol.
 * As in the current value-copy runtime, the array pool is disabled; generic
 * allocation and valid exclusively-owned input graphs are required. */
uint8_t thug_script_change_draft(const ThugScriptStructure *params,
    ThugScriptInstance *script, const ThugMemory *memory) {
    (void)script;
    uint32_t name = 0;
    thug_script_get_checksum(params, 0x60f6f242, &name, 0);
    const ThugScriptComponent *source = name
        ? thug_script_find_name_or_flag(params, 0x4b40630d)
        : thug_script_next_component(params, 0);
    if (!source) return 0;
    if (!name) name = source->name;
    ThugScriptSymbol *old = thug_script_symbol_find(name);
    if (!old || old->type == 7 || old->type == 8 || old->type == 9) return 0;
    uint32_t filename = old->unknown_8;
    thug_script_symbol_destroy(old, memory);
    ThugScriptSymbol *target = thug_script_symbol_create(name, memory);
    target->unknown_8 = filename;
    uint8_t type = source->type_and_flags >> 1;
    uint32_t value = source->value;
    if (type == 13 && thug_script_has_flag(params, 0x991a7bc3)) {
        const ThugScriptSymbol *resolved = thug_script_resolve_symbol(value);
        if (resolved) { type = resolved->type & 0x7f; value = resolved->value; }
    }
    switch (type) {
    case 1: case 2: case 13:
        target->type = type;
        target->value = value;
        break;
    case 12: {
        target->type = 12;
        ThugScriptArray *copy = memory->allocate(memory->context, 12, 1);
        if (copy) thug_script_array_initialize(copy);
        target->value = (uintptr_t)copy;
        thug_script_array_copy(copy, (ThugScriptArray *)(uintptr_t)value, memory);
        break;
    }
    case 10: {
        target->type = 10;
        ThugScriptStructure *copy = thug_script_structure_allocate(8, memory);
        if (copy) thug_script_structure_initialize(copy);
        target->value = (uintptr_t)copy;
        thug_script_structure_merge_optional(copy, (const ThugScriptStructure *)(uintptr_t)value, memory);
        break;
    }
    }
    return 1;
}

/* The fixed native ABI obtains the already-scoped interpreter memory service.
 * This host bridge is not counted as another recovered original routine. */
uint8_t thug_script_change_native_draft(ThugScriptStructure *params, ThugScriptInstance *script) {
    return thug_script_change_draft(params, script, thug_event_services->memory);
}
