/* 00527600: walk-to-transfer eligibility, original trajectory and events. */
#include "../../src/game/skater.h"
#include "../../src/game/grind.h"
#include "../../src/game/collision_events.h"
extern void thug_walk_change_state_draft(void *,uint32_t);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint8_t byte(const void *p,unsigned o){return *((const uint8_t *)p+o);}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
uint8_t thug_walk_try_transfer_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(byte(p,0x9b)||byte(ptr(p,0x1780),0x24)||!byte(ptr(p,0x1770),0xc0)||!byte(ptr(p,0x1770),0x120))return 0;
 float velocity[4];__builtin_memcpy(velocity,(char *)p+0x34,16);
 velocity[1]=(float)thug_walk_parameter((uintptr_t)p,0xc0491d2e);
 if(!thug_skater_find_transfer(ptr(p,0x178c),0,(void *)((char *)p+0x24),(void *)((char *)p+0x68),velocity,(void *)((char *)p+0x768),q))return 0;
 if(byte(p,0x1864)){
  const uint32_t events[3]={2,4,0};
  thug_collision_event_from_probe(ptr(p,0x177c),events,(void *)((char *)p+0x17b4),d,m);
  if(byte(ptr(p,0x1780),0x26))return 1;
 }
 thug_walk_change_state_draft(p,1);
 __builtin_memcpy((char *)p+0x34,velocity,16);put(p,0x38,0);put(p,0x44,word(velocity,4));
 put(p,0x748,2);put(p,0x78,0x2eda83ea);return 1;
}
