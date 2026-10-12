/* 0052cef0: complete airborne Walk update, composed from recovered callees. */
#include "../../src/game/skater.h"
#include "../../src/game/grind.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static uint8_t byte(const void *p,unsigned o){return *((const uint8_t *)p+o);}
extern void thug_walk_prepare_cache_draft(void *),thug_walk_air_steering_draft(void *),thug_walk_air_plane_draft(void *);
extern double thug_walk_gravity_draft(void);
extern uint8_t thug_walk_resolve_contacts_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_air_ceiling_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_air_landing_draft(void *,const float[4],const float[4],ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern uint8_t thug_walk_air_ledge_draft(void *,float,float,float,float,float,float,float,float,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern uint8_t thug_walk_air_rail_draft(void *,const float[4],const float[4],ThugCollisionQuery *,const ThugMemory *);
extern uint8_t thug_walk_try_grind_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *);
extern uint8_t thug_walk_air_transfer_draft(void *,ThugCollisionQuery *,const ThugMemory *);
extern void thug_walk_air_wallplant_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_air_contact_jump_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void *thug_moving_contact_escape_draft(void *,void *,const void *,ThugCollisionQuery *);
void thug_walk_air_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 uint8_t *input=ptr(p,0x1770);thug_walk_prepare_cache_draft(p);put(p,0x78,0x439f4704);thug_walk_air_steering_draft(p);
 if(!thug_walk_resolve_contacts_draft(p,q,d,m))*((uint8_t *)p+0x186c)=0;
 if(byte(ptr(p,0x1780),0x26))return;
 thug_walk_air_plane_draft(p);thug_walk_air_ceiling_draft(p,q,d,m);double gravity=thug_walk_gravity_draft();
 float *position=(void *)((char *)p+0x24),*previous=(void *)((char *)p+0x68);
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<4;i++)fp(p,0x24+4*i,R(R((double)number(p,0x80)*number(p,(j?0x189c:0x34)+4*i))+position[i]));
 double dt=number(p,0x80);fp(p,0x28,R(R(R((double)number(p,0x44)*dt)-R(R(R(dt*dt)*gravity)*.5))+number(p,0x28)));
 fp(p,0x44,R((double)number(p,0x44)-R(gravity*number(p,0x80))));
 if(number(p,0x28)>number(p,0x18ac)){put(p,0x189c,0);put(p,0x18a0,0);put(p,0x18a4,0);put(p,0x18a8,0x3f800000);}
 thug_skater_update_projectile(ptr(p,0x178c),d,m);thug_walk_air_landing_draft(p,previous,position,q,d,m);
 if(word(p,0x18)!=1||byte(ptr(p,0x1780),0x26))return;
 if(input[0x100]&&!byte(p,0x9a)){
  uint32_t old=word(p,0x20);uint8_t eligible=1;
  if(old==2||old==3||old==4){uint32_t age=thug_time_since(word(p,0x1c));double elapsed=(int32_t)age;if((int32_t)age<0)elapsed=R(elapsed+0x1p32);eligible=thug_walk_parameter((uintptr_t)p,0xe6e0c0a4)<(float)elapsed;}
  if(eligible&&(thug_walk_air_ledge_draft(p,previous[0],previous[1],previous[2],previous[3],position[0],position[1],position[2],position[3],q,d,m)||thug_walk_air_rail_draft(p,previous,position,q,m))){thug_collision_default_cache=0;return;}
 }
 thug_collision_default_cache=0;
 if(input[0x1a0]&&thug_walk_try_grind_draft(p,q,d))return;
 if(thug_walk_air_transfer_draft(p,q,m))return;
 thug_walk_air_wallplant_draft(p,q,d,m);thug_walk_air_contact_jump_draft(p,q,d,m);
 if(byte(ptr(p,0x1780),0x26))return;
 float old_position[4],current_point[4],previous_point[4],*offset=(void *)((char *)p+0x71c);
 thug_vector_copy(old_position,position);thug_vector_sum(current_point,position,offset);thug_vector_sum(previous_point,previous,offset);
 if(!thug_moving_contact_escape_draft(ptr(p,0x1784),current_point,previous_point,q))return;
 float corrected[4];thug_vector_difference(corrected,current_point,offset);thug_vector_copy(position,corrected);
 d->print(d->context,"M:%s:%i: %s\n","mponents\\WalkComponent.cpp",0x74b,"WALKING_AIR, within moving object");
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);const float vertical[4]={0,30,0,0};
 thug_vector_sum(probe.segment,(void *)((char *)ptr(p,12)+0x4c),vertical);thug_vector_difference(probe.segment+4,(void *)((char *)ptr(p,12)+0x4c),vertical);
 if(thug_collision_probe_query(&probe,1,0,q)&&thug_collision_probe_has_moving_object(&probe))thug_skater_moving_contact_set_owner(ptr(p,0x1784),(void *)thug_collision_probe_moving_object(&probe),m);
 put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);put(p,0x44,0);
 thug_walk_air_landing_draft(p,position,old_position,q,d,m);thug_collision_probe_release(&probe);
}
