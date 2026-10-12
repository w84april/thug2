/* PC texture cloning and destruction. File and GPU calls use existing ports. */
#include "../../src/core/lookup.h"
#include "../../src/graphics/mesh.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void put16(void *p,unsigned o,uint16_t v){__builtin_memcpy((char *)p+o,&v,2);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
extern const uintptr_t thug_texture_wrapper_pc_methods_draft[],thug_texture_wrapper_base_methods_draft[];
extern ThugMeshResourceLink *thug_texture_resource_registry_draft;
void *thug_texture_wrapper_base_construct_draft(void *);
void *thug_texture_stage_bindings_draft[4]; /* 00786e94 */
typedef struct Texture Texture;
typedef struct {uint32_t pitch;void *bytes;} Locked;
typedef struct {uint32_t format,type,usage,pool,size,multisample,width,height;} Description;
typedef struct {
 uintptr_t first[2];uint32_t (*release)(Texture *);uintptr_t before_levels[10];
 uint32_t (*levels)(Texture *);uintptr_t before_description[3];
 uint32_t (*description)(Texture *,uint32_t,Description *);uintptr_t gap;
 uint32_t (*lock)(Texture *,uint32_t,Locked *,const void *,uint32_t);
 uint32_t (*unlock)(Texture *,uint32_t);
} TextureMethods;
struct Texture{const TextureMethods *methods;};
typedef struct {uintptr_t before_create[23];uint32_t (*create)(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,Texture **,void *);
 uintptr_t before_bind[41];uint32_t (*bind)(void *,uint32_t,void *);} DeviceMethods;
_Static_assert(offsetof(TextureMethods,description)==0x44,"PC texture description slot");
_Static_assert(offsetof(DeviceMethods,bind)==0x104,"PC texture binding slot");
/* 004da730. Reload the cache after the platform callback, as in the original. */
void thug_texture_stage_bind_draft(uint32_t stage,void *texture,uint32_t unused){
 (void)unused;if(thug_texture_stage_bindings_draft[stage]==texture)return;
 const DeviceMethods *d=*(const DeviceMethods **)thug_mesh_device;d->bind(thug_mesh_device,stage,texture);
 thug_texture_stage_bindings_draft[stage]=texture;
}
/* 004e0500. Retain fields beyond+18; this copy is not registry construction.
 * GPU descriptions and pitches control each forward row copy. */
void *thug_texture_resource_copy_draft(void *p,void *source){
 put(p,16,0);put(p,20,0);put(p,24,0);put(p,0,word(source,0));
 for(unsigned o=4;o<12;o+=2)put16(p,o,(uint16_t)word(source,o));
 for(unsigned o=12;o<16;o++)((uint8_t *)p)[o]=((uint8_t *)source)[o];
 Texture *s=ptr(source,16);uint32_t levels=s->methods->levels(s);Description desc;
 s=ptr(source,16);s->methods->description(s,0,&desc);
 const DeviceMethods *device=*(const DeviceMethods **)thug_mesh_device;
 device->create(thug_mesh_device,desc.width,desc.height,levels,0,desc.format,1,(Texture **)((char *)p+16),0);
 for(uint32_t level=0;level<((uint8_t *)p)[12];level++){
  s=ptr(source,16);s->methods->description(s,level,&desc);
  uint32_t rows=desc.height,bytes;
  if(desc.format==0x15)bytes=desc.width*4;
  else {rows=(rows+3)>>2;bytes=desc.width*(desc.format==0x31545844?8:16);}
  Locked input,output;s=ptr(source,16);s->methods->lock(s,level,&input,0,0);
  Texture *t=ptr(p,16);t->methods->lock(t,level,&output,0,0);
  uint8_t *in=input.bytes,*out=output.bytes;
  for(uint32_t row=0;row<rows;row++){
   uint32_t j=0;for(;j<(bytes&~3u);j+=4)put(out,j,word(in,j));for(;j<bytes;j++)out[j]=in[j];
   in+=input.pitch;out+=output.pitch;
  }
  s=ptr(source,16);s->methods->unlock(s,level);t=ptr(p,16);t->methods->unlock(t,level);
 }return p;
}
/* 004e03f0. Remove only the matching ownership node, preserving neighbors. */
void thug_texture_resource_unlink_draft(void *p,const ThugMemory *m){
 ThugMeshResourceLink *n=thug_texture_resource_registry_draft;while(n&&n->value!=p)n=n->next;if(!n)return;
 if(n->previous)n->previous->next=n->next;else thug_texture_resource_registry_draft=n->next;
 if(n->next)n->next->previous=n->previous;m->release(m->context,n);
}
/* 004e06a0. Release secondary then main resource before clearing live bindings. */
void thug_texture_resource_destroy_draft(void *p,const ThugMemory *m){
 thug_texture_resource_unlink_draft(p,m);Texture *t=ptr(p,24);if(t)t->methods->release(t);
 t=ptr(p,16);if(t){t->methods->release(t);for(uint32_t i=0;i<4;i++)if(thug_texture_stage_bindings_draft[i]==ptr(p,16))thug_texture_stage_bind_draft(i,0,0);}
}
/* 004c7fb0/004c7fe0. The original returns only AX. */
uint16_t thug_texture_image_width_draft(void *p){void *r=ptr(p,16);if(!r)return 0;if(word(p,8)&1)r=ptr(r,0);return (uint16_t)word(r,8);}
uint16_t thug_texture_image_height_draft(void *p){void *r=ptr(p,16);if(!r)return 0;if(word(p,8)&1)r=ptr(r,0);return (uint16_t)word(r,10);}
/* 005b9e50 and the already credited common dispatch0049f3b0. */
uint8_t thug_texture_image_false_draft(void *p){(void)p;return 0;}
uint8_t thug_texture_image_flag_draft(void *p){typedef struct{uintptr_t slots[32];uint8_t (*flag)(void *);} Methods;const Methods *t=ptr(p,0);return t->flag(p);}
/* 004c8450. Preserve indirect storage and the original destination+8 test. */
void *thug_texture_image_copy_draft(void *p,void *source,const ThugMemory *m){
 thug_texture_wrapper_base_construct_draft(p);put(p,0,(uintptr_t)thug_texture_wrapper_pc_methods_draft);
 ((uint8_t *)p)[12]=((uint8_t *)source)[12];put(p,8,word(source,8));
 void *r=ptr(source,16);if(word(source,8)&1)r=ptr(r,0);void *copied=0;
 if(r){copied=m->allocate(m->context,32,1);if(copied){r=ptr(source,16);if(word(source,8)&1)r=ptr(r,0);thug_texture_resource_copy_draft(copied,r);}}
 typedef struct{uintptr_t slots[33];uint16_t (*width)(void *);uint16_t (*height)(void *);} Methods;
 const Methods *t=ptr(source,0);uint16_t width=t->width(source);t=ptr(source,0);uint16_t height=t->height(source);
 if(word(source,8)&1){
  void *pack=m->allocate(m->context,16,1);if(pack)__builtin_memset(pack,0,16);put(p,16,(uintptr_t)pack);put(pack,0,(uintptr_t)copied);
  if(word(ptr(source,16),4)){
   uint32_t bytes=(uint32_t)width*height*4;void *buffer=m->allocate(m->context,bytes,1);put(ptr(p,16),4,(uintptr_t)buffer);
   void *input=ptr(ptr(source,16),4);void *output=ptr(ptr(p,16),4);
   for(uint32_t j=0;j<bytes;j+=4)put(output,j,word(input,j));
  }else put(ptr(p,16),4,0);
  if(word(ptr(source,16),8)){
   void *buffer=m->allocate(m->context,(uint32_t)height*height*4,1);put(ptr(p,16),8,(uintptr_t)buffer);
   void *input=ptr(ptr(source,16),8);void *output=ptr(ptr(p,16),8);uint32_t bytes=(uint32_t)width*height*4;
   for(uint32_t j=0;j<bytes;j+=4)put(output,j,word(input,j));
  }else put(ptr(p,16),8,0);
  r=ptr(ptr(source,16),12);if(r){copied=m->allocate(m->context,32,1);if(copied){r=ptr(ptr(source,16),12);thug_texture_resource_copy_draft(copied,r);}put(ptr(p,16),12,(uintptr_t)copied);}else put(ptr(p,16),12,0);
 }else put(p,16,(uintptr_t)copied);return p;
}
/* 004c98b0. Return to direct ownership after destroying auxiliary storage. */
uint8_t thug_texture_image_collapse_draft(void *p,const ThugMemory *m){
 void *pack=ptr(p,16),*base=word(p,8)&1?ptr(pack,0):pack;
 void *buffer=ptr(pack,8);if(buffer){m->release(m->context,buffer);put(ptr(p,16),8,0);}
 buffer=ptr(ptr(p,16),4);if(buffer){m->release(m->context,buffer);put(ptr(p,16),4,0);}
 void *extra=ptr(ptr(p,16),12);if(extra){thug_texture_resource_destroy_draft(extra,m);m->release(m->context,extra);put(ptr(p,16),12,0);}
 m->release(m->context,ptr(p,16));put(p,16,(uintptr_t)base);put(p,8,word(p,8)&~1u);return 1;
}
/* 0049f210. */
void thug_texture_wrapper_base_destroy_draft(void *p){put(p,0,(uintptr_t)thug_texture_wrapper_base_methods_draft);}
/* 004c9d00/004cae60. */
void thug_texture_image_destroy_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_texture_wrapper_pc_methods_draft);if(word(p,8)&1)thug_texture_image_collapse_draft(p,m);
 void *r=ptr(p,16);if(r){thug_texture_resource_destroy_draft(r,m);m->release(m->context,r);}thug_texture_wrapper_base_destroy_draft(p);
}
void *thug_texture_image_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_texture_image_destroy_draft(p,m);if(flags&1)m->release(m->context,p);return p;}
/* 004c8090. Null deletion is accepted by this virtual. */
uint8_t thug_texture_dictionary_pc_remove_draft(void *dictionary,void *entry,const ThugMemory *m){
 (void)dictionary;if(entry){typedef struct{void *(*dispose)(void *,uint32_t,const ThugMemory *);} Methods;const Methods *t=ptr(entry,0);t->dispose(entry,1,m);}return 1;
}
/* 004c9c80. Valid resource/outer allocation is required by the original dereference. */
void *thug_texture_dictionary_pc_clone_draft(void *dictionary,uint32_t key,void *entry,const ThugMemory *m){
 (void)dictionary;void *p=m->allocate(m->context,20,1);if(p)thug_texture_image_copy_draft(p,entry,m);
 void *r=ptr(p,16);if(word(p,8)&1)r=ptr(r,0);put(r,0,key);return p;
}
/* 0049fbe0/0049f500. Cache the original key before deletion callbacks. */
void *thug_texture_dictionary_clone_image_draft(void *dictionary,uint32_t key,void *entry,const ThugMemory *m){
 typedef struct{uintptr_t slots[8];void *(*clone)(void *,uint32_t,void *,const ThugMemory *);} Methods;const Methods *t=ptr(dictionary,0);
 void *p=t->clone(dictionary,key,entry,m);if(p){put(p,4,key);thug_object_table_insert(ptr(dictionary,12),&key,p,m);}return p;
}
uint8_t thug_texture_dictionary_remove_image_draft(void *dictionary,void *entry,const ThugMemory *m){
 uint32_t key=word(entry,4);typedef struct{uintptr_t slots[5];uint8_t (*remove)(void *,void *,const ThugMemory *);} Methods;
 const Methods *t=ptr(dictionary,0);if(!t->remove(dictionary,entry,m))return 0;thug_object_table_remove(ptr(dictionary,12),&key,m);return 1;
}
