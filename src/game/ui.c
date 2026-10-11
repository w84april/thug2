#include "ui.h"
#include "object_registry.h"
#include "../script/delivery.h"
#include "../script/lifetime.h"
#include "../platform/math.h"
#include "../script/values.h"
#include <stddef.h>
_Static_assert(offsetof(ThugUiElement, parent) == 0x4c, "UI parent link");
_Static_assert(offsetof(ThugUiLayout, width) == 0x160, "UI width");
_Static_assert(offsetof(ThugUiLayout, target_x) == 0x90, "UI target position");
_Static_assert(offsetof(ThugUiLayout, target_scale_x) == 0xa4, "UI target scale");
_Static_assert(sizeof(ThugUiObjectBase) == 0x4c, "base object size");
_Static_assert(sizeof(ThugUiElement) == 0x7c, "UI tree prefix");
_Static_assert(sizeof(ThugUiLayout) == 0x178, "UI base allocation");
_Static_assert(offsetof(ThugUiObjectBase, queue_node) == 0x28, "object queue node");
_Static_assert(offsetof(ThugUiObjectBase, secondary_target) == 0x40, "secondary reference target");
uint32_t thug_object_default_id = UINT32_MAX, thug_object_default_type;
/* 0x004607c0. Missing parameter storage leaves the output untouched. */
uint8_t thug_ui_object_get_integer(const ThugUiObjectBase *object, uint32_t name, uint32_t *value) {
    return object->parameters ? thug_script_get_integer(object->parameters,name,value,0) : 0;
}
/* 0x004616d0. Allocate the owned parameter structure on demand. */
void thug_ui_object_set_checksum(ThugUiObjectBase *object, uint32_t name, uint32_t value, const ThugMemory *memory) {
    thug_ui_object_ensure_parameters(object,memory);
    thug_script_set_checksum(object->parameters,name,value,memory);
}
const ThugUiObjectMethods thug_ui_object_methods = {.dispose=thug_ui_object_delete,.receive_event=thug_ui_object_event_bridge};
const ThugUiElementMethods thug_ui_element_methods = {.base={.dispose=thug_ui_delete,.receive_event=thug_ui_object_event_bridge}};
const ThugQueueMethods thug_ui_object_queue_methods = {thug_ui_object_queue_delete};
const ThugReferenceTargetMethods thug_ui_object_secondary_methods = {thug_ui_object_secondary_delete};
uint32_t thug_font_table_shift;
ThugObjectLookupNode *thug_font_buckets;
uint8_t thug_button_glyphs[32];
/* 0x00461140. A script event can destroy its owning widget. */
uint8_t thug_ui_object_receive_event(ThugUiObjectBase *object, ThugEvent *event,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!object->object.unknown_8_to_10[2]) return 1;
    ThugObjectReference reference = {&object->object, NULL, NULL};
    thug_object_reference_link(reference.object,&reference);
    thug_script_receive_event((ThugScriptInstance *)(uintptr_t)object->object.unknown_8_to_10[2],event,diagnostics,memory);
    uint8_t alive = reference.object != NULL;
    thug_object_reference_destroy(&reference);
    return alive;
}
/* Platform ABI bridge, not an additional recovered game routine. */
void thug_ui_object_event_bridge(void *object, ThugEvent *event) {
    thug_ui_object_receive_event(object,event,thug_event_services->diagnostics,thug_event_services->memory);
}
/* 0x004a8f00 and 0x004a86c0. */
uint8_t thug_ui_is_input_disabled(const ThugUiElement *widget) {
    do {
        if (widget->object.unknown_8_to_10[0] & 0x200000) return 1;
        widget = widget->parent;
    } while (widget);
    return 0;
}
uint32_t thug_ui_owner(const ThugUiLayout *widget) { return widget->owner; }
/* 0x00460af0. The secondary target has the ordinary reference-base destructor. */
ThugReferenceTarget *thug_ui_object_secondary_delete(ThugReferenceTarget *target,
    uint32_t flags, const ThugMemory *memory) {
    thug_reference_target_destroy(target);
    if ((uint8_t)flags & 1) memory->release(memory->context, target);
    return target;
}
/* 0x00460b20 and 0x00460b40. Re-read links after the first neighbor write. */
void thug_ui_object_queue_destroy(ThugQueueNode *node) {
    node->methods = &thug_ui_object_queue_methods;
    node->next->previous = node->previous;
    node->previous->next = node->next;
    node->previous = node->next = node;
}
ThugQueueNode *thug_ui_object_queue_delete(ThugQueueNode *node, uint32_t flags, const ThugMemory *memory) {
    thug_ui_object_queue_destroy(node);
    if ((uint8_t)flags & 1) memory->release(memory->context, node);
    return node;
}
/* 0x004615d0. Cancel deferred script callbacks before destroying the script;
 * remaining owned scripts are stopped before either reference target is cleared. */
void thug_ui_object_destroy(ThugUiObjectBase *object, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    object->object.unknown_0 = (uintptr_t)&thug_ui_object_methods;
    ThugScriptStructure *parameters = object->parameters;
    if (parameters) {
        thug_script_structure_destroy(parameters, memory);
        thug_script_structure_free(parameters, memory);
    }
    ThugObjectManager *manager = (ThugObjectManager *)(uintptr_t)object->object.unknown_8_to_10[1];
    if (manager) manager->methods->remove(manager, object, memory);
    ThugScriptInstance *script = (ThugScriptInstance *)(uintptr_t)object->object.unknown_8_to_10[2];
    if (script) {
        thug_script_clear_deferred(script);
        script = (ThugScriptInstance *)(uintptr_t)object->object.unknown_8_to_10[2];
        if (script) {
            thug_script_destroy(script, diagnostics, memory);
            thug_script_free(script, memory);
        }
        object->object.unknown_8_to_10[2] = 0;
    }
    thug_script_stop_all_for_owner(&object->object, diagnostics, memory);
    thug_reference_target_destroy(&object->secondary_target);
    thug_ui_object_queue_destroy(&object->queue_node);
    thug_reference_target_destroy((ThugReferenceTarget *)&object->object);
}
/* 0x00461900. */
void *thug_ui_object_delete(void *object, uint32_t flags, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_ui_object_destroy(object, diagnostics, memory);
    if ((uint8_t)flags & 1) memory->release(memory->context, object);
    return object;
}
/* 0x004aab30. Detach before changing the ID, then clear references in reverse
 * member order. This destructor does not recursively delete child widgets. */
void thug_ui_destroy(ThugUiLayout *widget, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    widget->element.object.unknown_0 = (uintptr_t)&thug_ui_element_methods;
    ThugObjectReference parent = {0};
    thug_ui_set_parent(widget, &parent, 0);
    thug_object_reference_destroy(&parent);
    widget->element.object.id = 0xdeadbeef;
    thug_object_reference_destroy(&widget->element.previous_sibling);
    thug_object_reference_destroy(&widget->element.next_sibling);
    thug_object_reference_destroy(&widget->element.children);
    thug_object_reference_destroy(&widget->element.parent_reference);
    thug_ui_object_destroy(&widget->element.base, diagnostics, memory);
}
/* 0x004aac90. */
void *thug_ui_delete(void *widget, uint32_t flags, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_ui_destroy(widget, diagnostics, memory);
    if ((uint8_t)flags & 1) memory->release(memory->context, widget);
    return widget;
}
/* 0x00460b80. All unmentioned fields retain their incoming bytes. */
ThugUiObjectBase *thug_ui_object_initialize(ThugUiObjectBase *object) {
    thug_reference_target_initialize((ThugReferenceTarget *)&object->object);
    object->object.unknown_0 = (uintptr_t)&thug_ui_object_methods;
    object->queue_node.methods = &thug_ui_object_queue_methods;
    object->queue_node.value = object;
    object->queue_node.priority = 0;
    object->queue_node.previous = object->queue_node.next = &object->queue_node;
    thug_reference_target_initialize(&object->secondary_target);
    object->secondary_owner = &object->object;
    object->secondary_target.methods = &thug_ui_object_secondary_methods;
    object->object.id = thug_object_default_id;
    object->type = thug_object_default_type;
    object->parameters = NULL;
    object->object.unknown_8_to_10[2] = 0;
    object->object.unknown_8_to_10[1] = 0;
    object->object.unknown_8_to_10[0] = 0;
    object->alias_count = object->unknown_1c = 0;
    return object;
}
/* 0x004611e0. An empty selected pool does not fall back to the generic heap. */
void thug_ui_object_ensure_parameters(ThugUiObjectBase *object, const ThugMemory *memory) {
    if (!object->parameters) {
        memory->temp_scope(memory->context,6);
        ThugFixedPool *pool = thug_script_structure_pools[thug_script_structure_pool_index];
        ThugScriptStructure *parameters = pool ? thug_pool_allocate(pool) : memory->allocate(memory->context,8,1);
        object->parameters = parameters ? thug_script_structure_initialize(parameters) : NULL;
        memory->temp_scope(memory->context,0);
    }
}
/* 0x00461970. */
void thug_ui_object_set_type(ThugUiObjectBase *object, uint32_t type, const ThugMemory *memory) {
    object->type = type;
    thug_ui_object_ensure_parameters(object,memory);
    thug_script_set_checksum(object->parameters,0x7321a8d6,type,memory);
}
static void store_word(void *base, uint32_t offset, uint32_t word) {
    __builtin_memcpy((uint8_t *)base+offset,&word,4);
}
/* 0x004a8f90. The two copied states include four intentionally untouched words. */
ThugUiLayout *thug_ui_initialize(ThugUiLayout *widget) {
    thug_ui_object_initialize(&widget->element.base);
    widget->element.object.unknown_0 = (uintptr_t)&thug_ui_element_methods;
    widget->element.parent_reference = (ThugObjectReference){0};
    widget->element.children = (ThugObjectReference){0};
    widget->element.next_sibling = (ThugObjectReference){0};
    widget->element.previous_sibling = (ThugObjectReference){0};
    store_word(widget,0x108,0);
    const uint32_t ones[] = {0xa4,0xa8,0xac,0xb0,0x8c,0x7c};
    const uint32_t zeros[] = {0x90,0x94,0xb4,0x80,0x84,0x88};
    for (uint32_t i = 0; i < 6; ++i) store_word(widget,ones[i],0x3f800000);
    for (uint32_t i = 0; i < 6; ++i) store_word(widget,zeros[i],0);
    store_word(widget,0xb8,0x80808080);
    thug_ui_copy_layout_state((uint8_t *)widget+0xc0,(uint8_t *)widget+0x7c);
    thug_ui_copy_layout_state((uint8_t *)widget+0x114,(uint8_t *)widget+0x7c);
    widget->element.object.unknown_8_to_10[0] |= 0x10400;
    widget->width = widget->height = 0;
    widget->color = 0x80808080;
    widget->owner = 0; widget->depth = 0; widget->unknown_170 = 1;
    return widget;
}
/* 0x004a8f20. */
uint8_t thug_ui_has_inherited_owner(const ThugUiElement *widget) {
    do {
        if (widget->object.unknown_8_to_10[0] & 0x10000000) return 1;
        widget = widget->parent;
    } while (widget);
    return 0;
}
static void reference_start(ThugObjectReference *reference, ThugReferencedObject *object) {
    *reference = (ThugObjectReference){object,NULL,NULL};
    if (object) thug_object_reference_link(object,reference);
}
/* 0x004aa390. Fixed-depth widgets still propagate the incoming depth to children. */
void thug_ui_set_depth_tree(ThugUiLayout *widget, float depth) {
    if (!(widget->element.object.unknown_8_to_10[0] & 0x8000)) {
        widget->element.object.unknown_8_to_10[0] |= 0x1000;
        widget->depth = depth;
    }
    ThugObjectReference child;
    reference_start(&child,widget->element.children.object);
    if (child.object) {
        float next_depth = (float)thug_platform_round_x87_single((double)depth+1);
        do {
            thug_ui_set_depth_tree((ThugUiLayout *)child.object,next_depth);
            ThugReferencedObject *next = ((ThugUiElement *)child.object)->next_sibling.object;
            thug_object_reference_assign(&child,next);
        } while (child.object);
    }
}
/* 0x004aa470. */
void thug_ui_set_owner_tree(ThugUiLayout *widget, uint32_t owner) {
    widget->element.object.unknown_8_to_10[0] |= 0x10000000;
    widget->owner = owner;
    ThugObjectReference child;
    reference_start(&child,widget->element.children.object);
    while (child.object) {
        thug_ui_set_owner_tree((ThugUiLayout *)child.object,owner);
        ThugReferencedObject *next = ((ThugUiElement *)child.object)->next_sibling.object;
        thug_object_reference_assign(&child,next);
    }
}
/* 0x004aa8e0. Parent changes update intrusive sibling references before
 * appending to the new parent's tail. The second argument is unused. */
void thug_ui_set_parent(ThugUiLayout *widget, const ThugObjectReference *parent, uint32_t unused) {
    (void)unused;
    ThugUiElement *element = &widget->element;
    if (element->parent) {
        ThugObjectReference current;
        reference_start(&current,element->parent->children.object);
        while (current.object && current.object != &element->object) {
            ThugReferencedObject *next = ((ThugUiElement *)current.object)->next_sibling.object;
            thug_object_reference_assign(&current,next);
        }
        if (current.object) {
            ThugObjectReference *previous = element->previous_sibling.object ?
                &((ThugUiElement *)element->previous_sibling.object)->next_sibling : &element->parent->children;
            thug_object_reference_assign(previous,element->next_sibling.object);
            if (element->next_sibling.object)
                thug_object_reference_assign(&((ThugUiElement *)element->next_sibling.object)->previous_sibling,element->previous_sibling.object);
            thug_object_reference_unlink(current.object,&current);
        }
    }
    thug_object_reference_assign(&element->parent_reference,parent->object);
    if (element->parent) {
        ThugObjectReference last;
        reference_start(&last,element->parent->children.object);
        while (last.object && ((ThugUiElement *)last.object)->next_sibling.object) {
            ThugReferencedObject *next = ((ThugUiElement *)last.object)->next_sibling.object;
            thug_object_reference_assign(&last,next);
        }
        ThugObjectReference *tail = last.object ? &((ThugUiElement *)last.object)->next_sibling : &element->parent->children;
        thug_object_reference_assign(tail,&element->object);
        thug_object_reference_assign(&element->previous_sibling,last.object);
        if (last.object) thug_object_reference_unlink(last.object,&last);
    } else thug_object_reference_assign(&element->previous_sibling,NULL);
    thug_object_reference_assign(&element->next_sibling,NULL);
    float depth = 0;
    ThugUiLayout *new_parent = (ThugUiLayout *)parent->object;
    if (new_parent) {
        if (thug_ui_has_inherited_owner(&new_parent->element)) thug_ui_set_owner_tree(widget,new_parent->owner);
        /* The source reference is reread after owner propagation. */
        new_parent = (ThugUiLayout *)parent->object;
        depth = (float)thug_platform_round_x87_single((double)new_parent->depth+1);
    }
    thug_ui_set_depth_tree(widget,depth);
}
/* 0x004a8730. Forward word copies deliberately preserve overlapping behavior. */
void *thug_ui_copy_layout_state(void *destination, const void *source) {
    for (uint32_t i = 0; i < 17; ++i) {
        uint32_t word;
        __builtin_memcpy(&word,(const uint8_t *)source + i*4,4);
        __builtin_memcpy((uint8_t *)destination + i*4,&word,4);
    }
    return destination;
}
/* 0x004a8b80. As with lookup, the output must initially be unlinked. */
ThugObjectReference *thug_ui_parent_reference(const ThugUiElement *widget, ThugObjectReference *out) {
    out->previous = out->next = NULL;
    out->object = (ThugReferencedObject *)widget->parent;
    if (out->object) thug_object_reference_link(out->object,out);
    return out;
}
/* 0x004a8bb0. Temporary references are linked and released at every step. */
ThugUiElement *thug_ui_text_ancestor(const ThugUiElement *widget) {
    for (;;) {
        ThugObjectReference parent;
        thug_ui_parent_reference(widget,&parent);
        ThugUiElement *next = (ThugUiElement *)parent.object;
        if (parent.object) thug_object_reference_unlink(parent.object,&parent);
        if (!next) return NULL;
        uint32_t type;
        __builtin_memcpy(&type,(const uint8_t *)next+0x18,4);
        if (type == UINT32_C(0xa13adbb7)) return next;
        widget = next;
    }
}
/* 0x004020e0. A single base-32 character, not a decimal integer parser. */
uint32_t thug_text_digit(const char *text) {
    uint8_t c = (uint8_t)*text;
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'v') return c - 'a' + 10;
    return c >= 'A' && c <= 'V' ? c - 'A' + 10 : 0;
}
/* 0x0048d6a0. */
uint8_t thug_text_button_glyph(const char *text) { return thug_button_glyphs[thug_text_digit(text)]; }
/* 0x0048d760. Null matching values are skipped; five shift bits are used. */
void *thug_font_find(uint32_t name) {
    uint32_t slot = name & ((UINT32_C(1) << (thug_font_table_shift & 31)) - 1);
    ThugObjectLookupNode *node = (void *)((uintptr_t)thug_font_buckets + slot * 12u);
    for (; node; node = node->next) {
        if (node->key == name && node->value) {
            void *font; __builtin_memcpy(&font, (uint8_t *)node->value + 0x18, sizeof(font)); return font;
        }
    }
    return NULL;
}
/* 0x004aae20. Both temporary and returned references are linked in order. */
ThugObjectReference *thug_ui_find(ThugObjectReference *out, uint32_t name, uint32_t unused) {
    (void)unused;
    ThugObjectReference local = {thug_object_manager_find(thug_object_lookup_manager, name), NULL, NULL};
    if (local.object) {
        thug_object_reference_link(local.object, &local);
        out->previous = out->next = NULL; out->object = local.object;
        if (local.object) thug_object_reference_link(local.object, out);
        if (local.object) thug_object_reference_unlink(local.object, &local);
    } else { out->previous = out->next = NULL; out->object = NULL; }
    return out;
}
/* 0x004a8f40. Hidden status propagates through valid parent links. */
uint8_t thug_ui_is_hidden(const ThugUiElement *element) {
    while (element) { if (element->object.unknown_8_to_10[0] & 0x400000) return 1; element = element->parent; }
    return 0;
}
/* 0x004a8940. Compare the entire argument against the old boolean; only the
 * value one sets the flag, but any unequal value still sends its event. */
void thug_ui_set_events_enabled(ThugUiElement *element, uint32_t enabled, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint32_t flags = element->object.unknown_8_to_10[0];
    if (enabled != !!(flags & 0x4000)) {
        element->object.unknown_8_to_10[0] = enabled == 1 ? flags | 0x4000 : flags & ~UINT32_C(0x4000);
        thug_event_emit((ThugEventManager *)thug_object_lookup_manager, enabled == 1 ? 0x3056434f : 0x4a57316b,
            element->object.id, 0x36b2ee74, NULL, 0, -1, diagnostics, memory);
    }
}
static double rounded(double value) { return thug_platform_round_x87_single(value); }
/* Keep each x87 operation at 24-bit precision with its extended exponent.
 * Size and scale setters multiply their operands in different orders. */
static float layout_position(float anchor, float pivot, float first, float second) {
    double offset = rounded((double)pivot + 1.0);
    offset = rounded(offset * first);
    offset = rounded(offset * second);
    offset = rounded(offset * 0.5);
    return (float)rounded((double)anchor - offset);
}
/* 0x004a9100. Copy both anchor words when either changes, then update position.
 * Target coordinates change independently; unordered comparisons count as changed. */
void thug_ui_set_position(ThugUiLayout *widget, float x, float y, uint32_t set_target) {
    if (widget->anchor_x != x || widget->anchor_y != y) {
        widget->anchor_x = x; widget->anchor_y = y;
        widget->element.object.unknown_8_to_10[0] |= 0x400;
        float py = layout_position(y,widget->pivot_y,widget->height,widget->scale_y);
        widget->position_x = layout_position(x,widget->pivot_x,widget->width,widget->scale_x);
        widget->position_y = py;
    }
    if (set_target && (widget->target_x != x || widget->target_y != y)) {
        widget->target_x = x; widget->target_y = y;
        widget->element.object.unknown_8_to_10[0] |= 0x400;
    }
}
/* 0x004a92d0. */
void thug_ui_set_size(ThugUiLayout *widget, float width, float height, uint32_t fixed) {
    if (widget->width != width || widget->height != height) {
        widget->element.object.unknown_8_to_10[0] |= 0x400;
        widget->width = width; widget->height = height;
        float y = layout_position(widget->anchor_y,widget->pivot_y,widget->scale_y,height);
        widget->position_x = layout_position(widget->anchor_x,widget->pivot_x,widget->scale_x,width);
        widget->position_y = y;
    }
    if (fixed) widget->element.object.unknown_8_to_10[0] |= 0x2000;
    else widget->element.object.unknown_8_to_10[0] &= ~UINT32_C(0x2000);
}
/* 0x004a94a0. Only the relative flag is truncated to its low byte. */
void thug_ui_set_scale(ThugUiLayout *widget, float x, float y, uint32_t relative, uint32_t set_target) {
    if (widget->scale_x != x || widget->scale_y != y || (uint8_t)relative) {
        if ((uint8_t)relative) {
            x = (float)rounded((double)x * widget->base_scale_x);
            y = (float)rounded((double)y * widget->base_scale_y);
        } else { widget->base_scale_x = x; widget->base_scale_y = y; }
        widget->scale_x = x; widget->scale_y = y;
        float py = layout_position(widget->anchor_y,widget->pivot_y,widget->height,y);
        widget->position_x = layout_position(widget->anchor_x,widget->pivot_x,widget->width,x);
        widget->position_y = py;
        widget->element.object.unknown_8_to_10[0] |= 0x400;
    }
    if (set_target && (widget->target_scale_x != x || widget->target_scale_y != y)) {
        widget->target_scale_x = x; widget->target_scale_y = y;
        widget->element.object.unknown_8_to_10[0] |= 0x400;
    }
}
