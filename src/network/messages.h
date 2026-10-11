#ifndef THUG_NETWORK_MESSAGES_H
#define THUG_NETWORK_MESSAGES_H
#include "../core/memory.h"
#include "../platform/diagnostics.h"

typedef struct {
    uint8_t id, flags;
    uint16_t length;
    const uint8_t *data;
    uint32_t priority, delivery;
    uint8_t group, replace, padding[2];
    uint32_t delay, sequence;
    uint8_t compression, tail[3];
} ThugMessageSpec;
typedef struct {
    uint8_t id, padding;
    uint16_t length;
    uint8_t *data;
} ThugMessageHeader;
typedef struct { ThugMessageHeader header; uint32_t references; } ThugMessage;
typedef struct {
    ThugMessageHeader header;
    uint8_t group, padding[3];
    uint32_t references;
} ThugSequencedMessage;

void thug_message_spec_initialize(ThugMessageSpec *);
/* Internal codecs require valid, nonoverlapping buffers and successful
 * allocation. RLE ignores its capacity argument and preserves the original
 * empty output for a one-byte input. Message lengths must fit length+3 in a
 * halfword. Compression compares encoded size before adding the outer header. */
uint32_t thug_message_rle_encode(const uint8_t *, uint32_t size, uint8_t *, uint32_t capacity);
uint8_t *thug_message_compress(uint8_t *id, uint16_t *length, const uint8_t *, uint32_t compression,
    const ThugDiagnostics *, const ThugMemory *);
ThugMessage *thug_message_initialize(ThugMessage *, uint32_t id, uint32_t length, const uint8_t *,
    uint32_t compression, const ThugDiagnostics *, const ThugMemory *);
ThugSequencedMessage *thug_sequenced_message_initialize(ThugSequencedMessage *, uint32_t id, uint32_t length,
    const uint8_t *, uint32_t group, uint32_t compression, const ThugDiagnostics *, const ThugMemory *);
void thug_message_destroy(ThugMessageHeader *, const ThugMemory *);
extern const char thug_message_format_sending[], thug_message_format_rle[], thug_message_format_lzss[],
    thug_message_format_larger[];
#endif
