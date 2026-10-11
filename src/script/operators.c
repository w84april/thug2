#include "operators.h"
#include <stddef.h>

/* 0x00476490. NULL starts iteration; otherwise use the supplied member's link. */
ThugScriptComponent *thug_script_next_component(const ThugScriptStructure *s, const ThugScriptComponent *c) {
    return c ? c->next : s->first;
}
static void remove_matching(ThugScriptStructure *s, uint32_t value, uint32_t type, unsigned mode, const ThugMemory *memory) {
    ThugScriptComponent *previous = NULL, *c = s->first;
    while (c) {
        ThugScriptComponent *next = c->next;
        uint8_t match = mode == 2 ? !c->name && c->value == value
            : c->name == value && (!mode || (c->type_and_flags >> 1) == (type & 0xff));
        if (match) {
            if (previous) previous->next = next; else s->first = next;
            thug_script_component_clear(c, memory);
            memory->release(memory->context, c);
        } else previous = c;
        c = next;
    }
}
/* 0x004776b0 / 0x00477790 / 0x00477860. Remove every matching member, unlinking
 * before disposal. The unnamed-value variant does not check the value type. */
void thug_script_remove_name(ThugScriptStructure *s, uint32_t name, const ThugMemory *memory) {
    remove_matching(s, name, 0, 0, memory);
}
void thug_script_remove_typed(ThugScriptStructure *s, uint32_t name, uint32_t type, const ThugMemory *memory) {
    remove_matching(s, name, type, 1, memory);
}
void thug_script_remove_unnamed_value(ThugScriptStructure *s, uint32_t value, const ThugMemory *memory) {
    remove_matching(s, value, 0, 2, memory);
}

typedef struct { uint32_t type, value; } Value;
static Value resolved(const ThugScriptComponent *c) {
    Value v = { c->type_and_flags >> 1, c->value };
    if (v.type == 13) {
        const ThugScriptSymbol *symbol = thug_script_resolve_symbol(v.value);
        if (symbol) { v.type = symbol->type; v.value = symbol->value; }
    }
    return v;
}
static double number(Value v) {
    if (v.type == 1) return (double)(int32_t)v.value;
    union { uint32_t bits; float value; } f = { .bits = v.value };
    return f.value;
}
static uint32_t text_length(uint32_t pointer) {
    const char *text = (const char *)(uintptr_t)pointer;
    uint32_t length = 0; while (text[length]) ++length; return length;
}
/* 0x0049f4b0 really is an unconditional false return in this pinned modified
 * specimen. Distinct arrays are not compared recursively by 0x004791a0. */
uint8_t thug_script_array_equal_fallback(const ThugScriptArray *a, const ThugScriptArray *b) {
    (void)a; (void)b; return 0;
}
/* 0x004791a0. Mixed numeric comparisons retain exact signed FILD inputs, rather
 * than first rounding integers to float32. Structure/array equality is identity. */
uint8_t thug_script_component_equal(const ThugScriptComponent *left, const ThugScriptComponent *right) {
    Value a = resolved(left), b = resolved(right);
    if ((a.type == 1 || a.type == 2) && (b.type == 1 || b.type == 2)) return number(a) == number(b);
    if (a.type != b.type) return 0;
    switch (a.type) {
    case 3: case 4: {
        const uint8_t *x = (const uint8_t *)(uintptr_t)a.value, *y = (const uint8_t *)(uintptr_t)b.value;
        while (*x == *y) { if (!*x) return 1; ++x; ++y; }
        return 0;
    }
    case 5: case 6: {
        const float *x = (const float *)(uintptr_t)a.value, *y = (const float *)(uintptr_t)b.value;
        for (unsigned i = 1; i <= (a.type == 5 ? 2u : 3u); ++i) if (!(x[i] == y[i])) return 0;
        return 1;
    }
    case 7: case 10: case 13: return a.value == b.value;
    case 12: return a.value == b.value || thug_script_array_equal_fallback(
        (const ThugScriptArray *)(uintptr_t)a.value, (const ThugScriptArray *)(uintptr_t)b.value);
    default: return 0;
    }
}
/* 0x00476c10. Every left member must find one equal name/value on the right.
 * Matches are reusable, so duplicate members are not counted as a multiset. */
uint8_t thug_script_structure_is_subset(const ThugScriptStructure *left, const ThugScriptStructure *right) {
    for (const ThugScriptComponent *a = left->first; a; a = a->next) {
        const ThugScriptComponent *b = right->first;
        while (b && (a->name != b->name || !thug_script_component_equal(a, b))) b = b->next;
        if (!b) return 0;
    }
    return 1;
}
/* 0x00479410 / 0x004795a0. Strings compare lengths. Structures use non-strict
 * member inclusion, so both directions can be true for equal structures. */
static uint8_t compare(const ThugScriptComponent *left, const ThugScriptComponent *right, uint8_t greater) {
    Value a = resolved(left), b = resolved(right);
    if ((a.type == 1 || a.type == 2) && (b.type == 1 || b.type == 2))
        return greater ? number(a) > number(b) : number(a) < number(b);
    if ((a.type == 3 || a.type == 4) && a.type == b.type)
        return greater ? text_length(a.value) > text_length(b.value) : text_length(a.value) < text_length(b.value);
    if ((a.type == 10 || a.type == 20) && (b.type == 10 || b.type == 20)) {
        const ThugScriptStructure *x = (const ThugScriptStructure *)(uintptr_t)a.value, *y = (const ThugScriptStructure *)(uintptr_t)b.value;
        return greater ? thug_script_structure_is_subset(y, x) : thug_script_structure_is_subset(x, y);
    }
    return 0;
}
uint8_t thug_script_component_less(const ThugScriptComponent *a, const ThugScriptComponent *b) { return compare(a, b, 0); }
uint8_t thug_script_component_greater(const ThugScriptComponent *a, const ThugScriptComponent *b) { return compare(a, b, 1); }

static uint32_t item(const ThugScriptArray *array, int32_t index) {
    if (array->count == 1) return array->value_or_items;
    return ((const uint32_t *)(uintptr_t)array->value_or_items)[index];
}
/* 0x0046cb70. The original's type-specific branches all return the raw item. */
const char *thug_script_array_text(const ThugScriptArray *array, int32_t index) { return (const char *)(uintptr_t)item(array, index); }
static uint32_t quiet(uint32_t bits) {
    if ((bits & 0x7f800000) == 0x7f800000 && (bits & 0x7fffff)) bits |= 0x400000;
    return bits;
}
/* 0x0046cbf0. Type 2 loads float; every other type loads an exact signed int. */
double thug_script_array_number(const ThugScriptArray *array, int32_t index) {
    uint32_t value = item(array, index);
    if (((const uint8_t *)&array->unknown_0)[1] != 2) return (double)(int32_t)value;
    union { uint32_t bits; float value; } f = { .bits = quiet(value) };
    return f.value;
}
static void copy_word(void *destination, const void *source) {
    uint8_t *d = destination; const uint8_t *s = source;
    for (unsigned i = 0; i < 4; ++i) d[i] = s[i];
}
/* 0x0047a910. The shifted tag masks the array type to 7 bits before dispatch.
 * Local strings (type 4) are unsupported here. Output must not own a live value;
 * this routine overwrites it without clearing. Bounds are the caller's job. */
void thug_script_array_component(const ThugScriptArray *array, uint32_t index, ThugScriptComponent *out,
    uint32_t borrow, const ThugMemory *memory) {
    out->type_and_flags = (out->type_and_flags & 1) | (((const uint8_t *)&array->unknown_0)[1] << 1);
    switch (out->type_and_flags >> 1) {
    case 1: case 13: out->value = item(array, (int32_t)index); break;
    case 2: {
        union { float value; uint32_t bits; } f = { .value = (float)thug_script_array_number(array, (int32_t)index) };
        out->value = f.bits; break;
    }
    case 3: out->value = (uintptr_t)thug_script_string_copy(thug_script_array_text(array, (int32_t)index), memory); break;
    case 5: case 6: {
        uint8_t type = out->type_and_flags >> 1;
        const uint8_t *source = (const uint8_t *)(uintptr_t)item(array, (int32_t)index);
        void *copy = memory->allocate(memory->context, type == 5 ? 12 : 16, 1);
        if (type == 5) thug_script_pair_initialize(copy); else thug_script_vector_initialize(copy);
        out->value = (uintptr_t)copy;
        for (unsigned offset = 4; offset < (type == 5 ? 12u : 16u); offset += 4)
            copy_word((uint8_t *)(uintptr_t)out->value + offset, source + offset);
        break;
    }
    case 10:
        if (borrow) { out->type_and_flags = (out->type_and_flags & 1) | 0x28; out->value = item(array, (int32_t)index); }
        else {
            out->value = (uintptr_t)thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
            const ThugScriptStructure *source = (const ThugScriptStructure *)(uintptr_t)item(array, (int32_t)index);
            thug_script_structure_merge_optional((ThugScriptStructure *)(uintptr_t)out->value, source, memory);
        }
        break;
    case 12:
        if (borrow) { out->type_and_flags = (out->type_and_flags & 1) | 0x2a; out->value = item(array, (int32_t)index); }
        else {
            out->value = (uintptr_t)thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
            ThugScriptArray *source = (ThugScriptArray *)(uintptr_t)item(array, (int32_t)index);
            thug_script_array_copy((ThugScriptArray *)(uintptr_t)out->value, source, memory);
        }
        break;
    default: out->type_and_flags &= 1; out->value = 0; break;
    }
}
/* 0x0046d160 / 0x0046d180 / 0x0046d1a0. These only inspect/change type tags. */
uint8_t thug_script_component_is_borrowed(const ThugScriptComponent *c) {
    return (c->type_and_flags >> 1) == 20 || (c->type_and_flags >> 1) == 21;
}
void thug_script_component_borrow(ThugScriptComponent *c) {
    if ((c->type_and_flags >> 1) == 10) c->type_and_flags = (c->type_and_flags & 1) | 0x28;
    else if ((c->type_and_flags >> 1) == 12) c->type_and_flags = (c->type_and_flags & 1) | 0x2a;
}
void thug_script_component_own(ThugScriptComponent *c) {
    if ((c->type_and_flags >> 1) == 20) c->type_and_flags = (c->type_and_flags & 1) | 0x14;
    else if ((c->type_and_flags >> 1) == 21) c->type_and_flags = (c->type_and_flags & 1) | 0x18;
}
/* 0x0046d280. Integer truth preserves all bits; float truth is 0 or 1. */
uint32_t thug_script_component_truth(const ThugScriptComponent *c) {
    if ((c->type_and_flags >> 1) == 1) return c->value;
    if ((c->type_and_flags >> 1) == 2) { Value v = { 2, c->value }; return number(v) != 0; }
    return 0;
}

/* 0x00479730. Resolve a checksum in place without copying or disposing payloads.
 * Callers control ownership; unsupported symbol types leave the value unchanged. */
void thug_script_component_resolve(ThugScriptComponent *c) {
    if ((c->type_and_flags >> 1) != 13) return;
    const ThugScriptSymbol *s = thug_script_resolve_symbol(c->value);
    if (!s) return;
    switch (s->type) {
    case 1: case 2: case 3: case 4: case 5: case 6: case 10: case 12: case 13:
        c->type_and_flags = (c->type_and_flags & 1) | (s->type << 1);
        c->value = s->value;
    }
}
