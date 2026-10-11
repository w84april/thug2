/* Original skater construction dependencies and an explicit interrupted prefix. */
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/game/object_registry.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
void *thug_suspend_construct_draft(void *);
void *thug_component_b87c8e43_construct_draft(void *);
void *thug_composite_initialize_draft(void *);
void thug_composite_add_component_draft(void *,void *);
void thug_composite_add_parameters_draft(void *,ThugScriptStructure *,ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
void thug_component_suspend_update_draft(void *);
extern const ThugComponentMethods thug_skater_state_methods_draft,thug_skater_attachment_pending_methods_draft;
/* 00519740. The original factory contains this constructor inline. */
void *thug_skater_state_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x128,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_state_methods_draft);put(p,4,0x43686585);((uint8_t *)p)[0x120]=0;}return p;}
/* 00519460 /00519450 /00519620. */
void thug_skater_state_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;put(p,0x18,1);}
void thug_skater_state_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_state_methods_draft);thug_component_destroy(p);}
void *thug_skater_state_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_skater_state_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 0051bd80. Later attachment commands and disposal remain pending; none is
 * substituted by success. Only its real factory and empty initializer run. */
void *thug_skater_attachment_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x20,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_attachment_pending_methods_draft);put(p,4,0xf27a294d);put(p,0x18,0);put(p,0x1c,0);}return p;}
static void empty(void *p){(void)p;}
static void empty_init(void *p,const ThugScriptStructure *s){thug_component_empty_one(p,(void *)s);}
static void suspend_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
static uint32_t unhandled(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){return thug_animation_unhandled_command(p,name,s,script,0,0);}
static void *pending_delete(void *p,uint32_t flags,const ThugMemory *m){(void)p;(void)flags;(void)m;__builtin_trap();}
static uint32_t pending_command(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){(void)p;(void)name;(void)s;(void)script;__builtin_trap();}
#define COMMON .update=suspend_frame,.finalize=empty,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one
const ThugComponentMethods thug_skater_state_methods_draft={.dispose=thug_skater_state_delete_draft,.initialize=thug_skater_state_initialize_draft,COMMON,.descriptor=thug_component_descriptor,.checksum=unhandled};
const ThugComponentMethods thug_skater_attachment_pending_methods_draft={.dispose=pending_delete,.initialize=empty_init,COMMON,.descriptor=thug_component_descriptor_base,.checksum=pending_command};
uint32_t thug_skater_serial_draft; /* 00690fa0 */
/* 00401d80. Write the empty word before reading and incrementing the counter. */
void *thug_skater_handle_construct_draft(void *p){put(p,4,0);put(p,0,thug_skater_serial_draft);++thug_skater_serial_draft;return p;}
/* 0057b250. This entry is cdecl with one stack argument. Both original
 * constructors and the shared component append/registration routine execute. */
void thug_skater_add_base_components_draft(void *owner,const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x4c,m);if(p)p=thug_suspend_construct_draft(p);
 thug_composite_add_component_draft(owner,p);
 p=thug_allocate_zeroed(0x4c,m);if(p)p=thug_component_b87c8e43_construct_draft(p);
 thug_composite_add_component_draft(owner,p);
}
/* 00462a90. Replace a secondary alias and maintain the pointed object's count.
 * Counts decrement only when signed-positive; increment retains uint32 wrap. */
void thug_object_registry_set_alias_draft(ThugObjectLookupManager *manager,uint32_t name,ThugUiObjectBase *object,const ThugMemory *m){
 ThugUiObjectBase *old=thug_object_table_find(manager->secondary,&name,1);
 if(old){if((int32_t)old->alias_count>0)--old->alias_count;thug_object_table_remove(manager->secondary,&name,m);}
 ++object->alias_count;thug_object_table_insert(manager->secondary,&name,object,m);
}
/* Identity storage only. No unrecovered skater virtual can be called through
 * these tables: the constructor prefix stops before creating Score. */
const uint32_t thug_skater_pending_methods_draft[20]={0};
const uint32_t thug_skater_node_pending_methods_draft[1]={0};
const char thug_skater_number_format_draft[]="D:%s:%i: m_skater_number = %i\n";
const char thug_skater_id_format_draft[]="D:%s:%i: m_id = %i\n";
const char thug_skater_source_file_draft[]="jects\\skater.cpp";
uint32_t *thug_skater_construction_boundary_draft;
/* 00582d90 PREFIX ONLY. Six original stack arguments are retained. The sixth
 * belongs to the later constructor body and is not reached in this prefix.
 * This records the real 0045ee20 invocation and traps before executing it. */
void thug_skater_construct_prefix_draft(void *p,uint32_t controller,ThugObjectManager *manager,uint32_t local,uint32_t id,uint32_t heap_index,uint32_t later,const ThugDiagnostics *d,const ThugMemory *m){
 (void)later;thug_composite_initialize_draft(p);put(p,0,(uintptr_t)thug_skater_pending_methods_draft);
 thug_skater_handle_construct_draft((char *)p+0x15c);
 void *node=(char *)p+0x238;put(node,0,(uintptr_t)thug_skater_node_pending_methods_draft);
 put(node,4,(uintptr_t)p);put(node,8,0);put(node,12,(uintptr_t)node);put(node,16,(uintptr_t)node);
 ((uint8_t *)p)[0xbc]=(uint8_t)local;thug_skater_add_base_components_draft(p,m);
 put(p,0x18,0xbaf9b341);((uint8_t *)p)[0x2c4]=0;put(p,0x2b8,heap_index);put(p,0x14,id);
 if(heap_index<2)thug_object_registry_set_alias_draft(thug_object_lookup_manager,heap_index?0x06ed3fa7:0x5b8ab877,p,m);
 put(p,0x30,0xfffffe0c);manager->methods->add(manager,p,m);
 put(p,0x2bc,controller);put(p,0x31c,0);
 if(d&&d->print)d->print(d->context,thug_skater_number_format_draft,thug_skater_source_file_draft,0x43c,controller);
 if(d&&d->print)d->print(d->context,thug_skater_id_format_draft,thug_skater_source_file_draft,0x43d,word(p,0x14));
 const unsigned clear[]={0x24c,0x250,0x254,0x258,0x25c,0x264,0x268,0x270,0x278,0x280,0x28c,0x288,0x284};
 for(unsigned i=0;i<sizeof(clear)/sizeof(*clear);i++)put(p,clear[i],0);
 ThugScriptStructure *parameters=thug_script_structure_allocate(8,m);
 if(parameters)thug_script_structure_initialize(parameters);
 thug_script_set_checksum(parameters,0xb6015ea8,0x43686585,m);
 thug_composite_add_parameters_draft(p,parameters,0,d,m);
 thug_script_set_checksum(parameters,0xb6015ea8,0xf27a294d,m);
 thug_composite_add_parameters_draft(p,parameters,0,d,m);
 if(((uint8_t *)p)[0xbc]){
  thug_script_set_checksum(parameters,0xb6015ea8,0x27d7cd28,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  put(p,0x264,(uintptr_t)thug_object_find_component(p,0x27d7cd28));
 }
 thug_script_set_checksum(parameters,0xb6015ea8,0xd262802f,m);
 uint32_t *b=thug_skater_construction_boundary_draft;
 if(b){b[0]=0x45ee20;b[1]=(uintptr_t)parameters;b[2]=(uintptr_t)p;b[3]=1;}
 __builtin_trap();
}
