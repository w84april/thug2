#include "../../src/collision/load.h"
#include "../../src/core/number.h"
#include <stddef.h>

/* 0x0049cbb0. Allocation/heap setup and C++ exception machinery are replaced
 * by the platform memory adapter. Retains the four-byte array-count prefix. */
uint8_t thug_collision_load(uint32_t receiver, void *data, int32_t *count,
    ThugStaticCollisionInstance **instances, ThugCollisionObject **objects,
    ThugBounds *bounds, uint32_t unused, const ThugMemory *memory) {
    (void)unused;
    const uint32_t *header = data;
    *count = (int32_t)header[1];
    *objects = (ThugCollisionObject *)((uint8_t *)data + 32);
    uintptr_t vertices = ((uintptr_t)*objects + header[1] * 64u + 15u) & ~15u;
    uintptr_t vertex_aux = vertices + (header[6] + header[5] * 2u) * 6u;
    uintptr_t faces = (vertex_aux + header[2] + 3u) & ~3u;
    uint32_t face_bytes = header[3] * 10u + header[4] * 8u;
    uintptr_t node_size_at = faces + ((header[3] + face_bytes + 3u) & ~3u);
    uintptr_t nodes = node_size_at + 4u;
    uintptr_t face_list = nodes + *(const uint32_t *)node_size_at;
    const uint8_t *radii = (const uint8_t *)(faces + face_bytes);
    uint32_t *allocation = memory->allocate(memory->context, header[1] * 24u + 4u, 1);
    ThugStaticCollisionInstance *array = NULL;
    if (allocation) {
        *allocation = header[1];
        array = (ThugStaticCollisionInstance *)(allocation + 1);
        for (uint32_t i = 0; i < header[1]; ++i) thug_static_collision_initialize(&array[i]);
    }
    *instances = array;
    uint8_t any_faces = 0;
    for (int32_t i = 0; i < (int32_t)header[1]; ++i) {
        ThugCollisionObject *object = &(*objects)[i];
        thug_collision_bind(object, receiver, (void *)vertices, (void *)vertex_aux,
            (void *)faces, (void *)nodes, (void *)face_list);
        thug_collision_has_tree(object);
        array[i].base.methods->set_geometry(&array[i].base, object);
        radii = thug_collision_bind_radii(&array[i], radii, object);
        if (object->face_count) {
            thug_bounds_expand(bounds, object->bounds.min);
            thug_bounds_expand(bounds, object->bounds.max);
            any_faces = 1;
        }
    }
    if (!any_faces) {
        const float lower[4] = { -100, -100, -100, 1 }, upper[4] = { 100, 100, 100, 1 };
        thug_bounds_expand(bounds, lower);
        thug_bounds_expand(bounds, upper);
    }
    return 1;
}

/* 0x004183b0. */
ThugCollisionCell *thug_collision_cell_initialize(ThugCollisionCell *cell) {
    thug_bounds_reset(&cell->bounds);
    cell->unknown_20 = 0;
    cell->count = 0;
    cell->unknown_28 = 0;
    cell->objects = NULL;
    return cell;
}

/* 0x00418440: repeated additions preserve the PC's cell-boundary rounding. */
void thug_collision_grid_initialize(ThugCollisionGrid *grid, const ThugBounds *bounds) {
    grid->bounds = *bounds;
    grid->cell_width = (bounds->max[0] - bounds->min[0]) * 0.05f;
    grid->cell_depth = (bounds->max[2] - bounds->min[2]) * 0.05f;
    float x = bounds->min[0];
    for (unsigned column = 0; column < 20; ++column) {
        float z = bounds->min[2];
        for (unsigned row = 0; row < 20; ++row) {
            ThugBounds *cell = &grid->cells[column * 20 + row].bounds;
            cell->min[0] = x; cell->min[1] = -1.0e12f; cell->min[2] = z; cell->min[3] = 0;
            cell->max[0] = x + grid->cell_width; cell->max[1] = 1.0e12f;
            cell->max[2] = z + grid->cell_depth; cell->max[3] = 0;
            z += grid->cell_depth;
        }
        x += grid->cell_width;
    }
    grid->columns = grid->rows = 20;
}

/* Both passes in 0x00418bd0 use this arithmetic. Only the upper indices are
 * capped: the original requires object bounds to lie inside the grid bounds. */
static void object_cells(const ThugCollisionGrid *grid, const ThugCollisionInstance *object,
    int32_t *x0, int32_t *x1, int32_t *z0, int32_t *z1) {
    const ThugBounds *b = object->methods->bounds(object);
    float inv_x = 1.0f / grid->cell_width, inv_z = 1.0f / grid->cell_depth;
    *x0 = (int32_t)thug_truncate_low_word((b->min[0] - grid->bounds.min[0]) * inv_x);
    *x1 = (int32_t)thug_truncate_low_word((b->max[0] - grid->bounds.min[0]) * inv_x);
    *z0 = (int32_t)thug_truncate_low_word((b->min[2] - grid->bounds.min[2]) * inv_z);
    *z1 = (int32_t)thug_truncate_low_word((b->max[2] - grid->bounds.min[2]) * inv_z);
    if (*x1 >= 20) *x1 = 19;
    if (*z1 >= 20) *z1 = 19;
}

/* 0x00418bd0. Use freshly initialized cells. Preserve allocation order,
 * object order, the two passes, and the temporary array's lifetime. */
void thug_collision_grid_populate(ThugCollisionGrid *grid, ThugStaticCollisionInstance *objects,
    int32_t count, const ThugMemory *memory) {
    for (int32_t i = 0; i < count; ++i) {
        if (!objects[i].base.geometry->face_count) continue;
        int32_t x0, x1, z0, z1;
        object_cells(grid, &objects[i].base, &x0, &x1, &z0, &z1);
        for (int32_t x = x0; x <= x1; ++x)
            for (int32_t z = z0; z <= z1; ++z) ++grid->cells[x * 20 + z].count;
    }
    for (unsigned i = 0; i < 400; ++i) {
        ThugCollisionCell *cell = &grid->cells[i];
        if (cell->count > 0) cell->objects = memory->allocate(memory->context, (uint32_t)cell->count * 4u, 0);
    }
    memory->temp_scope(memory->context, 2);
    uint32_t *offsets = memory->allocate(memory->context, 400u * 4u, 1);
    for (unsigned i = 0; i < 400; ++i) offsets[i] = 0;
    memory->temp_scope(memory->context, 0);
    for (int32_t i = 0; i < count; ++i) {
        if (!objects[i].base.geometry->face_count) continue;
        int32_t x0, x1, z0, z1;
        object_cells(grid, &objects[i].base, &x0, &x1, &z0, &z1);
        for (int32_t x = x0; x <= x1; ++x) {
            for (int32_t z = z0; z <= z1; ++z) {
                unsigned cell = (unsigned)(x * 20 + z);
                grid->cells[cell].objects[offsets[cell]++] = &objects[i].base;
            }
        }
    }
    memory->release(memory->context, offsets);
}
