/* Remaining skater component startup. Unrecovered virtuals trap explicitly. */
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/game/objectives.h"
#include "../../src/script/operators.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
#define METHODS(n) extern const ThugComponentMethods thug_##n##_startup_methods_draft
METHODS(nonlocal_net);METHODS(component_125044e2);METHODS(state_history);METHODS(component_488af07a);
METHODS(component_8bce7e66);METHODS(component_1859f772);METHODS(component_380d909a);METHODS(component_408d2aa9);METHODS(stats_manager);
/* 005144e0. The factory requests 0x2c0 bytes. */
void *thug_nonlocal_net_construct_draft(void *p){
 thug_component_construct(p);
 const unsigned first[]={0x2a4,0x2b0,0x2b4,0x2a8,0x2ac,0x2b8,0x2bc,0x24};
 for(unsigned i=0;i<sizeof(first)/sizeof(*first);i++)put(p,first[i],0);
 put(p,0,(uintptr_t)&thug_nonlocal_net_startup_methods_draft);put(p,4,0x850eef66);
 put(p,0x28,0);put(p,0x2c,0);put(p,0x30,0);put(p,0x34,0x3f800000);
 put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0);put(p,0x44,0x3f800000);put(p,0x298,0);put(p,0x20,0);return p;
}
/* 0051acb0. Preserve both original clearing passes and the untouched last word. */
void *thug_state_history_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_state_history_startup_methods_draft);
 for(unsigned i=0;i<20;i++){unsigned o=0x1c+i*0x84;put(p,o+0x68,0);put(p,o+0x6c,0);__builtin_memset((char *)p+o,0,0x84);}
 __builtin_memset((char *)p+0xa70,0,0x690);put(p,0x1100,0);put(p,0x18,0);put(p,0xa6c,0);put(p,4,0x18223fd6);
 __builtin_memset((char *)p+0x1c,0,0xa50);__builtin_memset((char *)p+0xa70,0,0x690);return p;
}
/* 0051add0. Only the observed fields are initialized; gaps retain their bytes. */
void *thug_component_1859f772_construct_draft(void *p){
 thug_component_construct(p);put(p,0x1c,0);put(p,0x24,0);((uint8_t *)p)[0x28]=0;
 const unsigned offsets[]={0xa4,0xa8,0xb0,0xb4,0xb8,0xbc,0x2c,0x30};
 for(unsigned i=0;i<sizeof(offsets)/sizeof(*offsets);i++)put(p,offsets[i],0);
 put(p,0,(uintptr_t)&thug_component_1859f772_startup_methods_draft);put(p,4,0x1859f772);put(p,0xc0,0x1ca1ff20);((uint8_t *)p)[0xc4]=1;return p;
}
/* 0051c5a0. */
void *thug_stats_manager_construct_draft(void *p){
 thug_component_construct(p);put(p,0xa90,0);put(p,0xa94,0);put(p,0xa98,0);put(p,0xa9c,0);
 put(p,0,(uintptr_t)&thug_stats_manager_startup_methods_draft);put(p,4,0x4ff8dac6);
 const unsigned offsets[]={0xa24,0xa28,0xa2c,0xa30,0xa34,0xa38,0xa3c,0xa40,0xa5c,0xa60,0xa64,0xa68,0xa6c,0xa70,0xa74,0xa78,0xa8c};
 for(unsigned i=0;i<sizeof(offsets)/sizeof(*offsets);i++)put(p,offsets[i],0);return p;
}
/* 005147f0 /0051ad30 /0051b880 /0051cb90. */
void *thug_nonlocal_net_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x2c0,m);return p?thug_nonlocal_net_construct_draft(p):0;}
void *thug_state_history_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1108,m);return p?thug_state_history_construct_draft(p):0;}
void *thug_component_1859f772_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0xc8,m);return p?thug_component_1859f772_construct_draft(p):0;}
void *thug_stats_manager_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0xaa0,m);return p?thug_stats_manager_construct_draft(p):0;}
/* Inlined constructors belong to the factory address, not separate credit. */
void *thug_component_125044e2_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1c,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_component_125044e2_startup_methods_draft);put(p,4,0x125044e2);}return p;}
void *thug_component_488af07a_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x28,m);if(p){thug_component_construct(p);put(p,0x1c,0);put(p,0x20,0);((uint8_t *)p)[0x18]=0;put(p,0,(uintptr_t)&thug_component_488af07a_startup_methods_draft);put(p,4,0x488af07a);}return p;}
void *thug_component_8bce7e66_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x28,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_component_8bce7e66_startup_methods_draft);put(p,4,0x8bce7e66);}return p;}
void *thug_component_380d909a_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x38,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_component_380d909a_startup_methods_draft);put(p,4,0x380d909a);((uint8_t *)p)[0x1c]=0;((uint8_t *)p)[0x1d]=0;}return p;}
void *thug_component_408d2aa9_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x74,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_component_408d2aa9_startup_methods_draft);put(p,4,0x408d2aa9);put(p,0x18,0);put(p,0x70,0);}return p;}
/* 00511780. An unsigned ID outside the eight-entry table retains word18. */
void thug_component_125044e2_initialize_draft(void *p,const ThugScriptStructure *s){
 (void)s;uint32_t id=word((void *)(uintptr_t)word(p,12),0x14);
 const uint32_t keys[]={0xe797a186,0x90909110,0x0999c0aa,0x7e9ef03c,0xe0fa659f,0x97fd5509,0x0ef404b3,0x79f33425};
 if(id<8)put(p,0x18,keys[id]);
}
/* 004fbda0 /0051ae60. */
void thug_component_8bce7e66_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;put(p,0x18,0);}
void thug_component_1859f772_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;((uint8_t *)p)[0x28]=thug_skater_orientation_context->identifier!=0xd443a2bc;}
const char thug_stats_manager_difficulty_format_draft[]="STATSManager: difficulty ====================== %i\n";
const char thug_stats_manager_empty_text_draft[]="";
/* 0051c670. Valid loaded QB structures/arrays and difficulty indices are the
 * original contract. A failed required typed getter has no initialized native
 * output; trap instead of manufacturing a value for that unsupported input. */
void thug_stats_manager_initialize_draft(void *p,const ThugScriptStructure *unused,const ThugDiagnostics *d){
 (void)unused;((uint8_t *)p)[0x9f6]=0;((uint8_t *)p)[0x9f4]=0;
 const unsigned offsets[]={0xa1c,0xa20,0xa50,0xa54,0xa4c,0xa44,0xa48,0xa7c,0xa80,0xa84,0xa88};
 for(unsigned i=0;i<sizeof(offsets)/sizeof(*offsets);i++)put(p,offsets[i],0);((uint8_t *)p)[0x18]=1;
 void *owner=(void *)(uintptr_t)word(p,12);void *found=thug_object_find_global(0,word(owner,0x14));put(p,0xa90,(uintptr_t)found);
 if(found){put(p,0xa94,(uintptr_t)thug_object_find_component(found,0x43686585));put(p,0xa98,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,0xa90),0xd9151d4d));}
 else {put(p,0xa94,0);put(p,0xa98,0);}
 uint32_t difficulty=thug_game_difficulty(thug_objective_manager(),1);put(p,0xa18,difficulty);
 if(d&&d->print)d->print(d->context,thug_stats_manager_difficulty_format_draft,difficulty);
 if(thug_script_get_global_integer(0xb8688a8a,1)==1)((uint8_t *)p)[0x9f5]=1;
 ThugScriptArray *array=thug_script_get_global_array(0x4e46cc28,1);int32_t count=(int32_t)array->count;
 for(int32_t i=0;i<count;i++){
  const ThugScriptStructure *s=thug_script_array_structure(array,i);unsigned o=0x20+(uint32_t)i*0x24;uint32_t key;ThugScriptArray *a;const char *text;
  if(thug_script_has_name_or_flag(s,0x0ffd7bbe)){if(!thug_script_get_checksum(s,0x0ffd7bbe,&key,1))__builtin_trap();put(p,o-4,key);}
  if(thug_script_has_name_or_flag(s,0xc2455018)){if(!thug_script_get_checksum(s,0xc2455018,&key,1))__builtin_trap();put(p,o,key);}
  if(thug_script_has_name_or_flag(s,0xe288a7cb)){a=0;thug_script_get_array(s,0xe288a7cb,&a,1);put(p,o+4,(uintptr_t)thug_script_array_structure(a,word(p,0xa18)));}
  if(thug_script_has_name_or_flag(s,0xcd021293)){a=0;thug_script_get_array(s,0xcd021293,&a,1);put(p,o+0x14,(uintptr_t)thug_script_array_text(a,word(p,0xa18)));}
  if(thug_script_has_name_or_flag(s,0xc4745838)){text=thug_stats_manager_empty_text_draft;thug_script_get_text(s,0xc4745838,&text,1);put(p,o+0x10,(uintptr_t)text);}
  if(thug_script_has_name_or_flag(s,0xbd982fdc)){uint32_t ignored;if(!thug_script_get_integer(s,0xbd982fdc,&ignored,1))__builtin_trap();put(p,o+0xc,0);}
  if(thug_script_has_name_or_flag(s,0xd8a9d3ca)){a=0;thug_script_get_array(s,0xd8a9d3ca,&a,1);put(p,o+0x18,(uintptr_t)thug_script_array_structure(a,word(p,0xa18)));}
  if(thug_script_has_name_or_flag(s,0x3c2fb496)){a=0;thug_script_get_array(s,0x3c2fb496,&a,1);put(p,o+0x1c,(uintptr_t)thug_script_array_structure(a,word(p,0xa18)));}
  ((uint8_t *)p)[o+8]=0;
 }
}
static void stats_init(void *p,const ThugScriptStructure *s){thug_stats_manager_initialize_draft(p,s,thug_component_services?thug_component_services->diagnostics:0);}
static void empty(void *p){(void)p;}static void empty_init(void *p,const ThugScriptStructure *s){(void)p;(void)s;}
static void pending(void *p){(void)p;__builtin_trap();}
static void pending_one(void *p,void *x){(void)p;(void)x;__builtin_trap();}
static void *pending_dispose(void *p,uint32_t f,const ThugMemory *m){(void)p;(void)f;(void)m;__builtin_trap();}
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static uint32_t pending_checksum(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
#define TABLE(n,init,final,desc,last) const ThugComponentMethods thug_##n##_startup_methods_draft={.dispose=pending_dispose,.update=pending_frame,.initialize=init,.finalize=final,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=last,.descriptor=desc,.checksum=pending_checksum}
TABLE(nonlocal_net,empty_init,pending,thug_component_descriptor_base,pending_one);
TABLE(component_125044e2,thug_component_125044e2_initialize_draft,empty,thug_component_descriptor_base,thug_component_empty_one);
TABLE(state_history,empty_init,empty,thug_component_descriptor_base,thug_component_empty_one);
TABLE(component_488af07a,empty_init,pending,thug_component_descriptor_base,thug_component_empty_one);
TABLE(component_8bce7e66,thug_component_8bce7e66_initialize_draft,pending,thug_component_descriptor,pending_one);
TABLE(component_1859f772,thug_component_1859f772_initialize_draft,pending,thug_component_descriptor,thug_component_empty_one);
TABLE(component_380d909a,empty_init,pending,thug_component_descriptor_base,thug_component_empty_one);
TABLE(component_408d2aa9,empty_init,empty,thug_component_descriptor_base,thug_component_empty_one);
TABLE(stats_manager,stats_init,empty,thug_component_descriptor,thug_component_empty_one);
