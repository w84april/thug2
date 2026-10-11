#include "../../src/core/lookup.h"
#include "../../src/core/checksum.h"
#include "../../src/graphics/mesh.h"
#include "../../src/graphics/decal_scene.h"
#include "../../src/script/params.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void put16(void *p,unsigned o,uint16_t v){__builtin_memcpy((char *)p+o,&v,2);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
extern ThugObjectLookupTable thug_model_texture_table_draft;
extern void *(*thug_scene_file_open_draft)(const char *,const char *);
extern uint32_t (*thug_scene_file_read_draft)(void *,uint32_t,uint32_t,void *);
extern uint32_t (*thug_scene_file_close_draft)(void *);
void *thug_texture_dictionary_construct_draft(void *,uint32_t,const ThugMemory *);
void *thug_texture_wrapper_base_construct_draft(void *);
void *thug_texture_resource_construct_draft(void *,const ThugMemory *);
void *thug_texture_dictionary_cached_draft(uint32_t);
uint32_t thug_script_get_text_legacy_draft(const ThugScriptStructure *,uint32_t,const char **,uint32_t);
/* 005f45e0. Ordered raw reads/writes preserve overlapping inputs. */
void thug_image_palette_expand_draft(void *out,const uint8_t *indices,int32_t count,const void *palette){
 for(int32_t i=0;i<count;i++)put(out,(uint32_t)i*4,word(palette,(uint32_t)indices[i]*4));
}
/* 005f5af0. Consume interleaved x/y bits only while that dimension has bits.
 * Internal contract: bounded dimensions and enough input/output storage. */
void *thug_image_unswizzle_draft(void *out,const void *input,uint32_t width,uint32_t height,uint32_t bytes){
 const uint8_t *in=input;uint32_t pixels=width*height;
 for(uint32_t i=0;i<pixels;i++){
  uint32_t x=0,y=0,mask=1,xbit=1,ybit=1,w=width>>1,h=height>>1;
  while(w||h){if(w){w>>=1;if(i&mask)x|=xbit;xbit<<=1;mask<<=1;}if(h){h>>=1;if(i&mask)y|=ybit;ybit<<=1;mask<<=1;}}
  uint8_t *d=(uint8_t *)out+(y*width+x)*bytes;uint32_t j=0;
  for(;j<(bytes&~3u);j+=4)put(d,j,word(in,j));for(;j<bytes;j++)d[j]=in[j];in+=bytes;
 }return out;
}
typedef struct {uint32_t pitch;void *bytes;} LockedImage;
typedef struct Image Image;
typedef struct {uintptr_t unused[19];uint32_t (*lock)(Image *,uint32_t,LockedImage *,const void *,uint32_t);uint32_t (*unlock)(Image *,uint32_t);} ImageMethods;
struct Image {const ImageMethods *methods;};
typedef struct {uintptr_t unused[23];uint32_t (*create)(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,Image **,void *);} DeviceMethods;
/* 004e0790. File/GPU operations retain the existing explicit platform ports.
 * Preserve read grouping, temporary allocations, swizzle/palette conversion,
 * ignored pitch and retained resource fields. Complete internal files and
 * successful allocation/GPU operations are the tested contract. */
void *thug_image_file_load_draft(const char *name,const ThugMemory *m){
 void *file=thug_scene_file_open_draft(name,"rb");if(!file)return 0;
 uint32_t header[8];thug_scene_file_read_draft(header,32,1,file);
 uint32_t depth=header[4],palette_depth=0;
 if(!depth)depth=32;else if(depth==2)depth=16;else if(depth==0x13){depth=8;palette_depth=32;}else if(depth<16)palette_depth=32;
 void *p=m->allocate(m->context,32,1);if(p)thug_texture_resource_construct_draft(p,m);put(p,20,0);
 uint8_t palette[1024];if(palette_depth)thug_scene_file_read_draft(palette,header[7],1,file);
 uint32_t w=header[2],h=header[3];int linear=!w||(w&(w-1))||!h||(h&(h-1));
 const DeviceMethods *device=*(const DeviceMethods **)thug_mesh_device;
 device->create(thug_mesh_device,w,h,1,0,0x15,1,(Image **)((char *)p+16),0);
 put16(p,4,linear?header[6]:w);put16(p,6,linear?header[6]>>16:h);
 put16(p,8,header[6]);put16(p,10,header[6]>>16);
 uint32_t size=(((depth>>3)*(uint16_t)word(p,4)*(uint16_t)(word(p,4)>>16))+3)&~3u;
 Image *image=ptr(p,16);LockedImage locked;image->methods->lock(image,0,&locked,0,0);
 if(linear&&!palette_depth)thug_scene_file_read_draft(locked.bytes,size,1,file);
 else{
  void *input=m->allocate(m->context,size,1);thug_scene_file_read_draft(input,size,1,file);void *extra=0,*decoded=input;
  if(!linear){if(palette_depth){extra=thug_allocate_array_storage(size,m);decoded=extra;}else decoded=locked.bytes;
   thug_image_unswizzle_draft(decoded,input,w,h,depth>>3);}
  if(palette_depth)thug_image_palette_expand_draft(locked.bytes,decoded,(int32_t)size,palette);
  m->release(m->context,input);m->release(m->context,extra);
 }
 thug_scene_file_close_draft(file);((uint8_t *)p)[12]=1;((uint8_t *)p)[13]=32;((uint8_t *)p)[14]=0;((uint8_t *)p)[15]=0;
 image->methods->unlock(image,0);return p;
}
static unsigned copy(char *out,const char *s){unsigned n=0;do{out[n]=s[n];}while(s[n++]);return n-1;}
static const char *base(const char *s){const char *b=s;while(*s){if(*s=='/'||*s=='\\')b=s+1;s++;}return b;}
/* Versioned identities preserve earlier immutable constructor fixtures. The
 * remaining original virtuals are deliberately unbound, not fake lifecycle. */
typedef struct ThugImageWrapperMethods {uintptr_t dispose;uint8_t (*load)(void *,const char *,uint32_t,uint32_t,const ThugMemory *);} WrapperMethods;
typedef struct ThugImageDictionaryMethods {uintptr_t dispose;void *(*load)(void *,const char *,uint32_t,uint32_t,const ThugMemory *);} DictionaryMethods;
extern const WrapperMethods thug_texture_wrapper_pc_methods_draft;
extern const DictionaryMethods thug_texture_dictionary_pc_methods_draft;
/* 004c7f00. Bounded internal path plus the original platform extension. */
uint8_t thug_texture_image_load_draft(void *p,const char *name,uint32_t a,uint32_t b,const ThugMemory *m){
 (void)a;(void)b;char path[256];unsigned n=copy(path,name);copy(path+n,".img.xbx");void *resource=thug_image_file_load_draft(path,m);put(p,16,(uintptr_t)resource);return resource!=0;
}
/* 0049f220. The low prefix flag byte governs relative-path handling. */
void thug_texture_image_name_load_draft(void *p,const char *name,uint32_t prefix,uint32_t a,const ThugMemory *m){
 char path[512];copy(path,name);if((uint8_t)prefix){if(name[0]=='.'&&name[1]=='.'&&name[2]=='/')copy(path,name+3);else{copy(path,"images/");copy(path+7,name);}}
 put(p,4,thug_crc32_string(base(path)));const WrapperMethods *methods=ptr(p,0);methods->load(p,path,prefix,a,m);
}
/* 004c9b00. Original third argument is ignored and load receives literal1. */
void *thug_texture_image_create_draft(void *dictionary,const char *name,uint32_t prefix,uint32_t unused,const ThugMemory *m){
 (void)dictionary;(void)unused;void *p=m->allocate(m->context,20,1);
 if(p){thug_texture_wrapper_base_construct_draft(p);put(p,0,(uintptr_t)&thug_texture_wrapper_pc_methods_draft);((uint8_t *)p)[13]=0;put(p,16,0);((uint8_t *)p)[12]=0;put(p,8,0);}
 thug_texture_image_name_load_draft(p,name,prefix,1,m);return p;
}
const WrapperMethods thug_texture_wrapper_pc_methods_draft={0,thug_texture_image_load_draft};
const DictionaryMethods thug_texture_dictionary_pc_methods_draft={0,thug_texture_image_create_draft};
/* 004c7360. Existing PC constructor with this stage's relocated virtual table. */
void *thug_particle_dictionary_create_draft(uint32_t key,const ThugMemory *m){void *p=m->allocate(m->context,20,1);if(p){thug_texture_dictionary_construct_draft(p,key,m);put(p,0,(uintptr_t)&thug_texture_dictionary_pc_methods_draft);}return p;}
/* 00640c60. The real static dictionary initializer, including reference wrap. */
void thug_particle_dictionary_initialize_draft(const ThugMemory *m){
 uint32_t key=thug_crc32_string("particle");void *p=thug_texture_dictionary_cached_draft(key);
 if(p)put16(p,8,(uint16_t)word(p,8)+1);else{p=thug_particle_dictionary_create_draft(key,m);thug_object_table_insert(&thug_model_texture_table_draft,&key,p,m);}thug_decal_texture_dictionary=p;
}
/* 0049f560. Basename hashing retains extensions and handles both separators. */
void *thug_texture_dictionary_find_name_draft(const void *p,const char *name){uint32_t key=thug_crc32_string(base(name));void *table=ptr(p,12);return table?thug_object_table_find(table,&key,1):0;}
/* 0049f9b0. Original debug marker5480a0 is a bare RET. */
void *thug_texture_dictionary_load_image_draft(void *p,const char *name,uint32_t a,uint32_t b,uint32_t reuse,const ThugMemory *m){
 const DictionaryMethods *methods=ptr(p,0);void *entry=methods->load(p,name,a,b,m);
 if(entry){put(entry,8,(uint8_t)reuse?word(entry,8)|0x10000:word(entry,8)&~0x10000u);uint32_t key=word(entry,4);thug_object_table_insert(ptr(p,12),&key,entry,m);}return entry;
}
/* 005aa7b0. A non-null wrapper indicates success even if file loading failed;
 * preserve that original behavior instead of inventing a fallback texture. */
uint8_t thug_script_load_particle_texture_draft(const ThugScriptStructure *s,void *script,const ThugMemory *m){
 (void)script;const char *name;thug_script_get_text_legacy_draft(s,0,&name,0);if(!*name)return 0;
 void *entry=thug_texture_dictionary_find_name_draft(thug_decal_texture_dictionary,name);uint8_t reuse=thug_script_has_flag(s,0xd5928f25);
 if(!entry)entry=thug_texture_dictionary_load_image_draft(thug_decal_texture_dictionary,name,1,1,reuse,m);return entry!=0;
}

#include "../../src/game/components.h"
#include "../../src/core/number.h"
#include "../../src/script/delivery.h"
uint8_t thug_script_load_particle_texture_entry_draft(const ThugScriptStructure *s,void *script){return thug_script_load_particle_texture_draft(s,script,thug_event_services->memory);}
void *thug_particle_find_draft(const void *,uint32_t);
void *thug_particle_manager_create_draft(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
uint32_t *thug_particle_image_boundary_draft;
static void initialization_boundary(void *p,const ThugScriptStructure *s){if(thug_particle_image_boundary_draft){uint32_t *b=thug_particle_image_boundary_draft;b[0]=0x41dd49;b[1]=(uintptr_t)s;b[2]=(uintptr_t)p;b[3]=1;}__builtin_trap();}
extern void *thug_cutscene_context_draft;
uint32_t thug_script_get_text_legacy_draft(const ThugScriptStructure *,uint32_t,const char **,uint32_t);
void *thug_flexparticle_construct_draft(void *);
void thug_flexparticle_finalize_draft(void *);
void thug_flexparticle_visibility_draft(void *,uint32_t);
extern const ThugComponentMethods thug_flexparticle_image_methods_draft;
/* 0041db00 PARTIAL. Original parameter order and reference behavior through
 * engine creation. Neither post-creation setup nor scripts are substituted. */
void thug_flexparticle_image_initialize_prefix_draft(void *p,const ThugScriptStructure *s){
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
 if(reuse){void *effect=thug_particle_find_draft(thug_cutscene_context_draft,word(p,0x24));thug_object_reference_assign(reference,effect);if(reference->object)initialization_boundary(p,s);}
 put(p,0x24,(uintptr_t)p);void *effect=thug_particle_manager_create_draft(thug_cutscene_context_draft,(uintptr_t)p,type,count,segments,texture,blend,alpha,a,word(&b,0),c,reuse,inherit,(uintptr_t)model,thug_component_services->memory);
 thug_object_reference_assign(reference,effect);if(reference->object)initialization_boundary(p,s);
}
static void visibility_entry(void *p,void *v){thug_flexparticle_visibility_draft(p,(uintptr_t)v);}
const ThugComponentMethods thug_flexparticle_image_methods_draft={.initialize=thug_flexparticle_image_initialize_prefix_draft,.finalize=thug_flexparticle_finalize_draft,.unknown_20=visibility_entry};
/* Same already recovered factory, with the initializer identity versioned so
 * prior immutable boundary fixtures retain their original comparison point. */
void *thug_flexparticle_image_versioned_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x3c,m);if(p){thug_flexparticle_construct_draft(p);put(p,0,(uintptr_t)&thug_flexparticle_image_methods_draft);}return p;}
