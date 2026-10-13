/* Private candidate for original runtime skeleton storage and startup.
 * Initialized successful allocators and complete, separate 0..64-bone assets
 * are required. Virtual lifecycle/frame behavior remains unavailable. */
#include "../../src/game/components.h"
#include "../../src/game/assets.h"
#include "../../src/game/skater.h"
#include "../../src/game/stats.h"
#include "../../src/script/params.h"
typedef struct {uint32_t name;float *parent_matrix;uint32_t flags;uint32_t scale[4];} SkeletonBoneV1;
typedef struct {uint32_t flags;float (*matrices)[16];void *asset;uint32_t unknown_0c,state;int32_t count;SkeletonBoneV1 *bones;} SkeletonInstanceV1;
_Static_assert(sizeof(SkeletonBoneV1)==28,"bone runtime stride");
_Static_assert(sizeof(SkeletonInstanceV1)==28,"skeleton runtime instance");
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void store(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static SkeletonBoneV1 *allocate_bones(int32_t count,const ThugMemory *m){
 SkeletonBoneV1 *bones=m->allocate(m->context,(uint32_t)count*28,1);
 if(bones)for(int32_t i=0;i<count;i++){
  bones[i].name=0;bones[i].parent_matrix=0;bones[i].flags=0;
  for(unsigned j=0;j<4;j++)bones[i].scale[j]=0x3f800000;
 }
 return bones;
}
/* 004a3150. Parent checksums resolve to the first name, or index zero. */
void thug_skeleton_instance_prepare_v1(SkeletonInstanceV1 *s,const void *asset){
 int32_t count=(int32_t)word(asset,4);
 for(int32_t i=0;i<count;i++){
  uint32_t parent=word(asset,0x108+4*(unsigned)i);int32_t index=0;
  if(parent){for(index=0;index<count;index++)if(word(asset,8+4*(unsigned)index)==parent)break;if(index==count)index=0;}
  s->bones[i].parent_matrix=s->matrices[index];s->bones[i].flags=0;
 }
}
/* 004a3d30. Unspecified instance bytes are deliberately preserved. */
SkeletonInstanceV1 *thug_skeleton_instance_construct_v1(SkeletonInstanceV1 *s,void *asset,const ThugMemory *m){
 s->flags=(word(asset,0x594)&1)?0x10000000:0;
 int32_t count=(int32_t)word(asset,4);s->bones=allocate_bones(count,m);
 s->matrices=m->allocate(m->context,(uint32_t)(int32_t)word(asset,4)*64,1);
 for(int32_t i=0;i<(int32_t)word(asset,4);i++)for(unsigned j=0;j<16;j++)store(s->matrices[i],4*j,(j%5==0)?0x3f800000:0);
 s->count=(int32_t)word(asset,4);
 for(int32_t i=0;i<(int32_t)word(asset,4);i++)s->bones[i].name=word(asset,8+4*(unsigned)i);
 thug_skeleton_instance_prepare_v1(s,asset);s->asset=asset;s->state=0x1f;return s;
}
/* 004a3e80. Copy raw pose/scale bits; parent pointers bind new matrices. */
SkeletonInstanceV1 *thug_skeleton_instance_clone_v1(SkeletonInstanceV1 *s,const SkeletonInstanceV1 *from,const ThugMemory *m){
 s->count=(int32_t)word(from->asset,4);s->bones=allocate_bones(s->count,m);
 s->matrices=m->allocate(m->context,(uint32_t)s->count*64,1);
 for(int32_t i=0;i<s->count;i++)__builtin_memcpy(s->matrices[i],from->matrices[i],64);
 for(int32_t i=0;i<(int32_t)word(from->asset,4);i++)s->bones[i].name=word(from->asset,8+4*(unsigned)i);
 thug_skeleton_instance_prepare_v1(s,from->asset);
 for(int32_t i=0;i<s->count;i++){
  s->bones[i].flags=from->bones[i].flags;s->bones[i].name=from->bones[i].name;
  __builtin_memcpy(s->bones[i].scale,from->bones[i].scale,16);
 }
 s->asset=from->asset;s->unknown_0c=from->unknown_0c;s->flags=from->flags;s->state=from->state;return s;
}
/* Identity only; these thirteen virtual slots are not dispatched. */
const uint32_t thug_skeleton_component_pending_methods_v1[13]={0};
/* 00431f60. Original zeroed allocation followed by the recovered base ctor. */
void *thug_skeleton_component_create_v1(const ThugMemory *m){
 void *p=thug_allocate_zeroed(28,m);if(!p)return 0;thug_component_construct(p);
 store(p,0,(uintptr_t)thug_skeleton_component_pending_methods_v1);store(p,4,0x222756d5);store(p,24,0);return p;
}
/* 00431c70. The outer allocation can fail; nested runtime storage must succeed. */
void thug_skeleton_component_load_v1(void *p,uint32_t name,const ThugDiagnostics *d,const ThugMemory *m){
 void *asset=thug_asset_find(thug_asset_manager,name,0,d);SkeletonInstanceV1 *s=m->allocate(m->context,28,1);
 store(p,24,(uintptr_t)(s?thug_skeleton_instance_construct_v1(s,asset,m):0));
}
/* 00431cf0. Clone an existing object's Skeleton or load the supplied namespace. */
void thug_skeleton_component_initialize_v1(void *p,const ThugScriptStructure *parameters,const ThugDiagnostics *d,const ThugMemory *m){
 uint32_t existing=0;
 if(!thug_script_get_checksum(parameters,0xa81f615c,&existing,0)){
  uint32_t name;
  if(!thug_script_get_checksum(parameters,0x222756d5,&name,0)&&!thug_script_get_checksum(parameters,0x09794932,&name,1))__builtin_trap();
  thug_skeleton_component_load_v1(p,name,d,m);uint32_t state;
  if(thug_script_get_integer(parameters,0xd3982061,&state,0)&&word(p,24))store((void *)(uintptr_t)word(p,24),16,state);
 }else{
  ThugSkaterBody *owner=thug_object_find_global(0,existing);
  void *other=thug_object_find_component(owner,0x222756d5);
  SkeletonInstanceV1 *s=m->allocate(m->context,28,1);
  store(p,24,(uintptr_t)(s?thug_skeleton_instance_clone_v1(s,(const void *)(uintptr_t)word(other,24),m):0));
 }
}
