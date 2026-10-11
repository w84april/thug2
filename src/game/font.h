#ifndef THUG_GAME_FONT_H
#define THUG_GAME_FONT_H
#include "ui.h"
#include "../platform/text.h"
typedef struct {
    uint8_t unknown_0[16];
    uint16_t width;
    uint8_t unknown_12[6];
} ThugGlyph;
typedef struct {
    uint32_t height, unknown_4;
    const ThugGlyph *glyphs;
    uint8_t characters[256], special[40];
    int16_t spacing, space_width;
} ThugFontMetrics;
typedef struct ThugFont ThugFont;
typedef struct {
    uint32_t unavailable_0[8];
    void (*measure)(const ThugFont *, const char *, float *, float *);
} ThugFontMethods;
struct ThugFont {
    const ThugFontMethods *methods;
    uint32_t unknown_4;
    const ThugFontMetrics *metrics;
};
typedef struct {
    ThugUiLayout layout;
    char *text;
    uint32_t unknown_17c;
    const ThugFont *font;
    struct ThugTextDrawStyle **draw_styles, **secondary_styles;
    int32_t draw_style_count;
    uint32_t unknown_190;
    uint8_t has_secondary_styles;
    uint8_t unknown_195[11];
    uint32_t color;
    uint8_t flag_1a4, flag_1a5, unknown_1a6[2];
    uint32_t unknown_1a8, unknown_1ac;
} ThugUiText;
typedef struct {
    ThugUiLayout layout;
    uint32_t font_name;
    char **rows;
    uint32_t total_rows, current_row, row_bytes;
    float row_width;
    int32_t row_capacity;
    uint32_t unknown_194, unknown_198;
    float text_scale;
    float line_spacing, total_height;
    int32_t visible_rows;
    void *extra;
    uint8_t unknown_1b0, auto_height, unknown_1b2[10];
    uint32_t color;
    uint8_t flag_1c0, flag_1c1, unknown_1c2[2];
} ThugUiMultiline;
extern const ThugUiElementMethods thug_ui_multiline_methods;
ThugUiMultiline *thug_ui_multiline_initialize(ThugUiMultiline *, const ThugMemory *);
void thug_ui_multiline_destroy(ThugUiMultiline *, const ThugDiagnostics *, const ThugMemory *);
void *thug_ui_multiline_delete(void *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
/* At most thirty visible rows, bounded 95-byte words and valid fonts/styles.
 * Automatic height needs a nonzero integer line height when resizing. */
void thug_ui_multiline_set_text(ThugUiMultiline *, const char *const *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
extern const ThugFontMethods thug_font_methods;
extern const ThugFontMetrics *thug_button_font;
extern uint8_t thug_key_label_flags[4], thug_key_menu_override;
extern uint32_t thug_key_bindings[11], thug_text_language;
/* Entry zero precedes the named table, as used by the original -1 key code. */
extern uint16_t thug_key_name_storage[257][15];
extern char thug_key_label_text[256], thug_key_label_converted[256];
extern char thug_integer_text[32];
const uint16_t *thug_key_name(uint32_t code);
const char *thug_key_label(uint32_t button);
uint32_t thug_text_word(char *out, const char **cursor);
const char *thug_text_integer(int32_t value);
uint32_t thug_ui_font_name(const void *widget);
void thug_font_metrics_measure(const ThugFontMetrics *, const char *, float *, float *);
void thug_font_measure_concrete(const ThugFont *, const char *, float *, float *);
void thug_font_measure(const ThugFont *, const char *, float *, float *);
void thug_ui_set_text(ThugUiText *, const char *, const ThugMemory *);
/* Initialized row storage and words of at most 95 bytes are required. */
void thug_ui_wrap_text(ThugUiMultiline *, const char *);
#endif
