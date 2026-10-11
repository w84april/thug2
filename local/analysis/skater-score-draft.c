/* Original Score startup. Later frame, command and disposal paths remain pending. */
#include "../../src/game/components.h"
#include "../../src/game/score.h"
#include "../../src/script/delivery.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void float_put(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static void copy_pair(void *dst,const void *src){for(unsigned o=0;o<12;o+=4)put(dst,o,word(src,o));}
uint32_t thug_score_split_layout_draft; /* 0070134c */
/* 004a0710. */
uint32_t thug_score_get_split_layout_draft(void){return thug_score_split_layout_draft;}
/* 00561290. Preserve neighboring bytes and truncate the incoming identifier. */
void thug_score_set_player_draft(void *p,uint32_t id){uint16_t v=(uint16_t)id;__builtin_memcpy((char *)p+8,&v,2);}
/* 00561470. Growth/capacity precede allocation; loop reloads storage and limit. */
void *thug_score_array_construct_draft(void *p,uint32_t capacity,uint32_t growth,const ThugMemory *m){
 put(p,4,capacity);put(p,12,growth);put(p,0,(uintptr_t)m->allocate(m->context,capacity*4,0));
 for(int32_t i=0;i<(int32_t)word(p,4);i++)put(ptr(p,0),(uint32_t)i*4,0);
 put(p,8,0);return p;
}
/* 00561730. Original data contract requires the structure and selected arrays.
 * Copy raw words, including pair tags/padding, with the original load order. */
void thug_score_configure_balance_draft(void *p){
 ThugScriptStructure *settings=thug_script_get_global_structure(0x91cb3c33,0);
 ThugScriptArray *curve=0;thug_script_get_array(settings,0xf716442a,&curve,0);
 put(p,0x90,curve->count);
 for(int32_t i=0;i<(int32_t)word(p,0x90);i++)copy_pair((char *)p+0x94+(uint32_t)i*12,thug_script_array_structure(curve,i));
 uint32_t offset=word(p,0x90)*12;
 copy_pair((void *)((uintptr_t)p+0x94+offset),(void *)((uintptr_t)p+0x88+offset));
 float_put(p,0x184,1.0f/(float)(int32_t)word(p,0x90));
 uint32_t name=0xf314312a;
 if(thug_game_is_split_screen(0,0)&&thug_settings_mode(thug_game_settings)!=0x9d65d0e7&&thug_settings_mode(thug_game_settings)!=0xb239668f)
  name=thug_score_get_split_layout_draft()==1?0x44e39bb5:0xbeeca6d6;
 ThugScriptArray *positions=0;thug_script_get_array(settings,name,&positions,0);
 for(int32_t i=0;i<2;i++)copy_pair((char *)p+0x198+(uint32_t)i*12,thug_script_array_structure(positions,i));
}
/* 00563440. Allocation/zeroing belong to the caller, not this constructor. */
void *thug_score_construct_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0x38,0);put(p,0x3c,0);put(p,0x44,0);
 thug_score_array_construct_draft((char *)p+0x4c,8,8,m);
 for(unsigned i=0;i<20;i++)thug_script_pair_initialize((ThugScriptPair *)((char *)p+0x94+i*12));
 thug_script_pair_initialize((ThugScriptPair *)((char *)p+0x188));
 for(unsigned i=0;i<2;i++)thug_script_pair_initialize((ThugScriptPair *)((char *)p+0x198+i*12));
 put(p,0x68,UINT32_MAX);put(p,0x6c,UINT32_MAX);uint8_t special=((uint8_t *)p)[0x74];
 thug_score_set_player_draft(p,0);put(p,0xc,0);put(p,0x14,0);put(p,0x20,0);put(p,0x24,0);put(p,0x5c,0);put(p,0x60,0);put(p,0x70,0);
 if(special){
  ((uint8_t *)p)[0x74]=0;ThugSkaterBody *body=thug_game_skater_by_id(thug_game_context,0);
  if(body)thug_object_broadcast_event((ThugReferencedObject *)body,((uint8_t *)p)[0x74]?0xd0cd8081:0x7ccf5ee2,0,0,d,m);
 }
 put(p,0x84,0);put(p,0x2c,0);put(p,0x30,0);put(p,0x34,0);
 ((uint8_t *)p)[0x8c]=thug_script_get_global_integer(0x1edc33f1,0)!=0;
 float_put(p,0,(float)thug_script_get_global_number(0x59b9a85e,1));
 put(p,4,thug_script_get_global_integer(0xb33d71c0,1));thug_score_configure_balance_draft(p);return p;
}
extern const ThugComponentMethods thug_score_pending_methods_draft;
/* 00518b60. */
void *thug_score_component_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x1c,m);
 if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_score_pending_methods_draft);put(p,4,0xd262802f);put(p,0x18,0);}return p;
}
/* 00518660. Existing Score storage skips all work, including player-ID assignment. */
void thug_score_component_initialize_draft(void *p,const ThugScriptStructure *parameters,const ThugDiagnostics *d,const ThugMemory *m){
 (void)parameters;if(!word(p,0x18)){
  void *score=thug_allocate_zeroed(0x1550,m);if(score)score=thug_score_construct_draft(score,d,m);
  void *owner=ptr(p,0xc);put(p,0x18,(uintptr_t)score);
  uint16_t id;__builtin_memcpy(&id,(char *)owner+0x14,2);thug_score_set_player_draft(score,id);
 }
}
static void initialize_bridge(void *p,const ThugScriptStructure *s){
 const ThugDiagnostics *d=thug_component_services?thug_component_services->diagnostics:thug_event_services->diagnostics;
 const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
 thug_score_component_initialize_draft(p,s,d,m);
}
static void *pending_delete(void *p,uint32_t f,const ThugMemory *m){(void)p;(void)f;(void)m;__builtin_trap();}
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
static void empty(void *p){(void)p;}
const ThugComponentMethods thug_score_pending_methods_draft={.dispose=pending_delete,.update=pending_frame,.initialize=initialize_bridge,
 .finalize=empty,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=pending_command};
