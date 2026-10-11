#include "params.h"

/* 0x00476620,0x00476ec0,0x00476f10. Legacy forwarding/byte-assert variants;
 * the original disabled diagnostic is a bare RET. Outputs retain getter rules. */
uint8_t thug_script_get_text_forward(const ThugScriptStructure *s, uint32_t name, const char **out, uint32_t flag) {
    return thug_script_get_text(s,name,out,flag);
}
uint8_t thug_script_get_checksum_legacy(const ThugScriptStructure *s, uint32_t name, uint32_t *out, uint32_t flag) {
    return thug_script_get_checksum(s,name,out,(uint8_t)flag != 0);
}
uint8_t thug_script_get_array_legacy(const ThugScriptStructure *s, uint32_t name, ThugScriptArray **out, uint32_t flag) {
    return thug_script_get_array(s,name,out,(uint8_t)flag != 0);
}
#include "../core/number.h"
#include "../core/checksum.h"
#include <stddef.h>

_Static_assert(sizeof(ThugScriptSymbol) == 20, "Script symbol layout");
_Static_assert(sizeof(ThugScriptComponent) == 16, "Script component layout");
ThugScriptSymbol **thug_script_symbol_buckets;

/* 0x00476a00. Hash the supplied text, then use the ordinary checksum getter. */
uint8_t thug_script_get_checksum_string(const ThugScriptStructure *structure, const char *name, uint32_t *out, uint32_t assert_missing) {
    return thug_script_get_checksum(structure,thug_crc32_string(name),out,assert_missing);
}

/* 0x00479070. Alias resolution is shared with the other global getters. */
ThugScriptArray *thug_script_get_global_array(uint32_t name, uint32_t assert_missing) {
    (void)assert_missing;
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    return symbol && symbol->type == 12 ? (ThugScriptArray *)(uintptr_t)symbol->value : NULL;
}
/* 0x00479090. */
ThugScriptArray *thug_script_get_global_array_text(const char *name, uint32_t assert_missing) {
    return thug_script_get_global_array(thug_crc32_string(name),assert_missing);
}
/* 0x00478fb0. Unlike the typed getters, return the resolved raw value for any
 * symbol type. The assertion argument is unused in this executable. */
uint32_t thug_script_get_global_value_text(const char *name, uint32_t assert_missing) {
    (void)assert_missing;
    const ThugScriptSymbol *symbol=thug_script_resolve_symbol(thug_crc32_string(name));
    return symbol ? symbol->value : 0;
}

/* 0x0046cc30. One item is stored inline. The original does not check the
 * array type or bounds; a count other than one uses the supplied index. */
ThugScriptStructure *thug_script_array_structure(const ThugScriptArray *array, int32_t index) {
    if (array->count == 1) return (ThugScriptStructure *)(uintptr_t)array->value_or_items;
    const uint32_t *items = (const uint32_t *)(uintptr_t)array->value_or_items;
    return (ThugScriptStructure *)(uintptr_t)items[index];
}

/* 0x00476b40. Test literal unnamed flags before resolving structure inclusions.
 * Named members never participate. Valid inclusion graphs must be acyclic. */
uint8_t thug_script_has_flag(const ThugScriptStructure *structure, uint32_t flag) {
    for (const ThugScriptComponent *c = structure->first; c; c = c->next) {
        if (c->name || (c->type_and_flags & 0xfe) != 0x1a) continue;
        if (c->value == flag) return 1;
        const ThugScriptSymbol *symbol = thug_script_resolve_symbol(c->value);
        if (symbol && symbol->type == 10 && thug_script_has_flag(
                (const ThugScriptStructure *)(uintptr_t)symbol->value, flag)) return 1;
    }
    return 0;
}

/* 0x00478cf0. Aliases use type 13. An unresolved alias returns the alias entry;
 * missing initial names return NULL. Valid symbol graphs must be acyclic. */
ThugScriptSymbol *thug_script_resolve_symbol(uint32_t name) {
    ThugScriptSymbol *entry = thug_script_symbol_buckets[name & 0xfff];
    while (entry && entry->name != name) entry = entry->next;
    if (entry) {
        while (entry->type == 13) {
            ThugScriptSymbol *target = thug_script_symbol_buckets[entry->value & 0xfff];
            while (target && target->name != entry->value) target = target->next;
            if (!target) return entry;
            entry = target;
        }
    }
    return entry;
}

/* 0x00478f00. The second argument is unused in this specimen. FILD returns
 * an exact signed integer; returning float here would round it prematurely. */
double thug_script_get_global_number(uint32_t name, uint32_t assert_missing) {
    (void)assert_missing;
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (symbol && symbol->type == 1) return (double)(int32_t)symbol->value;
    if (symbol && symbol->type == 2) {
        union { uint32_t word; float value; } number = { .word = symbol->value };
        return number.value;
    }
    return 0;
}

/* 0x00479020. Resolve aliases, then accept only a structure symbol. */
ThugScriptStructure *thug_script_get_global_structure(uint32_t name, uint32_t assert_missing) {
    (void)assert_missing;
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    return symbol && symbol->type == 10 ? (ThugScriptStructure *)(uintptr_t)symbol->value : NULL;
}

static void copy_word(void *destination, const void *source) {
    uint8_t *out = destination; const uint8_t *in = source;
    for (unsigned i = 0; i < 4; ++i) out[i] = in[i];
}

/* 0x00476590, 0x00476860. Normal strings take precedence over localized
 * strings, even if a localized component occurs later. Failed reads preserve
 * the caller's output; the assert target is a bare RET in this specimen. */
uint8_t thug_script_get_text(const ThugScriptStructure *s, uint32_t name, const char **out, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t value;
    if (!thug_script_get_typed(s, name, 3, &value) && !thug_script_get_typed(s, name, 4, &value)) return 0;
    copy_word(out, &value); return 1;
}
uint8_t thug_script_get_array(const ThugScriptStructure *s, uint32_t name, ThugScriptArray **out, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t value;
    if (!thug_script_get_typed(s, name, 12, &value)) return 0;
    copy_word(out, &value); return 1;
}

/* 0x00476a90, 0x00476af0. First match wins, including unnamed literal flags
 * and recursive structure inclusions. A request for name zero matches the
 * component's name before looking at its type or included value. */
ThugScriptComponent *thug_script_find_name_or_flag(const ThugScriptStructure *s, uint32_t name) {
    for (ThugScriptComponent *c = s->first; c; c = c->next) {
        if (c->name == name) return c;
        if (c->name || (c->type_and_flags & 0xfe) != 26) continue;
        if (c->value == name) return c;
        const ThugScriptSymbol *symbol = thug_script_resolve_symbol(c->value);
        if (symbol && symbol->type == 10) {
            ThugScriptComponent *found = thug_script_find_name_or_flag((const ThugScriptStructure *)(uintptr_t)symbol->value, name);
            if (found) return found;
        }
    }
    return NULL;
}
uint32_t thug_script_has_name_or_flag(const ThugScriptStructure *s, uint32_t name) {
    return thug_script_find_name_or_flag(s, name) != NULL;
}

/* 0x004764b0. Scan the whole list: the last successful match wins. Anonymous
 * references to structures participate inline, unless name zero was requested.
 * Types other than integer-to-float conversion are copied as raw words. */
uint8_t thug_script_get_typed(const ThugScriptStructure *structure, uint32_t name, uint32_t type, void *output) {
    uint8_t found = 0;
    for (ThugScriptComponent *component = structure->first; component; component = component->next) {
        uint32_t actual_type = component->type_and_flags >> 1;
        if (component->name == name) {
            if (actual_type == type) { copy_word(output, &component->value); found = 1; }
            else if (actual_type == 1 && type == 2) {
                float value = (float)(int32_t)component->value; copy_word(output, &value); found = 1;
            } else if (actual_type == 13) {
                const ThugScriptSymbol *symbol = thug_script_resolve_symbol(component->value);
                if (symbol && symbol->type == type) { copy_word(output, &symbol->value); found = 1; }
                else if (symbol && symbol->type == 1 && type == 2) {
                    float value = (float)(int32_t)symbol->value; copy_word(output, &value); found = 1;
                }
            }
        } else if (!component->name && actual_type == 13) {
            const ThugScriptSymbol *symbol = thug_script_resolve_symbol(component->value);
            uint32_t value;
            if (symbol && symbol->type == 10
                && thug_script_get_typed((const ThugScriptStructure *)(uintptr_t)symbol->value, name, type, &value)) {
                copy_word(output, &value); found = 1;
            }
        }
    }
    return found;
}

/* 0x004766d0. The assert path calls 0x005480a0, a bare RET in this specimen. */
uint8_t thug_script_get_float(const ThugScriptStructure *structure, uint32_t name, float *output, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t value;
    if (thug_script_get_typed(structure, name, 2, &value)) { copy_word(output, &value); return 1; }
    return 0;
}

/* 0x00478f60. Float symbols use the low word of the CRT's int64 conversion. */
uint32_t thug_script_get_global_integer(uint32_t name, uint32_t assert_missing) {
    (void)assert_missing;
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (symbol && symbol->type == 1) return symbol->value;
    if (symbol && symbol->type == 2) {
        union { uint32_t word; float value; } number = { .word = symbol->value };
        return thug_truncate_low_word(number.value);
    }
    return 0;
}

/* 0x00476630, 0x00476cb0 and 0x004767c0. Failed lookups preserve the output.
 * The assert callee is a bare RET; its differing argument widths have no effect. */
uint8_t thug_script_get_integer(const ThugScriptStructure *s, uint32_t name, uint32_t *out, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t value;
    if (!thug_script_get_typed(s, name, 1, &value)) return 0;
    copy_word(out, &value); return 1;
}
uint8_t thug_script_get_boolean(const ThugScriptStructure *s, uint32_t name, uint32_t *out, uint32_t assert_missing) {
    return thug_script_get_integer(s, name, out, assert_missing);
}
uint8_t thug_script_get_structure(const ThugScriptStructure *s, uint32_t name, ThugScriptStructure **out, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t value;
    if (!thug_script_get_typed(s, name, 10, &value)) return 0;
    copy_word(out, &value); return 1;
}

/* 0x00476950. Return the literal checksum, not its resolved symbol value.
 * Anonymous structure inclusions are traversed only for nonzero requested names. */
uint8_t thug_script_get_checksum(const ThugScriptStructure *s, uint32_t name, uint32_t *out, uint32_t assert_missing) {
    (void)assert_missing;
    uint8_t found = 0;
    for (const ThugScriptComponent *c = s->first; c; c = c->next) {
        if ((c->type_and_flags & 0xfe) != 26) continue;
        if (c->name == name) {
            const ThugScriptSymbol *symbol = name ? NULL : thug_script_resolve_symbol(c->value);
            if (symbol && symbol->type == 10) continue;
            *out = c->value; found = 1;
        } else if (!c->name) {
            const ThugScriptSymbol *symbol = thug_script_resolve_symbol(c->value);
            if (symbol && symbol->type == 10 && thug_script_get_checksum(
                    (const ThugScriptStructure *)(uintptr_t)symbol->value, name, out, 0)) found = 1;
        }
    }
    return found;
}

/* 0x0047ac00. Padding is deliberately left untouched. */
ThugScriptPair *thug_script_pair_initialize(ThugScriptPair *pair) {
    pair->y = pair->x = 0; pair->tag = 0; return pair;
}
static uint32_t quiet_float_word(uint32_t word) {
    /* FLD/FSTP quiet signaling NaNs even when no arithmetic is performed. */
    if ((word & 0x7f800000) == 0x7f800000 && (word & 0x7fffff)) word |= 0x400000;
    return word;
}
/* 0x00476df0. Unlike scalar getters, absence writes two positive zeros.
 * Read both coordinates before either write, retaining overlapping-copy behavior. */
uint8_t thug_script_get_pair(const ThugScriptStructure *s, uint32_t name, ThugScriptPair *out, uint32_t assert_missing) {
    (void)assert_missing;
    uint32_t pointer, x = 0, y = 0;
    uint8_t found = thug_script_get_typed(s, name, 5, &pointer);
    if (found) {
        const ThugScriptPair *source = (const ThugScriptPair *)(uintptr_t)pointer;
        copy_word(&x, &source->x); copy_word(&y, &source->y);
        x = quiet_float_word(x); y = quiet_float_word(y);
    }
    copy_word(&out->x, &x); copy_word(&out->y, &y);
    return found;
}

/* 0x00476fb0. Capture all source coordinates before writing, preserve raw X,
 * and quiet only the Y/Z x87 loads. Missing values leave the output unchanged. */
uint8_t thug_script_get_vector(const ThugScriptStructure *s,uint32_t name,float out[4],uint32_t required) {
    (void)required; uint32_t pointer;
    if (!thug_script_get_typed(s,name,6,&pointer)) return 0;
    const uint32_t *source=(const uint32_t *)(uintptr_t)pointer;
    uint32_t z,x,y; copy_word(&z,source+3); copy_word(&x,source+1); copy_word(&y,source+2);
    z=quiet_float_word(z); y=quiet_float_word(y);
    copy_word(out+1,&y); copy_word(out,&x); out[3]=1; copy_word(out+2,&z); return 1;
}
