#ifndef THUG_GRAPHICS_MESH_H
#define THUG_GRAPHICS_MESH_H
#include "material.h"
typedef struct ThugMeshComObject ThugMeshComObject;
typedef struct {uint32_t opaque[2];uint32_t (*release)(ThugMeshComObject *);} ThugMeshComMethods;
struct ThugMeshComObject {const ThugMeshComMethods *methods;};
typedef struct ThugMeshDevice ThugMeshDevice;
typedef struct {
    uint32_t opaque[100];
    uint32_t (*set_stream)(ThugMeshDevice *,uint32_t,ThugMeshComObject *,uint32_t,uint32_t);
    uint32_t (*get_stream)(ThugMeshDevice *,uint32_t,ThugMeshComObject **,uint32_t *,uint32_t *);
} ThugMeshDeviceMethods;
struct ThugMeshDevice {const ThugMeshDeviceMethods *methods;};
typedef struct ThugMeshResourceLink {
    void *value;
    struct ThugMeshResourceLink *previous,*next;
} ThugMeshResourceLink;
/* Host-owned CRT heap and GPU interfaces; the game heap stays separate.
 * The pointer lifts the original embedded material table at775b80 without
 * inventing its static capacity. The runtime supplies valid table storage. */
typedef struct {void *context;void (*release)(void *,void *);} ThugMeshCrtHeap;
extern ThugMeshCrtHeap thug_mesh_crt_heap;
extern ThugMaterialTable *thug_mesh_material_table;
extern ThugMeshDevice *thug_mesh_device;
extern ThugMeshResourceLink *thug_mesh_vertex_registry,*thug_mesh_index_registry;
void thug_mesh_unregister_vertex(void *buffer);
void thug_mesh_destroy(ThugRenderMesh *,const ThugMemory *);
#endif
