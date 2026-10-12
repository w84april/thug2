/* 005293f0: choose a retained wall contact and apply a held-input rebound. */
#include "../../src/game/skater.h"
#include "../../src/game/objectives.h"
#include "../../src/game/collision_events.h"
#include "../../src/core/timing.h"
#include "../../src/core/vector.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
static double unsigned_number(uint32_t x){double v=(int32_t)x;if((int32_t)x<0)v=R(v+0x1p32);return v;}
extern void thug_walk_air_jump_clearance_draft(void *,ThugCollisionQuery *);
void thug_walk_air_contact_jump_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(!*((uint8_t *)ptr(p,0x1770)+0x1c0)||number(p,0x44)>0)return;
 if(thug_script_get_global_number(0xd5349cc6,0)>number(ptr(p,0x1788),0x11c))return;
 float elapsed=(float)unsigned_number(thug_time_since(word(ptr(p,0x178c),0x4e0)));
 if(thug_script_get_global_number(0x82135dd7,0)>elapsed)return;
 elapsed=(float)unsigned_number(thug_time_since(word(p,0x1c)));
 if(thug_script_get_global_number(0x4c2b6df3,0)>elapsed)return;
 const unsigned order[7]={0,1,6,2,5,3,4};unsigned i;
 for(i=0;i<7;i++)if(*((uint8_t *)p+0xa0+order[i]*0xcc))break;
 if(i==7)return;
 uint8_t *contact=(uint8_t *)p+0xa0+order[i]*0xcc;
 float direction[4];thug_vector_copy(direction,(void *)((char *)p+(number(p,0x94)==0?0x1878:0x84)));
 float *normal=(void *)(contact+4);
 double dot=R(R(R((double)direction[2]*normal[2])+R((double)direction[1]*normal[1]))+R((double)direction[0]*normal[0]));
 if(dot<0){float reflected[4];thug_vector_scaled(reflected,(float)R(dot+dot),normal);thug_vector_subtract(direction,reflected);}
 float jump=parameter(0x420d18bc),duration=parameter(0x12333ebd);
 double held=unsigned_number(thug_input_button_elapsed((void *)((char *)ptr(p,0x1770)+0x1c0)));
 double ratio=R(held/duration);
 if(held==0&&duration==0)ratio=-__builtin_nan("");
 float fraction=ratio>1?1:(float)ratio,minimum=parameter(0x246d0bf3);
 fp(p,0x44,R(R(R(R(1.0-minimum)*fraction)+minimum)*jump));
 float speed=parameter(0x99510695);for(unsigned k=0;k<4;k++)fp(p,0x34+4*k,R((double)speed*direction[k]));
 thug_vector_copy((void *)((char *)p+0x1878),(void *)((char *)p+0x48));
 ThugCollisionProbe *probe=(void *)(contact+0x1c);
 if(thug_collision_probe_has_moving_object(probe)){
  void *owner=thug_collision_probe_moving_object(probe);
  fp(p,0x44,R((double)number(owner,0xb0)+number(p,0x44)));
  fp(p,0x34,R((double)number(owner,0xac)+number(p,0x34)));
  fp(p,0x3c,R((double)number(owner,0xb4)+number(p,0x3c)));
 }
 thug_walk_air_jump_clearance_draft(p,q);
 const uint32_t events[3]={2,4,0};thug_collision_event_from_probe(ptr(p,0x177c),events,probe,d,m);
 if(*((uint8_t *)ptr(p,0x1780)+0x26))return;
 uint32_t key=word(contact,0x74);
 thug_skater_notify((void *)thug_object_find_component(ptr(p,12),0x270f56e1),key,d,m);
 uint32_t now=thug_elapsed_time()+thug_timer_offset;put(ptr(p,0x178c),0x4e0,now);put(p,0x78,0xcf74f6b7);
}
