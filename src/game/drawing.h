#ifndef THUG_GAME_DRAWING_H
#define THUG_GAME_DRAWING_H
#include "font.h"

typedef struct ThugDrawable {
    const uint32_t *methods;
    struct ThugDrawable *next;
    uint8_t hidden, unknown_9[3];
    float depth, priority;
} ThugDrawable;
typedef struct {
    ThugDrawable drawable;
    const ThugFontMetrics *metrics;
    void *records;
    uint32_t value_1c, x, y, scale_x, scale_y, value_30, value_34, value_38, color;
    uint8_t flag_40, unknown_41[3];
} ThugTextDrawable;
typedef struct ThugTextDrawStyle ThugTextDrawStyle;
typedef struct {
    uint32_t unavailable_dispose;
    void (*update)(ThugTextDrawStyle *);
    void (*visibility)(ThugTextDrawStyle *);
    void (*data)(ThugTextDrawStyle *);
    void (*order)(ThugTextDrawStyle *);
    void (*owner)(ThugTextDrawStyle *);
} ThugTextDrawStyleMethods;
struct ThugTextDrawStyle {
    const ThugTextDrawStyleMethods *methods;
    const ThugFont *font;
    void *records;
    uint32_t value_c, x, y, value_18, value_1c, scale_x, scale_y, value_28;
    float depth;
    uint32_t unknown_30, priority, color;
    uint8_t flag_3c, unknown_3d, hidden, use_priority;
    uint32_t owner;
    ThugTextDrawStyle *next;
    ThugTextDrawable *drawable;
};
/* These drawable virtual methods have not been recovered yet. */
extern const uint32_t thug_drawable_methods[4], thug_text_drawable_methods[4];
extern const ThugTextDrawStyleMethods thug_draw_style_base_methods, thug_text_draw_style_methods;
extern ThugDrawable *thug_drawables;
extern ThugTextDrawStyle *thug_text_draw_style_pool;
void thug_drawable_insert(ThugDrawable *);
void thug_drawable_unlink(ThugDrawable *);
ThugDrawable *thug_drawable_initialize(ThugDrawable *, uint32_t depth_bits, uint32_t hidden);
ThugTextDrawable *thug_text_drawable_initialize(ThugTextDrawable *, uint32_t depth_bits);
void thug_drawable_set_depth(ThugDrawable *, float);
void thug_drawable_set_priority(ThugDrawable *, float);
void thug_drawable_set_hidden(ThugDrawable *, uint32_t);
void thug_draw_style_noop(ThugTextDrawStyle *);
ThugTextDrawStyle *thug_draw_style_initialize(ThugTextDrawStyle *, uint32_t owner);
void thug_text_draw_style_data(ThugTextDrawStyle *);
void thug_text_draw_style_order(ThugTextDrawStyle *);
void thug_text_draw_style_visibility(ThugTextDrawStyle *);
void thug_draw_style_set_owner(ThugTextDrawStyle *, uint32_t owner);
ThugTextDrawStyle *thug_text_draw_style_initialize(ThugTextDrawStyle *, const ThugMemory *);
void thug_text_draw_style_populate(uint32_t count, const ThugMemory *);
ThugTextDrawStyle *thug_text_draw_style_take(void);
void thug_ui_allocate_text_styles(ThugUiText *, int32_t count, uint32_t secondary_only, const ThugMemory *);
extern const ThugUiElementMethods thug_ui_text_methods;
ThugUiText *thug_ui_text_initialize(ThugUiText *, const ThugMemory *);
void thug_ui_text_destroy(ThugUiText *, const ThugDiagnostics *, const ThugMemory *);
void *thug_ui_text_delete(void *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_draw_style_clear_storage(ThugTextDrawStyle *, const ThugMemory *);
void thug_text_draw_style_return(ThugTextDrawStyle *, const ThugMemory *);
void thug_ui_release_text_styles(ThugUiText *, uint32_t secondary_only, const ThugMemory *);
typedef struct {
    uint32_t unknown_0[2], flags, unknown_c;
    void *data;
} ThugSpriteTexture;
typedef struct {
    ThugDrawable drawable;
    void *texture;
    uint32_t x, y;
    uint16_t width, height;
    uint32_t scale_x, scale_y;
    float pivot_x, pivot_y;
    uint32_t rotation, color;
    uint8_t flip_x, flip_y, unknown_3e[2];
} ThugSpriteDrawable;
typedef struct ThugSpriteDrawStyle ThugSpriteDrawStyle;
typedef struct {
    uint32_t unavailable_dispose;
    void (*update)(ThugSpriteDrawStyle *);
    void (*visibility)(ThugSpriteDrawStyle *);
    void (*data)(ThugSpriteDrawStyle *);
    void (*order)(ThugSpriteDrawStyle *);
    void (*owner)(ThugSpriteDrawStyle *);
} ThugSpriteDrawStyleMethods;
struct ThugSpriteDrawStyle {
    const ThugSpriteDrawStyleMethods *methods;
    const ThugSpriteTexture *texture;
    uint32_t texture_name, x, y, scale_x, scale_y;
    float pivot_x, pivot_y, rotation, depth;
    uint32_t priority;
    uint16_t width, height;
    uint8_t hidden, use_priority, unknown_36, flip_x, flip_y, color[4], unknown_3d[3];
    uint32_t owner;
    ThugSpriteDrawable *drawable;
};
typedef struct {
    ThugUiLayout layout;
    uint32_t texture_name;
    uint8_t unknown_17c, unknown_17d[3];
    ThugSpriteDrawStyle *style;
} ThugUiSprite;
/* Construction/data/order are recovered; disposal and rendering remain unavailable. */
extern const ThugSpriteDrawStyleMethods thug_sprite_style_base_methods, thug_sprite_style_methods;
extern const uint32_t thug_sprite_drawable_methods[4];
extern const ThugUiElementMethods thug_ui_sprite_methods;
ThugSpriteDrawStyle *thug_sprite_style_initialize(ThugSpriteDrawStyle *, uint32_t owner);
ThugSpriteDrawable *thug_sprite_drawable_initialize(ThugSpriteDrawable *, uint32_t depth_bits);
ThugSpriteDrawStyle *thug_sprite_draw_style_initialize(ThugSpriteDrawStyle *, const ThugMemory *);
ThugSpriteDrawStyle *thug_sprite_draw_style_allocate(uint32_t unused, const ThugMemory *);
ThugSpriteDrawStyle *thug_create_sprite_style(uint32_t unused, const ThugMemory *);
ThugUiSprite *thug_ui_sprite_initialize(ThugUiSprite *, const ThugMemory *);
void thug_sprite_draw_style_data(ThugSpriteDrawStyle *);
void thug_sprite_draw_style_visibility(ThugSpriteDrawStyle *);
void thug_sprite_draw_style_order(ThugSpriteDrawStyle *);
void thug_sprite_draw_style_update(ThugSpriteDrawStyle *);
void thug_sprite_draw_style_set_rotation(ThugSpriteDrawStyle *, float angle);
void thug_ui_sprite_set_rotation(ThugUiSprite *, float degrees, uint32_t set_target);
#endif
