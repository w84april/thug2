#include "attachment.h"
#include "moving_contact.h"
#include "../core/matrix.h"
#include "../core/vector.h"
#include "../platform/math.h"
#include "../script/delivery.h"
#include <stddef.h>
_Static_assert(offsetof(ThugAttachmentProviderMethods, points) == 0x34, "Point provider method");
_Static_assert(offsetof(ThugAttachmentProvider, points) == 0x18, "Provider points");
_Static_assert(offsetof(ThugAttachmentComponent, provider) == 0x1c, "Attachment provider");
_Static_assert(offsetof(ThugAttachmentPoints, transform) == 8, "Point transform");
_Static_assert(offsetof(ThugSkaterBody, orientation_c0) == 0xc0, "Owner cached orientation");
_Static_assert(offsetof(ThugSkaterPhysics, attachment_moving) == 0x24a, "Attachment movement");
_Static_assert(offsetof(ThugSkaterPhysics, attachment_index) == 0x24c, "Attachment index");
_Static_assert(offsetof(ThugSkaterPhysics, attachment_direction) == 0x250, "Attachment direction");
_Static_assert(offsetof(ThugSkaterInput, button_a0) == 0xa0, "Input a0");
_Static_assert(offsetof(ThugSkaterInput, button_c0) == 0xc0, "Input c0");
_Static_assert(offsetof(ThugSkaterInput, button_100) == 0x100, "Input 100");
_Static_assert(offsetof(ThugSkaterInput, button_120) == 0x120, "Input 120");
#define R24 thug_platform_round_x87_single

_Static_assert(offsetof(ThugAttachmentComponent,next_of_type)==0x14,"Type chain");
_Static_assert(offsetof(ThugAttachmentComponent,enabled)==0x18,"Attachment enabled");
_Static_assert(offsetof(ThugSkaterPhysics,attachment_reference)==0x364,"Selected attachment");
/* 0x00503ec0. Strict input age and nearest-distance tests preserve the first
 * component on ties. Event delivery can change the live skater body. */
void thug_skater_find_attachment(ThugSkaterPhysics *p,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    if(p->parameter_mode_active)return;
    ThugInputButton *button=&p->input->button_20;
    if(p->state->moving_contact_locked||!button->pressed)return;
    uint32_t age=thug_input_button_elapsed(button);
    if(age<=thug_script_get_global_integer(0x19b2c752,0)||p->state->mode!=0)return;
    float best=(float)thug_script_get_global_number(0x2928f080,1);
    ThugSkaterBody *selected=0;
    for(ThugAttachmentComponent *component=thug_component_type_head(thug_component_type_registry,0x3506ce64);
        component;component=component->next_of_type) {
        if(!component->enabled)continue;
        ThugSkaterBody *owner=component->base.owner;
        if(owner==p->body)continue;
        float point[4]={0,0,0,1};
        int32_t index=thug_attachment_nearest(component,point,p->body->position);
        if(index==-1)continue;
        float difference[4];thug_vector_difference(difference,point,p->body->position);
        double distance=thug_vector_length(difference);
        if(distance<best) { best=(float)distance;selected=owner;p->attachment_index=index; }
    }
    if(!selected)return;
    thug_input_button_clear_latch((ThugInputButton *)((uint8_t *)button+0x80));
    thug_input_button_clear_latch((ThugInputButton *)((uint8_t *)button+0xe0));
    thug_object_reference_assign(&p->attachment_reference,(ThugReferencedObject *)selected);
    thug_object_emit_event((ThugReferencedObject *)selected,0x2f184eb1,0,diagnostics,memory);
    thug_object_emit_event((ThugReferencedObject *)p->body,0x2f184eb1,0,diagnostics,memory);
}

/* 0x005480f0, the point-provider slot in original table 0x006462d4. */
ThugAttachmentPoints *thug_attachment_provider_points(ThugAttachmentProvider *provider) { return provider->points; }
const ThugAttachmentProviderMethods thug_attachment_provider_methods = {{0}, thug_attachment_provider_points};

/* 0x00469340. The flag write precedes the overlapping forward matrix copy. */
void thug_attachment_set_transform(ThugAttachmentPoints *points, const float matrix[16]) {
    points->transformed = 1;
    thug_matrix_copy(points->transform, matrix);
}
/* Original final copies load X through x87, but retain the other raw words. */
static void copy_point(float out[4], const float in[4]) {
    uint32_t x;
    __builtin_memcpy(&x, in, 4);
    if ((x & 0x7f800000) == 0x7f800000 && (x & 0x7fffff)) x |= 0x400000;
    __builtin_memcpy(out, &x, 4);
    for (unsigned i = 1; i < 4; ++i) __builtin_memcpy(out+i, in+i, 4);
}
/* 0x00469350. The transformed path snapshots before writing; the raw path
 * copies forward, and therefore has different partial-overlap behavior. */
void thug_attachment_point_position(const ThugAttachmentPoints *points, float out[4], const float point[4]) {
    if (!points->transformed) { thug_vector_copy(out, point); return; }
    float value[4];
    thug_matrix_transform_vector(points->transform, value, point);
    copy_point(out, value);
}
static void set_owner_transform(ThugAttachmentPoints *points, const ThugSkaterBody *body) {
    float matrix[16];
    thug_matrix_copy(matrix, body->orientation);
    matrix[3] = matrix[7] = matrix[11] = 0;
    for (unsigned i = 0; i < 3; ++i) matrix[12+i] = body->position[i];
    matrix[15] = 1;
    thug_attachment_set_transform(points, matrix);
}
static void projected_point(ThugAttachmentPoints *points, const ThugSkaterBody *body, const ThugAttachmentPoint *point, float out[4]) {
    thug_attachment_point_position(points, out, point->position);
    thug_vector_subtract(out, body->position);
    thug_vector_project_plane(out, body->orientation+4);
    thug_vector_add(out, body->position);
}
/* 0x0051ba70. The candidate stays wide for comparison; best distance spills
 * to float only after accepting a strictly nearer, ordered candidate. */
int32_t thug_attachment_nearest(ThugAttachmentComponent *component, float out[4], const float target[4]) {
    ThugSkaterBody *body = component->base.owner;
    if (!component->provider || !body) return -1;
    ThugAttachmentPoints *points = component->provider->methods->points(component->provider);
    if (!points) return -1;
    set_owner_transform(points, body);
    float best = 1e14f, position[4] = {0,0,0,1};
    int32_t selected = -1;
    uint32_t index = 0;
    for (ThugAttachmentPoint *point = points->head; point; point = point->next, ++index) {
        float value[4];
        projected_point(points, body, point, value);
        double x = R24((double)value[0]-target[0]), y = R24((double)value[1]-target[1]), z = R24((double)value[2]-target[2]);
        double distance = R24(R24(R24(z*z)+R24(y*y))+R24(x*x));
        if (distance < best) { best = (float)distance; selected = (int32_t)index; thug_vector_copy(position,value); }
    }
    copy_point(out, position);
    return selected;
}
/* 0x0051bc70. Exhausting the list is success without an output write. */
uint8_t thug_attachment_indexed(ThugAttachmentComponent *component, float out[4], int32_t index) {
    ThugSkaterBody *body = component->base.owner;
    if (!component->provider || !body) return 0;
    ThugAttachmentPoints *points = component->provider->methods->points(component->provider);
    if (!points) return 0;
    set_owner_transform(points, body);
    uint32_t current = 0;
    for (ThugAttachmentPoint *point = points->head; point; point = point->next, ++current) {
        if (current == (uint32_t)index) {
            float value[4];
            projected_point(points, body, point, value);
            copy_point(out, value);
            break;
        }
    }
    return 1;
}
/* 0x00501db0. Input latches choose a new point, then movement follows the
 * current contact while retaining the originally captured owner/component. */
void thug_skater_update_attachment(ThugSkaterPhysics *p, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugMovingContact *contact = p->ground_gate->contact;
    ThugSkaterInput *input = p->input;
    if (!contact || !contact->reference.object) {
        thug_object_emit_event((ThugReferencedObject *)p->body, 0x47d44b84, 0, diagnostics, memory);
        return;
    }
    ThugSkaterBody *owner = (ThugSkaterBody *)contact->reference.object;
    ThugAttachmentComponent *component = (ThugAttachmentComponent *)thug_object_find_component(owner, 0x3506ce64);
    float direction = 0;
    ThugInputButton *buttons[4] = {&input->button_a0,&input->button_100,&input->button_c0,&input->button_120};
    for (unsigned i = 0; i < 4; ++i) if (buttons[i]->pending_10) {
        thug_input_button_clear_latch(buttons[i]);
        direction = i & 1 ? -1 : 1;
    }
    if (direction != 0 && (!p->attachment_moving || direction != p->attachment_direction)) {
        for (float distance = 6; distance < 120; distance += 6) {
            ThugSkaterBody *body = p->body;
            float factor = distance*direction, target[4], unused[4] = {0,0,0,1};
            for (unsigned i = 0; i < 4; ++i) {
                double product = R24((double)body->orientation[i]*factor);
                if (i != 3) product = (float)product;
                target[i] = (float)R24(product+body->position[i]);
            }
            int32_t index = thug_attachment_nearest(component, unused, target);
            if (index != p->attachment_index) {
                p->attachment_index = index;
                p->attachment_moving = 1;
                p->attachment_direction = direction;
                thug_object_emit_event((ThugReferencedObject *)p->body, direction == 1 ? 0x74bf80cf : 0x2e7474b5, 0, diagnostics, memory);
                break;
            }
        }
    }
    if (!p->ground_gate->contact || !p->state->moving_contact_locked) return;
    float point[4];
    if (!thug_attachment_indexed(component, point, p->attachment_index)) return;
    p->body->position[3] = 0;
    ThugSkaterBody *parameter_body = p->body;
    float negative[4], offset[4], target[4];
    thug_vector_negated(negative, owner->orientation+8);
    float separation = (float)thug_script_get_global_number(0x21fb182c, 1);
    thug_vector_scaled(offset, separation, negative);
    thug_vector_sum(target, point, offset);
    if (p->attachment_moving) {
        float displacement[4], delta[4];
        thug_vector_copy(displacement, p->ground_gate->contact->displacement);
        thug_vector_add(p->body->position, displacement);
        thug_vector_difference(delta, target, p->body->position);
        float squared = (float)thug_vector_length_squared(delta);
        float step = (float)thug_platform_multiply_x87_single(thug_skater_get_parameter(0x97496256, 1, parameter_body), p->time_step);
        if (squared > 32400) {
            thug_object_emit_event((ThugReferencedObject *)p->body, 0x47d44b84, 0, diagnostics, memory);
            return;
        }
        if (!((double)squared <= R24((double)step*step))) {
            float scale = (float)R24((double)step/R24(__builtin_sqrt(squared)));
            thug_vector_scale(delta, scale);
            thug_vector_add(p->body->position, delta);
        } else {
            thug_vector_copy(p->body->position, target);
            p->attachment_moving = 0;
        }
    } else thug_vector_copy(p->body->position, target);
    thug_matrix_copy(p->body->orientation, owner->orientation_c0);
    thug_matrix_copy(p->cached_orientation, p->body->orientation);
}
