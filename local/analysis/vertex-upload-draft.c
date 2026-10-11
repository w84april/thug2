#include "../../src/graphics/mesh.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy(void *destination,const void *source,uint32_t bytes){
    uint8_t *d=destination;const uint8_t *s=source;uint32_t n=bytes&~3u;
    for(uint32_t i=0;i<n;i+=4)put(d,i,word(s,i));for(uint32_t i=n;i<bytes;i++)d[i]=s[i];
}
extern void *(*thug_mesh_crt_allocate_draft)(uint32_t);
static void *crt_allocate(uint32_t size){if(!thug_mesh_crt_allocate_draft)__builtin_trap();return thug_mesh_crt_allocate_draft(size);}
typedef struct {uint32_t unused[26];uint32_t (*create)(void *,uint32_t,uint32_t,uint32_t,uint32_t,void **,uint32_t);} VertexDeviceMethods;
typedef struct {uint32_t unused[11];int32_t (*lock)(void *,uint32_t,uint32_t,void **,uint32_t);uint32_t (*unlock)(void *);} VertexMethods;
/* 004d3ff0. GPU status is ignored; flags independently suppress GPU and CPU
 * allocation. Pending lock offset/size are retained. Registry allocation must
 * succeed, as required by the original constructor. */
void *thug_mesh_vertex_buffer_construct_draft(void *p,uint32_t size,uint32_t usage,uint32_t flags){
    put(p,8,0);
    if(!(flags&4)){
        const VertexDeviceMethods *methods=(const void *)thug_mesh_device->methods;
        methods->create(thug_mesh_device,size,usage,0,0,(void **)((uint8_t *)p+8),0);
    }
    put(p,0,size);put(p,4,usage);put(p,12,(uintptr_t)((flags&1)?0:crt_allocate(size)));
    put(p,0x1c,flags);put(p,0x20,0);put(p,0x18,0xffffffff);
    ThugMeshResourceLink *link=crt_allocate(12),*head=thug_mesh_vertex_registry;
    link->value=p;link->next=head;link->previous=0;thug_mesh_vertex_registry=link;
    if(head)head->previous=link;return p;
}
/* 004d5760. The outer allocation may fail without constructing anything. */
void *thug_mesh_vertex_buffer_create_draft(uint32_t size,uint32_t usage,uint32_t flags){
    void *p=crt_allocate(36);return p?thug_mesh_vertex_buffer_construct_draft(p,size,usage,flags):0;
}
/* 004d40e0. The source starts at CPU byte zero, even for a nonzero lock offset.
 * The direct-GPU branch returns Unlock's HRESULT; other branches return zero. */
uint32_t thug_mesh_vertex_buffer_upload_draft(void *p){
    if((word(p,0x1c)&4)&&!word(p,8)){put(p,0x18,0xffffffff);return 0;}
    if(!(word(p,0x18)&0x10)){
        if(word(p,0x18)&0x2000){
            put(p,0x18,0xffffffff);void *device=pointer(p,8);const VertexMethods *methods=pointer(device,0);return methods->unlock(device);
        }
        if(word(p,0x1c)&4)put(p,0x10,word(p,0x10)+word(p,0x20));
        void *device=pointer(p,8),*out;const VertexMethods *methods=pointer(device,0);
        if(methods->lock(device,word(p,0x10),word(p,0x14),&out,word(p,0x18))>=0){
            copy(out,pointer(p,12),word(p,0x14));device=pointer(p,8);methods=pointer(device,0);methods->unlock(device);
        }
    }
    put(p,0x18,0xffffffff);return 0;
}
/* 004d5c30. An auxiliary owner defers GPU creation and accumulates a 32-byte
 * aligned size; CPU storage and registry insertion still occur. */
void thug_mesh_vertex_load_draft(void *mesh,const void *data,uint32_t size,void *aux){
    if(aux)put(mesh,0x78,word(mesh,0x78)|4);
    put(mesh,0xcc,(uintptr_t)thug_mesh_vertex_buffer_create_draft(size,word(mesh,0x74),word(mesh,0x78)));
    if(aux)put(aux,8,word(aux,8)+((size+31)&~31u));
    void *buffer=pointer(mesh,0xcc),*cpu=pointer(buffer,12);uint32_t bytes=word(buffer,0);
    put(buffer,0x10,0);put(buffer,0x14,bytes);put(buffer,0x18,0);copy(cpu,data,size);
    thug_mesh_vertex_buffer_upload_draft(pointer(mesh,0xcc));
}
/* Original shader handles7ca920..7ca964; runtime initialization is separate. */
uint32_t thug_mesh_shader_handles_draft[18];
uint32_t thug_mesh_shader_code_draft(uint32_t code){
    if(code<=1)return 0;
    if(code<=18)return thug_mesh_shader_handles_draft[code<=8?19-code:18-code];
    return code;
}
/* 004da710. This PC routine only advances over the serialized shader record. */
uint32_t thug_mesh_shader_skip_draft(const uint8_t **cursor){
    const uint8_t *p=*cursor;*cursor=(const uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)p+word(p,4)+8);return 0;
}
