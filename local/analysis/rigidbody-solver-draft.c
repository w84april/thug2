#include "../../src/game/components.h"
#include "../../src/game/drawing.h"
#include "../../src/core/matrix.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/script/schedule.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const char *)p+o,2);return v;}
static double r(double x){return thug_platform_round_x87_single(x);}
static double invalid(double x){return __builtin_isnan(x)?-__builtin_nan(""):r(x);}
static double nan_operand(double a,double b){if(!__builtin_isnan(a))return b;if(!__builtin_isnan(b))return a;return !__builtin_signbit(a)?a:b;}
static double mul(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a*b);}
static double add(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a+b);}
static double sub(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a-b);}
static double divide(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a/b);}
static double root(double a){return __builtin_isnan(a)?a:invalid(__builtin_sqrt(a));}
typedef struct {float arm[4],normal[4],inverse,impulse,depth;uint8_t active,cached,shape,reserved;} RigidbodyContact;
_Static_assert(sizeof(RigidbodyContact)==48,"Original contact stride");
RigidbodyContact thug_rigidbody_collision_contacts_draft[24]; /* 006949b0. */
uint8_t thug_rigidbody_debug_contacts_draft; /* 006939d5. */
double thug_rigidbody_contact_inverse_draft(void *,const float[4],const float[4]);
void thug_rigidbody_impact_draft(void *,float,const float[4],const ThugDiagnostics *,const ThugMemory *);
/* 005480a0 is the existing specimen's return-only debug renderer. */
static void debug_line(const float a[4],const float b[4]){(void)a;(void)b;thug_draw_style_noop(0);}
/* 00430140. Full contact solver: capped normal impulses, optional directional
 * friction, penetration correction, failure script and strongest-impact effect.
 * Contact/shape arrays are the original disjoint, capacity-bounded storage. */
void thug_rigidbody_solve_contacts_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 float previous_v[4],previous_w[4];__builtin_memcpy(previous_v,fp(p,0x120),16);__builtin_memcpy(previous_w,fp(p,0x140),16);
 float strongest=0,*v=fp(p,0x120),*w=fp(p,0x140);
 for(unsigned iteration=0;;){
  uint8_t settled=1;
  for(int i=(int8_t)((uint8_t *)p)[0x190];i;){RigidbodyContact *c=&thug_rigidbody_collision_contacts_draft[--i];if(!c->active)continue;float *a=c->arm,*n=c->normal;
   double cx=sub(mul(w[1],a[2]),mul(w[2],a[1]));float cy=(float)sub(mul(w[2],a[0]),mul(w[0],a[2])),cz=(float)sub(mul(w[0],a[1]),mul(w[1],a[0]));
   float vx=(float)add(cx,v[0]);double vy=add(cy,v[1]),vz=add(cz,v[2]);
   double approach=add(add(mul(vz,n[2]),mul(vx,n[0])),mul(vy,n[1]));float speed=(float)approach;
   if(approach>0)continue;settled=0;if(-speed>strongest)strongest=-speed;
   float bounce=(float)-mul(speed,*fp(p,0x2c));
   if(!c->cached){c->inverse=(float)thug_rigidbody_contact_inverse_draft(p,n,a);c->cached=1;}
   double impulse=mul(sub(bounce,speed),c->inverse),dy=mul(n[1],impulse),dz=mul(n[2],impulse),dw=mul(n[3],impulse);float dx=(float)mul(n[0],impulse);
   c->impulse=(float)add(impulse,c->impulse);
   v[0]=(float)add(dx,v[0]);v[1]=(float)add(dy,v[1]);v[2]=(float)add(dz,v[2]);v[3]=(float)add(dw,v[3]);
   float tx=(float)sub(mul(dz,a[1]),mul(dy,a[2])),ty=(float)sub(mul(dx,a[2]),mul(dz,a[0]));double tz=sub(mul(dy,a[0]),mul(dx,a[1]));
   float da[3]={(float)mul(tx,*fp(p,0x18)),(float)mul(ty,*fp(p,0x18)),(float)mul(tz,*fp(p,0x18))};
   for(unsigned j=0;j<3;j++)w[j]=(float)add(da[j],w[j]);w[3]=(float)add(mul(*fp(p,0x18),0),w[3]);
  }
  if(++iteration==20){
   if(word(p,0xd0))thug_script_execute(thug_object_spawn_attached_script(ptr(p,12),word(p,0xd0),ptr(p,0xd4),0,0,d,m),d,m);
   else {v[0]=v[1]=v[2]=w[0]=w[1]=w[2]=0;v[3]=w[3]=1;}return;
  }
  if(half(p,0x8c)==1||settled)break;
 }
 for(int i=(int8_t)((uint8_t *)p)[0x190];i;){RigidbodyContact *c=&thug_rigidbody_collision_contacts_draft[--i];if(!c->active)continue;float *a=c->arm,*n=c->normal;
  double cx=sub(mul(previous_w[1],a[2]),mul(previous_w[2],a[1])),cy=sub(mul(previous_w[2],a[0]),mul(previous_w[0],a[2]));float cz=(float)sub(mul(previous_w[0],a[1]),mul(previous_w[1],a[0]));
  float vx=(float)add(cx,previous_v[0]);double vy=add(cy,previous_v[1]),vz=add(cz,previous_v[2]);
  double normal=-add(add(mul(vz,n[2]),mul(vx,n[0])),mul(vy,n[1]));
  float tangent[4]={(float)add(mul(normal,n[0]),vx),(float)add((float)mul(normal,n[1]),vy),(float)add((float)mul(normal,n[2]),vz),(float)add((float)mul(normal,n[3]),previous_v[3])};
  if(word(p,0x88)){
   void *shape=(char *)ptr(p,0x88)+(int8_t)c->shape*20;
   if(((uint8_t *)shape)[16]){
    float direction[4];thug_matrix_rotate_vector(fp(p,0x150),direction,shape);
    double dot=add(add(mul(direction[0],n[0]),mul(direction[2],n[2])),mul(direction[1],n[1]));
    direction[0]=(float)sub(direction[0],mul(dot,n[0]));for(unsigned j=1;j<4;j++)direction[j]=(float)sub(direction[j],(float)mul(dot,n[j]));
    double length=root(add(add(mul(direction[2],direction[2]),mul(direction[1],direction[1])),mul(direction[0],direction[0])));
    if(length>0.0010000000474974513f){double scale=divide(1,length);for(unsigned j=0;j<4;j++)direction[j]=(float)mul(direction[j],scale);thug_vector_project_axis(tangent,direction);}
   }
  }
  double length=root(add(add(mul(tangent[2],tangent[2]),mul(tangent[1],tangent[1])),mul(tangent[0],tangent[0])));float speed=(float)length;
  if(length<0.0010000000474974513f)continue;
  double scale=divide(1,speed);for(unsigned j=0;j<4;j++)tangent[j]=(float)mul(tangent[j],scale);
  double impulse=mul(thug_rigidbody_contact_inverse_draft(p,tangent,a),speed);float limit=(float)mul(c->impulse,*fp(p,0x30));if(impulse>limit)impulse=limit;impulse=-impulse;
  double dx=mul(tangent[0],impulse);float dy=(float)mul(tangent[1],impulse),dz=(float)mul(tangent[2],impulse),dw=(float)mul(tangent[3],impulse);
  double tx=sub(mul(dz,a[1]),mul(dy,a[2])),ty=sub(mul(dx,a[2]),mul(dz,a[0]));float tz=(float)sub(mul(dy,a[0]),mul(dx,a[1]));
  float da[4]={(float)mul(tx,*fp(p,0x18)),(float)mul(ty,*fp(p,0x18)),(float)mul(tz,*fp(p,0x18)),(float)mul(*fp(p,0x18),0)};
  double dv[]={dx,dy,dz,dw};for(unsigned j=0;j<4;j++){v[j]=(float)add(dv[j],v[j]);w[j]=(float)add(da[j],w[j]);previous_v[j]=(float)add(dv[j],previous_v[j]);previous_w[j]=(float)add(da[j],previous_w[j]);}
 }
 float dt=(float)thug_frame_duration();
 for(int i=(int8_t)((uint8_t *)p)[0x190];i;){RigidbodyContact *c=&thug_rigidbody_collision_contacts_draft[--i];if(!c->active)continue;float *a=c->arm,*n=c->normal;
  double amount=-mul(mul(c->depth,*fp(p,0x34)),dt);float dv[4];for(unsigned j=0;j<4;j++)dv[j]=(float)mul(amount,n[j]);
  double tx=sub(mul(dv[2],a[1]),mul(dv[1],a[2])),ty=sub(mul(dv[0],a[2]),mul(dv[2],a[0]));float tz=(float)sub(mul(dv[1],a[0]),mul(dv[0],a[1]));
  float dax=(float)mul(tx,*fp(p,0x18)),daw=(float)mul(*fp(p,0x18),0);double day=mul(ty,*fp(p,0x18)),daz=mul(tz,*fp(p,0x18));
  for(unsigned j=0;j<4;j++)v[j]=(float)add(dv[j],v[j]);w[0]=(float)add(dax,w[0]);w[1]=(float)add(day,w[1]);w[2]=(float)add(daz,w[2]);w[3]=(float)add(daw,w[3]);
  if(thug_rigidbody_debug_contacts_draft){float from[4],to[4];for(unsigned j=0;j<4;j++){from[j]=(float)add(a[j],*fp(p,0x110+4*j));to[j]=(float)add(from[j],mul(dv[j],60));}debug_line(from,to);}
 }
 for(int i=(int8_t)((uint8_t *)p)[0x190];i;){RigidbodyContact *c=&thug_rigidbody_collision_contacts_draft[--i];if(!c->active)continue;float point[4];for(unsigned j=0;j<4;j++)point[j]=(float)add(c->arm[j],*fp(p,0x110+4*j));thug_rigidbody_impact_draft(p,strongest,point,d,m);break;}
}
