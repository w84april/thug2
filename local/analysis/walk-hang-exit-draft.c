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
#include "../../src/script/delivery.h"
/* 0043db00: settle a ledge climb on its retained floor contact. */
void thug_walk_hang_ground_finish_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 thug_walk_change_state_draft(p,0);thug_object_emit_event(ptr(p,12),0xbeedb40d,0,d,m);
 const uint32_t rail_events[3]={10,4,0};thug_skater_rail_event(ptr(p,0x178c),rail_events,d,m);
 if(*((uint8_t *)p+0x1864)){const uint32_t floor_events[3]={1,3,0};ThugCollisionProbe *probe=(void *)((char *)p+0x17b4);thug_collision_event_from_probe(ptr(p,0x177c),floor_events,probe,d,m);thug_skater_moving_contact_acquire(ptr(p,0x1784),probe,m);}
 put(p,0x71c,0);put(p,0x720,0);put(p,0x724,0);put(p,0x728,0x3f800000);put(p,0x9c,word(p,0x1918));
}
/* 0043db90: finish a climb without a floor and inherit platform velocity. */
void thug_walk_hang_air_finish_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 thug_walk_change_state_draft(p,1);thug_object_emit_event(ptr(p,12),0xbeedb40d,0,d,m);
 const uint32_t events[3]={10,4,0};thug_skater_rail_event(ptr(p,0x178c),events,d,m);copy4((char *)p+0x1878,(char *)p+0x48);
 thug_walk_leave_platform_draft(p,(void *)((char *)p+0x34),(void *)((char *)p+0x44),m);put(p,0x9c,word(p,0x1918));
}
/* 0043e530: floor candidates, radial clearance and the climb-up transition. */
uint8_t thug_walk_hang_climb_draft(void *p,float candidate[4],ThugCollisionQuery *q){
 ThugCollisionProbe floor,clearance;thug_collision_probe_initialize(&floor);float target[4];uint8_t found=thug_walk_exit_floor_draft(p,candidate,target,&floor,q);
 if(!found){
  float original[4];copy4(original,target);float side_x=-number(p,0x50),side_z=number(p,0x48);
  candidate[0]=(float)R(R((double)side_x*12)+candidate[0]);candidate[2]=(float)R(R((double)side_z*12)+candidate[2]);candidate[3]=(float)R((double)candidate[3]+12);
  found=thug_walk_exit_floor_draft(p,candidate,target,&floor,q);
  if(!found){
   candidate[0]=(float)R((double)candidate[0]-R((double)side_x*24));candidate[2]=(float)R((double)candidate[2]-R((double)side_z*24));candidate[3]=(float)R((double)candidate[3]-24);
   found=thug_walk_exit_floor_draft(p,candidate,target,&floor,q);if(!found)copy4(target,original);
  }
 }
 thug_collision_probe_initialize(&clearance);float radius=(float)R((double)parameter(0xa20c43b7)*.5f),height=parameter(0x6da7f696);float dy=(float)R((double)radius*0);
 uint8_t result=0;
 for(unsigned i=0;i<7;i++){
  copy4(clearance.segment,target);clearance.segment[1]=(float)R((double)target[1]+height);
  double angle=R((double)i*.8975979089736938f),cosine=thug_platform_cos(angle),sine=thug_platform_sin(angle);
  float x=(float)R(R(cosine*number(p,0x48))-R(sine*number(p,0x50)));x=(float)R((double)x*radius);
  float z=(float)R(R(R(sine*number(p,0x48))+R(cosine*number(p,0x50)))*radius);
  clearance.segment[4]=(float)R((double)x+target[0]);clearance.segment[5]=(float)R((double)(float)R((double)dy+target[1])+height);
  clearance.segment[6]=(float)R((double)z+target[2]);clearance.segment[7]=(float)R((double)target[3]+radius);
  if(thug_collision_probe_query(&clearance,1,0,q))goto done;
 }
 for(unsigned i=0;i<4;i++){double delta=R((double)number(p,0x48+i*4)*-6);if(i>=2)delta=(float)delta;clearance.segment[i]=(float)R(delta+number(p,0x24+i*4));}
 float high=parameter(0xa8c13e74),extra=parameter(0x9b2818cf);clearance.segment[1]=(float)R(R((double)clearance.segment[1]+extra)+high);
 copy4(clearance.segment+4,target);clearance.segment[5]=(float)R((double)target[1]+1);
 if(thug_collision_probe_query(&clearance,1,0,q))goto done;
 void (*callback)(void *,const ThugDiagnostics *,const ThugMemory *)=found?thug_walk_hang_ground_finish_draft:thug_walk_hang_air_finish_draft;
 put(p,0x1948,(uintptr_t)callback);put(p,0x194c,0);put(p,0x1950,0);put(p,0x1954,0);
 if(found){thug_collision_probe_assign((void *)((char *)p+0x17b4),&floor);*((uint8_t *)p+0x1864)=1;copy4((char *)p+0x1794,floor.normal);}
 copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);thug_walk_prepare_facing_draft(p,(void *)((char *)p+0x48),0x3f800000);
 put(p,0x1944,1);put(p,0x1914,word(p,0x9c));put(p,0x1918,0);
 double back=-R((double)parameter(0x21dfbe77)+6);float stored_back=(float)back;
 for(unsigned i=0;i<4;i++)fp(p,0x71c+i*4,R((i==3?back:stored_back)*number(p,0x48+i*4)));put(p,0x720,0x3f800000);
 copy4((char *)p+0x18b4,(char *)p+0x48);fp(p,0x18c8,R((double)number(p,0x28)-number(p,0x18d0)));thug_walk_change_state_draft(p,4);put(p,0x78,0x9ef9f8f1);result=1;
 done:thug_collision_probe_release(&clearance);thug_collision_probe_release(&floor);return result;
}
