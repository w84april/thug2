#include "skater.h"
#include "objectives.h"
#include "collision_events.h"
#include "moving_contact.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include "../script/delivery.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterState, surface_flag_8)==0x40,"Floor flag");
_Static_assert(offsetof(ThugSkaterState, landing_flag_98)==0x98,"Landing flag");
_Static_assert(offsetof(ThugSkaterInput, button_20)==0x20,"Floor input");

/* 0x00509bd0. Full floor contact/leave handling. The original keeps the input
 * pointer across event dispatch while reloading mutable body/state pointers. */
void thug_skater_handle_floor(ThugSkaterPhysics *p, ThugCollisionQuery *query,
        const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugSkaterBody *saved_body=p->body;
    ThugSkaterInput *input=p->input;
    double height=thug_skater_get_parameter(0xe4d79235,1,saved_body);
    for (unsigned i=0;i<4;++i) p->surface_segment[i]=(float)R24(height*saved_body->orientation[4+i]);
    for (unsigned i=0;i<4;++i) p->surface_segment[4+i]=(float)R24(-200.0*p->body->orientation[4+i]);
    for (unsigned i=0;i<4;++i) p->surface_segment[i]=(float)R24((double)p->surface_segment[i]+p->body->position[i]);
    for (unsigned i=0;i<4;++i) p->surface_segment[4+i]=(float)R24((double)p->surface_segment[4+i]+p->body->position[i]);
    if (!thug_skater_query_surface(p,0x10,0,query)) goto leave;
    ThugSkaterBody *body=p->body;
    double dx=R24((double)body->position[0]-p->surface_probe.point[0]);
    double dy=R24((double)body->position[1]-p->surface_probe.point[1]);
    double dz=R24((double)body->position[2]-p->surface_probe.point[2]);
    float distance=(float)R24(__builtin_sqrt(R24(R24(R24(dx*dx)+R24(dz*dz))+R24(dy*dy))));
    float signed_distance=(float)R24(R24(R24(dz*body->orientation[6])+R24(dy*body->orientation[5]))+R24(dx*body->orientation[4]));
    if (!p->surface_skatable) {
        if (signed_distance<(double)0.001f)
            for (unsigned i=0;i<4;++i) body->position[i]=(float)R24((double)p->surface_probe.point[i]+p->surface_probe.normal[i]);
        goto leave;
    }
    float normal[4],forward[4],previous[4];
    thug_vector_copy(normal,p->surface_probe.normal);
    thug_vector_copy(forward,body->orientation+8); thug_vector_copy(previous,forward);
    float normal_dot=(float)R24(R24(R24((double)forward[0]*normal[0])+R24((double)forward[2]*normal[2]))+R24((double)forward[1]*normal[1]));
    thug_vector_project_preserve_length(forward,normal);
    thug_vector_project_preserve_length(previous,p->orientation_target);
    float alignment=(float)R24(R24(R24((double)previous[0]*forward[0])+R24((double)previous[2]*forward[2]))+R24((double)previous[1]*forward[1]));
    double threshold=thug_platform_cos(R24(thug_skater_get_parameter(input->button_20.pressed?0x4138283e:0xef161c2a,1,saved_body)*0.01745329238474369f));
    if (normal_dot>0 && alignment>0 && alignment<threshold) goto leave;
    if (signed_distance>0) {
        float clamped=alignment>1?1:(alignment< -1?-1:alignment);
        body=p->body;
        float x=(float)R24((double)body->position[0]-body->previous_position[0]);
        float y=(float)R24((double)body->position[1]-body->previous_position[1]);
        float z=(float)R24((double)body->position[2]-body->previous_position[2]);
        double tangent=thug_platform_tan(thug_platform_acos_x87_single(clamped));
        double length=R24(__builtin_sqrt(R24(R24(R24((double)x*x)+R24((double)z*z))+R24((double)y*y))));
        float limit=(float)R24(tangent*length);
        double minimum=thug_skater_get_parameter(0x899ba3d0,1,saved_body);
        if (limit<minimum) limit=(float)minimum;
        if (distance>limit) goto leave;
    }
    ThugSkaterState *state=p->state;
    if (state->surface_flag_8!=p->surface_flag_8) {
        state->surface_flag_8=p->surface_flag_8;
        state->surface_flag_time=thug_elapsed_time()+thug_timer_offset;
    }
    thug_skater_set_up_vector(p,normal[0],normal[1],normal[2],normal[3],query);
    thug_vector_copy(p->body->position,p->surface_probe.point);
    state=p->state;
    if (!state->mode && distance>2 && alignment>(double)0.99f && state->landing_flag_98!=1) {
        state->landing_flag_98=1; state->landing_time_9c=thug_elapsed_time()+thug_timer_offset;
    }
    uint8_t material=((const uint8_t *)&p->surface_probe)[0x52];
    union { float value; uint32_t bits; } argument={.value=distance};
    argument.bits=(argument.bits&0xffffff00)|material;
    thug_skater_state_set_material(p->state,argument.bits,diagnostics,memory);
    ((uint8_t *)p->sound)[0x1c]=material;
    thug_skater_blend_orientation(p);
    thug_skater_adjust_moving_contact(p,memory);
    if (p->saved_probe.result.instance!=p->surface_probe.result.instance) {
        static const uint32_t old_events[3]={1,4,0},new_events[3]={1,3,0};
        thug_collision_event_from_probe(p->collision_events,old_events,&p->saved_probe,diagnostics,memory);
        if (p->wall_gate->wall_response_suppressed) return;
        thug_collision_event_from_probe(p->collision_events,new_events,&p->surface_probe,diagnostics,memory);
        if (p->wall_gate->wall_response_suppressed) return;
    }
    if (!((const uint8_t *)p->name_context)[0x13b0]) thug_skater_set_notification_flag(p->name_context,0,diagnostics,memory);
    thug_skater_save_surface(p,&p->surface_probe);
    return;
leave:
    thug_skater_change_state(p,1,diagnostics,memory);
    thug_object_broadcast_event((ThugReferencedObject *)p->body,0xd96f01f1,0,0,diagnostics,memory);
    thug_object_emit_event((ThugReferencedObject *)p->body,0x3b1001b6,0,diagnostics,memory);
    thug_skater_prepare_floor_transition(p,query,diagnostics);
    if (p->state->ground_transition_flag) {
        ThugSkaterState *s=p->state;
        if (s->transition_flag_48!=1) { s->transition_flag_48=1; s->transition_time_4c=thug_elapsed_time()+thug_timer_offset; }
        if (!(input->button_c0.pressed && input->button_120.pressed)) thug_skater_leave_transition(p,0,query,diagnostics,memory);
        int32_t delay=(int32_t)thug_script_get_global_integer(0x6bb5b751,1);
        if ((int32_t)thug_input_button_elapsed_8(&input->button_20)>delay &&
                (int32_t)thug_input_button_elapsed(&input->button_20)>delay) {
            s=p->state;
            if (s->transition_flag_48) { s->transition_flag_48=0; s->transition_time_4c=thug_elapsed_time()+thug_timer_offset; }
        }
    } else if (input->button_c0.pressed && input->button_120.pressed) {
        ThugSkaterTransferResult result;
        body=p->body;
        if (thug_skater_find_transfer(p,1,body->position,body->previous_position,body->velocity,&result,query))
            thug_skater_apply_transfer(p,&result,diagnostics,memory);
    }
    static const uint32_t events[3]={1,5,0};
    thug_collision_event_from_probe(p->collision_events,events,&p->saved_probe,diagnostics,memory);
}
