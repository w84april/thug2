/* Recovered PC collision geometry accessors. See tools/verify_geometry.py.
 * Names are analyst-assigned; no claim of original compiler byte matching.
 */
#include "geometry.h"

/* 0x0040b230: compressed vertices are unsigned 16-bit offsets in sixteenths. */
float *thug_collision_vertex(const ThugCollisionObject *object, float output[4], uint32_t index) {
    float x, y, z;
    if (object->small_vertices) {
        const uint16_t *vertex = (const uint16_t *)object->vertices + index * 3;
        x = vertex[0] * 0.0625f + object->bounds.min[0];
        y = vertex[1] * 0.0625f + object->bounds.min[1];
        z = vertex[2] * 0.0625f + object->bounds.min[2];
    } else {
        const float *vertex = (const float *)object->vertices + index * 3;
        x = vertex[0]; y = vertex[1]; z = vertex[2];
    }
    output[0] = x; output[3] = 0.0f; output[1] = y; output[2] = z;
    return output;
}

/* 0x0040b2d0: same values, different argument order and no return value. */
void thug_collision_vertex_into(const ThugCollisionObject *object, uint32_t index, float output[4]) {
    if (object->small_vertices) {
        const uint16_t *vertex = (const uint16_t *)object->vertices + index * 3;
        output[0] = vertex[0] * 0.0625f + object->bounds.min[0];
        output[1] = vertex[1] * 0.0625f + object->bounds.min[1];
        output[2] = vertex[2] * 0.0625f + object->bounds.min[2];
    } else {
        const float *vertex = (const float *)object->vertices + index * 3;
        output[0] = vertex[0]; output[1] = vertex[1]; output[2] = vertex[2];
    }
    output[3] = 0.0f;
}

static uint16_t face_vertex(const ThugCollisionObject *object, uint32_t face, unsigned corner) {
    const uint8_t *bytes = object->faces;
    if (object->small_faces) return bytes[face * 8 + 4 + corner];
    return ((const uint16_t *)(bytes + face * 10 + 4))[corner];
}

/* 0x00414d80: unit normal from the face's original vertex order.
 * Use single-precision intermediates: the game's CreateDevice call at
 * 0x004d7c80 uses flags 0x24/0x44, without D3DCREATE_FPU_PRESERVE. Direct3D
 * therefore selects single-precision, round-to-nearest x87 arithmetic.
 * This is not an emulation of x87's wider exponent range on extreme inputs.
 */
float *thug_collision_face_normal(const ThugCollisionObject *object, float output[4], uint32_t face) {
    float a[4], b[4], c[4];
    float ax, ay, az, bx, by, bz;
    float x, y, z, length;
    thug_collision_vertex(object, a, face_vertex(object, face, 0));
    thug_collision_vertex(object, b, face_vertex(object, face, 1));
    thug_collision_vertex(object, c, face_vertex(object, face, 2));
    ax = b[0] - a[0]; ay = b[1] - a[1]; az = b[2] - a[2];
    bx = c[0] - a[0]; by = c[1] - a[1];
    bz = c[2] - a[2];
    x = bz * ay - by * az;
    y = az * bx - bz * ax;
    z = by * ax - ay * bx;
    length = __builtin_sqrtf((z * z + y * y) + x * x);
    if (length > 0.0f) {
        float inverse = 1.0f / length;
        x *= inverse; y *= inverse; z *= inverse;
    }
    output[0] = (float)x; output[1] = (float)y; output[2] = (float)z;
    output[3] = 0.0f;
    return output;
}

/* 0x0040b420: one-sided segment/triangle intersection. delta is end - start,
 * not a unit direction. Preserve the original determinant cutoff, relaxed
 * upper barycentric boundary, and operation order. Rejections before the
 * fraction calculation leave its output untouched; later misses write it.
 * The x87 branches allow unordered intermediate comparisons, but the final
 * fraction check rejects NaN. NaN payload bits are not portable to wasm.
 */
uint8_t thug_collision_triangle(const float origin[4], const float delta[4],
    const float a[4], const float b[4], const float c[4], float *fraction) {
    float ex = b[0] - a[0], ey = b[1] - a[1], ez = b[2] - a[2];
    float fx = c[0] - a[0], fy = c[1] - a[1], fz = c[2] - a[2];
    float px = fz * delta[1] - fy * delta[2];
    float py = fx * delta[2] - fz * delta[0];
    float pz = fy * delta[0] - fx * delta[1];
    float determinant = (ez * pz + ex * px) + ey * py;
    if (determinant < 0.03f) return 0;
    float limit = determinant * 1.00001f;
    float tx = origin[0] - a[0], ty = origin[1] - a[1], tz = origin[2] - a[2];
    float u = (tz * pz + ty * py) + tx * px;
    if (u < 0.0f || u > limit) return 0;
    /* Inlined cross product 0x00402550. */
    float qx = ty * ez - tz * ey;
    float qy = tz * ex - tx * ez;
    float qz = tx * ey - ty * ex;
    float v = (qz * delta[2] + qx * delta[0]) + qy * delta[1];
    if (v < 0.0f || u + v > limit) return 0;
    float t = ((qz * fz + qy * fy) + qx * fx) * (1.0f / determinant);
    *fraction = t;
    return t <= 1.0f && t >= 0.0f;
}
