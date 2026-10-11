#include "../../src/core/vector.h"
#include "../../src/core/line.h"
#include "../../src/platform/math.h"
#include <stdint.h>
extern void *thug_capsule_from_segment_draft(float *,const float *,float);
extern void *thug_capsule_from_delta_draft(float *,const float *,const float *,float);
extern uint32_t thug_capsule_segment_draft(const float *,const float *,float *,float *,float *);
extern uint32_t thug_capsule_point_draft(const float *,const float *,float *);
extern uint32_t thug_segment_sphere_intersections_draft(const float *,const float *,uint32_t *,float *);
extern uint32_t thug_sphere_relative_time_draft(const float *,const float *,const float *,const float *,float *,float);
extern double thug_triangle_distance_squared_draft(const float *,const float *,const float *,const float *,float *,float *);
static double r(double x){return __builtin_isnan(x)?-__builtin_nan(""):thug_platform_round_x87_single(x);}
static double add(double a,double b){return r(a+b);}
static double sub(double a,double b){return r(a-b);}
static double mul(double a,double b){return r(a*b);}
static double divi(double a,double b){return r(a/b);}
static double dot(const float *a,const float *b,unsigned x,unsigned y,unsigned z){return add(add(mul(a[x],b[x]),mul(a[y],b[y])),mul(a[z],b[z]));}
/* 00401020. Compiler array constructor: signed test of count-1, then forward
 * thiscall construction at the supplied stride. Constructor returns are ignored. */
void thug_array_construct_draft(void *start,uint32_t stride,uint32_t count,void *(*construct)(void *)){
 if((int32_t)(count-1)<0)return;
 uintptr_t at=(uintptr_t)start;do{construct((void *)at);at+=stride;}while(--count);
}
/* 0040e560. Initial segment/sphere intersection, then relative capsule query.
 * The original chooses between the two closest-segment parameters as time;
 * do not substitute a quadratic root finder. maximum is passed through to an
 * unused argument of the original initial-intersection callee. */
uint32_t thug_moving_segment_sphere_draft(const float segment[8],const float segment_velocity[4],const float sphere[5],const float sphere_velocity[4],float *time,float maximum,uint32_t *count,float points[8]){
 (void)maximum;
 if(thug_segment_sphere_intersections_draft(segment,sphere,count,points))return 1;
 float capsule[9],path[8],s,t;
 thug_capsule_from_segment_draft(capsule,segment,sphere[4]);thug_segment_initialize(path);
 double dx=sub(sphere_velocity[0],segment_velocity[0]);float dy=(float)sub(sphere_velocity[1],segment_velocity[1]);
 float dz=(float)sub(sphere_velocity[2],segment_velocity[2]),dw=(float)sub(sphere_velocity[3],segment_velocity[3]);
 thug_vector_copy(path,sphere);path[4]=(float)add(dx,path[0]);path[5]=(float)add(dy,path[1]);path[6]=(float)add(dz,path[2]);path[7]=(float)add(dw,path[3]);
 if(!thug_capsule_segment_draft(capsule,path,&s,&t,0))return 0;
 if(s>=0&&s<=1)*count=t>=0&&t<=1?2:1;
 else if(t>=0&&t<=1){*count=1;s=t;}
 *time=s;if(*count==2&&t<s)*time=t;
 double mx=add(mul(*time,sphere_velocity[0]),sphere[0]);
 double my=add((float)mul(*time,sphere_velocity[1]),sphere[1]);
 double mz=add((float)mul(*time,sphere_velocity[2]),sphere[2]);
 float moved[4],delta[4];
 for(unsigned i=0;i<4;i++){double product=mul(*time,segment_velocity[i]);if(i)product=(float)product;moved[i]=(float)add(product,segment[i]);}
 for(unsigned i=0;i<4;i++)delta[i]=(float)sub(segment[i+4],segment[i]);
 float lo=(float)dot(delta,moved,2,1,0),hi=(float)add(dot(delta,delta,2,1,0),lo);
 float center=(float)add(add(mul(delta[2],mz),mul(delta[1],my)),mul(delta[0],mx));
 if(center<lo)thug_vector_copy(points,moved);
 else{
  float offset[4];if(center>hi)thug_vector_copy(offset,delta);
  else thug_vector_scaled(offset,(float)divi(sub(center,lo),sub(hi,lo)),delta);
  float result[4];thug_vector_sum(result,moved,offset);
  points[2]=result[2];points[3]=result[3];points[0]=result[0];points[1]=result[1];
 }
 *count=1;return 1;
}
/* 0040e940. Select the adjacent triangle edge at a known vertex and test its
 * relative motion. vertex must equal one of a/b/c, as all original callers do.
 * The initial inside-sphere failure clears time; approach failures retain it. */
uint32_t thug_sphere_vertex_edge_draft(const float vertex[4],const float sphere[5],const float sphere_velocity[4],const float edge_velocity[4],const float a[4],const float b[4],const float c[4],const float side[4],const float edge[4],float *time,float maximum,uint32_t *count,float point[4]){
 float relative[3];for(unsigned i=0;i<3;i++)relative[i]=(float)sub(vertex[i],sphere[i]);
 if(mul(sphere[4],sphere[4])>dot(relative,relative,2,0,1)){*time=0;return 0;}
 float dx=(float)sub(sphere_velocity[0],edge_velocity[0]);double dy=sub(sphere_velocity[1],edge_velocity[1]),dz=sub(sphere_velocity[2],edge_velocity[2]);float dzf=(float)dz;
 if(add(add(mul(dz,relative[2]),mul(dy,relative[1])),mul(dx,relative[0]))<=0)return 0;
 double vplane=dot(side,vertex,2,0,1),splane=dot(side,sphere,2,1,0);
 double denominator=add(add(mul(dy,side[1]),mul(dzf,side[2])),mul(dx,side[0]));
 if(denominator==0)denominator=0.009999999776482582f;
 double ratio=divi(sub(vplane,splane),denominator);
 double x=add(mul(dx,ratio),sphere[0]),y=add((float)mul(dy,ratio),sphere[1]),z=add((float)mul(dzf,ratio),sphere[2]);
 float vertex_projection=(float)dot(edge,vertex,2,0,1);
 float center_projection=(float)add(add(mul(x,edge[0]),mul(z,edge[2])),mul(y,edge[1]));
 float segment[8];thug_segment_initialize(segment);
 if(center_projection>=vertex_projection){
  thug_vector_copy(segment,vertex);
  if(thug_vector_equal(vertex,a))thug_vector_copy(segment+4,b);
  else if(thug_vector_equal(vertex,b))thug_vector_copy(segment+4,c);
  else if(thug_vector_equal(vertex,c))thug_vector_copy(segment+4,a);
 }else{
  if(thug_vector_equal(vertex,a))thug_vector_copy(segment,c);
  else if(thug_vector_equal(vertex,b))thug_vector_copy(segment,a);
  else if(thug_vector_equal(vertex,c))thug_vector_copy(segment,b);
  thug_vector_copy(segment+4,vertex);
 }
 float points[8];thug_array_construct_draft(points,16,2,thug_segment_initialize);
 if(!thug_moving_segment_sphere_draft(segment,edge_velocity,sphere,sphere_velocity,time,maximum,count,points))return 0;
 thug_vector_copy(point,points);return 1;
}
static void side_normal(float out[4],const float edge[4],const float normal[4]){
 out[0]=(float)sub(mul(edge[2],normal[1]),mul(edge[1],normal[2]));
 out[1]=(float)sub(mul(edge[0],normal[2]),mul(edge[2],normal[0]));
 out[2]=(float)sub(mul(edge[1],normal[0]),mul(edge[0],normal[1]));out[3]=0;
}
/* 0040ec90. Complete original swept sphere/triangle routine: plane and region
 * selection, edge and vertex contacts, closest-point capsule fallback, timing,
 * normal/output side effects and actual recovered callees. */
uint32_t thug_swept_sphere_triangle_draft(const float sphere[5],const float a[4],const float b[4],const float c[4],float *time,float maximum,const float velocity[4],float point[4],float normal[4]){
 float ab[4],bc[4],ca[4];thug_vector_difference(ab,b,a);thug_vector_difference(bc,c,b);thug_vector_difference(ca,a,c);
 double fx=sub(c[0],a[0]),fy=sub(c[1],a[1]),fz=sub(c[2],a[2]);
 float ex=(float)sub(b[0],a[0]),ey=(float)sub(b[1],a[1]);double ez=sub(b[2],a[2]);
 float nx=(float)sub(mul(ey,fz),mul(ez,fy)),ny=(float)sub(mul(ez,fx),mul(fz,ex));
 double nz=sub(mul(fy,ex),mul(ey,fx));normal[0]=nx;normal[1]=ny;normal[2]=(float)nz;normal[3]=0;
 double length2=add(add(mul(nz,nz),mul(ny,ny)),mul(nx,nx));if(length2<=0)return 0;
 float sphere_plane=(float)dot(normal,sphere,2,0,1),radius_plane2=(float)mul(mul(sphere[4],sphere[4]),length2);
 float triangle_plane=(float)dot(normal,a,2,1,0),plane_distance=(float)sub(sphere_plane,triangle_plane);
 float segment[8];thug_segment_initialize(segment);float zero[4]={0,0,0,1},side_ab[4],side_bc[4],side_ca[4];
 side_normal(side_ab,ab,normal);side_normal(side_bc,bc,normal);side_normal(side_ca,ca,normal);thug_vector_normalize(normal);
 const float *edge_a=0,*edge_b=0,*corner=0,*corner_side=0,*corner_edge=0;uint32_t count=0;
 if(mul(plane_distance,plane_distance)>radius_plane2){
  uint32_t ia=dot(side_ab,a,1,2,0)<=dot(side_ab,sphere,2,0,1);
  uint32_t ib=dot(side_bc,b,2,0,1)<=dot(side_bc,sphere,2,0,1);
  uint32_t ic=dot(side_ca,c,0,2,1)<=dot(side_ca,sphere,2,0,1);
  if(ia&&ib&&ic){
   float s,t,delta[4],scaled_c[4],scaled_b[4],temp[4],sum[4],capsule[9];
   thug_triangle_distance_squared_draft(sphere,a,b,c,&s,&t);
   thug_vector_difference(delta,c,a);thug_vector_scaled(scaled_c,t,delta);
   thug_vector_difference(delta,b,a);thug_vector_scaled(scaled_b,s,delta);
   thug_vector_sum(temp,a,scaled_b);thug_vector_sum(sum,temp,scaled_c);thug_vector_copy(point,sum);
   thug_capsule_from_delta_draft(capsule,sphere,velocity,sphere[4]);return thug_capsule_point_draft(capsule,point,0);
  }
  if(ia&&ib){edge_a=c;edge_b=a;}
  else if(ia&&ic){edge_a=b;edge_b=c;}
  else if(ib&&ic){edge_a=a;edge_b=b;}
  else if(ia){corner=c;corner_side=side_ca;corner_edge=ca;}
  else if(ib){corner=a;corner_side=side_ab;corner_edge=ab;}
  else if(ic){corner=b;corner_side=side_bc;corner_edge=bc;}
  else return 0;
  if(corner)return thug_sphere_vertex_edge_draft(corner,sphere,velocity,zero,a,b,c,corner_side,corner_edge,time,maximum,&count,point);
 }else{
  float motion[4]={velocity[0],velocity[1],velocity[2],(float)sub(velocity[3],1)};
  double speed_wide=dot(motion,normal,0,2,1);float speed=(float)speed_wide;
  if(sphere_plane>triangle_plane){if(speed_wide>=0)return 0;}
  else if(speed_wide<=0)return 0;
  float radius_offset[4],surface[4];thug_vector_scaled(radius_offset,sphere[4],normal);thug_vector_difference(surface,sphere,radius_offset);
  float contact_time=(float)divi(sub(dot(normal,a,2,1,0),dot(normal,surface,0,2,1)),speed);
  float contact[4];for(unsigned i=0;i<4;i++){double product=mul(motion[i],contact_time);if(i)product=(float)product;contact[i]=(float)add(product,surface[i]);}
  uint32_t ia=dot(side_ab,a,1,2,0)<=dot(contact,side_ab,2,1,0);
  uint32_t ib=dot(side_bc,b,2,0,1)<=dot(contact,side_bc,2,1,0);
  uint32_t ic=dot(side_ca,c,0,2,1)<=dot(contact,side_ca,2,1,0);
  if(ia&&ib&&ic){
   if(contact_time>maximum)return 0;*time=contact_time;
   float scaled[4],sum[4];thug_vector_scaled(scaled,contact_time,zero);thug_vector_sum(sum,contact,scaled);thug_vector_copy(point,sum);return 1;
  }
  if(ia&&ib){edge_a=c;edge_b=a;}
  else if(ia&&ic){edge_a=b;edge_b=c;}
  else if(ib&&ic){edge_a=a;edge_b=b;}
  else if(ia)corner=c;else if(ib)corner=a;else if(ic)corner=b;else return 0;
  if(corner){
   if(!thug_sphere_relative_time_draft(corner,zero,sphere,velocity,time,maximum))return 0;
   float scaled[4],sum[4];thug_vector_scaled(scaled,*time,zero);thug_vector_sum(sum,corner,scaled);thug_vector_copy(point,sum);return 1;
  }
 }
 thug_vector_copy(segment,edge_a);thug_vector_copy(segment+4,edge_b);float points[8];
 if(!thug_moving_segment_sphere_draft(segment,zero,sphere,velocity,time,maximum,&count,points))return 0;
 thug_vector_copy(point,points);return 1;
}
