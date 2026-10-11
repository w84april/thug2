#ifndef THUG_COMPRESS_H
#define THUG_COMPRESS_H
#include "memory.h"
#include "../platform/diagnostics.h"

typedef struct {
    uint32_t *parent, *right, *left;
    uint8_t *window;
    int32_t match_length, match_position;
    uint32_t input_count, output_count, unknown_count;
} ThugLzssEncoder;
/* Original globals at 0x00690f7c..0x00690f9c. Encoding leaves the freed buffer
 * addresses in these fields, as the original does; calls cannot be reentrant. */
extern ThugLzssEncoder thug_lzss_encoder;
extern const char thug_lzss_format_input[], thug_lzss_format_output[], thug_lzss_format_ratio[];
void thug_lzss_initialize_encoder(const ThugMemory *);
void thug_lzss_insert(uint32_t node);
void thug_lzss_remove(uint32_t node);
/* Requires non-overlapping buffers, valid input and enough output capacity
 * (input_size + ceil(input_size/8) is sufficient). Allocation must succeed.
 * A nonzero low verbose byte requires a configured diagnostics adapter. */
uint32_t thug_lzss_encode_unchecked(const uint8_t *input, uint8_t *output, uint32_t input_size,
    uint32_t verbose, const ThugDiagnostics *, const ThugMemory *);
#endif
