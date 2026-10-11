#ifndef THUG_PLATFORM_TEXT_H
#define THUG_PLATFORM_TEXT_H
#include <stdint.h>
typedef struct {
    uint32_t unknown_0, codepage, unknown_8[3], ctype_locale;
} ThugTextLocale;
/* Windows services used by the original CRT and button-label formatter.
 * The browser host supplies these services; none are gameplay callbacks. */
typedef struct {
    int32_t (*wide_to_multibyte)(uint32_t, uint32_t, const uint16_t *, int32_t,
        char *, int32_t, const char *, int32_t *);
    uint32_t (*last_error)(void);
    uint32_t (*map_virtual_key)(uint32_t, uint32_t);
} ThugTextPlatform;
extern const ThugTextPlatform *thug_text_platform;
extern ThugTextLocale *thug_text_locale;
extern int32_t thug_text_mb_max;
uint32_t thug_text_convert_wide(const ThugTextLocale *, char *, const uint16_t *, uint32_t);
/* Current locale is supplied by the single-threaded host, replacing CRT TLS. */
uint32_t thug_text_wcstombs(char *, const uint16_t *, uint32_t);
/* Bounded adapters for the score display's legacy CRT formats, in the C locale.
 * These are not a general sprintf implementation. Buffers need 12/44 bytes. */
void thug_text_signed_decimal(char *, int32_t);
void thug_text_fixed_one(char *, float);
#endif
