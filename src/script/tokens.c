#include "tokens.h"

/* 0x0046f810, 0x0046f840. Byte stores preserve unaligned/overlapping writes. */
uint8_t *thug_script_write_word(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) *p++ = (uint8_t)(value >> (i*8));
    return p;
}
uint8_t *thug_script_write_half(uint8_t *p, uint32_t value) {
    *p++ = (uint8_t)value; *p++ = (uint8_t)(value >> 8); return p;
}

/* 0x0046f800. Unaligned little-endian read; only AX is the original result. */
uint16_t thug_script_read_half(const uint8_t *p) { return (uint16_t)p[0] | (uint16_t)p[1] << 8; }
/* 0x0046f850. Consume ordinary and numbered line tokens only. */
const uint8_t *thug_script_skip_lines(const uint8_t *p) {
    while (*p == 1 || *p == 2) p += *p == 1 ? 1 : 5;
    return p;
}

/* 0x0046f7e0. Explicit little-endian, unaligned reads. */
uint32_t thug_script_read_word(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static const uint8_t *advance(const uint8_t *p, uint32_t count) {
    return (const uint8_t *)((uintptr_t)p + count);
}
/* 0x0046f690. Unknown tokens (including zero) return the same pointer. Random
 * choice headers advance over their tables, without resolving any branch. */
const uint8_t *thug_script_next_token(const uint8_t *p) {
    switch (*p) {
    case 1: case 3: case 4: case 5: case 6: case 7: case 8: case 9:
    case 10: case 11: case 12: case 13: case 14: case 15:
    case 0x11: case 0x12: case 0x13: case 0x14: case 0x15:
    case 0x20: case 0x21: case 0x22: case 0x23: case 0x24: case 0x25:
    case 0x26: case 0x27: case 0x28: case 0x29: case 0x2c: case 0x2d:
    case 0x30: case 0x32: case 0x33: case 0x34: case 0x35: case 0x36:
    case 0x38: case 0x39: case 0x3a: case 0x3b: case 0x3c: case 0x3d:
    case 0x3e: case 0x3f: case 0x42: case 0x45:
        return p + 1;
    case 2: case 0x16: case 0x17: case 0x18: case 0x1a:
    case 0x2e: case 0x43: case 0x44: case 0x46:
        return p + 5;
    case 0x1b: case 0x1c:
        return advance(p, thug_script_read_word(p + 1) + 5);
    case 0x1e: return p + 13;
    case 0x1f: return p + 9;
    case 0x2b:
        p += 5;
        while (*p) ++p;
        return p + 1;
    case 0x2f: case 0x37: case 0x40: case 0x41:
        return advance(p, thug_script_read_word(p + 1) * 6 + 5);
    case 0x47: case 0x48: case 0x49: return p + 3;
    default: return p;
    }
}
/* 0x0046fd60 (input in EAX). A compound value is skipped by balancing its
 * own delimiter kind while using the token decoder for payload boundaries. */
const uint8_t *thug_script_skip_value(const uint8_t *p) {
    uint8_t type = *p;
    switch (type) {
    case 3: case 5: {
        uint32_t depth = 1;
        do {
            p = thug_script_next_token(p);
            if (*p == type) ++depth;
            else if (*p == type + 1) --depth;
        } while (depth);
        return p + 1;
    }
    case 0x16: case 0x17: case 0x18: case 0x1a: return p + 5;
    case 0x1b: case 0x1c: return advance(p, thug_script_read_word(p + 1) + 5);
    case 0x1e: return p + 13;
    case 0x1f: return p + 9;
    default: return p;
    }
}
/* 0x0046f920. Includes END_SCRIPT and exactly one following numbered-line
 * token, if present. It does not consume an ordinary newline afterward. */
const uint8_t *thug_script_skip_script(const uint8_t *p) {
    while (*p != 0x24) p = thug_script_next_token(p);
    p = thug_script_next_token(p);
    return *p == 2 ? thug_script_next_token(p) : p;
}
/* 0x0046fb30. Only top-level line/EOF tokens stop this scan. Brace, array and
 * expression nesting are independent counters; EOF itself does not advance. */
const uint8_t *thug_script_skip_line(const uint8_t *p) {
    uint32_t braces = 0, arrays = 0, parentheses = 0;
    for (;;) {
        uint8_t token = *p;
        if (token == 3) ++braces;
        if (token == 4) --braces;
        if (token == 5) ++arrays;
        if (token == 6) --arrays;
        if (token == 14) ++parentheses;
        if (token == 15) --parentheses;
        if (!braces && !arrays && !parentheses && (token == 0 || token == 1 || token == 2))
            return thug_script_next_token(p);
        p = thug_script_next_token(p);
    }
}
/* 0x0046ff00. Skip the initial defaults line, then rewrite only command names
 * at line/conditional starts. Symbol callable values must already be relocated
 * for the target platform before this preparation pass runs. */
void thug_script_prepare_bytecode(uint8_t *p) {
    p = (uint8_t *)thug_script_skip_line(p);
    while (*p != 0x24) {
        if (*p == 0x16) {
            const ThugScriptSymbol *symbol = thug_script_resolve_symbol(thug_script_read_word(p + 1));
            if (symbol && (symbol->type == 8 || symbol->type == 9)) {
                if (symbol->type == 9 && !symbol->value) *p = 0x44;
                else {
                    *p = symbol->type == 8 ? 0x43 : 0x46;
                    for (uint32_t i = 0; i < 4; ++i) p[i + 1] = symbol->value >> (i * 8);
                }
            }
            p = (uint8_t *)thug_script_skip_line(p + 5);
        } else if (*p == 0x47) {
            p = (uint8_t *)thug_script_next_token(p);
            if (*p == 0x39) ++p;
        } else p = (uint8_t *)thug_script_skip_line(p);
    }
}
