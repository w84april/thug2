#include "serialize.h"
#include "tokens.h"
#include "values.h"
#include "operators.h"
#include <stddef.h>

/* 0x00479840. The byte table takes precedence, including duplicate matches.
 * Counts compare signed; matched indexes truncate to the chosen wire width. */
uint8_t *thug_script_write_named_header(uint8_t *p, uint32_t type, uint32_t name) {
    const ThugScriptArray *table = thug_script_get_global_array(0x35115a20, 0);
    uint32_t count = table->count;
    for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i)
        if ((uintptr_t)thug_script_array_structure(table, (int32_t)i) == name) {
            *p++ = (uint8_t)(type | 0x80); *p++ = (uint8_t)i; return p;
        }
    table = thug_script_get_global_array(0x25231f42, 0); count = table->count;
    for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i)
        if ((uintptr_t)thug_script_array_structure(table, (int32_t)i) == name) {
            *p++ = (uint8_t)(type | 0x40); return thug_script_write_half(p, i);
        }
    *p++ = (uint8_t)type; return thug_script_write_word(p, name);
}
/* 0x004798f0. Serialize into a temporary first: short capacity leaves output
 * untouched. Positive compact integers use unsigned tags; negative ones signed. */
uint32_t thug_script_serialize_integer(uint32_t name, uint32_t value, uint8_t *out, uint32_t capacity) {
    uint32_t type = 1;
    int32_t signed_value = (int32_t)value;
    if (!value) type = 0x12;
    else if (signed_value > 0 && value <= 255) type = 0x10;
    else if (signed_value > 0 && value <= 65535) type = 0x11;
    else if (signed_value >= -128 && signed_value <= 127) type = 0x0e;
    else if (signed_value >= -32768 && signed_value <= 32767) type = 0x0f;
    uint8_t temporary[20], *p = thug_script_write_named_header(temporary, type, name);
    switch (type) {
    case 1: p = thug_script_write_word(p, value); break;
    case 0x0e: case 0x10: *p++ = (uint8_t)value; break;
    case 0x0f: case 0x11: p = thug_script_write_half(p, value); break;
    default: break;
    }
    uint32_t size = (uint32_t)(p-temporary);
    if (capacity < size) return 0;
    for (uint32_t i = 0; i < size; ++i) out[i] = temporary[i];
    return size;
}
/* 0x00479a50. Tiny magnitudes use a zero tag. Capacity tests conservatively
 * assume a full five-byte name even when a compact name needs fewer bytes.
 * The comparisons load floats, but the serialized payload keeps raw NaN bits. */
uint32_t thug_script_serialize_float(uint8_t *out, uint32_t name, uint32_t bits, uint32_t capacity) {
    union { uint32_t bits; float value; } magnitude = { .bits = bits & 0x7fffffff };
    uint8_t *p;
    if ((double)magnitude.value < 0.0001) {
        if (capacity < 5) return 0;
        p = thug_script_write_named_header(out, 0x13, name);
    } else {
        if (capacity < 9) return 0;
        p = thug_script_write_named_header(out, 2, name);
        p = thug_script_write_word(p, bits);
    }
    return (uint32_t)(p-out);
}
static uint32_t serialize_text(const char *text, uint8_t *out, uint32_t name, uint32_t capacity, uint32_t type) {
    uint32_t length = 0; while (text[length]) ++length;
    if (capacity < length+6u) return 0;
    uint8_t *p = thug_script_write_named_header(out, type, name);
    for (uint32_t i = 0; i < length; ++i) *p++ = (uint8_t)text[i];
    *p++ = 0; return (uint32_t)(p-out);
}
/* 0x00479ac0 and 0x00479b20 differ only in their output type. */
uint32_t thug_script_serialize_string(const char *text, uint8_t *out, uint32_t name, uint32_t capacity) {
    return serialize_text(text, out, name, capacity, 3);
}
uint32_t thug_script_serialize_local_string(const char *text, uint8_t *out, uint32_t name, uint32_t capacity) {
    return serialize_text(text, out, name, capacity, 4);
}
/* 0x00479b80. Array count is written as a halfword, but the full word controls
 * traversal. Unsupported element types still emit the three-byte header. */
uint32_t thug_script_serialize_array(const ThugScriptArray *array, uint8_t *out, uint32_t capacity, uint32_t reserved) {
    if (capacity < 3) return 0;
    uint32_t type = ((const uint8_t *)&array->unknown_0)[1], count = array->count;
    *out = (uint8_t)type;
    uint8_t *p = thug_script_write_half(out+1, count);
    uint32_t remaining = capacity-3;
    if (type == 1 || type == 2 || type == 13 || type == 5 || type == 6) {
        uint32_t width = type == 5 ? 8 : type == 6 ? 12 : 4;
        uint32_t bytes = count*width;
        if (remaining < bytes) return 0;
        const uint32_t *items = thug_script_array_items((ThugScriptArray *)array);
        for (uint32_t i = 0; i < count; ++i) {
            if (width == 4) p = thug_script_write_word(p, items[i]);
            else {
                const uint32_t *value = (const uint32_t *)(uintptr_t)items[i];
                for (uint32_t j = 1; j <= width/4; ++j) p = thug_script_write_word(p, value[j]);
            }
        }
        remaining -= bytes;
    } else if (type == 3 || type == 4) {
        const uint32_t *items = thug_script_array_items((ThugScriptArray *)array);
        for (uint32_t i = 0; i < count; ++i) {
            const uint8_t *text = (const uint8_t *)(uintptr_t)items[i];
            uint8_t byte = *text;
            while (byte) {
                if (!remaining) return 0;
                *p = byte; byte = text[1]; ++p; ++text; --remaining;
            }
            if (!remaining) return 0;
            *p++ = 0; --remaining;
        }
    } else if (type == 10 || type == 12) {
        const uint32_t *items = thug_script_array_items((ThugScriptArray *)array);
        for (uint32_t i = 0; i < count; ++i) {
            uint32_t used = type == 10
                ? thug_script_serialize_structure((const ThugScriptStructure *)(uintptr_t)items[i], p, remaining, reserved, NULL)
                : thug_script_serialize_array((const ThugScriptArray *)(uintptr_t)items[i], p, remaining, reserved);
            if (!used) return 0;
            p += used; remaining -= used;
        }
    }
    return capacity-remaining;
}
/* 0x00479e20. Callbacks run before each top-level component is inspected and
 * can alter its value or next link. Nested structures suppress the callback.
 * Unsupported values fail; a script body is represented by a fixed checksum. */
uint32_t thug_script_serialize_structure(const ThugScriptStructure *structure, uint8_t *out, uint32_t capacity,
    uint32_t reserved, ThugScriptSerializeCallback callback) {
    uint32_t remaining = capacity; uint8_t *p = out;
    if (structure) for (ThugScriptComponent *c = thug_script_next_component(structure, NULL); c;
        c = thug_script_next_component(structure, c)) {
        if (callback) callback();
        uint32_t type = c->type_and_flags >> 1, size = 0;
        switch (type) {
        case 1: size = thug_script_serialize_integer(c->name, c->value, p, remaining); break;
        case 2: size = thug_script_serialize_float(p, c->name, c->value, remaining); break;
        case 3: size = thug_script_serialize_string((const char *)(uintptr_t)c->value, p, c->name, remaining); break;
        case 4: size = thug_script_serialize_local_string((const char *)(uintptr_t)c->value, p, c->name, remaining); break;
        case 5: case 6: {
            if (remaining < (type == 5 ? 13u : 17u)) return 0;
            const uint32_t *value = (const uint32_t *)(uintptr_t)c->value;
            uint8_t *end = thug_script_write_named_header(p, type, c->name);
            for (uint32_t i = 1; i <= (type == 5 ? 2u : 3u); ++i) end = thug_script_write_word(end, value[i]);
            size = (uint32_t)(end-p); break;
        }
        case 7: case 13: {
            if (remaining < 9) return 0;
            uint32_t value = type == 7 ? 0xb9c4f664 : c->value;
            uint8_t *end = thug_script_write_named_header(p, 13, c->name);
            size = (uint32_t)(thug_script_write_word(end, value)-p); break;
        }
        case 10: case 12: {
            if (remaining < 5) return 0;
            uint32_t value = c->value;
            uint8_t *end = thug_script_write_named_header(p, type, c->name);
            uint32_t header = (uint32_t)(end-p);
            size = type == 10
                ? thug_script_serialize_structure((const ThugScriptStructure *)(uintptr_t)value, end, remaining-header, reserved, NULL)
                : thug_script_serialize_array((const ThugScriptArray *)(uintptr_t)value, end, remaining-header, reserved);
            if (!size) return 0;
            size += header; break;
        }
        default: return 0;
        }
        if (!size) return 0;
        p += size; remaining -= size;
    }
    if (!remaining) return 0;
    *p = 0; return capacity-remaining+1;
}
