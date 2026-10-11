#include "values.h"
#include "../core/checksum.h"
#include <stddef.h>
_Static_assert(sizeof(ThugScriptVector) == 16, "Script vector layout");
uint8_t thug_script_string_interning;
char *thug_script_string_cursor;
ThugScriptStringEntry *thug_script_string_entries;
uint32_t thug_script_string_count;

static uint32_t text_length(const char *text) {
    uint32_t length = 0;
    while (text[length]) ++length;
    return length;
}
static void copy_word(void *destination, const void *source) {
    uint8_t *out = destination; const uint8_t *in = source;
    for (unsigned i = 0; i < 4; ++i) out[i] = in[i];
}
static uint16_t component_length(const ThugScriptComponent *c) {
    return c->padding[1] | (uint16_t)c->padding[2] << 8;
}

/* 0x00476260 (input in EAX). Lookup compares raw CRC only, not string bytes.
 * A checksum collision returns the first table entry, as in the executable. */
char *thug_script_string_intern(const char *text) {
    uint32_t length = text_length(text);
    uint32_t checksum = thug_crc32_buffer((const unsigned char *)text, (int32_t)length);
    uint32_t count = thug_script_string_count;
    for (uint32_t i = 0; i < count; ++i)
        if (thug_script_string_entries[i].checksum == checksum) return thug_script_string_entries[i].text;
    char *result = thug_script_string_cursor;
    for (uint32_t i = 0; i <= length; ++i) result[i] = text[i];
    thug_script_string_cursor = result + length + 1;
    thug_script_string_entries[count].checksum = checksum;
    thug_script_string_entries[count].text = result;
    thug_script_string_count = count + 1;
    return result;
}

/* 0x004763a0. The ordinary copy uses the original temporary heap scope. */
char *thug_script_string_copy(const char *text, const ThugMemory *memory) {
    if (thug_script_string_interning) return thug_script_string_intern(text);
    memory->temp_scope(memory->context, 1);
    uint32_t length = text_length(text);
    char *result = memory->allocate(memory->context, length + 1, 0);
    for (uint32_t i = 0; i <= length; ++i) result[i] = text[i];
    memory->temp_scope(memory->context, 0);
    return result;
}

/* 0x0047abf0. Padding survives construction. */
ThugScriptVector *thug_script_vector_initialize(ThugScriptVector *v) {
    v->z = v->y = v->x = 0; v->tag = 0; return v;
}

/* 0x0046cc50. Resize storage only; callers must first dispose owned payloads.
 * New multi-item buffers contain zero words. A single item remains inline. */
void thug_script_array_set_size(ThugScriptArray *array, uint32_t count, uint8_t type, const ThugMemory *memory) {
    if (array->value_or_items) {
        if (array->count != 1) memory->release(memory->context, (void *)(uintptr_t)array->value_or_items);
        array->value_or_items = 0;
    }
    ((uint8_t *)&array->unknown_0)[1] = type;
    array->count = count;
    if (!count) ((uint8_t *)&array->unknown_0)[1] = 0;
    else if (count != 1) {
        memory->temp_scope(memory->context, 1);
        array->value_or_items = (uintptr_t)memory->allocate(memory->context, array->count * 4, 0);
        memory->temp_scope(memory->context, 0);
        uint32_t *items = (uint32_t *)(uintptr_t)array->value_or_items;
        for (uint32_t i = 0; i < array->count; ++i) items[i] = 0;
    }
}

/* 0x004773e0. Existing destination values are cleared before reading the
 * source's type/name. Bit 0 stays with the destination. Borrowing affects only
 * owned structures/arrays, converting them to types 20/21. */
void thug_script_component_copy(ThugScriptComponent *destination, const ThugScriptComponent *source,
    uint32_t borrow_nested, const ThugMemory *memory) {
    if (destination->value) thug_script_component_clear(destination, memory);
    destination->type_and_flags = (destination->type_and_flags & 1) | (source->type_and_flags & 0xfe);
    destination->name = source->name;
    switch (source->type_and_flags >> 1) {
    case 3: case 4:
        destination->value = (uintptr_t)thug_script_string_copy((const char *)(uintptr_t)source->value, memory);
        break;
    case 5: case 6: {
        uint8_t type = source->type_and_flags >> 1;
        void *value = memory->allocate(memory->context, type == 5 ? 12 : 16, 1);
        if (type == 5) thug_script_pair_initialize(value);
        else thug_script_vector_initialize(value);
        destination->value = (uintptr_t)value;
        for (unsigned offset = 4; offset < (type == 5 ? 12u : 16u); offset += 4)
            copy_word((uint8_t *)(uintptr_t)destination->value + offset, (const uint8_t *)(uintptr_t)source->value + offset);
        break;
    }
    case 7: {
        memory->temp_scope(memory->context, 1);
        destination->value = (uintptr_t)memory->allocate(memory->context, component_length(source), 0);
        destination->padding[1] = source->padding[1]; destination->padding[2] = source->padding[2];
        memory->temp_scope(memory->context, 0);
        const uint8_t *input = (const uint8_t *)(uintptr_t)source->value;
        uint8_t *output = (uint8_t *)(uintptr_t)destination->value;
        for (uint32_t i = 0; i < component_length(source); ++i) output[i] = input[i];
        break;
    }
    case 10:
        if (borrow_nested) {
            destination->type_and_flags = (destination->type_and_flags & 1) | 0x28;
            destination->value = source->value;
        } else {
            ThugScriptStructure *copy = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
            destination->value = (uintptr_t)copy;
            const ThugScriptStructure *original = (const ThugScriptStructure *)(uintptr_t)source->value;
            if (copy != original) {
                thug_script_structure_clear(copy, memory);
                thug_script_structure_merge(copy, original, memory);
            }
        }
        break;
    case 12:
        if (!borrow_nested) {
            ThugScriptArray *copy = thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
            destination->value = (uintptr_t)copy;
            thug_script_array_copy(copy, (ThugScriptArray *)(uintptr_t)source->value, memory);
            break;
        }
        destination->type_and_flags = (destination->type_and_flags & 1) | 0x2a;
        /* fall through */
    case 1: case 2: case 13: case 20: case 21:
        destination->value = source->value;
        break;
    default: break;
    }
}

/* 0x00478480. Copy source members in order, applying the real replacement
 * rules for every member. Neither source header nor member links are copied. */
ThugScriptStructure *thug_script_structure_merge(ThugScriptStructure *destination,
    const ThugScriptStructure *source, const ThugMemory *memory) {
    for (const ThugScriptComponent *c = source->first; c; c = c->next) {
        ThugScriptComponent *copy = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
        thug_script_component_copy(copy, c, 0, memory);
        thug_script_structure_insert(destination, copy, memory);
    }
    return destination;
}
/* 0x00478540. Its null-source path returns the zero argument left in EAX. */
ThugScriptStructure *thug_script_structure_merge_optional(ThugScriptStructure *destination,
    const ThugScriptStructure *source, const ThugMemory *memory) {
    return source ? thug_script_structure_merge(destination, source, memory) : NULL;
}

/* 0x004787a0. Scalar copies are sequential raw words, including overlap and
 * NaN payload bits. Null owned elements leave destination words untouched. */
void thug_script_array_copy_items(uint32_t *destination, const uint32_t *source,
    uint32_t count, uint32_t type, const ThugMemory *memory) {
    if (type == 1 || type == 2 || type == 13) {
        for (uint32_t i = 0; i < count; ++i) destination[i] = source[i];
        return;
    }
    if (type != 3 && type != 4 && type != 5 && type != 6 && type != 10 && type != 12) return;
    for (uint32_t i = 0; i < count; ++i) {
        if (!source[i]) continue;
        const uint8_t *original = (const uint8_t *)(uintptr_t)source[i];
        void *copy;
        if (type == 3 || type == 4) copy = thug_script_string_copy((const char *)original, memory);
        else if (type == 5 || type == 6) {
            copy = memory->allocate(memory->context, type == 5 ? 12 : 16, 1);
            if (type == 5) thug_script_pair_initialize(copy);
            else thug_script_vector_initialize(copy);
            for (unsigned offset = 4; offset < (type == 5 ? 12u : 16u); offset += 4)
                copy_word((uint8_t *)copy + offset, original + offset);
        } else if (type == 10) {
            copy = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
            if (copy != (const void *)original) {
                thug_script_structure_clear(copy, memory);
                thug_script_structure_merge(copy, (const ThugScriptStructure *)original, memory);
            }
        } else {
            copy = thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
            thug_script_array_copy(copy, (ThugScriptArray *)original, memory);
        }
        destination[i] = (uintptr_t)copy;
    }
}

/* 0x00478a60. Clearing comes before source header reads, so self-copy empties
 * the array exactly as the original does. */
void thug_script_array_copy(ThugScriptArray *destination, ThugScriptArray *source, const ThugMemory *memory) {
    thug_script_array_clear(destination, memory);
    uint8_t type = ((uint8_t *)&source->unknown_0)[1];
    uint32_t count = source->count;
    thug_script_array_set_size(destination, count, type, memory);
    if (count) thug_script_array_copy_items(thug_script_array_items(destination), thug_script_array_items(source), count, type, memory);
}
