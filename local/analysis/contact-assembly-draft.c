#include "sphere-query-draft.h"
#include "../../src/collision/probe.h"
#include "../../src/platform/math.h"
typedef struct {
 float arm[4],normal[4],inverse,impulse,depth;
 uint8_t active,cached,shape,reserved;
} ContactAssemblyRecord;
_Static_assert(sizeof(ContactAssemblyRecord)==48,"Original Rigidbody contact stride");
extern ContactAssemblyRecord thug_rigidbody_collision_contacts_draft[24];
extern float thug_rigidbody_rotated_points_draft[24][4];
extern float thug_rigidbody_rotated_spheres_draft[24][4];
extern void *thug_sphere_probe_construct_draft(void *,const float *,float);
extern uint8_t thug_sphere_probe_query_draft(void *,uint32_t,ThugCollisionQuery *);
ThugCollisionCache thug_rigidbody_contact_cache_draft; /* 006939e0. */
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static void *pointer(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return (void *)(uintptr_t)v;}
static float *fp(void *p,unsigned o){return (float *)((uint8_t *)p+o);}
static double r(double x){return __builtin_isnan(x)?-__builtin_nan(""):thug_platform_round_x87_single(x);}
static double add(double a,double b){return r(a+b);}
static double sub(double a,double b){return r(a-b);}
static double mul(double a,double b){return r(a*b);}
/* 0042c950. Build the shared broadphase cache, query point segments and shape
 * spheres in reverse order, and assemble the solver's ordered contact records.
 * As in the original engine, shape/contact storage must fit its24-slot arrays.
 * The original BSP globals remain the explicit existing query context. */
uint8_t thug_rigidbody_collect_contacts_draft(void *p,ThugCollisionQuery *query_state){
 float *position=fp(p,0x110),radius=*fp(p,0x198),lower[4],upper[4];ThugBounds bounds;
 for(unsigned j=0;j<4;j++){
  double extent=j==3?1:radius;
  upper[j]=(float)add(position[j],extent);lower[j]=(float)sub(position[j],extent);
 }
 thug_collision_segment_copy(bounds.min,lower,upper);
 thug_collision_cache_build(&thug_rigidbody_contact_cache_draft,&bounds);
 uint8_t *count=(uint8_t *)p+0x190,*active_count=count+1;*count=0;*active_count=0;
 if(half(p,0x8c)){
  ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
  probe.cache=&thug_rigidbody_contact_cache_draft;
  for(unsigned i=half(p,0x8c);i;){
   --i;float *offset=thug_rigidbody_rotated_points_draft[i];
   ContactAssemblyRecord *out=thug_rigidbody_collision_contacts_draft+(int8_t)*count;
   for(unsigned j=0;j<4;j++){probe.segment[j]=position[j];probe.segment[j+4]=(float)add(position[j],offset[j]);}
   out->active=thug_collision_probe_query(&probe,0,0,query_state);
   if(!out->active)continue;
   float dx=(float)sub(probe.segment[4],probe.segment[0]);
   double dy=sub(probe.segment[5],probe.segment[1]),dz=sub(probe.segment[6],probe.segment[2]);
   for(unsigned j=0;j<4;j++){out->arm[j]=offset[j];out->normal[j]=probe.normal[j];}
   float remaining=(float)sub(1,probe.fraction),scaled_z=(float)mul(dz,remaining);
   out->cached=0;out->impulse=0;
   double depth=add(add(mul(mul(dy,remaining),out->normal[1]),mul(scaled_z,out->normal[2])),mul(mul(dx,remaining),out->normal[0]));
   out->depth=(float)depth;out->active=depth<=0;out->shape=(uint8_t)i;
   if(out->active)++*active_count;
   ++*count;
  }
  if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
 }
 for(unsigned i=half(p,0x94);i;){
  --i;float *shape=fp(pointer(p,0x90),i*20),*offset=thug_rigidbody_rotated_spheres_draft[i],center[4];
  for(unsigned j=0;j<4;j++)center[j]=(float)add(offset[j],position[j]);
  float probe[0xb60/4];thug_sphere_probe_construct_draft(probe,center,shape[4]);
  const ThugCollisionCache *cache=&thug_rigidbody_contact_cache_draft;
  __builtin_memcpy((uint8_t *)probe+0xb5c,&cache,4);
  if(!thug_sphere_probe_query_draft(probe,0,query_state))continue;
  ThugSphereResultDraft *result=(void *)((uint8_t *)probe+0x14);
  for(unsigned j=result->count;j;){
   const ThugSphereHitDraft *hit=result->hits+--j;
   ContactAssemblyRecord *out=thug_rigidbody_collision_contacts_draft+(int8_t)*count;
   for(unsigned k=0;k<4;k++)out->arm[k]=(float)sub(hit->point[k],position[k]);
   for(unsigned k=0;k<4;k++)out->normal[k]=(float)sub(hit->point[k],probe[k]);
   float *normal=out->normal;
   float length=(float)r(__builtin_sqrt(add(add(mul(normal[0],normal[0]),mul(normal[1],normal[1])),mul(normal[2],normal[2]))));
   if(length!=0){double inverse=r(1.0/-length);for(unsigned k=0;k<4;k++)normal[k]=(float)mul(inverse,normal[k]);}
   else {normal[0]=0;normal[1]=1;normal[2]=0;normal[3]=1;}
   double facing=add(add(mul(hit->normal[2],normal[2]),mul(hit->normal[0],normal[0])),mul(normal[1],hit->normal[1]));
   if(facing<0)continue;
   double inward=add(add(mul(normal[2],out->arm[2]),mul(normal[1],out->arm[1])),mul(normal[0],out->arm[0]));
   if(inward>0)continue;
   out->cached=0;out->impulse=0;double depth=sub(length,shape[4]);
   out->depth=(float)depth;out->active=depth<=0;out->shape=(uint8_t)i;
   if(out->active)++*active_count;
   ++*count;
  }
 }
 return *active_count!=0;
}
