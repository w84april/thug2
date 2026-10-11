#include "mesh.h"
#include <stddef.h>
ThugMeshCrtHeap thug_mesh_crt_heap;
ThugMaterialTable *thug_mesh_material_table;
ThugMeshDevice *thug_mesh_device;
ThugMeshResourceLink *thug_mesh_vertex_registry,*thug_mesh_index_registry;
_Static_assert(offsetof(ThugMeshDeviceMethods,set_stream)==0x190,"Stream setter slot");
_Static_assert(offsetof(ThugMeshDeviceMethods,get_stream)==0x194,"Stream getter slot");
static uint32_t word(const void *p) {uint32_t n;__builtin_memcpy(&n,p,4);return n;}
static void store(void *p,uint32_t n) {__builtin_memcpy(p,&n,4);}
static void *pointer(const void *p) {return (void *)(uintptr_t)word(p);}
static void crt_release(void *p) {thug_mesh_crt_heap.release(thug_mesh_crt_heap.context,p);}
static void com_release(ThugMeshComObject *p) {p->methods->release(p);}
static void zero(void *p,uint32_t bytes) {
    for(uint32_t i=0;i<bytes;i+=4)store((uint8_t *)p+i,0);
}
static void unregister(ThugMeshResourceLink **head,ThugMeshResourceLink *link,void *value) {
    while(link && link->value!=value)link=link->next;
    if(!link)return;
    if(link->previous)link->previous->next=link->next;else *head=link->next;
    if(link->next)link->next->previous=link->previous;
    zero(link,12);crt_release(link);
}
/* 0x004d3be0. Remove only the first matching registration, zero then CRT free. */
void thug_mesh_unregister_vertex(void *buffer) {
    unregister(&thug_mesh_vertex_registry,thug_mesh_vertex_registry,buffer);
}
static void destroy_vertex(uint8_t *buffer) {
    com_release(pointer(buffer+8));store(buffer+8,0);
    thug_mesh_unregister_vertex(buffer);
    if(word(buffer+8))com_release(pointer(buffer+8));
    if(word(buffer+12))crt_release(pointer(buffer+12));
    zero(buffer,36);crt_release(buffer);
}
/* 0x004d69e0. Complete destructor, including concrete material-list removal.
 * GetStreamSource must supply its three outputs, as required by this original
 * caller. Captured output can be changed by callbacks and is reloaded later. */
void thug_mesh_destroy(ThugRenderMesh *mesh,const ThugMemory *memory) {
    uint8_t *b=(uint8_t *)mesh;
    if(word(b)&0x10)thug_material_table_remove_mesh(thug_mesh_material_table,mesh,memory);
    if(word(b+0x90))memory->release(memory->context,pointer(b+0x90));
    if(!(word(b)&1)) {
        for(uint32_t i=0;i<8;++i) {
            uint8_t *buffer=pointer(b+0x54+i*4);
            if(buffer) {
                com_release(pointer(buffer+12));
                ThugMeshResourceLink *head=thug_mesh_index_registry;
                store(buffer+12,0);unregister(&thug_mesh_index_registry,head,buffer);
                if(word(buffer+12))com_release(pointer(buffer+12));
                if(word(buffer+16))crt_release(pointer(buffer+16));
                zero(buffer,24);crt_release(buffer);
            }
            store(b+0x54+i*4,0);
        }
        static const uint8_t offsets[]={0x8c,0x48,0x4c};
        for(uint32_t i=0;i<3;++i) {
            uint8_t *slot=b+offsets[i];
            if(word(slot)) {memory->release(memory->context,pointer(slot));store(slot,0);}
        }
        crt_release(pointer(b+0x94));
        ThugMeshComObject *captured;uint32_t offset,stride;
        thug_mesh_device->methods->get_stream(thug_mesh_device,0,&captured,&offset,&stride);
        if(captured)com_release(captured);
        for(uint32_t i=0;i<b[0x1a];++i) {
            uint8_t *slot=b+0xcc+i*4,*buffer=pointer(slot);
            if(buffer) {
                if(pointer(buffer+8)==captured)
                    thug_mesh_device->methods->set_stream(thug_mesh_device,0,NULL,0,0);
                destroy_vertex(pointer(slot));store(slot,0);
            }
            slot=b+0xbc+i*4;buffer=pointer(slot);
            if(buffer) {
                if(pointer(buffer+8)==captured)
                    thug_mesh_device->methods->set_stream(thug_mesh_device,0,NULL,0,0);
                /* The secondary slot stays observable until the final clear. */
                destroy_vertex(pointer(slot));
            }
        }
        if(word(b+0xc8)) {destroy_vertex(pointer(b+0xc8));store(b+0xc8,0);}
    }
    if(word(b+0xb8))crt_release(pointer(b+0xb8));
    if(word(b+0xb0))crt_release(pointer(b+0xb0));
    zero(mesh,0xd8);
}
