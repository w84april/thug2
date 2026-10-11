#include "drawing.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(sizeof(ThugDrawable) == 0x14, "drawable prefix");
_Static_assert(sizeof(ThugTextDrawable) == 0x44, "text drawable allocation");
_Static_assert(sizeof(ThugTextDrawStyle) == 0x4c, "text style allocation");
_Static_assert(offsetof(ThugTextDrawStyle, owner) == 0x40, "text style owner");
_Static_assert(offsetof(ThugTextDrawStyleMethods, owner) == 0x14, "style owner virtual");
_Static_assert(offsetof(ThugUiText, has_secondary_styles) == 0x194, "text widget secondary styles");
_Static_assert(sizeof(ThugUiText) == 0x1b0, "text widget allocation");
_Static_assert(sizeof(ThugSpriteDrawStyle) == 0x48, "sprite style allocation");
_Static_assert(offsetof(ThugSpriteDrawStyle, color) == 0x39, "unaligned sprite color");
_Static_assert(offsetof(ThugSpriteDrawStyle, drawable) == 0x44, "sprite drawable pointer");
_Static_assert(sizeof(ThugSpriteDrawable) == 0x40, "sprite drawable allocation");
_Static_assert(offsetof(ThugUiSprite, style) == 0x180, "UI sprite style");
_Static_assert(offsetof(ThugUiLayout, rotation) == 0xf8, "UI rotation");
_Static_assert(offsetof(ThugUiLayout, target_rotation) == 0xb4, "UI target rotation");
const ThugUiElementMethods thug_ui_text_methods = {.base={.dispose=thug_ui_text_delete,.receive_event=thug_ui_object_event_bridge}};
/* 0x004b1830. The optional object path deliberately reacquires one style before
 * the final release. Preserve this allocation/release ordering. */
void thug_ui_text_destroy(ThugUiText *widget, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    widget->layout.element.object.unknown_0 = (uintptr_t)&thug_ui_text_methods;
    if (widget->unknown_190) {
        thug_ui_release_text_styles(widget, 0, memory);
        void *extra = (void *)(uintptr_t)widget->unknown_190;
        if (extra) { thug_draw_style_noop(extra); memory->release(memory->context, extra); }
        widget->unknown_190 = 0;
        thug_ui_allocate_text_styles(widget, 1, 0, memory);
    }
    thug_ui_release_text_styles(widget, 0, memory);
    if (widget->text) memory->release(memory->context, widget->text);
    thug_ui_destroy(&widget->layout, diagnostics, memory);
}
/* 0x004b2030. */
void *thug_ui_text_delete(void *widget, uint32_t flags, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_ui_text_destroy(widget, diagnostics, memory);
    if ((uint8_t)flags & 1) memory->release(memory->context, widget);
    return widget;
}
const uint32_t thug_drawable_methods[4], thug_text_drawable_methods[4];
const uint32_t thug_sprite_drawable_methods[4];
const ThugUiElementMethods thug_ui_sprite_methods = {.base={.receive_event=thug_ui_object_event_bridge}};
/* Typed bridge to the already recovered return-only virtual 5480a0. */
static void sprite_noop(ThugSpriteDrawStyle *style) { thug_draw_style_noop((void *)style); }
const ThugSpriteDrawStyleMethods thug_sprite_style_base_methods = {
    0,sprite_noop,sprite_noop,sprite_noop,sprite_noop,sprite_noop
};
const ThugSpriteDrawStyleMethods thug_sprite_style_methods = {
    0,thug_sprite_draw_style_update,thug_sprite_draw_style_visibility,
    thug_sprite_draw_style_data,thug_sprite_draw_style_order,sprite_noop
};
/* 0x0049ed60. The original leaves priority, byte 36 and padding untouched. */
ThugSpriteDrawStyle *thug_sprite_style_initialize(ThugSpriteDrawStyle *style, uint32_t owner) {
    style->x = style->y = 0xbf800000;
    style->pivot_x = style->pivot_y = -1;
    style->methods = &thug_sprite_style_base_methods;
    style->texture = NULL; style->texture_name = 0x54628ed7;
    style->scale_x = style->scale_y = 0x3f800000;
    style->rotation = style->depth = 0;
    style->width = style->height = 0;
    for (unsigned i=0;i<4;++i) style->color[i] = 0x80;
    style->owner = owner; style->hidden = 1;
    style->use_priority = style->flip_x = style->flip_y = 0;
    return style;
}
/* 0x004dfc50. The remaining draw data retains its incoming bytes. */
ThugSpriteDrawable *thug_sprite_drawable_initialize(ThugSpriteDrawable *drawable, uint32_t depth_bits) {
    __builtin_memcpy(&drawable->drawable.depth,&depth_bits,4);
    drawable->drawable.hidden = 1;
    drawable->drawable.priority = 0; drawable->drawable.next = NULL;
    drawable->drawable.methods = thug_sprite_drawable_methods;
    drawable->texture = NULL;
    return drawable;
}
/* 0x004c70e0. Unlike text styles, this constructor does not populate draw data. */
ThugSpriteDrawStyle *thug_sprite_draw_style_initialize(ThugSpriteDrawStyle *style, const ThugMemory *memory) {
    thug_sprite_style_initialize(style,0);
    style->methods = &thug_sprite_style_methods;
    ThugSpriteDrawable *drawable = memory->allocate(memory->context,0x40,1);
    style->drawable = drawable ? thug_sprite_drawable_initialize(drawable,0) : NULL;
    return style;
}
/* 0x004b2a80 and its 0x0048bf30 forwarding entry. */
ThugSpriteDrawStyle *thug_sprite_draw_style_allocate(uint32_t unused, const ThugMemory *memory) {
    (void)unused;
    ThugSpriteDrawStyle *style = memory->allocate(memory->context,0x48,1);
    return style ? thug_sprite_draw_style_initialize(style,memory) : NULL;
}
ThugSpriteDrawStyle *thug_create_sprite_style(uint32_t unused, const ThugMemory *memory) {
    return thug_sprite_draw_style_allocate(unused,memory);
}
/* 0x004af1a0. Sprite allocation precedes object type/parameter initialization. */
ThugUiSprite *thug_ui_sprite_initialize(ThugUiSprite *widget, const ThugMemory *memory) {
    thug_ui_initialize(&widget->layout);
    widget->layout.element.object.unknown_0 = (uintptr_t)&thug_ui_sprite_methods;
    widget->texture_name = 0;
    widget->style = thug_create_sprite_style(0,memory);
    widget->unknown_17c = 1;
    thug_ui_object_set_type(&widget->layout.element.base,0xb12b510a,memory);
    return widget;
}
/* 0x004c71b0. Null textures retain the prior draw texture. Flag 1 selects an
 * indirect texture handle. Scalar copies, including color at +39, stay raw. */
void thug_sprite_draw_style_data(ThugSpriteDrawStyle *style) {
    if (style->texture) {
        void *data = style->texture->data;
        if (style->texture->flags & 1) __builtin_memcpy(&data,data,sizeof(data));
        style->drawable->texture = data;
    }
    style->drawable->flip_x = style->flip_x; style->drawable->flip_y = style->flip_y;
    style->drawable->x = style->x; style->drawable->y = style->y;
    style->drawable->width = style->width; style->drawable->height = style->height;
    style->drawable->scale_x = style->scale_x; style->drawable->scale_y = style->scale_y;
    double x = thug_platform_round_x87_single((double)style->pivot_x+1);
    x = thug_platform_round_x87_single(x*0.5);
    style->drawable->pivot_x = (float)thug_platform_round_x87_single(x*style->width);
    double y = thug_platform_round_x87_single((double)style->pivot_y+1);
    y = thug_platform_round_x87_single(y*0.5);
    style->drawable->pivot_y = (float)thug_platform_round_x87_single(y*style->height);
    __builtin_memcpy(&style->drawable->rotation,&style->rotation,4);
    __builtin_memcpy(&style->drawable->color,style->color,4);
}
/* 0x004c70b0 and 0x004c70c0. Sprite ordering uses depth only. */
void thug_sprite_draw_style_visibility(ThugSpriteDrawStyle *style) {
    thug_drawable_set_hidden(&style->drawable->drawable,style->hidden);
}
void thug_sprite_draw_style_order(ThugSpriteDrawStyle *style) {
    if (style->drawable) thug_drawable_set_depth(&style->drawable->drawable,style->depth);
}
/* 0x004b3d80. Re-read the virtual table between calls. */
void thug_sprite_draw_style_update(ThugSpriteDrawStyle *style) {
    style->methods->data(style); style->methods->order(style); style->methods->visibility(style);
}
/* 0x0049ec90. The data virtual is part of setting a rotation. */
void thug_sprite_draw_style_set_rotation(ThugSpriteDrawStyle *style, float angle) {
    const ThugSpriteDrawStyleMethods *methods = style->methods;
    __builtin_memcpy(&style->rotation,&angle,4);
    methods->data(style);
}
/* 0x004af240. The current-angle comparison uses the unspilled x87 exponent;
 * the target comparison and sprite call use the stored float instead. */
void thug_ui_sprite_set_rotation(ThugUiSprite *widget, float degrees, uint32_t set_target) {
    double angle = thug_platform_round_x87_single((double)degrees * (double)0.01745329238474369f);
    angle = thug_platform_round_x87_single(angle + (double)0.0010000000474974513f);
    float stored = (float)angle;
    if ((double)widget->layout.rotation != angle) {
        widget->layout.rotation = stored; widget->layout.element.object.unknown_8_to_10[0] |= 0x400;
    }
    if (set_target && widget->layout.target_rotation != stored) {
        thug_sprite_draw_style_set_rotation(widget->style,stored);
        widget->layout.target_rotation = stored; widget->layout.element.object.unknown_8_to_10[0] |= 0x400;
    }
}
const ThugTextDrawStyleMethods thug_draw_style_base_methods = {
    0,thug_draw_style_noop,thug_draw_style_noop,thug_draw_style_noop,thug_draw_style_noop,thug_draw_style_noop
};
const ThugTextDrawStyleMethods thug_text_draw_style_methods = {
    0,NULL,thug_text_draw_style_visibility,thug_text_draw_style_data,thug_text_draw_style_order,thug_draw_style_noop
};
ThugDrawable *thug_drawables;
ThugTextDrawStyle *thug_text_draw_style_pool;
/* 0x004df900. Equal depths insert before existing nodes. Unordered comparisons
 * advance, matching the original x87 condition flags rather than a > test. */
void thug_drawable_insert(ThugDrawable *drawable) {
    ThugDrawable **link = &thug_drawables;
    while (*link && !(drawable->depth <= (*link)->depth)) link = &(*link)->next;
    drawable->next = *link;
    *link = drawable;
}
/* 0x004df950. The removed node retains its next pointer. */
void thug_drawable_unlink(ThugDrawable *drawable) {
    ThugDrawable **link = &thug_drawables;
    while (*link && *link != drawable) link = &(*link)->next;
    if (*link) *link = drawable->next;
}
/* 0x004dfa70. Depth is copied as raw bits, including signaling NaNs. */
ThugDrawable *thug_drawable_initialize(ThugDrawable *drawable, uint32_t depth_bits, uint32_t hidden) {
    __builtin_memcpy(&drawable->depth,&depth_bits,4);
    drawable->methods = thug_drawable_methods;
    drawable->hidden = (uint8_t)hidden;
    drawable->priority = 0;
    drawable->next = NULL;
    if (!drawable->hidden) thug_drawable_insert(drawable);
    return drawable;
}
/* 0x004ceed0. */
ThugTextDrawable *thug_text_drawable_initialize(ThugTextDrawable *drawable, uint32_t depth_bits) {
    thug_drawable_initialize(&drawable->drawable,depth_bits,1);
    drawable->drawable.methods = thug_text_drawable_methods;
    return drawable;
}
/* 0x004dfae0. */
void thug_drawable_set_depth(ThugDrawable *drawable, float depth) {
    if (drawable->depth != depth) {
        drawable->depth = depth;
        if (!drawable->hidden) { thug_drawable_unlink(drawable); thug_drawable_insert(drawable); }
    }
}
/* 0x004dfb20. Positive priority clears nonzero depth and reorders visible nodes. */
void thug_drawable_set_priority(ThugDrawable *drawable, float priority) {
    drawable->priority = priority;
    if (priority > 0 && drawable->depth != 0) {
        drawable->depth = 0;
        if (!drawable->hidden) { thug_drawable_unlink(drawable); thug_drawable_insert(drawable); }
    }
}
/* 0x004dfb70. Nonzero byte values remain distinct. */
void thug_drawable_set_hidden(ThugDrawable *drawable, uint32_t hidden) {
    if (drawable->hidden != (uint8_t)hidden) {
        drawable->hidden = (uint8_t)hidden;
        if (drawable->hidden) thug_drawable_unlink(drawable);
        else thug_drawable_insert(drawable);
    }
}
/* 0x005480a0. This virtual method is a return-only function in the original. */
void thug_draw_style_noop(ThugTextDrawStyle *style) { (void)style; }
/* 0x0048d220. Offsets 30/34 and all derived fields are left untouched. */
ThugTextDrawStyle *thug_draw_style_initialize(ThugTextDrawStyle *style, uint32_t owner) {
    style->scale_x = style->scale_y = 0x3f800000;
    style->methods = &thug_draw_style_base_methods;
    style->font = NULL; style->records = NULL;
    style->x = style->y = style->value_18 = style->value_1c = style->value_28 = 0;
    style->depth = 0;
    style->color = 0x80808080;
    style->flag_3c = style->unknown_3d = style->use_priority = 0;
    style->hidden = 1;
    style->owner = owner; style->next = NULL; style->value_c = 0;
    return style;
}
/* 0x004b3f50. These are raw copies, not floating-point conversions. */
void thug_text_draw_style_data(ThugTextDrawStyle *style) {
    const ThugFont *font = style->font;
    style->drawable->value_1c = style->value_c;
    if (font) style->drawable->metrics = font->metrics;
    style->drawable->value_30 = style->value_18;
    style->drawable->value_34 = style->value_1c;
    style->drawable->records = style->records;
    style->drawable->value_38 = style->value_28;
    style->drawable->x = style->x; style->drawable->y = style->y;
    style->drawable->scale_x = style->scale_x; style->drawable->scale_y = style->scale_y;
    style->drawable->color = style->color; style->drawable->flag_40 = style->flag_3c;
}
/* 0x004b3db0. Signed FILD is corrected before the multiply for high-bit IDs. */
void thug_text_draw_style_order(ThugTextDrawStyle *style) {
    thug_drawable_set_depth(&style->drawable->drawable,style->depth);
    float priority = 0;
    if (style->use_priority) {
        double value = (int32_t)style->priority;
        if ((int32_t)style->priority < 0) value = thug_platform_round_x87_single(value + 4294967296.0);
        priority = (float)thug_platform_round_x87_single(value * 0x1p-16);
    }
    thug_drawable_set_priority(&style->drawable->drawable,priority);
}
/* 0x004b3da0. */
void thug_text_draw_style_visibility(ThugTextDrawStyle *style) {
    thug_drawable_set_hidden(&style->drawable->drawable,style->hidden);
}
/* 0x0048d1b0. */
void thug_draw_style_set_owner(ThugTextDrawStyle *style, uint32_t owner) {
    const ThugTextDrawStyleMethods *methods = style->methods;
    style->owner = owner;
    methods->owner(style);
}
/* 0x004b3e70. The supplied heap adapter owns initialized allocation services. */
ThugTextDrawStyle *thug_text_draw_style_initialize(ThugTextDrawStyle *style, const ThugMemory *memory) {
    thug_draw_style_initialize(style,0);
    style->methods = &thug_text_draw_style_methods;
    ThugTextDrawable *drawable = memory->allocate(memory->context,0x44,1);
    style->drawable = drawable ? thug_text_drawable_initialize(drawable,0) : NULL;
    style->priority = 0;
    style->methods->data(style); style->methods->order(style); style->methods->visibility(style);
    return style;
}
/* 0x004b3fd0. Allocation success is the original caller contract. */
void thug_text_draw_style_populate(uint32_t count, const ThugMemory *memory) {
    while (count--) {
        ThugTextDrawStyle *style = memory->allocate(memory->context,0x4c,1);
        if (style) style = thug_text_draw_style_initialize(style,memory);
        style->next = thug_text_draw_style_pool;
        thug_text_draw_style_pool = style;
    }
}
/* 0x0048d1d0. Taking a style does not clear its old pool link. */
ThugTextDrawStyle *thug_text_draw_style_take(void) {
    ThugTextDrawStyle *style = thug_text_draw_style_pool;
    if (style) thug_text_draw_style_pool = style->next;
    return style;
}
/* 0x004b0620. Only the first style in each array receives the ancestor's owner
 * value. Secondary allocation precedes primary allocation and pool acquisition. */
void thug_ui_allocate_text_styles(ThugUiText *widget, int32_t count, uint32_t secondary_only, const ThugMemory *memory) {
    if (widget->has_secondary_styles) {
        memory->temp_scope(memory->context,6);
        widget->secondary_styles = memory->allocate(memory->context,(uint32_t)count*4u,1);
        memory->temp_scope(memory->context,0);
        for (int32_t i = 0; i < count; ++i) widget->secondary_styles[i] = thug_text_draw_style_take();
    }
    if (!(uint8_t)secondary_only) {
        widget->draw_style_count = count;
        memory->temp_scope(memory->context,6);
        widget->draw_styles = memory->allocate(memory->context,(uint32_t)count*4u,1);
        memory->temp_scope(memory->context,0);
        for (int32_t i = 0; i < count; ++i) widget->draw_styles[i] = thug_text_draw_style_take();
    }
    ThugUiElement *ancestor = thug_ui_text_ancestor(&widget->layout.element);
    if (ancestor) {
        if (widget->draw_style_count) thug_draw_style_set_owner(widget->draw_styles[0],thug_ui_font_name(ancestor));
        if (widget->has_secondary_styles) thug_draw_style_set_owner(widget->secondary_styles[0],thug_ui_font_name(ancestor));
    }
}
/* 0x004b0920. The text constructor acquires a style before creating parameters. */
ThugUiText *thug_ui_text_initialize(ThugUiText *widget, const ThugMemory *memory) {
    thug_ui_initialize(&widget->layout);
    widget->layout.element.object.unknown_0 = (uintptr_t)&thug_ui_text_methods;
    widget->color = 0x80000000;
    widget->unknown_17c = 0; widget->font = NULL; widget->text = NULL;
    widget->unknown_190 = 0; widget->has_secondary_styles = 0;
    thug_ui_allocate_text_styles(widget,1,0,memory);
    widget->unknown_1a8 = widget->unknown_1ac = 0;
    widget->flag_1a4 = widget->flag_1a5 = 0;
    thug_ui_object_set_type(&widget->layout.element.base,0x5200dfb6,memory);
    return widget;
}
/* 0x0048d5a0. The original vector destructor walks ten-byte records backwards;
 * its concrete element destructor is the recovered return-only function. */
void thug_draw_style_clear_storage(ThugTextDrawStyle *style, const ThugMemory *memory) {
    if (style->value_c) {
        memory->release(memory->context,(void *)(uintptr_t)style->value_c);
        style->value_c = 0;
    }
    if (style->records) {
        void *allocation = (uint8_t *)style->records-4;
        uint32_t count;
        __builtin_memcpy(&count,allocation,4);
        uintptr_t end = (uintptr_t)style->records + count*10u;
        while ((int32_t)--count >= 0) { end -= 10; thug_draw_style_noop((ThugTextDrawStyle *)end); }
        memory->release(memory->context,allocation);
        style->records = NULL;
    }
}
/* 0x0048d5f0. Visibility is updated before either owned buffer is released. */
void thug_text_draw_style_return(ThugTextDrawStyle *style, const ThugMemory *memory) {
    const ThugTextDrawStyleMethods *methods = style->methods;
    style->hidden = 1;
    methods->visibility(style);
    thug_draw_style_clear_storage(style,memory);
    style->next = thug_text_draw_style_pool;
    thug_text_draw_style_pool = style;
}
/* 0x004b0760. The primary array pointer is deliberately retained after release. */
void thug_ui_release_text_styles(ThugUiText *widget, uint32_t secondary_only, const ThugMemory *memory) {
    if (widget->secondary_styles) {
        for (int32_t i = 0; i < widget->draw_style_count; ++i) thug_text_draw_style_return(widget->secondary_styles[i],memory);
        memory->release(memory->context,widget->secondary_styles);
        widget->secondary_styles = NULL;
    }
    if (!(uint8_t)secondary_only) {
        for (int32_t i = 0; i < widget->draw_style_count; ++i) thug_text_draw_style_return(widget->draw_styles[i],memory);
        memory->release(memory->context,widget->draw_styles);
        widget->draw_style_count = 0;
    }
}
