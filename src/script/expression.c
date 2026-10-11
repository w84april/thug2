#include "expression.h"
#include <stddef.h>

_Static_assert(sizeof(ThugScriptExpression) == 0x1f8, "Expression layout");
_Static_assert(offsetof(ThugScriptExpression, value_index) == 0x140, "Value stack index");
_Static_assert(offsetof(ThugScriptExpression, operators) == 0x144, "Operator stack");
_Static_assert(offsetof(ThugScriptExpression, operator_index) == 0x1e4, "Operator stack index");
_Static_assert(offsetof(ThugScriptExpression, error) == 0x1f0, "Expression error");

/* Original string literals 0x00647b50 / 0x00647b68, relocated by the C linker. */
const char thug_expression_error_operator_overflow[] = "Operator stack overflow";
const char thug_expression_error_value_overflow[] = "Value stack overflow";

/* 0x0046d1c0. Clear all slots, including those beyond value_index. Origin,
 * initialized, component metadata and object padding retain their old bytes. */
void thug_script_expression_clear(ThugScriptExpression *e, const ThugMemory *memory) {
    for (unsigned i = 0; i < 20; ++i) thug_script_component_clear(&e->values[i], memory);
    e->value_index = 0;
    e->operator_index = 0;
    for (unsigned i = 0; i < 20; ++i) {
        e->operators[i].opcode = 0;
        e->operators[i].parentheses = 0;
    }
    e->has_operator = 0;
    e->error = NULL;
}
/* 0x0046d220. This predicate deliberately does not inspect other slots or flags. */
void thug_script_expression_clear_if_needed(ThugScriptExpression *e, const ThugMemory *memory) {
    if (e->value_index || (e->values[0].type_and_flags & 0xfe) || e->operator_index || e->error)
        thug_script_expression_clear(e, memory);
}
/* 0x0046d250 / 0x0046d260. Error assignment occurs after releasing stack values. */
void thug_script_expression_set_origin(ThugScriptExpression *e, const uint8_t *origin) { e->origin = origin; }
void thug_script_expression_set_error(ThugScriptExpression *e, const char *error, const ThugMemory *memory) {
    thug_script_expression_clear(e, memory);
    e->error = error;
}
/* 0x0046d2b0. Index zero is the sentinel, so this stack accepts 19 pushes.
 * The original uses a signed comparison after a wrapping 32-bit increment. */
void thug_script_expression_push_operator(ThugScriptExpression *e, uint32_t opcode, const ThugMemory *memory) {
    ++e->operator_index;
    if ((int32_t)e->operator_index >= 20) {
        thug_script_expression_set_error(e, thug_expression_error_operator_overflow, memory);
        return;
    }
    e->operators[e->operator_index].opcode = opcode;
    e->operators[e->operator_index].parentheses = 0;
    e->has_operator = 1;
}
/* 0x0046d310. An empty slot zero is reused; other pushes advance first. The
 * copy routine controls ownership and source/destination alias behavior. */
void thug_script_expression_push_value(ThugScriptExpression *e, const ThugScriptComponent *value, const ThugMemory *memory) {
    if (e->value_index || (e->values[0].type_and_flags & 0xfe)) {
        ++e->value_index;
        if ((int32_t)e->value_index >= 20) {
            thug_script_expression_set_error(e, thug_expression_error_value_overflow, memory);
            return;
        }
    }
    thug_script_component_copy(&e->values[e->value_index], value, 0, memory);
}
/* 0x0046d370. Parentheses belong to the current operator and wrap as uint32. */
void thug_script_expression_open_parenthesis(ThugScriptExpression *e) {
    ++e->operators[e->operator_index].parentheses;
}
/* 0x0046d380. Constructor: initialize components before the common cleanup. */
ThugScriptExpression *thug_script_expression_initialize(ThugScriptExpression *e, const ThugMemory *memory) {
    for (unsigned i = 0; i < 20; ++i) thug_script_component_initialize(&e->values[i]);
    thug_script_expression_clear(e, memory);
    e->initialized = 1;
    return e;
}
/* 0x0046d3c0 is a tail jump to the same cleanup. It does not free this object. */
void thug_script_expression_destroy(ThugScriptExpression *e, const ThugMemory *memory) {
    thug_script_expression_clear(e, memory);
}

/* Error literals referenced by the original evaluator; addresses are provenance,
 * not runtime pointers. */
const char thug_expression_error_6482c8[] = "Not enough values in stack to execute operation";
const char thug_expression_error_6482ac[] = "Non-zero parentheses count";
const char thug_expression_error_648288[] = "Tried to execute with no operator";
const char thug_expression_error_64825c[] = "Second arg cannot be added to an integer";
const char thug_expression_error_648234[] = "Second arg cannot be added to a float";
const char thug_expression_error_648208[] = "Second arg cannot be added to a checksum";
const char thug_expression_error_6481e0[] = "Second arg cannot be added to a vector";
const char thug_expression_error_6481b8[] = "Second arg cannot be added to a pair";
const char thug_expression_error_648194[] = "Result of string addition too long";
const char thug_expression_error_64816c[] = "Second arg cannot be added to a string";
const char thug_expression_error_648140[] = "Result of local-string addition too long";
const char thug_expression_error_648110[] = "Second arg cannot be added to a local-string";
const char thug_expression_error_6480d4[] = "Structure add operator requires 2nd arg to be a structure";
const char thug_expression_error_648098[] = "Array add operator requires 2nd arg to be an array as well";
const char thug_expression_error_648070[] = "Addition not supported for this type";
const char thug_expression_error_648040[] = "Second arg cannot be subtracted from an integer";
const char thug_expression_error_648010[] = "Second arg cannot be subtracted from a float";
const char thug_expression_error_647fe0[] = "Second arg cannot be subtracted from a vector";
const char thug_expression_error_647fb4[] = "Second arg cannot be subtracted from a pair";
const char thug_expression_error_647f58[] = "Structure minus operator requires 2nd arg to be a name, an array of names, or a structure";
const char thug_expression_error_647f00[] = "Subtracting an array from a structure requires the array to be an array of names";
const char thug_expression_error_647ed8[] = "Subtraction not supported for this type";
const char thug_expression_error_647ea8[] = "Second arg cannot be multiplied by an integer";
const char thug_expression_error_647e7c[] = "Second arg cannot be multiplied by a float";
const char thug_expression_error_647e50[] = "Vector cannot be multiplied by second arg";
const char thug_expression_error_647e28[] = "Pair cannot be multiplied by second arg";
const char thug_expression_error_647dfc[] = "Multiplication not supported for this type";
const char thug_expression_error_647de0[] = "Integer division by zero";
const char thug_expression_error_647dc4[] = "Float division by zero";
const char thug_expression_error_647d9c[] = "Integer cannot be divided by second arg";
const char thug_expression_error_647d74[] = "Float cannot be divided by second arg";
const char thug_expression_error_647d4c[] = "Vector cannot be divided by second arg";
const char thug_expression_error_647d24[] = "Pair cannot be divided by second arg";
const char thug_expression_error_647cfc[] = "Division not supported for this type";
const char thug_expression_error_647cc4[] = "Vector can only be dot producted with another vector";
const char thug_expression_error_647c90[] = "Pair can only be dot producted with another pair";
const char thug_expression_error_647c58[] = "Structure dot operator requires 2nd arg to be a name";
const char thug_expression_error_647c30[] = "Dot product not supported for this type";
const char thug_expression_error_647bfc[] = "Array element operator not supported for this type";
const char thug_expression_error_647be0[] = "[] index must be an integer";
const char thug_expression_error_647bc8[] = "[] index out of range";
const char thug_expression_error_647b98[] = "Array type cannot be accessed using [] yet ...";
const char thug_expression_error_647b80[] = "Operator not supported";
const char thug_expression_error_64831c[] = "Not enough close parentheses";
const char thug_expression_error_6482f8[] = "Too many operators in expression";

#include "../platform/math.h"
ThugScriptComponent thug_expression_temporary; /* Original 0x006f2348. */
/* Original table at 0x0067d908. The parser supplies tokens within this range. */
const int32_t thug_expression_precedence[64] = {
    -1,-1,-1,-1,-1,100,-1,76,100,-1,98,98,99,100,-1,-1,
    -1,-1,80,79,78,77,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,
    -1,-1,58,60,59,90,89,-1,-1,-1,-1,-1,-1,-1,-1,-1
};
#define ERROR(address) thug_script_expression_set_error(e, thug_expression_error_##address, memory)
static uint8_t type(const ThugScriptComponent *c) { return c->type_and_flags >> 1; }
static void temporary_type(uint8_t kind) {
    thug_expression_temporary.type_and_flags = (thug_expression_temporary.type_and_flags & 1) | (kind << 1);
}
static double numeric(const ThugScriptComponent *c) {
    if (type(c) == 1) return (double)(int32_t)c->value;
    union { uint32_t bits; float value; } f = { .bits = c->value };
    return f.value;
}
/* A double intermediate can erase a tiny term that decides a PC=24 halfway
 * result (for example, FILD(16777217) plus the smallest positive float).
 * Error-free sum/product transforms retain that direction before rounding. */
static double round_result(double value, double residual) {
    union { double value; uint64_t bits; } n = { .value = value };
    if (__builtin_isfinite(value) && (n.bits & UINT64_C(0x1fffffff)) == UINT64_C(0x10000000) && residual != 0) {
        if (value < 0) residual = -residual;
        n.bits &= ~UINT64_C(0x1fffffff);
        if (residual > 0) n.bits += UINT64_C(0x20000000);
        return n.value;
    }
    return thug_platform_round_x87_single(value);
}
static double product_error(double a, double b, double product) {
    double split = 134217729.0 * a, high_a = split - (split - a), low_a = a - high_a;
    split = 134217729.0 * b;
    double high_b = split - (split - b), low_b = b - high_b;
    return ((high_a * high_b - product) + high_a * low_b + low_a * high_b) + low_a * low_b;
}
static double arithmetic(uint32_t opcode, double a, double b) {
    if (opcode == 10 || opcode == 11) {
        if (opcode == 10) b = -b;
        double sum = a + b, rounded_b = sum - a;
        return round_result(sum, (a - (sum - rounded_b)) + (b - rounded_b));
    }
    if (opcode == 12) {
        double quotient = a / b, product = quotient * b;
        return round_result(quotient, ((a - product) - product_error(quotient, b, product)) / b);
    }
    double product = a * b;
    return round_result(product, product_error(a, b, product));
}
static void temporary_float(double value) {
    union { float value; uint32_t bits; } f = { .value = (float)value };
    thug_expression_temporary.value = f.bits;
}
static float *new_coordinates(uint8_t kind, const ThugMemory *memory) {
    temporary_type(kind);
    void *p = memory->allocate(memory->context, kind == 5 ? 12 : 16, 1);
    if (kind == 5) thug_script_pair_initialize(p); else thug_script_vector_initialize(p);
    thug_expression_temporary.value = (uintptr_t)p;
    return p;
}
static ThugScriptStructure *new_structure(const ThugMemory *memory) {
    temporary_type(10);
    ThugScriptStructure *s = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
    thug_expression_temporary.value = (uintptr_t)s;
    return s;
}
static const float *coordinates(const ThugScriptComponent *c) { return (const float *)(uintptr_t)c->value; }
static uint32_t length(const char *text) { uint32_t n = 0; while (text[n]) ++n; return n; }

/* 0x0046d450. Execute the top binary operation, retaining the original typed
 * dispatch, ownership and finalization order. Indices and owned graphs must be
 * valid. Integer IDIV overflow traps, as it does in the original executable. */
void thug_script_expression_execute(ThugScriptExpression *e, const ThugMemory *memory) {
    if ((int32_t)e->value_index < 1) { ERROR(6482c8); return; }
    if (e->operators[e->operator_index].parentheses) { ERROR(6482ac); return; }
    uint32_t opcode = e->operators[e->operator_index].opcode;
    if (!opcode) { ERROR(648288); return; }
    ThugScriptComponent *b = &e->values[e->value_index], *a = b - 1;
    ThugScriptComponent *t = &thug_expression_temporary;
    uint8_t ka = type(a), kb = type(b);
    temporary_type(0); t->value = 0;
    switch (opcode) {
    case 5:
        if (ka != 12 && ka != 21) { ERROR(647bfc); break; }
        if (kb != 1) { ERROR(647be0); break; }
        if (b->value >= ((ThugScriptArray *)(uintptr_t)a->value)->count) { ERROR(647bc8); break; }
        thug_script_array_component((const ThugScriptArray *)(uintptr_t)a->value, b->value, t, ka == 21, memory);
        if (!type(t)) ERROR(647b98);
        break;
    case 7: case 18: case 20:
        temporary_type(1);
        t->value = opcode == 7 ? thug_script_component_equal(a, b)
            : opcode == 18 ? thug_script_component_less(a, b) : thug_script_component_greater(a, b);
        break;
    case 8:
        if (ka == 5 || ka == 6) {
            if (ka != kb) {
                if (ka == 5) ERROR(647c90); else ERROR(647cc4);
                break;
            }
            temporary_type(2);
            const float *x = coordinates(a), *y = coordinates(b);
            double dot = arithmetic(13, x[1], y[1]);
            dot = arithmetic(11, dot, arithmetic(13, x[2], y[2]));
            if (ka == 6) dot = arithmetic(11, dot, arithmetic(13, x[3], y[3]));
            temporary_float(dot);
        } else if (ka == 10 || ka == 20) {
            if (kb != 13) { ERROR(647c58); break; }
            const ThugScriptComponent *member = thug_script_find_component((const ThugScriptStructure *)(uintptr_t)a->value, b->value);
            if (member) thug_script_component_copy(t, member, ka == 20, memory);
        } else ERROR(647c30);
        break;
    case 10: case 11: case 12: case 13:
        if (opcode == 12) {
            if (kb == 1 && !b->value) { ERROR(647de0); break; }
            if (kb == 2) {
                double divisor = numeric(b); if (divisor < 0) divisor = -divisor;
                union { uint32_t bits; float value; } cutoff = { .bits = 0x358637bd };
                if (divisor < cutoff.value) { ERROR(647dc4); break; }
            }
        }
        if ((ka == 1 || ka == 2) && (kb == 1 || kb == 2)) {
            if (ka == 1 && kb == 1) {
                temporary_type(1);
                if (opcode == 10) t->value = a->value - b->value;
                else if (opcode == 11) t->value = a->value + b->value;
                else if (opcode == 13) t->value = a->value * b->value;
                else {
                    if (a->value == 0x80000000 && b->value == 0xffffffff) __builtin_trap();
                    t->value = (int32_t)a->value / (int32_t)b->value;
                }
            } else {
                temporary_type(2);
                temporary_float(arithmetic(opcode, numeric(a), numeric(b)));
            }
            break;
        }
        if ((opcode == 10 || opcode == 11) && (ka == 5 || ka == 6) && ka == kb) {
            float *out = new_coordinates(ka, memory);
            for (unsigned i = 1; i <= (ka == 5 ? 2u : 3u); ++i)
                out[i] = (float)arithmetic(opcode, coordinates(a)[i], coordinates(b)[i]);
            break;
        }
        if ((opcode == 12 || opcode == 13) && (ka == 5 || ka == 6) && (kb == 1 || kb == 2)) {
            float *out = new_coordinates(ka, memory);
            for (unsigned i = 1; i <= (ka == 5 ? 2u : 3u); ++i)
                out[i] = (float)arithmetic(opcode, coordinates(a)[i], numeric(b));
            break;
        }
        if (opcode == 13 && (ka == 1 || ka == 2) && (kb == 5 || kb == 6)) {
            float *out = new_coordinates(kb, memory);
            for (unsigned i = 1; i <= (kb == 5 ? 2u : 3u); ++i)
                out[i] = (float)arithmetic(13, numeric(a), coordinates(b)[i]);
            break;
        }
        if (opcode == 13 && ka == 6 && kb == 6) {
            float *out = new_coordinates(6, memory);
            for (unsigned i = 1; i <= 3; ++i) {
                unsigned j = i % 3 + 1, k = j % 3 + 1;
                const float *x = coordinates(a), *y = coordinates(b);
                out[i] = (float)arithmetic(10, arithmetic(13, x[j], y[k]), arithmetic(13, x[k], y[j]));
            }
            break;
        }
        if (opcode == 11 && (ka == 3 || ka == 4) && kb == ka) {
            const char *x = (const char *)(uintptr_t)a->value, *y = (const char *)(uintptr_t)b->value;
            uint32_t na = length(x), nb = length(y);
            if (na + nb + 1 >= 201) {
                if (ka == 3) ERROR(648194); else ERROR(648140);
                break;
            }
            temporary_type(ka);
            char joined[200];
            for (uint32_t i = 0; i < na; ++i) joined[i] = x[i];
            for (uint32_t i = 0; i <= nb; ++i) joined[na + i] = y[i];
            t->value = (uintptr_t)thug_script_string_copy(joined, memory);
            break;
        }
        if (opcode == 11 && ka == 13 && (kb == 1 || kb == 13)) {
            temporary_type(13); t->value = a->value + b->value; break;
        }
        if (opcode == 11 && (ka == 12 || ka == 21) && (kb == 12 || kb == 21)) {
            ThugScriptArray *out = thug_script_array_initialize(memory->allocate(memory->context, 12, 1));
            t->value = (uintptr_t)out; temporary_type(12);
            ThugScriptArray *x = (ThugScriptArray *)(uintptr_t)a->value, *y = (ThugScriptArray *)(uintptr_t)b->value;
            uint32_t nx = x->count, ny = y->count;
            if (!nx) thug_script_array_copy(out, y, memory);
            else if (!ny) thug_script_array_copy(out, x, memory);
            else {
                uint8_t kind = ((const uint8_t *)&x->unknown_0)[1];
                thug_script_array_set_size(out, nx + ny, kind, memory);
                thug_script_array_copy_items(thug_script_array_items(out), thug_script_array_items(x), nx, kind, memory);
                thug_script_array_copy_items(thug_script_array_items(out) + nx, thug_script_array_items(y), ny, kind, memory);
            }
            break;
        }
        if ((opcode == 10 || opcode == 11) && (ka == 10 || ka == 20)) {
            if (opcode == 11 && (kb == 10 || kb == 20)) {
                ThugScriptStructure *out = new_structure(memory);
                thug_script_structure_merge_optional(out, (const ThugScriptStructure *)(uintptr_t)a->value, memory);
                thug_script_structure_merge_optional(out, (const ThugScriptStructure *)(uintptr_t)b->value, memory);
                break;
            }
            if (opcode == 10 && (kb == 13 || kb == 10 || kb == 20 || kb == 12 || kb == 21)) {
                ThugScriptArray *array = (ThugScriptArray *)(uintptr_t)b->value;
                if ((kb == 12 || kb == 21) && ((const uint8_t *)&array->unknown_0)[1] != 0
                    && ((const uint8_t *)&array->unknown_0)[1] != 13) { ERROR(647f00); break; }
                ThugScriptStructure *out = new_structure(memory);
                thug_script_structure_merge_optional(out, (const ThugScriptStructure *)(uintptr_t)a->value, memory);
                if (kb == 13) {
                    thug_script_remove_name(out, b->value, memory);
                    thug_script_remove_unnamed_value(out, b->value, memory);
                } else if (kb == 12 || kb == 21) {
                    for (uint32_t i = 0; i < array->count; ++i) {
                        thug_script_remove_name(out, (uintptr_t)thug_script_array_structure(array, i), memory);
                        thug_script_remove_unnamed_value(out, (uintptr_t)thug_script_array_structure(array, i), memory);
                    }
                } else {
                    const ThugScriptStructure *right = (const ThugScriptStructure *)(uintptr_t)b->value;
                    for (const ThugScriptComponent *c = thug_script_next_component(right, NULL); c; c = thug_script_next_component(right, c)) {
                        if (c->name) thug_script_remove_typed(out, c->name, type(c), memory);
                        else if (type(c) == 13) {
                            thug_script_remove_name(out, c->value, memory);
                            thug_script_remove_unnamed_value(out, c->value, memory);
                        }
                    }
                }
                break;
            }
        }
        /* The error strings and their type-specific selection are observable. */
        if (opcode == 10) {
            switch (ka) {
            case 1: ERROR(648040); break; case 2: ERROR(648010); break;
            case 5: ERROR(647fb4); break; case 6: ERROR(647fe0); break;
            case 10: case 20: ERROR(647f58); break; default: ERROR(647ed8); break;
            }
        } else if (opcode == 11) {
            switch (ka) {
            case 1: ERROR(64825c); break; case 2: ERROR(648234); break;
            case 3: ERROR(64816c); break; case 4: ERROR(648110); break;
            case 5: ERROR(6481b8); break; case 6: ERROR(6481e0); break;
            case 10: case 20: ERROR(6480d4); break; case 12: case 21: ERROR(648098); break;
            case 13: ERROR(648208); break; default: ERROR(648070); break;
            }
        } else if (opcode == 12) {
            switch (ka) {
            case 1: ERROR(647d9c); break; case 2: ERROR(647d74); break;
            case 5: ERROR(647d24); break; case 6: ERROR(647d4c); break; default: ERROR(647cfc); break;
            }
        } else {
            switch (ka) {
            case 1: ERROR(647ea8); break; case 2: ERROR(647e7c); break;
            case 5: ERROR(647e28); break; case 6: ERROR(647e50); break; default: ERROR(647dfc); break;
            }
        }
        break;
    case 50: case 51: {
        temporary_type(1);
        uint32_t right = thug_script_component_truth(b), left = thug_script_component_truth(a);
        t->value = opcode == 50 ? right | left : right & left;
        break;
    }
    default: ERROR(647b80); break;
    }
    /* Switch errors clear the stacks, but still reach this suffix. In particular,
     * value_index then underflows to UINT32_MAX. Guard errors returned above. */
    thug_script_component_clear(a, memory);
    thug_script_component_clear(b, memory);
    a->type_and_flags = (a->type_and_flags & 1) | (t->type_and_flags & 0xfe);
    a->value = t->value;
    temporary_type(0); t->value = 0;
    --e->value_index;
    e->operators[e->operator_index].opcode = 0;
    if (!e->operator_index) e->has_operator = 0; else --e->operator_index;
}
/* 0x0046eb70. Equal operators execute first. After an execution error the new
 * operator is still pushed, matching the original control flow. */
void thug_script_expression_accept_operator(ThugScriptExpression *e, uint32_t opcode, const ThugMemory *memory) {
    if (e->has_operator) {
        while (!e->operators[e->operator_index].parentheses) {
            uint32_t old = e->operators[e->operator_index].opcode;
            if (old != opcode && thug_expression_precedence[old] < thug_expression_precedence[opcode]) break;
            thug_script_expression_execute(e, memory);
            if (!e->has_operator) break;
        }
    }
    thug_script_expression_push_operator(e, opcode, memory);
}
/* 0x0046ebf0. Closing an unmatched parenthesis reaches the normal error path. */
void thug_script_expression_close_parenthesis(ThugScriptExpression *e, const ThugMemory *memory) {
    while (!e->operators[e->operator_index].parentheses) {
        thug_script_expression_execute(e, memory);
        if (e->error) return;
    }
    --e->operators[e->operator_index].parentheses;
}
/* 0x0046ec40. A borrowed final structure/array is owned temporarily for the deep
 * output copy, then made borrowed again before clearing the expression slot. */
uint8_t thug_script_expression_finish(ThugScriptExpression *e, ThugScriptComponent *out, const ThugMemory *memory) {
    for (;;) {
        if (e->operators[e->operator_index].parentheses) { ERROR(64831c); return 0; }
        if (!e->value_index) break;
        thug_script_expression_execute(e, memory);
        if (e->error) return 0;
    }
    if (e->operators[0].opcode || e->operator_index) { ERROR(6482f8); return 0; }
    if (thug_script_component_is_borrowed(&e->values[0])) {
        thug_script_component_own(&e->values[0]);
        thug_script_component_copy(out, &e->values[0], 0, memory);
        thug_script_component_borrow(&e->values[0]);
    } else thug_script_component_copy(out, &e->values[0], 0, memory);
    thug_script_component_clear(&e->values[0], memory);
    return 1;
}
#undef ERROR
