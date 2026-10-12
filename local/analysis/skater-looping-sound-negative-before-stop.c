/* SkaterLoopingSound lifecycle; frame/command paths remain unavailable. */
#include "../../src/game/components.h"
#include "../../src/audio/sound.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
extern const ThugComponentMethods thug_looping_sound_pending_methods_draft;
extern uint8_t thug_sound_stop_draft(const ThugSoundConfiguration *,uint32_t);
/* 005138e0 /00513ad0. Initialize the embedded volume's 24-byte prefix only. */
void *thug_looping_sound_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_looping_sound_pending_methods_draft);
 thug_sound_volume_initialize((void *)((char *)p+0x28));
 ((uint8_t *)p)[0xfd]=1;put(p,0x74,1);((uint8_t *)p)[0x10c]=1;
 ((uint8_t *)p)[0x100]=0;((uint8_t *)p)[0xff]=0;((uint8_t *)p)[0xfc]=0;((uint8_t *)p)[0xfe]=0;
 put(p,4,0xb5f1e9d2);put(p,0x108,0x3f800000);return p;
}
void *thug_looping_sound_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x110,m);return p?thug_looping_sound_construct_draft(p):0;}
/* 00513b30 /00513fa0. Clear the voice only after stopping it. */
void thug_looping_sound_destroy_draft(void *p){
 put(p,0,(uintptr_t)&thug_looping_sound_pending_methods_draft);
 uint32_t id=word(p,24);if(id){put(p,24,0);thug_sound_stop_draft(thug_sound_configuration,id);}
 thug_component_destroy(p);
}
void *thug_looping_sound_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_looping_sound_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00513880 /00513970. Optional float retains the current field when absent. */
void thug_looping_sound_initialize_draft(void *p,const ThugScriptStructure *s){
 put(p,0x58,0x4192aaab);put(p,0x54,0x42340000);
 thug_script_get_float(s,0xf1a99b27,(float *)((char *)p+0x108),0);
}
void thug_looping_sound_bind_draft(void *p){put(p,0x5c,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,12),0xd9151d4d));}
/* 00513f60. The low byte gates stop/resume, after base suspension changes. */
void thug_looping_sound_suspend_draft(void *p,uint32_t flags){
 thug_component_suspend(p,flags);
 if((uint8_t)flags){uint32_t id=word(p,24);if(id){put(p,24,0);thug_sound_stop_draft(thug_sound_configuration,id);}}
 else ((uint8_t *)p)[0xfd]=1;
}
static void empty(void *p){(void)p;}
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
const ThugComponentMethods thug_looping_sound_pending_methods_draft={.dispose=thug_looping_sound_delete_draft,.update=pending_frame,.initialize=thug_looping_sound_initialize_draft,.finalize=thug_looping_sound_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_looping_sound_suspend_draft,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor,.checksum=pending_command};
