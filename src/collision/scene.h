#ifndef THUG_COLLISION_SCENE_H
#define THUG_COLLISION_SCENE_H
#include "segment.h"
#include "../core/memory.h"
#include "../core/lookup.h"

typedef struct {
    ThugBounds bounds;
    uint32_t unknown_20;
    int32_t count;
    uint32_t unknown_28;
    ThugCollisionInstance **objects;
} ThugCollisionCell;

typedef struct {
    ThugBounds bounds;
    float cell_width, cell_depth;
    int32_t columns, rows;
    ThugCollisionCell cells[400]; /* Fixed column stride of 20 cells. */
} ThugCollisionGrid;

struct ThugCollisionScene {
    uint8_t unknown_0_to_cf[0xd0];
    ThugObjectLookupTable *objects;
    ThugCollisionGrid *collision;
};

typedef struct ThugCollisionSceneNode {
    uint32_t unknown_0;
    ThugCollisionScene *scene;
    uint32_t unknown_8;
    struct ThugCollisionSceneNode *next;
} ThugCollisionSceneNode;

typedef struct {
    ThugCollisionInstance *object;
    const ThugBounds *bounds;
} ThugCachedCollision;

typedef struct {
    ThugBounds bounds;
    ThugCachedCollision objects[500];
    uint32_t count;
    int32_t static_count, moving_count;
} ThugCollisionCache;
extern ThugCollisionCache *thug_collision_cache_registry[8];
extern uint32_t thug_collision_cache_mask;
void thug_collision_cache_register(ThugCollisionCache *);
void thug_collision_cache_unregister(ThugCollisionCache *);
ThugCollisionCache *thug_collision_cache_initialize(ThugCollisionCache *);
void thug_collision_cache_destroy(ThugCollisionCache *);
/* Engine-owned candidates must fit the original 500-entry fixed storage. */
void thug_collision_cache_build(ThugCollisionCache *, const ThugBounds *);
float *thug_collision_segment_copy(float out[8], const float start[4], const float end[4]);

/* Original mutable globals: same ordering, termination and stamp wrap behavior. */
extern ThugCollisionSceneNode *thug_collision_scene_list;
extern ThugCollisionScene *thug_collision_selected_scenes[16];
extern ThugCollisionGrid *thug_collision_selected_grids[16];
extern ThugCollisionInstance *thug_collision_grid_output[2048];
extern uint8_t thug_collision_grid_stamp;
ThugCollisionCell *thug_collision_cell_initialize(ThugCollisionCell *cell);
void thug_collision_grid_initialize(ThugCollisionGrid *grid, const ThugBounds *bounds);
void thug_collision_grid_populate(ThugCollisionGrid *grid, ThugStaticCollisionInstance *objects,
    int32_t count, const ThugMemory *memory);
ThugCollisionGrid **thug_collision_select_scenes(const float segment[8]);
ThugCollisionScene **thug_collision_get_selected_scenes(void);
void *thug_scene_find_object(const ThugCollisionScene *, uint32_t name);
void *thug_scenes_find_object(uint32_t name);
ThugCollisionInstance **thug_collision_grid_bounds(const ThugCollisionGrid *, const ThugBounds *);
ThugCollisionInstance **thug_collision_grid_query(const ThugCollisionGrid *grid,
    const float segment[8], int32_t *count);
uint8_t thug_collision_scene_segment(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache,
    ThugCollisionQuery *query_state);
uint8_t thug_collision_scene_segment_farthest(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache,
    ThugCollisionQuery *query_state);
#endif
