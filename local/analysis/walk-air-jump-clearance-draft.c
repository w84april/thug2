/* 00529160: clear an overhead lip during a contact jump, retaining x87 spills. */
#include "../../src/game/stats.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
/* Invalid x87 arithmetic creates a negative indefinite. Existing NaNs retain
 * their sign, including the following FCHS in the displacement calculation. */
static double arithmetic(double a,double b,unsigned operation){
 if(__builtin_isnan(a))return a;if(__builtin_isnan(b))return b;
 double value=operation==0?a*b:operation==1?a/b:a-b;
 return __builtin_isnan(value)?-__builtin_nan(""):R(value);
}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
extern double thug_walk_gravity_draft(void);
void thug_walk_air_jump_clearance_draft(void *p,ThugCollisionQuery *q){
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 thug_vector_copy(probe.segment,(void *)((char *)p+0x24));
 probe.segment[1]=(float)R((double)probe.segment[1]+parameter(0x9ea1974a));
 thug_vector_copy(probe.segment+4,probe.segment);probe.segment[5]=(float)R((double)probe.segment[5]+parameter(0x48c0ac2a));
 if(thug_collision_probe_query(&probe,0,0,q)){
  float offset=parameter(0x06ebbab7),rise=(float)R((double)probe.point[1]-probe.segment[1]);
  for(unsigned i=0;i<4;i++)probe.segment[i]=(float)R((double)probe.segment[i]-R((double)offset*number(p,0x48+4*i)));
  for(unsigned i=0;i<4;i++)probe.segment[4+i]=(float)R((double)probe.segment[4+i]-R((double)offset*number(p,0x48+4*i)));
  if(!thug_collision_probe_query(&probe,0,0,q)){
   double gravity=thug_walk_gravity_draft(),velocity=number(p,0x44);
   double twice=R(gravity*rise);twice=R(twice+twice);
   double discriminant=R(R(velocity*velocity)-twice);float stored=(float)discriminant;
   if(discriminant>0){
    double inverse=R(1/gravity),time=arithmetic(R(velocity-R(__builtin_sqrt(stored))),inverse,0);
    double rate=-arithmetic(offset,time,1);float spilled=(float)rate;
    fp(p,0x18a8,arithmetic(rate,number(p,0x54),0));
    for(unsigned i=0;i<3;i++)fp(p,0x189c+4*i,arithmetic(spilled,number(p,0x48+4*i),0));
    fp(p,0x18ac,R((double)rise+number(p,0x28)));
    double duration=arithmetic(inverse,velocity,0);fp(p,0x1898,arithmetic(R(duration+duration),time,2));
   }
  }
 }
 thug_collision_probe_release(&probe);
}
