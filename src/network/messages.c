#include "messages.h"
#include "../core/compress.h"
#include <stddef.h>
_Static_assert(sizeof(ThugMessageSpec) == 32, "Original message descriptor");
_Static_assert(sizeof(ThugMessage) == 12, "Original message");
_Static_assert(sizeof(ThugSequencedMessage) == 16, "Original sequenced message");

const char thug_message_format_sending[] = "*** Sending compressed message %d. Old size : %d ";
const char thug_message_format_rle[] = "RLE : New payload len : %d, New size : %d\n";
const char thug_message_format_lzss[] = "LZSS : New payload len : %d, New size : %d\n";
const char thug_message_format_larger[] = "*** Compressed message was larger. Defaulting back to uncompressed version\n";

/* 0x004549f0. Padding remains untouched. */
void thug_message_spec_initialize(ThugMessageSpec *spec) {
    spec->id = 0; spec->flags = 0; spec->length = 0; spec->data = NULL;
    spec->priority = 0x80; spec->delivery = 0; spec->group = 0; spec->replace = 0;
    spec->delay = 0; spec->sequence = 0; spec->compression = 0;
}
/* 0x00454a60. Lookahead ends a literal two bytes before an equal pair, then
 * reuses that pair as the start of a run. Runs cap at 129, literals at 128. */
uint32_t thug_message_rle_encode(const uint8_t *input, uint32_t size, uint8_t *output, uint32_t capacity) {
    (void)capacity;
    uint8_t *begin = output;
    if (!size) return 0;
    uint8_t first = *input++, last, literal[128];
    if (!--size) return 0;
    last = *input++; --size;
    for (;;) {
        uint32_t count = 2;
        if (first == last) {
            while (size && first == last && count < 129) { last = *input++; --size; ++count; }
            if (first == last) {
                *output++ = (uint8_t)(count + 0x7e); *output++ = first;
                if (!size) break;
                first = *input++; --size;
            } else {
                *output++ = (uint8_t)(count + 0x7d); *output++ = first;
                first = last;
            }
        } else {
            literal[0] = first; literal[1] = last;
            while (size && literal[count - 2] != literal[count - 1] && count < 128) {
                literal[count++] = *input++; --size;
            }
            first = literal[count - 2];
            if (first == literal[count - 1]) {
                *output++ = (uint8_t)(count - 3);
                for (uint32_t i = 0; i < count - 2; ++i) *output++ = literal[i];
                last = first;
                continue;
            }
            *output++ = (uint8_t)(count - 1);
            for (uint32_t i = 0; i < count; ++i) *output++ = literal[i];
            if (!size) break;
            first = *input++; --size;
        }
        if (!size) { *output++ = 0; *output++ = first; break; }
        last = *input++; --size;
    }
    return (uint32_t)(output - begin);
}
static void copy_bytes(uint8_t *to, const uint8_t *from, uint32_t count) {
    for (uint32_t i = 0; i < count; ++i) to[i] = from[i];
}
static void write_half(uint8_t *to, uint16_t value) { to[0] = (uint8_t)value; to[1] = (uint8_t)(value >> 8); }
/* 0x00454e30. Unsupported nonzero modes retain the original zero-size encoded
 * candidate. Diagnostics are emitted even when the candidate is discarded. */
uint8_t *thug_message_compress(uint8_t *id, uint16_t *length, const uint8_t *data, uint32_t compression,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint16_t original_length = *length;
    uint32_t size = (uint16_t)(original_length + 3), encoded = 0;
    uint8_t *input = memory->allocate(memory->context, size, 1);
    input[0] = *id; write_half(input + 1, *length); copy_bytes(input + 3, data, *length);
    diagnostics->print(diagnostics->context, thug_message_format_sending, (uint32_t)*id, (uint32_t)*length);
    uint32_t capacity = size * 4 / 3 + size;
    uint8_t *candidate = memory->allocate(memory->context, capacity + 3, 1);
    candidate[0] = (uint8_t)compression; write_half(candidate + 1, (uint16_t)(original_length + 3));
    if ((uint8_t)compression == 1) {
        encoded = thug_message_rle_encode(input, size, candidate + 3, capacity);
        diagnostics->print(diagnostics->context, thug_message_format_rle, size, encoded);
    } else if ((uint8_t)compression == 2) {
        encoded = thug_lzss_encode_unchecked(input, candidate + 3, size, 0, diagnostics, memory);
        diagnostics->print(diagnostics->context, thug_message_format_lzss, size, encoded);
    }
    memory->release(memory->context, input);
    if (encoded < *length) { *length = (uint16_t)(encoded + 3); *id = 0x12; return candidate; }
    diagnostics->print(diagnostics->context, thug_message_format_larger);
    memory->release(memory->context, candidate);
    return NULL;
}
static void initialize_header(ThugMessageHeader *header, uint8_t id, uint16_t length, const uint8_t *data,
    uint8_t compression, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    header->data = NULL;
    if (length) {
        uint8_t *compressed = compression ? thug_message_compress(&id, &length, data, compression, diagnostics, memory) : NULL;
        if (compressed) data = compressed;
        header->data = memory->allocate(memory->context, length, 1);
        copy_bytes(header->data, data, length);
        if (compressed) memory->release(memory->context, compressed);
    }
    header->id = id; header->length = length;
}
/* 0x00454fa0 / 0x00455040. References reset before payload allocation. */
ThugMessage *thug_message_initialize(ThugMessage *message, uint32_t id, uint32_t length, const uint8_t *data,
    uint32_t compression, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    message->references = 0;
    initialize_header(&message->header, (uint8_t)id, (uint16_t)length, data, (uint8_t)compression, diagnostics, memory);
    return message;
}
ThugSequencedMessage *thug_sequenced_message_initialize(ThugSequencedMessage *message, uint32_t id, uint32_t length,
    const uint8_t *data, uint32_t group, uint32_t compression, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    message->references = 0;
    initialize_header(&message->header, (uint8_t)id, (uint16_t)length, data, (uint8_t)compression, diagnostics, memory);
    message->group = (uint8_t)group;
    return message;
}
/* 0x004550f0. The payload pointer is deliberately not cleared. */
void thug_message_destroy(ThugMessageHeader *message, const ThugMemory *memory) {
    if (message->data) memory->release(memory->context, message->data);
}
