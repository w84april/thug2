/* 00527080: original ground validation, surface light, shadow and fallback. */
#include "../../src/game/skater.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
extern void thug_walk_change_state_draft(void *,uint32_t);
extern void thug_model_surface_light_draft(void *,const ThugCollisionProbe *,uint32_t,float);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
#define R thug_platform_round_x87_single
void thug_walk_validate_ground_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d){
 float depth=(float)R(thug_script_get_global_number(0x801c9cb6,0)*12);
 ThugCollisionProbe ground,light;thug_collision_probe_initialize(&ground);
 for(unsigned i=0;i<4;i++)ground.segment[i]=ground.segment[i+4]=(float)R((double)number(p,0x24+i*4)+number(p,0x71c+i*4));
 float y=ground.segment[1];ground.segment[1]=(float)R((double)y+1);ground.segment[5]=(float)R((double)y-depth);
 uint8_t hit=thug_collision_probe_query(&ground,1,0,q);
 thug_collision_probe_initialize(&light);thug_collision_probe_set_flags(&light,0,0x20);
 for(unsigned i=0;i<4;i++)light.segment[i]=light.segment[i+4]=(float)R((double)number(p,0x24+i*4)+number(p,0x71c+i*4));
 light.segment[1]=(float)R((double)light.segment[1]+12);
 if(hit){thug_vector_copy(light.segment+4,ground.point);light.segment[5]=(float)R((double)ground.point[1]-1);}
 else light.segment[5]=(float)R((double)light.segment[1]-depth);
 uint8_t second=thug_collision_probe_query(&light,1,0,q);
 if(second||hit)thug_model_surface_light_draft(ptr(p,0x1778),second?&light:&ground,1,1);
 if(hit){
  fp(ptr(p,0x1788),0x11c,R((double)number(p,0x28)-ground.point[1]));
  void *shadow=thug_object_find_component(ptr(p,12),0x8a897dd2);
  thug_shadow_set_position(shadow,ground.point);thug_shadow_set_up(shadow,ground.normal);
 }else{
  if(d&&d->print)d->print(d->context,"M:%s:%i: %s\n","mponents\\WalkComponent.cpp",0x941,"applying uber frig");
  thug_vector_copy((void *)((char *)p+0x24),(void *)((char *)p+0x68));
  put(p,0x38,0);put(p,0x40,0x3f800000);fp(p,0x34,R((double)number(p,0x34)*-1));fp(p,0x3c,R((double)number(p,0x3c)*-1));
  for(unsigned i=0;i<4;i++)fp(p,0x48+i*4,R((double)number(p,0x48+i*4)*-1));
  put(p,0x44,0);*((uint8_t *)p+0x70c)=1;put(p,0x710,60);thug_walk_change_state_draft(p,0);
  *((uint8_t *)p+0x1864)=0;put(p,0x1794,0);put(p,0x1798,0x3f800000);put(p,0x179c,0);put(p,0x17a0,0x3f800000);put(p,0x78,0x57ff2a27);
 }
 thug_collision_probe_release(&light);thug_collision_probe_release(&ground);
}
