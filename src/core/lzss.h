#ifndef THUG_LZSS_H
#define THUG_LZSS_H
#include <stdint.h>

/* The original keeps this window at 0x0068ff68. It is made explicit here so
 * separate engine instances need not share mutable process-global state. */
typedef struct { uint8_t window[4096]; } ThugLzssState;

/* Recovered 0x004014f0. Requires a well-formed stream and enough output space.
 * Returns the first byte after the output. Does not validate either buffer.
 * The final 18 window bytes persist between calls, as in the executable. */
uint8_t *thug_lzss_decode_unchecked(ThugLzssState *state,
    const uint8_t *input, uint8_t *output, uint32_t input_size);
#endif
