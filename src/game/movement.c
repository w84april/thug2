/* 00510830: full movement dispatcher. */
#include "skater.h"
#include "rail.h"
#include "attachment.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../script/delivery.h"
static void mark(ThugSkaterState *state,unsigned offset,uint8_t value) {
    uint8_t *at=(uint8_t *)state+offset;
    if(*at!=value) {*at=value;uint32_t now=thug_elapsed_time()+thug_timer_offset;__builtin_memcpy(at+4,&now,4);}
}
void thug_skater_update_movement(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    p->time_step=(float)thug_frame_duration();ThugSkaterState *state=p->state;
    p->unknown_254=0;p->unknown_256_to_257[0]=state->mode==3;
    p->previous_skip_ground_probe=state->skip_ground_probe;
    if(!state->drag_coefficient_selector&&p->input->button_1c0.pressed)mark(state,0x20,1);
    thug_skater_update_speed_limits(p);mark(p->state,0x98,0);mark(p->state,0xa0,0);
    thug_skater_build_collision_cache(p);thug_skater_update_rotation(p,d,m);
    switch(p->state->mode) {
    case 0:
        thug_vector_copy((float *)p->unknown_338_to_347,p->body->position);
        thug_skater_update_grounded(p,q,d,m);thug_skater_find_attachment(p,d,m);break;
    case 1:
        thug_skater_update_airborne(p,q,d,m);if(!p->state->mode)p->unknown_254=1;break;
    case 2:thug_skater_update_wallride(p,q,d,m);break;
    case 3:thug_skater_update_lip(p,d,m);break;
    case 4:thug_skater_update_rail(p,q,d,m);break;
    case 5:thug_skater_update_wallplant_state(p,q,d,m);break;
    }
    thug_skater_update_transfer_speed(p,d);
    /* 510994..510c61 repeats the complete0050dae0 acquisition with force0.
     * Share the recovered implementation, preserving every gate/callee. */
    thug_skater_acquire_rail(p,0,q,d,m);
    thug_skater_update_revert_count(p,d);thug_skater_update_focus_input(p,d,m);
    thug_skater_update_projectile(p,d,m);thug_skater_update_special_timer(p,d,m);
    state=p->state;uint8_t vert=state->mode==1&&state->ground_transition_flag&&!state->skip_ground_probe;
    if(p->vert_air_event_active!=vert) {
        p->vert_air_event_active=!p->vert_air_event_active;
        thug_object_broadcast_event((void *)p->body,p->vert_air_event_active?0xf225fe69:0x5e27200a,0,0,d,m);
    }
    if(p->state->mode!=1)p->wall_transition_value=0;
    thug_collision_default_cache=0;
}

#undef R
