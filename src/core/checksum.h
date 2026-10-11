#ifndef THUG_CHECKSUM_H
#define THUG_CHECKSUM_H
#include <stdint.h>

uint32_t thug_crc32_buffer(const unsigned char *bytes, int32_t length);
uint32_t thug_crc32_extend_buffer(const unsigned char *bytes, int32_t length, uint32_t crc);
uint32_t thug_crc32_normalized_buffer(const unsigned char *bytes, int32_t length);
uint32_t thug_crc32_string(const char *text);
uint32_t thug_crc32_extend_string(uint32_t crc, const char *text);
#endif
