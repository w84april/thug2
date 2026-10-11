/* Recovered static scene queries, following the original mutable query state.
 * Input lists, cache sizes and grid contents must satisfy engine invariants;
 * this is not an external-data parser.
 */
#include "scene.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>

_Static_assert(sizeof(ThugCollisionCell) == 0x30, "Grid cell layout");
_Static_assert(offsetof(ThugCollisionGrid, cells) == 0x30, "Grid header layout");
_Static_assert(offsetof(ThugCollisionScene, collision) == 0xd4, "Scene collision pointer");
_Static_assert(offsetof(ThugCollisionCache, static_count) == 0xfc4, "Cache count offset");
_Static_assert(offsetof(ThugCollisionMethods, segment) == 0x38, "Segment virtual method");

ThugCollisionSceneNode *thug_collision_scene_list;          /* 0x006fa7ec */
ThugCollisionScene *thug_collision_selected_scenes[16];     /* 0x006fa738 */
ThugCollisionGrid *thug_collision_selected_grids[16];       /* 0x006fa778 */
ThugCollisionInstance *thug_collision_grid_output[2048];    /* 0x00691998 */
uint8_t thug_collision_grid_stamp;                         /* 0x00693998 */

/* 0x0048c980: original list terminates in a node whose scene word is -1.
 * No match leaves both output arrays untouched, including old terminators. */
ThugCollisionGrid **thug_collision_select_scenes(const float segment[8]) {
    ThugBounds bounds;
    thug_bounds_from_point(&bounds, segment);
    thug_bounds_expand(&bounds, segment + 4);
    ThugCollisionSceneNode *node = thug_collision_scene_list;
    unsigned count = 0;
    if ((uintptr_t)node->scene == UINT32_MAX) return NULL;
    while (node) {
        ThugCollisionSceneNode *next = node->next;
        if ((uintptr_t)next->scene == UINT32_MAX) next = NULL;
        ThugCollisionScene *scene = node->scene;
        ThugCollisionGrid *grid = scene->collision;
        if (grid && thug_bounds_overlap(&grid->bounds, &bounds)) {
            thug_collision_selected_scenes[count] = scene;
            thug_collision_selected_grids[count] = grid;
            if (++count == 15) break;
        }
        node = next;
    }
    if (!count) return NULL;
    thug_collision_selected_scenes[count] = NULL;
    thug_collision_selected_grids[count] = NULL;
    return thug_collision_selected_grids;
}

/* 0x0048c0b0. */
ThugCollisionScene **thug_collision_get_selected_scenes(void) {
    return thug_collision_selected_scenes;
}

/* 0x0049cb00. Same bucket/chain rules as the recovered generic table lookup. */
void *thug_scene_find_object(const ThugCollisionScene *scene,uint32_t name) {
    return thug_object_table_find(scene->objects,&name,1);
}
/* 0x0048c510. Capture the following sentinel before searching the current scene. */
void *thug_scenes_find_object(uint32_t name) {
    ThugCollisionSceneNode *node=thug_collision_scene_list;
    if((uintptr_t)node->scene==UINT32_MAX)return NULL;
    while(node) {
        ThugCollisionSceneNode *next=node->next;
        if((uintptr_t)next->scene==UINT32_MAX)next=NULL;
        void *value=thug_scene_find_object(node->scene,name);
        if(value)return value;
        node=next;
    }
    return NULL;
}

#define R24 thug_platform_round_x87_single
static int32_t cell_index(float point, float lower, double inverse_width, int32_t count) {
    int32_t index = (int32_t)thug_truncate_double_low_word(R24(R24((double)point - lower) * inverse_width));
    if (index < 0) return 0;
    if (index >= count) return count - 1;
    return index;
}

/* 0x00418710. Bounds queries always advance the shared byte stamp, including
 * empty and single-cell queries. The caller must fit the fixed output buffer. */
ThugCollisionInstance **thug_collision_grid_bounds(const ThugCollisionGrid *grid,const ThugBounds *bounds) {
    double inverse_x=R24(1.0/grid->cell_width);
    uint8_t stamp=++thug_collision_grid_stamp;
    int32_t x0=(int32_t)thug_truncate_double_low_word(R24(R24(R24((double)bounds->min[0]-grid->bounds.min[0])-0.5)*inverse_x));
    float inverse_z=(float)R24(1.0/grid->cell_depth);
    int32_t z0=(int32_t)thug_truncate_double_low_word(R24(R24(R24((double)bounds->min[2]-grid->bounds.min[2])-0.5)*inverse_z));
    int32_t x1=(int32_t)thug_truncate_double_low_word(R24(R24(R24((double)bounds->max[0]-grid->bounds.min[0])+0.5)*inverse_x));
    int32_t z1=(int32_t)thug_truncate_double_low_word(R24(R24(R24((double)bounds->max[2]-grid->bounds.min[2])+0.5)*inverse_z));
    if(x0<0)x0=0;else if(x0>=grid->columns)x0=grid->columns-1;
    if(z0<0)z0=0;else if(z0>=grid->rows)z0=grid->rows-1;
    if(x1<0)x1=0;else if(x1>=grid->columns)x1=grid->columns-1;
    if(z1<0)z1=0;else if(z1>=grid->rows)z1=grid->rows-1;
    uint32_t count=0;
    for(int32_t x=x0;x<=x1;++x)for(int32_t z=z0;z<=z1;++z) {
        const ThugCollisionCell *cell=&grid->cells[x*20+z];
        for(int32_t i=0;i<cell->count;++i) {
            ThugCollisionInstance *object=cell->objects[i];
            if(!(object->flags&6)&&object->query_stamp!=stamp) {
                thug_collision_grid_output[count++]=object;object->query_stamp=stamp;
            }
        }
    }
    thug_collision_grid_output[count]=NULL;return thug_collision_grid_output;
}

/* 0x004188c0. Length arithmetic stays wide, but length and inverse spill to
 * float at the original stores. Normalized X and the X cell inverse stay wide.
 * Single-cell queries keep duplicates and don't change stamps.
 * Multi-cell queries deduplicate by an 8-bit stamp and cap at 2047 objects.
 * The original single-cell path has no cap: validated cells must fit output. */
ThugCollisionInstance **thug_collision_grid_query(const ThugCollisionGrid *grid,
    const float segment[8], int32_t *count_out) {
    double dx = R24((double)segment[4] - segment[0]);
    float stored_x = (float)dx, dy = segment[5] - segment[1], dz = segment[6] - segment[2];
    double length = R24(__builtin_sqrt(R24(R24(R24((double)dz*dz) + R24((double)dy*dy)) + R24((double)stored_x*stored_x))));
    if (length > 0) {
        float inverse = (float)R24(1.0 / (float)length);
        dx = R24((double)stored_x*inverse); dz = (float)R24((double)dz*inverse);
    }
    dx = R24(dx*0.5); dz *= 0.5f;
    double inverse_x = R24(1.0 / grid->cell_width);
    float inverse_z = 1.0f / grid->cell_depth;
    int32_t x0 = cell_index((float)R24((double)segment[0] - dx), grid->bounds.min[0], inverse_x, grid->columns);
    int32_t z0 = cell_index(segment[2] - dz, grid->bounds.min[2], inverse_z, grid->rows);
    int32_t x1 = cell_index((float)R24((double)segment[4] + dx), grid->bounds.min[0], inverse_x, grid->columns);
    int32_t z1 = cell_index(segment[6] + dz, grid->bounds.min[2], inverse_z, grid->rows);
    if (x1 < x0) { int32_t swap = x0; x0 = x1; x1 = swap; }
    if (z1 < z0) { int32_t swap = z0; z0 = z1; z1 = swap; }
    int32_t count = 0;
    if (x0 == x1 && z0 == z1) {
        const ThugCollisionCell *cell = &grid->cells[x0 * 20 + z0];
        for (int32_t i = 0; i < cell->count; ++i) {
            ThugCollisionInstance *object = cell->objects[i];
            if (!(object->flags & 6)) thug_collision_grid_output[count++] = object;
        }
    } else {
        uint8_t stamp = ++thug_collision_grid_stamp;
        for (int32_t x = x0; x <= x1; ++x) {
            for (int32_t z = z0; z <= z1; ++z) {
                const ThugCollisionCell *cell = &grid->cells[x * 20 + z];
                for (int32_t i = 0; i < cell->count; ++i) {
                    ThugCollisionInstance *object = cell->objects[i];
                    if (!(object->flags & 6) && object->query_stamp != stamp && count < 2047) {
                        thug_collision_grid_output[count++] = object;
                        object->query_stamp = stamp;
                    }
                }
            }
        }
    }
    thug_collision_grid_output[count] = NULL;
    if (count_out) *count_out = count;
    return thug_collision_grid_output;
}
#undef R24

/* 0x004106c0. Cache containment is checked before adding the 0.5 AABB margin.
 * Cached queries intentionally leave result->scene unchanged. With no selected
 * scene, uncached queries also preserve it. The result's hit flag is not reset. */
uint8_t thug_collision_scene_segment(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache,
    ThugCollisionQuery *query_state) {
    result->callback = callback;
    ThugBounds bounds;
    thug_bounds_from_point(&bounds, segment);
    thug_bounds_expand(&bounds, segment + 4);
    uint8_t use_cache = cache && thug_bounds_contains(&cache->bounds, &bounds);
    float point[4];
    for (unsigned i = 0; i < 3; ++i) point[i] = bounds.max[i] + 0.5f;
    point[3] = bounds.max[3];
    thug_bounds_expand(&bounds, point);
    for (unsigned i = 0; i < 3; ++i) point[i] = bounds.min[i] - 0.5f;
    point[3] = bounds.min[3];
    thug_bounds_expand(&bounds, point);
    float delta[4];
    for (unsigned i = 0; i < 4; ++i) delta[i] = segment[i + 4] - segment[i];
    result->fraction = thug_collision_select_farthest ? -0.01f : 1.01f;
    uint8_t found = 0;
    if (use_cache) {
        int32_t count = cache->static_count;
        for (int32_t i = 0; i < count; ++i) {
            const ThugCachedCollision *entry = &cache->objects[i];
            if (thug_bounds_overlap(&bounds, entry->bounds)
                && entry->object->methods->segment(entry->object, segment, delta, result, &bounds, query_state))
                found = 1;
        }
    } else {
        ThugCollisionGrid **grids = thug_collision_select_scenes(segment);
        if (!grids) return 0;
        ThugCollisionScene **scenes = thug_collision_get_selected_scenes();
        result->scene = NULL;
        while (*grids) {
            ThugCollisionInstance **objects = thug_collision_grid_query(*grids++, segment, NULL);
            while (*objects) {
                ThugCollisionInstance *object = *objects++;
                if (object->methods->intersects(object, &bounds)
                    && object->methods->segment(object, segment, delta, result, &bounds, query_state)) {
                    found = 1;
                    result->scene = *scenes;
                }
            }
            ++scenes;
        }
    }
    return found;
}

/* 0x00410930: resets to zero afterward, rather than restoring a prior mode. */
uint8_t thug_collision_scene_segment_farthest(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache,
    ThugCollisionQuery *query_state) {
    thug_collision_select_farthest = 1;
    uint8_t found = thug_collision_scene_segment(segment, result, callback, cache, query_state);
    thug_collision_select_farthest = 0;
    return found;
}
