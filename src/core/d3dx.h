#ifndef THUG_CORE_D3DX_H
#define THUG_CORE_D3DX_H
float *thug_d3dx_normalize3_sse(float *output, const float *input);
float *thug_d3dx_transform_coordinate_sse(float *output, const float *input, const float *matrix);
float *thug_d3dx_ortho_rh(float *output, float width, float height, float near, float far);
float *thug_d3dx_look_at_rh(float *output, const float *eye, const float *target, const float *up);
/* Original dispatch slots 684ff4 and 685000. Like matrix multiplication,
 * browser startup selects the recovered SSE path; original CPU detection
 * and the other backends remain outside this recovered subset. */
extern float *(*thug_d3dx_normalize3)(float *, const float *);
extern float *(*thug_d3dx_transform_coordinate)(float *, const float *, const float *);
#endif
