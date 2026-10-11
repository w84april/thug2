#include "camera.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugCamera, position) == 0x5c, "Camera position");
_Static_assert(offsetof(ThugCamera, orientation) == 0x6c, "Camera orientation");
_Static_assert(offsetof(ThugViewport, camera) == 0x18, "Viewport camera");
uint32_t thug_viewport_mode;
const int32_t thug_viewport_counts[6] = {1,2,2,4,1,1};
int32_t *thug_viewport_mapping;
ThugViewport *thug_viewports[10];
/* 0x00485a00, 0x00485a10. Camera accessors, not camera update behavior. */
const float *thug_camera_position(const ThugCamera *camera) { return camera->position; }
const float *thug_camera_orientation(const ThugCamera *camera) { return camera->orientation; }
/* 0x004a0950. This accessor indexes the mapping directly; it does not skip
 * unused entries as nearest-camera selection does. Only -1 means absent. */
ThugCamera *thug_camera_at_viewport(uint32_t index) {
    int32_t mapped = thug_viewport_mapping[index];
    return mapped == -1 ? NULL : thug_viewports[mapped]->camera;
}
/* 0x004a09e0. Valid modes have enough nonnegative mapping entries and each
 * selected viewport exists. Null camera slots are allowed. Compare the wide
 * candidate squared distance with the previous float; equal distances retain
 * the first camera. The optional distance is untouched if no camera exists. */
ThugCamera *thug_camera_nearest(const float position[4], float *distance) {
    ThugCamera *nearest = NULL;
    float best = -1;
    int32_t count = thug_viewport_counts[thug_viewport_mode];
    for (int32_t i = 0; i < count; ++i) {
        ThugViewport *viewport = NULL;
        int32_t found = 0;
        for (unsigned j = 0; j < 10; ++j) if (thug_viewport_mapping[j] >= 0) {
            if (found == i) { viewport = thug_viewports[thug_viewport_mapping[j]]; break; }
            ++found;
        }
        ThugCamera *camera = viewport->camera;
        if (!camera) continue;
        const float *p = thug_camera_position(camera);
        double x = R24((double)position[0] - p[0]), y = R24((double)position[1] - p[1]), z = R24((double)position[2] - p[2]);
        double squared = R24(R24(R24(x*x) + R24(y*y)) + R24(z*z));
        if (best < 0 || squared < best) { best = (float)squared; nearest = camera; }
    }
    if (nearest && distance) *distance = (float)R24(__builtin_sqrt((double)best));
    return nearest;
}
