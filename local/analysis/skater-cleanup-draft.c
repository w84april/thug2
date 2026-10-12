/* SkaterCleanupState and its original lighting/projected-shadow direction path. */
#include "../../src/game/components.h"
#include "../../src/game/camera.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/core/d3dx.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
#define R thug_platform_round_x87_single
float *thug_light_global_directions_draft; /* 0067dc9c */
float thug_light_shared_direction_draft[4]; /* 0070166c */
uint32_t thug_light_shared_flags_draft; /* 0070167c */
float thug_skater_shadow_vertical_draft[4],thug_skater_shadow_light_draft[4]; /* 007ce4c4/d4 */
uint32_t thug_skater_shadow_flags_draft; /* 007ce4e4 */
void *thug_shadow_projection_table_draft; /* 007ca970 */
/* 004b6ab0 /0048e920. Loads precede writes, even when the global source aliases
 * the shared vector. Only X bypasses x87's signaling-NaN quieting. */
float *thug_light_global_direction_pc_draft(uint32_t i){
 if(!(thug_light_shared_flags_draft&1))thug_light_shared_flags_draft|=1;
 const void *p=(void *)((uintptr_t)thug_light_global_directions_draft+(uint32_t)(i<<4));
 uint32_t z=quiet(word(p,8)),x=word(p,0),y=quiet(word(p,4));
 put(thug_light_shared_direction_draft,4,y);put(thug_light_shared_direction_draft,0,x);
 put(thug_light_shared_direction_draft,12,0x3f800000);put(thug_light_shared_direction_draft,8,z);
 return thug_light_shared_direction_draft;
}
float *thug_light_global_direction_draft(uint32_t i){return thug_light_global_direction_pc_draft(i);}
/* 004b6250 /004b6180 /00456b30. Preserve the two actual virtual calls. */
uint32_t thug_light_direction_enabled_draft(void *p,uint32_t i){return (word(p,0x1c)&(2u<<(i&31)))!=0;}
float *thug_light_direction_pc_draft(void *p,uint32_t i){
 const uint32_t *v=ptr(p,0);
 if((uint8_t)((uint32_t (*)(void *,uint32_t))(uintptr_t)v[12])(p,i))return (float *)((uintptr_t)ptr(p,0x2c)+(uint32_t)(i<<4));
 return thug_light_global_direction_draft(i);
}
float *thug_light_direction_draft(void *p,uint32_t i){const uint32_t *v=ptr(p,0);return ((float *(*)(void *,uint32_t))(uintptr_t)v[5])(p,i);}
/* 00485a70 /00485a90. Forward word copies intentionally retain overlap. */
void thug_camera_set_position_draft(void *p,const void *v){for(unsigned i=0;i<4;i++)put(p,0x5c+4*i,word(v,4*i));}
float *thug_camera_set_orientation_draft(void *p,const float *v){return thug_matrix_copy((float *)((char *)p+0x6c),v);}
/* 004db100. Valid initialized table; an absent key has no effects. The
 * vertical eye/target case uses up=(0,0,1), otherwise up=(0,1,0). */
void thug_shadow_projection_matrices_draft(uint32_t key,const float *eye,const float *target){
 void *table=thug_shadow_projection_table_draft;
 uint32_t slot=key&((1u<<(word(table,0)&31))-1);
 void *node=(void *)((uintptr_t)ptr(table,4)+(uint32_t)(slot*12));
 while(node){if(word(node,0)==key&&word(node,4))break;node=ptr(node,8);}
 if(!node)return;void *entry=ptr(node,4);if(!entry)return;
 float up[3]={0,1,0};if(eye[0]==target[0]&&eye[2]==target[2]){up[1]=0;up[2]=1;}
 thug_d3dx_look_at_rh((float *)((char *)entry+12),eye,target,up);
 thug_d3dx_ortho_rh((float *)((char *)entry+0x4c),120,120,5,500);
 thug_d3dx_ortho_rh((float *)((char *)entry+0x8c),120,120,80,500);
}
/* 004b2c50 /0048bf60. Texture carries either a key or a pointer to a key. */
void thug_shadow_camera_projection_pc_draft(void *texture,const ThugCamera *camera){
 const float *z=thug_camera_position(camera),*y=thug_camera_position(camera),*x=thug_camera_position(camera);
 float eye[3],target[3];put(eye,8,quiet(word(z,8)));put(eye,4,quiet(word(y,4)));put(eye,0,word(x,0));
 z=thug_camera_orientation(camera);y=thug_camera_orientation(camera);x=thug_camera_orientation(camera);
 target[0]=(float)R((double)number(x,0x20)+eye[0]);target[1]=(float)R((double)number(y,0x24)+eye[1]);target[2]=(float)R((double)number(z,0x28)+eye[2]);
 uint32_t key=word(texture,8)&1?word(ptr(texture,0x10),0):word(texture,0x10);
 thug_shadow_projection_matrices_draft(key,eye,target);
}
void thug_shadow_camera_projection_draft(void *texture,const ThugCamera *camera){thug_shadow_camera_projection_pc_draft(texture,camera);}
/* Shared transcription of004a1ba0/004a21a0; no renderer callback substituted.
 * Preserve saved position, live camera rereads and raw/quiet vector lanes. */
static void shadow_direction(void *p,const void *input,unsigned offset){
 uint32_t saved[4];const float *position=thug_camera_position(ptr(p,8));
 for(unsigned i=0;i<4;i++)saved[i]=word(position,4*i);
 float *direction=(float *)((char *)p+offset);
 for(unsigned i=0;i<4;i++)put(direction,4*i,word(input,4*i));
 thug_vector_normalize(direction);
 const float zero[4]={0,0,0,1};thug_camera_set_position_draft(ptr(p,8),zero);
 uint32_t x=word(direction,0),y=quiet(word(direction,4)),z=word(direction,8),w=word(direction,12);
 uint32_t matrix[16]={z,quiet(x)^0x80000000,y^0x80000000,0,y,quiet(z)^0x80000000,quiet(x)^0x80000000,0,x,y,z,w,0,0,0,0x3f800000};
 thug_camera_set_orientation_draft(ptr(p,8),(const float *)matrix);
 thug_camera_set_position_draft(ptr(p,8),saved);
}
void thug_shadow_projected_direction_draft(void *p,const void *v){shadow_direction(p,v,0x10);thug_shadow_camera_projection_draft(ptr(p,12),ptr(p,8));}
void thug_shadow_dynamic_direction_draft(void *p,const void *v){shadow_direction(p,v,0x50);}
typedef struct {uintptr_t unavailable[3];void (*direction)(void *,const void *);} ShadowMethods;
/* Unrecovered renderer methods are absent and trap if used. These tables
 * expose only the direction slot; renderer creation/rendering is separate. */
static void blob_direction(void *p,const void *v){thug_component_empty_one(p,(void *)v);}
const ShadowMethods thug_shadow_blob_direction_methods_draft={.direction=blob_direction};
const ShadowMethods thug_shadow_projected_direction_methods_draft={.direction=thug_shadow_projected_direction_draft};
const ShadowMethods thug_shadow_dynamic_direction_methods_draft={.direction=thug_shadow_dynamic_direction_draft};
/* 00431360. The outer component's optional renderer owns the virtual. */
void thug_shadow_set_direction_draft(void *p,const void *v){void *renderer=ptr(p,0x18);if(renderer)((const ShadowMethods *)ptr(renderer,0))->direction(renderer,v);}
extern void *thug_model_renderer_lights_draft(const void *);
/* 005809c0. Both supplied vectors are unused by the original body. */
void thug_skater_update_shadow_direction_draft(void *p,const void *position,const void *orientation){
 (void)position;(void)orientation;uint32_t flags=thug_skater_shadow_flags_draft;
 if(!(flags&1)){thug_skater_shadow_flags_draft=flags|=1;const float v[4]={.8f,-.8f,.3f,1};__builtin_memcpy(thug_skater_shadow_light_draft,v,16);}
 if(!(flags&2)){thug_skater_shadow_flags_draft=flags|2;const float v[4]={0,-1,0,1};__builtin_memcpy(thug_skater_shadow_vertical_draft,v,16);}
 if(thug_object_find_component(p,0x286a8d26)&&ptr(thug_object_find_component(p,0x286a8d26),0x208)){
  void *light=thug_model_renderer_lights_draft(ptr(thug_object_find_component(p,0x286a8d26),0x208));
  if(light){float *v=thug_light_direction_draft(light,0);
   double x=R((double)v[0]*-1),y=R((double)v[1]*-1),wide_z=R((double)v[2]*-1),w=R((double)v[3]*-1);float z=(float)wide_z;
   thug_skater_shadow_light_draft[0]=(float)x;thug_skater_shadow_light_draft[1]=(float)y;thug_skater_shadow_light_draft[2]=(float)wide_z;thug_skater_shadow_light_draft[3]=(float)w;
   if(y>(double)-.65f){double sum=R(R((double)z*z)+R(x*x));double scale=sum>0?R(__builtin_sqrt(R((double).5775f/sum))):0;
    thug_skater_shadow_light_draft[1]=-.65f;thug_skater_shadow_light_draft[0]=(float)R(x*scale);thug_skater_shadow_light_draft[2]=(float)R((double)z*scale);
   }
  }
 }
 void *control=ptr(p,0x284);uint8_t active;
 if(control&&!((uint8_t *)ptr(control,0x2c))[0x118]&&!word(ptr(control,0x2c),0x1c))active=word(ptr(ptr(p,0x280),0x1528),0x18)==0;
 else {void *walk=ptr(p,0x288);active=!walk||word(walk,0x18)!=1;}
 int32_t counter=(int32_t)word(p,0x174);counter=active?(counter>0?counter-1:0):(counter<16?counter+1:16);put(p,0x174,(uint32_t)counter);
 float direction[4];float factor=(float)R(R((double)counter)*.0625f);
 thug_vector_lerp(direction,thug_skater_shadow_light_draft,thug_skater_shadow_vertical_draft,factor);
 thug_shadow_set_direction_draft(ptr(p,0x254),direction);
}
extern const ThugComponentMethods thug_skater_cleanup_methods_draft;
/* 004fbe20 /004fbd90 /004fbdb0 /004fbda0 /004fbde0 /004fbe00. */
void *thug_skater_cleanup_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1c,m);if(!p)return 0;thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_cleanup_methods_draft);put(p,4,0xd8cc3428);return p;}
void thug_skater_cleanup_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_cleanup_methods_draft);thug_component_destroy(p);}
void *thug_skater_cleanup_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_skater_cleanup_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
void thug_skater_cleanup_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;put(p,0x18,0);}
void thug_skater_cleanup_bind_draft(void *p){put(p,0x18,(uintptr_t)thug_object_find_component(ptr(p,12),0x43686585));}
void thug_skater_cleanup_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;void *owner=ptr(p,12);thug_skater_update_shadow_direction_draft(owner,(char *)owner+0x4c,(char *)owner+0x6c);}
static void empty(void *p){(void)p;}
static uint32_t command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;return 2;}
const ThugComponentMethods thug_skater_cleanup_methods_draft={.dispose=thug_skater_cleanup_delete_draft,.update=thug_skater_cleanup_update_draft,.initialize=thug_skater_cleanup_initialize_draft,.finalize=thug_skater_cleanup_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=command};
