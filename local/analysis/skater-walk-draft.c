/* Original Walk lifecycle and common movement-frame setup. State handlers remain pending. */
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/game/grind.h"
#include "../../src/collision/probe.h"
#include "../../src/collision/moving.h"
#include "../../src/core/vector.h"
#include "../../src/core/number.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void pb(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static void copy(void *p,unsigned at,const void *s,unsigned from,unsigned n){for(unsigned i=0;i<n;i++)put(p,at+i*4,word(s,from+i*4));}
#define R thug_platform_round_x87_single
extern const ThugComponentMethods thug_walk_pending_methods_draft;
/* 00528880 /00528890. The embedded record owns a collision probe at+1c. */
void *thug_walk_contact_construct_draft(void *p){thug_collision_probe_initialize((void *)((char *)p+0x1c));return p;}
void thug_walk_contact_destroy_draft(void *p){void *reference=(char *)p+0xb4;if(word(reference,0)){thug_object_reference_unlink(ptr(reference,0),reference);put(reference,0,0);}}
/* 0052a190. CRT array construction is the forward eight-record loop; no
 * allocation occurs there. The original SEH cleanup is for exceptional exits. */
void *thug_walk_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_walk_pending_methods_draft);
 for(unsigned i=0;i<8;i++)thug_walk_contact_construct_draft((char *)p+0xa0+i*0xcc);
 thug_collision_cache_initialize((void *)((char *)p+0x790));thug_collision_probe_initialize((void *)((char *)p+0x17b4));
 for(unsigned o=0x1770;o<=0x178c;o+=4)put(p,o,0);
 put(p,4,0x726e85aa);put(p,0x84,0);put(p,0x88,0);put(p,0x8c,0);put(p,0x90,0x3f800000);
 put(p,0x189c,0);put(p,0x18a0,0);put(p,0x18a4,0);put(p,0x18a8,0x3f800000);put(p,0x72c,0);pb(p,0x1958,0);return p;
}
/* 0052a5c0 /005288b0 /0052a290. Destruction detaches contacts in reverse. */
void *thug_walk_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1960,m);return p?thug_walk_construct_draft(p):0;}
void thug_walk_destroy_draft(void *p){
 put(p,0,(uintptr_t)&thug_walk_pending_methods_draft);void *reference=(char *)p+0x184c;
 if(word(reference,0)){thug_object_reference_unlink(ptr(reference,0),reference);put(reference,0,0);}
 thug_collision_cache_destroy((void *)((char *)p+0x790));
 for(unsigned i=8;i;i--)thug_walk_contact_destroy_draft((char *)p+0xa0+(i-1)*0xcc);
 thug_component_destroy(p);
}
void *thug_walk_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_walk_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00526060 /00525fb0. Optional camera ownership and nine component links. */
void thug_walk_initialize_draft(void *p,const ThugScriptStructure *s){uint32_t key;
 if(thug_script_get_checksum(s,0xc4e311fa,&key,0)){void *owner=thug_object_find_global(0,key);put(p,0x175c,(uintptr_t)owner);put(p,0x1760,(uintptr_t)thug_object_find_component(owner,0xc7d37ec2));}
 put(p,0x710,0);
}
void thug_walk_bind_draft(void *p){
 const uint32_t types[]={0x27d7cd28,0x7149b753,0x286a8d26,0xe594f0a2,0xd9151d4d,0x408d2aa9,0x43686585,0x5bd63b29,0x380d909a};
 for(unsigned i=0;i<9;i++){void *result=thug_object_find_component(ptr(p,12),types[i]);put(p,0x1770+i*4,(uintptr_t)result);}
}
extern double thug_input_stick_magnitude_draft(void *,float,float,float);
/* Required walk parameters are supplied by the original QB global structure. */
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
/* 00527f20. Camera-relative direction, dead zone, analog/digital speed and
 * the retained ground direction. FSIN/FCOS use the existing platform adapter. */
void thug_walk_read_input_draft(void *p){
 void *camera=ptr(p,0x175c),*pad=(char *)ptr(p,0x1770)+0x20;
 float x=(float)-(double)number(camera,0x8c),z=(float)-(double)number(camera,0x94);
 double length=R(__builtin_sqrt(R(R((double)z*z)+R((double)x*x))));
 if(length>0){double inverse=R(1/length);x=(float)R((double)x*inverse);z=(float)R((double)z*inverse);}
 float angle=number(pad,0x228);double dead=R((double)parameter(0x4676a268)*0.01745329238474369f);
 if(dead>__builtin_fabs((double)angle))angle=0;
 double sine=thug_platform_sin(angle),cosine=thug_platform_cos(angle);
 fp(p,0x84,R(R((double)x*cosine)-R((double)z*sine)));fp(p,0x8c,R(R((double)z*cosine)+R((double)x*sine)));
 if(number(pad,0x208)==0&&number(pad,0x20c)==0){
  pb(p,0x99,0);
  if(number(pad,0x22c)==0){put(p,0x94,0);pb(p,0x98,0);}
  else if(word(p,0x18)==0&&!byte(pad,0x1a0)){fp(p,0x94,thug_walk_parameter((uintptr_t)p,0xc1528f7f));pb(p,0x98,1);}
  else {put(p,0x94,0x3f800000);pb(p,0x98,1);}
 }else{
  pb(p,0x99,1);double value=R(thug_input_stick_magnitude_draft(pad,number(pad,0x208),number(pad,0x20c),number(pad,0x228))*1.1764705181121826f);
  fp(p,0x94,value);if(value<1)pb(p,0x98,0);else{put(p,0x94,0x3f800000);pb(p,0x98,1);}
 }
 if(word(p,0x18)==0&&byte(p,0x70c))copy(p,0x84,p,0x48,4);
}
/* 00527db0. Load live owner vectors, flatten velocity/forward and retain the
 * vertical values. An almost vertical forward vector falls back to -up. */
void thug_walk_read_owner_draft(void *p){
 copy(p,0x24,ptr(p,12),0x4c,4);copy(p,0x34,ptr(p,12),0xac,4);put(p,0x38,0);
 void *owner=ptr(p,12);put(p,0x44,word(owner,0xb0));copy(p,0x58,owner,0x7c,4);
 copy(p,0x48,ptr(p,12),0x8c,4);put(p,0x744,word(p,0x4c));put(p,0x4c,0);
 double x=number(p,0x48),y=number(p,0x4c),z=number(p,0x50);
 double length=R(__builtin_sqrt(R(R(R(x*x)+R(y*y))+R(z*z))));
 if(length<(double).001f){
  owner=ptr(p,12);float values[4];for(unsigned i=0;i<4;i++)values[i]=(float)-(double)number(owner,0x7c+i*4);
  __builtin_memcpy((char *)p+0x48,values,16);put(p,0x4c,0);thug_vector_normalize((float *)((char *)p+0x48));
  fp(p,0x5c,R((double)number(p,0x5c)+.01f));thug_vector_normalize((float *)((char *)p+0x58));
 }else{
  double inverse=R(1/length);for(unsigned i=0;i<4;i++)fp(p,0x48+i*4,R((double)number(p,0x48+i*4)*inverse));
 }
}
/* 00528370. Integer score truncation decides between full charge and decay. */
void thug_walk_score_decay_draft(void *p){
 void *score=ptr(thug_object_find_component(ptr(p,12),0xd262802f),0x18);
 double value=R((double)(int32_t)word(score,0x14)*number(score,0x60));
 if((int32_t)thug_truncate_double_low_word(value)>0){put(p,0x1868,0x3f800000);return;}
 float rate=parameter(0x3fb31dfc);double result=R((double)number(p,0x1868)-R(thug_frame_duration()*rate));
 if(result<0)result=0;fp(p,0x1868,result);
}
extern uint32_t *thug_skater_construction_boundary_draft;
/* PREFIX ONLY of0052d4b0: common frame setup, then an explicit state-handler
 * boundary. This is neither a completed frame nor a recovered routine count. */
void thug_walk_update_prefix_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;uint32_t previous=word(p,0x78);
 if(byte(p,0x9a)&&!byte(ptr(p,0x1770),0x100))pb(p,0x9a,0);
 put(p,0x7c,previous);put(p,0x78,0);thug_walk_read_input_draft(p);thug_walk_read_owner_draft(p);
 copy(p,0x68,p,0x24,4);fp(p,0x80,thug_frame_duration());pb(p,0x718,0);
 fp(p,0x28,R((double)number(p,0x28)-number(p,0x714)));thug_walk_score_decay_draft(p);
 const uint32_t handlers[]={0x52d300,0x52cef0,0x440bf0,0x4425b0,0x52ad10};uint32_t state=word(p,0x18),*b=thug_skater_construction_boundary_draft;
 if(b){b[0]=state<5?handlers[state]:0x52d563;b[1]=0;b[2]=(uintptr_t)p;b[3]=1;}__builtin_trap();
}
static void empty(void *p){(void)p;}
static uint32_t command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;return 2;}
const ThugComponentMethods thug_walk_pending_methods_draft={.dispose=thug_walk_delete_draft,.update=thug_walk_update_prefix_draft,.initialize=thug_walk_initialize_draft,.finalize=thug_walk_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=command};
