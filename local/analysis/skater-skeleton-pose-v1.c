/* Private partial original4a4240/4a44e0: ordinary finite quaternion poses,
 * valid separately allocated matrices and parent pointers, no runtime scale
 * flags or instance root-collapse flag. Unsupported modes trap explicitly.
 * No complete-function, rendering, animation sampling or gameplay credit. */
#include "../../src/core/matrix.h"
#include <stdint.h>
typedef struct {uint32_t name;float *parent_matrix;uint32_t flags;uint32_t scale[4];} PoseBoneV1;
typedef struct {uint32_t flags;float (*matrices)[16];void *asset;uint32_t lod,state;int32_t count;PoseBoneV1 *bones;} PoseSkeletonV1;
extern float *thug_quaternion_translation_matrix_draft(float *,const float *,float *);
static uint32_t pose_word(const void *p,unsigned offset){uint32_t v;__builtin_memcpy(&v,(const char *)p+offset,4);return v;}
/* Original4a2f20 has a register ABI and does not modify its quaternion.
 * The already-compared463aa0 conjugates its argument; copying it gives the
 * same ordinary no-flip/no-mirror basis. Original comparison is required. */
static void ordinary_pose_matrix(float out[16],const float q[4],const float t[4]){
 float copy[4];__builtin_memcpy(copy,q,16);thug_quaternion_translation_matrix_draft(copy,t,out);
}
void thug_skeleton_evaluate_pose_partial_v1(PoseSkeletonV1 *s,const float (*q)[4],const float (*t)[4]){
 if(s->flags&0x08000000)__builtin_trap();
 for(int32_t i=0;i<s->count;i++)if(!(s->bones[i].flags&0x40000000)&&(s->bones[i].flags&0x30000000))__builtin_trap();
 uint32_t mask=1u<<(s->lod&31);
 for(int32_t i=0;i<s->count;i++){
  PoseBoneV1 *bone=s->bones+i;if(bone->flags&0x40000000)continue;
  if(pose_word(s->asset,0x408+4*(unsigned)i)&mask)__builtin_memcpy(s->matrices[i],bone->parent_matrix,64);
  else{ordinary_pose_matrix(s->matrices[i],q[i],t[i]);if(i)thug_matrix_multiply(s->matrices[i],s->matrices[i],bone->parent_matrix);}
 }
 const float (*inverse)[16]=(const float (*)[16])(uintptr_t)pose_word(s->asset,0x58c);
 for(int32_t i=0;i<s->count;i++)if(!(s->bones[i].flags&0x40000000)){
  thug_matrix_multiply(s->matrices[i],inverse[i],s->matrices[i]);
  s->matrices[i][3]=s->matrices[i][7]=s->matrices[i][11]=0;
 }
}
void thug_skeleton_evaluate_pose_block_partial_v1(PoseSkeletonV1 *s,const uint8_t *pose){
 thug_skeleton_evaluate_pose_partial_v1(s,(const float (*)[4])pose,(const float (*)[4])(pose+0x400));
}
