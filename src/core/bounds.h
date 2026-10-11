#ifndef THUG_BOUNDS_H
#define THUG_BOUNDS_H
#include <stdint.h>

/* Two four-float vectors, matching the 32-byte layout in the executable. */
typedef struct { float min[4], max[4]; } ThugBounds;
void thug_bounds_reset(ThugBounds *bounds);
ThugBounds *thug_bounds_from_point(ThugBounds *bounds, const float point[4]);
void thug_bounds_expand(ThugBounds *bounds, const float point[4]);
uint8_t thug_bounds_overlap(const ThugBounds *a, const ThugBounds *b);
uint8_t thug_bounds_contains(const ThugBounds *outer, const ThugBounds *inner);
int32_t thug_bounds_count_containing_axes(const ThugBounds *bounds,
    const float point[4], uint32_t *axis_mask);
#endif
