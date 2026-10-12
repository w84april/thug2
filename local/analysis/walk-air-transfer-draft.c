/* 00527510: transfer eligibility while airborne and moving-contact update. */
#include "../../src/game/skater.h"
#include "../../src/game/grind.h"
#include "../../src/game/moving_contact.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint8_t byte(const void *p,unsigned o){return *((const uint8_t *)p+o);}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
uint8_t thug_walk_air_transfer_draft(void *p,ThugCollisionQuery *q,const ThugMemory *m){
 if(byte(p,0x9b)||byte(ptr(p,0x1780),0x24)||!byte(ptr(p,0x1770),0xc0)||!byte(ptr(p,0x1770),0x120))return 0;
 float velocity[4];put(velocity,0,word(p,0x34));put(velocity,4,word(p,0x44));put(velocity,8,word(p,0x3c));put(velocity,12,0x3f800000);
 if(!thug_skater_find_transfer(ptr(p,0x178c),0,(void *)((char *)p+0x24),(void *)((char *)p+0x68),velocity,(void *)((char *)p+0x768),q))return 0;
 thug_skater_moving_contact_acquire(ptr(p,0x1784),(void *)((char *)p+0x17b4),m);
 __builtin_memcpy((char *)p+0x34,velocity,16);put(p,0x38,0);put(p,0x44,word(velocity,4));
 put(p,0x748,2);put(p,0x78,0x2eda83ea);return 1;
}
