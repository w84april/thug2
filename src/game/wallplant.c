#include "skater.h"
#include "../core/matrix.h"
#include "ui.h"
#include "moving_contact.h"
#include "wall_marks.h"
#include "collision_events.h"
#include "objectives.h"
#include "../script/delivery.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterPhysics,wall_mark)==0x1538,"Wall-mark component offset");
const uint32_t thug_vert_wallplant_events[3]={2,4,0}; /* 0064bb8c */
/* 0x00503710. Vert_Wallplant (event 3722e9bf). Input consumption precedes the remaining gates. Signed script
 * integers remain exact through FILD comparisons; unordered height, velocity
 * and normal tests take the original fall-through paths. Event callbacks can
 * replace the body, state or component pointers, which are reread afterward. */
uint8_t thug_skater_try_vert_wallplant(ThugSkaterPhysics *p,ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    if(p->parameter_mode_active)return 0;
    if(!thug_skater_named_button(p->name_context,0x7323e97c)) {
        uint32_t window=thug_truncate_double_low_word(R24(thug_script_get_global_number(0x5d241b00,1)*1000));
        if(!thug_skater_consume_recent_input(p->name_context,0x7323e97c,window,UINT32_MAX))return 0;
    }
    ThugSkaterState *state=p->state;
    if(!state->ground_transition_flag||!state->state_flag_d8)return 0;
    if(p->name_context->spin_angle!=0||p->ground_flag_4e8)return 0;
    ThugSkaterBody *body=p->body;
    float vector[4],height=(float)thug_skater_get_parameter(0xe4d79235,1,body);
    thug_vector_copy(p->surface_segment,thug_vector_scaled_copy(vector,body->orientation+4,height));
    thug_vector_copy(p->surface_segment+4,thug_vector_scaled_copy(vector,p->body->orientation+4,-200));
    thug_vector_add(p->surface_segment,p->body->position);
    thug_vector_add(p->surface_segment+4,p->body->position);
    if(!thug_skater_query_surface(p,0x10,0,query))return 0;
    thug_vector_difference(vector,p->body->position,p->surface_probe.point);
    float distance=(float)thug_vector_length(vector);
    if((double)(int32_t)thug_script_get_global_integer(0xdc2c15ad,0)<distance)return 0;
    body=p->body;
    if((double)(int32_t)thug_script_get_global_integer(0x273c9920,0)>body->velocity[1])return 0;
    if(p->state->wallplant_height<60)return 0;
    if(!(p->surface_probe.result.surface_flags&8)&&__builtin_fabsf(p->surface_probe.normal[1])>0.10000000149011612f)return 0;
    if(!thug_wall_contact_mark(p->wall_mark,1,0,0,query,diagnostics,memory))return 0;
    thug_collision_event_from_probe(p->collision_events,thug_vert_wallplant_events,&p->surface_probe,diagnostics,memory);
    if(!p->wall_gate->wall_response_suppressed) {
        body=p->body;
        if(body->velocity[1]>=0) {
            int32_t boost=(int32_t)thug_script_get_global_integer(0x751dbcb4,0);
            body->velocity[1]=(float)R24((double)boost+body->velocity[1]);
        }
        thug_object_emit_event((ThugReferencedObject *)p->body,0x3722e9bf,NULL,diagnostics,memory);
        thug_skater_notify(p->name_context,p->surface_probe.result.checksum,diagnostics,memory);
        state=p->state;
        if(state->state_flag_c0){state->state_flag_c0=0;state->state_time_c4=thug_elapsed_time()+thug_timer_offset;}
        state=p->state;
        if(state->transfer_flag_b0){state->transfer_flag_b0=0;state->transfer_time_b4=thug_elapsed_time()+thug_timer_offset;}
        p->ground_flag_4e8=1;
    }
    return 1;
}

_Static_assert(offsetof(ThugSkaterPhysics,wallplant_saved_velocity)==0x14d0,"Saved wallplant velocity offset");
_Static_assert(offsetof(ThugSkaterState,wallplant_height)==0x11c,"Wallplant height offset");
_Static_assert(offsetof(ThugSkaterState,wallplant_time_a4)==0xa4,"Wallplant timestamp offset");
_Static_assert(offsetof(ThugSkaterWallGate,wallplant_blocked)==0x24,"Wallplant gate offset");
static uint32_t stamp(void){return thug_elapsed_time()+thug_timer_offset;}
static float unsigned_float(uint32_t x){double v=(int32_t)x;if((int32_t)x<0)v=R24(v+0x1p32);return (float)v;}
static double product(float x,float y){return R24((double)x*y);}
const char thug_late_wallplant_text[]="late wallplant\n"; /* 0064bd58 */
const uint32_t thug_wallplant_events[3]={6,3,0}; /* 0064bbec */
/* 00507500. Standard WallPlant: late/forced input, reflection, moving contact,
 * outgoing clearance, script events and state transition. Float spill points and
 * component reloads preserve the original x87 and callback-sensitive ordering. */
uint8_t thug_skater_try_wallplant(ThugSkaterPhysics *p,uint32_t late_arg,uint32_t check_arg,uint32_t forced_arg,
    ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m) {
 uint8_t late=(uint8_t)late_arg,check=(uint8_t)check_arg,forced=(uint8_t)forced_arg;
 if(p->parameter_mode_active){uint32_t value=0;if(!thug_ui_object_get_integer((void *)p->body,0x5310e7b5,&value))return 0;}
 if(p->rotation_input_used||p->wall_gate->wallplant_blocked)return 0;
 float flat_velocity[4],flat_normal[4],up[4],a[4],b[4],c[4];
 if(!forced) {
  if(p->body->orientation[5]<.10000000149011612f)return 0;
  uint32_t last=p->rebound_gate_time;float elapsed=unsigned_float(stamp()-last);
  if(thug_script_get_global_number(0x82135dd7,0)>elapsed)return 0;
  float recent=(float)(int32_t)thug_time_since(p->wall_transition_time);
  if(R24(thug_script_get_global_number(0x545840c4,1)*1000)>recent)return 0;
  ThugSkaterState *state=p->state;
  if(thug_script_get_global_number(0xd5349cc6,0)>state->wallplant_height)return 0;
  if(!check&&!(p->surface_probe.result.surface_flags&8)&&__builtin_fabsf(p->surface_probe.normal[1])>.10000000149011612f&&!late)return 0;
  const ThugScriptArray *tricks=thug_script_get_global_array(0x5d1f84a7,0);
  uint32_t i=0;for(;i<tricks->count;++i)if(thug_skater_match_trick_input(p->name_context,thug_script_array_structure(tricks,i),0,0,1))break;
  if(i==tricks->count) {
   if(!late){
    p->wall_transition_value=thug_script_get_global_integer(0x3b389187,0);
    thug_vector_copy(p->wallplant_saved_velocity,p->body->velocity);thug_vector_copy(p->wallplant_saved_position,p->body->position);
    ThugSkaterBody *body=p->body;float direction[4]={-body->velocity[0],0,-body->velocity[2],body->velocity[3]};
    thug_vector_normalize(direction);
    double x=product(direction[0],24);float y=(float)product(direction[1],24),z=(float)product(direction[2],24),w=(float)product(direction[3],24);
    float next_z=(float)R24((double)z+body->position[2]),next_w=(float)R24((double)w+body->position[3]);
    body->position[2]=next_z;body->position[3]=next_w;
    body->position[0]=(float)R24(x+body->position[0]);body->position[1]=(float)R24((double)y+body->position[1]);
   }
   return 0;
  }
  if(late) {
   if(d&&d->print)d->print(d->context,thug_late_wallplant_text);
   thug_vector_copy(p->body->velocity,p->wallplant_saved_velocity);thug_vector_copy(p->body->position,p->wallplant_saved_position);
   ThugSkaterBody *body=p->body;thug_vector_difference(a,body->position,body->previous_position);thug_vector_normalize(a);
   double h=thug_skater_get_parameter(0xd4205c9b,1,body);
   for(unsigned k=0;k<4;++k)up[k]=(float)R24(h*body->orientation[4+k]);
   body=p->body;for(unsigned k=0;k<4;++k)p->surface_segment[k]=(float)R24((double)up[k]+body->previous_position[k]);
   h=thug_skater_get_parameter(0x20102726,1,p->body);
   for(unsigned k=0;k<4;++k)a[k]=(float)R24(h*a[k]);
   body=p->body;
   for(unsigned k=0;k<4;++k){double start=R24((double)up[k]+body->position[k]);if(k!=3)start=(float)start;p->surface_segment[k+4]=(float)R24(start+a[k]);}
   if(!thug_skater_query_surface(p,0x10,0,query))return 0;
  }
 } else {
  ThugSkaterBody *body=p->body;float direction[4]={-body->orientation[8],body->orientation[9],-body->orientation[10],body->orientation[11]};
  thug_vector_normalize(direction);
  thug_vector_scaled_copy(up,body->orientation+4,(float)thug_skater_get_parameter(0xd4205c9b,1,body));
  thug_vector_copy(p->surface_segment,thug_vector_sum(a,p->body->position,up));
  body=p->body;thug_vector_scaled_copy(a,direction,36);
  thug_vector_sum(direction,body->position,up);thug_vector_copy(p->surface_segment+4,thug_vector_sum(b,direction,a));
  if(!thug_skater_query_surface(p,0x10,0,query))return 0;
 }
 if(check)return 1;
 ThugSkaterBody *body=p->body;double length=thug_vector_length(body->velocity);
 if(length<.009999999776482582f)return 0;
 thug_vector_divided(flat_velocity,body->velocity,(float)length);flat_velocity[1]=0;thug_vector_normalize(flat_velocity);
 float *normal=p->surface_probe.normal;
 thug_vector_copy(flat_normal,late?p->wallplant_saved_normal:normal);flat_normal[1]=0;thug_vector_normalize(flat_normal);
 if(!forced){
  double angle=R24(thug_script_get_global_number(0x8f79cc1c,0)*0.01745329238474369f);
  double dot=R24(R24(product(flat_velocity[0],flat_normal[0])+product(flat_velocity[2],flat_normal[2]))+product(flat_normal[1],flat_velocity[1]));
  if(-thug_platform_sin(angle)<dot)return 0;
 }
 if(p->body->velocity[1]>0&&p->input->button_1a0.pressed) {
  thug_vector_copy(a,p->surface_probe.point);thug_vector_copy(b,normal);
  float shift[4]={0,(float)product(p->body->velocity[1],.15000000596046448f),0,1};
  thug_vector_project_preserve_length(shift,b);thug_vector_add(a,shift);
  thug_vector_scaled_copy(c,b,6);float start[4],end[4];thug_vector_difference(end,a,c);
  thug_vector_scaled_copy(c,b,6);thug_vector_sum(start,a,c);
  ThugCollisionProbe probe;thug_collision_probe_from_points(&probe,start,end);uint8_t hit=thug_collision_probe_query(&probe,1,0,query);
  thug_collision_probe_release(&probe);if(!hit)return 0;
 }
 thug_wall_contact_mark(p->wall_mark,0,forced,late,query,d,m);p->body->velocity[1]=0;
 thug_collision_event_from_probe(p->collision_events,thug_wallplant_events,&p->surface_probe,d,m);
 if(p->wall_gate->wall_response_suppressed)return 1;
 body=p->body;thug_vector_scaled(a,(float)thug_vector_dot(flat_normal,body->velocity),flat_normal);
 if(!forced) {
  thug_vector_subtract(body->velocity,thug_vector_scaled(b,2,a));body=p->body;
  double horizontal=R24(__builtin_sqrt(R24(product(body->velocity[0],body->velocity[0])+product(body->velocity[2],body->velocity[2]))));
  float speed=(float)horizontal;
  if(horizontal>.00009999999747378752f) {
   body->velocity[1]=0;body=p->body;
   float after=(float)R24((double)speed-thug_script_get_global_number(0x09b2d4a3,0));
   float minimum=(float)thug_script_get_global_number(0x7cee396c,0);
   thug_vector_set_length(body->velocity,(float)thug_max_number(minimum,after));
  } else thug_vector_copy(body->velocity,thug_vector_scaled(b,(float)-thug_script_get_global_number(0x7cee396c,0),flat_velocity));
 } else thug_vector_copy(body->velocity,thug_vector_scaled_copy(b,flat_normal,(float)thug_script_get_global_number(0x5f768d84,0)));
 body=p->body;body->velocity[1]=(float)thug_script_get_global_number(0x074957fa,0);
 if(thug_collision_probe_has_moving_object(&p->surface_probe)) {
  if(!thug_skater_has_moving_contact(p->ground_gate,m)||p->ground_gate->contact->reference.object!=thug_collision_probe_moving_object(&p->surface_probe)) {
   thug_skater_moving_contact_release(p->ground_gate,m);
   thug_skater_moving_contact_set_owner(p->ground_gate,(void *)thug_collision_probe_moving_object(&p->surface_probe),m);
  }
 }
 if(!forced) {
  float *point=p->surface_probe.point;thug_vector_copy(p->surface_probe.segment,point);
  thug_vector_scaled(b,(float)thug_script_get_global_number(0x024be8f0,0),normal);
  thug_vector_copy(p->surface_probe.segment+4,thug_vector_sum(c,point,b));
  uint8_t hit=thug_collision_probe_query(&p->surface_probe,1,0,query);
  float *position=p->surface_probe.segment+4;
  if(hit){thug_vector_scaled(b,.10000000149011612f,normal);position=thug_vector_sum(c,point,b);}
  thug_vector_copy(p->body->position,position);
 }
 thug_vector_copy(p->body->orientation+8,p->body->velocity);p->body->orientation[9]=0;thug_vector_normalize(p->body->orientation+8);
 body=p->body;body->orientation[4]=body->orientation[6]=0;body->orientation[5]=body->orientation[7]=1;
 body=p->body;thug_vector_copy(body->orientation,thug_vector_cross(a,body->orientation+4,body->orientation+8));
 thug_matrix_copy(p->cached_orientation,p->body->orientation);p->rebound_gate_time=stamp();
 thug_object_emit_event((void *)p->body,0xcf74f6b7,0,d,m);thug_skater_notify(p->name_context,p->surface_probe.result.checksum,d,m);
 ThugSkaterState *state=p->state;
 if(state->state_flag_c0){state->state_flag_c0=0;state->state_time_c4=stamp();}
 state=p->state;if(state->transfer_flag_b0){state->transfer_flag_b0=0;state->transfer_time_b4=stamp();}
 state=p->state;if(state->wallplant_flag_a0!=1){state->wallplant_flag_a0=1;state->wallplant_time_a4=stamp();}
 thug_skater_change_state(p,5,d,m);p->wall_transition_value=0;p->wall_transition_time_3a0=stamp();return 1;
}

#undef R24

/* 00509050. Wallplant state (mode 5): wait for Physics_Wallplant_Duration,
 * then enter air and emit the surface event. Live component pointers are reloaded
 * after callbacks; unexpired wallplants follow moving contacts. */
void thug_skater_update_wallplant_state(ThugSkaterPhysics *p,ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    uint32_t started=p->state_change_time;
    p->ground_flag_2e4=0;
    float elapsed=(float)(thug_elapsed_time()+thug_timer_offset-started);
    double duration=thug_script_get_global_number(0xa06e446b,0);
    if(duration<elapsed) {
        thug_skater_change_state(p,1,diagnostics,memory);
        for(unsigned i=0;i<4;++i)p->surface_segment[i]=(float)thug_platform_round_x87_single((double)p->body->orientation[8+i]*12);
        for(unsigned i=0;i<4;++i)p->surface_segment[4+i]=(float)thug_platform_round_x87_single((double)p->body->orientation[8+i]*-36);
        thug_vector_add(p->surface_segment,p->body->position);
        thug_vector_add(p->surface_segment+4,p->body->position);
        if(thug_skater_query_surface(p,0x10,0,query)) {
            const uint32_t events[3]={6,4,0};
            thug_collision_event_from_probe(p->collision_events,events,&p->surface_probe,diagnostics,memory);
        }
        return;
    }
    ThugSkaterGroundGate *gate=p->ground_gate;
    ThugSkaterBody *body=p->body;
    p->ground_value_22c=0;p->ground_value_244=0;
    if(!gate->contact)return;
    if(!gate->contact->reference.object||!thug_moving_contact_update(gate->contact,body->position)) {
        thug_skater_moving_contact_release(gate,memory);return;
    }
    thug_vector_add(p->body->position,p->ground_gate->contact->displacement);
    if(p->ground_gate->contact->orientation_changed) {
        thug_matrix_multiply(p->body->orientation,p->body->orientation,p->ground_gate->contact->rotation);
        thug_matrix_multiply(p->cached_orientation,p->cached_orientation,p->ground_gate->contact->rotation);
    }
}
