#ifndef THUG_COLLISION_TREE_H
#define THUG_COLLISION_TREE_H
#include <stdint.h>
#include "../core/bounds.h"

/* These layouts retain the original PC's 32-bit pointers. Build with wasm32. */
typedef struct {
    uint32_t word;       /* axis in low 2 bits; signed fixed-point split above */
    uint32_t link;       /* tagged child-pair pointer, or uint16_t face list */
} ThugBspNode;

typedef struct {
    uint32_t checksum;
    uint16_t flags, vertex_count, face_count;
    uint8_t small_faces, small_vertices;
    void *faces;
    ThugBounds bounds;
    void *vertices;
    ThugBspNode *tree;
    uint8_t *vertex_aux;
    float face_radius_scale;
} ThugCollisionObject;

/* Original globals 0x00691968/6c/70, lifted into an explicit query context. */
typedef struct {
    uint16_t *output;
    int32_t count;
    uint32_t unknown;
} ThugCollisionQuery;

extern uint16_t thug_collision_fallback_indices[2048];
uint8_t thug_bsp_relocate(ThugBspNode *node, void *node_base, void *face_base);
uint8_t thug_collision_bind(ThugCollisionObject *object, uint32_t unused,
    void *vertices, void *vertex_aux, void *faces, void *nodes, void *face_list);
uint8_t thug_collision_has_tree(const ThugCollisionObject *object);
void thug_bsp_collect(const ThugCollisionObject *object, ThugBspNode *node,
    const ThugBounds *query, ThugCollisionQuery *state);
uint16_t *thug_collision_query(const ThugCollisionObject *object,
    const ThugBounds *query, uint32_t *count, uint16_t *output,
    uint32_t unknown, ThugCollisionQuery *state);
#endif
