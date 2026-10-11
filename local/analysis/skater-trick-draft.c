/* Original Trick startup/lifetime and PhysicsControl startup. */
#include "../../src/game/components.h"
#include "../../src/script/values.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void half(void *p,unsigned o,uint16_t v){__builtin_memcpy((char *)p+o,&v,2);}
static void byte(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
extern const ThugComponentMethods thug_trick_pending_methods_draft,thug_physics_control_pending_methods_draft;
/* 00588170. EAX returns the receiver; Ghidra's void prototype omits this. */
void *thug_trick_history_construct_draft(void *p){put(p,0x800,0);return p;}
/* 0051f320. Preserve all unmentioned bytes, including the gaps within each
 * 24-byte record and between the single-byte flags. No allocation occurs. */
void thug_trick_reset_draft(void *p){
 put(p,0x18,0);put(p,0xa18,0);byte(p,0xa24,0);put(p,0x1204,0);
 put(p,0xa2c,UINT32_MAX);put(p,0xa30,UINT32_MAX);
 for(unsigned o=0x1208;o<=0x1234;o+=4)put(p,o,0);
 byte(p,0x1268,0);for(unsigned o=0x1238;o<=0x1264;o+=4)put(p,o,0);
 byte(p,0x12b0,0);for(unsigned o=0x1280;o<=0x12ac;o+=4)put(p,o,0);
 byte(p,0x12c8,0);byte(p,0x12c9,0);
 put(p,0x12cc,0);put(p,0x12d0,0);put(p,0x12d4,0);put(p,0x1328,0);put(p,0x132c,0);
 for(unsigned i=0;i<100;i++){unsigned o=0x3c+i*24;put(p,o,0);byte(p,o+12,0);put(p,o+16,0);}
 half(p,0x998,0);half(p,0x99a,0);put(p,0x99c,0);put(p,0x9a0,0);put(p,0x9a4,0);
 for(unsigned i=0;i<22;i++){byte(p,0xa00+i,0);put(p,0x9a8+i*4,0);}
 byte(p,0x1330,0);byte(p,0x1bb8,0);
}
/* 00522390. Allocation/zeroing is the factory's responsibility. */
void *thug_trick_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_trick_pending_methods_draft);
 thug_trick_history_construct_draft((char *)p+0x13b4);put(p,4,0x270f56e1);put(p,0xa28,0);
 for(unsigned o=0x1c;o<=0x34;o+=4)put(p,o,0);
 thug_trick_reset_draft(p);return p;
}
/* 00523490. */
void *thug_trick_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1bc0,m);return p?thug_trick_construct_draft(p):0;}
/* 0051f2b0. Each next owner is loaded before the preceding link store. */
void thug_trick_finalize_draft(void *p){
 const uint32_t names[]={0x27d7cd28,0x589e5fb3,0x5bd63b29,0x488af07a,0x43686585,0x4ff8dac6};
 void *owner=ptr(p,12),*found=thug_object_find_component(owner,names[0]);
 for(unsigned i=1;i<6;i++){owner=ptr(p,12);put(p,0x1c+i*4,(uintptr_t)found);found=thug_object_find_component(owner,names[i]);}
 put(p,0x34,(uintptr_t)found);
}
/* 005234f0 and005243f0. The structure pointer stays unchanged after disposal. */
void thug_trick_destroy_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)&thug_trick_pending_methods_draft);void *s=ptr(p,0xa28);
 if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
 thug_component_destroy(p);
}
void *thug_trick_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_trick_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 005176c0,00517740. */
void thug_physics_control_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_physics_control_pending_methods_draft);thug_component_destroy(p);}
void *thug_physics_control_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_physics_control_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 005176d0. Does not reset either override byte24/25. */
void thug_physics_control_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;byte(p,0x18,0);}
/* 00517770. State is required and its state identifier is invalidated. */
void thug_physics_control_finalize_draft(void *p){
 void *found=thug_object_find_component(ptr(p,12),0x5bd63b29),*owner=ptr(p,12);
 put(p,0x28,(uintptr_t)found);found=thug_object_find_component(owner,0x43686585);put(p,0x2c,(uintptr_t)found);put(found,0x1c,UINT32_MAX);
}
/* 00517830. */
void *thug_physics_control_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x30,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_physics_control_pending_methods_draft);put(p,4,0xd9151d4d);put(p,0x28,0);}return p;
}
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
static void empty(void *p){(void)p;}
static void empty_initialize(void *p,const ThugScriptStructure *s){thug_component_empty_one(p,(void *)s);}
#define COMMON .update=pending_frame,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor,.checksum=pending_command
const ThugComponentMethods thug_trick_pending_methods_draft={.dispose=thug_trick_delete_draft,.initialize=empty_initialize,.finalize=thug_trick_finalize_draft,COMMON};
const ThugComponentMethods thug_physics_control_pending_methods_draft={.dispose=thug_physics_control_delete_draft,.initialize=thug_physics_control_initialize_draft,.finalize=thug_physics_control_finalize_draft,COMMON};
