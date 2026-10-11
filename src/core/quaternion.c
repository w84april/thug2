#include "matrix.h"
#include "vector.h"
#include "../platform/math.h"
static double r24(double x) { return thug_platform_round_x87_single(x); }
/* 0x00420140. Snapshot both operands; the X cross product and X*bW retain
 * their wide exponents while the other vector intermediates spill to float. */
float *thug_quaternion_multiply(float a[4],const float b[4]) {
    double x=a[0],y=a[1],z=a[2],w=a[3],bx=b[0],by=b[1],bz=b[2],bw=b[3];
    double cx=r24(r24(y*bz)-r24(z*by));
    float cy=(float)r24(r24(z*bx)-r24(x*bz)),cz=(float)r24(r24(x*by)-r24(y*bx));
    float sx=(float)r24((float)r24(bx*w)+r24(x*bw));
    float sy=(float)r24((double)(float)r24(by*w)+(float)r24(y*bw));
    float sz=(float)r24((double)(float)r24(bz*w)+(float)r24(z*bw));
    a[0]=(float)r24(cx+sx); a[1]=(float)r24((double)sy+cy); a[2]=(float)r24((double)sz+cz);
    a[3]=(float)r24(r24(w*bw)-r24(r24(r24(bz*z)+r24(by*y))+r24(bx*x)));
    return a;
}
/* 0x00420ac0. The vector length and sine scale spill, half-angle does not. */
float *thug_quaternion_axis_angle(float out[4],const float axis[4],float radians) {
    float length=(float)thug_vector_length(axis);
    double half=r24((double)radians*0.5),inverse=length>0?r24(1.0/length):0;
    float scale=(float)r24(thug_platform_sin(half)*inverse);
    double x=r24((double)scale*axis[0]),y=r24((double)scale*axis[1]),z=r24((double)scale*axis[2]);
    out[0]=(float)x; out[1]=(float)y; out[2]=(float)z; out[3]=(float)thug_platform_cos(half);
    return out;
}
/* 0x00420b50. The original embeds input XYZ with W=1 before Q*V*conjugate(Q). */
float *thug_quaternion_rotate(const float q[4],float out[4],const float vector[4]) {
    float inverse[4],product[4],v[4]={vector[0],vector[1],vector[2],1};
    thug_vector_negated(inverse,q); inverse[3]=q[3]; thug_vector_copy(product,q);
    thug_quaternion_multiply(product,v); thug_quaternion_multiply(product,inverse);
    thug_vector_copy(out,product); return out;
}

/* 00421440. In-place vector rotation via original quaternion helpers. */
float *thug_vector_rotate_axis(float v[4],const float axis[4],float angle) {
    float q[4],rotated[4];
    thug_quaternion_axis_angle(q,axis,angle);
    thug_quaternion_rotate(q,rotated,v);
    return thug_vector_copy(v,rotated);
}
