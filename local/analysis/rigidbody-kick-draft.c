#include "../../src/game/components.h"
#include "../../src/core/checksum.h"
#include "../../src/core/random.h"
#include "../../src/core/timing.h"
#include "../../src/collision/scene.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static double r(double x){return thug_platform_round_x87_single(x);}
static double invalid(double x){return __builtin_isnan(x)?-__builtin_nan(""):r(x);}
static double nan_operand(double a,double b){if(!__builtin_isnan(a))return b;if(!__builtin_isnan(b))return a;return !__builtin_signbit(a)?a:b;}
static double mul(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a*b);}
static double add(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a+b);}
static double sub(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a-b);}
static double divide(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a/b);}
static double root(double a){return __builtin_isnan(a)?a:invalid(__builtin_sqrt(a));}
/* Original eight reference records695150 and radii6939b0. The two trailing
 * words in each reference are owned by the reference machinery, not this call. */
uint32_t thug_rigidbody_skater_references_draft[8][3];
float thug_rigidbody_skater_radii_draft[8];
uint32_t thug_rigidbody_kick_sound_time_draft; /* 006939d8 */
extern uint32_t thug_rigidbody_initialization_constant_draft;
extern void thug_geometry_set_enabled_draft(void *,uint32_t);
extern void thug_object_sound_parameters_draft(void *,const ThugScriptStructure *);
/* 0048c770. The initialized list always includes a terminal sentinel. */
ThugCollisionScene *thug_scene_first_ordinary_draft(void){
 ThugCollisionSceneNode *node=thug_collision_scene_list;
 if(node->scene==(ThugCollisionScene *)(uintptr_t)UINT32_MAX)return 0;
 while(node){
  ThugCollisionSceneNode *next=node->next;
  if(next->scene==(ThugCollisionScene *)(uintptr_t)UINT32_MAX)next=0;
  ThugCollisionScene *scene=node->scene;
  if(!((const uint8_t *)scene)[0x8d])return scene;
  node=next;
 }
 return 0;
}
/* 0042c140. Complete skater/prop kick, with original reverse reference order,
 * float spills, activation, attached script, shadow and Sound side effects.
 * x87 PC24 retains a wide exponent between the explicit float stores. */
void thug_rigidbody_kick_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 for(unsigned i=8;i;){--i;
  void *skater=(void *)(uintptr_t)thug_rigidbody_skater_references_draft[i][0];
  if(!skater)continue;
  float radius=thug_rigidbody_skater_radii_draft[i];
  double extent=add(radius,*fp(p,0x40));
  double dz=sub(*fp(p,0x118),*fp(skater,0x54)),dx=sub(*fp(p,0x110),*fp(skater,0x4c));
  if(mul(extent,extent)<add(mul(dx,dx),mul(dz,dz)))continue;
  float dy=(float)sub(*fp(skater,0x50),*fp(p,0x114));
  if(add(radius,*fp(p,0x44))<dy)continue;
  float height;__builtin_memcpy(&height,&thug_rigidbody_initialization_constant_draft,4);
  if(-add(add(height,*fp(p,0x44)),radius)>dy)continue;
  float awayx=(float)sub(*fp(p,0x110),*fp(skater,0x4c));
  double awayz=sub(*fp(p,0x118),*fp(skater,0x54));
  double scale=divide(1,root(add(mul(awayz,awayz),mul(awayx,awayx))));
  awayx=(float)mul(awayx,scale);float az=(float)mul(awayz,scale);
  float vx=(float)sub(*fp(skater,0xac),*fp(p,0x120));
  double vy=sub(*fp(skater,0xb0),*fp(p,0x124));
  float vz=(float)sub(*fp(skater,0xb4),*fp(p,0x128));
  if(__builtin_fabs(vx)<=0.009999999776482582f&&__builtin_fabs(vy)<=0.009999999776482582f&&__builtin_fabs(vz)<=0.009999999776482582f)return;
  double strength=add(add(__builtin_fabs(mul(vy,0.3333333432674408f)),mul(vx,awayx)),mul(vz,az));
  if(strength<=0)continue; /* Original unordered comparison also enters. */
  if(strength>100)strength=add(strength,51);
  else if(strength>50)strength=add(add(strength,sub(strength,50)),50);
  else strength=add(strength,strength);
  double length=root(add(mul(vx,vx),mul(vz,vz)));if(length==0)length=0.009999999776482582f;
  scale=divide(1,length);
  float ix=(float)add(mul(vx,scale),awayx);
  double iz=add(mul(scale,vz),az);
  length=root(add(mul(ix,ix),mul(iz,iz)));if(length==0)length=0.009999999776482582f;
  scale=divide(1,length);
  float normalizedz=(float)mul(iz,scale);
  ix=(float)mul(mul(ix,scale),*fp(p,0x48));
  float impulsez=(float)mul(normalizedz,*fp(p,0x48));
  strength=mul(strength,*fp(p,0x50));
  ix=(float)mul(ix,strength);float iy=(float)mul(*fp(p,0x4c),strength);impulsez=(float)mul(impulsez,strength);
  double armx=sub(*fp(skater,0x4c),*fp(p,0x110));
  float armz=(float)sub(*fp(skater,0x54),*fp(p,0x118));
  length=root(add(mul(armx,armx),mul(armz,armz)));
  if(length>0){scale=divide(*fp(p,0x44),length);armx=mul(armx,scale);armz=(float)mul(armz,scale);}
  double army=dy>0?sub(*fp(skater,0x50),*fp(p,0x114))
    :(-height>dy?sub(add(height,*fp(skater,0x50)),*fp(p,0x114)):-12);
  *fp(p,0x120)=(float)add(ix,*fp(p,0x120));*fp(p,0x124)=(float)add(iy,*fp(p,0x124));
  *fp(p,0x128)=(float)add(impulsez,*fp(p,0x128));*fp(p,0x12c)=(float)add(strength,*fp(p,0x12c));
  float tx=(float)sub(mul(impulsez,army),mul(armz,iy));
  float ty=(float)sub(mul(armz,ix),mul(impulsez,armx));
  double tz=sub(mul(iy,armx),mul(army,ix));
  scale=mul(mul(*fp(p,0x54),*fp(p,0x18)),0.6000000238418579f);
  float ax=(float)mul(tx,scale),ay=(float)mul(ty,scale),azv=(float)mul(tz,scale);
  *fp(p,0x140)=(float)add(ax,*fp(p,0x140));*fp(p,0x144)=(float)add(ay,*fp(p,0x144));
  *fp(p,0x148)=(float)add(azv,*fp(p,0x148));*fp(p,0x14c)=(float)add(mul(scale,0),*fp(p,0x14c));
  if(word(p,0x10c)!=1){__builtin_memcpy((char *)p+0xf8,(char *)ptr(p,12)+0x4c,16);put(p,0x10c,1);}
  put(p,0x194,word(p,0xc0));
  if(word(p,0xc4))thug_script_execute(thug_object_spawn_attached_script(ptr(p,12),word(p,0xc4),ptr(p,0xd4),0,0,d,m),d,m);
  uint32_t name=thug_crc32_extend_string(word(ptr(p,12),0x14),"_Shadow");
  void *shadow=thug_scene_find_object(thug_scene_first_ordinary_draft(),name);
  if(shadow)thug_geometry_set_enabled_draft(shadow,0);
  uint32_t time=thug_frame_time();
  if((int32_t)(time-word(p,0xf0))<=0||(int32_t)(time-thug_rigidbody_kick_sound_time_draft)<=0)return;
  if(!word(p,0x19c)||!word(p,0xd8))return;
  float intensity=(float)mul(root(add(add(mul(ix,ix),mul(impulsez,impulsez)),mul(iy,iy))),0.10000000149011612f);
  thug_script_set_float_bits(ptr(p,0xd8),0x9e497fc6,word(&intensity,0),m);
  thug_object_sound_parameters_draft(ptr(p,0x19c),ptr(p,0xd8));
  uint32_t delay=((uint32_t)(thug_random_range(100)+50)*word(p,0xe0))/100;
  put(p,0xf0,delay+thug_frame_time());
  delay=((uint32_t)(thug_random_range(100)+50)*word(p,0xe4))/100;
  thug_rigidbody_kick_sound_time_draft=delay+thug_frame_time();return;
 }
}
