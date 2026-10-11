/* Recovered from the supplied PC executable identified in tools/specimen.py.
 * Analyst-assigned names. Behavior tested against x86 instructions; not yet
 * byte-matched with the original MSVC compiler. No final CRC inversion.
 */
#include "checksum.h"

static const uint32_t crc_table[256] = {
#include "crc_table.inc"
};

/* 0x00401aa0: null input OR nonpositive length returns zero. */
uint32_t thug_crc32_buffer(const unsigned char *bytes, int32_t length) {
    uint32_t crc = UINT32_MAX;
    int32_t i;
    if (!bytes || length <= 0) return 0;
    for (i = 0; i < length; ++i)
        crc = (crc >> 8) ^ crc_table[(bytes[i] ^ crc) & 255];
    return crc;
}

/* 0x00401af0: a nonpositive length returns the supplied seed, even for null. */
uint32_t thug_crc32_extend_buffer(const unsigned char *bytes, int32_t length, uint32_t crc) {
    int32_t i;
    for (i = 0; i < length; ++i)
        crc = (crc >> 8) ^ crc_table[(bytes[i] ^ crc) & 255];
    return crc;
}

/* 0x00401b30: counts embedded NULs, lowercases ASCII, normalizes slashes. */
uint32_t thug_crc32_normalized_buffer(const unsigned char *bytes, int32_t length) {
    uint32_t crc = UINT32_MAX;
    int32_t i;
    if (!bytes || length <= 0) return 0;
    for (i = 0; i < length; ++i) {
        unsigned char c = bytes[i];
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}

/* 0x00401b90: a null pointer returns zero; an empty string returns 0xffffffff. */
uint32_t thug_crc32_string(const char *text) {
    uint32_t crc = UINT32_MAX;
    unsigned char c;
    if (!text) return 0;
    while ((c = (unsigned char)*text++) != 0) {
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}

/* 0x00401be0: null and empty strings both leave the supplied seed unchanged. */
uint32_t thug_crc32_extend_string(uint32_t crc, const char *text) {
    unsigned char c;
    if (!text) return crc;
    while ((c = (unsigned char)*text++) != 0) {
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}
