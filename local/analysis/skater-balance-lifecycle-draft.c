/* BalanceTrick lifecycle. The checksum command remains explicitly unavailable. */
#include "../../src/game/components.h"
#include "../../src/script/delivery.h"
#include "../../src/script/schedule.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
typedef struct {void *(*dispose)(void *,uint32_t,const ThugMemory *);} BalanceRecordMethods;
extern const BalanceRecordMethods thug_balance_record_methods_draft;
extern const ThugComponentMethods thug_balance_component_pending_methods_draft;
/* 00579950. The conditional QB runs before the selected fields are cleared. */
void *thug_balance_record_construct_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)&thug_balance_record_methods_draft);
 if(thug_script_get_global_integer(0x5d07e2be,0))thug_script_run_sync(0x18f77ea1,0,0,0,d,m);
 const unsigned offsets[]={0x38,0x24,0x28,0x30,0x34};
 for(unsigned i=0;i<5;i++)put(p,offsets[i],0);
 ((uint8_t *)p)[0x3c]=0;((uint8_t *)p)[0x54]=0;put(p,0x50,0xffffffff);return p;
}
/* 00579850 /005799a0. The delete wrapper inlines the vtable write. */
void thug_balance_record_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_balance_record_methods_draft);}
void *thug_balance_record_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
 thug_balance_record_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
const BalanceRecordMethods thug_balance_record_methods_draft={thug_balance_record_delete_draft};
/* 00579860. Re-read the stored owner before each dependency search. */
void thug_balance_record_bind_draft(void *p,void *owner){
 put(p,4,(uintptr_t)owner);
 put(p,8,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,4),0x589e5fb3));
 put(p,12,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,4),0xd262802f));
 put(p,16,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,4),0x27d7cd28));
}
/* 004f8f80. Four embedded records; preserve the final selected write order. */
void *thug_balance_component_construct_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_balance_component_pending_methods_draft);
 for(unsigned i=0;i<4;i++)thug_balance_record_construct_draft((char *)p+0x24+i*0x58,d,m);
 put(p,4,0x589e5fb3);put(p,0x184,0);put(p,0x20,0);return p;
}
/* 004f9170. Registered factory ABI has only the host memory extension. */
void *thug_balance_component_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x188,m);if(!p)return 0;
 const ThugDiagnostics *d=thug_component_services?thug_component_services->diagnostics:thug_event_services?thug_event_services->diagnostics:0;
 return thug_balance_component_construct_draft(p,d,m);
}
/* 004f8cf0 /004f9010. Embedded destruction runs in reverse order. */
void thug_balance_component_destroy_draft(void *p){
 put(p,0,(uintptr_t)&thug_balance_component_pending_methods_draft);
 for(unsigned i=4;i;i--)thug_balance_record_destroy_draft((char *)p+0x24+(i-1)*0x58);
 thug_component_destroy(p);
}
void *thug_balance_component_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
 thug_balance_component_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 004f9040 /004f9080. Parameters unused; each child receives the current owner. */
void thug_balance_component_initialize_draft(void *p,const ThugScriptStructure *s){
 (void)s;for(unsigned i=0;i<4;i++)thug_balance_record_bind_draft((char *)p+0x24+i*0x58,(void *)(uintptr_t)word(p,12));
}
void thug_balance_component_bind_draft(void *p){put(p,0x184,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,12),0x7149b753));}
/* Shared original0051b970 is already recovered; this bridge earns no count. */
extern void thug_component_suspend_update_draft(void *);
static void frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
static void empty(void *p){(void)p;}
static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
const ThugComponentMethods thug_balance_component_pending_methods_draft={.dispose=thug_balance_component_delete_draft,.update=frame,.initialize=thug_balance_component_initialize_draft,.finalize=thug_balance_component_bind_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor,.checksum=pending_command};
