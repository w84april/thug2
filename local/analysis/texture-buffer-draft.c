#include "../../src/core/lookup.h"
#include "../../src/graphics/mesh.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void put16(void *p,unsigned o,uint16_t v){__builtin_memcpy((uint8_t *)p+o,&v,2);}
extern ThugObjectLookupTable thug_model_texture_table_draft;
/* These are identities only: destruction/drawing virtuals remain unavailable. */
const uintptr_t thug_texture_dictionary_base_methods_draft[1]; /*649bb4*/
const uintptr_t thug_texture_dictionary_pc_methods_draft[1]; /*64a824*/
const uintptr_t thug_texture_wrapper_base_methods_draft[1]; /*649af0*/
const uintptr_t thug_texture_wrapper_pc_methods_draft[1]; /*64a770*/
ThugMeshResourceLink *thug_texture_resource_registry_draft; /*7cc254*/
/* Heap port. Original5ba090 returns allocation-16, whose first word identifies
 * its owning heap. The provider translates that owner into ThugMemory scope IDs.
 * No provider or successful GPU implementation is invented here. */
uint32_t (*thug_texture_allocation_scope_draft)(const void *);

extern void thug_object_table_clear_draft(ThugObjectLookupTable *,const ThugMemory *);
/* 0049f830: only the low flag byte determines whether to allocate a table. */
void *thug_texture_dictionary_base_construct_draft(void *p,uint32_t key,uint32_t table,const ThugMemory *m){
    put(p,4,key);put(p,0,(uintptr_t)thug_texture_dictionary_base_methods_draft);put16(p,8,1);
    void *t=0;
    if((uint8_t)table){t=m->allocate(m->context,24,1);if(t)thug_object_table_initialize(t,5,m);}
    put(p,12,(uintptr_t)t);return p;
}
/* 004c8070. PC-specific storage at+10 is left untouched. */
void *thug_texture_dictionary_construct_draft(void *p,uint32_t key,const ThugMemory *m){
    thug_texture_dictionary_base_construct_draft(p,key,1,m);
    put(p,0,(uintptr_t)thug_texture_dictionary_pc_methods_draft);return p;
}
/* 004e04b0: resource ownership registry, retaining unspecified texture fields. */
void *thug_texture_resource_construct_draft(void *p,const ThugMemory *m){
    put(p,16,0);put(p,20,0);put(p,24,0);((uint8_t *)p)[28]=0;
    ThugMeshResourceLink *node=m->allocate(m->context,12,1),*old=thug_texture_resource_registry_draft;
    node->value=p;node->previous=0;node->next=old;thug_texture_resource_registry_draft=node;
    if(old)old->previous=node;return p;
}
/* 0049f200. */
void *thug_texture_wrapper_base_construct_draft(void *p){
    put(p,0,(uintptr_t)thug_texture_wrapper_base_methods_draft);put16(p,10,0);return p;
}
typedef struct Texture Texture;
typedef struct {int32_t pitch;void *bytes;} LockedTexture;
typedef struct {uintptr_t unavailable[19];uint32_t (*lock)(Texture *,uint32_t,LockedTexture *,const void *,uint32_t);
    uint32_t (*unlock)(Texture *,uint32_t);} TextureMethods;
struct Texture {const TextureMethods *methods;};
typedef struct {uintptr_t unavailable[23];uint32_t (*create)(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,Texture **,void *);} TextureDeviceMethods;
_Static_assert(offsetof(TextureMethods,lock)==0x4c,"original texture lock slot");
_Static_assert(offsetof(TextureDeviceMethods,create)==0x5c,"original device texture creation slot");

/* 004cb420. Internal parser contract: complete bounded file data, successful
 * allocations and GPU operations. This deliberately preserves the original
 * linear mip copy (it ignores reported pitch) and leaves the caller cursor
 * unchanged. The file version and palette-byte count are read/ignored as in PC.
 * Format for unrecognized encodings retains the original scratch argument.
 * No DXT decoding or rendering is performed by this recovered loader. */
ThugObjectLookupTable *thug_texture_buffer_parse_draft(const uint8_t **input,ThugObjectLookupTable *table,uint32_t rebuild,const ThugMemory *m){
    const uint8_t *p=*input+8;uint32_t count=word(*input,4),format=rebuild;
    if((uint8_t)rebuild){
        uint32_t slots=2,shift=1;
        while(slots<count*2&&shift<12){slots*=2;shift++;}
        if(!thug_texture_allocation_scope_draft)__builtin_trap();
        uint32_t scope=thug_texture_allocation_scope_draft(table);
        if(table){if(table->buckets){thug_object_table_clear_draft(table,m);m->release(m->context,table->buckets);table->buckets=0;}m->release(m->context,table);}
        m->temp_scope(m->context,scope);
        table=m->allocate(m->context,24,1);format=(uintptr_t)table;
        if(table)thug_object_table_initialize(table,shift,m);
        m->temp_scope(m->context,0);
    }
    if((int32_t)count<1)return table;
    do{
        void *resource=m->allocate(m->context,32,1);
        if(resource)thug_texture_resource_construct_draft(resource,m);
        put(resource,0,word(p,0));
        uint32_t width=word(p,4),height=word(p,8),mips=word(p,12),depth=word(p,16),palette_depth=word(p,20),compression=word(p,24),palette_bytes=word(p,28);
        put16(resource,4,width);put16(resource,6,height);
        ((uint8_t *)resource)[12]=mips;((uint8_t *)resource)[13]=depth;
        ((uint8_t *)resource)[14]=palette_depth;((uint8_t *)resource)[15]=compression;p+=32;
        if((uint8_t)compression==1||(uint8_t)compression==2)format=0x31545844;
        else if((uint8_t)compression==5)format=0x35545844;
        else if(!(uint8_t)compression){
            if((uint8_t)depth==8)format=0x29;
            else if((uint8_t)depth==16)format=0x19;
            else if((uint8_t)depth==32)format=0x15;
        }
        const TextureDeviceMethods *device=*(const TextureDeviceMethods **)thug_mesh_device;
        device->create(thug_mesh_device,(uint16_t)width,(uint16_t)height,(uint8_t)mips,0,format,1,(Texture **)((uint8_t *)resource+16),0);
        if(!palette_bytes)put(resource,20,0);
        for(uint32_t level=0;level<((uint8_t *)resource)[12];level++){
            uint32_t size=word(p,0);p+=4;Texture *texture=ptr(resource,16);LockedTexture locked;
            texture->methods->lock(texture,level,&locked,0,0);
            /* Original REP MOVSD then MOVSB; buffers do not overlap. */
            __builtin_memcpy(locked.bytes,p,size);p+=size;
            texture=ptr(resource,16);texture->methods->unlock(texture,level);
        }
        void *wrapper=m->allocate(m->context,20,1);
        if(wrapper){
            thug_texture_wrapper_base_construct_draft(wrapper);put(wrapper,0,(uintptr_t)thug_texture_wrapper_pc_methods_draft);
            ((uint8_t *)wrapper)[13]=0;put(wrapper,16,0);((uint8_t *)wrapper)[12]=0;put(wrapper,8,0);
        }
        put(wrapper,16,(uintptr_t)resource);put(wrapper,4,word(resource,0));
        thug_object_table_insert(table,resource,wrapper,m);
    }while(--count);
    return table;
}
/* 004cb7c0: an empty existing table is replaced with file-sized storage.
 * A nonempty table is extended; a null dictionary table stays null. */
uint32_t thug_texture_dictionary_load_buffer_draft(void *p,const uint8_t *data,const ThugMemory *m){
    ThugObjectLookupTable *t=ptr(p,12);
    if(!t){thug_texture_buffer_parse_draft(&data,0,0,m);return 1;}
    uint32_t count=0;t->iteration_bucket=UINT32_MAX;t->iteration_node=0;
    for(;;){t=ptr(p,12);if(!thug_object_table_next(t)||!t->iteration_node||!t->iteration_node->value)break;count++;}
    t=ptr(p,12);
    if(!count)put(p,12,(uintptr_t)thug_texture_buffer_parse_draft(&data,t,1,m));
    else thug_texture_buffer_parse_draft(&data,t,0,m);
    return 1;
}
/* 004c72e0: the last five file options are ignored by the original PC path. */
void *thug_texture_dictionary_create_buffer_draft(uint32_t key,const uint8_t *data,uint32_t size,uint32_t copy,uint32_t offset,uint32_t skin,uint32_t flag,const ThugMemory *m){
    (void)size;(void)copy;(void)offset;(void)skin;(void)flag;
    void *p=m->allocate(m->context,20,1);if(p)thug_texture_dictionary_construct_draft(p,key,m);
    thug_texture_dictionary_load_buffer_draft(p,data,m);return p;
}
/* 0049f010: dictionary cache lookup (no reference-count increment). */
void *thug_texture_dictionary_cached_draft(uint32_t key){return thug_object_table_find(&thug_model_texture_table_draft,&key,0);}
/* 0049f050: wraparound key+offset, create on miss and insert only afterwards. */
void *thug_texture_dictionary_get_buffer_draft(uint32_t key,const uint8_t *data,uint32_t size,uint32_t copy,uint32_t offset,uint32_t skin,uint32_t flag,const ThugMemory *m){
    uint32_t combined=key+offset;void *p=thug_texture_dictionary_cached_draft(combined);
    if(!p){p=thug_texture_dictionary_create_buffer_draft(combined,data,size,copy,offset,skin,flag,m);
        put(p,4,combined);thug_object_table_insert(&thug_model_texture_table_draft,&combined,p,m);}
    return p;
}
