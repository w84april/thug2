#include "line.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static float quiet(float value) {
    uint32_t bits;__builtin_memcpy(&bits,&value,4);
    if((bits&0x7f800000)==0x7f800000&&(bits&0x7fffff))bits|=0x400000;
    __builtin_memcpy(&value,&bits,4);return value;
}
/* 005902e0. Identity constructor; all segment storage remains untouched. */
void *thug_segment_initialize(void *segment){return segment;}
/* 0057c260. Ordered endpoint bounds. Ties and unordered comparisons
 * select the second endpoint for the minimum; maximum Y is a raw copy. */
float *thug_segment_bounds(const float a[4],const float b[4],float minimum[4],float maximum[4]) {
    float lo[3],hi[3];
    for(unsigned i=0;i<3;++i) {
        if(a[i]<b[i]) {lo[i]=a[i];hi[i]=b[i];}
        else {lo[i]=b[i];hi[i]=a[i];}
    }
    minimum[0]=quiet(lo[0]);minimum[1]=quiet(lo[1]);minimum[3]=1;minimum[2]=quiet(lo[2]);
    __builtin_memcpy(maximum+1,hi+1,4);maximum[0]=quiet(hi[0]);maximum[3]=1;maximum[2]=quiet(hi[2]);
    return maximum;
}
static double dot_z_y_x(const float a[3],const float b[3]) {
    return R(R(R((double)a[2]*b[2])+R((double)a[1]*b[1]))+R((double)a[0]*b[0]));
}
static double dot_x_z_y(const float a[3],const float b[3]) {
    return R(R(R((double)a[0]*b[0])+R((double)a[2]*b[2]))+R((double)a[1]*b[1]));
}
static void fraction(float *out,double value,uint8_t clamp) {
    *out=(float)value;
    if(clamp) {if(value>1)*out=1;else if(*out<0)*out=0;}
}
static void point(float out[4],const float start[4],const float delta[4],float amount) {
    double x=R((double)delta[0]*amount);
    float y=(float)R((double)delta[1]*amount),z=(float)R((double)delta[2]*amount),w=(float)R((double)delta[3]*amount);
    float result[4]={(float)R(x+start[0]),(float)R((double)y+start[1]),(float)R((double)z+start[2]),(float)R((double)w+start[3])};
    out[3]=result[3];out[0]=result[0];out[1]=result[1];out[2]=result[2];
}
/* 00402f00. Closest-line parameters with the original sequential
 * clamping (second parameter uses the stored first). Parallel/degenerate lines
 * leave outputs untouched. Late source/parameter reads preserve output aliases. */
uint8_t thug_segment_closest_points(const float a[8],const float b[8],float point_a[4],float point_b[4],float *amount_a,float *amount_b,uint32_t clamp) {
    float relative[3],da[4],db[4];
    for(unsigned i=0;i<3;++i)relative[i]=(float)R((double)a[i]-b[i]);
    for(unsigned i=0;i<4;++i)db[i]=(float)R((double)b[4+i]-b[i]);
    const float epsilon=9.999999747378752e-06f;
    if(__builtin_fabsf(db[0])<epsilon&&__builtin_fabsf(db[1])<epsilon&&__builtin_fabsf(db[2])<epsilon)return 0;
    for(unsigned i=0;i<4;++i)da[i]=(float)R((double)a[4+i]-a[i]);
    if(__builtin_fabsf(da[0])<epsilon&&__builtin_fabsf(da[1])<epsilon&&__builtin_fabsf(da[2])<epsilon)return 0;
    double n=dot_z_y_x(db,relative),cross=dot_x_z_y(da,db),bb=dot_x_z_y(db,db);
    double denominator=R(R(dot_x_z_y(da,da)*bb)-R(cross*cross));
    if(__builtin_fabs(denominator)<epsilon)return 0;
    double first=R(R(R(cross*n)-R(dot_z_y_x(da,relative)*bb))/denominator);
    fraction(amount_a,first,(uint8_t)clamp);
    double second=R(R(R(cross*(*amount_a))+n)/bb);
    fraction(amount_b,second,(uint8_t)clamp);
    point(point_a,a,da,*amount_a);point(point_b,b,db,*amount_b);
    return 1;
}

#undef R
