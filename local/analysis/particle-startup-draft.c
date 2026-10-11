#include "../../src/game/ui_manager.h"
#include "../../src/game/components.h"
#include "../../src/script/symbols.h"
#include "../../src/script/values.h"
void *thug_cutscene_context_draft; /* 006fa7c0, only the list field is used here. */
static uint32_t read_word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void start_reference(ThugObjectReference *r,ThugReferencedObject *o){r->object=o;r->previous=r->next=0;if(o)thug_object_reference_link(o,r);}
static void clear_reference(ThugObjectReference *r){if(r->object){thug_object_reference_unlink(r->object,r);r->object=0;}r->object=0;}
/* 0044a380. This tests the stored symbol type, without resolving aliases. */
uint8_t thug_script_global_exists_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
 (void)script;uint32_t name=0,kind=0;thug_script_get_checksum(s,0xa1dc81f9,&name,0);thug_script_get_checksum(s,0x7321a8d6,&kind,0);
 unsigned type=0;switch(kind){
 case 0x21902065:case 0xa1dc81f9:type=13;break;
 case 0x456d28d1:case 0x90fec815:type=10;break;
 case 0xa5f054f4:case 0xebae254e:type=1;break;
 case 0x365aa16a:type=2;break;case 0x5ef31148:type=12;break;case 0x61414d56:type=3;break;
 case 0xe491b7a4:type=6;break;case 0xf6a5e196:type=5;break;
 }
 const ThugScriptSymbol *symbol=thug_script_symbol_find(name);return symbol&&symbol->type==type;
}
/* 0044be40. Required operands accept checksum or integer; addition wraps. */
uint8_t thug_script_mangle_checksums_draft(const ThugScriptStructure *s,ThugScriptInstance *script,const ThugMemory *m){
 uint32_t a,b;if(!thug_script_get_checksum(s,0x174841bc,&a,0))thug_script_get_integer(s,0x174841bc,&a,1);
 if(!thug_script_get_checksum(s,0x8e411006,&b,0))thug_script_get_integer(s,0x8e411006,&b,1);
 thug_script_set_checksum(script->arguments,0xfba40626,a+b,m);return 1;
}
/* 0044a940. Named components and literal/included flags use their own lookups. */
uint8_t thug_script_structure_contains_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
 (void)script;ThugScriptStructure *target;uint32_t name=0;if(!thug_script_get_structure(s,0x90fec815,&target,0))return 0;
 thug_script_get_checksum(s,0,&name,0);if(thug_script_has_name_or_flag(target,name))return 1;return thug_script_has_flag(target,name);
}
/* 0049a8e0 and005ae000. No list allocation or mutation occurs. */
uint32_t thug_cutscene_destroy_list_active_draft(const void *p){return read_word(p,0x10)!=0;}
uint32_t thug_script_cutscene_destroy_list_active_draft(const ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return thug_cutscene_destroy_list_active_draft(thug_cutscene_context_draft);}
/* 004607e0. Missing parameter storage retains the caller's output. */
uint8_t thug_ui_object_get_checksum_draft(const ThugUiObjectBase *p,uint32_t name,uint32_t *out){return p->parameters?thug_script_get_checksum(p->parameters,name,out,0):0;}
/* 004aa2a0. A zero ID searches by index; a nonzero ID optionally writes index.
 * The returned reference is newly linked. Its destination is unlinked on entry. */
ThugObjectReference *thug_ui_child_draft(const ThugUiElement *parent,ThugObjectReference *out,uint32_t name,uint32_t *index){
 ThugObjectReference current;start_reference(&current,parent->children.object);uint32_t i=0;
 while(current.object){
  if(name?current.object->id==name:*index==i){if(name&&index)*index=i;break;}
  ThugReferencedObject *next=((ThugUiElement *)current.object)->next_sibling.object;
  thug_object_reference_unlink(current.object,&current);current.object=next;if(next)thug_object_reference_link(next,&current);++i;
 }
 out->previous=out->next=0;out->object=current.object;if(out->object)thug_object_reference_link(out->object,out);
 if(current.object)thug_object_reference_unlink(current.object,&current);return out;
}
/* 004aa6d0. The temporary reference is released before the raw pointer returns. */
ThugReferencedObject *thug_ui_child_at_draft(const ThugUiElement *parent,uint32_t index){
 ThugObjectReference temporary;thug_ui_child_draft(parent,&temporary,0,&index);ThugReferencedObject *result=temporary.object;
 if(temporary.object)thug_object_reference_unlink(temporary.object,&temporary);return result;
}
/* 004ab130. Local names are checksum-valued object parameters, not object IDs.
 * The original this pointer is unused. */
ThugObjectReference *thug_ui_child_named_draft(void *unused,ThugObjectReference *out,const ThugObjectReference *parent,uint32_t name){
 (void)unused;ThugObjectReference current;start_reference(&current,((ThugUiElement *)parent->object)->children.object);
 while(current.object){uint32_t value;
  if(thug_ui_object_get_checksum_draft((ThugUiObjectBase *)current.object,0x9494a525,&value)&&value==name)break;
  ThugReferencedObject *next=((ThugUiElement *)current.object)->next_sibling.object;
  thug_object_reference_unlink(current.object,&current);current.object=next;if(next)thug_object_reference_link(next,&current);
 }
 out->previous=out->next=0;out->object=current.object;if(out->object)thug_object_reference_link(out->object,out);
 if(current.object)thug_object_reference_unlink(current.object,&current);return out;
}
/* 00462190. Only the secondary (alias) table participates. */
ThugReferencedObject *thug_object_find_alias_draft(const ThugObjectLookupManager *manager,uint32_t name){return thug_object_table_find(manager->secondary,&name,1);}
/* 004ac120. Nested ID structures narrow the manager's live selection, recurse
 * through 'child', then clear the selection. Required index searches have a
 * valid selected parent; all graphs are acyclic and references are valid. */
uint8_t thug_ui_resolve_id_draft(ThugUiManager *manager,const ThugScriptStructure *s,uint32_t field,uint32_t *out){
 ThugObjectReference *selection=&manager->unknown_50;ThugScriptStructure *nested=0;uint32_t name=0,index=UINT32_MAX;
 if(thug_script_get_structure(s,field,&nested,0)){
  uint32_t root_name=0,root_index=UINT32_MAX;thug_script_get_checksum(nested,0,&root_name,0);thug_script_get_integer(nested,0,&root_index,0);
  if(root_name){
   ThugObjectReference found;if(selection->object)thug_ui_child_named_draft(manager,&found,selection,root_name);else thug_ui_find(&found,root_name,0);
   thug_object_reference_assign(selection,found.object);if(found.object)thug_object_reference_unlink(found.object,&found);
   if(!selection->object)return 0;
  }else if(root_index!=UINT32_MAX){thug_object_reference_assign(selection,thug_ui_child_at_draft((ThugUiElement *)selection->object,root_index));if(!selection->object)return 0;}
  uint8_t result=thug_ui_resolve_id_draft(manager,nested,0xdd4cabd6,out);clear_reference(selection);if(result)return result;
 }
 if(thug_script_get_checksum(s,field,&name,0)){
  ThugReferencedObject *object;
  if(selection->object){
   ThugObjectReference found;thug_ui_child_named_draft(manager,&found,selection,name);object=found.object;
   thug_object_reference_assign(selection,object);if(found.object)thug_object_reference_unlink(found.object,&found);
   object=selection->object;if(!object)return 0;
  }else object=thug_object_find_alias_draft(thug_object_lookup_manager,name);
  if(object)name=object->id;clear_reference(selection);*out=name;return 1;
 }
 if(thug_script_get_integer(s,field,&index,0)){
  if(!selection->object)return 0;
  ThugObjectReference found;start_reference(&found,thug_ui_child_at_draft((ThugUiElement *)selection->object,index));clear_reference(selection);
  if(found.object){*out=found.object->id;thug_object_reference_unlink(found.object,&found);return 1;}return 0;
 }
 clear_reference(selection);return 0;
}
/* 00462340. Capture the lookup manager before resolving the supplied ID. */
uint32_t thug_script_object_exists_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
 (void)script;ThugObjectLookupManager *lookup=thug_object_lookup_manager;uint32_t name;
 return thug_ui_resolve_id_draft(thug_ui_manager,s,0x40c698af,&name)?thug_object_manager_find(lookup,name)!=0:0;
}
/* 00460940, descriptor500eb224. Return ObjID through the live script arguments. */
uint8_t thug_object_get_id_command_draft(const ThugReferencedObject *p,const ThugScriptStructure *s,ThugScriptInstance *script,const ThugMemory *m){(void)s;uint32_t id=p->id;thug_script_set_checksum(script->arguments,0x0830ecaf,id,m);return 1;}
void *thug_composite_create_from_array_draft(ThugObjectManager *,ThugScriptArray *,ThugScriptStructure *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
/* 00449540. Build and finalize the actual registered components. */
uint8_t thug_script_create_composite_draft(const ThugScriptStructure *s,ThugScriptInstance *script,const ThugDiagnostics *d,const ThugMemory *m){
 (void)script;ThugScriptArray *components=0;ThugScriptStructure *parameters=0;
 thug_script_get_array(s,0x11b70a02,&components,1);thug_script_get_structure(s,0x7031f10c,&parameters,0);
 thug_composite_create_from_array_draft((ThugObjectManager *)thug_component_type_registry,components,parameters,1,d,m);return 1;
}
/* Fixed original native/member signatures obtain already-scoped host services. */
uint32_t thug_script_mangle_checksums_entry_draft(ThugScriptStructure *s,ThugScriptInstance *i){return thug_script_mangle_checksums_draft(s,i,thug_event_services->memory);}
uint32_t thug_script_create_composite_entry_draft(ThugScriptStructure *s,ThugScriptInstance *i){return thug_script_create_composite_draft(s,i,thug_event_services->diagnostics,thug_event_services->memory);}
uint32_t thug_object_get_id_entry_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *i){return thug_object_get_id_command_draft(p,s,i,thug_event_services->memory);}
