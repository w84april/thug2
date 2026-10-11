#include "compress.h"
#include "../platform/math.h"

_Static_assert(sizeof(ThugLzssEncoder) == 36, "Original compression globals");
ThugLzssEncoder thug_lzss_encoder;
const char thug_lzss_format_input[] = "     In : %ld bytes\n";
const char thug_lzss_format_output[] = "     Out: %ld bytes\n";
const char thug_lzss_format_ratio[] = "     Out/In: %.3f\n";

/* 0x00401600. Only roots right[4097..4352] and parent[0..4095] are
 * initialized; all other allocator bytes, including sentinel slots, survive. */
void thug_lzss_initialize_encoder(const ThugMemory *memory) {
    ThugLzssEncoder *s = &thug_lzss_encoder;
    memory->temp_scope(memory->context, 2);
    s->window = memory->allocate(memory->context, 4113, 1);
    s->left = memory->allocate(memory->context, 16388, 1);
    s->right = memory->allocate(memory->context, 17412, 1);
    s->parent = memory->allocate(memory->context, 16388, 1);
    memory->temp_scope(memory->context, 0);
    for (uint32_t i = 4097; i <= 4352; ++i) s->right[i] = 4096;
    for (uint32_t i = 0; i < 4096; ++i) s->parent[i] = 4096;
}

/* 0x00401290. Insert an 18-byte window suffix, keeping the first strictly
 * longer match. A full-length match replaces the existing tree node. */
void thug_lzss_insert(uint32_t node) {
    ThugLzssEncoder *s = &thug_lzss_encoder;
    const uint8_t *key = s->window + node;
    s->left[node] = 4096; s->right[node] = 4096;
    int32_t comparison = 1;
    uint32_t parent = key[0] + 4097;
    s->match_length = 0;
    for (;;) {
        uint32_t *child = comparison < 0 ? &s->left[parent] : &s->right[parent];
        if (*child == 4096) { *child = node; s->parent[node] = parent; return; }
        parent = *child;
        int32_t length = 1;
        for (; length < 18; ++length) {
            comparison = (int32_t)key[length] - s->window[parent + length];
            if (comparison) break;
        }
        if (length <= s->match_length) continue;
        s->match_position = parent; s->match_length = length;
        if (length < 18) continue;
        s->parent[node] = s->parent[parent];
        s->left[node] = s->left[parent]; s->right[node] = s->right[parent];
        s->parent[s->left[parent]] = node; s->parent[s->right[parent]] = node;
        uint32_t *link = s->right[s->parent[parent]] == parent
            ? &s->right[s->parent[parent]] : &s->left[s->parent[parent]];
        *link = node; s->parent[parent] = 4096;
        return;
    }
}

/* 0x004013e0. Removal also writes parent[4096] when the chosen child is the
 * sentinel. Do not discard those writes or clear other fields of the old node. */
void thug_lzss_remove(uint32_t node) {
    ThugLzssEncoder *s = &thug_lzss_encoder;
    if (s->parent[node] == 4096) return;
    uint32_t replacement;
    if (s->right[node] == 4096) replacement = s->left[node];
    else if (s->left[node] == 4096) replacement = s->right[node];
    else {
        replacement = s->left[node];
        if (s->right[replacement] != 4096) {
            do { replacement = s->right[replacement]; } while (s->right[replacement] != 4096);
            s->right[s->parent[replacement]] = s->left[replacement];
            s->parent[s->left[replacement]] = s->parent[replacement];
            s->left[replacement] = s->left[node];
            s->parent[s->left[node]] = replacement;
        }
        s->right[replacement] = s->right[node];
        s->parent[s->right[node]] = replacement;
    }
    s->parent[replacement] = s->parent[node];
    uint32_t *link = s->right[s->parent[node]] == node
        ? &s->right[s->parent[node]] : &s->left[s->parent[node]];
    *link = replacement; s->parent[node] = 4096;
}

static void dispose(const ThugMemory *memory) {
    memory->release(memory->context, thug_lzss_encoder.parent);
    memory->release(memory->context, thug_lzss_encoder.right);
    memory->release(memory->context, thug_lzss_encoder.left);
    memory->release(memory->context, thug_lzss_encoder.window);
}
static double unsigned_load(uint32_t value) {
    double n = (int32_t)value;
    return (int32_t)value < 0 ? thug_platform_round_x87_single(n + 4294967296.0) : n;
}

/* 0x00401700. Literal groups have one flag byte and up to eight tokens;
 * matches encode a 12-bit position and length minus three. */
uint32_t thug_lzss_encode_unchecked(const uint8_t *input, uint8_t *output, uint32_t remaining,
    uint32_t verbose, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugLzssEncoder *s = &thug_lzss_encoder;
    s->input_count = 0; s->output_count = 0; s->unknown_count = 0;
    thug_lzss_initialize_encoder(memory);
    uint8_t group[17], mask = 1;
    group[0] = 0;
    uint32_t group_size = 1, tail = 0, cursor = 4078;
    for (uint32_t i = 0; i < 4078; ++i) s->window[i] = 0x20;
    int32_t length = 0;
    while (length < 18 && remaining) { s->window[4078 + length++] = *input++; --remaining; }
    s->input_count = length;
    if (!length) { dispose(memory); return 0; }
    for (uint32_t i = 4077; i >= 4060; --i) thug_lzss_insert(i);
    thug_lzss_insert(cursor);
    do {
        if (s->match_length > length) s->match_length = length;
        if (s->match_length < 3) {
            group[0] |= mask; s->match_length = 1;
            group[group_size++] = s->window[cursor];
        } else {
            group[group_size++] = s->match_position;
            group[group_size++] = ((s->match_position >> 4) & 0xf0) | (s->match_length - 3);
        }
        mask <<= 1;
        if (!mask) {
            for (uint32_t i = 0; i < group_size; ++i) *output++ = group[i];
            s->output_count += group_size; group_size = 1; group[0] = 0; mask = 1;
        }
        int32_t consumed = 0, match = s->match_length;
        while (consumed < match && remaining) {
            uint8_t value = *input++; --remaining;
            thug_lzss_remove(tail);
            s->window[tail] = value;
            if (tail < 17) s->window[tail + 4096] = value;
            cursor = (cursor + 1) & 4095; tail = (tail + 1) & 4095;
            thug_lzss_insert(cursor); ++consumed;
        }
        s->input_count += consumed;
        while (consumed++ < match) {
            thug_lzss_remove(tail); tail = (tail + 1) & 4095; cursor = (cursor + 1) & 4095;
            --length;
            if (length) thug_lzss_insert(cursor);
        }
    } while (length > 0);
    if (group_size > 1) {
        for (uint32_t i = 0; i < group_size; ++i) *output++ = group[i];
        s->output_count += group_size;
    }
    if ((uint8_t)verbose) {
        diagnostics->print(diagnostics->context, thug_lzss_format_input, s->input_count);
        diagnostics->print(diagnostics->context, thug_lzss_format_output, s->output_count);
        double ratio = thug_platform_round_x87_single(unsigned_load(s->output_count) / unsigned_load(s->input_count));
        diagnostics->print(diagnostics->context, thug_lzss_format_ratio, ratio);
    }
    dispose(memory);
    return s->output_count;
}
