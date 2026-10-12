/* Original vertical-rail climbing and animation-backed exits. */
#include "../../src/game/skater.h"
#include "../../src/game/rail.h"
#include "../../src/game/moving_contact.h"
#include "../../src/game/collision_events.h"
#include "../../src/core/timing.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void copy4(void *out,const void *in){for(unsigned i=0;i<4;i++)put(out,4*i,word(in,4*i));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
extern uint8_t thug_walk_exit_floor_draft(void *,const float[4],float[4],ThugCollisionProbe *,ThugCollisionQuery *);
extern void thug_walk_change_state_draft(void *,uint32_t),thug_walk_prepare_facing_draft(void *,const float[4],uint32_t);
extern void thug_walk_leave_platform_draft(void *,float[4],float *,const ThugMemory *);
/* 00441020 and00441070: distinct lower/upper completion event sequences. */
static void finish_ground(void *p,const uint32_t floor_events[3],const ThugDiagnostics *d,const ThugMemory *m){
 thug_walk_change_state_draft(p,0);const uint32_t rail_events[3]={10,4,0};thug_skater_rail_event(ptr(p,0x178c),rail_events,d,m);
 if(*((uint8_t *)p+0x1864)){
  ThugCollisionProbe *probe=(void *)((char *)p+0x17b4);thug_collision_event_from_probe(ptr(p,0x177c),floor_events,probe,d,m);
  thug_skater_moving_contact_acquire(ptr(p,0x1784),probe,m);
 }
}
void thug_walk_rail_bottom_finish_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){const uint32_t events[3]={1,3,0};finish_ground(p,events,d,m);}
void thug_walk_rail_top_finish_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){const uint32_t events[3]={14,3,0};finish_ground(p,events,d,m);}
/* 00441860: top exit without a floor inherits any platform velocity. */
void thug_walk_rail_air_finish_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 thug_walk_change_state_draft(p,1);const uint32_t events[3]={10,4,0};thug_skater_rail_event(ptr(p,0x178c),events,d,m);
 copy4((char *)p+0x1878,(char *)p+0x48);thug_walk_leave_platform_draft(p,(void *)((char *)p+0x34),(void *)((char *)p+0x44),m);
}
static void transition(void *p,float target_height){
 put(p,0x1914,word(p,0x9c));put(p,0x1918,0);thug_walk_prepare_facing_draft(p,(void *)((char *)p+0x48),0x3f800000);
 put(p,0x1944,1);copy4((char *)p+0x18b4,(char *)p+0x48);fp(p,0x18c8,target_height);thug_walk_change_state_draft(p,4);
}
static void callback(void *p,void (*fn)(void *,const ThugDiagnostics *,const ThugMemory *)){
 put(p,0x1948,(uintptr_t)fn);put(p,0x194c,0);put(p,0x1950,0);put(p,0x1954,0);
}
/* 00441680: lower exit queries directly into the retained collision probe. */
void thug_walk_rail_bottom_exit_draft(void *p,ThugCollisionQuery *q){
 float target[4],distance=parameter(0xcaf2831b);
 for(unsigned i=0;i<4;i++){double delta=R((double)distance*number(p,0x48+i*4));if(i>=2)delta=(float)delta;target[i]=(float)R((double)number(p,0x24+i*4)-delta);}
 target[1]=(float)R((double)target[1]-parameter(0x5296e3fd));
 ThugCollisionProbe *probe=(void *)((char *)p+0x17b4);uint8_t found=thug_walk_exit_floor_draft(p,target,target,probe,q);*((uint8_t *)p+0x1864)=found;
 if(found)copy4((char *)p+0x1794,probe->normal);
 copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);callback(p,thug_walk_rail_bottom_finish_draft);
 transition(p,number(p,0x28));put(p,0x78,0x4db1bbb1);
}
/* 00441b80: upper exit retains a hit, or selects the airborne completion. */
void thug_walk_rail_top_exit_draft(void *p,ThugCollisionQuery *q){
 float target[4],distance=parameter(0xb620b580);
 for(unsigned i=0;i<4;i++){double delta=R((double)distance*number(p,0x48+i*4));if(i<3)delta=(float)delta;target[i]=(float)R(delta+number(p,0x24+i*4));}
 target[1]=(float)R((double)target[1]+parameter(0x76bf49e0));
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);uint8_t found=thug_walk_exit_floor_draft(p,target,target,&probe,q);
 copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);
 if(found){callback(p,thug_walk_rail_top_finish_draft);thug_collision_probe_assign((void *)((char *)p+0x17b4),&probe);*((uint8_t *)p+0x1864)=1;copy4((char *)p+0x1794,(char *)p+0x183c);}
 else callback(p,thug_walk_rail_air_finish_draft);
 transition(p,target[1]);put(p,0x78,0x12521bfb);thug_collision_probe_release(&probe);
}
/* 00442280: move along the rail, select an exit, or publish the climbing pose. */
void thug_walk_rail_climb_draft(void *p,ThugCollisionQuery *q){
 float rate=parameter(0x0ab2db54);double speed=R(R(thug_platform_cos(number(ptr(p,0x1770),0x248))*number(p,0x94))*rate);
 fp(p,0x704,speed);void *node=ptr(p,0x1764),*other=ptr(node,0x40);float step=(float)R(speed*number(p,0x80));if(!other)other=ptr(node,0x44);
 float from[4],to[4],delta[4];thug_rail_point(ptr(p,0x176c),from,node);thug_rail_point(ptr(p,0x176c),to,other);
 for(unsigned i=0;i<4;i++)delta[i]=(float)R((double)to[i]-from[i]);
 double length=R(__builtin_sqrt(R(R(R((double)delta[2]*delta[2])+R((double)delta[1]*delta[1]))+R((double)delta[0]*delta[0]))));
 double change=R((double)step/length);uint8_t rising=change>0;fp(p,0x18cc,R(change+number(p,0x18cc)));float stored_length=(float)length;
 float lower=parameter(0x5296e3fd),inverse=(float)R(1.0/stored_length);
 if(R((double)inverse*lower)>number(p,0x18cc)){thug_walk_rail_bottom_exit_draft(p,q);return;}
 float upper=parameter(0x76bf49e0);
 if(R(R((double)stored_length-upper)*inverse)<number(p,0x18cc)){thug_walk_rail_top_exit_draft(p,q);return;}
 float fraction=number(p,0x18cc);if(fraction>1)fraction=1;else if(fraction<0)fraction=0;fp(p,0x18cc,fraction);
 if(fraction==0||fraction==1){put(p,0x78,0xc84243da);put(p,0x704,0);}
 else put(p,0x78,0xfec9dded+(rising?0xb090de95u:0));
 float offset[4];float distance=parameter(0x35b3bbda);for(unsigned i=0;i<4;i++){offset[i]=(float)R((double)distance*number(p,0x48+i*4));delta[i]=(float)R((double)number(p,0x18cc)*delta[i]);}
 thug_rail_point(ptr(p,0x176c),from,ptr(p,0x1764));
 for(unsigned i=0;i<4;i++){double sum=R((double)delta[i]+from[i]);if(i)sum=(float)sum;fp(p,0x24+i*4,R(sum-offset[i]));}
 fp(p,0x704,__builtin_fabsf(number(p,0x704)));
}
/* 004425b0: short entry event window and the original input-angle cone. */
void thug_walk_rail_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 uint32_t age=thug_time_since(word(p,0x1c));if(age<25){const uint32_t events[3]={10,3,0};thug_skater_rail_event(ptr(p,0x178c),events,d,m);}
 *((uint8_t *)p+0x1958)=0;float angle=(float)R(1.5707963705062866f-__builtin_fabsf(number(ptr(p,0x1770),0x248)));
 double threshold=thug_platform_cos(R((double)parameter(0x7ee1b95b)*.01745329238474369f));
 if(__builtin_fabsf(angle)>threshold)thug_walk_rail_climb_draft(p,q);
 else{put(p,0x78,0xc84243da);put(p,0x704,0);}
}
