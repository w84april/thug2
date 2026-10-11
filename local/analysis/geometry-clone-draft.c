#include "../../src/graphics/mesh.h"
#include "../../src/collision/scene.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy(void *out,const void *in,uint32_t n){
    uint32_t whole=n&~3u;for(uint32_t i=0;i<whole;i+=4)put(out,i,word(in,i));
    for(uint32_t i=whole;i<n;i++)((uint8_t *)out)[i]=((const uint8_t *)in)[i];
}
extern void *(*thug_mesh_crt_allocate_draft)(uint32_t);
/* Partial004d71f0: original shared-buffer clone branch used by LevelObject.
 * Deep vertex/index copies remain unavailable. Optional auxiliary triangles
 * and vertices are nevertheless independently copied even in shared mode. */
void *thug_mesh_clone_draft(const void *source,uint32_t shared,const ThugMemory *m){
    if(!(uint8_t)shared)__builtin_trap();
    void *mesh=m->allocate(m->context,216,1);if(mesh)thug_render_mesh_initialize(mesh);
    copy(mesh,source,216);put(mesh,0,word(mesh,0)|1);
    if(word(source,0xac)){
        put(mesh,0xb8,(uintptr_t)thug_mesh_crt_allocate_draft(word(source,0xb4)*6));
        copy(pointer(mesh,0xb8),pointer(source,0xb8),word(source,0xb4)*6);
        put(mesh,0xb0,(uintptr_t)thug_mesh_crt_allocate_draft(word(source,0xac)*12));
        copy(pointer(mesh,0xb0),pointer(source,0xb0),word(source,0xac)*12);
    }return mesh;
}
void *thug_model_scene_data_initialize_draft(void *);
void thug_model_scene_count_meshes_draft(void *,int32_t,void *const *);
void thug_model_scene_allocate_meshes_draft(void *,const ThugMemory *);
void thug_model_scene_fill_meshes_draft(void *,int32_t,void *const *);
void thug_model_scene_sort_meshes_draft(void *);
void thug_model_scene_data_bounds_draft(void *);
/* 004b4510,215bytes. The clone's private render list inherits geometry bounds. */
void *thug_geometry_scene_data_draft(void *geometry,const ThugMemory *m){
    void *header=m->allocate(m->context,132,1);if(header)thug_model_scene_data_initialize_draft(header);
    thug_model_scene_count_meshes_draft(header,word(geometry,0x40),pointer(geometry,0x3c));
    thug_model_scene_allocate_meshes_draft(header,m);
    thug_model_scene_fill_meshes_draft(header,word(geometry,0x40),pointer(geometry,0x3c));
    thug_model_scene_sort_meshes_draft(header);
    for(unsigned i=0;i<8;i++)put(header,0x44+i*4,word(geometry,0x14+i*4));
    thug_model_scene_data_bounds_draft(header);return header;
}
void *thug_model_geometry_construct_draft(void *);
void thug_render_set_enabled_draft(void *,uint32_t);
void *thug_model_render_instance_construct_draft(void *,void *,const float *,void *,void *);
/* Partial004b58c0: clone geometry into an independent render instance while
 * retaining shared mesh buffers. Scene-merging/deep-copy mode still traps. */
void *thug_geometry_clone_pc_draft(void *source,uint32_t shared,void *scene,const ThugMemory *m){
    (void)scene;if(!(uint8_t)shared)__builtin_trap();
    void *geometry=thug_allocate_zeroed(100,m);if(geometry)thug_model_geometry_construct_draft(geometry);
    put(geometry,0x3c,(uintptr_t)m->allocate(m->context,word(source,0x40)*4,1));put(geometry,0x40,word(source,0x40));
    for(uint32_t i=0;i<word(geometry,0x40);i++){
        void *mesh=thug_mesh_clone_draft(pointer(pointer(source,0x3c),i*4),shared,m);put(pointer(geometry,0x3c),i*4,(uintptr_t)mesh);
    }
    for(unsigned i=0;i<8;i++)put(geometry,0x14+i*4,word(source,0x14+i*4));
    void *header=thug_geometry_scene_data_draft(geometry,m);thug_render_set_enabled_draft(geometry,1);
    float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
    void *instance=m->allocate(m->context,100,1);if(instance)thug_model_render_instance_construct_draft(instance,header,identity,(void *)1,0);
    put(instance,0,word(instance,0)|1);put(geometry,0x4c,(uintptr_t)instance);return geometry;
}
/* 0048dd80. Wrapper retains inherited resource identity, then drops owned data.
 * Its PC clone callee is currently partial outside shared-buffer mode. */
void *thug_geometry_clone_draft(void *source,uint32_t shared,void *scene,const ThugMemory *m){
    typedef struct{uintptr_t unused[2];void *(*clone)(void *,uint32_t,void *,const ThugMemory *);} Methods;
    void *result=((const Methods *)pointer(source,0))->clone(source,shared,scene,m);
    if(result){put(result,4,((uint8_t)shared==0)+1);if(word(source,8))put(result,8,word(source,8));put(result,12,0);}return result;
}
uint8_t thug_model_geometry_flag16_draft(void *,uint32_t);
void thug_model_geometry_set_lights_draft(void *,void *);
void thug_model_part_insert_draft(void *,void *,void *const *,const ThugMemory *);
/* Partial004938e0: mandatory-allocation path (lowbyte third argument nonzero).
 * The optional allocation/failure policy is not part of this host adapter yet.
 * second argument is the stored part value, not the cloned geometry. */
uint8_t thug_renderer_append_geometry_draft(void *renderer,void *geometry,void *value,uint32_t required,const ThugMemory *m){
    ((uint8_t *)renderer)[0x44]&=0xfe;if(!(uint8_t)required)__builtin_trap();
    void *part=m->allocate(m->context,24,1);put(part,0,(uintptr_t)geometry);
    thug_model_geometry_flag16_draft(geometry,(((uint8_t *)renderer)[0x44]>>4)&1);put(part,8,(uintptr_t)value);
    put(renderer,0x18,word(renderer,0x18)|(1u<<(((uint8_t *)renderer)[0x46]&31)));put(part,4,0);
    if(word(renderer,0x2c))thug_model_geometry_set_lights_draft(pointer(part,0),pointer(renderer,0x2c));
    put(part,20,0);put(part,12,0);put(part,16,0);thug_model_part_insert_draft((uint8_t *)renderer+0x10,pointer(renderer,0x10),&part,m);
    uint16_t n;__builtin_memcpy(&n,(uint8_t *)renderer+0x46,2);n++;__builtin_memcpy((uint8_t *)renderer+0x46,&n,2);
    if(word(renderer,4)){
        typedef struct{uintptr_t unused[3];uint32_t (*set)(void *,uint32_t);} Methods;
        if((uint8_t)((const Methods *)pointer(renderer,0))->set(renderer,0))put(renderer,4,0);
    }
    __builtin_memcpy(&n,(uint8_t *)renderer+0x46,2);if(n==1)put(renderer,0x30,0x9facc1a5);return 1;
}
void *thug_model_sector_geometry_draft(const void *);
/* 0041ffa0: actual LevelObject path, including absent-sector/geometry no-ops.
 * Its clone and mandatory append use the recovered PC paths above. */
void thug_model_level_object_draft(void *component,uint32_t key,const ThugMemory *m){
    void *sector=thug_scenes_find_object(key);if(!sector)return;
    void *geometry=thug_model_sector_geometry_draft(sector);if(!geometry)return;
    void *clone=thug_geometry_clone_draft(geometry,1,0,m);thug_render_set_enabled_draft(clone,1);
    thug_renderer_append_geometry_draft(pointer(component,0x208),clone,0,1,m);((uint8_t *)component)[0x235]=1;
}
