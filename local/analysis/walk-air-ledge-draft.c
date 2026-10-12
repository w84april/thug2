/* 0043f030: fixed/moving airborne ledge catch and immediate hanging transition. */
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/game/attachment.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/matrix.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
extern void thug_walk_change_state_draft(void *,uint32_t);
extern double thug_walk_hang_height_draft(void);
extern double thug_walk_ledge_blend_height_draft(const void *);
extern uint8_t thug_walk_scan_ledge_draft(const ThugObjectTransform *,const float[4],const float[4],const float[4],void *,float[13],float,ThugCollisionQuery *,const ThugDiagnostics *);
uint8_t thug_walk_air_ledge_draft(void *p,float fx,float fy,float fz,float fw,float tx,float ty,float tz,float tw,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)fw;(void)tw;if(number(p,0x44)>50)return 0;
 float from[4]={fx,(float)R((double)fy+parameter(0xa8c13e74)),fz,1};
 float to[4]={tx,(float)R((double)ty+parameter(0xa8c13e74)),tz,1};
 put(p,0x176c,(uintptr_t)thug_game_context->rail_transform);
 float target[13],*facing=(void *)((char *)p+0x48),radius=(float)thug_script_get_global_number(0x30ce7f2c,0);
 uint8_t found=thug_walk_scan_ledge_draft(ptr(p,0x176c),from,to,facing,p,target,radius,q,d);
 if(found)thug_skater_moving_contact_release(ptr(p,0x1784),m);
 else{
  ThugTransformComponent *component=thug_component_type_head(thug_component_type_registry,0x1cdfb2a3);
  for(;component;component=(void *)(uintptr_t)component->unknown_14){
   if(found)break;
   float inverse[16],a[4],b[4];thug_component_world_transform(component,inverse);thug_matrix_inverse(inverse);
   thug_matrix_transform_vector(inverse,a,from);thug_matrix_transform_vector(inverse,b,to);
   ThugAttachmentProvider *provider=(void *)component;put(p,0x176c,(uintptr_t)provider->methods->points(provider));
   radius=(float)thug_script_get_global_number(0x30ce7f2c,0);
   found=thug_walk_scan_ledge_draft(ptr(p,0x176c),a,b,facing,p,target,radius,q,d);
   if(found)thug_skater_moving_contact_set_owner(ptr(p,0x1784),component->base.owner,m);
  }
 }
 if(!found)return 0;
 put(p,0x1764,word(target,48));put(p,0x1768,word(ptr(target,48),0x40));
 copy4((char *)p+0x24,target);copy4(facing,target+4);put(p,0x18cc,word(target,32));put(p,0x18d0,word(target,40));put(p,0x18d4,word(target,36));put(p,0x18d8,word(target,44));
 float offset=parameter(0xc3263e6e);for(unsigned j=0;j<4;j++)fp(p,0x71c+j*4,R((double)offset*facing[j]));
 fp(p,0x720,thug_walk_hang_height_draft());put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);put(p,0x44,0);
 fp(p,0x9c,thug_walk_ledge_blend_height_draft(p));thug_walk_change_state_draft(p,2);
 if(word(p,0x1764))put(ptr(p,0x178c),0x22c,word(p,0x1764));
 if(word(p,0x176c))put(ptr(p,0x178c),0x230,word(p,0x176c));
 const uint32_t events[3]={10,3,0};thug_skater_rail_event(ptr(p,0x178c),events,d,m);put(p,0x78,0x4194ecca);
 uint8_t *state=ptr(ptr(p,0x178c),0x1528);
 if(state[0xa0]!=1){state[0xa0]=1;put(state,0xa4,thug_elapsed_time()+thug_timer_offset);}
 return 1;
}
