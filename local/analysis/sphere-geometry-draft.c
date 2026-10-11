#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
#include <stdint.h>
static double r(double x){return thug_platform_round_x87_single(x);}
static double invalid(double x){return __builtin_isnan(x)?-__builtin_nan(""):r(x);}
static double add(double a,double b){return invalid(a+b);}
static double sub(double a,double b){return invalid(a-b);}
static double mul(double a,double b){return invalid(a*b);}
static double divide(double a,double b){return invalid(a/b);}
/* 00403210. The original sphere constructor only clears the radius. */
void *thug_sphere_initialize_draft(void *p){((float *)p)[4]=0;return p;}
/* 00418330. Other contact/result bytes deliberately remain untouched. */
void *thug_sphere_probe_construct_draft(void *p,const float center[4],float radius){
 thug_sphere_initialize_draft(p);
 for(unsigned i=0;i<4;i++)__builtin_memcpy((char *)p+4*i,center+i,4);
 __builtin_memcpy((char *)p+16,&radius,4);
 for(unsigned off=0x598;off<=0x5a8;off+=4){uint32_t value=off==0x5a4?0x3f800000:0;__builtin_memcpy((char *)p+off,&value,4);}
 uint32_t zero=0;uint16_t flags=0x10,required=0;
 __builtin_memcpy((char *)p+0xb5c,&zero,4);__builtin_memcpy((char *)p+0x5ac,&zero,4);
 __builtin_memcpy((char *)p+0x5b4,&zero,4);__builtin_memcpy((char *)p+0xb50,&zero,4);
 __builtin_memcpy((char *)p+0x5b2,&required,2);__builtin_memcpy((char *)p+0x5b0,&flags,2);
 return p;
}
/* 0040b860. Squared point/triangle distance and optional barycentric outputs.
 * Keep the original PC24 expression order and the few unspilled intermediates. */
double thug_triangle_distance_squared_draft(const float p[4],const float a[4],const float b[4],const float c[4],float *out_s,float *out_t){
 double dx=sub(a[0],p[0]),dy=sub(a[1],p[1]),dz=sub(a[2],p[2]);
 double ex=sub(b[0],a[0]),ey=sub(b[1],a[1]),ez=sub(b[2],a[2]);
 float exf=(float)ex,eyf=(float)ey,ezf=(float)ez;
 float a00=(float)add(add(mul(ez,ezf),mul(ey,ey)),mul(exf,exf));
 double fx=sub(c[0],a[0]);float fxf=(float)fx,fy=(float)sub(c[1],a[1]),fz=(float)sub(c[2],a[2]);
 float a01=(float)add(add(mul(ezf,fz),mul(eyf,fy)),mul(exf,fx));
 float a11=(float)add(add(mul(fz,fz),mul(fy,fy)),mul(fxf,fxf));
 float b0=(float)add(add(mul(ezf,dz),mul(ey,dy)),mul(exf,dx));
 float b1=(float)add(add(mul(fz,dz),mul(fy,dy)),mul(fxf,dx));
 double distance=add(add(mul(dx,dx),mul(dz,dz)),mul(dy,dy));
 float det=(float)__builtin_fabs(sub(mul(a11,a00),mul(a01,a01)));
 float s=(float)sub(mul(b1,a01),mul(b0,a11)),t=0;double twide=sub(mul(b0,a01),mul(b1,a00));
 if(add(s,twide)<=det){
  if(s<0){
   if(twide<0){
    if(b0<0)goto edge_s;
    s=0;if(b1>=0){t=0;goto done;}
    if(-b1>=a11)goto vertex_t;
    goto ratio_t;
   }
   s=0;if(b1>=0){t=0;goto done;}
   /* This branch compares b1 itself, as in 0040bacc -> 0040ba80. */
   if(b1>=a11)goto vertex_t;
   goto ratio_t;
  }
  if(twide<0){t=0;if(b0<0)goto edge_s;s=0;goto done;}
  {double inv=divide(1,det);s=(float)mul(s,inv);t=(float)mul(inv,twide);twide=t;goto quadratic;}
 }
 if(s<0){
  float x=(float)add(b0,a01);double y=add(b1,a11);
  if(y>x){
   double numerator=sub(y,x),denominator=add(sub(a00,add(a01,a01)),a11);
   if(numerator>=denominator)goto vertex_s;
   s=(float)divide(numerator,denominator);twide=sub(1,s);t=(float)twide;goto quadratic;
  }
  s=0;if(y<=0)goto vertex_t;if(b1>=0){t=0;goto done;}goto ratio_t;
 }
 if(twide<0){
  float x=(float)add(b1,a01);double y=add(b0,a00);
  if(y>x){
   double numerator=sub(y,x),denominator=add(sub(a00,add(a01,a01)),a11);
   if(numerator>=denominator)goto vertex_t;
   t=(float)divide(numerator,denominator);s=(float)sub(1,t);twide=t;goto quadratic;
  }
  t=0;if(y<=0)goto vertex_s;if(b0>=0){s=0;goto done;}goto ratio_s;
 }
 {double numerator=sub(sub(add(b1,a11),a01),b0);float stored=(float)numerator;
  if(numerator<=0)goto vertex_t;
  double denominator=add(sub(a00,add(a01,a01)),a11);
  if(stored>=denominator)goto vertex_s;
  s=(float)divide(stored,denominator);twide=sub(1,s);t=(float)twide;goto quadratic;
 }
edge_s:t=0;if(-b0>=a00)goto vertex_s;
ratio_s:{double scale=-divide(b0,a00);s=(float)scale;distance=add(mul(scale,b0),distance);goto done;}
ratio_t:{double scale=-divide(b1,a11);t=(float)scale;distance=add(mul(scale,b1),distance);goto done;}
vertex_s:s=1;t=0;distance=add(add(add(b0,b0),distance),a00);goto done;
vertex_t:s=0;t=1;distance=add(add(add(b1,b1),distance),a11);goto done;
quadratic:{double part_t=mul(add(add(mul(twide,a11),mul(s,a01)),add(b1,b1)),t);
 double part_s=mul(add(add(mul(t,a01),mul(s,a00)),add(b0,b0)),s);distance=add(add(part_s,part_t),distance);}
done:if(out_s)*out_s=s;if(out_t)*out_t=t;return __builtin_fabs(distance);
}
/* Comparison ABI preserves all return bits across the JavaScript boundary. */
uint64_t thug_triangle_distance_squared_bits_draft(const float *p,const float *a,const float *b,const float *c,float *s,float *t){
 double value=thug_triangle_distance_squared_draft(p,a,b,c,s,t);uint64_t bits;__builtin_memcpy(&bits,&value,8);return bits;
}
/* 0040f9e0. One-sided stationary sphere/triangle test. The normal is written
 * even on an early miss; the closest point is written after the plane gate,
 * including distance misses. Equality at the radius is a hit. */
uint32_t thug_sphere_triangle_draft(const float sphere[5],const float a[4],const float b[4],const float c[4],float point[4],float normal[4]){
 double fx=sub(c[0],a[0]),fy=sub(c[1],a[1]),fz=sub(c[2],a[2]);
 float ex=(float)sub(b[0],a[0]),ey=(float)sub(b[1],a[1]);double ez=sub(b[2],a[2]);
 normal[3]=0;float nx=(float)sub(mul(ey,fz),mul(ez,fy)),ny=(float)sub(mul(ez,fx),mul(fz,ex));
 normal[1]=ny;double nz=sub(mul(fy,ex),mul(ey,fx));normal[0]=nx;normal[2]=(float)nz;
 if(add(add(mul(nz,nz),mul(ny,ny)),mul(nx,nx))<=0)return 0;
 double dx=sub(a[0],sphere[0]),dy=sub(a[1],sphere[1]),dz=sub(a[2],sphere[2]);
 if(add(add(mul(dy,normal[1]),mul(dx,normal[0])),mul(dz,normal[2]))>=0)return 0;
 thug_vector_normalize(normal);float s,t;double distance=thug_triangle_distance_squared_draft(sphere,a,b,c,&s,&t);
 float cx=(float)mul(sub(c[0],a[0]),t);double cy=mul(sub(c[1],a[1]),t);
 float cz=(float)mul((float)sub(c[2],a[2]),t),cw=(float)mul((float)sub(c[3],a[3]),t);
 float bx=(float)mul(sub(b[0],a[0]),s);double by=mul(sub(b[1],a[1]),s),bz=mul((float)sub(b[2],a[2]),s);
 float bw=(float)mul((float)sub(b[3],a[3]),s);
 float px=(float)add(bx,a[0]),py=(float)add(by,a[1]),pz=(float)add(bz,a[2]),pw=(float)add(bw,a[3]);
 float ox=(float)add(px,cx),oy=(float)add(cy,py),oz=(float)add(pz,cz),ow=(float)add(pw,cw);
 point[3]=ow;point[0]=ox;point[1]=oy;point[2]=oz;
 return distance<=mul(sphere[4],sphere[4]);
}
