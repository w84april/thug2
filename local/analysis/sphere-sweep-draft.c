#include "../../src/core/vector.h"
#include "../../src/core/line.h"
#include "../../src/platform/math.h"
#include <stdint.h>
static double rounded(double x){return __builtin_isnan(x)?-__builtin_nan(""):thug_platform_round_x87_single(x);}
static double add(double a,double b){return rounded(a+b);}
static double sub(double a,double b){return rounded(a-b);}
static double mul(double a,double b){return rounded(a*b);}
static double divi(double a,double b){return rounded(a/b);}
static double dot_zyx(const double a[3],const double b[3]){return add(add(mul(a[2],b[2]),mul(a[1],b[1])),mul(a[0],b[0]));}
static double dot_xzy(const double a[3],const double b[3]){return add(add(mul(a[0],b[0]),mul(a[2],b[2])),mul(a[1],b[1]));}
/* 00402640. Segment/segment squared distance and optional parameters.
 * The original region-specific arithmetic, parallel branch and float spills
 * matter: replacing this with the other closest-line routine changes results. */
double thug_segment_distance_squared_draft(const float first[8],const float second[8],float *out_s,float *out_t){
 double diff[3],u[3],v[3],neg_u[3],neg_diff[3];
 for(unsigned i=0;i<3;i++){diff[i]=(float)sub(first[i],second[i]);u[i]=sub(first[i+4],first[i]);v[i]=(float)sub(second[i+4],second[i]);neg_u[i]=-u[i];neg_diff[i]=-diff[i];}
 float a=(float)dot_xzy(u,u);
 float b=(float)dot_xzy(neg_u,v),c=(float)dot_xzy(v,v);
 float d=(float)add(add(mul(u[0],diff[0]),mul(u[1],diff[1])),mul(u[2],diff[2]));
 double distance=dot_xzy(diff,diff),detwide=__builtin_fabs(sub(mul(c,a),mul(b,b)));
 float det=(float)detwide,s=0,t=0,e=0;double q=0,ewide=0;
 if(detwide>=9.999999974752427e-07f){
  ewide=dot_xzy(neg_diff,v);e=(float)ewide;
  s=(float)sub(mul(ewide,b),mul(d,c));t=(float)sub(mul(d,b),mul(e,a));
  if(s>=0){
   if(s<=det){
    if(t<0)goto edge_bottom;
    if(t<=det){
     double inverse=divi(1,det);s=(float)mul(s,inverse);double twide=mul(inverse,t);t=(float)twide;
     double part_t=mul(add(add(mul(twide,c),mul(s,b)),add(e,e)),t);
     double part_s=mul(add(add(mul(t,b),mul(s,a)),add(d,d)),s);
     distance=add(add(part_t,part_s),distance);goto done;
    }
    t=1;q=add(d,b);goto top_wide;
   }
   if(t<0){
    if(-d>=a)goto edge_right;
    t=0;if(d>=0){s=0;goto done;}
    goto bottom_ratio_wide;
   }
   if(t<=det)goto edge_right;
   q=(float)add(d,b);
   if(-q>a)goto edge_right;
   t=1;if(q>=0)goto top_left;
   s=(float)-divi(q,a);distance=add(add(add(mul(q,s),add(e,e)),distance),c);goto done;
  }
  if(t<0){if(d>=0)goto edge_left;t=0;goto bottom_clamp;}
  if(t<=det)goto edge_left;
  q=add(d,b);if(q>=0)goto edge_left;
  t=1;goto top_wide;
 }
 if(b>0){
  if(d>=0){s=0;t=0;goto done;}
  if(-d<=a){s=(float)-divi(d,a);t=0;distance=add(mul(s,d),distance);goto done;}
  s=1;ewide=dot_xzy(neg_diff,v);q=add(d,a);
  if(-q>=b){t=1;double n=add(add(ewide,d),b);distance=add(add(add(add(n,n),distance),c),a);goto done;}
  t=(float)-divi(q,b);double n=add(ewide,b);
  distance=add(add(add(mul(add(add(n,n),mul(t,c)),t),add(d,d)),distance),a);goto done;
 }
 if(-d>=a){s=1;t=0;distance=add(add(add(d,d),distance),a);goto done;}
 if(d<=0){s=(float)-divi(d,a);t=0;distance=add(mul(s,d),distance);goto done;}
 e=(float)dot_xzy(neg_diff,v);s=0;
 if(-b<=d){t=1;distance=add(add(add(e,e),distance),c);goto done;}
 {double twide=-divi(d,b);t=(float)twide;distance=add(mul(add(mul(twide,c),add(e,e)),t),distance);goto done;}
edge_bottom:t=0;if(d>=0){s=0;goto done;}
bottom_clamp:if(-d>=a){s=1;distance=add(add(add(d,d),distance),a);goto done;}
bottom_ratio_wide:{double swide=-divi(d,a);s=(float)swide;distance=add(mul(swide,d),distance);goto done;}
edge_left:s=0;if(e>=0){t=0;goto done;}
 if(-e>=c){t=1;distance=add(add(add(e,e),distance),c);goto done;}
 {double twide=-divi(e,c);t=(float)twide;distance=add(mul(twide,e),distance);goto done;}
edge_right:s=1;q=add(e,b);
 if(q>=0){t=0;distance=add(add(add(d,d),distance),a);goto done;}
 if(-q>=c){t=1;double n=add(q,d);distance=add(add(add(add(n,n),distance),c),a);goto done;}
 t=(float)-divi(q,c);distance=add(add(add(mul(q,t),add(d,d)),distance),a);goto done;
top_wide:if(q>=0)goto top_left;
 if(-q>=a){s=1;double n=add(q,e);distance=add(add(add(add(n,n),distance),c),a);goto done;}
 s=(float)-divi(q,a);distance=add(add(add(mul(q,s),add(e,e)),distance),c);goto done;
top_left:s=0;distance=add(add(add(e,e),distance),c);
done:if(out_s)*out_s=s;if(out_t)*out_t=t;return __builtin_fabs(distance);
}
/* 00402d60. The optional output is point minus closest segment point,
 * including W. End branches retain all components in x87 until the stores. */
double thug_segment_point_distance_squared_draft(const float segment[8],const float point[4],float *displacement){
 float delta[4];double relative[4];
 for(unsigned i=0;i<4;i++){delta[i]=(float)sub(segment[i+4],segment[i]);relative[i]=sub(point[i],segment[i]);}
 double dv[3]={delta[0],delta[1],delta[2]};
 float dot=(float)dot_zyx(relative,dv),length=(float)dot_zyx(dv,dv);
 if(dot<=0)goto endpoint;
 if(length<=dot){for(unsigned i=0;i<4;i++)relative[i]=sub(point[i],segment[i+4]);goto endpoint;}
 {
  double ratio=divi(dot,length),cx=add(mul(delta[0],ratio),segment[0]);
  double cy=add((float)mul(delta[1],ratio),segment[1]);
  float cz=(float)add((float)mul(delta[2],ratio),segment[2]),cw=(float)add((float)mul(delta[3],ratio),segment[3]);
  relative[0]=(float)sub(point[0],cx);relative[1]=sub(point[1],cy);relative[2]=sub(point[2],cz);relative[3]=sub(point[3],cw);
  if(displacement){displacement[1]=(float)relative[1];displacement[0]=(float)relative[0];displacement[2]=(float)relative[2];displacement[3]=(float)relative[3];}
  return dot_zyx(relative,relative);
 }
endpoint:if(displacement)for(unsigned i=0;i<4;i++)displacement[i]=(float)relative[i];return dot_zyx(relative,relative);
}
/* 00403230 / 004032a0. Capsule constructors, from start+delta or segment.
 * Sequential raw word copies preserve overlapping source behavior. */
void *thug_capsule_from_delta_draft(float capsule[9],const float start[4],const float delta[4],float radius){
 thug_vector_copy(capsule,start);float end[4];for(unsigned i=0;i<4;i++)end[i]=(float)add(start[i],delta[i]);
 capsule[6]=end[2];capsule[7]=end[3];capsule[4]=end[0];capsule[5]=end[1];
 __builtin_memcpy(capsule+8,&radius,4);return capsule;
}
void *thug_capsule_from_segment_draft(float capsule[9],const float segment[8],float radius){
 for(unsigned i=0;i<8;i++)__builtin_memcpy(capsule+i,segment+i,4);
 __builtin_memcpy(capsule+8,&radius,4);return capsule;
}
/* 004032e0. Inclusive radius test; optional squared distance is stored first. */
uint32_t thug_capsule_segment_draft(const float capsule[9],const float segment[8],float *s,float *t,float *distance){
 double d=thug_segment_distance_squared_draft(capsule,segment,s,t);if(distance)*distance=(float)d;
 return d<=mul(capsule[8],capsule[8]);
}
/* 00403330. Radius is captured before the callee and output only on a hit. */
uint32_t thug_capsule_point_draft(const float capsule[9],const float point[4],float *displacement){
 float radius=capsule[8],temp[4];double distance=thug_segment_point_distance_squared_draft(capsule,point,temp);
 if(!(mul(radius,radius)>=distance))return 0;
 if(displacement)thug_vector_copy(displacement,temp);return 1;
}
/* 0040b610. Original relative-motion point/sphere time calculation. A miss
 * at the perpendicular-distance gate retains time; a late miss writes it.
 * Negative times and the original zero-discriminant arithmetic are retained. */
uint32_t thug_sphere_relative_time_draft(const float origin[4],const float velocity_origin[4],const float sphere[5],const float velocity_end[4],float *time,float maximum){
 double v[3],p[3];for(unsigned i=0;i<3;i++){v[i]=sub(velocity_end[i],velocity_origin[i]);p[i]=(float)sub(sphere[i],origin[i]);}
 double cross[3]={sub(mul(p[1],v[2]),mul(p[2],v[1])),sub(mul(p[2],v[0]),mul(v[2],p[0])),sub(mul(p[0],v[1]),mul(p[1],v[0]))};
 float radius2=(float)mul(sphere[4],sphere[4]);float velocity2=(float)add(add(mul(v[2],v[2]),mul(v[0],v[0])),mul(v[1],v[1]));
 if(mul(velocity2,radius2)<dot_zyx(cross,cross))return 0;
 double dot=dot_zyx(p,v),c=sub(dot_zyx(p,p),radius2);
 double inverse=divi(1,rounded(__builtin_sqrt(__builtin_fabs(sub(mul(dot,dot),mul(c,velocity2))))));
 double value=divi(mul(inverse,c),sub(1,mul(inverse,dot)));*time=(float)value;return !(value>maximum);
}
/* 0040e280. Finite segment/sphere intersections. This routine deliberately
 * retains the original inside-sphere exit behavior and count/output ordering. */
uint32_t thug_segment_sphere_intersections_draft(const float segment[8],const float sphere[5],uint32_t *count,float points[8]){
 double relative[3];float delta[4];for(unsigned i=0;i<3;i++)relative[i]=sub(segment[i],sphere[i]);
 for(unsigned i=0;i<4;i++)delta[i]=(float)sub(segment[i+4],segment[i]);
 double dv[3]={delta[0],delta[1],delta[2]};float a=(float)dot_zyx(dv,dv);
 float b=(float)add(add(mul(dv[2],relative[2]),mul(dv[0],relative[0])),mul(dv[1],relative[1]));
 double c=sub(add(add(mul(relative[2],relative[2]),mul(relative[0],relative[0])),mul(relative[1],relative[1])),mul(sphere[4],sphere[4]));
 float disc=(float)sub(mul(b,b),mul(c,a)),first=0,second=0;
 if(disc<0){*count=0;return 0;}
 if(disc>0){
  double root=rounded(__builtin_sqrt(disc)),inverse=divi(1,a);first=(float)mul(sub(-b,root),inverse);second=(float)mul(sub(root,b),inverse);
  if(first>1||second<0){*count=0;return 0;}
  if(first>=0)*count=second>1?1:2;
  else{*count=1;first=second;}
 }else{
  first=(float)-divi(b,a);if(!(first>=0&&first<=1)){*count=0;return 0;}*count=1;
 }
 uint32_t emit=*count;float temp[4],sum[4];
 thug_vector_scaled(temp,first,delta);thug_vector_sum(sum,segment,temp);thug_vector_copy(points,sum);
 if(emit==2){thug_vector_scaled(temp,second,delta);thug_vector_sum(sum,segment,temp);thug_vector_copy(points+4,sum);}
 return 1;
}
/* Comparison-only wrappers keep all double return bits across JavaScript. */
uint64_t thug_segment_distance_squared_bits_draft(const float *a,const float *b,float *s,float *t){double x=thug_segment_distance_squared_draft(a,b,s,t);uint64_t bits;__builtin_memcpy(&bits,&x,8);return bits;}
uint64_t thug_segment_point_distance_squared_bits_draft(const float *a,const float *b,float *v){double x=thug_segment_point_distance_squared_draft(a,b,v);uint64_t bits;__builtin_memcpy(&bits,&x,8);return bits;}
