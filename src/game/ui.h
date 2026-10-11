#ifndef THUG_GAME_UI_H
#define THUG_GAME_UI_H
#include "stats.h"
#include "../network/queue.h"
typedef struct {
    ThugReferencedObject object;
    uint32_t type, unknown_1c;
    ThugScriptStructure *parameters;
    uint32_t unknown_24;
    ThugQueueNode queue_node;
    uint32_t alias_count;
    ThugReferenceTarget secondary_target;
    ThugReferencedObject *secondary_owner;
} ThugUiObjectBase;
typedef struct ThugUiElement {
    union {
        ThugUiObjectBase base;
        struct { ThugReferencedObject object; uint8_t unknown_18_to_4b[0x34]; };
    };
    union {
        ThugObjectReference parent_reference;
        struct { struct ThugUiElement *parent; ThugObjectReference *parent_previous, *parent_next; };
    };
    ThugObjectReference children, next_sibling, previous_sibling;
} ThugUiElement;
typedef struct {
    ThugUiElement element;
    uint8_t unknown_7c[0x14];
    float target_x, target_y;
    uint8_t unknown_98[0xc];
    float target_scale_x, target_scale_y;
    uint8_t unknown_ac[8];
    float target_rotation;
    uint8_t unknown_b8[0x1c];
    float anchor_x, anchor_y, unknown_dc;
    float position_x, position_y, scale_x, scale_y, base_scale_x, base_scale_y;
    float rotation;
    uint8_t unknown_fc[0x5c];
    float pivot_x, pivot_y, width, height;
    uint32_t color;
    float depth, unknown_170;
    uint32_t owner;
} ThugUiLayout;
extern uint32_t thug_object_default_id, thug_object_default_type;
typedef struct ThugEvent ThugEvent;
typedef struct {
    void *(*dispose)(void *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
    uint32_t unavailable_4[4];
    void (*receive_event)(void *, ThugEvent *);
    uint32_t unavailable_18[2];
} ThugUiObjectMethods;
typedef struct { ThugUiObjectMethods base; uint32_t unavailable[3]; } ThugUiElementMethods;
/* Recovered destruction and event methods; other slots remain unavailable. */
extern const ThugUiObjectMethods thug_ui_object_methods;
extern const ThugUiElementMethods thug_ui_element_methods;
extern const ThugQueueMethods thug_ui_object_queue_methods;
extern const ThugReferenceTargetMethods thug_ui_object_secondary_methods;
ThugUiObjectBase *thug_ui_object_initialize(ThugUiObjectBase *);
uint8_t thug_ui_object_receive_event(ThugUiObjectBase *, ThugEvent *, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_object_event_bridge(void *, ThugEvent *);
uint8_t thug_ui_is_input_disabled(const ThugUiElement *);
uint32_t thug_ui_owner(const ThugUiLayout *);
void thug_ui_object_destroy(ThugUiObjectBase *, const ThugDiagnostics *, const ThugMemory *);
void *thug_ui_object_delete(void *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_destroy(ThugUiLayout *, const ThugDiagnostics *, const ThugMemory *);
void *thug_ui_delete(void *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_object_queue_destroy(ThugQueueNode *);
ThugQueueNode *thug_ui_object_queue_delete(ThugQueueNode *, uint32_t, const ThugMemory *);
ThugReferenceTarget *thug_ui_object_secondary_delete(ThugReferenceTarget *, uint32_t, const ThugMemory *);
void thug_ui_object_ensure_parameters(ThugUiObjectBase *, const ThugMemory *);
void thug_ui_object_set_type(ThugUiObjectBase *, uint32_t, const ThugMemory *);
uint8_t thug_ui_object_get_integer(const ThugUiObjectBase *, uint32_t name, uint32_t *);
void thug_ui_object_set_checksum(ThugUiObjectBase *, uint32_t name, uint32_t value, const ThugMemory *);
ThugUiLayout *thug_ui_initialize(ThugUiLayout *);
uint8_t thug_ui_has_inherited_owner(const ThugUiElement *);
void thug_ui_set_depth_tree(ThugUiLayout *, float);
void thug_ui_set_owner_tree(ThugUiLayout *, uint32_t);
void thug_ui_set_parent(ThugUiLayout *, const ThugObjectReference *, uint32_t unused);
extern uint32_t thug_font_table_shift;
extern ThugObjectLookupNode *thug_font_buckets;
extern uint8_t thug_button_glyphs[32];
uint32_t thug_text_digit(const char *);
uint8_t thug_text_button_glyph(const char *);
void *thug_font_find(uint32_t name);
/* The output reference must be unlinked on entry. */
ThugObjectReference *thug_ui_find(ThugObjectReference *, uint32_t name, uint32_t unused);
uint8_t thug_ui_is_hidden(const ThugUiElement *);
void thug_ui_set_events_enabled(ThugUiElement *, uint32_t enabled, const ThugDiagnostics *, const ThugMemory *);
void thug_ui_set_size(ThugUiLayout *, float width, float height, uint32_t fixed);
void thug_ui_set_position(ThugUiLayout *, float x, float y, uint32_t set_target);
void thug_ui_set_scale(ThugUiLayout *, float x, float y, uint32_t relative, uint32_t set_target);
ThugObjectReference *thug_ui_parent_reference(const ThugUiElement *, ThugObjectReference *);
ThugUiElement *thug_ui_text_ancestor(const ThugUiElement *);
void *thug_ui_copy_layout_state(void *destination, const void *source);
#endif
