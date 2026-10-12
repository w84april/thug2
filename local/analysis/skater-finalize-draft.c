/* Original SkaterFinalizePhysics lifecycle and complete per-frame propagation. */
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/core/matrix.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void putbyte(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
#define R thug_platform_round_x87_single
/* 00405480. Repair axes shorter than0.99. X sums Z/X/Y, Y and Z sum X/Y/Z;
 * only the Y length spills to float. Unordered lengths are not short. */
uint8_t thug_matrix_repair_basis_draft(float matrix[16]){
 double lengths[3];
 for(unsigned i=0;i<3;i++){
  const float *v=matrix+i*4;
  double x=R((double)v[0]*v[0]),y=R((double)v[1]*v[1]),z=R((double)v[2]*v[2]);
  lengths[i]=R(__builtin_sqrt(i?R(R(x+y)+z):R(R(z+x)+y)));
 }
 lengths[1]=(float)lengths[1];
 unsigned bad[3],count=0;for(unsigned i=0;i<3;i++){bad[i]=lengths[i]<(double)0.99f;count+=bad[i];}
 if(!count)return 0;
 if(count>=2){for(unsigned i=0;i<16;i++)matrix[i]=(i%5==0)?1:0;return 1;}
 unsigned axis=bad[0]?0:bad[1]?1:2;float result[4];
 thug_vector_cross(result,matrix+4*((axis+1)%3),matrix+4*((axis+2)%3));
 thug_vector_normalize(result);thug_vector_copy(matrix+axis*4,result);return 1;
}
/* 005138b0. Preserve argument bits unless an ordered comparison exceeds1. */
void thug_skater_animation_speed_draft(void *p,float value){
 uint32_t raw;__builtin_memcpy(&raw,&value,4);put(p,0x104,raw);if(value>1)put(p,0x104,0x3f800000);
}
extern const ThugComponentMethods thug_skater_finalize_methods_draft;
/* 00511280. Successful allocation constructs the base and clears both links. */
void *thug_skater_finalize_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x20,m);if(!p)return 0;thug_component_construct(p);
 put(p,0,(uintptr_t)&thug_skater_finalize_methods_draft);put(p,4,0x9b373e58);put(p,0x18,0);put(p,0x1c,0);return p;
}
/* 00511010 /00511020. */
void thug_skater_finalize_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_finalize_methods_draft);thug_component_destroy(p);}
void *thug_skater_finalize_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_skater_finalize_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00511050. Preserve owner rereads between component searches. */
void thug_skater_finalize_bind_draft(void *p){
 void *physics=thug_object_find_component(ptr(p,12),0x5bd63b29),*owner=ptr(p,12);
 put(p,0x18,(uintptr_t)physics);put(p,0x1c,(uintptr_t)thug_object_find_component(owner,0x43686585));
}
/* 00511080. Dependencies are initialized by the owning skater. */
void thug_skater_finalize_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;
 if(byte(ptr(p,0x18),0x256)&&word(ptr(p,0x1c),0x18)!=3){
  putbyte(ptr(p,0x1c),0xf4,0);
  if(word(ptr(p,0x1c),0x18)==1){void *owner=ptr(p,12);
   if(__builtin_fabsf(number(owner,0xac))<1&&__builtin_fabsf(number(owner,0xb4))<1)putbyte(ptr(p,0x1c),0xf4,1);
  }
 }
 if(word(ptr(p,0x1c),0x18)!=1)putbyte(ptr(p,0x1c),0xf4,0);
 for(unsigned k=0;k<2;k++){
  void *physics=ptr(p,0x18),*state=ptr(p,0x1c);
  for(unsigned i=0;i<4;i++)put(state,0xf8+16*k+4*i,word(physics,0x58+16*k+4*i));
 }
 thug_matrix_orthogonalize((float *)((char *)ptr(p,12)+0x6c),1);
 thug_matrix_orthogonalize((float *)((char *)ptr(p,0x18)+0x18),1);
 if(thug_matrix_repair_basis_draft((float *)((char *)ptr(p,12)+0x6c))){
  void *physics=ptr(p,0x18);thug_matrix_copy((float *)((char *)physics+0x18),(const float *)((char *)ptr(physics,12)+0x6c));
 }
 thug_matrix_copy((float *)((char *)ptr(p,12)+0xc0),(const float *)((char *)ptr(p,0x18)+0x18));
 void *sound=thug_object_find_component(ptr(p,12),0x187574fa);
 putbyte(sound,0x1e,byte(ptr(p,0x1c),0x58));putbyte(sound,0x1c,byte(ptr(p,0x1c),0xe1));
 void *animation=thug_object_find_component(ptr(p,12),0xb5f1e9d2),*owner=ptr(p,12);
 double x=number(owner,0xac),z=number(owner,0xb4);
 float speed=(float)R(__builtin_sqrt(R(R(x*x)+R(z*z))));
 double limit=thug_skater_stat_parameter(owner,0xcc5f87aa);
 float ratio=(float)R((double)speed/limit);
 /* x87 invalid division stores its negative indefinite, not Wasm's NaN. */
 if((speed==0&&limit==0)||(__builtin_isinf(speed)&&__builtin_isinf(limit))){uint32_t raw=0xffc00000;__builtin_memcpy(&ratio,&raw,4);}
 thug_skater_animation_speed_draft(animation,ratio);
 uint8_t value=byte(ptr(p,0x1c),0x70),old=byte(animation,0x100);putbyte(animation,0xff,value);
 value=byte(ptr(p,0x1c),0x58);uint8_t dirty=byte(animation,0xfd)|(old!=value);old=byte(animation,0x60);
 putbyte(animation,0xfd,dirty);putbyte(animation,0x100,value);
 value=byte(ptr(p,0x1c),0xe1);dirty=byte(animation,0xfd)|(old!=value);putbyte(animation,0xfd,dirty);putbyte(animation,0x60,value);
 uint32_t state=word(ptr(p,0x1c),0x18),previous=word(animation,0x74);
 putbyte(animation,0xfd,byte(animation,0xfd)|(previous!=state));put(animation,0x74,state);
}
static void empty(void *p){(void)p;}
static void empty_init(void *p,const ThugScriptStructure *s){(void)p;(void)s;}
static uint32_t command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;return 2;}
const ThugComponentMethods thug_skater_finalize_methods_draft={
 .dispose=thug_skater_finalize_delete_draft,.update=thug_skater_finalize_update_draft,.initialize=empty_init,
 .finalize=thug_skater_finalize_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,
 .suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,
 .unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=command};
