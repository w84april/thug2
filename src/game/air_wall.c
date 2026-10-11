#include "skater.h"
#include "stats.h"
#include "collision_events.h"
#include "../audio/events.h"
#include "../script/schedule.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static double mul(float a,float b){return R((double)a*b);}
const uint32_t thug_air_wall_events[3]={9,0,0}; /* 0064bbbc */
/* 0x00508780. A successful raised path or step returns true; completing a
 * wallplant, wall transition or ordinary collision response still returns false.
 * Keep the initial Z subtraction and the endpoint W sum wide until their
 * original spill points. The retained probe owns its own moving reference.
 * Audio and script callbacks may replace live components or contact data. */
uint8_t thug_skater_resolve_air_wall(ThugSkaterPhysics *p,const float previous[4],
 ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m) {
 ThugSkaterBody *original_body=p->body,*body=original_body;
 float direction[4];
 direction[0]=(float)R((double)body->position[0]-previous[0]);
 direction[1]=(float)R((double)body->position[1]-previous[1]);
 double z=R((double)body->position[2]-previous[2]);direction[2]=(float)z;
 direction[3]=(float)R((double)body->position[3]-previous[3]);
 double length=R(__builtin_sqrt(R(R(mul(direction[0],direction[0])+mul(direction[1],direction[1]))+R(z*z))));
 if(length>0){double scale=R(1/length);direction[0]=(float)R(direction[0]*scale);direction[1]=(float)R(direction[1]*scale);direction[2]=(float)R(z*scale);}
 double height=thug_skater_get_parameter(0xd4205c9b,1,original_body);
 float up[4];for(unsigned k=0;k<4;++k)up[k]=(float)R(height*original_body->orientation[k+4]);
 for(unsigned k=0;k<4;++k)p->surface_segment[k]=(float)R((double)up[k]+previous[k]);
 double extend=thug_skater_get_parameter(0x20102726,1,original_body);
 for(unsigned k=0;k<4;++k)direction[k]=(float)R(direction[k]*extend);
 body=p->body;for(unsigned k=0;k<4;++k){double start=R((double)up[k]+body->position[k]);if(k!=3)start=(float)start;p->surface_segment[k+4]=(float)R(start+direction[k]);}
 if(!thug_skater_query_surface(p,0x10,0,query))return 0;
 float normal[4];thug_vector_copy(normal,p->surface_probe.normal);
 if(p->surface_skatable&&(!(thug_vector_dot(normal,p->orientation_target)<.800000011920929f)||!(normal[1]<.5f)))return 0;
 ThugCollisionProbe saved;thug_collision_probe_copy_initialize(&saved,&p->surface_probe);
 uint8_t wall=p->surface_probe.normal[1]<.10000000149011612f;
 float position[4];thug_vector_copy(position,p->body->position);
 body=p->body;for(unsigned k=0;k<4;++k)body->position[k]=(float)R((double)p->surface_segment[k+4]-up[k]);
 if(thug_skater_try_raised_path(p,previous,query)&&(p->body->velocity[1]>10||wall)) {thug_collision_probe_release(&saved);return 1;}
 thug_vector_copy(p->body->position,position);thug_collision_probe_assign(&p->surface_probe,&saved);
 body=p->body;
 if(body->orientation[5]>.5f&&body->velocity[1]>0&&normal[1]<.009999999776482582f) {
  float step=(float)thug_skater_get_parameter(0x786b3272,1,original_body);
  saved.segment[1]=(float)R((double)saved.segment[1]+step);saved.segment[5]=(float)R((double)saved.segment[5]+step);
  if(!thug_collision_probe_query(&saved,1,0,query)) {
   if(step>4)do {
    saved.segment[1]=(float)R((double)saved.segment[1]-2);saved.segment[5]=(float)R((double)saved.segment[5]-2);
    if(thug_collision_probe_query(&saved,1,0,query))break;
    step=(float)R((double)step-2);
   }while(step>4);
   p->body->position[1]=(float)R((double)step+p->body->position[1]);thug_collision_probe_release(&saved);return 1;
  }
 }
 if(p->state->ground_transition_flag) {
  body=p->body;for(unsigned k=0;k<4;++k)body->position[k]=(float)R((double)p->surface_probe.point[k]-up[k]);
  double push=thug_skater_get_parameter(0x23410c14,1,original_body);
  body=p->body;for(unsigned k=0;k<4;++k)body->position[k]=(float)R(R(push*normal[k])+body->position[k]);
  if(!p->state->skip_ground_probe)thug_vector_project_plane(p->body->velocity,normal);
  else thug_vector_project_preserve_length(p->body->velocity,p->surface_probe.normal);
 } else if(p->state->unknown_e0||p->state->resistance_requested||
     ((p->parameter_mode_fallback||!thug_skater_try_wallplant(p,0,0,0,query,d,m))&&!thug_skater_try_wall_transition(p,query,d,m))) {
  ThugSkaterState *state=p->state;if(state->transfer_flag_b0!=1){state->transfer_flag_b0=1;state->transfer_time_b4=thug_elapsed_time()+thug_timer_offset;}
  thug_collision_event_from_probe(p->collision_events,thug_air_wall_events,&p->surface_probe,d,m);
  if(!p->wall_gate->wall_response_suppressed) {
   if(p->surface_probe.normal[1]<.05000000074505806f) {
    if(!p->parameter_mode_active) {
     uint32_t material=p->surface_probe.result.surface_metadata;body=p->body;
     float speed=(float)thug_vector_length(body->velocity);
     float intensity=(float)R((double)speed/thug_skater_stat_parameter(body,0xcc5f87aa));
     thug_sound_component_impact(p->sound,intensity,material,d,m);
    } else thug_script_run_sync(0xd478c96d,0,(void *)p->body,0,d,m);
   }
   float y=0;if(normal[1]>-.10000000149011612f){y=p->body->velocity[1];p->body->velocity[1]=0;}
   thug_vector_project_plane(p->body->velocity,normal);body=p->body;
   float a[4],b[4];thug_vector_scaled_copy(a,normal,(float)R(thug_vector_length(body->velocity)*.10000000149011612f));
   thug_vector_add(body->velocity,a);
   if(normal[1]>-.10000000149011612f)p->body->velocity[1]=y;
   float forward_y=p->body->orientation[9];p->body->orientation[9]=0;
   thug_vector_copy(p->wallplant_saved_normal,normal);p->body->orientation[9]=forward_y;
   body=p->body;thug_vector_scaled(a,.05000000074505806f,normal);thug_vector_add(body->orientation+8,a);
   thug_vector_normalize(p->body->orientation+8);
   body=p->body;thug_vector_copy(body->orientation,thug_vector_cross(b,body->orientation+4,body->orientation+8));thug_vector_normalize(p->body->orientation);
   body=p->body;thug_vector_copy(body->orientation+4,thug_vector_cross(b,body->orientation+8,body->orientation));thug_vector_normalize(p->body->orientation+4);
   if(thug_collision_probe_has_moving_object(&p->surface_probe)) {
    ThugSkaterBody *owner=(void *)thug_collision_probe_moving_object(&p->surface_probe);
    float velocity[4];thug_vector_copy(velocity,owner->velocity);
    if(thug_vector_dot(velocity,p->surface_probe.normal)>0) {
     body=p->body;thug_vector_scaled_copy(a,velocity,p->time_step);thug_vector_scaled_copy(b,a,2);thug_vector_add(body->position,b);
     thug_vector_add(p->body->velocity,velocity);
    }
   }
  }
 }
 thug_collision_probe_release(&saved);return 0;
}
#undef R
