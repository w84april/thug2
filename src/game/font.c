#include "font.h"
#include "drawing.h"
#include "ui_manager.h"
#include "../core/checksum.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(sizeof(ThugGlyph) == 24, "font glyph stride");
_Static_assert(offsetof(ThugFontMetrics, spacing) == 0x134, "font spacing");
_Static_assert(offsetof(ThugFontMethods, measure) == 0x20, "font measure virtual slot");
_Static_assert(offsetof(ThugUiText, text) == 0x178, "text widget buffer");
_Static_assert(offsetof(ThugUiText, font) == 0x180, "text widget font");
_Static_assert(offsetof(ThugUiMultiline, text_scale) == 0x19c, "multiline text scale");
_Static_assert(offsetof(ThugUiMultiline, auto_height) == 0x1b1, "automatic multiline height");
_Static_assert(offsetof(ThugUiMultiline, color) == 0x1bc, "multiline color");
const ThugUiElementMethods thug_ui_multiline_methods = {.base={.dispose=thug_ui_multiline_delete,.receive_event=thug_ui_object_event_bridge}};
/* 0x004b0810. Row storage/capacity and the other unmentioned fields are retained. */
ThugUiMultiline *thug_ui_multiline_initialize(ThugUiMultiline *widget, const ThugMemory *memory) {
    thug_ui_initialize(&widget->layout);
    widget->layout.element.object.unknown_0 = (uintptr_t)&thug_ui_multiline_methods;
    widget->color = 0x80000000;
    widget->text_scale = widget->line_spacing = 1;
    widget->font_name = 0; widget->total_height = 0; widget->visible_rows = 0;
    widget->extra = NULL; widget->auto_height = widget->flag_1c0 = widget->flag_1c1 = 0;
    thug_ui_object_set_type(&widget->layout.element.base,0x40d92263,memory);
    return widget;
}
/* 0x004b08b0 and 0x004b0b30. Child deletion belongs to the manager; temporary
 * wrapping rows have already been freed by the text update. */
void thug_ui_multiline_destroy(ThugUiMultiline *widget, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    widget->layout.element.object.unknown_0 = (uintptr_t)&thug_ui_multiline_methods;
    if (widget->extra) {
        void *extra = widget->extra;
        thug_draw_style_noop(extra);
        memory->release(memory->context,extra);
    }
    thug_ui_destroy(&widget->layout,diagnostics,memory);
}
void *thug_ui_multiline_delete(void *widget, uint32_t flags, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_ui_multiline_destroy(widget,diagnostics,memory);
    if ((uint8_t)flags & 1) memory->release(memory->context,widget);
    return widget;
}
const ThugFontMetrics *thug_button_font;
uint8_t thug_key_label_flags[4], thug_key_menu_override;
uint32_t thug_key_bindings[11], thug_text_language;
uint16_t thug_key_name_storage[257][15];
char thug_key_label_text[256], thug_key_label_converted[256], thug_integer_text[32];
/* 0x005f3120. Unsigned address arithmetic retains the original wrapped index. */
const uint16_t *thug_key_name(uint32_t code) {
    return (const void *)((uintptr_t)&thug_key_name_storage[1] + code*30u);
}
static void assign_reference(ThugObjectReference *to, const ThugObjectReference *from) {
    ThugReferencedObject *object = from->object;
    if (to->object) thug_object_reference_unlink(to->object,to);
    to->object = object;
    if (object) thug_object_reference_link(object,to);
}
static char *copy_text(char *out, const char *in) {
    while ((*out = *in++)) ++out;
    return out;
}
static void convert_key(uint32_t code) {
    thug_text_wcstombs(thug_key_label_converted,thug_key_name(code),256);
    thug_key_label_converted[255] = 0;
}
/* 0x005bcd50. Menu/reference operations intentionally retain their original
 * order, including visibility reads whose results are unused. */
const char *thug_key_label(uint32_t button) {
    uint8_t alternate = thug_key_label_flags[0] || thug_key_label_flags[3];
    uint8_t forced = thug_key_label_flags[2], menu = 0;
    ThugObjectReference selected, temporary;
    thug_ui_find(&selected,thug_crc32_string("select_skater_hmenu"),0);
    if (selected.object) thug_ui_is_hidden((const ThugUiElement *)selected.object);
    thug_ui_find(&temporary,thug_crc32_string("piece_menu_hmenu"),0);
    assign_reference(&selected,&temporary);
    if (temporary.object) thug_object_reference_unlink(temporary.object,&temporary);
    if (!thug_key_menu_override && selected.object && !thug_ui_is_hidden((const ThugUiElement *)selected.object)) menu = 1;
    thug_ui_find(&temporary,thug_crc32_string("select_skater_hmenu"),0);
    assign_reference(&selected,&temporary);
    if (temporary.object) { thug_object_reference_unlink(temporary.object,&temporary); temporary.object = NULL; }
    if (selected.object) thug_ui_is_hidden((const ThugUiElement *)selected.object);
    uint8_t keyboard = !menu && alternate && !forced;
    uint32_t code = 0;
    if (forced) {
        switch (button) {
        case 0: case 1: case 2: case 3: case 8: case 9: case 14: case 15: case 16: case 17: code = UINT32_MAX; break;
        case 22: code = 28; break;
        case 23: code = 1; break;
        default: break;
        }
    } else {
        switch (button) {
        case 0: code = thug_key_bindings[3]; break;
        case 1: code = thug_key_bindings[2]; break;
        case 2: code = thug_key_bindings[1]; break;
        case 3: code = thug_key_bindings[0]; break;
        case 8: code = 1; break;
        case 9: code = keyboard ? 57 : thug_key_bindings[5]; break;
        case 14: code = thug_key_bindings[8]; break;
        case 15: code = thug_key_bindings[9]; break;
        case 16: code = thug_key_bindings[6]; break;
        case 17: code = thug_key_bindings[7]; break;
        case 21: code = thug_key_bindings[10]; break;
        case 22: code = keyboard ? 28 : 0; break;
        case 23: code = keyboard ? 1 : 0; break;
        case 24: code = keyboard ? 18 : 0; break;
        case 25: code = keyboard ? 19 : 0; break;
        case 26: code = keyboard ? 12 : 0; break;
        case 27: code = keyboard ? 13 : 0; break;
        case 28: code = keyboard ? 2 : 0; break;
        case 29: code = keyboard ? 3 : 0; break;
        default: break;
        }
    }
    convert_key(code);
    copy_text(thug_key_label_text,thug_key_label_converted);
    if (button == 18) {
        convert_key(thug_key_bindings[8]);
        char *end = copy_text(thug_key_label_text,thug_key_label_converted);
        *end++ = '+'; *end = 0;
        convert_key(thug_key_bindings[9]);
        end = thug_key_label_text; while (*end) ++end;
        copy_text(end,thug_key_label_converted);
    }
    if (keyboard && (button == 19 || button == 20)) {
        uint32_t first = button == 20 ? 31 : 44, second = button == 20 ? 45 : 46;
        uint8_t a = (uint8_t)thug_text_platform->map_virtual_key(thug_text_platform->map_virtual_key(first,1),2);
        uint8_t b = (uint8_t)thug_text_platform->map_virtual_key(thug_text_platform->map_virtual_key(second,1),2);
        thug_key_label_text[0] = (char)a; thug_key_label_text[1] = '/';
        thug_key_label_text[2] = (char)b; thug_key_label_text[3] = 0;
    }
    if (selected.object) thug_object_reference_unlink(selected.object,&selected);
    return thug_key_label_text;
}
/* 0x00402170. The caller owns enough storage; the cursor can alias output. */
uint32_t thug_text_word(char *out, const char **cursor) {
    for (;;) {
        const char *in = *cursor;
        char c = *in;
        if (!c) { *out = 0; return 2; }
        if (c == ' ') { *out++ = **cursor; ++*cursor; *out = 0; return 0; }
        if (c == '\\') {
            *cursor = ++in;
            c = *in;
            if (c == '_') { *out++ = ' '; ++*cursor; }
            else if (c == 'n') { *cursor = in+1; *out = 0; return 1; }
            else { *out++ = '\\'; *out++ = **cursor; ++*cursor; }
        } else { *out++ = c; ++*cursor; }
    }
}
/* 0x00402200. Original signed negation wraps at INT_MIN, producing two minus
 * signs after sprintf; grouping includes that inner sign. */
const char *thug_text_integer(int32_t value) {
    char digits[16], *out = thug_integer_text;
    uint32_t word = (uint32_t)value;
    if (value < 0) { *out++ = '-'; word = 0u-word; }
    uint32_t magnitude = (int32_t)word < 0 ? 0u-word : word, count = 0;
    do { digits[count++] = (char)('0' + magnitude%10); magnitude /= 10; } while (magnitude);
    if ((int32_t)word < 0) digits[count++] = '-';
    char separator = thug_text_language == 3 ? ' ' : thug_text_language >= 4 && thug_text_language <= 6 ? '.' : ',';
    while (count) { *out++ = digits[--count]; if (count && count%3 == 0) *out++ = separator; }
    *out = 0;
    return thug_integer_text;
}
/* 0x004b2160. */
uint32_t thug_ui_font_name(const void *widget) {
    uint32_t name; __builtin_memcpy(&name,(const uint8_t *)widget+0x178,4); return name;
}
/* 0x004af720. Newlines act on the following word. Rows form a ring, while the
 * total keeps increasing. The original also reads the byte before an empty
 * row when wrapping, so callers must retain that valid backing storage. */
void thug_ui_wrap_text(ThugUiMultiline *widget, const char *text) {
    const ThugFont *font = thug_font_find(widget->font_name);
    uint32_t previous = 0;
    for (;;) {
        char word[96];
        uint32_t token = thug_text_word(word,&text);
        float width, height;
        thug_font_measure(font,word,&width,&height);
        width = (float)thug_platform_round_x87_single((double)width * widget->text_scale);
        uint32_t length = 0;
        while (word[length]) ++length;
        if ((widget->row_width > 0 &&
             thug_platform_round_x87_single((double)width + widget->row_width) > widget->layout.width) ||
            previous == 1 || widget->row_bytes + length >= 96) {
            char *last = (char *)((uintptr_t)widget->rows[widget->current_row] + widget->row_bytes - 1u);
            if (*last == ' ') *last = 0;
            ++widget->total_rows;
            ++widget->current_row;
            if ((int32_t)widget->current_row >= widget->row_capacity) widget->current_row = 0;
            widget->row_bytes = 0;
            widget->row_width = 0;
        }
        copy_text(widget->rows[widget->current_row] + widget->row_bytes,word);
        widget->row_width = (float)thug_platform_round_x87_single((double)width + widget->row_width);
        widget->row_bytes += length;
        previous = token;
        if (token == 2) return;
    }
}
/* 0x004cecb0. Width accumulation wraps as a 32-bit integer. Button glyphs use
 * the button font's widths but always the base font's character spacing. */
void thug_font_metrics_measure(const ThugFontMetrics *font, const char *text, float *width, float *height) {
    uint32_t total = 0;
    for (;;) {
        const ThugFontMetrics *active = font;
        const ThugGlyph *glyph = NULL;
        uint8_t resolved = 0, draw = 1;
        while ((uint8_t)*text == '\\' && !resolved) {
            uint8_t escape = (uint8_t)*++text;
            if (escape == '\\') break;
            switch (escape) {
            case 'B': case 'b': case 'M': case 'm': {
                ++text;
                uint32_t button;
                if (escape == 'm' || escape == 'M') { char mapped = (char)thug_text_button_glyph(text); button = thug_text_digit(&mapped); }
                else button = thug_text_digit(text);
                if ((button >= 4 && button <= 7) || (button >= 10 && button <= 13)) {
                    active = thug_button_font; glyph = &active->glyphs[active->special[button]];
                } else {
                    const char *label = thug_key_label(button);
                    if (*label) {
                        const ThugGlyph *glyphs = font->glyphs;
                        int32_t spacing = font->spacing;
                        do {
                            uint8_t index = *(const uint8_t *)((uintptr_t)font + (uint32_t)(0x0c + (int8_t)*label));
                            total += glyphs[index].width + (uint32_t)spacing;
                        } while (*++label);
                    }
                    draw = 0;
                }
                resolved = 1; break;
            }
            case 'S': case 's': ++text; glyph = &font->glyphs[font->special[thug_text_digit(text)]]; resolved = 1; break;
            case 'C': case 'c': case 'U': case 'u': text += 2; break;
            case 'L': ++text; break;
            default: break;
            }
        }
        uint8_t c = (uint8_t)*text;
        if (!c) {
            *width = (float)(int32_t)total;
            uint32_t pixels; __builtin_memcpy(&pixels,font,4);
            *height = (float)pixels; return;
        }
        if (draw) {
            uint32_t advance;
            if (c == ' ' && !glyph) advance = (uint32_t)(int32_t)font->space_width;
            else { if (!glyph) glyph = &active->glyphs[active->characters[c]]; advance = glyph->width; }
            total += advance + (uint32_t)(int32_t)font->spacing;
        }
        ++text;
    }
}
/* 0x004b3d10 and concrete vtable0x0064a328 slot+0x20. */
void thug_font_measure_concrete(const ThugFont *font, const char *text, float *width, float *height) {
    thug_font_metrics_measure(font->metrics,text,width,height);
}
const ThugFontMethods thug_font_methods = {{0},thug_font_measure_concrete};
/* 0x0048d060. */
void thug_font_measure(const ThugFont *font, const char *text, float *width, float *height) {
    font->methods->measure(font,text,width,height);
}
static uint32_t text_length(const char *s) { uint32_t n = 0; while (s[n]) ++n; return n; }
/* 0x004af8c0. Buffer reuse compares current string lengths, not allocation
 * capacity. Two escaped backslashes are retained for the font parser. */
void thug_ui_set_text(ThugUiText *widget, const char *in, const ThugMemory *memory) {
    uint32_t length = text_length(in);
    if (!widget->text || (int32_t)text_length(widget->text) < (int32_t)length) {
        if (widget->text) memory->release(memory->context,widget->text);
        memory->temp_scope(memory->context,6);
        widget->text = memory->allocate(memory->context,length+1,1);
        memory->temp_scope(memory->context,0);
    }
    char *out = widget->text;
    while (*in) {
        char c = *in;
        if (c == '\\') {
            if (in[1] == '\\') { *out++ = c; c = *++in; }
            else if (in[1] == '_') { in += 2; *out++ = ' '; continue; }
            else if (in[1] == 'm') { *out++ = '\\'; *out++ = 'b'; in += 2; c = (char)thug_text_button_glyph(in); }
        }
        *out++ = c; ++in;
    }
    *out = 0;
    if (widget->font) {
        float width, height;
        thug_font_measure(widget->font,widget->text,&width,&height);
        if (!(widget->layout.element.object.unknown_8_to_10[0] & 0x2000)) thug_ui_set_size(&widget->layout,width,height,0);
    }
    widget->layout.element.object.unknown_8_to_10[0] |= 0x1000;
}

/* 0x004b0cd0. Rebuild actual child widgets, retaining the original thirty-row
 * temporary ring, signed counts, second wrapping pass and event ordering. */
void thug_ui_multiline_set_text(ThugUiMultiline *widget, const char *const *texts, uint32_t count,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugUiManager *manager = thug_ui_manager;
    thug_ui_set_events_enabled(&widget->layout.element,0,diagnostics,memory);
    ThugObjectReference child = {widget->layout.element.children.object,NULL,NULL};
    if (child.object) thug_object_reference_link(child.object,&child);
    while (child.object) {
        ThugObjectReference next = {((ThugUiElement *)child.object)->next_sibling.object,NULL,NULL};
        if (next.object) thug_object_reference_link(next.object,&next);
        thug_ui_manager_delete_id(manager,child.object->id,1,0,NULL,diagnostics,memory);
        thug_object_reference_assign_reference(&child,&next);
        thug_object_reference_destroy(&next);
    }
    memory->temp_scope(memory->context,6);
    widget->rows = memory->allocate(memory->context,0x78,1);
    widget->rows[0] = memory->allocate(memory->context,0xb40,1);
    memory->temp_scope(memory->context,0);
    for (uint32_t i = 1; i < 30; ++i) widget->rows[i] = widget->rows[0]+i*96;
    for (uint32_t i = 0; i < 30; ++i) widget->rows[i][0] = 0;
    widget->row_bytes = widget->total_rows = widget->current_row = 0; widget->row_width = 0;
    if (widget->auto_height) { widget->layout.height = 0; widget->row_capacity = 0; }
    for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i) thug_ui_wrap_text(widget,texts[i]);
    if (count) { ++widget->total_rows; ++widget->current_row; }
    widget->visible_rows = (int32_t)widget->current_row;
    int32_t start_row = 0;
    if ((int32_t)widget->total_rows >= widget->row_capacity) {
        if (!widget->auto_height) start_row = (int32_t)widget->total_rows % widget->row_capacity;
        else {
            float width, height;
            thug_font_measure(thug_font_find(widget->font_name),"AAA",&width,&height);
            double line = thug_platform_round_x87_single((double)widget->line_spacing*widget->text_scale);
            line = thug_platform_round_x87_single(line*height);
            double total = thug_platform_round_x87_single((double)(int32_t)widget->total_rows*line);
            widget->layout.height = (float)total;
            int32_t capacity = (int32_t)thug_truncate_double_low_word(total) / (int32_t)thug_truncate_double_low_word(line);
            widget->row_bytes = widget->total_rows = widget->current_row = 0; widget->row_width = 0;
            widget->row_capacity = capacity;
            for (uint32_t i = 0; (int32_t)i < (int32_t)count; ++i) thug_ui_wrap_text(widget,texts[i]);
        }
        widget->visible_rows = widget->row_capacity;
    }
    widget->total_height = 0;
    for (int32_t i = 0; i < widget->visible_rows; ++i) {
        memory->temp_scope(memory->context,6);
        ThugUiText *text = thug_allocate_zeroed(0x1b0,memory);
        if (text) thug_ui_text_initialize(text,memory);
        memory->temp_scope(memory->context,0);
        manager->base.methods->add(&manager->base,(ThugUiObjectBase *)text,memory);
        ThugObjectReference created = {(ThugReferencedObject *)text,NULL,NULL};
        if (created.object) thug_object_reference_link(created.object,&created);
        ThugObjectReference parent = {&widget->layout.element.object,NULL,NULL};
        thug_object_reference_link(parent.object,&parent);
        thug_ui_manager_attach(manager,&parent,&created,1);
        thug_object_reference_destroy(&parent); thug_object_reference_destroy(&created);
        text->unknown_17c = widget->font_name;
        text->font = thug_font_find(widget->font_name);
        text->layout.element.object.unknown_8_to_10[0] |= 0x1000;
        thug_ui_set_text(text,widget->rows[start_row],memory);
        thug_ui_set_scale(&text->layout,widget->text_scale,widget->text_scale,0,0);
        double height = thug_platform_round_x87_single((double)text->layout.height*widget->text_scale);
        height = thug_platform_round_x87_single(height*widget->line_spacing);
        widget->total_height = (float)thug_platform_round_x87_single(height+widget->total_height);
        if (++start_row >= widget->row_capacity) start_row = 0;
    }
    memory->release(memory->context,widget->rows[0]);
    memory->release(memory->context,widget->rows);
    thug_ui_set_events_enabled(&widget->layout.element,1,diagnostics,memory);
    widget->layout.element.object.unknown_8_to_10[0] |= 0x1000;
    thug_object_reference_destroy(&child);
}
