#include "../../src/game/components.h"
#include "../../src/script/registration.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void set(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static double r(double x){return thug_platform_round_x87_single(x);}
static uint8_t get(void *p,unsigned o,const ThugScriptStructure *s,uint32_t key){return thug_script_get_float(s,key,(float *)((char *)p+o),0);}
static void radians(void *p,unsigned o){set(p,o,(float)r((double)number(p,o)*0x1.1df46ap-6));}
/* 00423f10. Finite rotation chooses every rate's sign from its target angle. */
void thug_motion_rotation_direction_draft(void *p,uint32_t axis){
 unsigned o=axis*4;const unsigned offsets[]={0x15c,0x14c,0x16c,0x17c};
 for(unsigned i=0;i<4;i++)set(p,offsets[i]+o,__builtin_fabsf(number(p,offsets[i]+o)));
 if(number(p,0x12c+o)<0)for(unsigned i=0;i<4;i++)set(p,offsets[i]+o,-number(p,offsets[i]+o));
}
/* 00424b90 /00424d50 /00424f50. The original X command reverses its angle
 * under flag26af9dc9; Y and Z instead exchange axes. Rate precedence and
 * optional-value retention are shared by all three original bodies. */
static uint32_t rotate(void *p,const ThugScriptStructure *s,unsigned axis){
 if(word(p,0x18)&0x40)put(p,0x18,word(p,0x18)&0xffffffb8);
 float sign=1;
 if(thug_script_has_flag(s,0x26af9dc9)){if(axis==0)sign=-1;else axis=3-axis;}
 unsigned o=axis*4,angle=0x12c+o,velocity=0x15c+o,target=0x14c+o,accel=0x16c+o,brake=0x17c+o;
 put(p,brake,0);put(p,accel,0);put(p,angle,0);
 if(get(p,angle,s,0xff7ebaf6)){
  double converted=r((double)number(p,angle)*0x1.1df46ap-6);
  set(p,angle,(float)(axis==0?r(converted*sign):converted));
  put(p,0x1c,word(p,0x1c)&~(0x20u<<axis));put(p,0x13c+o,0);put(p,velocity,0);
  if(number(p,angle)==0){put(p,0x18,word(p,0x18)&~(1u<<axis));return 1;}
 }
 if(get(p,brake,s,0xf59ff7d7)){
  radians(p,brake);if(get(p,target,s,0xf0d90109))radians(p,target);
 }else if(get(p,accel,s,0x85894a84)){
  radians(p,accel);if(get(p,target,s,0xf0d90109))radians(p,target);
  if(!(word(p,0x18)&(1u<<axis)))put(p,velocity,0);
 }else if(get(p,velocity,s,0xf0d90109))radians(p,velocity);
 if(number(p,angle)==0&&number(p,brake)==0)put(p,0x1c,word(p,0x1c)|(0x20u<<axis));
 if(!(word(p,0x1c)&(0x20u<<axis)))thug_motion_rotation_direction_draft(p,axis);
 put(p,0x18,word(p,0x18)|(1u<<axis));return 1;
}
uint32_t thug_motion_rotate_x_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return rotate(p,s,0);}
uint32_t thug_motion_rotate_y_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return rotate(p,s,1);}
uint32_t thug_motion_rotate_z_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return rotate(p,s,2);}

/* The complete original Motion table is retained. Unrecovered members trap at
 * distinct, named boundaries; none pretend to implement their game behavior. */
uint32_t *thug_motion_rotation_command_boundary_draft;
static uint32_t unavailable(uint32_t address,void *p,ThugScriptStructure *s){
 if(thug_motion_rotation_command_boundary_draft){uint32_t *b=thug_motion_rotation_command_boundary_draft;b[0]=address;b[1]=(uintptr_t)p;b[2]=(uintptr_t)s;b[3]=1;}__builtin_trap();
}
uint32_t thug_motion_unavailable_00423160_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423160,p,s);}
uint32_t thug_motion_unavailable_00423170_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423170,p,s);}
uint32_t thug_motion_unavailable_00423180_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423180,p,s);}
uint32_t thug_motion_unavailable_00423190_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423190,p,s);}
uint32_t thug_motion_unavailable_004231a0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4231a0,p,s);}
uint32_t thug_motion_unavailable_00423210_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423210,p,s);}
uint32_t thug_motion_unavailable_00423280_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423280,p,s);}
uint32_t thug_motion_unavailable_004232f0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4232f0,p,s);}
uint32_t thug_motion_unavailable_00423360_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423360,p,s);}
uint32_t thug_motion_unavailable_004233a0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4233a0,p,s);}
uint32_t thug_motion_unavailable_004233e0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4233e0,p,s);}
uint32_t thug_motion_unavailable_00423480_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423480,p,s);}
uint32_t thug_motion_unavailable_00423490_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423490,p,s);}
uint32_t thug_motion_unavailable_004234b0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4234b0,p,s);}
uint32_t thug_motion_unavailable_004234d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4234d0,p,s);}
uint32_t thug_motion_unavailable_004234f0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4234f0,p,s);}
uint32_t thug_motion_unavailable_004237d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4237d0,p,s);}
uint32_t thug_motion_unavailable_00423810_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423810,p,s);}
uint32_t thug_motion_unavailable_00423830_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423830,p,s);}
uint32_t thug_motion_unavailable_00423890_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423890,p,s);}
uint32_t thug_motion_unavailable_004238d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4238d0,p,s);}
uint32_t thug_motion_unavailable_004239f0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4239f0,p,s);}
uint32_t thug_motion_unavailable_00423b30_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x423b30,p,s);}
uint32_t thug_motion_unavailable_00425150_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x425150,p,s);}
uint32_t thug_motion_unavailable_004251c0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4251c0,p,s);}
uint32_t thug_motion_unavailable_00425220_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x425220,p,s);}
uint32_t thug_motion_unavailable_00425270_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x425270,p,s);}
uint32_t thug_motion_unavailable_00425290_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x425290,p,s);}
uint32_t thug_motion_unavailable_004252c0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4252c0,p,s);}
uint32_t thug_motion_unavailable_00426770_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x426770,p,s);}
uint32_t thug_motion_unavailable_00426790_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x426790,p,s);}
uint32_t thug_motion_unavailable_004267b0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4267b0,p,s);}
uint32_t thug_motion_unavailable_004267d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4267d0,p,s);}
uint32_t thug_motion_unavailable_00426810_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x426810,p,s);}
uint32_t thug_motion_unavailable_00426880_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x426880,p,s);}
uint32_t thug_motion_unavailable_004268a0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4268a0,p,s);}
uint32_t thug_motion_unavailable_004268c0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4268c0,p,s);}
uint32_t thug_motion_unavailable_00426960_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x426960,p,s);}
uint32_t thug_motion_unavailable_004272d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4272d0,p,s);}
uint32_t thug_motion_unavailable_00427320_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x427320,p,s);}
uint32_t thug_motion_unavailable_004273d0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4273d0,p,s);}
uint32_t thug_motion_unavailable_00427470_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x427470,p,s);}
uint32_t thug_motion_unavailable_00427490_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x427490,p,s);}
uint32_t thug_motion_unavailable_004274b0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4274b0,p,s);}
uint32_t thug_motion_unavailable_004276a0_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)script;return unavailable(0x4276a0,p,s);}
typedef uint32_t (*MotionMember)(void *,ThugScriptStructure *,ThugScriptInstance *);
typedef struct {uint32_t name,type;MotionMember member;uint32_t adjustment,reserved,flags;} MotionDescriptor;
MotionDescriptor thug_motion_rotation_descriptors_draft[49]={
{0x21accf0d,0xa015e17,0x0,0x0,0x0,0x0},
{0x7bc461ae,0xa015e17,0x0,0x0,0x0,0x0},
{0x8e52abea,0xa015e17,0x0,0x0,0x0,0x0},
{0xc8cc6820,0xa015e17,0x0,0x0,0x0,0x0},
{0x68e1f022,0xa015e17,0x0,0x0,0x0,0x0},
{0xdfbe3db3,0xa015e17,0x0,0x0,0x0,0x0},
{0xfb603ea9,0xa015e17,0x0,0x0,0x0,0x0},
{0x2ca63cdf,0xa015e17,0x0,0x0,0x0,0x0},
{0xd6697ad0,0xa015e17,0x0,0x0,0x0,0x0},
{0xa67fc783,0xa015e17,0x0,0x0,0x0,0x0},
{0x5cf1b7d4,0xa015e17,0x0,0x0,0x0,0x0},
{0xb231a9d,0xa015e17,0x0,0x0,0x0,0x0},
{0x7c242a0b,0xa015e17,0x0,0x0,0x0,0x0},
{0xe52d7bb1,0xa015e17,0x0,0x0,0x0,0x0},
{0xd8f4bc32,0xa015e17,0x0,0x0,0x0,0x0},
{0xaa3cb476,0xa015e17,0x0,0x0,0x0,0x0},
{0xb75589ce,0xa015e17,0x0,0x0,0x0,0x0},
{0x6866312f,0xa015e17,0x0,0x0,0x0,0x0},
{0x434ea1fb,0xa015e17,0x0,0x0,0x0,0x0},
{0x76003d82,0xa015e17,0x0,0x0,0x0,0x0},
{0xbfb0031d,0xa015e17,0x0,0x0,0x0,0x0},
{0x33e04032,0xa015e17,0x0,0x0,0x0,0x0},
{0x103bd253,0xa015e17,0x0,0x0,0x0,0x0},
{0x6419ceff,0xa015e17,0x0,0x0,0x0,0x0},
{0xa5a2d218,0xa015e17,0x0,0x0,0x0,0x0},
{0x74c30242,0xa015e17,0x0,0x0,0x0,0x0},
{0xe8d121cb,0xa015e17,0x0,0x0,0x0,0x0},
{0x33df698f,0xa015e17,0x0,0x0,0x0,0x0},
{0xfe71453f,0xa015e17,0x0,0x0,0x0,0x0},
{0xbd6c6807,0xa015e17,0x0,0x0,0x0,0x0},
{0xda2d86d,0xa015e17,0x0,0x0,0x0,0x0},
{0xcc19c48a,0xa015e17,0x0,0x0,0x0,0x0},
{0x8b669799,0xa015e17,0x0,0x0,0x0,0x0},
{0xf389285d,0xa015e17,0x0,0x0,0x0,0x0},
{0x5ce058fd,0xa015e17,0x0,0x0,0x0,0x0},
{0x84ec6600,0xa015e17,0x0,0x0,0x0,0x0},
{0xea81a32b,0xa015e17,0x0,0x0,0x0,0x0},
{0x3bcaac3f,0xa015e17,0x0,0x0,0x0,0x0},
{0xc5eca638,0xa015e17,0x0,0x0,0x0,0x0},
{0x1e094b84,0xa015e17,0x0,0x0,0x0,0x0},
{0xbdc4c878,0xa015e17,0x0,0x0,0x0,0x0},
{0xdbfdd02f,0xa015e17,0x0,0x0,0x0,0x0},
{0x8d95f1e1,0xa015e17,0x0,0x0,0x0,0x0},
{0x3407ad3d,0xa015e17,0x0,0x0,0x0,0x0},
{0xe606eba2,0xa015e17,0x0,0x0,0x0,0x0},
{0xe76d73d2,0xa015e17,0x0,0x0,0x0,0x0},
{0x1ae46261,0xa015e17,0x0,0x0,0x0,0x0},
{0x2fad370d,0xa015e17,0x0,0x0,0x0,0x0},
{0x0,0xa015e17,0x0,0x0,0x0,0x0}};
/* 00640e30. Initialize all original member identities and sentinel fields. */
void thug_motion_rotation_descriptors_initialize_draft(void){
 const MotionMember members[]={thug_motion_unavailable_00423160_draft,thug_motion_unavailable_00423170_draft,thug_motion_unavailable_004237d0_draft,thug_motion_unavailable_00423810_draft,thug_motion_unavailable_00423180_draft,thug_motion_unavailable_00423190_draft,thug_motion_unavailable_004231a0_draft,thug_motion_unavailable_00423210_draft,thug_motion_unavailable_00423280_draft,thug_motion_unavailable_004232f0_draft,thug_motion_unavailable_00426770_draft,thug_motion_rotate_x_command_draft,thug_motion_rotate_y_command_draft,thug_motion_rotate_z_command_draft,thug_motion_unavailable_00423360_draft,thug_motion_unavailable_00423830_draft,thug_motion_unavailable_00425150_draft,thug_motion_unavailable_00423890_draft,thug_motion_unavailable_004233a0_draft,thug_motion_unavailable_004251c0_draft,thug_motion_unavailable_00425220_draft,thug_motion_unavailable_004276a0_draft,thug_motion_unavailable_00426790_draft,thug_motion_unavailable_004267b0_draft,thug_motion_unavailable_004267d0_draft,thug_motion_unavailable_00426810_draft,thug_motion_unavailable_00426880_draft,thug_motion_unavailable_004268a0_draft,thug_motion_unavailable_004233e0_draft,thug_motion_unavailable_00423480_draft,thug_motion_unavailable_00425270_draft,thug_motion_unavailable_00425290_draft,thug_motion_unavailable_004272d0_draft,thug_motion_unavailable_00427320_draft,thug_motion_unavailable_004273d0_draft,thug_motion_unavailable_00427470_draft,thug_motion_unavailable_00427490_draft,thug_motion_unavailable_004274b0_draft,thug_motion_unavailable_004268c0_draft,thug_motion_unavailable_00423490_draft,thug_motion_unavailable_004234b0_draft,thug_motion_unavailable_004234d0_draft,thug_motion_unavailable_004234f0_draft,thug_motion_unavailable_00426960_draft,thug_motion_unavailable_004238d0_draft,thug_motion_unavailable_004239f0_draft,thug_motion_unavailable_00423b30_draft,thug_motion_unavailable_004252c0_draft,0};
 for(unsigned i=0;i<49;i++){MotionDescriptor *p=&thug_motion_rotation_descriptors_draft[i];p->member=members[i];p->adjustment=p->reserved=0;p->flags=i==48?0xffffffff:0;}
}
/* 00423130. Register the complete table with its original component type. */
void thug_motion_rotation_descriptors_register_draft(const ThugMemory *m){thug_script_register_commands(0x0a015e17,thug_motion_rotation_descriptors_draft,24,m);}
