/* Derived from the pinned skater constructor prefix; now continues through local SkaterFinalizePhysics. */
#include "../../src/game/components.h"
#include "../../src/game/object_registry.h"
#include "../../src/script/values.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
void *thug_composite_initialize_draft(void *);
void *thug_skater_handle_construct_draft(void *);
void thug_skater_add_base_components_draft(void *,const ThugMemory *);
void thug_object_registry_set_alias_draft(ThugObjectLookupManager *,uint32_t,ThugUiObjectBase *,const ThugMemory *);
void thug_composite_add_parameters_draft(void *,ThugScriptStructure *,ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
extern const uint32_t thug_skater_pending_methods_draft[20],thug_skater_node_pending_methods_draft[1];
extern const char thug_skater_number_format_draft[],thug_skater_id_format_draft[],thug_skater_source_file_draft[];
extern uint32_t *thug_skater_construction_boundary_draft;
/* PREFIX ONLY: stop before locald8cc3428 or nonlocal850eef66 component creation. */
void thug_skater_construct_finalize_prefix_draft(void *p,uint32_t controller,ThugObjectManager *manager,uint32_t local,uint32_t id,uint32_t heap_index,uint32_t later,const ThugDiagnostics *d,const ThugMemory *m){
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
 thug_composite_add_parameters_draft(p,parameters,0,d,m);
 put(p,0x278,(uintptr_t)thug_object_find_component(p,0xd262802f));
 thug_script_set_checksum(parameters,0xb6015ea8,((uint8_t *)p)[0xbc]?0xbf518e27:0x850eef66,m);
 if(((uint8_t *)p)[0xbc]){
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  thug_script_set_checksum(parameters,0xb6015ea8,0x270f56e1,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  put(p,0x258,(uintptr_t)thug_object_find_component(p,0x270f56e1));
  thug_script_set_checksum(parameters,0xb6015ea8,0xd9151d4d,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  put(p,0x284,(uintptr_t)thug_object_find_component(p,0xd9151d4d));
  thug_script_set_checksum(parameters,0xb6015ea8,0x5bd63b29,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  put(p,0x280,(uintptr_t)thug_object_find_component(p,0x5bd63b29));
  thug_script_set_checksum(parameters,0xb6015ea8,0x52d61a0d,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  thug_script_set_checksum(parameters,0xb6015ea8,0x11b4c67f,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  put(p,0x270,(uintptr_t)thug_object_find_component(p,0x11b4c67f));
  thug_script_set_checksum(parameters,0xb6015ea8,0x9f9cc949,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  thug_script_set_checksum(parameters,0xb6015ea8,0xe594f0a2,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  thug_script_set_checksum(parameters,0xb6015ea8,0x9b373e58,m);
  thug_composite_add_parameters_draft(p,parameters,0,d,m);
  thug_script_set_checksum(parameters,0xb6015ea8,0xd8cc3428,m);
 }
 uint32_t *b=thug_skater_construction_boundary_draft;
 if(b){b[0]=0x45ee20;b[1]=(uintptr_t)parameters;b[2]=(uintptr_t)p;b[3]=1;}
 __builtin_trap();
}
