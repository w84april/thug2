/* Test-only virtual wait method. It records dispatch and deliberately mutates
 * the owner/script to test the scheduler's boundary, not a recovered component. */
#include <stdint.h>

void fixture_script_wait(uint32_t *owner, uint32_t *script, uint32_t argument) {
    uint32_t *control = (uint32_t *)0x01804000;
    uint32_t *record = control + 4 + control[0]++ * 6;
    record[0] = (uintptr_t)owner;
    record[1] = (uintptr_t)script;
    record[2] = argument;
    record[3] = script[0xa4 / 4];
    record[4] = script[0xac / 4];
    record[5] = owner[2];
    switch (owner[1]) {
    case 1:
        owner[2] ^= 0x80000000;
        script[0xa4 / 4] = 0;
        break;
    case 2:
        script[0xa8 / 4] ^= 0x13579bdf;
        script[0xa4 / 4] = 3;
        break;
    case 3:
        script[0xac / 4] = owner[3];
        owner[2] += argument;
        script[0x98 / 4] = argument;
        break;
    }
}
