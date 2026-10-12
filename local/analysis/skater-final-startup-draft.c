/* Final two skater startup components. Other lifecycle methods remain pending. */
#include "../../src/game/components.h"
#include "../../src/script/params.h"
#include "../../src/core/checksum.h"
#include "../../src/platform/text.h"
#include "../../src/graphics/decal_scene.h"
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
extern const ThugComponentMethods thug_tag_texture_startup_methods_draft,thug_component_d1515392_startup_methods_draft;
void *thug_texture_dictionary_load_image_draft(void *,const char *,uint32_t,uint32_t,uint32_t,const ThugMemory *);
void *thug_texture_dictionary_clone_image_draft(void *,uint32_t,void *,const ThugMemory *);
uint8_t thug_texture_dictionary_remove_image_draft(void *,void *,const ThugMemory *);
uint8_t thug_texture_image_flag_draft(void *);
/* 0051da80. Constructor is inlined in the original factory. */
void *thug_tag_texture_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x24,m);if(p){thug_component_construct(p);((uint8_t *)p)[0x18]=0;put(p,0x1c,0);put(p,0x20,0);
 put(p,0,(uintptr_t)&thug_tag_texture_startup_methods_draft);put(p,4,0x5b512edc);}return p;
}
/* 004ece10/004ecf20. Preserve untouched sentinel word0 and parent gaps. */
void *thug_component_d1515392_construct_draft(void *p,const ThugMemory *m){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_component_d1515392_startup_methods_draft);put(p,0x1c,0);
 void *node=m->allocate(m->context,12,1);if(node){put(node,4,(uintptr_t)node);put(node,8,(uintptr_t)node);}
 put(p,0x18,(uintptr_t)node);put(p,4,0xd1515392);return p;
}
void *thug_component_d1515392_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x20,m);return p?thug_component_d1515392_construct_draft(p,m):0;}
/* 0051d890. sprintf's fixed C-locale signed format uses the existing adapter.
 * The absent optional integer retains the incoming parameter pointer. */
void thug_tag_texture_initialize_draft(void *p,const ThugScriptStructure *s,const ThugMemory *m){
 uint32_t index=(uintptr_t)s;thug_script_get_integer(s,0xa2b033fd,&index,0);char suffix[32];suffix[0]='_';thug_text_signed_decimal(suffix+1,(int32_t)index);
 m->temp_scope(m->context,2);
 void *entry=thug_texture_dictionary_load_image_draft(thug_decal_texture_dictionary,"tags\\cas_01",1,1,1,m);
 m->temp_scope(m->context,0);
 uint32_t key=thug_crc32_extend_string(0xf4fd2d63,suffix);
 put(p,0x1c,(uintptr_t)thug_texture_dictionary_clone_image_draft(thug_decal_texture_dictionary,key,entry,m));
 thug_texture_image_flag_draft(entry);thug_texture_dictionary_remove_image_draft(thug_decal_texture_dictionary,entry,m);
 m->temp_scope(m->context,2);
 entry=thug_texture_dictionary_load_image_draft(thug_decal_texture_dictionary,"tags\\sticker",1,1,1,m);
 m->temp_scope(m->context,0);key=thug_crc32_extend_string(0x130618a0,suffix);
 put(p,0x20,(uintptr_t)thug_texture_dictionary_clone_image_draft(thug_decal_texture_dictionary,key,entry,m));
 thug_texture_image_flag_draft(entry);thug_texture_dictionary_remove_image_draft(thug_decal_texture_dictionary,entry,m);
}
static void initialize(void *p,const ThugScriptStructure *s){thug_tag_texture_initialize_draft(p,s,thug_component_services->memory);}
static void empty(void *p){(void)p;}static void empty_init(void *p,const ThugScriptStructure *s){(void)p;(void)s;}
void thug_component_suspend_update_draft(void *);
static void suspend_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
static void *pending_dispose(void *p,uint32_t flags,const ThugMemory *m){(void)p;(void)flags;(void)m;__builtin_trap();}
static uint32_t pending_checksum(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
#define TABLE(name,init,desc,frame) const ThugComponentMethods name={.dispose=pending_dispose,.update=frame,.initialize=init,.finalize=empty,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=desc,.checksum=pending_checksum}
TABLE(thug_tag_texture_startup_methods_draft,initialize,thug_component_descriptor_base,suspend_frame);
TABLE(thug_component_d1515392_startup_methods_draft,empty_init,thug_component_descriptor,thug_component_empty_frame_bridge);
