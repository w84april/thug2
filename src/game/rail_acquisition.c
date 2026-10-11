/* 0050dae0: original fixed and moving rail acquisition. */
#include "rail.h"
#include "stats.h"
#include "attachment.h"
#include "moving_contact.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(offsetof(ThugSkaterPhysics,rebound_gate_time)==0x4e0,"rail cooldown timestamp");
void thug_skater_acquire_rail(ThugSkaterPhysics *p,uint32_t force,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    if(p->state->mode!=1&&!(uint8_t)force)return;
    if(p->state->resistance_requested||p->rotation_requested||!p->input->button_1a0.pressed)return;
    uint32_t elapsed=thug_elapsed_time()+thug_timer_offset-p->rebound_gate_time;
    if(elapsed<(uint32_t)thug_script_get_global_integer(0x96dca7dc,0))return;
    float previous[4],current[4],point[4];ThugRailNode *node;
    thug_vector_copy(previous,p->body->previous_position);thug_vector_copy(current,p->body->position);
    float alignment=1;
    if(thug_skater_orientation_context->identifier!=0xd443a2bc&&thug_time_since(p->rail_reentry_time)<p->rail_retry_delay)
        alignment=(float)thug_platform_cos(thug_platform_multiply_x87_single(thug_script_get_global_number(0x76c1da15,1),0.01745329238474369f));
    ThugObjectTransform *transform=thug_game_context->rail_transform;
    if(thug_rail_search(transform,previous,current,point,&node,0,alignment,0,q)) {
        thug_skater_track_movement(2,p->body->previous_position,p->body->position,d);
        thug_skater_moving_contact_release(p->ground_gate,m);
        if(thug_skater_rail_eligible(p,node,(uintptr_t)transform,0))
            thug_skater_enter_rail(p,point,node,transform,0,0,q,d,m);
        return;
    }
    ThugTransformComponent *component=thug_component_type_head(thug_component_type_registry,0x1cdfb2a3);
    for(;component;component=(void *)(uintptr_t)component->unknown_14) {
        /* Original rail table64637c uses the same5480f0 pointer getter as
         * attachment providers; retain its virtual dispatch and captured result. */
        ThugAttachmentProvider *provider=(void *)component;
        transform=(void *)provider->methods->points(provider);
        float world[16],inverse[16],local_previous[4],local_current[4];
        thug_component_world_transform(component,world);thug_matrix_copy(inverse,world);thug_matrix_inverse(inverse);
        previous[3]=current[3]=1;
        thug_matrix_transform_vector(inverse,local_previous,previous);thug_matrix_transform_vector(inverse,local_current,current);
        if(!thug_rail_search(transform,local_previous,local_current,point,&node,0,alignment,0,q))continue;
        point[3]=1;float world_point[4];thug_matrix_transform_vector(world,world_point,point);thug_vector_copy(point,world_point);
        if(!thug_skater_rail_eligible(p,node,(uintptr_t)transform,0))return;
        thug_skater_enter_rail(p,point,node,transform,0,0,q,d,m);
        thug_skater_moving_contact_set_owner(p->ground_gate,component->base.owner,m);
        thug_skater_store_contact_relative(p->ground_gate,m);
        ThugSkaterBody *owner=(void *)p->ground_gate->contact->reference.object;
        thug_vector_subtract(p->body->velocity,owner->velocity);return;
    }
}
