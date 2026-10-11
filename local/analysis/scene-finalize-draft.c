#include "../../src/graphics/mesh.h"
#include "../../src/core/bounds.h"
#include "../../src/core/sort.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void copy(void *destination,const void *source,uint32_t n){
 uint8_t *d=destination;const uint8_t *s=source;uint32_t words=n&~3u;
 for(uint32_t i=0;i<words;i+=4)put(d,i,word(s,i));for(uint32_t i=words;i<n;i++)d[i]=s[i];
}
typedef struct {void *(*dispose)(void *,uint32_t,const ThugMemory *);} NodeMethods;
extern const NodeMethods thug_model_mesh_node_methods_draft,thug_model_mesh_list_methods_draft;
/* 004b5ec0: unlink only this node, retaining its value and priority. */
void thug_model_mesh_node_unlink_draft(void *p){
    void *previous=pointer(p,16);uint32_t next=word(p,12);put(p,0,(uintptr_t)&thug_model_mesh_node_methods_draft);
    put(previous,12,next);void *after=pointer(p,12);put(after,16,word(p,16));put(p,12,(uintptr_t)p);put(p,16,(uintptr_t)p);
}
/* 004b5e50 and004b5e90 differ only by the latter's out-of-line unlink call. */
void *thug_model_mesh_node_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_model_mesh_node_unlink_draft(p);if(flags&1)m->release(m->context,p);return p;
}
void *thug_model_mesh_sentinel_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_model_mesh_node_unlink_draft(p);if(flags&1)m->release(m->context,p);return p;
}
/* 004d3e50. Bind a deferred vertex buffer into a shared allocation. */
void thug_mesh_vertex_bind_shared_draft(void *mesh,void *aux){
    void *buffer=pointer(mesh,0xcc);if(word(buffer,8)){put(aux,4,word(aux,4));return;}
    put(buffer,8,word(aux,0));put(buffer,0x20,word(aux,4));
    copy((void *)(uintptr_t)(word(aux,12)+word(aux,4)),pointer(buffer,12),word(buffer,0));
    void *device=pointer(aux,0);typedef struct {uint32_t unused;uint32_t (*add_ref)(void *);} Methods;
    ((const Methods *)pointer(device,0))->add_ref(device);put(aux,4,word(aux,4)+((word(buffer,0)+31)&~31u));
}
/* 004b5360. Original list order becomes array order; deleting nodes must not
 * delete meshes. Existing arrays retain their old list/count without change. */
void thug_model_geometry_finish_meshes_draft(void *geometry,void *aux,const ThugMemory *m){
    if(word(geometry,0x3c))return;
    uint32_t count=0;void *node=pointer(pointer(geometry,0x38),12);
    while(word(node,4)!=0xffffffff&&node){node=pointer(node,12);count++;}
    put(geometry,0x40,count);
    if(count){
        put(geometry,0x3c,(uintptr_t)m->allocate(m->context,count*4,1));node=pointer(pointer(geometry,0x38),12);
        if(word(node,4)!=0xffffffff&&node){
            uint32_t offset=0;
            do{
                void *next=pointer(node,12);if(word(next,4)==0xffffffff)next=0;
                put(pointer(geometry,0x3c),offset,word(node,4));const NodeMethods *methods=pointer(node,0);methods->dispose(node,1,m);
                if(aux)thug_mesh_vertex_bind_shared_draft(pointer(pointer(geometry,0x3c),offset),aux);
                offset+=4;node=next;
            }while(node);
        }
    }
    node=pointer(geometry,0x38);if(node){const NodeMethods *methods=pointer(node,0);methods->dispose(node,1,m);}put(geometry,0x38,0);
}
/* 004dddf0 /004dde20: count, then fill the scene's mesh array. */
void thug_model_scene_count_meshes_draft(void *header,int32_t count,void *const *meshes){
    for(int32_t i=0;i<count;i++){
        put(header,0x20,word(header,0x20)+1);void *material=pointer(meshes[i],0x14);
        if(material&&(((uint8_t *)material)[0x20]&0x40))put(header,0x24,word(header,0x24)+1);
    }
}
void thug_model_scene_fill_meshes_draft(void *header,int32_t count,void *const *meshes){
    for(int32_t i=0;i<count;i++){
        void *mesh=meshes[i];uint32_t index=word(header,0x28);put(pointer(header,0x1c),index*4,(uintptr_t)mesh);put(header,0x28,word(header,0x28)+1);
    }
}
/* 004b44d0. Only the low byte selects the pass; return's public ABI is a byte. */
uint8_t thug_model_geometry_collect_meshes_draft(void *geometry,uint32_t count_only){
    void *header=pointer(pointer(geometry,0x34),0x280);int32_t count=word(geometry,0x40);void *const *meshes=pointer(geometry,0x3c);
    if((uint8_t)count_only)thug_model_scene_count_meshes_draft(header,count,meshes);else thug_model_scene_fill_meshes_draft(header,count,meshes);return 1;
}
/* 004de3e0. Nonpositive counts retain the previous array pointer. */
void thug_model_scene_allocate_meshes_draft(void *header,const ThugMemory *m){
    int32_t n=word(header,0x20);if(n>0)put(header,0x1c,(uintptr_t)m->allocate(m->context,(uint32_t)n*4,1));
}
/* 004ddd50,156bytes. Unordered priorities return minus one, just like an ordered lesser value.
 * The final ties use unsigned shader handles, then unsigned material addresses. */
int32_t thug_model_mesh_compare_draft(const void *a,const void *b){
    const void *left=pointer(a,0),*right=pointer(b,0),*x=pointer(left,0x14),*y=pointer(right,0x14);
    float px=number(x,0x1c),py=number(y,0x1c);
    if(px!=py)return px>py?1:-1;
    uint8_t ax=((const uint8_t *)x)[12],ay=((const uint8_t *)y)[12];if(ax!=ay)return ax?1:-1;
    if(x==y)return 0;
    uint8_t fx=((const uint8_t *)x)[0x20]&0x10,fy=((const uint8_t *)y)[0x20]&0x10;
    if(fx&&!fy)return 1;if(!fx&&fy)return -1;
    uint32_t sx=word(left,0x44),sy=word(right,0x44);
    return sy==sx?((uintptr_t)y<(uintptr_t)x?1:-1):(sy<sx?1:-1);
}
/* 004ddfa0. Reuse the recovered original CRT sort, including its tie ordering. */
void thug_model_scene_sort_meshes_draft(void *header){
    thug_crt_qsort(pointer(header,0x1c),word(header,0x20),4,thug_model_mesh_compare_draft);
    uint32_t count=word(header,0x20);put(header,0x24,0);put(header,0x2c,count);put(header,0x30,count);put(header,0x34,0);
    if((int32_t)count>0){
        void *const *meshes=pointer(header,0x1c);
        for(int32_t i=0;i<(int32_t)word(header,0x20);i++){
            void *material=pointer(meshes[i],0x14);
            if(material&&(((uint8_t *)material)[0x20]&0x40)){
                put(header,0x24,word(header,0x24)+1);if(i<(int32_t)word(header,0x2c))put(header,0x2c,i);
                material=pointer(meshes[i],0x14);
                if(((uint8_t *)material)[12]){put(header,0x34,word(header,0x34)+1);if(i<(int32_t)word(header,0x30))put(header,0x30,i);}
            }
        }
    }
}
/* 004a2ba0. */
void *thug_model_sector_geometry_draft(const void *sector){return pointer(sector,0x14);}
static void *next_sector(void *scene){
    ThugObjectLookupTable *t=pointer(scene,0xd0);if(!thug_object_table_next(t)||!t->iteration_node)return 0;return t->iteration_node->value;
}
static void reset_sectors(void *scene){void *t=pointer(scene,0xd0);put(t,12,0xffffffff);put(t,16,0);}
/* 004c6270. The optional shared vertex allocation is a real GPU boundary. */
void thug_model_scene_finalize_draft(void *scene,void *aux,const ThugMemory *m){
    reset_sectors(scene);void *sector=next_sector(scene);
    if(aux){
        typedef struct{uint32_t unused[26];uint32_t (*create)(void *,uint32_t,uint32_t,uint32_t,uint32_t,void **,uint32_t);} Device;
        typedef struct{uint32_t unused[11];uint32_t (*lock)(void *,uint32_t,uint32_t,void **,uint32_t);} Buffer;
        ((const Device *)thug_mesh_device->methods)->create(thug_mesh_device,word(aux,8),8,0,0,(void **)aux,0);
        void *device=pointer(aux,0);((const Buffer *)pointer(device,0))->lock(device,0,0,(void **)((uint8_t *)aux+12),0);
        put(aux,4,0);put(pointer(scene,0x280),0x7c,word(aux,0));put(pointer(scene,0x280),0x80,word(aux,8));
    }
    while(sector){void *g=thug_model_sector_geometry_draft(sector);thug_model_geometry_finish_meshes_draft(g,aux,m);thug_model_geometry_collect_meshes_draft(g,1);sector=next_sector(scene);}
    if(aux){typedef struct {uint32_t unused[12];uint32_t (*unlock)(void *);} Buffer;void *device=pointer(aux,0);((const Buffer *)pointer(device,0))->unlock(device);put(aux,12,0);}
    thug_model_scene_allocate_meshes_draft(pointer(scene,0x280),m);reset_sectors(scene);
    for(sector=next_sector(scene);sector;sector=next_sector(scene))thug_model_geometry_collect_meshes_draft(thug_model_sector_geometry_draft(sector),0);
    thug_model_scene_sort_meshes_draft(pointer(scene,0x280));
}
/* 0049c910. Copy the name bytewise, then call the scene's finalize virtual. */
void thug_model_scene_name_finalize_draft(void *scene,const char *name,void *aux,const ThugMemory *m){
    char *out=(char *)scene+4;do{*out++=*name;}while(*name++);
    typedef struct{uint32_t unused;void (*finalize)(void *,void *,const ThugMemory *);} Methods;
    ((const Methods *)pointer(scene,0))->finalize(scene,aux,m);
}
const uintptr_t thug_model_object_base_methods_draft[1]={0},thug_model_object_pc_methods_draft[1]={0};
/* 00490a60 /004b7b30. */
void *thug_model_object_base_construct_draft(void *p){
    put(p,0,(uintptr_t)thug_model_object_base_methods_draft);thug_bounds_reset((ThugBounds *)((uint8_t *)p+0x90));
    put(p,0xb0,0);put(p,0xb4,0);put(p,0xb8,0);((uint8_t *)p)[8]=0;return p;
}
void *thug_model_object_construct_draft(void *p){thug_model_object_base_construct_draft(p);put(p,0,(uintptr_t)thug_model_object_pc_methods_draft);return p;}
/* 004b7ed0, including the original reload of scene->header. */
void thug_model_object_bind_scene_draft(void *model,void *scene){
    put(model,0xc4,(uintptr_t)scene);put(model,0xb4,word(pointer(scene,0x280),0x74));put(model,0xb8,word(pointer(scene,0x280),0x78));
}
/* 004d3ce0 resets only the first BYTE, then five words. */
uint32_t thug_model_render_cache_draft[6];
void thug_model_render_cache_reset_draft(void){((uint8_t *)thug_model_render_cache_draft)[0]=0;for(unsigned i=1;i<6;i++)thug_model_render_cache_draft[i]=0;}
