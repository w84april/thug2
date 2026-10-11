#include "d3dx.h"
#include "../platform/math.h"
#include <stdint.h>
#define R24 thug_platform_round_x87_single
static float rf(const void *p) {float v;__builtin_memcpy(&v,p,4);return v;}
static void wf(void *p,float v) {__builtin_memcpy(p,&v,4);}
/* 005e17ed, selected D3DX SSE three-component normalization. */
float *thug_d3dx_normalize3_sse(float *out,const float *in) {
    float x=rf(in),y=rf(in+1),z=rf(in+2);
    float xy=x*x+y*y,squared=xy+z*z;
    if(squared<0x1p-46f) {wf(out,0);wf(out+1,0);wf(out+2,0);return out;}
    float seed=thug_platform_rsqrt_seed(squared),step=squared*seed;step*=seed;
    float correction=3-step,half=0.5f*seed,inverse=half*correction;
    wf(out,inverse*x);wf(out+1,inverse*y);wf(out+2,inverse*z);return out;
}
/* 005e16ea. The original takes both aligned and unaligned matrix paths. */
float *thug_d3dx_transform_coordinate_sse(float *out,const float *in,const float *m) {
    float x=rf(in),y=rf(in+1),z=rf(in+2),v[4];
    for(uint32_t i=0;i<4;++i) {
        float high=z*rf(m+8+i)+rf(m+12+i),low=x*rf(m+i)+y*rf(m+4+i);
        v[i]=low+high;
    }
    float seed=thug_platform_reciprocal_seed(v[3]),step=seed*v[3];step*=seed;
    float twice=seed+seed,scale=twice-step;
    wf(out,v[0]*scale);wf(out+1,v[1]*scale);wf(out+2,v[2]*scale);return out;
}
/* 005c0b39. Keep the depth reciprocal wide for the final translation. */
float *thug_d3dx_ortho_rh(float *out,float width,float height,float near,float far) {
    wf(out,(float)R24(2.0/width));for(uint32_t i=1;i<5;++i)wf(out+i,0);
    wf(out+5,(float)R24(2.0/height));for(uint32_t i=6;i<10;++i)wf(out+i,0);
    double depth=R24(1.0/R24((double)near-far));wf(out+10,(float)depth);
    wf(out+11,0);wf(out+12,0);wf(out+13,0);wf(out+14,(float)R24(depth*near));wf(out+15,1);return out;
}
static double cross_term(float a,float b,float c,float d) {return R24(R24((double)a*b)-R24((double)c*d));}
static double dot_wide(const double *axis,const float *p) {
    return R24(R24(R24(axis[0]*rf(p))+R24(axis[1]*rf(p+1)))+R24(axis[2]*rf(p+2)));
}
/* 005c0985. Preserve eye reads after partial output stores for aliased calls. */
float *thug_d3dx_look_at_rh(float *out,const float *eye,const float *target,const float *up) {
    float z[3]={rf(eye)-rf(target),rf(eye+1)-rf(target+1),rf(eye+2)-rf(target+2)},x[3];
    thug_d3dx_normalize3(z,z);
    x[0]=(float)cross_term(z[2],rf(up+1),z[1],rf(up+2));
    x[1]=(float)cross_term(z[0],rf(up+2),z[2],rf(up));
    x[2]=(float)cross_term(z[1],rf(up),z[0],rf(up+1));
    thug_d3dx_normalize3(x,x);
    wf(out+4,x[1]);wf(out+8,x[2]);
    double y[3]={cross_term(z[1],x[2],z[2],x[1]),cross_term(z[2],x[0],z[0],x[2]),cross_term(z[0],x[1],z[1],x[0])};
    wf(out,x[0]);double wide_x[3]={x[0],x[1],x[2]};wf(out+12,(float)-dot_wide(wide_x,eye));
    wf(out+1,(float)y[0]);wf(out+5,(float)y[1]);wf(out+9,(float)y[2]);
    double ty=-dot_wide(y,eye);wf(out+2,z[0]);wf(out+6,z[1]);wf(out+10,z[2]);wf(out+13,(float)ty);
    double wide_z[3]={z[0],z[1],z[2]};wf(out+14,(float)-dot_wide(wide_z,eye));
    wf(out+3,0);wf(out+7,0);wf(out+11,0);wf(out+15,1);return out;
}
#undef R24

float *(*thug_d3dx_normalize3)(float *, const float *) = thug_d3dx_normalize3_sse;
float *(*thug_d3dx_transform_coordinate)(float *, const float *, const float *) = thug_d3dx_transform_coordinate_sse;
