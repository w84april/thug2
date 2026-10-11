#include "../../src/game/components.h"
#include "../../src/collision/probe.h"
#include "../../src/graphics/decal_scene.h"
#include "../../src/core/line.h"
#include "../../src/core/random.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* New host routes: 0x100+mode preserves 5bafc0's non-default mode;
 * 0x200+mode denotes 5bb000 allocation before its exact zero fill. These are
 * allocator ports, not recovered virtual heap operations. Mode1 raw allocation
 * retains the established route1. Explicit-heap argument is zero in this path. */
uint8_t thug_particle_allocation_mode_draft;
static void *allocate(uint32_t size,int zero,const ThugMemory *m){
 uint32_t mode=thug_particle_allocation_mode_draft,route=zero?0x200+mode:mode==1?1:0x100+mode;
 void *p=m->allocate(m->context,size,route);if(p&&zero)__builtin_memset(p,0,size);return p;
}
/* Constructor identities only; unbound lifecycle/render virtuals unavailable. */
const void *const thug_particle_base_methods_draft[]={0},*const thug_particle_base_node_methods_draft[]={0};
int32_t thug_particle_one_segment_draft(void *);
int32_t thug_particle_four_colors_draft(void *);
const void *const thug_particle_buffer_methods_draft[]={[2]=thug_particle_one_segment_draft,[3]=thug_particle_four_colors_draft},*const thug_particle_buffer_node_methods_draft[]={0};
const void *const thug_particle_point_methods_draft[]={[2]=thug_particle_one_segment_draft,[3]=thug_particle_four_colors_draft},*const thug_particle_point_node_methods_draft[]={0};
extern uint32_t thug_mesh_shader_handles_draft[18];
/* Optional comparison breakpoint before the shared texture dictionary is used.
 * The real training startup has not yet recovered that dictionary's loading. */
uint32_t *thug_particle_create_boundary_draft;
/* 00496d70. Raw defaults preserve every unassigned field and flag bit. */
void thug_particle_reset_draft(void *p){
 static const unsigned zero[]={0xfc,0x100,0x104,0xdc,0x70,0x74,0x80,0x84,0x88,0x2c,0x30,0x34,0x38,0x3c,0xa0,0xa8,0xb0,0xd0,0xd8,0xe0,0xe4,0xe8,0x78};
 static const unsigned one[]={0xc4,0x98,0x9c,0xd4,0x90,0xec,0x60,0x64,0x68,0x6c};
 static const unsigned two[]={0xb4,0xb8,0xbc,0xc0,0xc8,0xcc,0x94};
 for(unsigned i=0;i<sizeof(zero)/sizeof(*zero);i++)put(p,zero[i],0);
 for(unsigned i=0;i<sizeof(one)/sizeof(*one);i++)put(p,one[i],0x3f800000);
 for(unsigned i=0;i<sizeof(two)/sizeof(*two);i++)put(p,two[i],0x40000000);
 put(p,0x20,0x45000000);put(p,0x24,0x43100000);put(p,0x28,0xc4680000);put(p,0xa4,0x3f000000);put(p,0xac,0xbca3d70a);
 static const unsigned bytes[]={0x124,0x12c,0x12d,0x128,0x127,0x125,0x131,0x126,0x132};
 for(unsigned i=0;i<sizeof(bytes)/sizeof(*bytes);i++)((uint8_t *)p)[bytes[i]]=0;
 ((uint8_t *)p)[0x12f]=1;((uint8_t *)p)[0x129]=1;((uint8_t *)p)[0x130]=1;((uint8_t *)p)[0x133]=1;
 put(p,0x120,(word(p,0x120)&~0x11u)|0x100);
}
/* 00496f10. The reference target and intrusive list have distinct identities. */
void *thug_particle_base_construct_draft(void *p){
 thug_reference_target_initialize(p);void *node=(char *)p+12;
 put(node,4,(uintptr_t)p);put(node,8,0);put(node,12,(uintptr_t)node);put(node,16,(uintptr_t)node);
 put(p,0,(uintptr_t)thug_particle_base_methods_draft);put(node,0,(uintptr_t)thug_particle_base_node_methods_draft);
 put(p,0x120,0);thug_particle_reset_draft(p);return p;
}
/* 0049b660. The six unused original arguments remain in the exported ABI. */
void *thug_particle_buffer_construct_draft(void *p,uint32_t name,uint32_t count,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,const ThugMemory *m){
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;thug_particle_base_construct_draft(p);
 put(p,0,(uintptr_t)thug_particle_buffer_methods_draft);put(p,12,(uintptr_t)thug_particle_buffer_node_methods_draft);
 put(p,0xf0,name);put(p,0x7c,count);put(p,0x8c,0);
 void *storage=allocate(count*0x30+4,0,m),*records=0;
 if(storage){put(storage,0,count);records=(char *)storage+4;for(uint32_t i=0;i<count;i++)thug_segment_initialize((char *)records+i*0x30);}
 put(p,0xf8,(uintptr_t)records);if(!records)return p;
 storage=allocate(count*12,0,m);put(p,0x11c,(uintptr_t)storage);if(!storage)return p;
 for(unsigned o=0x10c;o<=0x114;o+=4){storage=allocate(16,0,m);if(storage)for(unsigned i=0;i<4;i++)thug_segment_initialize((char *)storage+i*4);put(p,o,(uintptr_t)storage);if(!storage)return p;}
 for(unsigned i=0;i<16;i+=4)for(unsigned o=0x10c;o<=0x114;o+=4)for(unsigned j=0;j<4;j++)((uint8_t *)ptr(p,o))[i+j]=0x80;
 put(p,0x108,0xbf800000);put(p,0x120,word(p,0x120)|4);return p;
}
/* 004d9cf0. Original blend checksum dispatch, including default zero. */
uint32_t thug_particle_blend_draft(uint32_t mode){
 switch(mode){case 0x02e58c18:return 1;case 0xa86285a1:return 2;case 0xa7fd7d23:case 0xdea7e576:return 3;
 case 0x0d7a749a:case 0x0eea99ff:return 4;case 0x54628ed7:return 5;case 0x18b98905:return 6;
 case 0x40f44b8a:return 7;case 0x90b93703:return 8;case 0x68e77f40:return 9;case 0xb8aa03c9:return 10;default:return 0;}
}
/* 004d9b80. Actual texture table lookup, material defaults, CRT random checksum,
 * signed alpha conversion and shader selection; no renderer is supplied. */
void *thug_particle_material_construct_draft(void *p,uint32_t count,uint32_t kind,uint32_t texture,uint32_t blend,uint32_t alpha,uint32_t a,uint32_t b,const ThugMemory *m){
 if(thug_particle_create_boundary_draft){uint32_t *r=thug_particle_create_boundary_draft;r[0]=0x4d9b80;r[1]=texture;r[2]=(uintptr_t)p;r[3]=1;__builtin_trap();}
 (void)count;(void)kind;(void)a;(void)b;void *entry=thug_texture_dictionary_find(thug_decal_texture_dictionary,texture),*resource=0;
 if(entry)resource=word(entry,8)&1?ptr(ptr(entry,16),0):ptr(entry,16);
 void *material=m->allocate(m->context,0x110,1);if(material)thug_render_material_initialize(material);
 put(material,0x20,resource?0x44:0x40);uint32_t r=thug_crt_random();put(material,0,r*thug_crt_random());put(material,8,1);put(material,0x30,(uintptr_t)resource);
 put(material,0x80,thug_particle_blend_draft(blend)|(alpha<<24));
 for(unsigned o=0x40;o<0x4c;o+=4)put(material,o,0x3f000000);
 float opacity=(float)thug_platform_round_x87_single((double)(int32_t)alpha*0.0078125);__builtin_memcpy((char *)material+0x4c,&opacity,4);
 put(material,0x90,0);put(material,0xe0,0);((uint8_t *)material)[16]=1;((uint8_t *)material)[13]=1;((uint8_t *)material)[14]=0;
 put(p,0,(uintptr_t)material);uint32_t code=word(material,0x80)&0xffffff;put(p,4,thug_mesh_shader_handles_draft[code==9||code==10?9:17]);return p;
}
/* 004c21a0. Point-sprite class used by the actual training barrel fire. */
void *thug_particle_point_construct_draft(void *p,uint32_t name,uint32_t count,uint32_t texture,uint32_t blend,uint32_t alpha,const ThugMemory *m){
 thug_particle_buffer_construct_draft(p,name,count,texture,blend,alpha,0,0,0,m);
 put(p,0,(uintptr_t)thug_particle_point_methods_draft);put(p,12,(uintptr_t)thug_particle_point_node_methods_draft);
 void *material=m->allocate(m->context,8,1);if(material)thug_particle_material_construct_draft(material,count,2,texture,blend,alpha,0,0,m);put(p,0x134,(uintptr_t)material);return p;
}
/* 004bcef0 PARTIAL. Other classes remain explicit unavailable branches. */
void *thug_particle_factory_prefix_draft(uint32_t name,uint32_t type,uint32_t count,uint32_t segments,uint32_t texture,uint32_t blend,uint32_t alpha,uint32_t a,uint32_t b,uint32_t c,uint32_t d,const ThugMemory *m){
 (void)segments;(void)a;(void)b;(void)c;(void)d;if(type!=0xf4d8d486)__builtin_trap();
 void *p=allocate(0x138,1,m);return p?thug_particle_point_construct_draft(p,name,count,texture,blend,alpha,m):0;
}
/* 00497a70 and 00496ce0. Raw byte and ordered raw-word copies preserve aliases. */
void thug_particle_emission_draft(void *p,uint32_t value){uint8_t v=value;put(p,0x120,v?word(p,0x120)|0x10000:word(p,0x120)&~0x10000u);((uint8_t *)p)[0x12a]=v;}
void thug_particle_color_draft(void *p,const void *color){if(word(p,0x120)&0x10000)for(unsigned i=0;i<4;i++)put(p,0x60+4*i,word(color,4*i));}
/* 0049ac20. Valid intrusive list nodes have non-null links. */
void *thug_particle_find_draft(const void *manager,uint32_t name){void *list=ptr(manager,20);if(!list)return 0;void *node=ptr(list,12);
 while(word(node,4)!=0xffffffff&&node){void *p=(char *)node-12;if(!p)break;if(word(p,0xf0)==name)return p;node=ptr(node,12);}return 0;}
/* 0049ac60. The selected class comes from the partial factory above. Failure
 * cleanup remains an actual virtual dispatch; its class bodies are unbound. */
void *thug_particle_manager_create_draft(void *manager,uint32_t name,uint32_t type,uint32_t count,uint32_t segments,uint32_t texture,uint32_t blend,uint32_t alpha,uint32_t a,uint32_t b,uint32_t c,uint32_t reuse,uint32_t inherit,uint32_t d,const ThugMemory *m){
 uint32_t heap=word(manager,16);if(!heap)heap=word(manager,8);m->temp_scope(m->context,heap);
 void *p=thug_particle_factory_prefix_draft(name,type,count,segments,texture,blend,alpha,a,b,c,d,m);m->temp_scope(m->context,0);if(!p)return 0;
 if(!(word(p,0x120)&4)){typedef void (*Delete)(void *,uint32_t);((Delete *)ptr(p,0))[0](p,1);return 0;}
 ((uint8_t *)p)[0x12e]=reuse!=0;put(p,0x120,word(p,0x120)|1);thug_particle_emission_draft(p,1);put(p,0x120,word(p,0x120)|0x10000);((uint8_t *)p)[0x12b]=0;
 if((uint8_t)inherit){put(p,0x120,word(p,0x120)|0x10000);thug_particle_color_draft(p,(char *)manager+24);}
 void *list=ptr(manager,20),*node=(char *)p+12;put(node,16,word(list,16));put(node,12,(uintptr_t)list);put(ptr(list,16),12,(uintptr_t)node);put(list,16,(uintptr_t)node);return p;
}
extern void *thug_cutscene_context_draft;
uint32_t thug_script_get_text_legacy_draft(const ThugScriptStructure *,uint32_t,const char **,uint32_t);
void *thug_flexparticle_construct_draft(void *);
void thug_flexparticle_finalize_draft(void *);
void thug_flexparticle_visibility_draft(void *,uint32_t);
extern const ThugComponentMethods thug_flexparticle_create_methods_draft;
/* 0041db00 PARTIAL. Original parameter order and reference behavior through
 * engine creation. Neither post-creation setup nor scripts are substituted. */
void thug_flexparticle_create_initialize_prefix_draft(void *p,const ThugScriptStructure *s){
 thug_script_get_checksum(s,0xa1dc81f9,(void *)((char *)p+0x24),0);
 float capacity=1;thug_script_get_float(s,0x6289dd76,&capacity,0);uint32_t count=thug_truncate_double_low_word(capacity);
 uint32_t segments=2,texture=0,blend=0x515e298e,type=0xaab555bb,alpha=0,a=8,c=1,reuse=0,local_count=0;
 float b=.5f,local_float=0;const char *model=0;
 thug_script_get_integer(s,0x9e52a20f,&segments,0);thug_script_get_checksum(s,0x7d99f28d,&texture,0);
 thug_script_get_checksum(s,0xdd6bb3d5,&blend,0);thug_script_get_checksum(s,0x7321a8d6,&type,0);
 thug_script_get_checksum(s,0x184197d5,(void *)((char *)p+0x28),0);thug_script_get_integer(s,0xa605b89f,&alpha,0);
 thug_script_get_integer(s,0xd93124d6,&a,0);thug_script_get_float(s,0x4e0a65ee,&b,0);thug_script_get_integer(s,0xd8458fb4,&c,0);
 thug_script_get_integer(s,0xd5928f25,&reuse,0);thug_script_get_integer(s,0x03d4e483,&local_count,0);
 thug_script_get_float(s,0x8e9a640e,&local_float,0);thug_script_get_text_legacy_draft(s,0x286a8d26,&model,0);
 uint8_t inherit=thug_script_has_flag(s,0xa0e585b0);ThugObjectReference *reference=(void *)((char *)p+0x18);
 if(reuse){void *effect=thug_particle_find_draft(thug_cutscene_context_draft,word(p,0x24));thug_object_reference_assign(reference,effect);if(reference->object)__builtin_trap();}
 put(p,0x24,(uintptr_t)p);void *effect=thug_particle_manager_create_draft(thug_cutscene_context_draft,(uintptr_t)p,type,count,segments,texture,blend,alpha,a,word(&b,0),c,reuse,inherit,(uintptr_t)model,thug_component_services->memory);
 thug_object_reference_assign(reference,effect);if(reference->object)__builtin_trap();
}
static void visibility_entry(void *p,void *v){thug_flexparticle_visibility_draft(p,(uintptr_t)v);}
const ThugComponentMethods thug_flexparticle_create_methods_draft={.initialize=thug_flexparticle_create_initialize_prefix_draft,.finalize=thug_flexparticle_finalize_draft,.unknown_20=visibility_entry};
/* Same already recovered factory, with the initializer identity versioned so
 * prior immutable boundary fixtures retain their original comparison point. */
void *thug_flexparticle_create_versioned_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x3c,m);if(p){thug_flexparticle_construct_draft(p);put(p,0,(uintptr_t)&thug_flexparticle_create_methods_draft);}return p;}
