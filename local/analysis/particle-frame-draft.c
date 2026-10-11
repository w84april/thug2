#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/script/lifetime.h"
#include "../../src/script/delivery.h"
#include "../../src/core/matrix.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static double r(double x){return thug_platform_round_x87_single(x);}
uint32_t thug_particle_suspend_half_counter_draft,thug_particle_suspend_quarter_counter_draft;
/* 00433e90. */
uint8_t thug_particle_suspend_far_draft(const void *p){return ((const uint8_t *)p)[0x30];}
/* 00433ea0. The optional output is stored before subsequent source reads;
 * counters still advance when the final forced-update override is enabled. */
uint8_t thug_particle_suspend_ready_draft(void *p,float *out){
 float distance=*fp(p,0x24);if(out)*out=distance;uint8_t ready=1;
 if(distance>r((double)*fp(p,0x34)**fp(p,0x34)))ready=0;
 else{
  float near=(float)thug_script_get_global_number(0xdb120fb5,0);
  double far=thug_script_get_global_number(0x3271aa80,0);float near_squared=(float)r((double)near*near);
  if(distance>r(far*far))ready=(++thug_particle_suspend_quarter_counter_draft&3)==0;
  else if(distance>near_squared)ready=(++thug_particle_suspend_half_counter_draft&1)==0;
 }
 return word(p,0x44)?1:ready;
}
/* 00496f60. Execution may change the retained slot; reload it before cleanup. */
void thug_particle_advance_setup_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 ThugScriptInstance *script=ptr(p,0xfc);
 if(script&&thug_script_execute(script,d,m)==0){
  script=ptr(p,0xfc);if(script){thug_script_destroy(script,d,m);thug_script_free(script,m);}put(p,0xfc,0);
 }
}
float *thug_matrix_euler_draft(float *,const float *);
/* 00497ab0. Snapshot angles before the output matrix can overwrite the effect. */
float *thug_particle_orientation_draft(void *p,float *out){
 float angles[4],matrix[16];for(unsigned i=0;i<3;i++)put(angles,i*4,word(p,0xe0+i*4));angles[3]=1;
 thug_matrix_euler_draft(matrix,angles);thug_matrix_copy(out,matrix);return out;
}
/* 00496970 / 004969b0. Raw position words, segment-major storage. Preserve
 * sequential loads/stores when getter outputs alias the source or one another. */
void thug_particle_position_get_draft(void *p,uint32_t index,uint32_t segment,uint32_t *x,uint32_t *y,uint32_t *z){
 void *position=(char *)ptr(p,0x11c)+(word(p,0x7c)*segment+index)*12;
 *x=word(position,0);*y=word(position,4);*z=word(position,8);
}
void thug_particle_position_set_draft(void *p,uint32_t index,uint32_t segment,uint32_t x,uint32_t y,uint32_t z){
 void *position=(char *)ptr(p,0x11c)+(word(p,0x7c)*segment+index)*12;
 put(position,0,x);put(position,4,y);put(position,8,z);
}
/* 00496c30. Keep both ordered maxima and the wide-exponent PC24 expression. */
void thug_particle_bounds_draft(void *p){
 double acceleration=__builtin_fabs(*fp(p,0xb0));
 double value=__builtin_fabs(*fp(p,0xac));if(value>acceleration)acceleration=value;
 value=__builtin_fabs(*fp(p,0xa8));if(value>acceleration)acceleration=value;
 double radius=r(r(acceleration**fp(p,0xcc))+*fp(p,0x94));
 for(unsigned i=0;i<4;i++)put(p,0x50+4*i,word(p,0x20+4*i));
 double extent=*fp(p,0xa0);value=*fp(p,0x9c);if(value>extent)extent=value;
 value=*fp(p,0x98);if(value>extent)extent=value;
 *fp(p,0x5c)=(float)r(r(r(radius**fp(p,0xcc))*60)+extent);
}
