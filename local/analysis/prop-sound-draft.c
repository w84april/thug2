#include "../../src/audio/device.h"
#include "../../src/core/bounds.h"
#include "../../src/core/number.h"
#include "../../src/core/timing.h"
#include "../../src/core/vector.h"
#include "../../src/game/components.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void store(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy4(void *out,const void *in){for(unsigned i=0;i<4;i++)put(out,4*i,word(in,4*i));}
static float quiet(float value){uint32_t w;__builtin_memcpy(&w,&value,4);if((w&0x7f800000)==0x7f800000&&(w&0x7fffff))w|=0x400000;__builtin_memcpy(&value,&w,4);return value;}
/* 00404010. x87 result retains its exponent until its caller stores it. */
double thug_approach_number_draft(float target,float current,float step){
 double amount=__builtin_fabs((double)step);
 if(target<current){if(R((double)current-target)>amount)return R((double)current-amount);}
 else if(R((double)target-current)>amount)return R((double)current+amount);
 return target;
}
/* 004025a0/00403bb0/00403c00. These are point tests and nearest SURFACE,
 * including points already inside the box (where ordinary clamp is wrong). */
uint32_t thug_bounds_contains_point_draft(const ThugBounds *b,const float *v){
 for(unsigned i=0;i<3;i++)if(!(v[i]>=b->min[i]))return 0;
 for(unsigned i=0;i<3;i++)if(!(v[i]<=b->max[i]))return 0;
 return 1;
}
float *thug_bounds_center_draft(const ThugBounds *b,float *out){
 float result[3];for(unsigned i=0;i<3;i++)result[i]=(float)R(R(R((double)b->max[i]-b->min[i])*.5)+b->min[i]);
 out[3]=1;for(unsigned i=0;i<3;i++)out[i]=result[i];return out;
}
void thug_bounds_nearest_surface_draft(const ThugBounds *b,const float *v,float *out){
 uint32_t mask;int32_t count=thug_bounds_count_containing_axes(b,v,&mask);
 if(count==3){
  unsigned axis=0;float best=0,coordinate=0;
  for(unsigned i=0;i<3;i++){
   double low=R((double)v[i]-b->min[i]);float high=(float)R((double)b->max[i]-v[i]);
   double distance=low<high?low:high;float c=low<high?b->min[i]:b->max[i];
   if(!i||distance<best){axis=i;best=(float)distance;coordinate=c;}
  }
  copy4(out,v);out[axis]=quiet(coordinate);
 }else{
  out[3]=1;
  for(unsigned i=0;i<3;i++)out[i]=mask&(1u<<i)?v[i]:(v[i]<=b->min[i]?b->min[i]:b->max[i]);
 }
}
/* 0041f470. All results precede the first store, in the original sum orders. */
float *thug_sound_transform_draft(float *out,const float *v,const float *m){
 float result[4];for(unsigned i=0;i<4;i++){
  double s=R((double)m[12+i]*v[3]);
  if(!i)s=R(R(R(s+R((double)m[8]*v[2]))+R((double)m[4]*v[1]))+R((double)m[0]*v[0]));
  else s=R(R(R(s+R((double)m[i]*v[0]))+R((double)m[8+i]*v[2]))+R((double)m[4+i]*v[1]));
  result[i]=(float)s;
 }
 for(unsigned i=0;i<4;i++)out[i]=result[i];return out;
}
/* 00412060/004123b0. Actual collision transform accessors used by0049e740. */
float thug_static_collision_orientation_draft[16]; /* 00691928, startup-owned */
const float *thug_moving_collision_orientation_draft(const void *p){return (const float *)((const char *)p+0x20);}
const float *thug_static_collision_orientation_get_draft(const void *p){(void)p;return thug_static_collision_orientation_draft;}
/* 0049e740. Both render-presence branches dispatch the collision +20 slot. */
const float *thug_geometry_orientation_draft(const void *p){
 void *collision=pointer(p,0x18);const void *table=pointer(collision,0);
 const float *(*get)(const void *)=(void *)(uintptr_t)word(table,0x20);return get(collision);
}
/* 00468120/004681a0. Closest output is defined for box0 and sphere2.
 * Other volume kinds leave an original stack result uninitialized. */
uint8_t thug_sound_volume_contains_draft(const void *p,const float *v){
 float d[3];for(unsigned i=0;i<3;i++)d[i]=(float)R((double)v[i]-number(p,4+4*i));
 if(word(p,0x28)==0)return thug_bounds_contains_point_draft((const void *)((const char *)p+0x38),v);
 if(word(p,0x28)!=2)return 0;
 return R(R(R((double)d[2]*d[2])+R((double)d[0]*d[0]))+R((double)d[1]*d[1]))<=number(p,0x30);
}
static void sphere_surface(const void *p,float radius,float *out,const float *v){
 float d[4];for(unsigned i=0;i<4;i++)d[i]=(float)R((double)v[i]-number(p,4+4*i));
 thug_vector_normalize(d);for(unsigned i=0;i<3;i++)d[i]=(float)R((double)d[i]*radius);
 double w=R((double)d[3]*radius);float result[4];
 for(unsigned i=0;i<3;i++)result[i]=(float)R((double)d[i]+number(p,4+4*i));
 result[3]=(float)R(w+number(p,16));copy4(out,result);
}
float *thug_sound_volume_nearest_draft(const void *p,float *out,const float *v){
 if(thug_sound_volume_contains_draft(p,v)){copy4(out,v);return out;}
 if(word(p,0x28)==0)thug_bounds_nearest_surface_draft((const void *)((const char *)p+0x38),v,out);
 else if(word(p,0x28)==2)sphere_surface(p,number(p,0x2c),out,v);
 else __builtin_trap(); /* No defined original output for unsupported shape. */
 return out;
}
/* 0046aec0. Shape3/out-of-range likewise has an uninitialized original result. */
float *thug_proximity_nearest_draft(const void *p,float *out,const float *v){
 uint32_t shape=word(p,0x6c);float result[4];const ThugBounds *b=(const void *)((const char *)p+0x7c);
 if(shape==0)sphere_surface(p,number(p,0x70),result,v);
 else if(shape==1)thug_bounds_nearest_surface_draft(b,v,result);
 else if(shape==2||shape==4){
  float center[4],delta[4],rotated[4],point[4];thug_bounds_center_draft(b,center);
  for(unsigned i=0;i<4;i++)delta[i]=(float)R((double)v[i]-center[i]);
  thug_sound_transform_draft(rotated,delta,(const void *)((const char *)p+0x14));
  for(unsigned i=0;i<4;i++)point[i]=(float)R((double)center[i]+rotated[i]);
  thug_bounds_nearest_surface_draft(b,point,result);
  for(unsigned i=0;i<4;i++)result[i]=(float)R((double)result[i]-center[i]);
  thug_sound_transform_draft(rotated,result,thug_geometry_orientation_draft(pointer(p,0x78)));
  for(unsigned i=0;i<4;i++)result[i]=(float)R((double)center[i]+rotated[i]);
 }else __builtin_trap();
 copy4(out,result);return out;
}
/* 00432e50/00432f10. Forward word copies retain overlap and raw payloads. */
float *thug_object_sound_origin_draft(const void *p,float *out,const ThugCamera *camera){
 if(pointer(p,0xb8)&&camera)thug_sound_volume_nearest_draft(pointer(p,0xb8),out,thug_camera_position(camera));
 else copy4(out,(const char *)p+0x98);return out;
}
uint8_t thug_object_sound_range_origin_draft(const void *p,const ThugCamera *camera,float *out){
 if(!camera||!pointer(p,0xbc))return 0;
 float v[4];thug_proximity_nearest_draft(pointer(p,0xbc),v,thug_camera_position(camera));copy4(out,v);return 1;
}
/* 00432f70. This is a callee-cleaned stack argument, with no receiver use. */
void thug_sound_parameters_approach_draft(void *p){
 for(unsigned i=0;i<2;i++){
  unsigned current=8+4*i,target=0x18+4*i,rate=0x20+4*i;
  if(number(p,target)!=number(p,current)){
   float step=(float)R(R(thug_frame_duration()*60)*number(p,rate));
   store(p,current,(float)thug_approach_number_draft(number(p,target),number(p,current),step));
  }
 }
}
/* 00432d40. The forward twelve-word copy deliberately permits overlap. */
void thug_object_sound_queue_draft(void *p,const void *parameters,uint32_t time){
 for(unsigned i=0;i<2;i++)if(!word(p,0x38+i*0x30)){
  void *record=(char *)p+0x38+i*0x30;
  for(unsigned j=0;j<12;j++)put(record,4*j,word(parameters,4*j));put(record,0x2c,time+2000);return;
 }
}
extern uint32_t thug_sound_pending_count_draft;
uint32_t thug_sound_pending_pool_draft[128][6]; /* 006f3668 */
/* 0047ae20. Count increments before the pool scan, even if it is exhausted. */
void thug_sound_register_owner_draft(const ThugSoundConfiguration *config,uint32_t id,uint32_t name,void *owner){
 (void)config;if(!id||thug_sound_pending_count_draft==128)return;
 ++thug_sound_pending_count_draft;
 for(unsigned i=0;i<128;i++)if(!(thug_sound_pending_pool_draft[i][2]&1)){
  uint32_t *p=thug_sound_pending_pool_draft[i];if(thug_sound_pending)put(thug_sound_pending,20,(uintptr_t)p);
  p[4]=(uintptr_t)thug_sound_pending;p[2]=1;p[5]=0;thug_sound_pending=(void *)p;p[0]=id;p[1]=name;p[3]=(uintptr_t)owner;return;
 }
}
/* 0047b6f0. A first matching inactive ID suppresses later duplicate IDs. */
uint8_t thug_sound_active_id_draft(const ThugSoundConfiguration *config,uint32_t id,uint32_t *index){
 (void)config;if(thug_sound_disabled()||!id)return 0;
 for(unsigned i=0;i<48;i++)if(thug_sound_voices[i].id==id){if(!thug_audio_slot_active(i))return 0;if(index)*index=i;return 1;}
 return 0;
}
/* 0047ba00. Low-byte name flag; stop at the first owner/key match. */
ThugSoundVoiceParameters *thug_sound_owner_parameters_draft(const ThugSoundConfiguration *config,void *owner,uint32_t key,uint32_t by_name){
 for(void *p=thug_sound_pending;p;p=pointer(p,16))if(pointer(p,12)==owner&&word(p,(uint8_t)by_name?4:0)==key){
  uint32_t i;if(!thug_sound_active_id_draft(config,word(p,0),&i))return 0;return &thug_sound_voices[i].parameters;
 }
 return 0;
}
/* 0047c140. Queuing and playback both retain the original ownership behavior. */
uint32_t thug_object_sound_play_draft(const ThugSoundConfiguration *config,uint32_t name,const ThugSoundPlaybackControls *controls,void *owner,uint32_t detached,uint32_t force){
 if(thug_sound_disabled())return 0;ThugSoundAsset *asset=thug_sound_find_asset(name);if(!asset)return 0;
 ThugSpatialSoundVolume volume;thug_sound_volume_initialize(&volume.volume);float position[4];copy4(position,(char *)owner+0x98);
 ThugCamera *camera=thug_camera_nearest(position,0);
 if(camera){
  const float *range_origin=thug_object_sound_range_origin_draft(owner,camera,position)?position:0;
  float distance=number(controls,8);if(distance==0)distance=asset->distance;
  float origin[4];thug_object_sound_origin_draft(owner,origin,camera);
  thug_sound_spatialize(config,&volume,origin,distance,controls->flags,camera,range_origin);
 }else for(unsigned i=0;i<5;i++)volume.volume.channels[i]=0;
 if(thug_sound_volume_silent(&volume.volume)&&!(uint8_t)force){
  if(!(uint8_t)detached&&(uint8_t)asset->unknown_18){
   uint32_t id=thug_sound_available_id(name);uint32_t parameters[12];
   thug_sound_voice_parameters((void *)parameters,asset,controls);
   /* Word11 is copied by432d40 but immediately replaced by the due time. */
   parameters[11]=0;thug_object_sound_queue_draft(owner,parameters,thug_frame_time());return id;
  }
  return 0;
 }
 thug_sound_volume_scale(&volume.volume,number(controls,4));
 uint32_t id=thug_sound_play(config,name,&volume,number(controls,0),0,controls,0);
 if(!thug_sound_debug_mode)thug_script_get_global_integer(0x6d2e270e,0);
 if(!(uint8_t)detached){thug_sound_register_owner_draft(config,id,name,owner);if(!thug_sound_debug_mode)thug_script_get_global_integer(0x6d2e270e,0);}
 return id;
}
/* 00433480. At least one camera is required for a due nonempty record: the
 * original no-camera branch reads an uninitialized distance from its stack. */
void thug_object_sound_pending_update_draft(void *p){
 uint32_t time=thug_frame_time();
 for(unsigned i=0;i<2;i++){
  void *record=(char *)p+0x38+i*0x30;if(!word(record,0))continue;
  thug_sound_parameters_approach_draft(record);if(word(record,0x2c)>time)continue;
  float distance;ThugCamera *camera=thug_camera_nearest((const void *)((char *)p+0x98),&distance);
  float range=number(record,4);if(range==0)range=1020;
  if(!camera)__builtin_trap();
  if(R(240.0+range)>distance){
   ThugSoundPlaybackControls c={word(record,0x10),word(record,0x14),word(record,4),word(record,0x28)};
   uint32_t id=thug_object_sound_play_draft(thug_sound_configuration,word(record,0),&c,p,0,1);
   if(id){
    ThugSoundVoiceParameters *v=thug_sound_owner_parameters_draft(thug_sound_configuration,p,id,0);
    if(v){put(v,0x1c,word(record,0x1c));double rate=R((double)number(v,0x1c)*0.009999999776482582f);
     put(v,0x18,word(record,0x18));store(v,0x24,(float)rate);put(v,0x20,word(record,0x20));put(v,0xc,0);}
    put(record,0,0);
   }
  }else{
   double delay=R(R(R((double)distance-range)*1000)*-0.0016666667070239782f);
   put(record,0x2c,time-thug_truncate_double_low_word(delay)+333);
  }
 }
}
/* 004335d0. Preserve the previous position, copy the owner's live position. */
void thug_object_sound_update_draft(void *p){copy4((char *)p+0xa8,(char *)p+0x98);copy4((char *)p+0x98,(char *)pointer(p,12)+0x4c);thug_object_sound_pending_update_draft(p);}
void thug_object_sound_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_object_sound_update_draft(p);}
/* Typed bridge for existing004a1090, not an additional recovered routine. */
void thug_object_sound_moved_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){((const ThugComponentMethods *)pointer(p,0))->update(p,q,d,m);}
