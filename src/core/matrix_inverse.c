#include "matrix.h"
#include "vector.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(offsetof(ThugMatrixInterpolation,axis)==0x80,"Interpolation axis");
_Static_assert(offsetof(ThugMatrixInterpolation,small_angle)==0x94,"Interpolation flag");
float thug_matrix_small_angle=0.03490658476948738f; /* 0x0067c648 */
static double r24(double x) { return thug_platform_round_x87_single(x); }
/* The unrolled original uses this precise cofactor order. No intermediate
 * float store occurs before a cofactor's final output store. */
static double minor3(const float *m,unsigned r0,unsigned r1,unsigned r2,unsigned c0,unsigned c1,unsigned c2) {
    double a=r24(r24((double)m[r1*4+c1]*m[r2*4+c2])-r24((double)m[r2*4+c1]*m[r1*4+c2]));
    double b=r24(r24((double)m[r1*4+c0]*m[r2*4+c2])-r24((double)m[r2*4+c0]*m[r1*4+c2]));
    double c=r24(r24((double)m[r1*4+c0]*m[r2*4+c1])-r24((double)m[r2*4+c0]*m[r1*4+c1]));
    return r24(r24(r24(a*m[r0*4+c0])-r24(b*m[r0*4+c1]))+r24(c*m[r0*4+c2]));
}
/* 0x00404120. Equality skips every write, including signaling payloads. */
float *thug_matrix_scale(float m[16],float factor) {
    if (factor!=1) for (unsigned i=0;i<16;++i) m[i]=(float)r24((double)factor*m[i]);
    return m;
}
/* 0x004041e0. Ghidra's void prototype omits its ST(0) return. Expansion of
 * the first row retains PC=24 precision and a wider exponent throughout. */
double thug_matrix_determinant(const float m[16]) {
    double a=r24(minor3(m,1,2,3,1,2,3)*m[0]);
    double b=r24(minor3(m,1,2,3,0,2,3)*m[1]);
    double c=r24(minor3(m,1,2,3,0,1,3)*m[2]);
    double d=r24(minor3(m,1,2,3,0,1,2)*m[3]);
    return r24(r24(r24(a-b)+c)-d);
}
/* 0x004043a0. Store down each output column, reading the next cofactor after
 * the preceding store. This also preserves the original overlap behavior. */
void thug_matrix_adjugate(float out[16],const float m[16]) {
    static const unsigned keep[4][3]={{1,2,3},{0,2,3},{0,1,3},{0,1,2}};
    for (unsigned row=0;row<4;++row) for (unsigned col=0;col<4;++col) {
        const unsigned *r=keep[row],*c=keep[col];
        double value=minor3(m,r[0],r[1],r[2],c[0],c[1],c[2]);
        out[col*4+row]=(float)(((row+col)&1)?-value:value);
    }
}
/* 0x00405600. The original does not reject singular matrices. */
float *thug_matrix_inverse(float m[16]) {
    float adjugate[16]; thug_matrix_adjugate(adjugate,m);
    double determinant=thug_matrix_determinant(m);
    if (determinant!=1) thug_matrix_scale(adjugate,(float)r24(1/determinant));
    thug_matrix_copy(m,adjugate); return m;
}
/* 0x00405310. Preserve the reciprocal in axis W on the ordinary path and
 * handle the near-pi case using the largest diagonal after output writes. */
void thug_matrix_to_axis_angle(const float m[16],float axis[4],float *angle) {
    double trace=r24(r24(r24((double)m[5]+m[0])+m[10])-1);
    float x=(float)r24((double)m[6]-m[9]),y=(float)r24((double)m[8]-m[2]);
    double wide_z=r24((double)m[1]-m[4]); float z=(float)wide_z;
    double length=r24(__builtin_sqrt(r24(r24(r24(wide_z*z)+r24((double)x*x))+r24((double)y*y))));
    if (length>0) {
        double inverse=r24(1/length);
        axis[0]=(float)r24(x*inverse); axis[1]=(float)r24(y*inverse);
        axis[2]=(float)r24(z*inverse); axis[3]=(float)inverse;
    } else { axis[0]=axis[1]=axis[2]=0; axis[3]=1; }
    *angle=(float)thug_platform_atan2(length,trace);
    if (!(length<=(double)0.01f && trace<=0)) return;
    if (m[0]>m[5] && m[0]>m[10]) {
        double diagonal=r24((double)m[0]+1);
        x=(float)r24(diagonal+diagonal); y=(float)r24((double)m[4]+m[1]); z=(float)r24((double)m[2]+m[8]);
    } else if (!(m[0]>m[5]) && m[5]>m[10]) {
        double diagonal=r24((double)m[5]+1);
        y=(float)r24(diagonal+diagonal); z=(float)r24((double)m[6]+m[9]); x=(float)r24((double)m[4]+m[1]);
    } else {
        double diagonal=r24((double)m[10]+1);
        z=(float)r24(diagonal+diagonal); x=(float)r24((double)m[2]+m[8]); y=(float)r24((double)m[6]+m[9]);
    }
    axis[2]=z; axis[0]=x; axis[1]=y; axis[3]=1; thug_vector_normalize(axis);
}
/* 0x00405990. Input copies are sequential and may alias this state. */
void thug_matrix_interpolation_initialize(ThugMatrixInterpolation *state,const float from[16],const float to[16]) {
    thug_matrix_copy(state->from,from); thug_matrix_copy(state->to,to);
    float relative[16]; thug_matrix_copy(relative,state->from); thug_matrix_inverse(relative);
    thug_matrix_multiply(relative,relative,state->to);
    thug_matrix_to_axis_angle(relative,state->axis,&state->angle);
    state->small_angle=state->angle<thug_matrix_small_angle;
}
/* 0x004058e0. The small-angle flag is intentionally retained. */
void thug_matrix_interpolation_reverse(ThugMatrixInterpolation *state) {
    thug_vector_negated(state->axis,state->axis);
    state->angle=(float)r24((double)6.2831854820251465f-state->angle);
}
/* 0x00405a20. Snapshot differences before writing each basis row. Subsequent
 * rows reread the source, preserving the original partial-overlap behavior. */
void thug_matrix_interpolate(const ThugMatrixInterpolation *s,float out[16],float t) {
    if (t<=0) { thug_matrix_copy(out,s->from); return; }
    if (t>=1) { thug_matrix_copy(out,s->to); return; }
    float from[4],to[4]; thug_vector_copy(from,s->from+12); thug_vector_copy(to,s->to+12);
    if (s->small_angle) {
        float product[16];
        for (unsigned i=0;i<16;++i) {
            double delta=r24((double)s->to[i]-s->from[i]);
            if (i!=13 && i!=14) delta=(float)delta;
            product[i]=(float)r24(delta*t);
        }
        for (unsigned row=0;row<3;++row) {
            float v[4]; for (unsigned i=0;i<4;++i) v[i]=(float)r24((double)product[row*4+i]+s->from[row*4+i]);
            if (!row) { out[3]=v[3]; out[0]=v[0]; out[1]=v[1]; out[2]=v[2]; }
            else { unsigned k=row*4; out[k+2]=v[2]; out[k+3]=v[3]; out[k]=v[0]; out[k+1]=v[1]; }
        }
        float translation[4]; for (unsigned i=0;i<4;++i) translation[i]=(float)r24((double)product[12+i]+from[i]);
        for (unsigned row=0;row<3;++row) thug_vector_normalize(out+row*4);
        out[3]=out[7]=out[11]=0; thug_vector_copy(out+12,translation);
    } else {
        thug_matrix_copy(out,s->from); out[12]=out[13]=out[14]=0; out[15]=1;
        thug_matrix_rotate_axis(out,s->axis,(float)r24((double)t*s->angle));
        for (unsigned i=0;i<4;++i) {
            double delta=r24((double)to[i]-from[i]); if (i>=2) delta=(float)delta;
            double product=r24(delta*t); if (i!=2) product=(float)product;
            out[12+i]=(float)r24(product+from[i]);
        }
        out[15]=1;
    }
}
/* 0x00404dd0. Preserve the positive and negative sine stores independently. */
float *thug_matrix_rotation_x(float out[16],float radians) {
    double sine=thug_platform_sin(radians),cosine=thug_platform_cos(radians);
    out[0]=1; out[1]=out[2]=out[3]=out[4]=0;
    out[5]=(float)cosine; out[6]=(float)sine; out[7]=out[8]=0;
    out[9]=(float)-sine; out[10]=(float)cosine; out[11]=out[12]=out[13]=out[14]=0; out[15]=1;
    return out;
}
