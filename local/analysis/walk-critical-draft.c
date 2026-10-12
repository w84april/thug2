/* Candidate for the common Walk critical-point displacement and collision step. */
#include "../../src/collision/probe.h"
#include "../../src/core/vector.h"
#include "../../src/platform/diagnostics.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
#define R thug_platform_round_x87_single
/* 005278d0,772 bytes. Decay the offset, sweep its critical point, then apply the
 * stored limiting plane. The actual position receives collision corrections. */
void thug_walk_critical_point_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 float *offset=(float *)((char *)p+0x71c),*position=(float *)((char *)p+0x24);
 float squared=(float)R(R(R((double)offset[0]*offset[0])+R((double)offset[1]*offset[1]))+R((double)offset[2]*offset[2]));
 int32_t state=(int32_t)word(p,0x18);if(squared==0||state<0||(state>1&&state!=3))return;
 float previous[4];__builtin_memcpy(previous,offset,16);
 double amount=R((double)number(p,0x80)*1000),length=R(__builtin_sqrt(squared));
 if(amount<length){double factor=R(amount/length);for(unsigned i=0;i<4;i++)offset[i]=(float)R((double)offset[i]-R(factor*offset[i]));}
 else{offset[0]=offset[1]=offset[2]=0;offset[3]=1;}
 if(word(p,0x18)==3)return;
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 thug_vector_sum(probe.segment,(float *)((char *)p+0x68),previous);thug_vector_sum(probe.segment+4,position,offset);
 if(thug_collision_probe_query(&probe,1,0,query)){
  float scaled[4],target[4];thug_vector_scaled(scaled,.10000000149011612f,probe.normal);
  thug_vector_sum(target,probe.point,scaled);thug_vector_difference(previous,target,probe.segment+4);thug_vector_add(position,previous);
  diagnostics->print(diagnostics->context,"M:%s:%i: %s\n","mponents\\WalkComponent.cpp",0xb8c,"adjusting position due to bad critical point");
  diagnostics->print(diagnostics->context,"D:%s:%i: required_pos_adjustment = %g, %g, %g\n","mponents\\WalkComponent.cpp",0xb8d,(double)previous[0],(double)previous[1],(double)previous[2]);
  diagnostics->print(diagnostics->context,"D:%s:%i: m_critical_point_offset = %g, %g, %g\n","mponents\\WalkComponent.cpp",0xb8e,(double)offset[0],(double)offset[1],(double)offset[2]);
 }
 if(((uint8_t *)p)[0x18b0]){
  float sum[4],*normal=(float *)((char *)p+0x18b4);thug_vector_sum(sum,position,offset);
  double distance=R(R(R(R((double)sum[2]*normal[2])+R((double)sum[1]*normal[1]))+R((double)sum[0]*normal[0]))-number(p,0x18c4));
  float stored=(float)distance;if(distance>0){float correction[4];thug_vector_scaled(correction,stored,normal);thug_vector_subtract(position,correction);}
 }
 thug_collision_probe_release(&probe);
}
