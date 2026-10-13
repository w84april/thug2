/* Private original484760 uncached/no-LOD-reader subset. Complete bounded
 * compressed clips and finite times/poses are required. Unsupported cache,
 * reader LOD and animation bone-mask modes trap; no complete-root credit. */
#include "../../src/game/animation_cache.h"
#include "../../src/game/assets.h"
#include "../../src/platform/math.h"
static double R(double v){return thug_platform_round_x87_single(v);}
static uint16_t H(const void *p){uint16_t v;__builtin_memcpy(&v,p,2);return v;}
static float rotation_time(const uint8_t key[8]){return (float)((int16_t)(H(key)<<1)>>1);}
static float translation_time(const uint8_t key[8]){return (float)(int16_t)H(key);}
/* Original483a00 via the compared483d00 helper in separate local storage. */
static void unpack_quaternion(float out[4],const uint8_t key[8]){
 uint8_t expanded[20]={0};thug_animation_expand_quaternion(expanded,key);__builtin_memcpy(out,expanded+4,16);
}
static void unpack_translation(float out[4],const uint8_t key[8]){
 for(unsigned i=0;i<3;i++)out[i]=(float)(int16_t)H(key+2+2*i)*0.03125f;out[3]=1;
}
/* Original47d470 ordinary non-overlapping inputs. The second quaternion is
 * mutated; PC24 X/Y stay wide, Z/W and the reciprocal have explicit spills. */
static void nlerp(float out[4],const float a[4],float b[4],float f){
 double dot=R(R(R(R((double)a[0]*b[0])+R((double)b[3]*a[3]))+R((double)b[2]*a[2]))+R((double)b[1]*a[1]));
 if(dot<0)for(unsigned i=0;i<4;i++)b[i]=-b[i];
 double x=R(R(R((double)b[0]-a[0])*f)+a[0]),y=R(R(R((double)b[1]-a[1])*f)+a[1]);
 float z=(float)R(R(R((double)b[2]-a[2])*f)+a[2]);
 double w=R(R(R((double)b[3]-a[3])*f)+a[3]);float ws=(float)w;
 double length=R(R(R(R(w*ws)+R((double)z*z))+R(y*y))+R(x*x));
 double inverse=R(1/R(__builtin_sqrt(length)));float inv=(float)inverse;
 b[0]=(float)R(inverse*x);b[1]=(float)R((double)inv*y);b[2]=(float)R((double)inv*z);b[3]=(float)R((double)inv*ws);
 __builtin_memcpy(out,b,16);
}
static void rotation(float out[4],const uint8_t a[8],const uint8_t b[8],float f){
 if(f==0){unpack_quaternion(out,a);return;}if(f==1){unpack_quaternion(out,b);return;}
 float first[4],second[4];unpack_quaternion(first,a);unpack_quaternion(second,b);nlerp(out,first,second,f);
}
static void translation(float out[4],const uint8_t a[8],const uint8_t b[8],float f){
 if(f==0){unpack_translation(out,a);return;}if(f==1){unpack_translation(out,b);return;}
 float first[4],second[4];unpack_translation(first,a);unpack_translation(second,b);
 for(unsigned i=0;i<4;i++)out[i]=(float)R(R(R((double)second[i]-first[i])*f)+first[i]);
}
uint8_t thug_keyframe_sample_uncached_partial_v1(ThugKeyframeAnimation *a,float (*q)[4],float (*t)[4],uint8_t *valid,float seconds,int32_t cache_index,ThugAnimationReader *reader){
 (void)cache_index;
 if(a->cache||(reader&&reader->mode)||(a->flags&0x80000))__builtin_trap();
 float frame=(float)R((double)seconds*60);const uint8_t *rp=a->rotation_keys,*tp=a->translation_keys;
 const uint16_t *rl=a->rotation_lengths,*tl=a->translation_lengths;
 for(uint32_t i=0;i<a->bone_count;i++,rp+=*rl++,tp+=*tl++){
  valid[i]=1;
  if(!*rl){q[i][0]=q[i][1]=q[i][2]=0;q[i][3]=1;}
  else{
   const uint8_t *p=rp,*end=rp+*rl;uint8_t first[8]={0},second[8]={0};float fraction;
   for(;;){
    if(reader)__builtin_memcpy((uint8_t *)reader+8+4*i,&p,4);
    p=thug_animation_decode_rotation(p,first,a->flags,a->rotation_table);
    if(p>=end){__builtin_memcpy(second,first,8);fraction=0;break;}
    thug_animation_decode_rotation(p,second,a->flags,a->rotation_table);
    float from=rotation_time(first),to=rotation_time(second);
    if(frame>=from&&frame<=to){fraction=(float)R(R((double)frame-from)/R((double)to-from));break;}
   }
   rotation(q[i],first,second,fraction);
  }
  if(!(a->flags&0x20000)||*tl){
   const uint8_t *p=tp,*end=tp+*tl;uint8_t first[8]={0},second[8]={0};float fraction;
   for(;;){
    if(reader)__builtin_memcpy((uint8_t *)reader+0x108+4*i,&p,4);
    p=thug_animation_decode_translation(p,first,a->flags);
    if(p>=end||frame<=translation_time(first)){__builtin_memcpy(second,first,8);fraction=0;break;}
    thug_animation_decode_translation(p,second,a->flags);
    float from=translation_time(first),to=translation_time(second);
    if(frame<=to){fraction=(float)R(R((double)frame-from)/R((double)to-from));break;}
   }
   float old[4];__builtin_memcpy(old,t[i],16);translation(t[i],first,second,fraction);
   if((a->flags&0x4000)&&(a->flags&0x20000))for(unsigned j=0;j<4;j++)t[i][j]=(float)R((double)old[j]+t[i][j]);
  }
 }
 return 1;
}
