/* Original Walk ground helpers, compared against the original executable.
 * The ground parent is an explicit partial prefix; it is not a recovered routine. */
#include "../../src/game/components.h"
#include "../../src/game/moving_contact.h"
#include "../../src/collision/moving.h"
#include "../../src/core/matrix.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
/* 0052a620,215 bytes. Move with the platform, then rotate and flatten facing. */
void thug_walk_follow_platform_draft(void *p,const ThugMemory *memory){
 ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *contact=gate->contact;
 if(!contact)return;
 if(!contact->reference.object||!thug_moving_contact_update(contact,(float *)((char *)p+0x24))){thug_skater_moving_contact_release(gate,memory);return;}
 contact=((ThugSkaterGroundGate *)ptr(p,0x1784))->contact;
 for(unsigned i=0;i<4;i++)fp(p,0x24+i*4,R((double)contact->displacement[i]+number(p,0x24+i*4)));
 contact=((ThugSkaterGroundGate *)ptr(p,0x1784))->contact;
 if(contact->orientation_changed){
  float rotated[4];thug_matrix_rotate_vector(contact->rotation,rotated,(float *)((char *)p+0x48));
  __builtin_memcpy((char *)p+0x48,rotated,16);
  if(number(p,0x4c)!=0){put(p,0x4c,0);thug_vector_normalize((float *)((char *)p+0x48));}
 }
}
/* 005277b0,281 bytes. Build the original collision cache around owner position. */
void thug_walk_prepare_cache_draft(void *p){
 float radius=(float)R((double)parameter(0x99978d2b)+1),above=parameter(0x9ea1974a),below=parameter(0xaf3e4251);
 float upper_y=(float)R((double)above+1),lower_y=(float)R((double)below+1);void *owner=ptr(p,12);
 float high[4],low[4];
 high[0]=(float)R((double)radius+number(owner,0x4c));high[1]=(float)R((double)upper_y+number(owner,0x50));high[2]=(float)R((double)radius+number(owner,0x54));high[3]=number(owner,0x58);
 low[0]=(float)R((double)number(owner,0x4c)-radius);low[1]=(float)R((double)number(owner,0x50)-lower_y);low[2]=(float)R((double)number(owner,0x54)-radius);low[3]=number(owner,0x58);
 ThugBounds bounds;thug_collision_segment_copy(bounds.min,low,high);
 ThugCollisionCache *cache=(void *)((char *)p+0x790);thug_collision_cache_build(cache,&bounds);thug_collision_default_cache=cache;
}
/* 00526260,464 bytes. Blend the facing direction toward normalized velocity. */
void thug_walk_face_velocity_draft(void *p){
 float speed=(float)thug_vector_length((float *)((char *)p+0x34));float threshold=parameter(0x0515a933);
 if(speed<threshold)return;
 float direction[4];__builtin_memcpy(direction,(char *)p+0x34,16);thug_vector_normalize(direction);
 float fast=parameter(0xe6c1cd0d);double factor;
 if(speed>fast)factor=R((double)parameter(0x7a583b9b)*number(p,0x80));
 else{
  fast=parameter(0xe6c1cd0d);threshold=parameter(0x0515a933);float rate=parameter(0x7a583b9b);
  double fraction=R(R((double)speed-threshold)/R((double)fast-threshold));factor=R(R((double)rate*number(p,0x80))*fraction);
 }
 float stored=(float)factor;
 if(factor>=1)__builtin_memcpy((char *)p+0x48,direction,16);
 else{
  float out[4];thug_vector_lerp(out,(float *)((char *)p+0x48),direction,stored);__builtin_memcpy((char *)p+0x48,out,16);thug_vector_normalize((float *)((char *)p+0x48));
 }
}
#include "../../src/core/timing.h"
#include "../../src/game/grind.h"
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void pb(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static double dot_zyx(const float a[4],const float b[4]){return R(R(R((double)a[2]*b[2])+R((double)a[1]*b[1]))+R((double)a[0]*b[0]));}
/* 00528120. Analog input chooses walking/running speed and preserves the
 * run flag on zero input. The running interpolation fraction spills to float. */
double thug_walk_target_speed_draft(void *p){
 float input=number(p,0x94);if(input==0)return 0;
 float split=parameter(0xc1528f7f);
 if(input<=split){pb(p,0x17a4,0);float walking=parameter(0x79d182ad);return R(R(R((double)input-.30000001192092896f)/R((double)split-.30000001192092896f))*walking);}
 pb(p,0x17a4,1);float walking=parameter(0x79d182ad);float fraction=(float)R(R((double)input-split)/R(1-(double)split));
 return R(R(R(thug_skater_transfer_speed(p)-walking)*fraction)+walking);
}
/* 00526430. Slope normal attenuates only speeds above ordinary walking. */
double thug_walk_slope_speed_draft(void *p,float speed,const float direction[4]){
 if(number(p,0x1798)>.949999988079071f)return speed;
 if(speed<=parameter(0x79d182ad))return speed;
 float normal[4]={number(p,0x1794),0,number(p,0x179c),number(p,0x17a0)};thug_vector_normalize(normal);
 double alignment=__builtin_fabs(dot_zyx(normal,direction));
 return R(R(R(1-alignment)+R(alignment*number(p,0x1798)))*speed);
}
/* 00528950. Full acceleration and steering, including a real sharp-turn
 * clearance probe. Shared collision services supply query scratch storage. */
void thug_walk_accelerate_draft(void *p,float velocity[4],ThugCollisionQuery *query){
 float speed=(float)thug_vector_length(velocity);double target_wide=thug_walk_target_speed_draft(p);float target=(float)target_wide;
 put(p,0x78,(target_wide<0||target_wide==0)?0x9b46e749:0xaf895b3f);
 float direction[4],movement[4];float threshold=parameter(0x8afb8788);
 if(speed>threshold)thug_vector_divided(direction,velocity,speed);
 else if(number(p,0x94)!=0)copy4(direction,(char *)p+0x84);
 else if(speed>.01f)thug_vector_divided(direction,velocity,speed);
 else copy4(direction,(char *)p+0x48);
 copy4(movement,direction);
 float *input=(void *)((char *)p+0x84),*facing=(void *)((char *)p+0x48);
 if(number(p,0x94)>0){
  double alignment=dot_zyx(direction,input);if(alignment<0||alignment==0)target=0;
  double angle_dot=dot_zyx(direction,facing);float cosine=(float)angle_dot;
  if(angle_dot>1)cosine=1;else if(cosine<-1)cosine=-1;
  float degrees=(float)__builtin_fabs(R(thug_platform_acos_x87_single(cosine)*57.2957763671875f));
  float max_angle=parameter(0xdb05e84e);
  if(degrees>max_angle){
   float rate=parameter(0xb557804b);float angle=(float)R(R(R(thug_frame_duration()*number(p,0x94))*rate)*.01745329238474369f);
   int negative=R(R((double)facing[0]*input[2])-R((double)input[0]*facing[2]))<0;
   if(!byte(p,0x17a4))angle=(float)R((double)parameter(0x7b446c98)*angle);
   if(byte(p,0x186c))angle=(float)R((double)parameter(0xe0456382)*angle);
   else{
    double signed_angle=negative?angle:-(double)angle,cos=thug_platform_cos(signed_angle),sin=thug_platform_sin(signed_angle);
    float x=(float)R(R(sin*facing[2])+R(cos*facing[0])),z=(float)R(R(cos*facing[2])-R(sin*facing[0]));
    ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);copy4(probe.segment,(char *)p+0x24);
    probe.segment[1]=(float)R((double)probe.segment[1]+parameter(0x6da7f696));
    float radius=parameter(0x99978d2b),zero=(float)R((double)radius*0),dx=(float)R((double)x*radius),dz=(float)R((double)z*radius);
    probe.segment[4]=(float)R((double)dx+probe.segment[0]);probe.segment[5]=(float)R((double)zero+probe.segment[1]);probe.segment[6]=(float)R((double)dz+probe.segment[2]);probe.segment[7]=(float)R((double)zero+probe.segment[3]);
    if(thug_collision_probe_query(&probe,0,0,query))angle=(float)R(thug_walk_parameter((uintptr_t)p,0xe0456382)*angle);
    if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
   }
   double signed_angle=negative?angle:-(double)angle,cos=thug_platform_cos(signed_angle),sin=thug_platform_sin(signed_angle);
   double x=R(R(sin*facing[2])+R(cos*facing[0]));float z=(float)R(R(cos*facing[2])-R(sin*facing[0]));
   facing[2]=z;facing[0]=(float)x;
   if(negative!=(R(R(x*input[2])-R((double)input[0]*facing[2]))<0))copy4(facing,input);
   copy4(movement,input);
  }else{
   double blend=R(R(1-dot_zyx(input,facing))*2);float weight=(float)blend;
   if(blend>1)weight=1;else if(weight<0)weight=0;
   float sharp=parameter(0x6cb2e5de),gentle=parameter(0xa26760f5);
   float rate=(float)R(R(R(R((double)sharp-gentle)*weight)+gentle)*number(p,0x94));
   double factor=R(thug_frame_duration()*rate);float stored=(float)factor;
   if(factor>=1)copy4(facing,input);
   else{float out[4];thug_vector_lerp(out,facing,input,stored);copy4(facing,out);thug_vector_normalize(facing);}
   copy4(movement,facing);
  }
 }
 fp(p,0x704,target);target=(float)thug_walk_slope_speed_draft(p,target,direction);
 double final_speed;
 if(speed>target){
  float rate=parameter(0xacfa4e0c);
  if(target==0){float walking=parameter(0x79d182ad);if(!(speed>walking))rate=parameter(0x0a2aa811);}
  final_speed=R(R(R(thug_frame_duration()*rate)*R((double)target-speed))+speed);
 }else{
  float rate=parameter(byte(p,0x17a4)?0x4f47c998:0x6590a49b);final_speed=R(R(thug_frame_duration()*rate)+speed);if(final_speed>target)final_speed=target;
 }
 for(unsigned i=0;i<4;i++)velocity[i]=(float)R((double)movement[i]*final_speed);
}
/* 005264f0. Two real probes estimate the step ahead and smooth its height. */
void thug_walk_step_height_draft(void *p,ThugCollisionQuery *query){
 float direction[4];copy4(direction,(char *)p+0x48);thug_vector_project_plane(direction,(float *)((char *)p+0x1794));
 if(direction[1]<0)direction[1]=0;
 double length=R(__builtin_sqrt(R(R(R((double)direction[2]*direction[2])+R((double)direction[0]*direction[0]))+R((double)direction[1]*direction[1]))));
 if(length>0){float inverse=(float)R(1/length);for(unsigned i=0;i<3;i++)direction[i]=(float)R((double)inverse*direction[i]);}
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 probe.segment[0]=number(p,0x24);probe.segment[1]=(float)R((double)number(p,0x28)+.5f);probe.segment[2]=number(p,0x2c);probe.segment[3]=0;
 float distance=parameter(0x11edcc52),dx=(float)R((double)direction[0]*distance),dy=(float)R((double)direction[1]*distance);
 probe.segment[4]=(float)R((double)dx+number(p,0x24));probe.segment[5]=(float)R(R((double)dy+number(p,0x28))+.5f);probe.segment[6]=(float)R(R((double)direction[2]*distance)+number(p,0x2c));probe.segment[7]=0;
 if(thug_collision_probe_query(&probe,1,0,query)){
  float first_fraction=probe.fraction;
  for(unsigned i=0;i<4;i++){
   double delta=R((double)direction[i]*.5f);if(i<3)delta=(float)delta;
   float v=(float)R(delta+probe.point[i]);probe.segment[i]=v;probe.segment[4+i]=v;
  }
  probe.segment[1]=(float)R((double)parameter(0xcee3a3e1)+number(p,0x28));
  if(thug_collision_probe_query(&probe,1,0,query)){
   float target=(float)R(R((double)probe.point[1]-number(p,0x28))*R(1-(double)first_fraction));
   int change=1;
   if(__builtin_fabs((double)number(p,0x714))<.01f&&number(p,0x94)==0){
    double minimum=thug_walk_parameter((uintptr_t)p,0x227d72ee);
    if(R(minimum*minimum)>thug_vector_length_squared((float *)((char *)p+0x34)))change=0;
   }
   if(change){float rate=parameter(0x856a80d3);double gain=R((double)rate*number(p,0x80));fp(p,0x714,R(R(R((double)target-number(p,0x714))*gain)+number(p,0x714)));}
   pb(p,0x718,1);
  }
 }
 if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
}
extern uint32_t *thug_skater_construction_boundary_draft;
/* PREFIX ONLY of0052d300: execute the original platform, cache and steering
 * sequence, then stop before the unrecovered transition/collision handler. */
void thug_walk_ground_prefix_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 (void)diagnostics;thug_walk_follow_platform_draft(p,memory);thug_walk_prepare_cache_draft(p);thug_walk_accelerate_draft(p,(float *)((char *)p+0x34),query);
 if(word(p,0x78)==0x1d537eff&&number(p,0x1870)<parameter(0x8e1cf27a))put(p,0x78,0x9b46e749);
 uint32_t *b=thug_skater_construction_boundary_draft;if(b){b[0]=0x52c2c0;b[1]=0;b[2]=(uintptr_t)p;b[3]=1;}__builtin_trap();
}
