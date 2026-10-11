#include "material.h"
#include "../core/sort.h"
#include <stddef.h>
_Static_assert(sizeof(ThugMaterialNode)==20,"Material list node");
_Static_assert(sizeof(ThugMaterialGroup)==20,"Material group");
const ThugMaterialNodeMethods thug_material_node_methods={thug_material_node_delete};
const ThugMaterialNodeMethods thug_material_sentinel_methods={thug_material_sentinel_delete};
static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4);return v;}
static void unlink_node(ThugMaterialNode *node) {
    node->methods=&thug_material_node_methods;
    node->next->previous=node->previous;
    node->previous->next=node->next;
    node->previous=node;node->next=node;
}
/* 004ce960 / 004ce9d0 / 004ce9a0. Sentinel destruction unlinks only itself;
 * it does not recursively destroy entries or own their payloads. */
ThugMaterialNode *thug_material_node_delete(ThugMaterialNode *node,uint32_t flags,const ThugMemory *memory) {
    unlink_node(node);if (flags&1) memory->release(memory->context,node);return node;
}
void thug_material_sentinel_destroy(ThugMaterialNode *node) {unlink_node(node);}
ThugMaterialNode *thug_material_sentinel_delete(ThugMaterialNode *node,uint32_t flags,const ThugMemory *memory) {
    thug_material_sentinel_destroy(node);if (flags&1) memory->release(memory->context,node);return node;
}
/* 004ceb30. Preserve the three separate zero-allocation calls. */
ThugMaterialGroup *thug_material_group_initialize(ThugMaterialGroup *group,ThugRenderMaterial *material,const ThugMemory *memory) {
    group->material=material;
    for (uint32_t i=0;i<3;++i) {
        ThugMaterialNode *node=thug_allocate_zeroed(20,memory);
        if (node) {
            node->value=(ThugMaterialEntry *)(uintptr_t)UINT32_MAX;node->priority=0;
            node->previous=node;node->next=node;node->methods=&thug_material_sentinel_methods;
        }
        group->lists[i]=node;
    }
    group->flags=0x40;group->flags=(word(material->storage+8)+2)<<5;return group;
}
/* 004ce1d0. Host memory is already initialized; PC memory-manager startup is
 * not recovered. Like the original, this path requires successful allocation
 * and a valid list selector obtained through mesh+4c. */
void thug_material_group_add_mesh(ThugMaterialGroup *group,ThugRenderMesh *mesh,const ThugMemory *memory) {
    ThugMaterialEntry *value=memory->allocate(memory->context,8,1);
    value->mesh=mesh;value->list=word((const void *)(uintptr_t)word((const uint8_t *)mesh+0x4c));
    ThugMaterialNode *node=thug_allocate_zeroed(20,memory);
    node->methods=&thug_material_node_methods;node->value=value;node->priority=0;node->previous=node;node->next=node;
    ThugMaterialNode *sentinel=group->lists[value->list];
    node->next=sentinel->next;node->previous=sentinel;
    sentinel->next->previous=node;sentinel->next=node;
}
/* 004ce250. Reverse traversal; release only the first matching entry. */
void thug_material_group_remove_mesh(ThugMaterialGroup *group,ThugRenderMesh *mesh,const ThugMemory *memory) {
    for (uint32_t i=0;i<3;++i) {
        ThugMaterialNode *node=group->lists[i]->previous;
        if ((uintptr_t)node->value==UINT32_MAX) continue;
        while (node) {
            ThugMaterialNode *next=node->previous;
            if ((uintptr_t)next->value==UINT32_MAX) next=NULL;
            ThugMaterialEntry *value=node->value;
            if (value->mesh==mesh) {
                node->methods->dispose(node,1,memory);memory->release(memory->context,value);return;
            }
            node=next;
        }
    }
}
/* 004cda60. All entries within the signed count must be valid groups. */
ThugMaterialGroup *thug_material_table_find(const ThugMaterialTable *table,const ThugRenderMaterial *material) {
    for (int32_t i=0;i<table->count;++i) if (table->groups[i]->material==material) return table->groups[i];
    return NULL;
}
/* 004cd9d0. Null groups sort last; missing materials have priority zero.
 * Unordered priorities compare equal, matching both original ordered tests. */
int32_t thug_material_group_compare(const void *a,const void *b) {
    ThugMaterialGroup *left,*right;__builtin_memcpy(&left,a,4);__builtin_memcpy(&right,b,4);
    if (!left) return right!=NULL;
    if (!right) return -1;
    float x=0,y=0;
    if (left->material) __builtin_memcpy(&x,left->material->storage+0x1c,4);
    if (right->material) __builtin_memcpy(&y,right->material->storage+0x1c,4);
    return x<y?-1:x>y?1:0;
}
/* 004ce9f0. Remove an empty group, compact it using the recovered CRT sort,
 * then decrement the live count. Other groups may reorder on equal keys. */
void thug_material_table_remove_mesh(ThugMaterialTable *table,ThugRenderMesh *mesh,const ThugMemory *memory) {
    ThugRenderMaterial *material=(ThugRenderMaterial *)(uintptr_t)word((uint8_t *)mesh+0x14);
    if (!material) return;
    ThugMaterialGroup *group=thug_material_table_find(table,material);
    if (!group) return;
    thug_material_group_remove_mesh(group,mesh,memory);
    for (uint32_t i=0;i<3;++i) if (group->lists[i]->next!=group->lists[i]) return;
    for (int32_t i=0;i<table->count;++i) {
        if (table->groups[i]!=group) continue;
        for (uint32_t j=0;j<3;++j) {
            ThugMaterialNode *node=group->lists[j];if (node) node->methods->dispose(node,1,memory);
        }
        memory->release(memory->context,group);table->groups[i]=NULL;break;
    }
    thug_crt_qsort(table->groups,(uint32_t)table->count,4,thug_material_group_compare);
    table->count=(int32_t)((uint32_t)table->count-1);
}
