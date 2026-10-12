/* 00526ba0: airborne overhead collision and corrected-position recheck. */
#include <stddef.h>
#include "../../src/collision/probe.h"
#include "../../src/core/vector.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
void thug_walk_air_ceiling_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(*((uint8_t *)p+0x18b0))return;
 float height;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x9ea1974a,&height,1);
 if(number(p,0x44)<0)height=(float)R((double)height-18);
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 thug_vector_copy(probe.segment,(float *)((char *)p+0x24));thug_vector_copy(probe.segment+4,probe.segment);
 probe.segment[1]=(float)R((double)number(p,0x28)+3);probe.segment[5]=(float)R((double)number(p,0x28)+height);
 if(thug_collision_probe_query(&probe,1,0,q)){
  put(p,0x38,word(p,0x44));float *velocity=(float *)((char *)p+0x34);
  double dot=R(R(R((double)probe.normal[1]*velocity[1])+R((double)probe.normal[2]*velocity[2]))+R((double)probe.normal[0]*velocity[0]));
  if(dot<0)thug_vector_project_plane(velocity,probe.normal);
  float correction[4];for(unsigned i=0;i<4;i++)correction[i]=(float)R((double)probe.point[i]-probe.segment[4+i]);
  put(p,0x44,word(p,0x38));put(p,0x38,0);thug_vector_project_axis(correction,probe.normal);
  for(unsigned i=0;i<4;i++)probe.segment[4+i]=(float)R((double)correction[i]+number(p,0x24+i*4));
  float *position=(float *)((char *)p+0x24);
  if(thug_collision_probe_query(&probe,1,0,q))for(unsigned i=0;i<4;i++)position[i]=(float)R((double)probe.point[i]+probe.normal[i]);
  else thug_vector_copy(position,probe.segment+4);
  thug_object_emit_event((void *)(uintptr_t)word(p,12),0x6e84acf3,NULL,d,m);
 }
 thug_collision_probe_release(&probe);
}
