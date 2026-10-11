/* Recovered collision/scene bounds helpers. Names are analyst-assigned.
 * Behavior tested against the pinned x86 specimen, not compiler byte-matched.
 */
#include "bounds.h"

/* 0x00403410: includes the fourth components and returns the receiver. */
ThugBounds *thug_bounds_from_point(ThugBounds *bounds, const float point[4]) {
    for (unsigned i = 0; i < 4; ++i) bounds->min[i] = point[i];
    for (unsigned i = 0; i < 4; ++i) bounds->max[i] = point[i];
    return bounds;
}

/* 0x0040b170: the original branches reject only ordered greater-than.
 * In particular, NaNs do not reject an overlap in this helper. */
uint8_t thug_bounds_overlap(const ThugBounds *a, const ThugBounds *b) {
    return !(a->min[0] > b->max[0] || b->min[0] > a->max[0]
          || a->min[2] > b->max[2] || b->min[2] > a->max[2]
          || a->min[1] > b->max[1] || b->min[1] > a->max[1]);
}

/* 0x0040b1d0: inclusive containment, with unordered comparisons rejected. */
uint8_t thug_bounds_contains(const ThugBounds *outer, const ThugBounds *inner) {
    return inner->min[0] >= outer->min[0] && inner->max[0] <= outer->max[0]
        && inner->min[1] >= outer->min[1] && inner->max[1] <= outer->max[1]
        && inner->min[2] >= outer->min[2] && inner->max[2] <= outer->max[2];
}

/* 0x004033e0: the game uses finite sentinels, not infinities or FLT_MAX. */
void thug_bounds_reset(ThugBounds *bounds) {
    bounds->min[0] = bounds->min[1] = bounds->min[2] = 10000000.0f;
    bounds->max[0] = bounds->max[1] = bounds->max[2] = -10000000.0f;
    bounds->min[3] = bounds->max[3] = 1.0f;
}

/* 0x00403450: preserve both fourth components. Ordered comparisons are
 * intentional: using fmin/fmax would change behavior when a bound is NaN. */
void thug_bounds_expand(ThugBounds *bounds, const float point[4]) {
    unsigned i;
    for (i = 0; i < 3; ++i)
        if (point[i] < bounds->min[i]) bounds->min[i] = point[i];
    for (i = 0; i < 3; ++i)
        if (point[i] > bounds->max[i]) bounds->max[i] = point[i];
}

/* 0x004034d0: returns a count (0..3) and an XYZ bit mask, with inclusive edges. */
int32_t thug_bounds_count_containing_axes(const ThugBounds *bounds,
    const float point[4], uint32_t *axis_mask) {
    unsigned i;
    int32_t count = 0;
    *axis_mask = 0;
    for (i = 0; i < 3; ++i) {
        if (point[i] >= bounds->min[i] && point[i] <= bounds->max[i]) {
            *axis_mask |= 1u << i;
            ++count;
        }
    }
    return count;
}
