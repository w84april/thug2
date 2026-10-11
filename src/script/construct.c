#include "values.h"
#include "runtime.h"
#include <stddef.h>
/* 0x004783c0. This setter accepts only these five tags. Structure tag 11
 * selects the ordinary owned-structure setter; other tags leave it unchanged. */
void thug_script_set_scalar(ThugScriptStructure *structure, uint32_t name, uint32_t type,
    uint32_t value, const ThugMemory *memory) {
    switch (type) {
        case 1: thug_script_set_integer(structure, name, value, memory); break;
        case 2: thug_script_set_float_bits(structure, name, value, memory); break;
        case 11: thug_script_set_structure(structure, name, (ThugScriptStructure *)(uintptr_t)value, memory); break;
        case 12: thug_script_set_array(structure, name, (ThugScriptArray *)(uintptr_t)value, memory); break;
        case 13: thug_script_set_checksum(structure, name, value, memory); break;
    }
}

static ThugScriptComponent *new_component(uint32_t name, uint8_t type, const ThugMemory *memory) {
    ThugScriptComponent *c = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
    c->name = name;
    c->type_and_flags = (c->type_and_flags & 1) | (type << 1);
    return c;
}
static void set_word(ThugScriptStructure *s, uint32_t name, uint8_t type, uint32_t value, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, type, memory);
    c->value = value;
    thug_script_structure_insert(s, c, memory);
}
static void set_text(ThugScriptStructure *s, uint32_t name, uint8_t type, const char *text, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, type, memory);
    c->value = (uintptr_t)thug_script_string_copy(text, memory);
    thug_script_structure_insert(s, c, memory);
}
static void store_word(void *destination, uint32_t value) {
    uint8_t *p = destination;
    for (unsigned i = 0; i < 4; ++i) p[i] = (uint8_t)(value >> (i * 8));
}

/* 0x004779d0 / 0x00477ac0. Copy text before inserting the new component, so a
 * source that belongs to the replaced component remains alive during copying. */
void thug_script_set_string(ThugScriptStructure *s, uint32_t name, const char *text, const ThugMemory *memory) {
    set_text(s, name, 3, text, memory);
}
void thug_script_set_local_string(ThugScriptStructure *s, uint32_t name, const char *text, const ThugMemory *memory) {
    set_text(s, name, 4, text, memory);
}
/* 0x00477b80 / 0x00477c60 / 0x00477d40. Numeric payloads are raw words; the
 * original float setter performs no floating-point load or conversion. */
void thug_script_set_integer(ThugScriptStructure *s, uint32_t name, uint32_t value, const ThugMemory *memory) {
    set_word(s, name, 1, value, memory);
}
void thug_script_set_float_bits(ThugScriptStructure *s, uint32_t name, uint32_t value, const ThugMemory *memory) {
    set_word(s, name, 2, value, memory);
}
void thug_script_set_checksum(ThugScriptStructure *s, uint32_t name, uint32_t value, const ThugMemory *memory) {
    set_word(s, name, 13, value, memory);
}
/* 0x00477e20 / 0x00477fc0. Raw coordinate words, including signaling NaNs. */
void thug_script_set_vector_bits(ThugScriptStructure *s, uint32_t name, uint32_t x, uint32_t y, uint32_t z, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, 6, memory);
    c->value = (uintptr_t)thug_script_vector_initialize(memory->allocate(memory->context, 16, 1));
    store_word((uint8_t *)(uintptr_t)c->value + 4, x);
    store_word((uint8_t *)(uintptr_t)c->value + 8, y);
    store_word((uint8_t *)(uintptr_t)c->value + 12, z);
    thug_script_structure_insert(s, c, memory);
}
void thug_script_set_pair_bits(ThugScriptStructure *s, uint32_t name, uint32_t x, uint32_t y, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, 5, memory);
    c->value = (uintptr_t)thug_script_pair_initialize(memory->allocate(memory->context, 12, 1));
    store_word((uint8_t *)(uintptr_t)c->value + 4, x);
    store_word((uint8_t *)(uintptr_t)c->value + 8, y);
    thug_script_structure_insert(s, c, memory);
}
/* 0x004780d0 / 0x004781b0. Transfer ownership; do not deep-copy the payload. */
void thug_script_set_array(ThugScriptStructure *s, uint32_t name, ThugScriptArray *value, const ThugMemory *memory) {
    set_word(s, name, 12, (uintptr_t)value, memory);
}
/* 0x00478b00. Copy the array and its owned elements before replacing a member. */
void thug_script_set_array_copy(ThugScriptStructure *s, uint32_t name, ThugScriptArray *source, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name,12,memory);
    ThugScriptArray *copy = thug_script_array_initialize(memory->allocate(memory->context,12,1));
    c->value = (uintptr_t)copy;
    thug_script_array_copy(copy,source,memory);
    thug_script_structure_insert(s,c,memory);
}
/* 0x0046cb10. Single-item storage ignores the supplied index. */
void thug_script_array_set_word(ThugScriptArray *array, int32_t index, uint32_t value) {
    if (array->count == 1) array->value_or_items = value;
    else {
        void *at = (void *)(uintptr_t)(array->value_or_items + (uint32_t)index*4);
        __builtin_memcpy(at,&value,4);
    }
}
void thug_script_set_structure(ThugScriptStructure *s, uint32_t name, ThugScriptStructure *value, const ThugMemory *memory) {
    set_word(s, name, 10, (uintptr_t)value, memory);
}
/* 0x00478670. Allocate the owned copy before replacing the destination member;
 * this permits the source to be that member's existing structure. */
void thug_script_set_structure_copy(ThugScriptStructure *s, uint32_t name,
    const ThugScriptStructure *source, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, 10, memory);
    ThugScriptStructure *copy = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
    c->value = (uintptr_t)copy;
    thug_script_structure_assign(copy, source, memory);
    thug_script_structure_insert(s, c, memory);
}
/* 0x00478290. The allocated/copied size is 32 bits; only the saved component
 * length truncates to 16 bits. The payload is attached after the copy. */
void thug_script_set_blob(ThugScriptStructure *s, uint32_t name, const uint8_t *source, uint32_t length, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(name, 7, memory);
    c->padding[1] = (uint8_t)length; c->padding[2] = (uint8_t)(length >> 8);
    memory->temp_scope(memory->context, 1);
    uint8_t *copy = memory->allocate(memory->context, length, 0);
    memory->temp_scope(memory->context, 0);
    for (uint32_t i = 0; i < length; ++i) copy[i] = source[i];
    c->value = (uintptr_t)copy;
    thug_script_structure_insert(s, c, memory);
}

/* 0x00478650. Self-assignment preserves the structure; other assignments
 * clear it before merging the source's members. Owned graphs must not overlap. */
ThugScriptStructure *thug_script_structure_assign(ThugScriptStructure *destination,
    const ThugScriptStructure *source, const ThugMemory *memory) {
    if (destination != source) {
        thug_script_structure_clear(destination, memory);
        thug_script_structure_merge(destination, source, memory);
    }
    return destination;
}

/* 0x00476430. Last match wins, including anonymous global structure inclusions.
 * Matching literal names return their component regardless of value type.
 * Looking for name zero therefore does not traverse those inclusions. */
ThugScriptComponent *thug_script_find_component(const ThugScriptStructure *s, uint32_t name) {
    ThugScriptComponent *result = NULL;
    for (ThugScriptComponent *c = s->first; c; c = c->next) {
        if (c->name == name) result = c;
        else if (!c->name && (c->type_and_flags & 0xfe) == 0x1a) {
            const ThugScriptSymbol *symbol = thug_script_resolve_symbol(c->value);
            if (symbol && symbol->type == 10) {
                ThugScriptComponent *match = thug_script_find_component((const ThugScriptStructure *)(uintptr_t)symbol->value, name);
                if (match) result = match;
            }
        }
    }
    return result;
}

/* 0x004739d0. Snapshot a source that would be destroyed when the instance's
 * current parameters/arguments are cleared. Otherwise return NULL. */
ThugScriptStructure *thug_script_snapshot_arguments(const ThugScriptInstance *script,
    const ThugScriptStructure *source, const ThugMemory *memory) {
    if (!source) return NULL;
    if ((script->parameters && thug_script_structure_contains(script->parameters, source))
        || (script->arguments && thug_script_structure_contains(script->arguments, source))) {
        ThugScriptStructure *copy = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
        thug_script_structure_merge_optional(copy, source, memory);
        return copy;
    }
    return NULL;
}
