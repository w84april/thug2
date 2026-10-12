#include "../../src/core/vector.h"
#include "../../src/platform/math.h"

static double length_xyz(const float vector[4]) {
    double x = thug_platform_round_x87_single((double)vector[0] * vector[0]);
    double y = thug_platform_round_x87_single((double)vector[1] * vector[1]);
    double z = thug_platform_round_x87_single((double)vector[2] * vector[2]);
    double sum = thug_platform_round_x87_single(thug_platform_round_x87_single(x + y) + z);
    return thug_platform_round_x87_single(__builtin_sqrt(sum));
}

/* 0x004a86d0. All four lanes participate; NaNs compare unequal. */
uint8_t thug_vector_not_equal(const float left[4], const float right[4]) {
    return !(left[0] == right[0] && left[1] == right[1]
        && left[2] == right[2] && left[3] == right[3]);
}
/* 0x0040aed0. Unlike the byte-return inequality helper, EAX is fully defined. */
uint32_t thug_vector_equal(const float left[4], const float right[4]) {
    return left[0] == right[0] && left[1] == right[1]
        && left[2] == right[2] && left[3] == right[3];
}

/* 0x004023f0. Leaves w and zero-length vectors unchanged. The sum order
 * differs from the inlined face-normal helper at 0x00414d80. Retain the x87
 * exponent range through length and scale; only the final coordinates spill. */
float *thug_vector_normalize(float vector[4]) {
    double length = length_xyz(vector);
    if (length > 0) {
        double inverse = thug_platform_round_x87_single(1 / length);
        for (unsigned i = 0; i < 3; ++i) {
            /* x87 infinity times zero produces the negative indefinite NaN;
             * Wasm's default NaN sign is not that original stored encoding. */
            if (__builtin_isinf(vector[i]) && inverse == 0) {
                uint32_t indefinite = UINT32_C(0xffc00000);
                __builtin_memcpy(vector+i, &indefinite, 4);
            } else vector[i] = (float)thug_platform_round_x87_single((double)vector[i] * inverse);
        }
    }
    return vector;
}

/* 0x0042bbf0. W is retained, including when the requested length is zero. */
float *thug_vector_set_length(float vector[4], float length) {
    double current = length_xyz(vector);
    if (current > 0) {
        double scale = thug_platform_round_x87_single((double)length / current);
        for (unsigned i = 0; i < 3; ++i)
            vector[i] = (float)thug_platform_round_x87_single((double)vector[i] * scale);
    }
    return vector;
}

#define R24 thug_platform_round_x87_single
/* 0x004061a0. Retain XYZ magnitude, replace all four lanes. Snapshot products
 * before stores so a partially overlapping direction remains valid. */
float *thug_vector_align_magnitude(float vector[4], const float direction[4]) {
    double length=length_xyz(vector),x=R24(length*direction[0]),y=R24(length*direction[1]);
    float z=(float)R24(length*direction[2]),w=(float)R24(length*direction[3]);
    vector[2]=z;vector[3]=w;vector[0]=(float)x;vector[1]=(float)y;
    return vector;
}
/* 0x004fc370. Equality and unordered comparisons preserve all original bits. */
float *thug_vector_clear_below(float vector[4], float threshold) {
    if(R24((double)threshold*threshold)>thug_vector_length_squared(vector))
        for(unsigned i=0;i<4;i++)vector[i]=0;
    return vector;
}
/* 0x004023a0. X/Y/Z accumulation with a wide exponent until the caller spills. */
double thug_vector_length_squared(const float v[4]) {
    return R24(R24(R24((double)v[0]*v[0])+R24((double)v[1]*v[1]))+R24((double)v[2]*v[2]));
}
/* 0x00402440. Snapshot all sums before any output write. */
float *thug_vector_sum(float out[4], const float left[4], const float right[4]) {
    float result[4];
    for (unsigned i = 0; i < 4; ++i) result[i] = (float)R24((double)left[i]+right[i]);
    for (unsigned i = 0; i < 4; ++i) out[i] = result[i];
    return out;
}
/* 0x0043d990. X/Y differences retain the x87 exponent; Z/W spill before
 * scaling. Only Y retains a wide product through the addition. Snapshot all
 * results before the first output write, including for partial overlaps. */
float *thug_vector_lerp(float out[4], const float left[4], const float right[4], float factor) {
    float result[4];
    for (unsigned i = 0; i < 4; ++i) {
        double delta = R24((double)right[i]-left[i]);
        if (i >= 2) delta = (float)delta;
        double product = R24(delta*factor);
        if (i != 1) product = (float)product;
        result[i] = (float)R24(product+left[i]);
    }
    for (unsigned i = 0; i < 4; ++i) out[i] = result[i];
    return out;
}
/* 0x00402470, 0x00402500. All inputs are loaded before the first store.
 * Negation goes through x87: signaling NaNs quiet on load. */
float *thug_vector_difference(float out[4], const float left[4], const float right[4]) {
    float value[4];
    for (unsigned i = 0; i < 4; ++i) value[i] = (float)R24((double)left[i] - right[i]);
    for (unsigned i = 0; i < 4; ++i) out[i] = value[i];
    return out;
}
float *thug_vector_negated(float out[4], const float source[4]) {
    uint32_t value[4];
    for (unsigned i = 0; i < 4; ++i) {
        __builtin_memcpy(value + i, source + i, 4);
        if ((value[i] & 0x7f800000) == 0x7f800000 && (value[i] & 0x7fffff)) value[i] |= 0x400000;
        value[i] ^= 0x80000000;
    }
    for (unsigned i = 0; i < 4; ++i) __builtin_memcpy(out + i, value + i, 4);
    return out;
}
/* 0x00423680. Z/X/Y squared-distance accumulation, with no float spill
 * before the square root. This differs from the other distance helpers. */
double thug_vector_distance(const float left[4], const float right[4]) {
    double x = R24((double)left[0] - right[0]), y = R24((double)left[1] - right[1]), z = R24((double)left[2] - right[2]);
    return R24(__builtin_sqrt(R24(R24(R24(z*z) + R24(x*x)) + R24(y*y))));
}
/* 0x00402320. Forward word copies retain partial-overlap behavior and raw
 * signaling NaNs, unlike an arithmetic vector operation. */
float *thug_vector_copy(float destination[4], const float source[4]) {
    for (unsigned i = 0; i < 4; ++i) {
        uint32_t word;
        __builtin_memcpy(&word, source + i, 4);
        __builtin_memcpy(destination + i, &word, 4);
    }
    return destination;
}
/* 0x00402340 and 0x00406050. Each lane is read after the preceding store. */
float *thug_vector_add(float destination[4], const float source[4]) {
    for (unsigned i = 0; i < 4; ++i) destination[i] = (float)R24((double)source[i] + destination[i]);
    return destination;
}
float *thug_vector_subtract(float destination[4], const float source[4]) {
    for (unsigned i = 0; i < 4; ++i) destination[i] = (float)R24((double)destination[i] - source[i]);
    return destination;
}
/* 0x00402370. Scale all four lanes; the argument is passed by value. */
float *thug_vector_scale(float vector[4], float scale) {
    for (unsigned i = 0; i < 4; ++i) vector[i] = (float)R24((double)scale * vector[i]);
    return vector;
}
/* 0x004024d0. Snapshot every product before writing, preserving output/input
 * overlap. The original cdecl argument order is output, scale, input. */
float *thug_vector_scaled(float out[4], float scale, const float vector[4]) {
    float result[4];
    for (unsigned i = 0; i < 4; ++i) result[i] = (float)R24((double)scale * vector[i]);
    for (unsigned i = 0; i < 4; ++i) out[i] = result[i];
    return out;
}
/* 0x004024a0. Same products and snapshots, with the other cdecl order. */
float *thug_vector_scaled_copy(float out[4], const float vector[4], float scale) {
    return thug_vector_scaled(out,scale,vector);
}
/* 0x0040af20. W uses the retained reciprocal; XYZ reload its float spill. */
float *thug_vector_divided(float out[4], const float vector[4], float divisor) {
    double reciprocal = R24(1.0/(double)divisor);
    float spilled = (float)reciprocal, result[4];
    for (unsigned i = 0; i < 4; ++i)
        result[i] = (float)R24((i == 3 ? reciprocal : (double)spilled)*vector[i]);
    for (unsigned i = 0; i < 4; ++i) out[i] = result[i];
    return out;
}
/* 0x004023c0. Same X/Y/Z arithmetic as the normalization helper. */
double thug_vector_length(const float vector[4]) { return length_xyz(vector); }
/* 0x00402530. Dot products instead accumulate Z/Y/X. W is ignored. */
double thug_vector_dot(const float left[4], const float right[4]) {
    return R24(R24(R24((double)left[2]*right[2]) + R24((double)left[1]*right[1])) + R24((double)left[0]*right[0]));
}
/* 0x00402550. Compute all three lanes before writing the zero W and XYZ. */
float *thug_vector_cross(float out[4], const float left[4], const float right[4]) {
    double z = R24(R24((double)left[0]*right[1]) - R24((double)left[1]*right[0]));
    double y = R24(R24((double)left[2]*right[0]) - R24((double)left[0]*right[2]));
    double x = R24(R24((double)left[1]*right[2]) - R24((double)left[2]*right[1]));
    out[3] = 0; out[0] = (float)x; out[1] = (float)y; out[2] = (float)z;
    return out;
}
/* 0x0041a820. X/Z/Y summation and the extended exponent range matter to
 * event-radius filtering. W is ignored and no intermediate spills to float. */
double thug_vector_distance_squared(const float left[4], const float right[4]) {
    double x = R24((double)left[0] - right[0]);
    double y = R24((double)left[1] - right[1]);
    double z = R24((double)left[2] - right[2]);
    return R24(R24(R24(x*x) + R24(z*z)) + R24(y*y));
}
/* 0x00406200. The caller supplies a unit axis. All four output products are
 * computed before any coordinate is overwritten, including aliased inputs. */
float *thug_vector_project_axis(float v[4], const float axis[4]) {
    double dot = R24(R24((double)axis[0]*v[0]) + R24((double)v[2]*axis[2]));
    dot = R24(dot + R24((double)v[1]*axis[1]));
    float result[4];
    for (unsigned i = 0; i < 4; ++i) result[i] = (float)R24(dot*axis[i]);
    for (unsigned i = 0; i < 4; ++i) v[i] = result[i];
    return v;
}

/* 0x00406080. Normal is assumed unit length by the caller. All four lanes
 * are reduced. The X product stays wide; Y/Z/W spill before any output write. */
float *thug_vector_project_plane(float v[4], const float normal[4]) {
    double dot = R24(R24((double)normal[0]*v[0]) + R24((double)v[2]*normal[2]));
    dot = R24(dot + R24((double)v[1]*normal[1]));
    double x = R24(dot*normal[0]);
    float y = (float)R24(dot*normal[1]), z = (float)R24(dot*normal[2]), w = (float)R24(dot*normal[3]);
    v[0] = (float)R24((double)v[0] - x);
    v[1] -= y; v[2] -= z; v[3] -= w;
    return v;
}

/* 0x004060f0. Preserve the pre-projection XYZ length and clear W. A zero
 * projection uses the original coordinate permutation as a fallback. Reads in
 * that fallback stay sequential because normal may overlap the output. */
float *thug_vector_project_preserve_length(float v[4], const float normal[4]) {
    float original_length = (float)length_xyz(v);
    thug_vector_project_plane(v,normal);
    if (length_xyz(v) == 0) {
        v[0] = -normal[2]; v[1] = normal[0]; v[2] = -normal[1];
    }
    thug_vector_normalize(v);
    v[3] = 0;
    for (unsigned i = 0; i < 3; ++i) v[i] = (float)R24((double)original_length*v[i]);
    return v;
}

/* This sequence is inlined in 406630 and sums Z, Y, X, unlike 4023f0. */
static double length_zyx(const double v[3]) {
    return R24(__builtin_sqrt(R24(R24(R24(v[2]*v[2]) + R24(v[1]*v[1])) + R24(v[0]*v[0]))));
}
/* 0x00406460. Normalize in registers, preserving the wide exponent range.
 * Left magnitude and final dot accumulate Z/X/Y; right magnitude uses Z/Y/X.
 * Only the clamped dot spills to float before the original CRT acos path. */
double thug_vector_angle_degrees(const float left[4], const float right[4]) {
    double a[3] = {left[0],left[1],left[2]}, b[3] = {right[0],right[1],right[2]};
    double length = R24(__builtin_sqrt(R24(R24(R24(a[2]*a[2]) + R24(a[0]*a[0])) + R24(a[1]*a[1]))));
    if (length > 0) { double scale = R24(1/length); for (unsigned i = 0; i < 3; ++i) a[i] = R24(a[i]*scale); }
    length = length_zyx(b);
    if (length > 0) { double scale = R24(1/length); for (unsigned i = 0; i < 3; ++i) b[i] = R24(b[i]*scale); }
    float cosine = (float)R24(R24(R24(b[2]*a[2]) + R24(b[0]*a[0])) + R24(b[1]*a[1]));
    if (cosine > 1) cosine = 1; else if (cosine < -1) cosine = -1;
    return R24(thug_platform_acos_x87_single(cosine) * (double)57.2957763671875f);
}
/* 0x00420a90. Snapshot X before either write. Y and W are unchanged. */
float *thug_vector_rotate_y(float vector[4], float angle) {
    double sine = thug_platform_sin(angle), cosine = thug_platform_cos(angle), x = vector[0];
    vector[0] = (float)R24(R24(sine*vector[2]) + R24(cosine*x));
    vector[2] = (float)R24(R24(cosine*vector[2]) - R24(x*sine));
    return vector;
}
static void normalize_zyx(float v[4]) {
    double input[3] = {v[0],v[1],v[2]}, length = length_zyx(input);
    if (length > 0) {
        double scale = R24(1/length);
        for (unsigned i = 0; i < 3; ++i) v[i] = (float)R24(input[i]*scale);
    }
}
/* 0x00406630. Project both directions onto the plane, normalize, then clamp
 * their dot product before acos. The second direction remains in x87 registers
 * after its normalization. No input vectors are modified. */
double thug_vector_signed_angle(const float from[4], const float to[4], const float normal[4]) {
    float a[4], b_stored[4], n[4];
    for (unsigned i = 0; i < 4; ++i) { a[i]=from[i]; b_stored[i]=to[i]; n[i]=normal[i]; }
    normalize_zyx(n);
    thug_vector_project_plane(a,n); thug_vector_project_plane(b_stored,n);
    normalize_zyx(a);
    double b[3] = {b_stored[0],b_stored[1],b_stored[2]}, length = length_zyx(b);
    if (length > 0) {
        double scale = R24(1/length);
        for (unsigned i = 0; i < 3; ++i) b[i] = R24(b[i]*scale);
    }
    float cosine = (float)R24(R24(R24(a[2]*b[2]) + R24(b[1]*a[1])) + R24(b[0]*a[0]));
    double x = R24(R24((double)a[2]*n[1]) - R24((double)a[1]*n[2]));
    double y = R24(R24((double)n[2]*a[0]) - R24((double)a[2]*n[0]));
    double z = R24(R24((double)a[1]*n[0]) - R24((double)n[1]*a[0]));
    float sign = (float)R24(R24(R24(z*b[2]) + R24(y*b[1])) + R24(x*b[0]));
    if (cosine > 1) cosine = 1;
    else if (cosine < -1) cosine = -1;
    double angle = thug_platform_acos_x87_single(cosine);
    return sign < 0 ? -angle : angle;
}

/* 0x00405ef0. Convert XYZ degrees to radians; the fourth lane is untouched. */
void thug_vector_degrees_to_radians(float vector[4]) {
    for (unsigned i=0;i<3;++i) vector[i]=(float)thug_platform_round_x87_single((double)vector[i]*(double)0.01745329238474369f);
}
