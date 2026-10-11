/* Original SkaterRotate component and its four missing math helpers. */
#include "../../src/game/components.h"
#include "../../src/game/nodes.h"
#include "../../src/core/matrix.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float num(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void number(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static float *vector(void *p,unsigned o){return (float *)((char *)p+o);}
static void byte(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
/* 00404ec0. EAX returns the output; Ghidra's void prototype omits it.
 * The game supplies coordinate axes 0..2. Signed modulo follows the original. */
float *thug_matrix_rotation_coordinate_draft(float out[16],int32_t axis,float radians){
 double sine=thug_platform_sin(radians),cosine=thug_platform_cos(radians);
 int32_t next=(int32_t)((uint32_t)axis+1)%3,last=(int32_t)((uint32_t)axis+2)%3;
 for(unsigned i=0;i<16;i++)out[i]=(i%5==0)?1:0;
 out[next*5]=(float)cosine;out[last+next*4]=(float)sine;
 out[next+last*4]=(float)-sine;out[last*5]=(float)cosine;return out;
}
/* 004057b0. The original inlines the same Z rotation stores. */
float *thug_matrix_rotate_z_draft(float matrix[16],float radians){
 float rotation[16];thug_matrix_rotation_z(rotation,radians);
 thug_matrix_multiply(matrix,rotation,matrix);return matrix;
}
/* 00406260. Ties and unordered comparisons favor the earlier coordinate.
 * Write the initial index before reading the vector, preserving aliasing. */
double thug_vector_dominant_coordinate_draft(const float v[4],uint32_t *index){
 uint32_t local;if(!index)index=&local;*index=0;
 double y=__builtin_fabs((double)v[1]);float x=(float)__builtin_fabs((double)v[0]);
 if(y>x){if(__builtin_fabs((double)v[2])>y)*index=2;else *index=1;}
 else if(__builtin_fabs((double)v[2])>x)*index=2;
 return v[*index];
}
/* 004062d0. Project on a selected basis plane, then use the dominant cross
 * coordinate to select the sign. The negative acos is stored as float first. */
double thug_matrix_direction_angle_draft(const float matrix[16],const float direction[4],uint32_t forward,uint32_t normal){
 float v[4];for(unsigned i=0;i<4;i++)put(v,i*4,word(direction,i*4));
 thug_vector_project_plane(v,matrix+normal*4);
 double length2=R(R(R((double)v[2]*v[2])+R((double)v[0]*v[0]))+R((double)v[1]*v[1]));
 if(length2<0.00009999999747378752f)return 0;
 thug_vector_normalize(v);const float *basis=matrix+forward*4;
 double dot=R(R(R((double)v[2]*basis[2])+R((double)v[1]*basis[1]))+R((double)v[0]*basis[0]));
 float cosine=(float)dot;if(dot>1)cosine=1;else if(cosine< -1)cosine=-1;
 float angle=(float)-thug_platform_acos_x87_single(cosine),cross[4];
 cross[0]=(float)R(R((double)v[2]*basis[1])-R((double)v[1]*basis[2]));
 cross[1]=(float)R(R((double)v[0]*basis[2])-R((double)v[2]*basis[0]));
 cross[2]=(float)R(R((double)v[1]*basis[0])-R((double)v[0]*basis[1]));cross[3]=0;
 uint32_t index;double dominant=thug_vector_dominant_coordinate_draft(cross,&index);
 return (dominant>0)==(matrix[normal*4+index]>0)?-(double)angle:angle;
}
extern const ThugComponentMethods thug_skater_rotate_methods_draft;
/* 00517cc0,00517cf0. */
void thug_skater_rotate_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_rotate_methods_draft);thug_component_destroy(p);}
void *thug_skater_rotate_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_skater_rotate_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00517cd0. Clear only the three active bytes, in reverse coordinate order. */
void thug_skater_rotate_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;byte(p,0x50,0);byte(p,0x3c,0);byte(p,0x28,0);}
/* 00517d20. */
void thug_skater_rotate_finalize_draft(void *p){put(p,0x54,(uintptr_t)thug_object_find_component(ptr(p,12),0x5bd63b29));}
/* 00517d40. */
void *thug_skater_rotate_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x58,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_rotate_methods_draft);put(p,4,0x52d61a0d);put(p,0x54,0);}return p;
}
static void suspend(void *p,uint32_t value){((const ThugComponentMethods *)ptr(p,0))->suspend(p,value);}
/* 00517dc0. Progress uses the wide delta before its float spill. Owner and
 * cached Physics matrices are independently premultiplied in that order. */
void thug_skater_rotate_update_draft(void *p){
 for(unsigned axis=0;axis<3;axis++){
  unsigned o=0x18+axis*20;if(!((uint8_t *)p)[o+16])continue;
  double wide_delta=R(thug_frame_duration()*num(p,o+8));float delta=(float)wide_delta;
  float progress=(float)R(__builtin_fabs(wide_delta)+num(p,o+12));number(p,o+12,progress);
  if(progress>=num(p,o)){
   byte(p,o+16,0);double sign=delta<0?-1:1;
   delta=(float)R((double)delta-R(R((double)progress-num(p,o))*sign));
  }
  float rotation[16];thug_matrix_rotation_coordinate_draft(rotation,axis,delta);
  float *owner=vector(ptr(p,12),0x6c);thug_matrix_multiply(owner,rotation,owner);
  float *physics=vector(ptr(p,0x54),0x18);thug_matrix_multiply(physics,rotation,physics);
 }
 if(!((uint8_t *)p)[0x28]&&!((uint8_t *)p)[0x3c]&&!((uint8_t *)p)[0x50])suspend(p,1);
}
/* 00517ea0. Timed parameters can replace selected axes without resetting
 * the others. Immediate commands prefer X, then Y, then Z, else reverse. */
uint32_t thug_skater_rotate_command_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)script;if(name!=0xc876adf3)return 2;float duration=0,angle=0;
 if(thug_script_get_float(s,0x79a07f3f,&duration,0)){
  if(!thug_script_has_flag(s,0xd029f619)&&!thug_script_has_flag(s,0x49e0ee96)){
   float factor=(thug_script_has_flag(s,0x019176c5)||thug_script_has_flag(s,0x4a07c332))?0.01666666753590107f:0.0010000000474974513f;
   duration=(float)R((double)duration*factor);
  }
  const uint32_t names[]={0x7323e97c,0x0424d9ea,0x9d2d8850};
  for(unsigned axis=0;axis<3;axis++){
   unsigned o=0x18+axis*20;
   if(thug_script_get_float(s,names[axis],vector(p,o),0)){
    number(p,o+4,duration);if(axis!=2)put(p,o+12,0);byte(p,o+16,1);
    number(p,o+8,(float)R(R((double)num(p,o)/duration)*0.01745329238474369f));
    number(p,o,(float)__builtin_fabs(R((double)num(p,o)*0.01745329238474369f)));
    if(axis==2)put(p,o+12,0);
   }
  }
  uint32_t node=0;
  if(thug_script_get_checksum(s,0x7a8017ba,&node,0)){
   float target[4],direction[4];thug_node_position(thug_node_find(node,1),target);
   void *owner=ptr(p,12);for(unsigned i=0;i<4;i++)direction[i]=(float)R((double)target[i]-num(owner,0x4c+i*4));
   double degrees=R(thug_matrix_direction_angle_draft(vector(owner,0x6c),direction,2,1)*57.2957763671875f);
   number(p,0x30,duration);put(p,0x38,0);byte(p,0x3c,1);
   number(p,0x34,(float)R(R(degrees/duration)*0.01745329238474369f));
   number(p,0x2c,(float)__builtin_fabs(R(degrees*0.01745329238474369f)));
  }
  suspend(p,0);return 1;
 }
 if(thug_script_get_float(s,0x7323e97c,&angle,0)){
  void *owner=ptr(p,12);float rotation[16];thug_matrix_rotation_x(rotation,(float)R((double)angle*0.01745329238474369f));
  thug_matrix_multiply(vector(owner,0x6c),rotation,vector(owner,0x6c));
 }else if(thug_script_get_float(s,0x0424d9ea,&angle,0))thug_matrix_rotate_y(vector(ptr(p,12),0x6c),(float)R((double)angle*0.01745329238474369f));
 else if(thug_script_get_float(s,0x9d2d8850,&angle,0))thug_matrix_rotate_z_draft(vector(ptr(p,12),0x6c),(float)R((double)angle*0.01745329238474369f));
 else{
  void *owner=ptr(p,12);for(unsigned i=0;i<3;i++)number(owner,0x8c+i*4,(float)-(double)num(owner,0x8c+i*4));
  owner=ptr(p,12);for(unsigned i=0;i<3;i++)number(owner,0x6c+i*4,(float)-(double)num(owner,0x6c+i*4));
  void *physics=ptr(p,0x54);thug_matrix_copy(vector(physics,0x18),vector(ptr(physics,12),0x6c));
  physics=ptr(p,0x54);byte(physics,0x34c,!((uint8_t *)physics)[0x34c]);return 1;
 }
 void *physics=ptr(p,0x54);thug_matrix_copy(vector(physics,0x18),vector(ptr(physics,12),0x6c));return 1;
}
static void frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_skater_rotate_update_draft(p);}
static void empty(void *p){(void)p;}
const ThugComponentMethods thug_skater_rotate_methods_draft={
 .dispose=thug_skater_rotate_delete_draft,.update=frame,.initialize=thug_skater_rotate_initialize_draft,.finalize=thug_skater_rotate_finalize_draft,
 .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=thug_skater_rotate_command_draft};
