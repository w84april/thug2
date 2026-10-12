/* Original floor and ground updates; the common Walk frame remains incomplete. */
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/game/attachment.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
#include "../../src/game/collision_events.h"
#include "../../src/script/delivery.h"
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
extern uint8_t thug_walk_try_grind_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *);
extern uint8_t thug_walk_try_rail_top_draft(void *,ThugCollisionQuery *,const ThugMemory *);
extern uint8_t thug_walk_try_hang_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_change_state_draft(void *,uint32_t);
extern void thug_walk_leave_platform_draft(void *,float[4],float *,const ThugMemory *);
/* 0052b370,1116 bytes. Complete floor probing and surface/airborne transitions. */
void thug_walk_floor_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);copy4(probe.segment,(char *)p+0x24);
 float above=parameter(0xcee3a3e1);probe.segment[1]=(float)R((double)probe.segment[1]+above);copy4(probe.segment+4,(char *)p+0x24);
 float below=parameter(0xaf3e4251);probe.segment[5]=(float)R((double)probe.segment[5]-below);
 if(thug_collision_probe_query(&probe,1,0,query)&&!(probe.result.surface_flags&2)){
  float rise=(float)R((double)probe.point[1]-number(p,0x28)),threshold=parameter(0xd3193d8e);
  if(__builtin_fabs((double)rise)>threshold)thug_object_emit_event(ptr(p,12),rise>0?0x93fcf3ed:0x56e21153,0,diagnostics,memory);
  put(p,0x28,word(probe.point,4));
  if(rise>0||rise<-3){double remaining=R((double)number(p,0x714)-rise);if(remaining<0)remaining=0;fp(p,0x714,remaining);}
  if(word(p,0x1808)!=word(&probe,0x54)){
   if(byte(p,0x1864)){
    const uint32_t leave[3]={14,4,0};thug_collision_event_from_probe(ptr(p,0x177c),leave,(void *)((char *)p+0x17b4),diagnostics,memory);
    if(byte(ptr(p,0x1780),0x26))goto done;
   }
   const uint32_t enter[3]={14,3,0};thug_collision_event_from_probe(ptr(p,0x177c),enter,&probe,diagnostics,memory);
   if(byte(ptr(p,0x1780),0x26))goto done;
  }
  thug_collision_probe_assign((void *)((char *)p+0x17b4),&probe);((uint8_t *)p)[0x1864]=1;copy4((char *)p+0x1794,probe.normal);
  thug_skater_moving_contact_acquire(ptr(p,0x1784),&probe,memory);thug_skater_state_set_material(ptr(p,0x1788),word(&probe,0x52),diagnostics,memory);goto done;
 }
 if(thug_collision_probe_query(&probe,1,0,query)){
  for(unsigned i=0;i<4;i++){double offset=R((double)probe.normal[i]*.10000000149011612f);if(i<3)offset=(float)offset;fp(p,0x24+i*4,R((double)probe.point[i]+offset));}
 }
 if(byte(p,0x1864)){
  const uint32_t leave[3]={1,5,0};thug_collision_event_from_probe(ptr(p,0x177c),leave,(void *)((char *)p+0x17b4),diagnostics,memory);
  if(byte(ptr(p,0x1780),0x26))goto done;
 }
 if(byte(ptr(p,0x1770),0x1a0)){
  if(thug_vector_equal((void *)((char *)p+0x24),(void *)((char *)p+0x68)))fp(p,0x6c,R((double)number(p,0x6c)+.0010000000474974513f));
  if(thug_walk_try_grind_draft(p,query,diagnostics))goto done;
 }
 if(thug_walk_try_rail_top_draft(p,query,memory)||thug_walk_try_hang_draft(p,query,diagnostics,memory))goto done;
 thug_walk_change_state_draft(p,1);copy4((char *)p+0x1878,(char *)p+0x48);
 thug_walk_leave_platform_draft(p,(void *)((char *)p+0x34),(void *)((char *)p+0x44),memory);
 put(p,0x78,0xabf1f6ac);thug_object_broadcast_event(ptr(p,12),0xd96f01f1,0,0,diagnostics,memory);
 done:thug_collision_probe_release(&probe);
}
extern void thug_walk_follow_platform_draft(void *,const ThugMemory *);
extern void thug_walk_prepare_cache_draft(void *);
extern void thug_walk_accelerate_draft(void *,float[4],ThugCollisionQuery *);
extern uint8_t thug_walk_resolve_contacts_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_face_velocity_draft(void *);
extern void thug_walk_step_height_draft(void *,ThugCollisionQuery *);
extern void *thug_moving_contact_escape_draft(void *,void *,const void *,ThugCollisionQuery *);
/* 0052d300,431 bytes. Full ground state, including the floor and common tail. */
void thug_walk_ground_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 thug_walk_follow_platform_draft(p,memory);thug_walk_prepare_cache_draft(p);thug_walk_accelerate_draft(p,(void *)((char *)p+0x34),query);
 if(word(p,0x78)==0x1d537eff&&number(p,0x1870)<parameter(0x8e1cf27a))put(p,0x78,0x9b46e749);
 if(thug_walk_resolve_contacts_draft(p,query,diagnostics,memory))thug_walk_face_velocity_draft(p);else ((uint8_t *)p)[0x186c]=0;
 ((uint8_t *)p)[0x1958]=0;if(word(p,0x18)||byte(ptr(p,0x1780),0x26))goto done;
 double dx=R((double)number(p,0x80)*number(p,0x34));float dy=(float)R((double)number(p,0x80)*number(p,0x38)),dz=(float)R((double)number(p,0x80)*number(p,0x3c)),dw=(float)R((double)number(p,0x80)*number(p,0x40));
 fp(p,0x24,R(dx+number(p,0x24)));fp(p,0x28,R((double)dy+number(p,0x28)));fp(p,0x2c,R((double)dz+number(p,0x2c)));fp(p,0x30,R((double)dw+number(p,0x30)));
 thug_walk_floor_draft(p,query,diagnostics,memory);if(word(p,0x18)||byte(ptr(p,0x1780),0x26))goto done;
 thug_walk_step_height_draft(p,query);
 void *owner=thug_moving_contact_escape_draft(ptr(p,0x1784),(char *)p+0x24,(char *)p+0x68,query);
 if(owner){
  diagnostics->print(diagnostics->context,"M:%s:%i: %s\n","mponents\\WalkComponent.cpp",0x369,"WALKING_GROUND, within moving object");
  thug_vector_copy((void *)((char *)p+0x34),(void *)((char *)owner+0xac));put(p,0x38,0);put(p,0x44,0);
  double squared=thug_vector_length_squared((void *)((char *)p+0x34));
  if(squared>100){float normalized[4];thug_vector_divided(normalized,(void *)((char *)p+0x34),(float)R(__builtin_sqrt(squared)));thug_vector_copy((void *)((char *)p+0x48),normalized);}
 }
 thug_skater_update_projectile(ptr(p,0x178c),diagnostics,memory);
 done:thug_collision_default_cache=0;
}
