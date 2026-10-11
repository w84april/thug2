#ifndef THUG_CORE_MATRIX_H
#define THUG_CORE_MATRIX_H
#include <stdint.h>
typedef struct {
    float from[16], to[16], axis[4], angle;
    uint8_t small_angle, untouched[3];
} ThugMatrixInterpolation;
extern float thug_matrix_small_angle;
float *thug_matrix_scale(float matrix[16], float factor);
double thug_matrix_determinant(const float matrix[16]);
void thug_matrix_adjugate(float out[16], const float matrix[16]);
float *thug_matrix_inverse(float matrix[16]);
void thug_matrix_to_axis_angle(const float matrix[16], float axis[4], float *angle);
void thug_matrix_interpolation_initialize(ThugMatrixInterpolation *, const float from[16], const float to[16]);
void thug_matrix_interpolation_reverse(ThugMatrixInterpolation *);
void thug_matrix_interpolate(const ThugMatrixInterpolation *, float out[16], float factor);
float *thug_quaternion_multiply(float quaternion[4], const float right[4]);
float *thug_quaternion_axis_angle(float quaternion[4], const float axis[4], float radians);
float *thug_quaternion_rotate(const float quaternion[4], float out[4], const float vector[4]);
float *thug_matrix_rotation_x(float out[16], float radians);
float *thug_matrix_rotation_z(float out[16], float radians);
float *thug_matrix_rotate_x(float matrix[16], float radians);
uint8_t thug_matrix_equal(const float left[16], const float right[16]);
void thug_matrix_rigid_inverse(float matrix[16]);
float *thug_matrix_transform_vector(const float matrix[16], float output[4], const float input[4]);
float *thug_matrix_rotate_vector(const float matrix[16], float output[4], const float input[4]);
float *thug_matrix_orthogonalize(float matrix[16], unsigned fixed_axis);
float *thug_matrix_copy(float destination[16], const float source[16]);
float *thug_matrix_axis_angle(float out[16], const float axis[4], float radians);
float *thug_matrix_multiply_sse(float out[16], const float left[16], const float right[16]);
/* Lifted D3DX dispatch slot 684fe4. Browser startup selects the recovered SSE
 * arithmetic path; original CPU/registry dispatch and other backends remain. */
extern float *(*thug_matrix_multiply)(float *, const float *, const float *);
float *thug_matrix_rotate_axis(float matrix[16], const float axis[4], float radians);
float *thug_matrix_rotation_y(float out[16], float radians);
float *thug_matrix_rotate_y(float matrix[16], float radians);
#endif
