#ifndef THUG_CORE_LINE_H
#define THUG_CORE_LINE_H
#include <stdint.h>
void *thug_segment_initialize(void *);
float *thug_segment_bounds(const float a[4],const float b[4],float minimum[4],float maximum[4]);
uint8_t thug_segment_closest_points(const float a[8],const float b[8],float point_a[4],float point_b[4],float *amount_a,float *amount_b,uint32_t clamp);
#endif
