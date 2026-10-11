#include "parser.h"
#include "tokens.h"
#include "delivery.h"
#include <stddef.h>

ThugScriptExpression thug_script_parser_expression;
ThugScriptComponent thug_script_parser_value;
uint32_t thug_script_call_native(ThugScriptNativePredicate function, ThugScriptStructure *parameters,
    ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const ThugEventServices *previous = thug_event_services;
    const ThugEventServices services = {diagnostics ? diagnostics : previous ? previous->diagnostics : NULL, memory};
    thug_event_services = &services;
    uint32_t result = function(parameters, script);
    thug_event_services = previous;
    return result;
}
static void set_type(ThugScriptComponent *c, uint8_t type) { c->type_and_flags = (c->type_and_flags & 1) | (type << 1); }
static ThugScriptComponent *new_component(const ThugMemory *memory) {
    return thug_script_component_initialize(memory->allocate(memory->context, 16, 1));
}
static ThugScriptStructure *new_structure(const ThugMemory *memory) {
    return thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
}
static ThugScriptArray *new_array(const ThugMemory *memory) {
    return thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
}
static const uint8_t *skip_lines(const uint8_t *p) {
    while (*p == 1 || *p == 2) p += *p == 1 ? 1 : 5;
    return p;
}

/* 0x00470130. Original arguments: ECX=bytecode, EDX=name, stack=target,args.
 * Unknown tokens do not advance. A script definition supplies its own name. */
const uint8_t *thug_script_parse_named_value(const uint8_t *p, uint32_t name,
    ThugScriptStructure *target, const ThugScriptStructure *arguments, const ThugMemory *memory) {
    const uint8_t *next = p + 1;
    switch (*p) {
    case 3: {
        ThugScriptStructure *s = new_structure(memory);
        next = thug_script_parse_structure(s, p, arguments, memory);
        thug_script_set_structure(target, name, s, memory); return next;
    }
    case 5: {
        memory->temp_scope(memory->context, 1);
        ThugScriptArray *a = new_array(memory);
        memory->temp_scope(memory->context, 0);
        next = thug_script_parse_array(a, p, arguments, memory);
        thug_script_set_array(target, name, a, memory); return next;
    }
    case 9: return next;
    case 0x16: thug_script_set_checksum(target, name, thug_script_read_word(next), memory); return p + 5;
    case 0x17: thug_script_set_integer(target, name, thug_script_read_word(next), memory); return p + 5;
    case 0x1a: thug_script_set_float_bits(target, name, thug_script_read_word(next), memory); return p + 5;
    case 0x1b: case 0x1c: {
        uint32_t count = thug_script_read_word(next);
        if (*p == 0x1b) thug_script_set_string(target, name, (const char *)(p + 5), memory);
        else thug_script_set_local_string(target, name, (const char *)(p + 5), memory);
        return p + 5 + count;
    }
    case 0x1e: {
        uint32_t x = thug_script_read_word(next), y = thug_script_read_word(p + 5), z = thug_script_read_word(p + 9);
        if (name == 0x9d2d0915) {
            union { uint32_t bits; float value; } a = { .bits = x }, b = { .bits = y }, c = { .bits = z };
            if (__builtin_fabsf(a.value) < 0.01f && __builtin_fabsf(b.value) < 0.01f && __builtin_fabsf(c.value) < 0.01f)
                return p + 13;
        }
        thug_script_set_vector_bits(target, name, x, y, z, memory); return p + 13;
    }
    case 0x1f: {
        uint32_t x = thug_script_read_word(next), y = thug_script_read_word(p + 5);
        thug_script_set_pair_bits(target, name, x, y, memory); return p + 9;
    }
    case 0x23: {
        uint32_t script_name = thug_script_read_word(p + 2);
        next = thug_script_skip_script(p + 6);
        thug_script_set_blob(target, script_name, p + 6, (uintptr_t)next - (uintptr_t)(p + 6), memory);
        return next;
    }
    case 0x2c:
        if (arguments) {
            if (!name) thug_script_structure_merge(target, arguments, memory);
            else {
                ThugScriptStructure *s = new_structure(memory);
                thug_script_structure_assign(s, arguments, memory);
                thug_script_set_structure(target, name, s, memory);
            }
        }
        return next;
    case 0x2d: {
        uint32_t key = thug_script_read_word(p + 2);
        const ThugScriptComponent *source = arguments ? thug_script_find_component(arguments, key) : NULL;
        if (source) {
            if (!name && (source->type_and_flags >> 1) == 10)
                thug_script_structure_merge_optional(target, (const ThugScriptStructure *)(uintptr_t)source->value, memory);
            else {
                ThugScriptComponent *copy = new_component(memory);
                thug_script_component_copy(copy, source, 0, memory); copy->name = name;
                thug_script_structure_insert(target, copy, memory);
            }
        }
        return p + 6;
    }
    case 0x30: case 0x38: {
        uint32_t alternate = *p == 0x38;
        ThugScriptComponent *value = new_component(memory);
        next = thug_script_random_value(p + 1, value, alternate);
        value->name = name; thug_script_structure_insert(target, value, memory); return next;
    }
    default: return p;
    }
}

/* 0x004706f0. Output must not already own a value. Unsupported tokens advance
 * one byte without changing it. Script blobs leave the length/padding untouched. */
const uint8_t *thug_script_parse_component_value(const uint8_t *p, const ThugScriptStructure *arguments,
    ThugScriptComponent *out, const ThugMemory *memory) {
    const uint8_t *next = p + 1;
    switch (*p) {
    case 3: {
        ThugScriptStructure *s = new_structure(memory);
        next = thug_script_parse_structure(s, p, arguments, memory);
        set_type(out, 10); out->value = (uintptr_t)s; break;
    }
    case 5: {
        memory->temp_scope(memory->context, 1);
        ThugScriptArray *a = new_array(memory);
        memory->temp_scope(memory->context, 0);
        next = thug_script_parse_array(a, p, arguments, memory);
        set_type(out, 12); out->value = (uintptr_t)a; break;
    }
    case 0x16: case 0x17: case 0x1a:
        set_type(out, *p == 0x16 ? 13 : *p == 0x17 ? 1 : 2);
        out->value = thug_script_read_word(next); return p + 5;
    case 0x1b: case 0x1c: {
        set_type(out, *p == 0x1b ? 3 : 4);
        uint32_t count = thug_script_read_word(next);
        out->value = (uintptr_t)thug_script_string_copy((const char *)(p + 5), memory);
        return p + 5 + count;
    }
    case 0x1e: case 0x1f: {
        uint8_t kind = *p == 0x1e ? 6 : 5;
        set_type(out, kind);
        uint32_t x = thug_script_read_word(next), y = thug_script_read_word(p + 5);
        uint32_t z = kind == 6 ? thug_script_read_word(p + 9) : 0;
        uint32_t *copy = memory->allocate(memory->context, kind == 6 ? 16 : 12, 1);
        if (kind == 6) thug_script_vector_initialize((ThugScriptVector *)copy);
        else thug_script_pair_initialize((ThugScriptPair *)copy);
        out->value = (uintptr_t)copy; copy[1] = x; copy[2] = y;
        if (kind == 6) copy[3] = z;
        return p + (kind == 6 ? 13 : 9);
    }
    case 0x23: {
        out->name = thug_script_read_word(p + 2);
        next = thug_script_skip_script(p + 6); set_type(out, 7);
        uint32_t length = (uintptr_t)next - (uintptr_t)(p + 6);
        memory->temp_scope(memory->context, 1);
        uint8_t *copy = memory->allocate(memory->context, length, 0);
        memory->temp_scope(memory->context, 0);
        for (uint32_t i = 0; i < length; ++i) copy[i] = p[6 + i];
        out->value = (uintptr_t)copy; break;
    }
    case 0x2c:
        if (arguments) {
            ThugScriptStructure *s = new_structure(memory);
            thug_script_structure_assign(s, arguments, memory);
            set_type(out, 10); out->value = (uintptr_t)s;
        }
        break;
    case 0x2d: {
        uint32_t key = thug_script_read_word(p + 2);
        const ThugScriptComponent *source = arguments ? thug_script_find_component(arguments, key) : NULL;
        if (source) thug_script_component_copy(out, source, 0, memory);
        return p + 6;
    }
    case 0x30: case 0x38: return thug_script_random_value(p + 1, out, *p == 0x38);
    }
    return next;
}

static const uint8_t *expression_member(ThugScriptStructure *target, const uint8_t *p,
    const ThugScriptStructure *arguments, uint32_t name, uint8_t merge_structure, const ThugMemory *memory) {
    ThugScriptComponent *c = new_component(memory);
    p = thug_script_parse_expression(p, arguments, c, memory);
    uint8_t kind = c->type_and_flags >> 1;
    if (merge_structure && kind == 10) {
        thug_script_structure_merge_optional(target, (const ThugScriptStructure *)(uintptr_t)c->value, memory);
        thug_script_component_clear(c, memory); memory->release(memory->context, c);
    } else if (!kind) memory->release(memory->context, c);
    else { c->name = name; thug_script_structure_insert(target, c, memory); }
    return p;
}

/* 0x00470f30. Stop before a line terminator, EOF or closing parenthesis. */
const uint8_t *thug_script_parse_parameters(ThugScriptStructure *target, const uint8_t *p,
    const ThugScriptStructure *arguments, const ThugMemory *memory) {
    for (;;) {
        p = thug_script_resolve_branches(p, memory);
        if (*p == 0 || *p == 1 || *p == 2 || *p == 15) return p;
        if (*p == 9) { ++p; continue; }
        if (*p == 3) { p = thug_script_parse_structure(target, p, arguments, memory); continue; }
        if (*p == 14) { p = expression_member(target, p, arguments, 0, 1, memory); continue; }
        if (*p == 0x2c) { ++p; if (arguments) thug_script_structure_merge(target, arguments, memory); continue; }
        if (*p == 0x16) {
            uint32_t name = thug_script_read_word(p + 1);
            const uint8_t *value = thug_script_resolve_branches(p + 5, memory);
            if (*value == 7) {
                value = thug_script_resolve_branches(value + 1, memory);
                p = *value == 14 ? expression_member(target, value, arguments, name, 0, memory)
                    : thug_script_parse_named_value(value, name, target, arguments, memory);
                continue;
            }
        }
        p = thug_script_parse_named_value(p, 0, target, arguments, memory);
    }
}

/* 0x00471860. Anonymous nested braces append directly into the target. Named
 * values may cross line breaks around '='; unassigned names remain flags. */
const uint8_t *thug_script_parse_structure(ThugScriptStructure *target, const uint8_t *p,
    const ThugScriptStructure *arguments, const ThugMemory *memory) {
    ++p;
    for (;;) {
        p = thug_script_resolve_branches(skip_lines(p), memory);
        if (*p == 4) return p + 1;
        if (*p == 1 || *p == 2) { p = skip_lines(p); continue; }
        if (*p == 9) { ++p; continue; }
        if (*p == 3) { p = thug_script_parse_structure(target, p, arguments, memory); continue; }
        if (*p == 14) { p = expression_member(target, p, arguments, 0, 1, memory); continue; }
        if (*p == 0x16) {
            uint32_t name = thug_script_read_word(p + 1);
            const uint8_t *value = thug_script_resolve_branches(skip_lines(p + 5), memory);
            if (*value == 7) {
                value = thug_script_resolve_branches(skip_lines(value + 1), memory);
                p = *value == 14 ? expression_member(target, value, arguments, name, 0, memory)
                    : thug_script_parse_named_value(value, name, target, arguments, memory);
                continue;
            }
        }
        p = thug_script_parse_named_value(p, 0, target, arguments, memory);
    }
}

/* 0x00471b00. The first pass chooses a common type and count. The second pass
 * resolves branches again, so random state advances on both passes. Empty arrays
 * leave the target unchanged. Homogeneous values (or mixed int/float) are required. */
const uint8_t *thug_script_parse_array(ThugScriptArray *target, const uint8_t *p,
    const ThugScriptStructure *arguments, const ThugMemory *memory) {
    const uint8_t *cursor = thug_script_resolve_branches(p + 1, memory);
    uint32_t kind = 0, count = 0;
    while (*cursor != 6) {
        uint8_t token = *cursor;
        switch (token) {
        case 3: kind = 10; break; case 5: kind = 12; break; case 0x16: kind = 13; break;
        case 0x17: case 0x18: if (kind != 2) kind = 1; break;
        case 0x1a: kind = 2; break; case 0x1b: kind = 3; break; case 0x1c: kind = 4; break;
        case 0x1e: kind = 6; break; case 0x1f: kind = 5; break;
        }
        switch (token) {
        case 1: case 2: case 9: cursor = thug_script_next_token(cursor); break;
        case 3: case 5: case 0x16: case 0x17: case 0x18: case 0x1a: case 0x1b: case 0x1c: case 0x1e: case 0x1f:
            ++count; cursor = thug_script_skip_value(cursor); break;
        }
        cursor = thug_script_resolve_branches(cursor, memory);
    }
    if (!kind) return cursor + 1;
    memory->temp_scope(memory->context, 1);
    thug_script_array_set_size(target, count, kind, memory);
    memory->temp_scope(memory->context, 0);
    uint32_t *item = thug_script_array_items(target);
    cursor = thug_script_resolve_branches(p + 1, memory);
    while (*cursor != 6) {
        uint8_t token = *cursor;
        if (kind == 10) {
            if (token == 1 || token == 9) ++cursor;
            else if (token == 2) cursor += 5;
            else if (token == 3) {
                ThugScriptStructure *s = new_structure(memory);
                cursor = thug_script_parse_structure(s, cursor, arguments, memory); *item++ = (uintptr_t)s;
            }
        } else {
            ++cursor;
            if (token == 2) cursor += 4;
            else if ((kind == 1 || kind == 2) && (token == 0x17 || token == 0x18)) {
                uint32_t value = thug_script_read_word(cursor); cursor += 4;
                if (kind == 2) { union { float value; uint32_t bits; } f = { .value = (float)(int32_t)value }; value = f.bits; }
                *item++ = value;
            } else if ((kind == 2 && token == 0x1a) || (kind == 13 && token == 0x16)) {
                *item++ = thug_script_read_word(cursor); cursor += 4;
            } else if ((kind == 3 && token == 0x1b) || (kind == 4 && token == 0x1c)) {
                uint32_t length = thug_script_read_word(cursor); cursor += 4;
                *item++ = (uintptr_t)thug_script_string_copy((const char *)cursor, memory); cursor += length;
            } else if ((kind == 5 && token == 0x1f) || (kind == 6 && token == 0x1e)) {
                uint32_t *copy = memory->allocate(memory->context, kind == 5 ? 12 : 16, 1);
                if (kind == 5) thug_script_pair_initialize((ThugScriptPair *)copy);
                else thug_script_vector_initialize((ThugScriptVector *)copy);
                for (unsigned i = 1; i <= (kind == 5 ? 2u : 3u); ++i) { copy[i] = thug_script_read_word(cursor); cursor += 4; }
                *item++ = (uintptr_t)copy;
            } else if (kind == 12 && token == 5) {
                ThugScriptArray *a = new_array(memory);
                cursor = thug_script_parse_array(a, cursor - 1, arguments, memory); *item++ = (uintptr_t)a;
            }
        }
        cursor = thug_script_resolve_branches(cursor, memory);
    }
    return cursor + 1;
}

/* 0x004712b0. Parse after an opening expression token. The global evaluator is
 * deliberately shared by recursive calls, including native predicate arguments. */
const uint8_t *thug_script_parse_expression(const uint8_t *p, const ThugScriptStructure *arguments,
    ThugScriptComponent *out, const ThugMemory *memory) {
    ThugScriptExpression *e = &thug_script_parser_expression;
    ThugScriptComponent *value = &thug_script_parser_value;
    thug_script_expression_clear_if_needed(e, memory);
    thug_script_expression_set_origin(e, p);
    ++p;
    uint32_t parentheses = 0;
    uint8_t expect_value = 1, previous_value = 0, member_name = 0;
    for (;;) {
        p = thug_script_resolve_branches(p, memory);
        uint8_t token = *p;
        if (token == 1 || token == 6) { ++p; continue; }
        if (token == 2) { p += 5; continue; }
        if (token == 14) {
            if (!expect_value) break;
            ++p; thug_script_expression_open_parenthesis(e); ++parentheses;
            previous_value = 0; expect_value = 1; continue;
        }
        if (token == 15) {
            ++p; if (!parentheses) break;
            thug_script_expression_close_parenthesis(e, memory); --parentheses;
            previous_value = 1; expect_value = 0; continue;
        }
        if (token == 5 || token == 7 || token == 8 || (token >= 10 && token <= 13)
            || token == 18 || token == 20 || token == 50 || token == 51) {
            ++p; thug_script_expression_accept_operator(e, token, memory);
            member_name = token == 8; previous_value = 0; expect_value = 1; continue;
        }
        if (token == 0x17 || token == 0x1a) {
            const uint8_t *next = thug_script_parse_component_value(p, arguments, value, memory);
            if (!expect_value) {
                union { uint32_t bits; float value; } f = { .bits = value->value };
                uint8_t negative = token == 0x17 ? (int32_t)value->value < 0 : f.value < 0;
                if (!negative || !previous_value) break;
                thug_script_expression_accept_operator(e, 10, memory);
                if (token == 0x17) value->value = 0u - value->value;
                else { f.value = -f.value; value->value = f.bits; }
            }
            p = next;
            thug_script_expression_push_value(e, value, memory);
            thug_script_component_clear(value, memory);
        } else if (token == 3 || token == 0x1b || token == 0x1c || token == 0x1e || token == 0x1f || token == 0x30) {
            if (!expect_value) break;
            p = thug_script_parse_component_value(p, arguments, value, memory);
            thug_script_expression_push_value(e, value, memory);
            thug_script_component_clear(value, memory);
        } else if (token == 0x16) {
            if (!expect_value) break;
            p = thug_script_parse_component_value(p, arguments, value, memory);
            const ThugScriptSymbol *symbol = member_name ? NULL : thug_script_resolve_symbol(value->value);
            if (symbol && symbol->type == 8) {
                ThugScriptInstance *script = thug_script_current();
                set_type(value, 1);
                ThugScriptStructure *params = new_structure(memory);
                p = thug_script_parse_parameters(params, p, arguments, memory);
                value->value = thug_script_call_native((ThugScriptNativePredicate)(uintptr_t)symbol->value, params, script, NULL, memory) & 0xff;
                thug_script_structure_destroy(params, memory); thug_script_structure_free(params, memory);
                thug_script_expression_push_value(e, value, memory);
            } else if (!symbol || symbol->type != 9) {
                if (symbol) {
                    switch (symbol->type) {
                    case 1: case 2: case 3: case 4: case 5: case 6: case 10: case 12: case 13:
                        set_type(value, symbol->type == 10 ? 20 : symbol->type == 12 ? 21 : symbol->type);
                        value->value = symbol->value;
                    }
                }
                thug_script_expression_push_value(e, value, memory);
            }
            set_type(value, 0); value->value = 0;
        } else if (token == 0x2d) {
            if (!expect_value) break;
            uint32_t name = thug_script_read_word(p + 2); p += 6;
            const ThugScriptComponent *source = arguments ? thug_script_find_component(arguments, name) : NULL;
            if (source) {
                set_type(value, source->type_and_flags >> 1); value->value = source->value;
                thug_script_component_resolve(value); thug_script_component_borrow(value);
                thug_script_expression_push_value(e, value, memory); set_type(value, 0); value->value = 0;
            }
        } else if (token == 0x2c) {
            if (!expect_value) break;
            ++p;
            if (arguments) {
                set_type(value, 20); value->value = (uintptr_t)arguments;
                thug_script_expression_push_value(e, value, memory);
            }
        } else continue; /* Unsupported grammar does not advance in the original. */
        previous_value = 1; expect_value = 0;
    }
    thug_script_expression_finish(e, out, memory);
    return p;
}
