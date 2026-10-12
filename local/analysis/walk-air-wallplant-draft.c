/* 00526e00: walking wallplant qualification and synchronous transition script. */
#include <stddef.h>
#include "../../src/game/skater.h"
#include "../../src/core/timing.h"
#include "../../src/core/vector.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static float unsigned_float(uint32_t x){double v=(int32_t)x;if((int32_t)x<0)v=R(v+0x1p32);return (float)v;}
const char thug_walk_wallplant_text_draft[]="walking sticker slap...........\n";
void thug_walk_air_wallplant_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 uint8_t *input=ptr(p,0x1770);
 if(!input[0x1c0]||!input[0x40]||thug_input_button_elapsed((void *)(input+0x40))>30)return;
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 thug_vector_copy(probe.segment,(void *)((char *)p+0x24));
 float value;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x6da7f696,&value,1);
 probe.segment[1]=(float)R((double)probe.segment[1]+value);
 thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x99978d2b,&value,1);
 for(unsigned i=0;i<4;i++){
  double delta=R((double)value*number(p,0x48+4*i));if(i<3)delta=(float)delta;
  probe.segment[4+i]=(float)R(delta+probe.segment[i]);
 }
 if(!thug_collision_probe_query(&probe,0,0,q))goto done;
 if(thug_script_get_global_number(0xd5349cc6,0)>number(ptr(p,0x1788),0x11c))goto done;
 float elapsed=unsigned_float(thug_time_since(word(ptr(p,0x178c),0x4e0)));
 if(thug_script_get_global_number(0x82135dd7,0)>elapsed)goto done;
 elapsed=unsigned_float(thug_time_since(word(p,0x1c)));
 if(thug_script_get_global_number(0x4c2b6df3,0)>elapsed)goto done;
 if(thug_skater_try_wallplant(ptr(p,0x178c),0,1,0,q,d,m)){
  if(d&&d->print)d->print(d->context,thug_walk_wallplant_text_draft);
  thug_script_run_sync(0x7243098f,NULL,ptr(p,12),0,d,m);
 }
done:thug_collision_probe_release(&probe);
}
