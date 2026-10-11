#include "../../src/core/lookup.h"
#include "../../src/core/bounds.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
typedef struct {uintptr_t unavailable[7];void *(*create_sector)(void *,const ThugMemory *);} SceneMethods;
extern const SceneMethods thug_model_scene_base_methods_draft,thug_model_scene_pc_methods_draft;
const uintptr_t thug_model_scene_list_methods_draft[1]={0};
const uintptr_t thug_model_mesh_list_methods_draft[1]={0};
const uintptr_t thug_model_sector_base_methods_draft[16]={0};
const uintptr_t thug_model_sector_pc_methods_draft[16]={0};
static void *sentinel(const uintptr_t *methods,const ThugMemory *m){
    void *p=thug_allocate_zeroed(20,m);
    if(p){put(p,4,0xffffffff);put(p,8,0);put(p,12,(uintptr_t)p);put(p,16,(uintptr_t)p);put(p,0,(uintptr_t)methods);}
    return p;
}
/* 0049d390: initialized heap; caller provides 640 bytes, shift0..12.
 * Retain the original unspecified bytes and allocation order. */
void *thug_model_scene_base_construct_draft(void *p,uint32_t shift,const ThugMemory *m){
    put(p,0,(uintptr_t)&thug_model_scene_base_methods_draft);
    thug_bounds_reset((ThugBounds *)((uint8_t *)p+0x90));thug_bounds_reset((ThugBounds *)((uint8_t *)p+0xb0));
    put(p,0xd4,0);ThugObjectLookupTable *table=m->allocate(m->context,24,1);
    if(table)thug_object_table_initialize(table,shift,m);put(p,0xd0,(uintptr_t)table);
    const unsigned words[]={0xd4,0x15c,0x160,0x158,0x1e4,0x26c,0x270,0x268};
    const unsigned bytes[]={4,0xd8,0x164,0x274,0x275};
    for(unsigned i=0;i<sizeof(words)/sizeof(*words);i++)put(p,words[i],0);
    for(unsigned i=0;i<sizeof(bytes)/sizeof(*bytes);i++)((uint8_t *)p)[bytes[i]]=0;
    put(p,0x278,(uintptr_t)sentinel(thug_model_scene_list_methods_draft,m));
    put(p,0x27c,(uintptr_t)sentinel(thug_model_scene_list_methods_draft,m));
    ((uint8_t *)p)[0x8c]=0;((uint8_t *)p)[0x8d]=0;return p;
}
/* 004c6130. */
void *thug_model_scene_construct_draft(void *p,uint32_t shift,const ThugMemory *m){
    thug_model_scene_base_construct_draft(p,shift,m);put(p,0,(uintptr_t)&thug_model_scene_pc_methods_draft);return p;
}
/* 0049e900 /004c6550. These constructors intentionally retain the name,
 * sector flags and final word until the model parser assigns them. */
void *thug_model_sector_base_construct_draft(void *p){
    put(p,0,(uintptr_t)thug_model_sector_base_methods_draft);put(p,8,1);
    put(p,0x14,0);put(p,0x18,0);put(p,0x10,0);put(p,12,0xe3714dc1);return p;
}
void *thug_model_sector_construct_draft(void *p){
    thug_model_sector_base_construct_draft(p);put(p,0,(uintptr_t)thug_model_sector_pc_methods_draft);
    put(p,0x20,0);put(p,0x24,0);put(p,0x28,0);put(p,0x2c,0x3f800000);return p;
}
/* 004c6190, the PC scene's +1c virtual. */
void *thug_model_scene_create_sector_draft(void *scene,const ThugMemory *m){
    (void)scene;void *p=m->allocate(m->context,52,1);return p?thug_model_sector_construct_draft(p):0;
}
const SceneMethods thug_model_scene_base_methods_draft={0};
const SceneMethods thug_model_scene_pc_methods_draft={.create_sector=thug_model_scene_create_sector_draft};
/* 0049ca10: the selected scene virtual must return a valid sector. */
void *thug_model_scene_new_sector_draft(void *scene,const ThugMemory *m){
    const SceneMethods *methods=pointer(scene,0);void *p=methods->create_sector(scene,m);
    put(p,0x14,0);put(p,0x18,0);return p;
}
/* 0049e660. */
void thug_model_sector_bind_geometry_draft(void *sector,void *geometry){put(sector,0x14,(uintptr_t)geometry);}
/* 004b5f60: allocate a mesh sentinel in the compression heap. Existing list
 * storage is simply overwritten, exactly as in the original initializer. */
void thug_model_geometry_mesh_list_initialize_draft(void *geometry,const ThugMemory *m){
    m->temp_scope(m->context,2);put(geometry,0x38,(uintptr_t)sentinel(thug_model_mesh_list_methods_draft,m));m->temp_scope(m->context,0);
}
/* 0049d4e0: shared5480c0 reads the sector's +4 key; insertion is recovered. */
void thug_model_scene_register_sector_draft(void *scene,void *sector,const ThugMemory *m){
    uint32_t key=word(sector,4);thug_object_table_insert(pointer(scene,0xd0),&key,sector,m);
}
/* Deliberate boundary: complete geometry parsing at4c6650 is still missing. */
void (*thug_model_sector_parse_pending_draft)(void *,const uint8_t **,const ThugMemory *);
extern void *thug_model_geometry_create_draft(const ThugMemory *);
void thug_model_scene_load_geometry_prefix_draft(void *scene,void *header,const uint8_t *cursor,uint32_t count,const ThugMemory *m){
    ((uint8_t *)scene)[0x8c]=0;((uint8_t *)scene)[0x8d]=0;put(scene,0x280,(uintptr_t)header);
    if((int32_t)count>0){
        void *sector=thug_model_scene_new_sector_draft(scene,m),*geometry=thug_model_geometry_create_draft(m);
        put(geometry,0x34,(uintptr_t)scene);thug_model_sector_bind_geometry_draft(sector,geometry);
        thug_model_geometry_mesh_list_initialize_draft(geometry,m);
        if(thug_model_sector_parse_pending_draft)thug_model_sector_parse_pending_draft(sector,&cursor,m);
    }
    __builtin_trap(); /* also stop rather than fabricate the zero-sector tail */
}
