/* 00527c50: airborne plane displacement and velocity projection. */
#include "../../src/core/vector.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t checksum){float value;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),checksum,&value,1);return value;}
static double dot(const float *a,const float *b){return R(R(R((double)a[2]*b[2])+R((double)a[1]*b[1]))+R((double)a[0]*b[0]));}
void thug_walk_air_plane_draft(void *p){
 if(!*((uint8_t *)p+0x18b0))return;
 if(number(p,0x28)>number(p,0x18c8)){*((uint8_t *)p+0x18b0)=0;return;}
 const float *normal=(const float *)((char *)p+0x18b4);
 float distance=(float)R(dot(normal,(const float *)((char *)p+0x24))-number(p,0x18c4));
 if(!(distance>-(double)parameter(0xa20c43b7)))return;
 double amount=R((double)parameter(0x4d16f37d)*number(p,0x80));
 double x=R(amount*normal[0]);float rest[3];
 for(unsigned i=0;i<3;i++)rest[i]=(float)R(amount*normal[i+1]);
 fp(p,0x24,R((double)number(p,0x24)-x));
 for(unsigned i=0;i<3;i++)fp(p,0x28+i*4,R((double)number(p,0x28+i*4)-rest[i]));
 float *velocity=(float *)((char *)p+0x34);
 if(dot(velocity,normal)!=0){float projected[4];thug_vector_scaled(projected,(float)dot(velocity,normal),normal);thug_vector_subtract(velocity,projected);}
}
