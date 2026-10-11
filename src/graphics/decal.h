#ifndef THUG_GRAPHICS_DECAL_H
#define THUG_GRAPHICS_DECAL_H
#include "../core/lookup.h"

typedef struct { uint32_t cursor,width; uint8_t data[0x4000]; } ThugGeometryStack;
typedef struct {
    float from[4],to[4],width,height,rotation,angle,lifetime;
    void *texture;
    uint32_t type;
    float *previous;
    uint8_t flag,unknown_41[3];
} ThugDecalProjection;
typedef struct { float position[3];uint32_t color;float uv[2]; } ThugDecalVertex;
typedef struct {
    uint32_t remaining[256],initial[256];
    uint8_t unknown_800_to_340f[0x2c10];
    ThugDecalVertex vertices[768];
} ThugDecalBuffer;
typedef struct { uint8_t storage[0x110]; } ThugRenderMaterial;
typedef struct {
    uint32_t flags;
    uint8_t unknown_4_to_17[0x14];
    uint8_t stride,flag_19,flag_1a,flag_1b,color_offset,normal_offset,uv_offset,flag_1f;
    uint8_t unknown_20_to_d7[0xb8];
} ThugRenderMesh;
typedef struct { uint8_t unknown_0_to_13[0x14];ThugRenderMesh *mesh; } ThugRenderGeometry;
typedef struct { uint8_t unknown_0_to_b[12];ThugObjectLookupTable *textures; } ThugTextureDictionary;

/* New browser boundary for the original vertex-buffer Lock method. The game
 * wrapper's CPU storage bookkeeping is recovered below; the host supplies GPU
 * storage and this method's HRESULT/output behavior. Other slots stay opaque. */
typedef struct ThugVertexBufferDevice ThugVertexBufferDevice;
typedef struct {
    uint32_t unavailable[11];
    uint32_t (*lock)(ThugVertexBufferDevice *,uint32_t,uint32_t,void **,uint32_t);
} ThugVertexBufferDeviceMethods;
struct ThugVertexBufferDevice { const ThugVertexBufferDeviceMethods *methods; };
typedef struct {
    uint32_t size,unknown_4;
    ThugVertexBufferDevice *device;
    void *data;
    uint32_t last_offset,last_size,last_flags;
} ThugVertexBuffer;
typedef struct { uint8_t unknown_0_to_f[16];void *data; } ThugIndexBuffer;

uint32_t thug_decal_choose_slot(const ThugDecalBuffer *,uint32_t count);
void thug_geometry_stack_initialize(ThugGeometryStack *);
void thug_geometry_stack_push(ThugGeometryStack *,const void *);
void thug_geometry_stack_pop(ThugGeometryStack *,void *);
ThugDecalProjection *thug_decal_projection_initialize(ThugDecalProjection *);
void thug_decal_collapse_triangle(ThugDecalBuffer *,uint32_t slot);
ThugRenderMaterial *thug_render_material_initialize(ThugRenderMaterial *);
ThugRenderMesh *thug_render_mesh_initialize(ThugRenderMesh *);
ThugRenderMesh *thug_render_geometry_mesh(const ThugRenderGeometry *);
void *thug_texture_dictionary_find(const ThugTextureDictionary *,uint32_t name);
uint32_t thug_vertex_buffer_lock(ThugVertexBuffer *,uint32_t offset,uint32_t size,void **output,uint32_t flags);
uint32_t thug_index_buffer_lock(const ThugIndexBuffer *,uint32_t offset,uint32_t size,void **output,uint32_t flags);
void *thug_component_copy_direction(const void *,void *output);
uint8_t thug_decal_segments_overlap(float ax,float ay,float bx,float by,float cx,float cy,float dx,float dy);
uint8_t thug_decal_triangle_in_square(float ax,float ay,float bx,float by,float cx,float cy);
extern ThugGeometryStack thug_decal_work_stack;
extern uint8_t thug_decal_scratch_vertices[6][128];
extern float thug_decal_area_threshold;
uint8_t thug_decal_subdivide(void **output,const ThugRenderMesh *format);
/* Original static array capacity is 150 (constructor at 00644c90). */
typedef struct {
    float position[4],intensity,radius;
    uint32_t name,color;
    void *owner;
} ThugDecalLight;
extern uint32_t thug_decal_reserved_slots,thug_decal_fade_step;
extern int32_t thug_decal_light_count;
extern ThugDecalLight thug_decal_lights[150];
void thug_decal_advance_lifetime(uint32_t elapsed,ThugDecalBuffer *);
void thug_decal_light_colors(const uint32_t *source,uint32_t *output,const float *positions,const float *normal,uint32_t count);
void thug_decal_refresh_colors(ThugDecalBuffer *);
extern ThugObjectLookupTable *thug_decal_buffers;
ThugDecalBuffer *thug_decal_find_or_create(void *texture,const ThugMemory *);
ThugDecalBuffer *thug_decal_project(ThugRenderGeometry *const *geometries,const void *unused,
    ThugDecalProjection *,const ThugMemory *);
#endif
