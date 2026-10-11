#include "skater.h"
#include "stats.h"
#include "animation.h"
#include "wall_marks.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../core/number.h"
#include "../script/schedule.h"
#include "../script/values.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterPhysics,revert_count)==0x318,"Revert count");
_Static_assert(offsetof(ThugSkaterPhysics,revert_recovery_time)==0x31c,"Revert recovery time");
_Static_assert(offsetof(ThugSkaterPhysics,speed_soft_limit)==0x354,"Soft speed limit");
_Static_assert(offsetof(ThugSkaterPhysics,speed_hard_limit)==0x358,"Hard speed limit");
_Static_assert(offsetof(ThugSkaterPhysics,collision_cache)==0x4f4,"Embedded collision cache");
_Static_assert(offsetof(ThugSkaterPhysics,focus_input_latched)==0x14c1,"Focus input latch");
_Static_assert(offsetof(ThugSkaterInput,button_e0)==0xe0,"Focus input button");
_Static_assert(offsetof(ThugSkaterPhysics,rotation_step)==0x2e8,"Rotation decrement");
_Static_assert(offsetof(ThugSkaterPhysics,projectile_count)==0x2f8,"Projectile count");
_Static_assert(offsetof(ThugSkaterPhysics,special_timer_active)==0x301,"Special timer gate");
_Static_assert(offsetof(ThugSkaterPhysics,projectile_input_value)==0x308,"Projectile input value");
_Static_assert(offsetof(ThugSkaterPhysics,projectile_cooldown)==0x14c4,"Projectile cooldown");
_Static_assert(offsetof(ThugSkaterPhysics,projectile_blocked)==0x14c8,"Projectile gate");
_Static_assert(offsetof(ThugSkaterState,stat_modifier_time)==0x2c,"Flip timestamp");
_Static_assert(offsetof(ThugSkaterFlipComponent,animation)==0x1c,"Flip animation component");
_Static_assert(offsetof(ThugSkaterPhysics,previous_skip_ground_probe)==0x255,"Previous transfer flag");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_speed_multiplier)==0x3ac,"Transfer speed multiplier");

int32_t thug_transfer_speed_diagnostic_counter; /* 007ccdcc */
const char thug_transfer_speed_format[]="Post-Transfer Speed Limit Overrides:  current / standard = %.2f\n"; /* 0064bc88 */
static void advance_speed_counter(void) {
    int32_t incremented=(int32_t)((uint32_t)thug_transfer_speed_diagnostic_counter+1);
    thug_transfer_speed_diagnostic_counter=incremented%10;
}
/* 0x004ff200. Preserve PC24 arithmetic before float stores/comparisons and the
 * two distinct minima. Diagnostics may change the counter and live limits. */
void thug_skater_update_transfer_speed(ThugSkaterPhysics *p,const ThugDiagnostics *diagnostics) {
    ThugSkaterBody *body=p->body;
    if(p->previous_skip_ground_probe&&!p->state->skip_ground_probe&&!p->state->resistance_requested) {
        float soft=(float)thug_skater_stat_parameter(body,0x2eacddb3);
        double magnitude=thug_vector_length(p->body->velocity);
        float stored_magnitude=(float)magnitude;
        if(magnitude<R((double)soft*1.25))return;
        double maximum=thug_skater_get_parameter(0xc6b38be0,1,body);
        double ratio=R((double)stored_magnitude/soft);
        float stored_ratio=(float)ratio;
        p->transfer_speed_multiplier=(float)(ratio<maximum?stored_ratio:maximum);
        uint32_t unlimited=0x60ad78ec;
        __builtin_memcpy(&p->speed_soft_limit,&unlimited,4);
        __builtin_memcpy(&p->speed_hard_limit,&unlimited,4);
    } else {
        uint32_t raw;__builtin_memcpy(&raw,&p->transfer_speed_multiplier,4);
        if(raw==0x3f800000)return;
    }
    p->drag_override_active=-1;
    double decrement=thug_platform_multiply_x87_single(thug_skater_get_parameter(0xf9b006aa,1,body),p->time_step);
    double remaining=R((double)p->transfer_speed_multiplier-decrement);
    p->transfer_speed_multiplier=(float)remaining;
    if(!(remaining<1)) {
        double soft=thug_skater_stat_parameter(p->body,0x2eacddb3);
        float standard=(float)soft;
        float target=(float)R(soft*p->transfer_speed_multiplier);
        body=p->body;
        double selected;
        if(p->state->mode==1)selected=target<p->speed_soft_limit?target:p->speed_soft_limit;
        else {
            float velocity_limit=(float)R(thug_vector_length(body->velocity)*(double)1.100000023841858f);
            selected=thug_min_three(target,velocity_limit,p->speed_soft_limit);
        }
        if(!(selected<standard)) {
            p->speed_soft_limit=(float)selected;
            float inverse=(float)R(1/(double)standard);
            double limit=thug_skater_stat_parameter(body,0x2eacddb3);
            limit=R(limit*inverse);
            p->speed_hard_limit=(float)R(limit*p->speed_soft_limit);
            advance_speed_counter();
            while(!thug_transfer_speed_diagnostic_counter) {
                diagnostics->print(diagnostics->context,thug_transfer_speed_format,R((double)inverse*p->speed_soft_limit));
                advance_speed_counter();
            }
            return;
        }
    }
    p->transfer_speed_multiplier=1;
    uint32_t active;__builtin_memcpy(&active,&p->drag_override_active,4);
    if(active!=0xc0000000)p->drag_override_active=0;
}

/* 0x00500670. The frame's cache extends farther below than above the skater.
 * Publish it only after the original static/moving candidate build completes. */
void thug_skater_build_collision_cache(ThugSkaterPhysics *p) {
    const float *position=p->body->position;
    ThugBounds bounds;
    float upper[4],lower[4];
    upper[0]=(float)R((double)position[0]+180);
    upper[1]=(float)R((double)position[1]+96);
    upper[2]=(float)R((double)position[2]+180);
    upper[3]=position[3];
    lower[0]=(float)R((double)position[0]-180);
    lower[1]=(float)R((double)position[1]-204);
    lower[2]=(float)R((double)position[2]-180);
    lower[3]=position[3];
    thug_collision_segment_copy(bounds.min,lower,upper);
    thug_collision_cache_build(&p->collision_cache,&bounds);
    thug_collision_default_cache=&p->collision_cache;
}

const char thug_revert_recovery_format[]="M:%s:%i: %s\n"; /* 006466b0 */
const char thug_revert_recovery_file[]="mponents\\SkaterCorePhysicsComponent.cpp"; /* 0064bce0: original interior string pointer */
const char thug_revert_recovery_message[]="You earned a free revert!!!!"; /* 0064bd08 */
/* 0x00500710. Unsigned strict expiry, low-word CRT conversion, and a reload
 * after diagnostics preserve wrapping counts and callback-side changes. */
void thug_skater_update_revert_count(ThugSkaterPhysics *p,const ThugDiagnostics *d) {
    if(!p->revert_count)return;
    uint32_t previous=p->revert_recovery_time;
    double seconds=thug_script_get_global_number(0xf4813ad5,0);
    uint32_t delay=thug_truncate_double_low_word(thug_platform_multiply_x87_single(seconds,1000));
    if(thug_elapsed_time()+thug_timer_offset-previous<=delay)return;
    --p->revert_count;
    d->print(d->context,thug_revert_recovery_format,thug_revert_recovery_file,0x293f,thug_revert_recovery_message);
    if(p->revert_count)p->revert_recovery_time=thug_elapsed_time()+thug_timer_offset;
}

/* 0x005007a0. One synchronous toggle per hold. The signed duration comparison
 * intentionally differs from the unsigned revert timer above. */
void thug_skater_update_focus_input(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugInputButton *button=&p->input->button_e0;
    if(p->focus_input_latched) {
        if(!button->pressed)p->focus_input_latched=0;
        return;
    }
    if(!button->pressed)return;
    int32_t threshold=(int32_t)thug_script_get_global_integer(0xd7e8d8de,1);
    if((int32_t)thug_input_button_elapsed(button)<=threshold)return;
    p->focus_input_latched=1;
    thug_script_run_sync(0xd7196d01,0,0,0,d,m);
}

/* 0x00501850. Temporarily remove vertical speed, apply hard/soft horizontal
 * limits, restore its raw bits, then expire the airborne-friction override.
 * Keep the unspilled timer differences for comparisons after their float stores. */
void thug_skater_update_speed_limits(ThugSkaterPhysics *p) {
    uint32_t vertical;__builtin_memcpy(&vertical,p->body->velocity+1,4);
    p->body->velocity[1]=0;
    float magnitude=(float)thug_vector_length(p->body->velocity);
    float hard=(float)thug_skater_stat_parameter(p->body,0xcc5f87aa);
    float soft=(float)thug_skater_stat_parameter(p->body,0x2eacddb3);
    if(p->drag_override_active!=0) {
        uint32_t active;__builtin_memcpy(&active,&p->drag_override_active,4);
        if(active!=0xbf800000 && active!=0xc0000000) {
            double left=R((double)p->drag_override_active-p->time_step);
            p->drag_override_active=(float)left;
            if(left<0)p->drag_override_active=0;
        }
        hard=p->speed_hard_limit;soft=p->speed_soft_limit;
    }
    if(magnitude>hard) {
        magnitude=hard;
        thug_vector_set_length(p->body->velocity,hard);
    }
    ThugSkaterBody *parameter_body=p->body;
    if(magnitude>soft) {
        float drag=(float)thug_script_get_global_number(0x850eb87a,1);
        thug_skater_apply_quadratic_drag(p,drag);
    }
    __builtin_memcpy(p->body->velocity+1,&vertical,4);
    if(p->airborne_friction_gate!=0) {
        double left=R((double)p->airborne_friction_gate-p->time_step);
        p->airborne_friction_gate=(float)left;
        if(left<=0) {
            p->airborne_friction_gate=0;
            p->friction=(float)thug_skater_get_parameter(0x78f80ec4,1,parameter_body);
        }
    }
}
/* 0x004fc3c0. The configured control is a raw symbol value, not an array. */
uint8_t thug_skater_check_projectile_input(ThugSkaterPhysics *p) {
    uint32_t key=thug_script_get_global_value_text("projectile_control",1);
    if(!thug_skater_match_release_input(p->name_context,key,0,1))return 0;
    p->projectile_input_value=UINT32_MAX;return 1;
}
/* 0x004fc420. */
uint32_t thug_skater_is_walking(const ThugSkaterWallGate *gate) {
    return !gate->movement_mode->alternate&&gate->movement_mode->mode==1;
}
/* 0x00500820. Early gates preserve the countdown. The script observes the new
 * 30-frame cooldown and owns any subsequent inventory/state changes. */
void thug_skater_update_projectile(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    if(p->projectile_blocked||!p->projectile_enabled||p->state->resistance_requested)return;
    ThugWallContactMark *mark=p->wall_mark;
    if(mark->armed||mark->inhibit||mark->cooldown!=0)return;
    if(p->projectile_cooldown) { --p->projectile_cooldown;return; }
    if(p->projectile_count<=0||!thug_skater_check_projectile_input(p)||p->projectile_cooldown)return;
    p->projectile_cooldown=30;
    uint32_t script=thug_skater_is_walking(p->wall_gate)?0x0ce5b783:0x3f356c63;
    thug_script_run_sync(script,0,(ThugReferencedObject *)p->body,0,d,m);
}
/* 0x00500900. Preserve the unspilled decrement for both comparisons and retain
 * the captured rotation component even if the flip path changes live links. */
void thug_skater_update_rotation(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    if(!p->rotation_input_used)return;
    ThugRotationComponent *rotation=(void *)thug_object_find_component(p->body,0x286a8d26);
    double remaining=R((double)p->rotation_duration-p->rotation_step);
    p->rotation_duration=(float)remaining;
    if(p->state->mode!=1) {
        thug_rotation_clear(rotation,d,m);
        p->rotation_input_used=0;p->rotation_requested=0;
        p->rotation_duration=0;p->ground_flag_2e4=0;return;
    }
    if(remaining<=20)p->rotation_requested=0;
    if(!(remaining<=0))return;
    p->rotation_input_used=0;p->rotation_duration=0;
    if(p->rotation_half_turn) {
        ThugSkaterFlipComponent *flip=(void *)thug_object_find_component(p->body,0x488af07a);
        thug_skater_toggle_flip(flip,d,m);
    }
    thug_rotation_clear(rotation,d,m);
}
/* 0x00500bc0. Expiry is dispatched on the frame after a positive timer crosses
 * zero. The script receives a real owned TimeLimit structure. */
void thug_skater_update_special_timer(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    if(!p->special_timer_active)return;
    ThugStatModifier *modifier=thug_skater_stat_modifier(p->body);
    if(!modifier)return;
    if(modifier->remaining>0) {
        modifier->remaining=(float)R((double)modifier->remaining-p->time_step);return;
    }
    ThugScriptStructure *parameters=thug_script_structure_allocate(8,m);
    if(parameters)thug_script_structure_initialize(parameters);
    thug_script_set_checksum(parameters,0x70f16ea9,1,m);
    thug_script_run_sync(0x266b570c,parameters,(ThugReferencedObject *)p->body,0,d,m);
    if(parameters) { thug_script_structure_destroy(parameters,m);thug_script_structure_free(parameters,m); }
}
#undef R
