/* 00526850: steering relative to the airborne basis and inherited velocity. */
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
static double dot(float az,float bz,float ay,float by,float ax,float bx){return R(R(R((double)az*bz)+R((double)ay*by))+R((double)ax*bx));}
void thug_walk_air_steering_draft(void *p){
 if(number(p,0x1898)!=0){double t=R((double)number(p,0x1898)-number(p,0x80));fp(p,0x1898,t<0?0:t);return;}
 for(unsigned i=0;i<4;i++)fp(p,0x34+i*4,R((double)number(p,0x34+i*4)-number(p,0x1888+i*4)));
 float amount=number(p,0x94),side_x=-number(p,0x1880),side_z=number(p,0x1878);
 float maximum=parameter(0x896c8888);
 double direction=R(R(R((double)side_z*number(p,0x8c))+R((double)side_x*number(p,0x84)))+R((double)number(p,0x88)*0));
 float lateral_target=(float)R(R(direction*maximum)*amount);
 float lateral=(float)R(R(R((double)side_z*number(p,0x3c))+R((double)side_x*number(p,0x34)))+R((double)number(p,0x38)*0));
 float rate=parameter(0xf085443b);
 lateral=(float)R(R(R((double)lateral_target-lateral)*R((double)rate*number(p,0x80)))+lateral);
 maximum=parameter(0x896c8888);
 float target=(float)R(R(dot(number(p,0x8c),number(p,0x1880),number(p,0x88),number(p,0x187c),number(p,0x84),number(p,0x1878))*maximum)*amount);
 float forward=(float)dot(number(p,0x3c),number(p,0x1880),number(p,0x38),number(p,0x187c),number(p,0x34),number(p,0x1878));
 uint8_t locked=*((uint8_t *)p+0x1958);
 if(!locked&&amount==0){target=0;forward=0;}
 else{
  if(locked)lateral=0;
  if(target>=0&&forward>target)goto compose;
  if(target<0&&forward>0)target=(float)R((double)forward+target);
 }
 rate=parameter(0xf085443b);
 forward=(float)R(R(R((double)target-forward)*R((double)rate*number(p,0x80)))+forward);
compose:;
 double lateral_x=R((double)side_x*lateral),forward_x=R((double)forward*number(p,0x1878));
 float lateral_y=(float)R((double)lateral*0),lateral_z=(float)R((double)side_z*lateral);
 float forward_y=(float)R((double)forward*number(p,0x187c)),forward_z=(float)R((double)forward*number(p,0x1880)),forward_w=(float)R((double)forward*number(p,0x1884));
 fp(p,0x3c,R((double)forward_z+lateral_z));fp(p,0x40,R((double)forward_w+lateral));
 fp(p,0x34,R(forward_x+lateral_x));fp(p,0x38,R((double)forward_y+lateral_y));
 for(unsigned i=0;i<4;i++)fp(p,0x34+i*4,R((double)number(p,0x1888+i*4)+number(p,0x34+i*4)));
}
