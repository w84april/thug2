#include "../../src/game/components.h"
#include "../../src/script/values.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const char *)p+o,2);return v;}
static void put_half(void *p,unsigned o,uint16_t v){__builtin_memcpy((char *)p+o,&v,2);}
static double r(double x){return thug_platform_round_x87_single(x);}
/* 00403220. Only the embedded record's final word is initialized. */
void *thug_rigidbody_record_construct_draft(void *p){put(p,0x20,0);return p;}
void thug_rigidbody_finalize_draft(void *p);
/* Identity plus the recovered finalize slot. Initialization, update and
 * destruction remain unavailable until their original bodies are recovered. */
const uintptr_t thug_rigidbody_methods_draft[13]={[3]=(uintptr_t)thug_rigidbody_finalize_draft};
/* 0042e3f0. Unwritten words retain their incoming contents. */
void *thug_rigidbody_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)thug_rigidbody_methods_draft);thug_rigidbody_record_construct_draft((char *)p+0x64);
 const uint32_t fields[][2]={{4,0xffb39248},{0xf4,0},{0x130,0},{0x134,0},{0x138,0},{0x13c,0x3f800000},{0x1c,0},{0x24,0},{0x28,0x3f800000},{0x20,0xc3c13333},{0x50,0x3f800000},{0x54,0x3f800000},{0x18,0x3b449ba6},{0x2c,0x3ecccccd},{0x30,0x3f000000},{0x34,0x41200000},{0x58,0x42c80000},{0x5c,0x3e23d70b},{0x40,0x42400000},{0x44,0x41400000},{0xc0,0x3daaaaab},{0xb0,0},{0xb4,0},{0xb8,0},{0xbc,0x3f800000},{0xd0,0},{0xcc,0},{0xc8,0},{0xc4,0},{0xe0,1000},{0xe4,100},{0xe8,0x41a00000},{0xec,0x43960000},{0x108,0xbf800000}};
 for(unsigned i=0;i<sizeof(fields)/sizeof(fields[0]);i++)put(p,fields[i][0],fields[i][1]);
 /* Exact double at6463f0; existing libm adapter has no physical x87 claim. */
 *fp(p,0x48)=(float)thug_platform_cos(0.4363323251406352);*fp(p,0x4c)=(float)thug_platform_sin(0.4363323251406352);return p;
}
/* 0042ef00. */
void *thug_rigidbody_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1a0,m);return p?thug_rigidbody_construct_draft(p):0;}
/* 0042e1f0. Preserve the early destination store for overlapping operands,
 * and the positive-trace scale's explicit float32 spill. */
float *thug_matrix_quaternion_draft(float q[4],const float m[16]){
 double trace=r(r((double)m[5]+m[0])+m[10]);
 if(trace>0){double root=r(__builtin_sqrt(r(trace+1)));q[3]=(float)r(.5*root);float scale=(float)r(.5/root);
  double z=r(r((double)m[4]-m[1])*scale),y=r(r((double)m[2]-m[8])*scale),x=r(r((double)m[9]-m[6])*scale);q[0]=(float)x;q[1]=(float)y;q[2]=(float)z;
 }else{unsigned i=m[5]>m[0]?1:0;if(m[10]>m[i*5])i=2;unsigned j=(i+1)%3,k=(j+1)%3;
  double root=r(__builtin_sqrt(r(r((double)m[i*5]-r((double)m[k*5]+m[j*5]))+1)));q[i]=(float)r(.5*root);double scale=r(.5/root);
  q[j]=(float)r(r((double)m[i+j*4]+m[j+i*4])*scale);q[k]=(float)r(r((double)m[i+k*4]+m[k+i*4])*scale);q[3]=(float)r(r((double)m[j+k*4]-m[k+j*4])*scale);
 }return q;
}
/* 0042e310. PC24 arithmetic retains wider exponents until final stores. */
float *thug_quaternion_scale_length_draft(float q[4],float length){
 double norm=r(__builtin_sqrt(r(r(r(r((double)q[0]*q[0])+r((double)q[1]*q[1]))+r((double)q[2]*q[2]))+r((double)q[3]*q[3]))));
 if(norm>0){double scale=r((double)length/norm);for(unsigned i=0;i<4;i++)q[i]=(float)r(scale*q[i]);}return q;
}
/* 0041a730. Identity is written before any input read, including aliases. */
float *thug_matrix_euler_draft(float out[16],const float angles[4]){
 for(unsigned i=0;i<16;i++)out[i]=i%5==0?1:0;
 if(angles[0]!=0||angles[1]!=0||angles[2]!=0){float v[16];thug_matrix_rotation_x(v,angles[0]);thug_matrix_multiply(out,out,v);thug_matrix_rotation_y(v,angles[1]);thug_matrix_multiply(out,out,v);thug_matrix_rotation_z(v,angles[2]);thug_matrix_multiply(out,out,v);}return out;
}
static void allocate_points(void *p,uint16_t n,const ThugMemory *m){put_half(p,0x8c,n);void *old=pointer(p,0x60);if(old)m->release(m->context,old);put(p,0x60,(uintptr_t)m->allocate(m->context,(uint32_t)half(p,0x8c)*16,1));}
/* 0042d4b0. Array count truncates to sixteen bits before allocation. */
void thug_rigidbody_points_draft(void *p,ThugScriptArray *a,const ThugMemory *m){
 allocate_points(p,(uint16_t)a->count,m);uint32_t *items=thug_script_array_items(a);
 for(unsigned i=0;i<half(p,0x8c);i++){void *v=(void *)(uintptr_t)items[i],*out=(char *)pointer(p,0x60)+i*16;for(unsigned j=0;j<3;j++)put(out,j*4,word(v,4+j*4));put(out,12,0);}
}
/* 0042d560. Eight vertices, ordered X side, Y side, then Z side. */
void thug_rigidbody_box_draft(void *p,const float top[4],const float bottom[4],const ThugMemory *m){
 allocate_points(p,8,m);unsigned i=0;
 for(unsigned x=0;x<2;x++)for(unsigned y=0;y<2;y++)for(unsigned z=0;z<2;z++,i++){
  float *v=(float *)pointer(p,0x60)+i*4;v[0]=(float)r((double)(y?top[0]:bottom[0])*(x?1:-1));v[1]=y?top[1]:-bottom[1];v[2]=(float)r((double)(y?top[2]:bottom[2])*(z?1:-1));v[3]=1;
 }
}
/* 0042d690. */
void thug_rigidbody_pyramid_draft(void *p,float height,float radius,const ThugMemory *m){
 allocate_points(p,5,m);float y=(float)r((double)height*-0.6000000238418579);float *v=pointer(p,0x60);
 for(unsigned i=0;i<4;i++){v[i*4]=(i==1||i==2)?-radius:radius;v[i*4+1]=y;v[i*4+2]=i<2?radius:-radius;v[i*4+3]=1;}
 v[16]=0;v[17]=(float)r((double)height*1.600000023841858);v[18]=0;v[19]=1;
}
/* 0042d790. Count is an internal nonnegative capacity-safe polygon count.
 * Cosine consumes the wide PC24 angle; sine consumes its float32 spill. */
void thug_rigidbody_cylinder_draft(void *p,float top,float bottom,float height,int32_t count,const ThugMemory *m){
 allocate_points(p,(uint16_t)((uint32_t)count*2),m);unsigned out=0;
 for(unsigned side=0;side<2;side++)for(int32_t i=count;i;){--i;double angle=r(r((double)i*6.2829999923706055)/count);float *v=(float *)pointer(p,0x60)+out++*4;
  v[0]=(float)r(thug_platform_cos(angle)*(side?top:bottom));v[1]=side?height:-height;v[2]=(float)r(thug_platform_sin((float)angle)*(side?top:bottom));v[3]=1;
 }
}
/* 0042d8a0. Two triangular end faces. */
void thug_rigidbody_prism_draft(void *p,const float size[4],const ThugMemory *m){
 allocate_points(p,6,m);unsigned i=0;
 for(unsigned side=0;side<2;side++)for(unsigned corner=0;corner<3;corner++,i++){float *v=(float *)pointer(p,0x60)+i*4;v[0]=corner==2?0:corner==1?-size[0]:size[0];v[1]=corner==2?size[1]:-size[1];v[2]=(float)r((side?-1.:1.)*size[2]);v[3]=1;}
}
/* 0042ed60. Named radius and unnamed position use the actual QB getters. */
void thug_rigidbody_spheres_draft(void *p,ThugScriptArray *a,const ThugMemory *m){
 put_half(p,0x94,(uint16_t)a->count);void *old=pointer(p,0x90);if(old)m->release(m->context,old);put(p,0x90,(uintptr_t)m->allocate(m->context,(uint32_t)half(p,0x94)*20,1));uint32_t *items=thug_script_array_items(a);
 for(unsigned i=0;i<half(p,0x94);i++){const ThugScriptStructure *s=(void *)(uintptr_t)items[i];float *v=(float *)pointer(p,0x90)+i*5;thug_script_get_vector(s,0,v,1);thug_script_get_float(s,0xc48391a5,v+4,1);}
}
/* 0042eb10. Optional sound settings own deep copies and preserve omissions. */
void thug_rigidbody_sound_profile_draft(void *p,uint32_t name,const ThugMemory *m){
 const ThugScriptStructure *profiles=thug_script_get_global_structure(0xb9738eba,1);ThugScriptStructure *s=0;thug_script_get_structure(profiles,name,&s,0);
 const uint32_t keys[2]={0xbf8e0ace,0x1fb2f60c};
 for(unsigned i=0;i<2;i++)if(thug_script_has_name_or_flag(s,keys[i])){
  ThugScriptStructure *value;thug_script_get_structure(s,keys[i],&value,1);unsigned offset=0xd8+i*4;ThugScriptStructure *old=pointer(p,offset);
  if(old){thug_script_structure_destroy(old,m);thug_script_structure_free(old,m);}ThugScriptStructure *copy=thug_script_structure_allocate(8,m);if(copy)thug_script_structure_initialize(copy);put(p,offset,(uintptr_t)copy);thug_script_structure_merge(copy,value,m);
  if(i){uint32_t n;if(thug_script_has_name_or_flag(s,0x3818ee47)){thug_script_get_integer(s,0x3818ee47,&n,0);put(p,0xe0,n);}if(thug_script_has_name_or_flag(s,0xad67a34d)){thug_script_get_integer(s,0xad67a34d,&n,0);put(p,0xe4,n);}thug_script_get_float(s,0x4511ca8d,fp(p,0xe8),0);thug_script_get_float(s,0x8fc6519f,fp(p,0xec),0);}
 }
}
/* 0042bd90. Y/Z rotate results spill before translation; X stays in x87. */
void thug_rigidbody_finalize_draft(void *p){
 put(p,0x19c,(uintptr_t)thug_object_find_component(pointer(p,12),0x07713c7b));
 for(unsigned i=0;i<half(p,0x9c);i++){float *v=fp(pointer(p,0x98),i*36);double x=r(r(r((double)v[1]**fp(p,0x160))+r((double)v[0]**fp(p,0x150)))+r((double)v[2]**fp(p,0x170)));
  float y=(float)r(r(r((double)v[0]**fp(p,0x154))+r((double)*fp(p,0x174)*v[2]))+r((double)v[1]**fp(p,0x164)));
  float z=(float)r(r(r((double)v[0]**fp(p,0x158))+r((double)*fp(p,0x178)*v[2]))+r((double)*fp(p,0x168)*v[1]));
  float tx=(float)r(x+*fp(p,0x110)),ty=(float)r((double)y+*fp(p,0x114)),tz=(float)r((double)z+*fp(p,0x118)),tw=(float)r((double)v[3]+*fp(p,0x11c));v[6]=tz;v[7]=tw;v[4]=tx;v[5]=ty;
 }
}
