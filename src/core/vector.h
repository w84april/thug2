#ifndef THUG_CORE_VECTOR_H
#define THUG_CORE_VECTOR_H
#include <stdint.h>
uint8_t thug_vector_not_equal(const float left[4], const float right[4]);
uint32_t thug_vector_equal(const float left[4], const float right[4]);
float *thug_vector_lerp(float out[4], const float left[4], const float right[4], float factor);
double thug_vector_distance_squared(const float left[4], const float right[4]);
double thug_vector_distance(const float left[4], const float right[4]);
double thug_vector_angle_degrees(const float left[4], const float right[4]);
float *thug_vector_rotate_y(float vector[4], float angle);
float *thug_vector_difference(float out[4], const float left[4], const float right[4]);
float *thug_vector_sum(float out[4], const float left[4], const float right[4]);
float *thug_vector_negated(float out[4], const float source[4]);
float *thug_vector_copy(float destination[4], const float source[4]);
float *thug_vector_add(float destination[4], const float source[4]);
float *thug_vector_subtract(float destination[4], const float source[4]);
float *thug_vector_scale(float vector[4], float scale);
float *thug_vector_scaled(float out[4], float scale, const float vector[4]);
float *thug_vector_scaled_copy(float out[4], const float vector[4], float scale);
float *thug_vector_divided(float out[4], const float vector[4], float divisor);
double thug_vector_length(const float vector[4]);
double thug_vector_length_squared(const float vector[4]);
double thug_vector_dot(const float left[4], const float right[4]);
float *thug_vector_cross(float out[4], const float left[4], const float right[4]);
float *thug_vector_normalize(float vector[4]);
float *thug_vector_set_length(float vector[4], float length);
float *thug_vector_align_magnitude(float vector[4], const float direction[4]);
float *thug_vector_clear_below(float vector[4], float threshold);
float *thug_vector_project_plane(float vector[4], const float normal[4]);
float *thug_vector_project_axis(float vector[4], const float axis[4]);
float *thug_vector_project_preserve_length(float vector[4], const float normal[4]);
double thug_vector_signed_angle(const float from[4], const float to[4], const float normal[4]);
void thug_vector_degrees_to_radians(float vector[4]);
float *thug_vector_rotate_axis(float vector[4],const float axis[4],float radians);
#endif
