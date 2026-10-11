/* Original SkaterMatrixQueries component (64bf70) and angle predicate. */
#include "../../src/game/components.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"
#include "../../src/script/delivery.h"
#include "../../src/script/values.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float num(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint32_t bits(float v){uint32_t u;__builtin_memcpy(&u,&v,4);return u;}
static float *vector(void *p,unsigned o){return (float *)((char *)p+o);}
static void copy_vector(float out[4],const void *p,unsigned o){for(unsigned i=0;i<4;i++)put(out,i*4,word(p,o+i*4));}
/* 00406560. Lengths below 0.5 fail. Dot is divided by the two lengths in
 * sequence; neither input is normalized in memory. W is ignored. Preserve
 * the original unordered sign branch, as well as its strict final comparison. */
uint8_t thug_vector_angle_exceeds_draft(const float a[4],const float b[4],float degrees){
 double length=R(__builtin_sqrt(R(R(R((double)a[0]*a[0])+R((double)a[1]*a[1]))+R((double)a[2]*a[2]))));
 if(length<0.5f)return 0;
 double dot=R(R(R((double)a[0]*b[0])+R((double)b[2]*a[2]))+R((double)a[1]*b[1]));
 dot=R(dot/length);
 length=R(__builtin_sqrt(R(R(R((double)b[1]*b[1])+R((double)b[2]*b[2]))+R((double)b[0]*b[0]))));
 if(length<0.5f)return 0;
 dot=R(dot/length);
 double cosine=thug_platform_cos(R((double)degrees*0.01745329238474369f));
 if(!(dot>=0)&&cosine>=0)return 1;
 return dot<cosine;
}
extern const ThugComponentMethods thug_skater_matrix_methods_draft;
/* 00513fd0, 00513fe0. */
void thug_skater_matrix_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_matrix_methods_draft);thug_component_destroy(p);}
void *thug_skater_matrix_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
 thug_skater_matrix_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 00514010. Physics may appear later in the owner's component list. */
void thug_skater_matrix_finalize_draft(void *p){put(p,0x5c,(uintptr_t)thug_object_find_component(ptr(p,12),0x5bd63b29));}
/* 00514030. The original copies raw matrix words, including overlaps. */
void thug_skater_matrix_update_draft(void *p){thug_matrix_copy(vector(p,0x18),vector(ptr(p,0x5c),0x18));}
/* 00514430. The empty initializer deliberately leaves the zeroed matrix. */
void *thug_skater_matrix_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x60,m);
 if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_matrix_methods_draft);put(p,4,0xbf518e27);put(p,0x5c,0);}return p;
}
static void output(ThugScriptInstance *s,uint32_t name,uint32_t value,const ThugMemory *m){thug_script_set_float_bits(ptr(s,0x14),name,value,m);}
/* 00514040. Zero/one are handled predicates, two is the unhandled result. */
uint32_t thug_skater_matrix_command_draft(void *p,uint32_t name,const ThugScriptStructure *params,ThugScriptInstance *s,const ThugMemory *m){
 float local[4],angle=0;
 switch(name){
 case 0x8e7833be:
  angle=(float)R(thug_acos_approximate(num(ptr(p,12),0x8c))*57.2957763671875f);
  if(num(ptr(p,12),0x94)<0)angle=(float)R(360.0f-(double)angle);
  output(s,0xfd4bc03e,bits(angle),m);
  output(s,0x2315ef17,word(ptr(p,12),0x8c),m);output(s,0x26910cc0,word(ptr(p,12),0x94),m);return 1;
 case 0x97201739:
  copy_vector(local,ptr(p,12),0x8c);local[1]=0;
  angle=(float)thug_vector_angle_degrees(vector(ptr(p,12),0x8c),local);
  if(num(ptr(p,12),0x90)<0)angle=-angle;
  output(s,0xa733ba7a,bits(angle),m);output(s,0x21afff16,bits((float)R((double)angle-num(p,0x58))),m);
  put(p,0x58,bits(angle));return 1;
 case 0x5e269b2b:
  thug_script_get_float(params,0,&angle,1);
  return thug_platform_cos(R((double)angle*0.01745329238474369f))>num(p,0x2c);
 case 0xa0551543:{
  thug_script_get_float(params,0,&angle,1);void *physics=ptr(p,0x5c);
  double dot=R(R(R((double)num(p,0x30)*num(physics,0x80))+R((double)num(p,0x2c)*num(physics,0x7c)))+R((double)num(physics,0x78)*num(p,0x28)));
  return thug_platform_cos(R((double)angle*0.01745329238474369f))>dot;
 }
 case 0xa745c080:
  copy_vector(local,ptr(p,12),0xac);thug_vector_project_preserve_length(local,vector(p,0x28));
  return R(R((double)local[2]*num(p,0x38))-R((double)local[0]*num(p,0x40)))>0;
 case 0xc8c4d2f4:{
  copy_vector(local,ptr(p,12),0xac);thug_vector_project_preserve_length(local,vector(p,0x28));
  float cross[4];thug_vector_cross(cross,local,vector(p,0x38));return cross[1]<0;
 }
 case 0xd3313e92:
  thug_script_get_float(params,0,&angle,1);copy_vector(local,p,0x18);
  thug_vector_project_preserve_length(local,vector(ptr(p,0x5c),0x78));
  return thug_vector_angle_exceeds_draft(local,vector(p,0x18),angle)!=0;
 case 0xb992f3cc:{
  ThugScriptPair pair;thug_script_pair_initialize(&pair);thug_script_get_pair(params,0,&pair,1);
  copy_vector(local,ptr(p,12),0xac);thug_vector_project_preserve_length(local,vector(p,0x28));
  if(!thug_vector_angle_exceeds_draft(local,vector(p,0x38),pair.x))return 0;
  return !thug_vector_angle_exceeds_draft(local,vector(p,0x38),pair.y);
 }
 default:return 2;
 }
}
static void frame_bridge(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_skater_matrix_update_draft(p);}
static uint32_t command_bridge(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){
 const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
 return thug_skater_matrix_command_draft(p,n,s,i,m);
}
static void initialize(void *p,const ThugScriptStructure *s){thug_component_empty_one(p,(void *)s);}
static void empty(void *p){(void)p;}
const ThugComponentMethods thug_skater_matrix_methods_draft={
 .dispose=thug_skater_matrix_delete_draft,.update=frame_bridge,.initialize=initialize,.finalize=thug_skater_matrix_finalize_draft,
 .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=command_bridge};
