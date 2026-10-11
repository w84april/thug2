#include "../../src/script/schedule.h"
#include "../../src/script/execute.h"
#include "../../src/core/vector.h"
/* Included after the Rigidbody core. Original fixed scratch capacities;
 * callers provide disjoint internal shape arrays and at most 24/24/2 entries. */
float thug_rigidbody_rotated_points_draft[24][4]; /* 00694e30 */
float thug_rigidbody_rotated_spheres_draft[24][4]; /* 00694fb0 */
float thug_rigidbody_rotated_contacts_draft[2][4]; /* 00695130 */
/* 0042be90. The attached script executes before the motion state is reset. */
void thug_rigidbody_stop_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 if(word(p,0xcc))thug_script_execute(thug_object_spawn_attached_script(pointer(p,12),word(p,0xcc),pointer(p,0xd4),0,0,d,m),d,m);
 for(unsigned j=0;j<4;j++){put(p,0x120+4*j,j==3?0x3f800000:0);put(p,0x140+4*j,j==3?0x3f800000:0);}put(p,0x10c,0);
}
static void rotate_scratch(void *p,unsigned integrated){
 const unsigned ptrs[]={0x60,0x90,0x98},counts[]={0x8c,0x94,0x9c},strides[]={16,20,36};
 float (*destinations[])[4]={thug_rigidbody_rotated_points_draft,thug_rigidbody_rotated_spheres_draft,thug_rigidbody_rotated_contacts_draft};
 float *matrix=fp(p,0x150);
 for(unsigned kind=0;kind<3;kind++)for(unsigned i=half(p,counts[kind]);i;){
  --i;float *v=fp(pointer(p,ptrs[kind]),i*strides[kind]);if(kind==2&&!((uint8_t *)v)[32])continue;
  double out[3];for(unsigned axis=0;axis<3;axis++){
   double x=r((double)v[0]*matrix[axis]),y=r((double)v[1]*matrix[axis+4]),z=r((double)v[2]*matrix[axis+8]);
   if(kind==2)out[axis]=r(r(z+y)+x);
   else if(axis==0)out[axis]=r(r(y+z)+x);
   else if(axis==1)out[axis]=r(r(x+z)+y);
   else if(!kind)out[axis]=r(r(z+y)+x);
   else out[axis]=r((integrated?r(z+x):r(x+z))+y);
  }
  float *outv=destinations[kind][i];uint32_t w=word(v,12);outv[2]=(float)out[2];outv[0]=(float)out[0];put(outv,12,w);outv[1]=(float)out[1];
 }
}
/* 0042bf00. Inactive contacts leave the corresponding scratch entry intact. */
void thug_rigidbody_rotate_draft(void *p){rotate_scratch(p,0);}
static double motion_length_squared(const float *v){return r(r(r((double)v[0]*v[0])+r((double)v[1]*v[1]))+r((double)v[2]*v[2]));}
/* 0042c6d0. Exact equality clamps, including the homogeneous lane. */
void thug_rigidbody_friction_draft(void *p){
 for(unsigned kind=0;kind<2;kind++){
  float threshold=*fp(p,0x38+4*kind),*v=fp(p,0x120+32*kind);if(threshold==0)continue;
  double length=r(__builtin_sqrt(motion_length_squared(v)));
  if(length<=threshold){v[0]=v[1]=v[2]=0;v[3]=1;continue;}
  double factor=-r((double)threshold/length),products[4];
  for(unsigned j=0;j<4;j++){products[j]=r(factor*v[j]);if(j)products[j]=(float)products[j];}
  for(unsigned j=0;j<4;j++)v[j]=(float)r(products[j]+v[j]);
 }
}
/* 0042c890. Contact count is a signed byte; stop may run real script code. */
void thug_rigidbody_settle_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 if(((int8_t *)p)[0x191]<3||motion_length_squared(fp(p,0x120))>*fp(p,0x58)||motion_length_squared(fp(p,0x140))>*fp(p,0x5c))return;
 thug_rigidbody_stop_draft(p,d,m);
 if(((uint8_t *)p)[0xf4]&1)if(!(thug_vector_distance_squared(fp(p,0x110),fp(p,0xf8))<2304.0))put(p,0x108,0x3fc00000);
}
/* 0042e540. Integrate one collision-selected substep. x87 PC24 values retain
 * wide exponents except at the original float32 spills. */
void thug_rigidbody_integrate_draft(void *p,float dt){
 float *position=fp(p,0x110),*velocity=fp(p,0x120),*gravity=fp(p,0x1c);double delta[4];
 if(((int8_t *)p)[0x191]<3){
  double halfdt=r((double)dt*.5),middle[4];
  for(unsigned j=0;j<4;j++){double product=r(halfdt*gravity[j]);if(j)product=(float)product;middle[j]=r(product+velocity[j]);if(j==0||j==3)middle[j]=(float)middle[j];}
  for(unsigned j=0;j<4;j++){delta[j]=r(middle[j]*dt);if(j<2)delta[j]=(float)delta[j];}
  for(unsigned j=0;j<4;j++)position[j]=(float)r(delta[j]+position[j]);
  for(unsigned j=0;j<4;j++){double product=r((double)dt*gravity[j]);if(j>=2)product=(float)product;velocity[j]=(float)r(product+velocity[j]);}
 }else{
  for(unsigned j=0;j<4;j++){delta[j]=r((double)dt*velocity[j]);if(j>=2)delta[j]=(float)delta[j];}
  for(unsigned j=0;j<4;j++)position[j]=(float)r(delta[j]+position[j]);
 }
 float q[4],omega[4];for(unsigned j=0;j<4;j++){q[j]=*fp(p,0x130+4*j);omega[j]=j==3?0:(float)r((double)*fp(p,0x140+4*j)*-.5);}
 thug_quaternion_multiply(q,omega);
 for(unsigned j=0;j<4;j++){double product=r((double)q[j]*dt);if(j>=2)product=(float)product;*fp(p,0x130+4*j)=(float)r(product+*fp(p,0x130+4*j));}
 thug_quaternion_scale_length_draft(fp(p,0x130),1);thug_quaternion_basis_draft(fp(p,0x130),fp(p,0x150));rotate_scratch(p,1);
}
/* 0042ef60. Release order and surviving pointer fields match the executable. */
void thug_rigidbody_destroy_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)&thug_rigidbody_methods_draft);
 const unsigned buffers[]={0x60,0x88,0x90,0x98},structures[]={0xd4,0xdc,0xd8};
 for(unsigned i=0;i<4;i++){void *v=pointer(p,buffers[i]);if(v)m->release(m->context,v);}
 for(unsigned i=0;i<3;i++){ThugScriptStructure *v=pointer(p,structures[i]);if(v){thug_script_structure_destroy(v,m);thug_script_structure_free(v,m);}}
 thug_component_destroy(p);
}
/* 00430df0. */
void *thug_rigidbody_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_rigidbody_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;}
