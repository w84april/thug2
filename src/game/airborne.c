#include "skater.h"
#include "stats.h"
#include "objectives.h"
#include "collision_events.h"
#include "moving_contact.h"
#include "../audio/events.h"
#include "../script/delivery.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
#include <stddef.h>
_Static_assert(offsetof(ThugSkaterPhysics, airborne_flag_2ec)==0x2ec,"Airborne frame flag");
_Static_assert(offsetof(ThugSkaterPhysics, airborne_friction_gate)==0x320,"Air friction gate");
_Static_assert(offsetof(ThugSkaterPhysics, landed_from_transfer)==0x372,"Transfer landing flag");
_Static_assert(offsetof(ThugSkaterPhysics, landing_flag_373)==0x373,"Retained landing flag");
_Static_assert(offsetof(ThugSkaterPhysics, landing_flag_374)==0x374,"Frame landing flag");
_Static_assert(offsetof(ThugSkaterPhysics, transfer_gate_time)==0x4ec,"Transfer gate time");
_Static_assert(offsetof(ThugSkaterPhysics, orientation_gate)==0x151c,"Orientation gate component");
_Static_assert(offsetof(ThugSkaterOrientationGate, blocked_50)==0x50,"Second orientation gate");
_Static_assert(offsetof(ThugSkaterNameContext, notification_flag)==0x13b0,"Gameplay notification flag");
static void timed(uint8_t *flag,uint32_t *timestamp,uint8_t value){
 if(*flag!=value){*flag=value;*timestamp=thug_elapsed_time()+thug_timer_offset;}
}
static uint8_t orientation_locked(const ThugSkaterPhysics *p){
 return p->orientation_gate->blocked_28||p->orientation_gate->blocked_50;
}
static void shifted_previous(float out[4],ThugSkaterBody *body,const float displacement[4]){for(unsigned k=0;k<4;k++)out[k]=(float)R((double)displacement[k]+body->previous_position[k]);}
const uint32_t thug_air_landing_events[3]={8,3,0}; /* 0064bb98 */
/* 0x0050ca00. Complete airborne frame: input, transport, transition following,
 * wall/floor/ceiling contacts, landing and transfers. Keep the captured input
 * and pre-query parameter body while reloading mutable components after callbacks.
 * The position and velocity spill points include the original W and zero products.
 * A failed moving update retains its defensive release branch even though a
 * nonnull owner cannot disappear inside the current single-threaded helper. */
void thug_skater_update_airborne(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 ThugSkaterInput *input=p->input;
 float gravity=(float)thug_skater_gravity(p);
 timed(&p->state->surface_flag_8,&p->state->surface_flag_time,0);
 ThugSkaterState *s=p->state;
 if(s->ground_transition_flag||s->skip_ground_probe||s->transfer_flag_a8||s->resistance_requested)timed(&s->transfer_flag_b0,&s->transfer_time_b4,1);
 p->airborne_flag_2ec=0;
 thug_skater_pitch_input(p);thug_skater_check_rotation_input(p,d,m);thug_skater_spin_input(p,d,m);thug_skater_transfer_orientation(p);
 if(p->state->ground_contact_flag||(input->button_c0.pressed&&input->button_120.pressed))thug_skater_ground_update(p,q);
 if(!p->state->ground_transition_flag&&!p->state->skip_ground_probe&&!orientation_locked(p))thug_skater_upright_orientation(p);
 if(p->airborne_friction_gate!=0)thug_skater_apply_friction(p);
 float velocity[4];thug_vector_copy(velocity,p->body->velocity);
 if((int32_t)p->wall_transition_value>0){
  --p->wall_transition_value;
  if(thug_skater_try_wallplant(p,1,0,0,q,d,m))p->wall_transition_value=0;
  else if(!p->wall_transition_value)thug_vector_project_preserve_length(p->body->orientation+8,p->wallplant_saved_normal);
 }
 s=p->state;
 if(s->skip_ground_probe){
  if(!(velocity[1]<0)||!(p->body->position[1]<p->transfer_height))thug_vector_add(velocity,s->transfer_velocity);
  else thug_vector_set_length(s->transfer_velocity,.10000000149011612f);
 }
 float displacement[4]={0,0,0,1};
 ThugSkaterGroundGate *gate=p->ground_gate;ThugMovingContact *contact=gate->contact;
 if(contact){
  if(!contact->reference.object||!thug_moving_contact_update(contact,p->body->position))thug_skater_moving_contact_release(gate,m);
  else if(!p->state->skip_ground_probe||p->transfer_moving)thug_vector_copy(displacement,p->ground_gate->contact->displacement);
 }
 ThugSkaterBody *body=p->body;
 double half_dt=R(R((double)p->time_step*p->time_step)*.5),zero=R(0*half_dt);
 float ax=(float)zero,ay=(float)R(half_dt*gravity),aw=(float)half_dt;
 double vx=R((double)p->time_step*velocity[0]);
 float vy=(float)R((double)p->time_step*velocity[1]),vz=(float)R((double)p->time_step*velocity[2]),vw=(float)R((double)p->time_step*velocity[3]);
 float dx=(float)R(vx+ax),dy=(float)R((double)vy+ay);
 double dz=R(zero+vz),dw=R((double)vw+aw);
 body->position[0]=(float)R((double)dx+body->position[0]);body->position[1]=(float)R((double)dy+body->position[1]);
 body->position[2]=(float)R(dz+body->position[2]);body->position[3]=(float)R(dw+body->position[3]);
 thug_vector_add(p->body->position,displacement);
 body=p->body;zero=R(0*(double)p->time_step);ax=(float)zero;ay=(float)R((double)p->time_step*gravity);aw=p->time_step;
 body->velocity[0]=(float)R((double)ax+body->velocity[0]);body->velocity[1]=(float)R((double)ay+body->velocity[1]);
 body->velocity[2]=(float)R(zero+body->velocity[2]);body->velocity[3]=(float)R((double)aw+body->velocity[3]);
 s=p->state;ThugSkaterBody *parameter_body=p->body;
 if(s->transition_flag_48){
  if(s->transition_flag_38&&s->ground_transition_flag){
   body=p->body;for(unsigned k=0;k<4;k++)p->surface_segment[k]=(float)R((double)body->orientation[4+k]+body->position[k]);
   body=p->body;double x=R((double)body->orientation[4]*-23);
   float y=(float)R((double)body->orientation[5]*-23),z=(float)R((double)body->orientation[6]*-23),w=(float)R((double)body->orientation[7]*-23);
   p->surface_segment[4]=(float)R(x+body->position[0]);p->surface_segment[5]=(float)R((double)y+body->position[1]);
   p->surface_segment[6]=(float)R((double)z+body->position[2]);p->surface_segment[7]=(float)R((double)w+body->position[3]);
   if(!thug_skater_query_surface(p,0x10,0,q)){
    thug_skater_leave_transition(p,0,q,d,m);
    int32_t delay=(int32_t)thug_script_get_global_integer(0x6bb5b751,1);
    if((int32_t)thug_input_button_elapsed_8(&input->button_20)>delay&&(int32_t)thug_input_button_elapsed(&input->button_20)>delay)timed(&p->state->transition_flag_48,&p->state->transition_time_4c,0);
   }
  }
  uint32_t timestamp=p->state->transition_time_4c,age=thug_elapsed_time()+thug_timer_offset-timestamp;
  if((int32_t)age>(int32_t)thug_script_get_global_integer(0x26495947,1))timed(&p->state->transition_flag_48,&p->state->transition_time_4c,0);
 }else if(s->ground_transition_flag&&((input->button_c0.pressed&&input->button_120.pressed)||p->ground_transition_flag)&&!s->skip_ground_probe&&parameter_body->velocity[1]>0)thug_skater_leave_transition(p,0,q,d,m);
 gate=p->ground_gate;contact=gate->contact;
 if(contact&&!contact->reference.object){thug_skater_moving_contact_release(gate,m);contact=0;}
 if(!contact&&p->state->transition_flag_38&&p->state->ground_transition_flag){
  p->surface_segment[0]=p->body->position[0];p->surface_segment[1]=p->transition_previous_position[1];p->surface_segment[2]=p->body->position[2];
  thug_vector_copy(p->surface_segment+4,p->surface_segment);
  for(unsigned endpoint=0;endpoint<2;endpoint++){
   double x=R((double)p->transition_orientation[0]*30),y=R((double)p->transition_orientation[1]*30);
   float z=(float)R((double)p->transition_orientation[2]*30),w=(float)R((double)p->transition_orientation[3]*30);
   float *a=p->surface_segment+endpoint*4;
   a[0]=(float)(endpoint?R((double)a[0]-x):R(x+a[0]));a[1]=(float)(endpoint?R((double)a[1]-y):R(y+a[1]));
   a[2]=(float)(endpoint?R((double)a[2]-z):R((double)z+a[2]));a[3]=(float)(endpoint?R((double)a[3]-w):R((double)w+a[3]));
  }
  uint8_t hit=0;
  if(p->transition_height>.5){
   p->surface_segment[1]=(float)R((double)p->transition_height+p->surface_segment[1]);p->surface_segment[5]=(float)R((double)p->surface_segment[5]+p->transition_height);
   hit=thug_skater_query_surface(p,0,8,q);
   if(!hit){p->surface_segment[1]=(float)R((double)p->surface_segment[1]-p->transition_height);p->surface_segment[5]=(float)R((double)p->surface_segment[5]-p->transition_height);p->transition_height=(float)R((double)p->transition_height*.5);}
  }
  if(!hit){hit=thug_skater_query_surface(p,0,8,q);if(!hit)for(unsigned i=0;i<10;i++){
   p->surface_segment[1]=(float)R((double)p->surface_segment[1]-3);p->surface_segment[5]=(float)R((double)p->surface_segment[5]-3);
   if((hit=thug_skater_query_surface(p,0,8,q))){p->transition_previous_position[1]=p->surface_probe.point[1];break;}
  }}
  double alignment=0;
  if(hit)alignment=R(__builtin_sqrt(__builtin_fabs(R(R((double)p->transition_orientation[2]*p->surface_probe.normal[2])+R((double)p->transition_orientation[0]*p->surface_probe.normal[0])))));
  if(hit&&alignment>.019999999552965164f){
   float point[4];thug_vector_copy(point,p->surface_probe.point);
   if(point[1]<p->transition_previous_position[1])point[1]=p->transition_previous_position[1];
   thug_vector_copy(p->transition_previous_position,point);p->body->position[0]=point[0];p->body->position[2]=point[2];
   thug_vector_copy(p->transition_orientation,p->surface_probe.normal);
   double push=thug_script_get_global_number(0x78384871,1);body=p->body;
   double x=R(push*p->transition_orientation[0]);float y=(float)R(push*p->transition_orientation[1]),z=(float)R(push*p->transition_orientation[2]),w=(float)R(push*p->transition_orientation[3]);
   body->position[0]=(float)R(x+body->position[0]);body->position[1]=(float)R((double)y+body->position[1]);body->position[2]=(float)R((double)z+body->position[2]);body->position[3]=(float)R((double)w+body->position[3]);
   float normal[4];thug_vector_copy(normal,p->transition_orientation);normal[1]=0;thug_vector_normalize(normal);
   thug_skater_set_up_vector(p,normal[0],normal[1],normal[2],normal[3],q);thug_vector_project_preserve_length(p->body->velocity,normal);
  }else timed(&p->state->transition_flag_38,&p->state->transition_time_3c,0);
 }
 if(p->state->ground_transition_flag&&!p->state->skip_ground_probe&&!p->rotation_input_used&&!orientation_locked(p))thug_skater_blend_orientation(p);
 else thug_matrix_copy(p->cached_orientation,p->body->orientation);
 float previous[4];shifted_previous(previous,p->body,displacement);
 uint8_t wall=thug_skater_resolve_air_wall(p,previous,q,d,m);
 if(p->state->mode==2||p->state->mode==5)return;
 shifted_previous(p->surface_segment,p->body,displacement);thug_vector_copy(p->surface_segment+4,p->body->position);
 if(!wall&&thug_skater_query_surface(p,0x10,0,q)){
  uint8_t steep=p->surface_probe.normal[1]<.10000000149011612f;
  shifted_previous(previous,p->body,displacement);
  if(!thug_skater_try_raised_path(p,previous,q)||((!(p->body->velocity[1]>10))&&!steep)||thug_skater_moving_contact_age(p->ground_gate)<=500){
   float normal[4];thug_vector_copy(normal,p->surface_probe.normal);
   thug_vector_copy(p->body->position,p->surface_probe.point);thug_vector_add(p->body->position,normal);
   if(p->surface_skatable){
    thug_skater_change_state(p,0,d,m);thug_skater_adjust_moving_contact(p,m);s=p->state;
    if(s->ground_transition_flag||s->skip_ground_probe){p->landing_flag_373=1;p->landing_flag_374=1;}else p->landing_flag_374=0;
    p->landed_from_transfer=s->skip_ground_probe;thug_skater_set_material(p,p->surface_probe.result.surface_metadata,d,m);
    if(!p->parameter_mode_active){uint32_t material=p->state->material;body=p->body;float speed=(float)thug_vector_length(body->velocity);float intensity=(float)R((double)speed/thug_skater_stat_parameter(body,0xcc5f87aa));thug_sound_component_land(p->sound,intensity,material,d,m);}
    if(!p->name_context->notification_flag)thug_skater_set_notification_flag(p->name_context,0,d,m);
    thug_skater_save_surface(p,&p->surface_probe);thug_collision_event_from_probe(p->collision_events,thug_air_landing_events,&p->saved_probe,d,m);
    if(!p->wall_gate->wall_response_suppressed){
     if(!p->landing_flag_374&&!p->landing_flag_373&&p->body->velocity[0]==0&&p->body->velocity[2]==0&&input->button_40.pressed)p->body->velocity[1]=0;
     else{
      if(!p->state->skip_ground_probe)thug_vector_project_plane(p->body->velocity,p->surface_probe.normal);
      else{
       float saved[4],aligned[4];thug_vector_copy(saved,p->body->velocity);thug_vector_align_magnitude(p->body->velocity,p->transfer_direction);thug_vector_project_preserve_length(p->body->velocity,p->surface_probe.normal);
       body=p->body;thug_vector_copy(aligned,body->velocity);thug_skater_align_velocity(p,aligned);
       if(aligned[1]>0){thug_vector_copy(body->velocity,saved);thug_vector_project_plane(p->body->velocity,p->surface_probe.normal);}
       body=p->body;float minimum=(float)thug_script_get_global_number(0x59484878,0);
       if(R((double)minimum*minimum)>thug_vector_length_squared(body->velocity)){body=p->body;float value=(float)thug_script_get_global_number(0x59484878,0);thug_vector_set_length(body->velocity,value);}
      }
      thug_vector_clear_below(p->body->velocity,10);
     }
     timed(&p->state->ground_transition_flag,&p->state->ground_transition_time,0);p->ground_transition_flag=0;
     thug_vector_copy(p->orientation_source,p->surface_probe.normal);thug_vector_copy(p->orientation_target,p->orientation_source);thug_vector_copy(p->orientation_previous,p->orientation_source);
     thug_skater_nearby_obstacle(p,q);thug_vector_copy(p->body->orientation+4,p->orientation_source);thug_matrix_orthogonalize(p->body->orientation,1);thug_matrix_copy(p->cached_orientation,p->body->orientation);
    }
    thug_object_emit_event((ThugReferencedObject *)p->body,0x532b16ef,0,d,m);return;
   }
   thug_vector_project_preserve_length(p->body->velocity,normal);thug_vector_project_preserve_length(p->body->orientation+8,normal);thug_matrix_orthogonalize(p->body->orientation,2);thug_matrix_copy(p->cached_orientation,p->body->orientation);
   body=p->body;float push=(float)thug_skater_get_parameter(0x23410c14,1,parameter_body),delta[4];thug_vector_scaled_copy(delta,normal,push);thug_vector_add(body->position,delta);timed(&p->state->transfer_flag_b0,&p->state->transfer_time_b4,1);
  }
 }else if(!p->state->ground_transition_flag)thug_skater_correct_sides(p,q,d,m);
 if(thug_skater_resolve_overhead(p,q))timed(&p->state->transfer_flag_b0,&p->state->transfer_time_b4,1);
 thug_skater_handle_input_release(p,d,m);thug_skater_try_vert_wallplant(p,q,d,m);
 if(p->state->transfer_flag_b0||!input->button_c0.pressed||!input->button_120.pressed)return;
 uint8_t force=p->transfer_gate_time<p->state_enter_time&&thug_time_since(p->state_enter_time)<250;
 ThugSkaterTransferResult result;body=p->body;
 if(thug_skater_find_transfer(p,force,body->position,body->previous_position,body->velocity,&result,q))thug_skater_apply_transfer(p,&result,d,m);
}
#undef R
