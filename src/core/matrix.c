#include "matrix.h"
#include "vector.h"
#include "../platform/math.h"
#include <stdint.h>

/* 0x00416d80. All sixteen lanes must compare ordered equal. */
uint8_t thug_matrix_equal(const float left[16], const float right[16]) {
    for (unsigned i = 0; i < 16; ++i) if (!(left[i] == right[i])) return 0;
    return 1;
}

/* 0x00416df0. Inverse of an orthonormal affine basis. The original does not
 * validate that contract, and retains the four W entries. Translation products
 * have PC24 precision with the wider x87 exponent until their final stores. */
void thug_matrix_rigid_inverse(float matrix[16]) {
    #define R thug_platform_round_x87_single
    double x = matrix[12], y = matrix[13], z = matrix[14];
    matrix[12] = (float)-R(R(R(y*matrix[1]) + R(z*matrix[2])) + R(x*matrix[0]));
    matrix[13] = (float)-R(R(R(z*matrix[6]) + R(y*matrix[5])) + R(x*matrix[4]));
    matrix[14] = (float)-R(R(R(z*matrix[10]) + R(y*matrix[9])) + R(x*matrix[8]));
    #undef R
    const unsigned from[3] = {1, 2, 6}, to[3] = {4, 8, 9};
    for (unsigned i = 0; i < 3; ++i) {
        uint32_t value, other;
        __builtin_memcpy(&value, matrix+from[i], 4);
        __builtin_memcpy(&other, matrix+to[i], 4);
        /* Only the FLD/FSTP side of each swap quiets signaling NaNs. */
        if ((value & 0x7f800000) == 0x7f800000 && (value & 0x7fffff)) value |= 0x400000;
        __builtin_memcpy(matrix+from[i], &other, 4);
        __builtin_memcpy(matrix+to[i], &value, 4);
    }
}

/* 0x0040af60. Snapshot all results before storing, including for overlapping
 * matrix/input/output. X adds W,Y,Z,X; the other lanes add W,Y,X,Z. */
float *thug_matrix_transform_vector(const float matrix[16], float output[4], const float input[4]) {
    #define R thug_platform_round_x87_single
    float result[4];
    for (unsigned i = 0; i < 4; ++i) {
        double value = R(R((double)matrix[12+i]*input[3]) + R((double)matrix[4+i]*input[1]));
        double x = R((double)matrix[i]*input[0]), z = R((double)matrix[8+i]*input[2]);
        result[i] = (float)(i ? R(R(value+x)+z) : R(R(value+z)+x));
    }
    #undef R
    for (unsigned i = 0; i < 4; ++i) output[i] = result[i];
    return output;
}

static void cross(float out[4], const float a[4], const float b[4]) {
    float x = a[1] * b[2] - a[2] * b[1];
    float y = a[2] * b[0] - a[0] * b[2];
    float z = a[0] * b[1] - a[1] * b[0];
    out[0] = x; out[1] = y; out[2] = z; out[3] = 0;
}

/* 0x00405170. fixed_axis must be 0, 1 or 2. Preserve that axis verbatim,
 * rebuild the other two using the less aligned direction, and normalize them.
 * Equal or unordered dot products take the second path. Translation is untouched. */
float *thug_matrix_orthogonalize(float matrix[16], unsigned fixed_axis) {
    unsigned next_axis = fixed_axis + 1;
    if (next_axis == 3) next_axis = 0;
    unsigned last_axis = next_axis + 1;
    if (last_axis == 3) last_axis = 0;
    float *fixed = matrix + fixed_axis * 4, *next = matrix + next_axis * 4, *last = matrix + last_axis * 4;
    float last_alignment = __builtin_fabsf((last[2] * fixed[2] + last[1] * fixed[1]) + last[0] * fixed[0]);
    float next_alignment = __builtin_fabsf((fixed[2] * next[2] + fixed[1] * next[1]) + fixed[0] * next[0]);
    if (next_alignment > last_alignment) {
        cross(next, last, fixed); thug_vector_normalize(next);
        cross(last, fixed, next); thug_vector_normalize(last);
    } else {
        cross(last, fixed, next); thug_vector_normalize(last);
        cross(next, last, fixed); thug_vector_normalize(next);
    }
    return matrix;
}

/* 0x0040b090. Translation is ignored and W is copied. Compute all results
 * before storing so output may alias input. x87 adds Z, then Y, then X. */
float *thug_matrix_rotate_vector(const float matrix[16], float output[4], const float input[4]) {
    float x = (matrix[8] * input[2] + matrix[4] * input[1]) + input[0] * matrix[0];
    float y = (matrix[9] * input[2] + matrix[5] * input[1]) + matrix[1] * input[0];
    float z = (matrix[10] * input[2] + matrix[6] * input[1]) + matrix[2] * input[0];
    output[3] = input[3]; output[0] = x; output[1] = y; output[2] = z;
    return output;
}

/* 0x00404090. Word-by-word forward copy, including partially overlapping input.
 * Integer copies preserve signaling NaNs and signed zero without FP operations. */
float *thug_matrix_copy(float destination[16], const float source[16]) {
    for (unsigned i = 0; i < 16; ++i) {
        uint32_t word;
        const uint8_t *in = (const uint8_t *)(source + i);
        uint8_t *out = (uint8_t *)&word;
        for (unsigned j = 0; j < 4; ++j) out[j] = in[j];
        in = (const uint8_t *)&word; out = (uint8_t *)(destination + i);
        for (unsigned j = 0; j < 4; ++j) out[j] = in[j];
    }
    return destination;
}

/* 0x005df4ac, the SSE D3DX multiply selected by 5d7c27/5d7d95. Outer rows
 * use pairwise sums; middle rows accumulate left to right. Snapshot all results
 * before any store, as the original does; all input/output aliasing is retained. */
float *thug_matrix_multiply_sse(float out[16], const float left[16], const float right[16]) {
    float result[16];
    for (unsigned row = 0; row < 4; ++row) for (unsigned col = 0; col < 4; ++col) {
        float a = left[row*4] * right[col], b = left[row*4+1] * right[col+4];
        float c = left[row*4+2] * right[col+8], d = left[row*4+3] * right[col+12];
        result[row*4+col] = row == 0 || row == 3 ? (a + b) + (c + d) : ((a + b) + c) + d;
    }
    for (unsigned i = 0; i < 16; ++i) out[i] = result[i];
    return out;
}
float *(*thug_matrix_multiply)(float *, const float *, const float *) = thug_matrix_multiply_sse;

/* 0x00404e70. Both copies of sine/cosine spill independently to float. */
float *thug_matrix_rotation_z(float out[16],float radians) {
    double sine=thug_platform_sin(radians),cosine=thug_platform_cos(radians);
    for(unsigned i=0;i<16;i++)out[i]=0;
    out[0]=out[5]=(float)cosine;out[1]=(float)sine;out[4]=(float)-sine;
    out[10]=out[15]=1;
    return out;
}
/* 0x00405670. Premultiply through the selected D3DX backend. */
float *thug_matrix_rotate_x(float matrix[16],float radians) {
    float rotation[16];
    thug_matrix_rotation_x(rotation,radians);
    thug_matrix_multiply(matrix,rotation,matrix);
    return matrix;
}

/* 0x00404e20. Row-vector Y rotation, used to premultiply the skater basis. */
float *thug_matrix_rotation_y(float out[16], float radians) {
    double sine = thug_platform_sin(radians), cosine = thug_platform_cos(radians);
    for (unsigned i = 0; i < 16; ++i) out[i] = 0;
    out[0] = out[10] = (float)cosine;
    out[2] = (float)-sine; out[8] = (float)sine;
    out[5] = out[15] = 1;
    return out;
}

/* 0x00405710. Premultiply by a Y rotation using the selected D3DX backend. */
float *thug_matrix_rotate_y(float matrix[16], float radians) {
    float rotation[16];
    thug_matrix_rotation_y(rotation,radians);
    thug_matrix_multiply(matrix,rotation,matrix);
    return matrix;
}

#define R24 thug_platform_round_x87_single
/* 0x00404c60. Keep the asymmetric float spills: X/Y remain in x87 registers
 * after normalization, while Z and several products are stored as float32.
 * Transcendentals use the port adapter, with the documented hardware limit. */
float *thug_matrix_axis_angle(float out[16], const float axis[4], float radians) {
    double x = axis[0], y = axis[1]; float z = axis[2];
    double length = R24(__builtin_sqrt(R24(R24(R24((double)z*z) + R24(y*y)) + R24(x*x))));
    if (length > 0) {
        double reciprocal = R24(1.0 / length);
        x = R24(x * reciprocal); y = R24(y * reciprocal); z = (float)R24((double)z * reciprocal);
    }
    double one_minus_cos = R24(1.0 - thug_platform_cos(radians));
    double xx = R24(1.0 - R24(x*x)), yy = R24(1.0 - R24(y*y));
    float zz = (float)R24(1.0 - R24((double)z*z));
    float dx = (float)R24(xx*one_minus_cos), dy = (float)R24(yy*one_minus_cos);
    zz = (float)R24((double)zz*one_minus_cos);
    double yz = R24((double)z*y), xz = R24((double)z*x);
    float xy = (float)R24(y*x);
    float a = (float)R24(yz*one_minus_cos), b = (float)R24(xz*one_minus_cos);
    xy = (float)R24((double)xy*one_minus_cos);
    float sine = (float)thug_platform_sin(radians), xs = (float)R24(x*sine);
    double ys = R24(y*sine), zs = R24((double)z*sine);
    out[0] = (float)R24(1.0-dx); out[1] = (float)R24((double)xy+zs); out[2] = (float)R24((double)b-ys); out[3] = 0;
    out[4] = (float)R24((double)xy-zs); out[5] = (float)R24(1.0-dy); out[6] = (float)R24((double)a+xs); out[7] = 0;
    out[8] = (float)R24((double)b+ys); out[9] = (float)R24((double)a-xs); out[10] = (float)R24(1.0-zz); out[11] = 0;
    out[12] = out[13] = out[14] = 0; out[15] = 1;
    return out;
}
#undef R24

/* 0x00405950, through the lifted D3DX dispatch. */
float *thug_matrix_rotate_axis(float matrix[16], const float axis[4], float radians) {
    float rotation[16];
    thug_matrix_axis_angle(rotation, axis, radians);
    thug_matrix_multiply(matrix, matrix, rotation);
    return matrix;
}
