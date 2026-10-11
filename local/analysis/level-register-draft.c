#include "../../src/core/checksum.h"
#include "../../src/collision/scene.h"

/* Identity-only method tables. Registry destruction has not been recovered. */
const uint32_t thug_level_scene_node_methods_draft[1]={0};
const uint32_t thug_level_scene_sentinel_methods_draft[1]={0};
uint32_t thug_level_scene_sentinel_draft[5]; /* original006fa7e0 */
uint8_t thug_level_shared_vertices_draft; /* original00786ab6 */
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}

/* Original fixed sprintf format levels\\%s\\%s%s.scn.%s, empty variant and
 * platform suffix Xbx. Internal contract: resulting path fits128 bytes. */
static void scene_path(char out[128],const char *name){
    const char *parts[]={"levels\\",name,"\\",name,".scn.Xbx"};unsigned n=0;
    for(unsigned i=0;i<5;i++)for(const char *p=parts[i];*p;p++){if(n>=127)__builtin_trap();out[n++]=*p;}
    out[n]=0;
}
void thug_model_scene_name_finalize_draft(void *,const char *,void *,const ThugMemory *);
void *thug_model_scene_file_load_draft(const char *,void *,uint32_t,uint32_t,uint32_t,void *,const ThugMemory *);

/* 0048c560,225bytes. Initialized registry, successful allocation and valid
 * scene are original internal contracts. The main collision head represents
 * the original sentinel+12 alias; preserve that alias after each append. */
void thug_level_scene_register_draft(void *scene,const char *name,void *textures,uint32_t skip_finalize,void *aux,const ThugMemory *m){
    char path[128];scene_path(path,name);put(scene,0x84,thug_crc32_string(name));put(scene,0x88,(uintptr_t)textures);
    if(!(uint8_t)skip_finalize)thug_model_scene_name_finalize_draft(scene,path,aux,m);
    void *node=thug_allocate_zeroed(20,m);
    if(node){put(node,0,(uintptr_t)thug_level_scene_node_methods_draft);put(node,4,(uintptr_t)scene);put(node,8,0);put(node,12,(uintptr_t)node);put(node,16,(uintptr_t)node);}
    put(node,16,thug_level_scene_sentinel_draft[4]);put(node,12,(uintptr_t)thug_level_scene_sentinel_draft);
    put(pointer(thug_level_scene_sentinel_draft,16),12,(uintptr_t)node);thug_level_scene_sentinel_draft[4]=(uintptr_t)node;
    thug_collision_scene_list=(void *)(uintptr_t)thug_level_scene_sentinel_draft[3];
}

/* 0048ccb0,200bytes. File loader remains partial outside the actual training
 * scene format; its unsupported material layers/tail records still trap. */
void *thug_level_scene_load_draft(const char *name,void *textures,uint32_t a,uint32_t b,uint32_t c,uint32_t unused,const ThugMemory *m){
    (void)unused;char path[128];scene_path(path,name);uint32_t storage[4]={0};void *aux=thug_level_shared_vertices_draft?storage:0;
    void *scene=thug_model_scene_file_load_draft(path,textures,a,b,c,aux,m);
    thug_level_scene_register_draft(scene,name,textures,0,aux,m);return scene;
}
