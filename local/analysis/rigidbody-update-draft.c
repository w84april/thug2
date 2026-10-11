#include "../../src/game/components.h"
#include "../../src/game/drawing.h"
#include "../../src/game/object_registry.h"
#include "../../src/core/matrix.h"
#include "../../src/core/timing.h"
#include "../../src/collision/probe.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const char *)p+o,2);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static double invalid(double x){return __builtin_isnan(x)?-__builtin_nan(""):thug_platform_round_x87_single(x);}
static double nan_operand(double a,double b){if(!__builtin_isnan(a))return b;if(!__builtin_isnan(b))return a;return !__builtin_signbit(a)?a:b;}
static double mul(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a*b);}
static double add(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a+b);}
static double sub(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a-b);}
static double divide(double a,double b){return (__builtin_isnan(a)||__builtin_isnan(b))?nan_operand(a,b):invalid(a/b);}
static double root(double a){return __builtin_isnan(a)?a:invalid(__builtin_sqrt(a));}
extern float thug_rigidbody_rotated_points_draft[24][4],thug_rigidbody_rotated_spheres_draft[24][4],thug_rigidbody_rotated_contacts_draft[2][4];
extern uint8_t thug_rigidbody_debug_contacts_draft;
uint8_t thug_rigidbody_debug_shapes_draft; /* 006939d4. */
/* The PC binary routes these different debug drawing signatures to5480a0,
 * whose entire body is RET. Preserve caller traversal/arguments, no renderer. */
static void debug_line(const float a[4],const float b[4],uint32_t color,uint32_t zero,uint32_t one){(void)a;(void)b;(void)color;(void)zero;(void)one;thug_draw_style_noop(0);}
static void debug_sphere(const float c[4],float radius,const float m[16],uint32_t count,uint32_t color,uint32_t one){(void)c;(void)radius;(void)m;(void)count;(void)color;(void)one;thug_draw_style_noop(0);}
static void debug_marker(const float p[4],float size,uint32_t color,uint32_t one){(void)p;(void)size;(void)color;(void)one;thug_draw_style_noop(0);}
/* 0042d9d0. Complete optional debug traversal; original draw targets are noops. */
void thug_rigidbody_debug_draw_draft(void *p){
 uint32_t mode=word(p,0x10c),color=mode==0?0xffc80000:mode==1?(*fp(p,0x194)>0?0xff00c800:0xff0000c8):mode==2?0xff640064:0;
 for(unsigned i=half(p,0x8c);i;){--i;for(unsigned j=0;j<i;j++){
  float a[4],b[4];for(unsigned k=0;k<4;k++){a[k]=(float)add(thug_rigidbody_rotated_points_draft[i][k],*fp(p,0x110+4*k));b[k]=(float)add(thug_rigidbody_rotated_points_draft[j][k],*fp(p,0x110+4*k));}
  debug_line(a,b,color,0,1);
 }}
 for(unsigned i=half(p,0x94);i;){--i;float center[4];for(unsigned k=0;k<4;k++)center[k]=(float)add(thug_rigidbody_rotated_spheres_draft[i][k],*fp(p,0x110+4*k));
  debug_sphere(center,*fp(ptr(p,0x90),i*20+16),fp(p,0x150),12,color,1);
 }
 if(thug_rigidbody_debug_contacts_draft)debug_marker(fp(p,0x110),36,0xffc800c8,1);
 for(unsigned i=half(p,0x9c);i;){--i;void *c=(char *)ptr(p,0x98)+i*36;if(!((uint8_t *)c)[32])continue;
  float anchor[4];for(unsigned k=0;k<4;k++)anchor[k]=(float)add(thug_rigidbody_rotated_contacts_draft[i][k],*fp(p,0x110+4*k));
  debug_marker(anchor,24,0xffc86400,1);debug_marker(fp(c,16),24,0xffc80064,1);
 }
}
extern void thug_rigidbody_kick_draft(void *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_rigidbody_rotate_draft(void *);
extern void thug_rigidbody_integrate_draft(void *,float);
extern void thug_rigidbody_response_draft(void *,void *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_rigidbody_stop_draft(void *,const ThugDiagnostics *,const ThugMemory *);
extern uint8_t thug_rigidbody_collect_contacts_draft(void *,ThugCollisionQuery *);
extern void thug_rigidbody_solve_contacts_draft(void *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_rigidbody_constraints_draft(void *);
extern void thug_rigidbody_friction_draft(void *);
extern void thug_rigidbody_settle_draft(void *,const ThugDiagnostics *,const ThugMemory *);
/* 00430e20. Full update, including the five-impact fallback and subsequent
 * contact solving. Query/diagnostic/heap parameters replace original globals
 * according to the existing component ABI. Shapes and owner are disjoint. */
void thug_rigidbody_update_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m){
 if(word(p,0x10c)==2)return;
 float dt=(float)thug_frame_duration();
 if(*fp(p,0x194)>0)*fp(p,0x194)=(float)sub(*fp(p,0x194),dt);
 else if(!(word(p,0xf4)&2))thug_rigidbody_kick_draft(p,d,m);
 if(*fp(p,0x108)>=0){
  if(*fp(p,0x108)<=dt){
   typedef void (*Expire)(void *,const ThugDiagnostics *,const ThugMemory *);
   void *owner=ptr(p,12);((Expire *)ptr(owner,0))[6](owner,d,m);
  }else *fp(p,0x108)=(float)sub(*fp(p,0x108),dt);
 }
 if(!word(p,0x10c)){thug_matrix_copy(fp(ptr(p,12),0xc0),fp(p,0x150));return;}
 thug_rigidbody_rotate_draft(p);
 float remaining=dt;
 for(unsigned iteration=0;;){
  float step=remaining;ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
  for(unsigned j=0;j<4;j++)probe.segment[j]=*fp(p,0x110+4*j);
  float dx=(float)mul(remaining,*fp(p,0x120)),dy=(float)mul(remaining,*fp(p,0x124));
  double dz=mul(remaining,*fp(p,0x128));float pw=(float)add(mul(remaining,*fp(p,0x12c)),*fp(p,0x11c));
  double px=add(dx,*fp(p,0x110)),py=add(dy,*fp(p,0x114)),pz=add(dz,*fp(p,0x118));
  double halfdt2=mul(mul(remaining,remaining),.5);
  float gy=(float)mul(halfdt2,*fp(p,0x20)),gz=(float)mul(halfdt2,*fp(p,0x24)),gw=(float)mul(halfdt2,*fp(p,0x28));
  probe.segment[4]=(float)add(mul(halfdt2,*fp(p,0x1c)),px);
  probe.segment[5]=(float)add(gy,py);probe.segment[6]=(float)add(gz,pz);probe.segment[7]=(float)add(gw,pw);
  uint8_t hit=thug_collision_probe_query(&probe,0,0,query);
  if(hit){
   double x=sub(probe.segment[4],probe.segment[0]),y=sub(probe.segment[5],probe.segment[1]),z=sub(probe.segment[6],probe.segment[2]);
   double distance=root(add(add(mul(x,x),mul(y,y)),mul(z,z)));
   float *v=fp(p,0x120);double speed=root(add(add(mul(v[0],v[0]),mul(v[1],v[1])),mul(v[2],v[2])));
   step=(float)divide(sub(mul(distance,probe.fraction),6),speed);if(step<0)step=0;
  }
  thug_rigidbody_integrate_draft(p,step);
  if(hit)thug_rigidbody_response_draft(p,&probe,d,m);
  remaining=(float)sub(remaining,step);
  if(++iteration==5){thug_rigidbody_stop_draft(p,d,m);thug_collision_probe_release(&probe);break;}
  thug_collision_probe_release(&probe);if(!hit)break;
 }
 if(thug_rigidbody_collect_contacts_draft(p,query))thug_rigidbody_solve_contacts_draft(p,d,m);
 if(half(p,0x9c))thug_rigidbody_constraints_draft(p);
 thug_rigidbody_friction_draft(p);thug_rigidbody_settle_draft(p,d,m);
 float center[4];thug_matrix_rotate_vector(fp(p,0x150),center,fp(p,0xb0));
 float *position=fp(ptr(p,12),0x4c);for(unsigned j=0;j<4;j++)position[j]=(float)add(*fp(p,0x110+4*j),center[j]);
 thug_matrix_copy(fp(ptr(p,12),0x6c),fp(p,0x150));thug_matrix_copy(fp(ptr(p,12),0xc0),fp(p,0x150));
 __builtin_memcpy((char *)ptr(p,12)+0xac,(char *)p+0x120,16);
 if(thug_rigidbody_debug_shapes_draft)thug_rigidbody_debug_draw_draft(p);
}
extern void thug_object_manager_visit_draft(ThugObjectManager *,ThugObjectVisitor,void *);
typedef struct {ThugCollisionQuery *query;const ThugDiagnostics *diagnostics;const ThugMemory *memory;} UpdateManagerContext;
static void update_owner(void *owner,void *opaque){UpdateManagerContext *s=opaque;thug_object_update_components(owner,s->query,s->diagnostics,s->memory);}
/* 0045f4a0. Same visited-bit reservation, forward-list capture and mutation
 * restart as461cc0; each eligible object runs the actual45d920 body. */
void thug_composite_manager_update_draft(ThugObjectManager *manager,ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m){
 UpdateManagerContext context={query,d,m};thug_object_manager_visit_draft(manager,update_owner,&context);
}
