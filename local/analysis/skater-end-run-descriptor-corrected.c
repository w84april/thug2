/* Original run-ending component and its settings/network dependencies. */
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/script/delivery.h"
#include "../../src/script/schedule.h"
#include "../../src/network/queue.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void clear(void *p,uint32_t mask){put(p,24,word(p,24)&~mask);}
extern const ThugComponentMethods thug_end_run_methods_draft;
/* 00510f90 /00510d20 /00510d40. */
void *thug_end_run_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(28,m);if(!p)return 0;
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_end_run_methods_draft);put(p,24,0);put(p,4,0xb1d5a3e1);return p;
}
void thug_end_run_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_end_run_methods_draft);thug_component_destroy(p);}
void *thug_end_run_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_end_run_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00510d30. Read before the potentially overlapping output write. */
uint32_t *thug_end_run_copy_flags_draft(const void *p,uint32_t *out){uint32_t v=word(p,24);__builtin_memcpy(out,&v,4);return out;}
/* 00510dc0. The command ABI's parameters and script are unused. */
uint32_t thug_end_run_command_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *i){
 (void)s;(void)i;
 switch(name){
 case 0x69a9e37f:put(p,24,word(p,24)|16);clear(p,32);break;
 case 0x4c58771e:put(p,24,word(p,24)|2);clear(p,4);break;
 case 0x00afc6a7:put(p,24,word(p,24)|8);break;
 case 0x95bdcfcd:return (word(p,24)&1)&&!(word(p,24)&2);
 case 0x962dea01:put(p,24,word(p,24)|1);break;
 case 0xea77e667:clear(p,1);clear(p,4);break;
 case 0xb866bf9b:clear(p,1);clear(p,8);clear(p,2);clear(p,16);clear(p,4);clear(p,32);break;
 default:return 2;
 }return 1;
}
/* 00553460. Missing required boolean retains an indeterminate original stack
 * word. Stop at that unsupported boundary instead of reading an uninitialized C
 * variable; this candidate is not claimed complete. */
uint8_t thug_end_run_settings_gate_draft(const ThugGameSettings *s){
 const uint32_t modes[]={0x5d32129c,0x6ef8fda0,0xf135ecb6,0x1498240a,0xe45f0ca2,0x3d6d444f,0xbff33600};
 for(unsigned i=0;i<7;i++)if(thug_settings_mode(s)==modes[i])return 0;
 uint32_t value;
 if(!thug_script_get_boolean(&s->parameters,0x8d38a280,&value,1))__builtin_trap();
 return value!=0;
}
/* 00553550. PUSH ECX leaves the settings pointer in the optional output slot. */
uint8_t thug_end_run_settings_deferred_draft(const ThugGameSettings *s){
 if(!thug_game_is_multiplayer(thug_game_context))return 0;
 if(!thug_end_run_settings_gate_draft(s))return 1;
 uint32_t value=(uintptr_t)s;thug_script_get_boolean(&s->parameters,0x48e748b5,&value,1);return value==1;
}
/* 005332a0 /00533250. Sending updates the remembered byte after queue calls. */
uint8_t thug_end_run_network_current_draft(const void *n){return ((const uint8_t *)n)[0x39]==((const uint8_t *)n)[0x38];}
void thug_end_run_network_send_draft(void *n,const ThugDiagnostics *d,const ThugMemory *m){
 ThugMessageSpec spec;thug_message_spec_initialize(&spec);
 spec.data=(uint8_t *)n+0x38;spec.length=1;spec.id=0x59;spec.delivery=2;spec.group=8;
 thug_queue_send_first((void *)(uintptr_t)word(n,8),&spec,d,m);
 ((uint8_t *)n)[0x39]=((uint8_t *)n)[0x38];
}
/* 00510d70. Single-player suspends through the actual virtual method. */
void thug_end_run_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;
 if(!thug_game_is_multiplayer(thug_game_context)){(*(const ThugComponentMethods **)p)->suspend(p,1);return;}
 if(!((uint8_t *)(uintptr_t)word(p,12))[0xbc]||!(word(p,24)&2))return;
 if(!thug_end_run_network_current_draft(thug_network_state))thug_end_run_network_send_draft(thug_network_state,d,m);
}
/* 00510ea0. Event callbacks can change flags before the final bit clear. */
void thug_end_run_request_draft(void *p,uint32_t force,const ThugDiagnostics *d,const ThugMemory *m){
 if(!(uint8_t)force&&!thug_end_run_settings_deferred_draft(thug_game_settings)){
  thug_object_emit_event((void *)(uintptr_t)word(p,12),0x822e13a9,0,d,m);clear(p,2);return;
 }
 if(word(p,24)&6)return;
 put(p,24,word(p,24)|4);void *owner=(void *)(uintptr_t)word(p,12);
 if(((uint8_t *)owner)[0xbc])thug_script_run_sync(0xf4ce3e97,0,owner,0,d,m);
}
/* 00510f10 /00510f30..00510f80. */
void thug_end_run_finish_secondary_draft(void *p,uint32_t unused,const ThugDiagnostics *d,const ThugMemory *m){
 (void)unused;clear(p,16);thug_object_emit_event((void *)(uintptr_t)word(p,12),0xab676175,0,d,m);
}
uint32_t thug_end_run_flag_2_draft(const void *p){return (word(p,24)>>1)&1;}
uint32_t thug_end_run_flag_16_draft(const void *p){return (word(p,24)>>4)&1;}
uint32_t thug_end_run_flag_1_draft(const void *p){return word(p,24)&1;}
void thug_end_run_clear_1_draft(void *p){clear(p,1);}
void thug_end_run_clear_8_draft(void *p){clear(p,8);}
void thug_end_run_clear_4_draft(void *p){clear(p,4);}
static void empty(void *p){(void)p;}
static void empty_init(void *p,const ThugScriptStructure *s){(void)p;(void)s;}
const ThugComponentMethods thug_end_run_methods_draft={.dispose=thug_end_run_delete_draft,.update=thug_end_run_update_draft,.initialize=empty_init,.finalize=empty,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=thug_end_run_command_draft};
