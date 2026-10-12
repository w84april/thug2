/* Candidate0052a2c0: original Walk speed-parent integration.
 * The two recognized animation checksum commands remain explicit boundaries;
 * this parent only sends the original unhandled bd4edd44 command. */
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
extern void thug_animation_component_speed_draft(ThugAnimationComponent *,float,uint32_t,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
/* 00419950 prefix, not a claimed complete recovery. The original returns2
 * for every other checksum, including the constant used by0052a2c0. */
uint32_t thug_animation_checksum_prefix_draft(void *component,uint32_t key,ThugScriptStructure *parameters,ThugScriptInstance *script){
 (void)component;(void)parameters;(void)script;
 if(key==0x0b1e7291||key==0xea6d0efd)__builtin_trap();
 return 2;
}
const ThugComponentMethods thug_animation_checksum_pending_methods_draft={.checksum=thug_animation_checksum_prefix_draft};
static void command(void *walk,float ratio,const ThugMemory *memory){
 ThugScriptStructure *parameters=thug_script_structure_allocate(8,memory);
 if(parameters)thug_script_structure_initialize(parameters);
 thug_script_set_float_bits(parameters,0xf0d90109,word(&ratio,0),memory);
 void *component=ptr(walk,0x1774);const ThugComponentMethods *methods=ptr(component,0);
 methods->checksum(component,0xbd4edd44,parameters,NULL);
 if(parameters){thug_script_structure_destroy(parameters,memory);thug_script_structure_free(parameters,memory);}
}
/* 0052a2c0,760 bytes. The Win32 exception-chain bookkeeping is host ABI. */
void thug_walk_animation_speed_draft(void *walk,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 uint32_t mode=word(walk,0x700);
 if(mode==1){
  float span=number(walk,0x17b0);if(!(span>0))return;
  float ratio=(float)R((double)number(walk,0x704)/span);
  thug_animation_component_speed_draft(ptr(walk,0x1774),ratio,0,0,0,diagnostics,memory);
  if(*((uint8_t *)ptr(walk,0x1780)+0x24)){
   ratio=(float)R((double)number(walk,0x704)/number(walk,0x17b0));command(walk,ratio,memory);
  }
 }else if(mode==2||mode==3){
  float span;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),mode==2?0x1a47ffab:0x0ab2db54,&span,1);
  float ratio=(float)R((double)number(walk,0x704)/span);command(walk,ratio,memory);
  uint32_t send=0;
  if(mode==3&&thug_network_is_active(thug_network_state)&&!(__builtin_fabs(R((double)ratio-number(walk,0x18e0)))<.10000000149011612f)){
   __builtin_memcpy((char *)walk+0x18e0,&ratio,4);send=1;
  }
  thug_animation_component_speed_draft(ptr(walk,0x1774),ratio,send,0,0,diagnostics,memory);
 }
}

#include "../../src/core/timing.h"
#include "../../src/script/delivery.h"
extern void thug_walk_read_input_draft(void *),thug_walk_read_owner_draft(void *),thug_walk_score_decay_draft(void *);
extern void thug_walk_transition_frame_draft(void *,const ThugMemory *);
extern void thug_walk_critical_point_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *);
extern void thug_walk_decay_model_offset_draft(void *),thug_walk_restore_up_draft(void *),thug_walk_write_owner_draft(void *),thug_walk_rotate_owner_draft(void *),thug_walk_update_camera_draft(void *);
extern void thug_walk_filter_speed_event_draft(void *,uint32_t);
extern uint32_t *thug_skater_construction_boundary_draft;
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static uint8_t byte(const void *p,unsigned o){return *((const uint8_t *)p+o);}
static void pb(void *p,unsigned o,uint8_t v){*((uint8_t *)p+o)=v;}
static void boundary(void *p,uint32_t address){uint32_t *b=thug_skater_construction_boundary_draft;if(b){b[0]=address;b[1]=0;b[2]=(uintptr_t)p;b[3]=1;}__builtin_trap();}
/* Partial0052d4b0: the original animation-state frame now reaches its return.
 * Other movement state handlers and later ground validation still stop at their
 * real boundaries. This partial function earns no recovered-routine count. */
void thug_walk_update_animation_prefix_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 uint32_t previous=word(p,0x78);
 if(byte(p,0x9a)&&!byte(ptr(p,0x1770),0x100))pb(p,0x9a,0);
 put(p,0x7c,previous);put(p,0x78,0);thug_walk_read_input_draft(p);thug_walk_read_owner_draft(p);
 __builtin_memcpy((char *)p+0x68,(char *)p+0x24,16);fp(p,0x80,thug_frame_duration());pb(p,0x718,0);
 fp(p,0x28,R((double)number(p,0x28)-number(p,0x714)));thug_walk_score_decay_draft(p);
 uint32_t state=word(p,0x18);
 if(state!=4){const uint32_t handlers[]={0x52d300,0x52cef0,0x440bf0,0x4425b0};boundary(p,state<4?handlers[state]:0x52d563);}
 thug_walk_transition_frame_draft(p,m);
 if(byte(ptr(p,0x1780),0x26))return;
 if(!byte(p,0x718)){
  float rate;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x9b3388fa,&rate,1);
  double value=number(p,0x714),factor=R((double)rate*number(p,0x80));fp(p,0x714,R(R(-value*factor)+value));
 }
 fp(p,0x28,R((double)number(p,0x714)+number(p,0x28)));
 if(word(p,0x18)==0&&thug_elapsed_time()+thug_timer_offset-word(p,0x1c)>500)boundary(p,0x527600);
 thug_walk_critical_point_draft(p,q,d);thug_walk_decay_model_offset_draft(p);
 if(word(p,0x18)<2)boundary(p,0x527080);
 thug_walk_restore_up_draft(p);thug_walk_write_owner_draft(p);thug_walk_rotate_owner_draft(p);thug_walk_filter_speed_event_draft(p,previous);
 thug_object_emit_event(ptr(p,12),word(p,0x78),NULL,d,m);thug_walk_animation_speed_draft(p,d,m);thug_walk_update_camera_draft(p);
 thug_skater_update_focus_input(ptr(p,0x178c),d,m);
 int32_t counter=(int32_t)word(p,0x710);if(counter>0){put(p,0x710,(uint32_t)--counter);if(!counter)pb(p,0x70c,0);}
}
