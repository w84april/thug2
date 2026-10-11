#include "../../src/game/components.h"
#include "../../src/game/attachment.h"
#include "../../src/game/stats.h"
#include "../../src/core/matrix.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *vector(void *p,unsigned o){return (float *)((char *)p+o);}
static double r(double x){return thug_platform_round_x87_single(x);}
static void origin(float *m){m[12]=m[13]=m[14]=0;m[15]=1;}
/* 00404100: capture both operands before invoking the selected SSE backend. */
float *thug_lock_matrix_pair_draft(float *out,const float *const *pair){
 const float *left=pair[0],*right=pair[1];thug_matrix_multiply(out,left,right);return out;
}
/* 004a2b60. Signed count, first matching seven-word record. */
int32_t thug_lock_bone_index_draft(const void *p,uint32_t name){
 int32_t count=word(p,0x14);const uint32_t *records=pointer(p,0x18);
 for(int32_t i=0;i<count;i++)if(records[i*7]==name)return i;return -1;
}
/* 004a2c50. Caller supplies a valid index in the skeleton's provider. */
uint32_t thug_lock_bone_parent_draft(const void *p,uint32_t index){return word(p,0x108+index*4);}
/* 004a36e0. Undo the bind transform, then apply the current pose. The special
 * root affects orientation only; the intermediate translation is restored. */
uint8_t thug_lock_bone_matrix_draft(const void *p,uint32_t name,float *out){
 int32_t index=thug_lock_bone_index_draft(p,name);if(index<0)return 0;
 float current[16],matrix[16],root[16],translation[4];
 thug_matrix_copy(current,vector(pointer(p,4),index*64));
 thug_matrix_copy(matrix,vector(pointer(pointer(p,8),0x58c),index*64));
 thug_matrix_rigid_inverse(matrix);thug_matrix_multiply(matrix,matrix,current);
 index=thug_lock_bone_index_draft(p,0x9f173eeb);
 if(index>=0){
  thug_vector_copy(translation,matrix+12);origin(matrix);
  thug_matrix_copy(root,vector(pointer(pointer(p,8),0x58c),index*64));
  thug_matrix_multiply(matrix,root,matrix);thug_vector_copy(matrix+12,translation);
 }
 thug_matrix_copy(out,matrix);return 1;
}
float *thug_sound_transform_draft(float *,const float *,const float *);
void *thug_model_transform_matrix_draft(void *,float *);
static int transformed(void *model,void *target){return model&&(((uint8_t *)model)[0x234]||word(target,0x14)<8);}
/* 0041f760. Valid component/owner layouts and, when a bone exists, a resolvable
 * parent bone. The original uses an uninitialized stack matrix otherwise. */
void thug_lock_update_draft(void *p){
 void *target=thug_object_find_global(thug_component_type_registry,word(p,0x1c));
 if(!target)target=thug_object_find_global(thug_component_type_registry,word(p,0x18));
 if(!target)return;
 void *owner=pointer(p,12);float point[4],delta[4]={0,0,0,1},temp[16];
 thug_vector_copy(point,vector(owner,0x4c));
 if(word(p,0x20)){
  if(!thug_object_find_component(target,0x222756d5))goto position;
  void *skeleton=thug_attachment_provider_points((void *)thug_object_find_component(target,0x222756d5));
  if(!skeleton)goto position;
  if(!thug_lock_bone_matrix_draft(skeleton,word(p,0x20),vector(pointer(p,12),0x6c)))goto position;
  void *provider=pointer(skeleton,8);int32_t index=thug_lock_bone_index_draft(skeleton,word(p,0x20));
  float parent[16],child_pos[4],parent_pos[4],offset[4],sum[4],up[4];
  thug_lock_bone_matrix_draft(skeleton,thug_lock_bone_parent_draft(provider,index),parent);
  owner=pointer(p,12);thug_vector_copy(child_pos,vector(owner,0x9c));thug_vector_copy(parent_pos,parent+12);
  origin(vector(owner,0x6c));origin(parent);
  void *model=thug_object_find_component(target,0x286a8d26);float *basis;
  if(transformed(model,target)){
   thug_model_transform_matrix_draft(model,temp);thug_vector_difference(delta,temp+12,vector(target,0x4c));
   origin(temp);basis=temp;
  }else basis=vector(target,0xc0);
  const float *pair[2]={vector(pointer(p,12),0x6c),basis};
  thug_lock_matrix_pair_draft(vector(pointer(p,12),0x6c),pair);pair[0]=parent;thug_lock_matrix_pair_draft(parent,pair);
  thug_matrix_transform_vector(basis,point,child_pos);owner=pointer(p,12);
  thug_sound_transform_draft(offset,vector(p,0x24),vector(owner,0x6c));
  thug_vector_sum(sum,vector(target,0x4c),offset);thug_vector_add(point,sum);
  thug_matrix_transform_vector(basis,parent_pos,parent_pos);
  thug_sound_transform_draft(offset,vector(p,0x24),parent);thug_vector_sum(sum,vector(target,0x4c),offset);thug_vector_add(parent_pos,sum);
  thug_vector_difference(vector(owner,0x8c),parent_pos,point);
  thug_vector_normalize(vector(pointer(p,12),0x8c));thug_vector_copy(up,vector(target,0xd0));owner=pointer(p,12);
  thug_vector_cross(offset,vector(owner,0x8c),up);thug_vector_copy(vector(owner,0x6c),offset);owner=pointer(p,12);
  thug_vector_cross(offset,vector(owner,0x8c),vector(owner,0x6c));thug_vector_copy(vector(owner,0x7c),offset);
  owner=pointer(p,12);thug_matrix_copy(vector(owner,0xc0),vector(owner,0x6c));
 }else{
  void *model=thug_object_find_component(target,0x286a8d26);
  if(transformed(model,target)){
   thug_model_transform_matrix_draft(model,temp);thug_sound_transform_draft(point,vector(p,0x24),temp);origin(temp);
   thug_matrix_copy(vector(pointer(p,12),0x6c),temp);
  }else{
   thug_matrix_copy(vector(pointer(p,12),0x6c),vector(target,0xc0));
   thug_sound_transform_draft(point,vector(p,0x24),vector(pointer(p,12),0x6c));
   thug_vector_add(point,vector(target,0x4c));
  }
 }
position:
 owner=pointer(p,12);float *pos=vector(owner,0x4c);
 if(((uint8_t *)p)[0x8c]&1){
  double x=r((double)point[0]-pos[0]),y=r((double)point[1]-pos[1]);
  float z=(float)r((double)point[2]-pos[2]),w=(float)r((double)point[3]-pos[3]);
  float factor=*vector(p,0x74),px=(float)r(x*factor),py=(float)r(y*factor),pw=(float)r((double)w*factor);
  double pz=r((double)z*factor),nx=r((double)px+pos[0]),ny=r((double)py+pos[1]);
  z=(float)r(pz+pos[2]);w=(float)r((double)pw+pos[3]);pos[2]=z;pos[3]=w;pos[0]=(float)nx;pos[1]=(float)ny;
  double tick=(thug_frame_time()+word(p,0x88))&0x3ff;
  double a=thug_platform_sin(r(r(tick**vector(p,0x84))*0.006135923322290182));
  double b=thug_platform_sin(r(r(tick**vector(p,0x80))*0.006135923322290182));
  *vector(p,0x74)=(float)r(r(r(r(r(a*b)+1)*r((double)*vector(p,0x7c)-*vector(p,0x78)))*.5)+*vector(p,0x78));
 }else thug_vector_sum(pos,delta,point);
 thug_vector_copy(vector(pointer(p,12),0xac),vector(target,0xac));
 if(((uint8_t *)p)[0x8c]&2){float *m=vector(pointer(p,12),0x6c);thug_matrix_multiply(m,m,vector(p,0x34));}
 owner=pointer(p,12);thug_matrix_copy(vector(owner,0xc0),vector(owner,0x6c));
}
/* 0041ff90. */
void thug_lock_update_enabled_draft(void *p){if(((uint8_t *)p)[0x8c]&4)thug_lock_update_draft(p);}
extern uint32_t *thug_proximity_frame_boundary_draft;
void thug_proximity_lock_boundary_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_lock_update_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(thug_proximity_frame_boundary_draft)thug_proximity_lock_boundary_draft(p,q,d,m);
 thug_lock_update_enabled_draft(p);
}
uint32_t *thug_lock_frame_boundary_draft;
static void boundary(void *p,uint32_t address){
 uint32_t *b=thug_lock_frame_boundary_draft;
 if(b){b[0]=address;b[1]=(uintptr_t)p;b[2]=word(p,12);b[3]=1;}__builtin_trap();
}
void thug_lock_rigidbody_boundary_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;boundary(p,0x430e20);
}
void thug_lock_particle_boundary_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;boundary(p,0x41df80);
}
