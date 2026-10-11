#include "symbols.h"
#include "tokens.h"
#include "../core/checksum.h"
#include <stddef.h>

ThugScriptSymbol *thug_script_symbol_iteration_entry;
uint32_t thug_script_symbol_iteration_bucket;

/* 0x00478cc0. Unlike resolve_symbol, this does not follow checksum aliases. */
ThugScriptSymbol *thug_script_symbol_find(uint32_t name) {
    ThugScriptSymbol *s = thug_script_symbol_buckets[name & 0xfff];
    while (s && s->name != name) s = s->next;
    return s;
}

/* 0x00478dc0. Prepend without changing the symbol's flags or payload. */
void thug_script_symbol_insert(ThugScriptSymbol *s) {
    uint32_t bucket = s->name & 0xfff;
    s->next = thug_script_symbol_buckets[bucket];
    thug_script_symbol_buckets[bucket] = s;
}

/* 0x00478d60. Match identity, not name. An absent symbol remains untouched. */
void thug_script_symbol_unlink(ThugScriptSymbol *s) {
    uint32_t bucket = s->name & 0xfff;
    ThugScriptSymbol *entry = thug_script_symbol_buckets[bucket], *previous = NULL;
    while (entry) {
        if (entry == s) {
            if (previous) previous->next = entry->next;
            else thug_script_symbol_buckets[bucket] = entry->next;
            entry->next = NULL;
            return;
        }
        previous = entry; entry = entry->next;
    }
}

/* 0x00478e50. A null previous restarts traversal. End resets both globals. */
ThugScriptSymbol *thug_script_symbol_iterate(const ThugScriptSymbol *previous) {
    ThugScriptSymbol *entry;
    uint32_t bucket;
    if (!previous) {
        bucket = 0; thug_script_symbol_iteration_bucket = 0;
        entry = thug_script_symbol_buckets[0];
    } else {
        entry = previous->next;
        bucket = thug_script_symbol_iteration_bucket;
        if (entry) { thug_script_symbol_iteration_entry = entry; return entry; }
        entry = thug_script_symbol_buckets[bucket + 1]; ++bucket;
    }
    for (;;) {
        if (bucket >= 4096) break;
        if (entry) {
            thug_script_symbol_iteration_bucket = bucket;
            thug_script_symbol_iteration_entry = entry; return entry;
        }
        entry = thug_script_symbol_buckets[bucket + 1]; ++bucket;
    }
    thug_script_symbol_iteration_bucket = 0;
    thug_script_symbol_iteration_entry = NULL;
    return NULL;
}

/* 0x00479110. The original generic heap route with successful allocation.
 * Bits 3..7 and bytes 2..3 survive construction. Duplicate names are permitted. */
ThugScriptSymbol *thug_script_symbol_create(uint32_t name, const ThugMemory *memory) {
    ThugScriptSymbol *s = memory->allocate(memory->context, 20, 1);
    s->name = 0; s->flags &= 0xf8; s->type = 0;
    s->value = 0; s->next = NULL; s->unknown_8 = 0;
    s->name = name; s->flags |= 1;
    s->next = thug_script_symbol_buckets[name & 0xfff];
    thug_script_symbol_buckets[name & 0xfff] = s;
    return s;
}

/* 0x004711d0. Always unlink first. Bit 2 preserves both the symbol and its
 * payload; other entries dispose the type-specific payload before the symbol. */
void thug_script_symbol_destroy(ThugScriptSymbol *s, const ThugMemory *memory) {
    thug_script_symbol_unlink(s);
    if (s->flags & 4) return;
    void *value = (void *)(uintptr_t)s->value;
    switch (s->type) {
    case 3: case 4: thug_script_string_release(value, memory); break;
    case 5: case 6: memory->release(memory->context, value); break;
    case 7: if (value) memory->release(memory->context, value); break;
    case 10:
        if (value) {
            thug_script_structure_destroy(value, memory);
            thug_script_structure_free(value, memory);
        }
        break;
    case 12:
        thug_script_array_clear(value, memory);
        value = (void *)(uintptr_t)s->value;
        if (value) {
            thug_script_array_clear_storage(value, memory);
            memory->release(memory->context, value);
        }
        break;
    }
    s->value = 0;
    memory->release(memory->context, s);
}

/* 0x00472240. Original ECX=bytecode, stack=name,filename. Component payloads
 * transfer into the symbol; freeing the temporary must not clear that payload. */
const uint8_t *thug_script_register_value(const uint8_t *p, uint32_t name,
    const char *filename, const ThugMemory *memory) {
    ThugScriptSymbol *symbol = thug_script_symbol_create(name, memory);
    symbol->unknown_8 = thug_crc32_string(filename);
    if (*p == 3) {
        symbol->type = 10;
        ThugScriptStructure *s = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
        symbol->value = (uintptr_t)s;
        return thug_script_parse_structure(s, p, NULL, memory);
    }
    if (*p == 5) {
        symbol->type = 12;
        ThugScriptArray *a = thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
        symbol->value = (uintptr_t)a;
        return thug_script_parse_array(a, p, NULL, memory);
    }
    if (*p == 14 || *p == 0x16 || *p == 0x17 || (*p >= 0x1a && *p <= 0x1c) || *p == 0x1e || *p == 0x1f) {
        ThugScriptComponent *c = thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
        p = *p == 14 ? thug_script_parse_expression(p, NULL, c, memory)
                    : thug_script_parse_component_value(p, NULL, c, memory);
        symbol->type = c->type_and_flags >> 1; symbol->value = c->value;
        c->value = 0; memory->release(memory->context, c);
    }
    return p;
}

/* 0x0046f960. Excludes line tokens and END_SCRIPT itself. Token payload bytes
 * participate unchanged, including bytes equal to line or terminator tokens. */
uint32_t thug_script_body_checksum(const uint8_t *p) {
    uint32_t crc = 0xffffffff;
    while (*p != 0x24) {
        const uint8_t *next = thug_script_next_token(p);
        if (*p != 1 && *p != 2) crc = thug_crc32_extend_buffer(p, (uintptr_t)next - (uintptr_t)p, crc);
        p = next;
    }
    return crc;
}
