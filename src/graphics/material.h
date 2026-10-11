#ifndef THUG_GRAPHICS_MATERIAL_H
#define THUG_GRAPHICS_MATERIAL_H
#include "decal.h"
typedef struct ThugMaterialNode ThugMaterialNode;
typedef struct {
    ThugMaterialNode *(*dispose)(ThugMaterialNode *, uint32_t, const ThugMemory *);
} ThugMaterialNodeMethods;
typedef struct { uint32_t list;ThugRenderMesh *mesh; } ThugMaterialEntry;
struct ThugMaterialNode {
    const ThugMaterialNodeMethods *methods;
    ThugMaterialEntry *value;
    uint32_t priority;
    ThugMaterialNode *previous,*next;
};
typedef struct {
    uint32_t flags;
    ThugRenderMaterial *material;
    ThugMaterialNode *lists[3];
} ThugMaterialGroup;
typedef struct { int32_t count;ThugMaterialGroup *groups[]; } ThugMaterialTable;
extern const ThugMaterialNodeMethods thug_material_node_methods,thug_material_sentinel_methods;
void thug_material_sentinel_destroy(ThugMaterialNode *);
ThugMaterialNode *thug_material_node_delete(ThugMaterialNode *,uint32_t,const ThugMemory *);
ThugMaterialNode *thug_material_sentinel_delete(ThugMaterialNode *,uint32_t,const ThugMemory *);
ThugMaterialGroup *thug_material_group_initialize(ThugMaterialGroup *,ThugRenderMaterial *,const ThugMemory *);
void thug_material_group_add_mesh(ThugMaterialGroup *,ThugRenderMesh *,const ThugMemory *);
void thug_material_group_remove_mesh(ThugMaterialGroup *,ThugRenderMesh *,const ThugMemory *);
ThugMaterialGroup *thug_material_table_find(const ThugMaterialTable *,const ThugRenderMaterial *);
int32_t thug_material_group_compare(const void *,const void *);
void thug_material_table_remove_mesh(ThugMaterialTable *,ThugRenderMesh *,const ThugMemory *);
#endif
