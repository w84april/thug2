/* Behavioral recovery from the executable pinned in tools/specimen.py.
 * Names/types are analyst-assigned. Requires validated buffers and trees, like
 * the original internal routines. Not a parser for arbitrary external input.
 */
#include "tree.h"
#include <stddef.h>

_Static_assert(sizeof(void *) == 4, "Collision data uses 32-bit pointers: build wasm32");
_Static_assert(sizeof(ThugBspNode) == 8, "BSP node layout");
_Static_assert(sizeof(ThugCollisionObject) == 64, "Collision object layout");
_Static_assert(offsetof(ThugCollisionObject, tree) == 0x34, "Tree field offset");

/* 0x0067c6b8: initialized lazily by the recovered 0x00414d30 helper. */
uint16_t thug_collision_fallback_indices[2048] = { UINT16_MAX };

static ThugBspNode *child(const ThugBspNode *node, unsigned right) {
    uintptr_t address = node->link & ~3u;
    if (((node->link & 1u) != 0) != (right != 0)) address += 8;
    return (ThugBspNode *)address;
}

/* 0x00416000: both children occupy an adjacent pair; bit 0 swaps their order. */
uint8_t thug_bsp_relocate(ThugBspNode *node, void *node_base, void *face_base) {
    if ((node->word & 3u) == 3u) {
        node->link = (uintptr_t)face_base + node->link * 2u;
    } else {
        node->link = ((node->link & ~3u) + (uintptr_t)node_base) | (node->link & 3u);
        thug_bsp_relocate(child(node, 0), node_base, face_base);
        thug_bsp_relocate(child(node, 1), node_base, face_base);
    }
    return 1;
}

/* 0x004169c0: turn the four object-relative data offsets into pointers. */
uint8_t thug_collision_bind(ThugCollisionObject *object, uint32_t unused,
    void *vertices, void *vertex_aux, void *faces, void *nodes, void *face_list) {
    (void)unused;
    object->vertex_aux = (void *)((uintptr_t)object->vertex_aux + (uintptr_t)vertex_aux);
    object->faces = (void *)((uintptr_t)object->faces + (uintptr_t)faces);
    object->tree = (void *)((uintptr_t)object->tree + (uintptr_t)nodes);
    object->vertices = (void *)((uintptr_t)object->vertices + (uintptr_t)vertices);
    thug_bsp_relocate(object->tree, nodes, face_list);
    return 1;
}

/* 0x00414d30: this helper also prepares the fallback list for later queries. */
uint8_t thug_collision_has_tree(const ThugCollisionObject *object) {
    if (thug_collision_fallback_indices[0] != 0) {
        unsigned i;
        for (i = 0; i < 2048; ++i) thug_collision_fallback_indices[i] = (uint16_t)i;
    }
    return object->tree != NULL;
}

/* 0x004160e0: collect leaf face indices, retaining order and duplicates. */
void thug_bsp_collect(const ThugCollisionObject *object, ThugBspNode *node,
    const ThugBounds *query, ThugCollisionQuery *state) {
    while ((node->word & 3u) != 3u) {
        unsigned axis = node->word & 3u;
        float split = (float)((int32_t)node->word >> 2) * 0.0625f;
        if (query->min[axis] < split)
            thug_bsp_collect(object, child(node, 0), query, state);
        /* The x87 comparison excludes NaNs, too; !(max < split) would differ. */
        if (!(query->max[axis] >= split) || state->count < 0) return;
        node = child(node, 1);
    }
    {
        uint32_t count = node->word >> 16, i;
        uint16_t *source = (uint16_t *)(uintptr_t)node->link;
        uint16_t *destination = state->output + state->count;
        state->count += (int32_t)count;
        if (state->count > object->face_count) {
            state->count = -1;
            return;
        }
        for (i = 0; i < count; ++i) destination[i] = source[i];
    }
}

/* 0x00416320: overflowing candidate lists fall back to every face in the object.
 * The caller's output buffer must hold at least object->face_count indices. */
uint16_t *thug_collision_query(const ThugCollisionObject *object,
    const ThugBounds *query, uint32_t *count, uint16_t *output,
    uint32_t unknown, ThugCollisionQuery *state) {
    uint16_t *result;
    if (!object->tree) {
        *count = object->face_count;
        return thug_collision_fallback_indices;
    }
    state->output = output;
    state->unknown = unknown;
    state->count = 0;
    thug_bsp_collect(object, object->tree, query, state);
    if (state->count < 0) {
        *count = object->face_count;
        result = thug_collision_fallback_indices;
    } else {
        *count = (uint32_t)state->count;
        result = state->output;
    }
    state->output = NULL;
    state->unknown = 0;
    return result;
}
