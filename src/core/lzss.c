/* Behavioral recovery of 0x004014f0 in the specimen pinned in tools/specimen.py.
 * The dictionary global is lifted into an explicit state parameter.
 * This has not been byte-matched with the original compiler.
 */
#include "lzss.h"

uint8_t *thug_lzss_decode_unchecked(ThugLzssState *state,
    const uint8_t *input, uint8_t *output, uint32_t remaining) {
    uint32_t cursor = 4078, flags = 0, i;
    for (i = 0; i < 4078; ++i) state->window[i] = 0x20;
    for (;;) {
        flags >>= 1;
        if (!(flags & 0x100)) {
            if (!remaining) break;
            flags = *input++ | 0xff00;
            --remaining;
        }
        if (!remaining) break;
        if (flags & 1) {
            uint8_t value = *input++;
            --remaining;
            *output++ = value;
            state->window[cursor] = value;
            cursor = (cursor + 1) & 4095;
        } else {
            uint32_t offset = *input++, descriptor = *input++;
            uint32_t count = (descriptor & 15) + 3;
            remaining -= 2;
            offset |= (descriptor & 0xf0) << 4;
            for (i = 0; i < count; ++i) {
                uint8_t value = state->window[(offset + i) & 4095];
                *output++ = value;
                state->window[cursor] = value;
                cursor = (cursor + 1) & 4095;
            }
        }
    }
    return output;
}
