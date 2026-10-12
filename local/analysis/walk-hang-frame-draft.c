/* Ledge traversal and corner-facing updates from the original walking engine. */
#include "../../src/game/rail.h"
#include "../../src/game/moving_contact.h"
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
extern double thug_walk_hang_height_draft(void);
extern uint8_t thug_walk_follow_ledge_draft(void *,float *,ThugRailNode *,ThugRailNode *,ThugRailNode **,ThugRailNode **,ThugCollisionQuery *,const ThugDiagnostics *);
extern uint8_t thug_walk_hang_side_blocked_draft(void *,const float[4],float,const float[4],uint32_t,const float[4],float,float,float,float,ThugRailNode *,ThugRailNode *,ThugCollisionQuery *,const ThugDiagnostics *);
#include "../../src/script/delivery.h"
extern uint32_t thug_walk_hang_drop_input_draft(const void *);
extern void thug_walk_hang_pose_draft(void *,const ThugMemory *);
extern uint8_t thug_walk_hang_climb_draft(void *,float[4],ThugCollisionQuery *);
extern void thug_walk_hang_traverse_draft(void *,float,ThugCollisionQuery *,const ThugDiagnostics *);
extern void thug_walk_change_state_draft(void *,uint32_t),thug_walk_leave_platform_draft(void *,float[4],float *,const ThugMemory *);
/* 00440bf0: moving ledge transport, climb/drop input and smoothed traversal. */
void thug_walk_hang_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *contact=gate->contact;
 if(contact){
  if(!contact->reference.object||!thug_moving_contact_update(contact,(void *)((char *)p+0x24)))thug_skater_moving_contact_release(gate,m);
  else{
   contact=((ThugSkaterGroundGate *)ptr(p,0x1784))->contact;
   ThugObjectComponent *component=thug_object_find_component((void *)contact->reference.object,0x1cdfb2a3);float matrix[16];thug_component_world_transform((void *)component,matrix);thug_walk_hang_pose_draft(p,m);
  }
 }
 *((uint8_t *)p+0x1958)=0;
 if(*((uint8_t *)p+0x98)){
  const void *pad=(char *)ptr(p,0x1770)+0x20;
  if(!word(pad,0x230)&&number(pad,0x22c)!=0&&__builtin_fabsf(number(pad,0x228))<.7853981852531433f){
   float candidate[4],distance=parameter(0x21dfbe77);
   for(unsigned i=0;i<4;i++){double delta=R((double)distance*number(p,0x48+i*4));if(i>=2)delta=(float)delta;candidate[i]=(float)R(delta+number(p,0x24+i*4));}
   candidate[1]=(float)R((double)candidate[1]+parameter(0x52fa7ca6));if(thug_walk_hang_climb_draft(p,candidate,q))return;
   double half=R((double)parameter(0x21dfbe77)*.5f);
   for(unsigned i=0;i<4;i++){double delta=R(half*number(p,0x48+i*4));if(i<3)delta=(float)delta;candidate[i]=(float)R(delta+number(p,0x24+i*4));}
   candidate[1]=(float)R((double)candidate[1]+parameter(0x52fa7ca6));if(thug_walk_hang_climb_draft(p,candidate,q))return;
  }else if(thug_walk_hang_drop_input_draft(pad)){
   thug_walk_change_state_draft(p,1);thug_object_emit_event(ptr(p,12),0xbeedb40d,0,d,m);const uint32_t events[3]={10,4,0};thug_skater_rail_event(ptr(p,0x178c),events,d,m);
   copy4((char *)p+0x1878,(char *)p+0x48);thug_walk_leave_platform_draft(p,(void *)((char *)p+0x34),(void *)((char *)p+0x44),m);put(p,0x78,0x439f4704);return;
  }
 }
 float angle=(float)R(1.5707963705062866f-__builtin_fabsf(number(ptr(p,0x1770),0x248))),target=0;
 if(thug_platform_cos(R((double)parameter(0x1b877928)*.01745329238474369f))>__builtin_fabsf(angle)){
  float sign=number(ptr(p,0x1770),0x248)>0?1:-1;float rate=parameter(0xd77ee881);target=(float)R(R((double)sign*number(p,0x94))*rate);
 }
 float rate=parameter(0xc506a97c);double current=number(p,0x18dc);fp(p,0x18dc,R(R(R((double)target-current)*R((double)rate*number(p,0x80)))+current));
 float saved=number(p,0x18dc),threshold=parameter(0x228b5376);
 if(__builtin_fabsf(saved)>threshold){
  fp(p,0x704,__builtin_fabsf(number(p,0x18dc)));float step=(float)R((double)number(p,0x18dc)*number(p,0x80));thug_walk_hang_traverse_draft(p,step,q,d);thug_walk_hang_pose_draft(p,m);
 }else put(p,0x78,0x4194ecca);
}
