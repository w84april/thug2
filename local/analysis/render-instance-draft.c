#include "../../src/core/memory.h"
#include "../../src/core/matrix.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
void *thug_model_render_instances_draft; /* original7825c0 */
/* 00492e50. */
void *thug_model_renderer_skeleton_draft(const void *renderer){return pointer(renderer,12);}
/* 004d1030. Copy the matrix before any fields/global changes. The mesh count is
 * captured once, and the scan exits at the first ineligible mesh. */
void *thug_model_render_instance_construct_draft(void *instance,void *header,const float *matrix,void *matrices,void *bones){
    thug_matrix_copy((float *)((uint8_t *)instance+4),matrix);
    put(instance,0x44,(uintptr_t)bones);put(instance,0x48,(uintptr_t)matrices);put(instance,0x58,(uintptr_t)header);
    put(instance,0x54,0);((uint8_t *)instance)[0x4c]=1;put(instance,0,0);
    put(instance,0x5c,(uintptr_t)thug_model_render_instances_draft);thug_model_render_instances_draft=instance;put(instance,0x60,0xffffffff);
    if(!bones||(int32_t)word(pointer(instance,0x58),0x78)>0){
        int32_t count=word(header,0x20);
        if(count>0){
            void *const *meshes=pointer(header,0x1c);
            for(int32_t i=0;i<count;i++)if(!(((uint8_t *)meshes[i])[0x38]&0x10)||(word(meshes[i],0)&0x20000))return instance;
        }
        put(instance,0,word(instance,0)|2);
    }
    return instance;
}
/* 004b54b0. A successful initialized game heap is the original contract;
 * its failed allocation subsequently dereferences NULL. Third argument unused. */
uint8_t thug_model_geometry_load_instance_draft(void *geometry,void *model,void *renderer,uint32_t skin,const ThugMemory *m){
    (void)skin;void *matrices=pointer(renderer,8);put(geometry,0x50,(uintptr_t)model);
    float identity[16]={1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1};
    void *instance=m->allocate(m->context,100,1);
    if(instance){void *header=pointer(pointer(model,0xc4),0x280);instance=thug_model_render_instance_construct_draft(instance,header,identity,matrices,thug_model_renderer_skeleton_draft(renderer));}
    put(geometry,0x4c,(uintptr_t)instance);put(instance,0x54,(uintptr_t)renderer);return 1;
}
/* 0048ddf0. Capture the virtual table before modifying the receiver. */
uint8_t thug_model_geometry_bind_draft(void *geometry,void *model,void *renderer,uint32_t skin,const ThugMemory *m){
    typedef struct{uintptr_t unused[3];uint8_t (*load)(void *,void *,void *,uint32_t,const ThugMemory *);} Methods;
    const Methods *methods=pointer(geometry,0);put(geometry,4,1);((uint8_t *)geometry)[0x10]=skin;
    return methods->load(geometry,model,renderer,skin,m);
}
/* 0049f3b0. Actual PC slot80 is the already recovered shared5bc7f0. */
uint8_t thug_model_geometry_flag16_draft(void *geometry,uint32_t flag){
    typedef struct{uintptr_t unused[32];uint32_t (*flag)(void *,uint32_t);} Methods;
    return ((const Methods *)pointer(geometry,0))->flag(geometry,flag);
}
/* 004964a0. Insert before the provided list node; keep its value untouched.
 * NULL allocation is outside the successful-heap contract (original crashes). */
void thug_model_part_insert_draft(void *list,void *before,void *const *part,const ThugMemory *m){
    void *node=m->allocate(m->context,12,1);uint32_t previous=word(before,8),value=(uintptr_t)*part;
    put(node,0,value);put(node,8,previous);put(node,4,(uintptr_t)before);put(list,4,word(list,4)+1);
    put(before,8,(uintptr_t)node);put(pointer(node,8),4,(uintptr_t)node);
}
