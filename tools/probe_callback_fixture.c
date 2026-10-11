/* Test callback only; no recovered gameplay behavior. */
#include <stdint.h>
void record_probe(uint8_t *probe) {
    volatile uint32_t *control = (volatile uint32_t *)0x02000400;
    uint8_t *log = (uint8_t *)(0x02100000 + control[1] * 176);
    for (unsigned i = 0; i < 176; ++i) log[i] = probe[i];
    ++control[1];
    uint8_t *result = probe + 36;
    if (control[0] & 1) {
        result[0x2f] ^= 0x5a; result[0x4a] ^= 0x5a; result[0x4b] ^= 0x5a;
        *(float *)(result + 0x24) = 0.25f;
        *(float *)result = 42.0f;
    }
    if (control[0] & 2) *(uint8_t *)(uintptr_t)control[2] ^= 1;
    if (control[0] & 4) {
        *(float *)probe += 1000.0f;
        *(uint32_t *)(probe + 0xac) = 0;
    }
    if (control[0] & 8) result[0x48] = 0;
}
