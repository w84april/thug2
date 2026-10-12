/* Candidates for the event-dependent camera-facing portion of the Walk frame. */
#include <stdint.h>
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
#define R thug_platform_round_x87_single
/* 00525f70,53 bytes. Keep sequential stores, including aliased facing sources. */
void thug_walk_camera_facing_draft(void *camera,const float *facing,float duration){
 ((uint8_t *)camera)[0x78]=1;
 for(unsigned i=0;i<4;i++)put(camera,0x7c+4*i,word(facing,4*i));
 __builtin_memcpy((char *)camera+0x8c,&duration,4);
}
/* 00529f80,498 bytes. Select a facing override from the current movement event. */
void thug_walk_update_camera_draft(void *p){
 uint32_t event=word(p,0x78);void *camera=ptr(p,0x1760);const float *facing=(const float *)((char *)p+0x48);
 if(event==0x4194ecca){thug_walk_camera_facing_draft(camera,facing,.05f);return;}
 if(event==0x2d9815c3){float copy[4];__builtin_memcpy(copy,facing,16);thug_vector_rotate_y(copy,-.949999988079071f);thug_walk_camera_facing_draft(camera,copy,.05f);return;}
 if(event==0x279b1f0b){
  float copy[4];__builtin_memcpy(copy,facing,16);
  /* Original inline fsin/fcos results spill to32 bits before the products. */
  float sine=(float)thug_platform_sin(.949999988079071),cosine=(float)thug_platform_cos(.949999988079071);
  double x=copy[0],z=copy[2];copy[0]=(float)R(R((double)cosine*x)+R((double)sine*z));copy[2]=(float)R(R(-R((double)sine*x))+R((double)cosine*z));
  thug_walk_camera_facing_draft(camera,copy,.05f);return;
 }
 if(event==0x4fe6069c){if(word(p,0x1944))facing=(const float *)((char *)p+0x191c);thug_walk_camera_facing_draft(camera,facing,.05f);return;}
 if(event==0xaf5abc82||event==0xc84243da||event==0xfec9dded){thug_walk_camera_facing_draft(camera,facing,.05f);return;}
 ((uint8_t *)camera)[0x78]=0;
}
