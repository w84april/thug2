#include <stddef.h>
#include "../../src/game/animation.h"
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
extern void thug_walk_animation_speed_draft(void *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_ground_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern uint8_t thug_walk_try_transfer_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_validate_ground_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *);
#include "../../src/core/timing.h"
#include "../../src/script/delivery.h"
extern void thug_walk_read_input_draft(void *),thug_walk_read_owner_draft(void *),thug_walk_score_decay_draft(void *);
extern void thug_walk_transition_frame_draft(void *,const ThugMemory *);
extern void thug_walk_critical_point_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *);
extern void thug_walk_decay_model_offset_draft(void *),thug_walk_restore_up_draft(void *),thug_walk_write_owner_draft(void *),thug_walk_rotate_owner_draft(void *),thug_walk_update_camera_draft(void *);
extern void thug_walk_filter_speed_event_draft(void *,uint32_t);
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static uint8_t byte(const void *p,unsigned o){return *((const uint8_t *)p+o);}
static void pb(void *p,unsigned o,uint8_t v){*((uint8_t *)p+o)=v;}
/* Complete0052d4b0: all five state handlers and the original out-of-range fallthrough. */
extern void thug_walk_air_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_rail_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_walk_hang_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_walk_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 uint32_t previous=word(p,0x78);
 if(byte(p,0x9a)&&!byte(ptr(p,0x1770),0x100))pb(p,0x9a,0);
 put(p,0x7c,previous);put(p,0x78,0);thug_walk_read_input_draft(p);thug_walk_read_owner_draft(p);
 __builtin_memcpy((char *)p+0x68,(char *)p+0x24,16);fp(p,0x80,thug_frame_duration());pb(p,0x718,0);
 fp(p,0x28,R((double)number(p,0x28)-number(p,0x714)));thug_walk_score_decay_draft(p);
 uint32_t state=word(p,0x18);
 if(state==0)thug_walk_ground_draft(p,q,d,m);
 else if(state==1)thug_walk_air_frame_draft(p,q,d,m);
 else if(state==2)thug_walk_hang_frame_draft(p,q,d,m);
 else if(state==3)thug_walk_rail_frame_draft(p,q,d,m);
 else if(state==4)thug_walk_transition_frame_draft(p,m);
 if(byte(ptr(p,0x1780),0x26))return;
 if(!byte(p,0x718)){
  float rate;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x9b3388fa,&rate,1);
  double value=number(p,0x714),factor=R((double)rate*number(p,0x80));fp(p,0x714,R(R(-value*factor)+value));
 }
 fp(p,0x28,R((double)number(p,0x714)+number(p,0x28)));
 if(word(p,0x18)==0&&thug_elapsed_time()+thug_timer_offset-word(p,0x1c)>500){thug_walk_try_transfer_draft(p,q,d,m);if(byte(ptr(p,0x1780),0x26))return;}
 thug_walk_critical_point_draft(p,q,d);thug_walk_decay_model_offset_draft(p);
 if(word(p,0x18)<2)thug_walk_validate_ground_draft(p,q,d);
 thug_walk_restore_up_draft(p);thug_walk_write_owner_draft(p);thug_walk_rotate_owner_draft(p);thug_walk_filter_speed_event_draft(p,previous);
 thug_object_emit_event(ptr(p,12),word(p,0x78),NULL,d,m);thug_walk_animation_speed_draft(p,d,m);thug_walk_update_camera_draft(p);
 thug_skater_update_focus_input(ptr(p,0x178c),d,m);
 int32_t counter=(int32_t)word(p,0x710);if(counter>0){put(p,0x710,(uint32_t)--counter);if(!counter)pb(p,0x70c,0);}
}
