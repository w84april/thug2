#ifndef THUG_GRAPHICS_DECAL_SCENE_H
#define THUG_GRAPHICS_DECAL_SCENE_H
#include "decal.h"
#include "../collision/scene.h"
typedef struct {float position[4];uint32_t type,timestamp;} ThugDecalPrevious;
extern ThugObjectLookupTable *thug_decal_previous_points;
extern ThugTextureDictionary *thug_decal_texture_dictionary;
extern ThugRenderGeometry *thug_decal_selected_geometry[128];
extern ThugCollisionInstance *thug_decal_selected_collision[128];
uint8_t thug_decal_project_scene(const float from[4],const float to[4],float width,float height,
    float rotation,float angle,float lifetime,const char *texture_name,uint32_t type,
    uint32_t tracking_id,uint8_t flag,void *texture,const ThugMemory *);
#endif
