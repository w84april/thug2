/* Local network component lifecycle. Its network-frame method remains pending. */
#include "../../src/game/components.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
extern const ThugComponentMethods thug_local_net_pending_methods_draft;
extern void thug_skater_cleanup_initialize_draft(void *,const ThugScriptStructure *);
extern uint32_t *thug_skater_construction_boundary_draft;
/* 00513630. Preserve both flag-byte initializers and the cleared link fields. */
void *thug_local_net_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x44,m);if(!p)return 0;
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_local_net_pending_methods_draft);
 put(p,0x2c,0);put(p,0x30,0);put(p,0x3c,0);put(p,0x40,0);put(p,0x18,0);
 ((uint8_t *)p)[0x1c]=255;put(p,4,0x7cd3e6d5);put(p,0x2c,0);
 ((uint8_t *)p)[0x35]=255;((uint8_t *)p)[0x34]=0;put(p,0x38,0);return p;
}
/* 00512e30 /00512e40. */
void thug_local_net_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_local_net_pending_methods_draft);thug_component_destroy(p);}
void *thug_local_net_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_local_net_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00512e70. The second lookup re-reads the owner. */
void thug_local_net_bind_draft(void *p){put(p,0x3c,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,12),0x43686585));put(p,0x40,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,12),0x5bd63b29));}
static void empty(void *p){(void)p;}
/* Shared original0051adc0, already recovered elsewhere; no additional count. */
uint32_t thug_local_net_command_draft(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;return 2;}
static void pending_update(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;uint32_t *b=thug_skater_construction_boundary_draft;
 if(b){b[0]=0x5136c0;b[1]=0;b[2]=(uintptr_t)p;b[3]=1;}__builtin_trap();
}
const ThugComponentMethods thug_local_net_pending_methods_draft={.dispose=thug_local_net_delete_draft,.update=pending_update,.initialize=thug_skater_cleanup_initialize_draft,.finalize=thug_local_net_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=thug_local_net_command_draft};
