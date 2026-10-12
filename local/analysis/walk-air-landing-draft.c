/* 0052a700: swept airborne collision, sliding and landing state publication. */
#include "../../src/game/skater.h"
#include "../../src/game/stats.h"
#include "../../src/game/grind.h"
#include "../../src/game/moving_contact.h"
#include "../../src/game/collision_events.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
extern void thug_walk_change_state_draft(void *,uint32_t);
static void clear_vector(void *p,unsigned o){put(p,o,0);put(p,o+4,0);put(p,o+8,0);put(p,o+12,0x3f800000);}
void thug_walk_air_landing_draft(void *p,const float from[4],const float to[4],ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);thug_vector_copy(probe.segment,from);thug_vector_copy(probe.segment+4,to);
 if(!thug_collision_probe_query(&probe,1,0,q))goto done;
 float *position=(float *)((char *)p+0x24);
 if(probe.result.surface_flags&2){
  for(unsigned i=0;i<4;i++){double offset=R((double)probe.normal[i]*.10000000149011612f);if(i<3)offset=(float)offset;position[i]=(float)R((double)probe.point[i]+offset);}
  float delta[4];double dw=R((double)probe.segment[7]-probe.segment[3]);
  for(unsigned i=0;i<3;i++)delta[i]=(float)R((double)probe.segment[i+4]-probe.segment[i]);
  float fraction=(float)R(1.0-probe.fraction);
  for(unsigned i=0;i<3;i++)delta[i]=(float)R((double)delta[i]*fraction);delta[3]=(float)R(dw*fraction);
  thug_vector_project_plane(delta,probe.normal);thug_vector_copy(probe.segment,position);
  for(unsigned i=0;i<4;i++)probe.segment[i+4]=(float)R((double)delta[i]+position[i]);
  if(thug_collision_probe_query(&probe,1,0,q)){
   for(unsigned i=0;i<4;i++){double offset=R((double)probe.normal[i]*.05000000074505806f);if(i<3)offset=(float)offset;position[i]=(float)R((double)probe.point[i]+offset);}
  }else thug_vector_copy(position,probe.segment+4);
  goto done;
 }
 thug_vector_copy(position,probe.point);put(p,0x44,0);thug_walk_change_state_draft(p,0);
 thug_collision_probe_assign((void *)((char *)p+0x17b4),&probe);*((uint8_t *)p+0x1864)=1;
 const uint32_t events[3]={8,3,0};thug_collision_event_from_probe(ptr(p,0x177c),events,(void *)((char *)p+0x17b4),d,m);
 if(*((uint8_t *)ptr(p,0x1780)+0x26))goto done;
 thug_vector_copy((void *)((char *)p+0x1794),probe.normal);
 ThugSkaterGroundGate *gate=ptr(p,0x1784);thug_skater_moving_contact_acquire(gate,&probe,m);
 if(gate->contact){
  if(!gate->contact->reference.object)thug_skater_moving_contact_release(gate,m);
  else{thug_vector_subtract((void *)((char *)p+0x34),(void *)((char *)gate->contact->reference.object+0xac));put(p,0x38,0);}
 }
 float *velocity=(float *)((char *)p+0x34),*facing=(float *)((char *)p+0x48);
 double dot=R(R(R((double)velocity[2]*facing[2])+R((double)velocity[1]*facing[1]))+R((double)velocity[0]*facing[0]));
 if(dot>0){
  thug_vector_project_axis(velocity,facing);
  if(number(p,0x94)==0){float speed=(float)thug_vector_length(velocity);if(thug_walk_parameter((uintptr_t)p,0x530dcf34)>speed)clear_vector(p,0x34);}
 }else clear_vector(p,0x34);
 clear_vector(p,0x71c);thug_input_button_clear_pending((void *)((char *)ptr(p,0x1770)+0x1c0));put(p,0x78,0x57ff2a27);
done:thug_collision_probe_release(&probe);
}
