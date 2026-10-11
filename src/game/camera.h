#ifndef THUG_GAME_CAMERA_H
#define THUG_GAME_CAMERA_H
#include <stdint.h>
typedef struct {
    uint8_t unknown_0[0x5c];
    float position[4], orientation[16];
} ThugCamera;
typedef struct { uint8_t unknown_0[0x18]; ThugCamera *camera; } ThugViewport;
extern uint32_t thug_viewport_mode;
extern const int32_t thug_viewport_counts[6];
extern int32_t *thug_viewport_mapping;
extern ThugViewport *thug_viewports[10];
const float *thug_camera_position(const ThugCamera *);
const float *thug_camera_orientation(const ThugCamera *);
ThugCamera *thug_camera_nearest(const float position[4], float *distance);
ThugCamera *thug_camera_at_viewport(uint32_t index);
#endif
