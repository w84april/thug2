#include "../../src/game/components.h"
#include "../../src/core/timing.h"
#include "../../src/core/number.h"
#include "../../src/audio/device.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const char *)p+o,2);return v;}
static double r(double x){return thug_platform_round_x87_single(x);}
/* Finite input overflows can create the x87 indefinite NaN. Retain its sign,
 * including FCHS, and prefer the positive canonical NaN when both signs meet. */
static double invalid(double x){return __builtin_isnan(x)?-__builtin_nan(""):r(x);}
static double nan_operand(double a,double b){if(!__builtin_isnan(a))return b;if(!__builtin_isnan(b))return a;return !__builtin_signbit(a)?a:b;}
static double mul(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a*b);}
static double add(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a+b);}
static double sub(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a-b);}
static double divide(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a/b);}
static double root(double a){return __builtin_isnan(a)?a:invalid(__builtin_sqrt(a));}
extern float thug_rigidbody_rotated_contacts_draft[2][4];
/* 0042cee0. Effective contact mass; preserve the original x87 float spills. */
static double contact_inverse(void *p,const double n[3],const float *v){
 double cx=sub(mul(v[1],n[2]),mul(v[2],n[1]));
 double cy=sub(mul(n[0],v[2]),mul(v[0],n[2]));
 float cz=(float)sub(mul(v[0],n[1]),mul(n[0],v[1]));
 float ax=(float)mul(cx,*fp(p,0x18));double ay=mul(cy,*fp(p,0x18)),az=mul(cz,*fp(p,0x18));
 float bx=(float)sub(mul(ay,v[2]),mul(az,v[1]));
 double by=sub(mul(az,v[0]),mul(ax,v[2]));
 float bz=(float)sub(mul(ax,v[1]),mul(ay,v[0]));
 float x=(float)add(bx,n[0]);double y=add(by,n[1]),z=add(bz,n[2]);
 return divide(1,add(add(mul(x,n[0]),mul(z,n[2])),mul(y,n[1])));
}
double thug_rigidbody_contact_inverse_draft(void *p,const float n[4],const float v[4]){double d[]={n[0],n[1],n[2]};return contact_inverse(p,d,v);}
/* Comparison ABI only: retain every return bit across JavaScript, including NaN. */
uint64_t thug_rigidbody_contact_inverse_bits_draft(void *p,const float n[4],const float v[4]){double value=thug_rigidbody_contact_inverse_draft(p,n,v);uint64_t bits;__builtin_memcpy(&bits,&value,8);return bits;}
/* 0042cf90. Full attached-contact constraint loop and positional correction.
 * Internal shape arrays are disjoint, with the original capacity of two. */
void thug_rigidbody_constraints_draft(void *p){
 for(unsigned iteration=0;;){
  uint8_t settled=1;
  for(unsigned i=half(p,0x9c);i;){--i;void *c=(char *)ptr(p,0x98)+36*i;if(!((uint8_t *)c)[32])continue;
   float *v=thug_rigidbody_rotated_contacts_draft[i],*linear=fp(p,0x120),*angular=fp(p,0x140);
   double crossx=sub(mul(v[2],angular[1]),mul(v[1],angular[2]));
   double crossy=sub(mul(angular[2],v[0]),mul(v[2],angular[0]));
   float crossz=(float)sub(mul(v[1],angular[0]),mul(angular[1],v[0]));
   float velocity[4]={(float)add(crossx,linear[0]),(float)add(crossy,linear[1]),(float)add(crossz,linear[2]),linear[3]};
   double length=root(add(add(mul(velocity[2],velocity[2]),mul(velocity[1],velocity[1])),mul(velocity[0],velocity[0])));
   float speed=(float)length;if(length<0.10000000149011612f)continue;
   settled=0;double scale=divide(1,speed),normal[3]={mul(velocity[0],scale),(float)mul(velocity[1],scale),(float)mul(velocity[2],scale)};
   float nw=(float)mul(velocity[3],scale),impulse=(float)-mul(contact_inverse(p,normal,v),speed);
   double dv[4]={mul(normal[0],impulse),mul(normal[1],impulse),mul(normal[2],impulse),mul(nw,impulse)};
   for(unsigned j=0;j<4;j++)linear[j]=(float)add(dv[j],linear[j]);
   float tx=(float)sub(mul(dv[2],v[1]),mul(dv[1],v[2]));
   float ty=(float)sub(mul(dv[0],v[2]),mul(dv[2],v[0]));
   double tz=sub(mul(dv[1],v[0]),mul(dv[0],v[1]));
   float da[3]={(float)mul(tx,*fp(p,0x18)),(float)mul(ty,*fp(p,0x18)),(float)mul(tz,*fp(p,0x18))};
   for(unsigned j=0;j<3;j++)angular[j]=(float)add(da[j],angular[j]);angular[3]=(float)add(mul(*fp(p,0x18),0),angular[3]);
  }
  if(++iteration==20||half(p,0x9c)==1||settled)break;
 }
 float dt=(float)thug_frame_duration();
 for(unsigned i=half(p,0x9c);i;){--i;float *c=(float *)((char *)ptr(p,0x98)+36*i);if(!((uint8_t *)c)[32])continue;
  float *v=thug_rigidbody_rotated_contacts_draft[i],*position=fp(p,0x110),*linear=fp(p,0x120),*angular=fp(p,0x140);
  float dx=(float)sub((float)add(position[0],v[0]),c[4]),dy=(float)sub(add(position[1],v[1]),c[5]);
  double dz=sub(add(position[2],v[2]),c[6]);float dw=(float)sub((float)add(position[3],v[3]),c[7]);
  float distance=(float)root(add(add(mul(dx,dx),mul(dz,dz)),mul(dy,dy)));if(distance==0)continue;
  double scale=divide(1,distance),nx=mul(dx,scale);float ny=(float)mul(dy,scale),nz=(float)mul(dz,scale),nw=(float)mul(dw,scale);
  double amount=mul(mul(mul(distance,*fp(p,0x34)),dt),-10),dvx=mul(nx,amount),dvy=mul(ny,(float)amount);
  float dvz=(float)mul(nz,(float)amount),dvw=(float)mul(nw,(float)amount);
  double tx=sub(mul(dvz,v[1]),mul(dvy,v[2])),ty=sub(mul(dvx,v[2]),mul(dvz,v[0]));float tz=(float)sub(mul(dvy,v[0]),mul(dvx,v[1]));
  float da[4]={(float)mul(tx,*fp(p,0x18)),(float)mul(ty,*fp(p,0x18)),(float)mul(tz,*fp(p,0x18)),(float)mul(*fp(p,0x18),0)};
  linear[0]=(float)add(dvx,linear[0]);linear[1]=(float)add(dvy,linear[1]);linear[2]=(float)add(dvz,linear[2]);linear[3]=(float)add(dvw,linear[3]);
  for(unsigned j=0;j<4;j++)angular[j]=(float)add(da[j],angular[j]);
 }
}
/* 0047ac10. Checksum names select the original four attenuation curves. */
uint32_t thug_sound_curve_draft(uint32_t name){return name==0x0ca64c41?3:name==0x9706104b?2:name==0xf221474c?1:0;}
/* 004680e0. Initialized hash table; continue past matching empty entries. */
extern ThugObjectLookupTable *thug_emitter_table_draft; /* Existing006f2260. */
void *thug_sound_volume_find_draft(uint32_t name){
 void *t=thug_emitter_table_draft;uint32_t mask=(1u<<(word(t,0)&31))-1;
 void *node=(char *)ptr(t,4)+(name&mask)*12;
 while(node){if(word(node,0)==name&&word(node,4))return ptr(node,4);node=ptr(node,8);}return 0;
}
/* 0047afe0. Count physical active slots using the original device accessor. */
uint32_t thug_sound_active_count_draft(const ThugSoundConfiguration *config){(void)config;uint32_t n=0;for(unsigned i=0;i<48;i++)if(thug_audio_slot_active(i))++n;return n;}
/* 0048d090. The concrete PC Sound notification virtual is exactly RET 12. */
void thug_sound_notification_draft(void *p,uint32_t name,float volume,float pitch){(void)p;(void)name;(void)volume;(void)pitch;}
uint32_t thug_object_sound_play_draft(const ThugSoundConfiguration *,uint32_t,const ThugSoundPlaybackControls *,void *,uint32_t,uint32_t);
/* 00433240. Resolve all named sound parameters before actual owned playback. */
void thug_object_sound_parameters_draft(void *p,const ThugScriptStructure *s){
 uint32_t name=0,curve=0,detached=0;float volume=100,pitch=100,distance=0;
 thug_script_get_checksum(s,0,&name,0);thug_script_get_float(s,0xf6a36814,&volume,0);thug_script_get_float(s,0xd8604126,&pitch,0);
 if(thug_script_has_name_or_flag(s,0x9e497fc6)){
  float maxvolume=100,minvolume=0,maxpitch=100,minpitch=100,strength;
  thug_script_get_float(s,0x0693daaf,&maxvolume,0);thug_script_get_float(s,0x4391992d,&minvolume,0);
  thug_script_get_float(s,0xfa3e14c5,&maxpitch,0);thug_script_get_float(s,0x1c5ebb24,&minpitch,0);thug_script_get_float(s,0x9e497fc6,&strength,1);
  double factor=mul(strength,0.009999999776482582f);volume=(float)add(mul(sub(maxvolume,minvolume),factor),minvolume);pitch=(float)add(mul(sub(maxpitch,minpitch),factor),minpitch);
 }
 if(thug_script_get_float(s,0xff2020ec,&distance,0))distance=(float)mul(distance,12);
 uint32_t value;if(thug_script_get_checksum(s,0x0c6ac50a,&value,0))curve=thug_sound_curve_draft(value);
 if(thug_script_has_flag(s,0xbb39837f))detached=1;
 put(p,0xb8,thug_script_get_checksum(s,0x8a7132ce,&value,0)?(uintptr_t)thug_sound_volume_find_draft(value):0);
 if(!name){uint32_t slot=0xffffffff;thug_script_get_integer(s,0x7321a8d6,&slot,0);if(slot==0xffffffff||(int32_t)slot>8)return;name=word(p,0x18+slot*4);if(!name)return;}
 typedef void (*Notify)(void *,uint32_t,float,float);((Notify *)ptr(p,0))[13](p,name,volume,pitch);
 ThugSoundPlaybackControls controls={word(&pitch,0),word(&volume,0),word(&distance,0),curve};thug_object_sound_play_draft(thug_sound_configuration,name,&controls,p,detached,0);
}
/* 0042e980. Real attached impact script, owned parameter copy and sound gates. */
void thug_rigidbody_impact_draft(void *p,float speed,const float position[4],const ThugDiagnostics *d,const ThugMemory *m){
 if(!(speed>*fp(p,0xe8)))return;
 if(word(p,0xc8)){
  ThugScriptStructure *s=thug_script_structure_allocate(8,m);if(s)thug_script_structure_initialize(s);
  if(word(p,0xd4))thug_script_structure_merge(s,ptr(p,0xd4),m);
  thug_script_set_vector_bits(s,0x43f454d0,word(position,0),word(position,4),word(position,8),m);
  thug_script_execute(thug_object_spawn_attached_script(ptr(p,12),word(p,0xc8),s,0,0,d,m),d,m);
  if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
 }
 if(!word(p,0x19c)||!word(p,0xdc))return;
 if((int32_t)(48-thug_sound_active_count_draft(thug_sound_configuration))<=12)return;
 float value=(float)thug_clamp_number((float)mul(divide(speed,*fp(p,0xec)),100),0,100);
 thug_script_set_float_bits(ptr(p,0xdc),0x9e497fc6,word(&value,0),m);thug_object_sound_parameters_draft(ptr(p,0x19c),ptr(p,0xdc));
}
/* 00430be0. Full collision response, tangent friction and original impact path. */
void thug_rigidbody_response_draft(void *p,void *feeler,const ThugDiagnostics *d,const ThugMemory *m){
 float *v=fp(p,0x120),*n=fp(feeler,0x88);
 double normal=add(add(mul(v[2],n[2]),mul(v[1],n[1])),mul(v[0],n[0])),amount=-mul(add(*fp(p,0x2c),1),normal);
 float bounce[3]={(float)mul(amount,n[0]),(float)mul(amount,n[1]),(float)mul(amount,n[2])};double bw=mul(amount,n[3]);
 float tangentx=(float)sub(v[0],mul(normal,n[0])),tangentz=(float)sub(v[2],(float)mul(normal,n[2]));
 double tangenty=sub(v[1],mul(normal,n[1])),tangentw=sub(v[3],(float)mul(normal,n[3]));
 double length=root(add(add(mul(tangentz,tangentz),mul(tangenty,tangenty)),mul(tangentx,tangentx)));
 if(length>0.0010000000474974513f){
  float speed=(float)length;double inv=divide(1,speed);float tx=(float)mul(tangentx,inv),ty=(float)mul(tangenty,inv),tz=(float)mul(tangentz,inv);double tw=mul(tangentw,inv);
  float friction=(float)mul(root(add(add(mul(bounce[2],bounce[2]),mul(bounce[1],bounce[1])),mul(bounce[0],bounce[0]))),*fp(p,0x30));
  double a=-(speed>friction?friction:speed),dx=mul(tx,a);float dy=(float)mul(ty,a),dz=(float)mul(tz,a),dw=(float)mul(tw,a);
  v[0]=(float)add(dx,v[0]);v[1]=(float)add(dy,v[1]);v[2]=(float)add(dz,v[2]);v[3]=(float)add(dw,v[3]);
 }
 for(unsigned j=0;j<3;j++)v[j]=(float)add(bounce[j],v[j]);v[3]=(float)add(bw,v[3]);
 thug_rigidbody_impact_draft(p,(float)-normal,fp(feeler,0x78),d,m);
}
