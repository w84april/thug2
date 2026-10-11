#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/core/random.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float *fp(void *p,unsigned o){return (float *)((char *)p+o);}
static double r(double x){return thug_platform_round_x87_single(x);}
/* 0052dac0 / 0049bb70: actual buffer/point class virtual methods. */
int32_t thug_particle_one_segment_draft(void *p){(void)p;return 1;}
int32_t thug_particle_four_colors_draft(void *p){(void)p;return 4;}
/* 004968b0 / 004968e0 / 00496910 / 00496940: raw stack words. */
void thug_particle_extents_draft(void *p,uint32_t x,uint32_t y,uint32_t z){put(p,0x98,x);put(p,0x9c,y);put(p,0xa0,z);}
void thug_particle_acceleration_draft(void *p,uint32_t x,uint32_t y,uint32_t z){put(p,0xa8,x);put(p,0xac,y);put(p,0xb0,z);}
void thug_particle_direction_draft(void *p,uint32_t x,uint32_t y,uint32_t z){put(p,0xd0,x);put(p,0xd4,y);put(p,0xd8,z);}
void thug_particle_angles_draft(void *p,uint32_t x,uint32_t y,uint32_t z){put(p,0xe0,x);put(p,0xe4,y);put(p,0xe8,z);}
/* 0041d9c0: x86 masks a variable shift count to five bits; enable uses one byte. */
void thug_particle_flag_draft(void *p,uint32_t bit,uint32_t enabled){uint32_t mask=1u<<(bit&31);put(p,0x120,(uint8_t)enabled?word(p,0x120)|mask:word(p,0x120)&~mask);}
/* 004969f0. An explicit orientation overrides direction-derived axes. The
 * identity writes precede direction reads, preserving overlapping outputs. */
void thug_particle_basis_draft(void *p,float *out){
 void *matrix=ptr(p,0xdc);if(matrix){thug_matrix_copy(out,matrix);return;}
 for(unsigned i=0;i<16;i++)out[i]=i%5==0?1:0;
 out[12]=out[13]=out[14]=0;out[15]=1;
 uint32_t z=word(p,0xd8),y=word(p,0xd4),x=word(p,0xd0);
 put(out,36,y);put(out,32,x);put(out,40,z);out[11]=1;
 thug_vector_normalize(out+8);
 float up[4]={0,1,0,0};if(__builtin_fabs(out[9])>0x1.fae148p-1f){up[0]=1;up[1]=0;}
 thug_vector_cross(out,up,out+8);thug_vector_cross(out+4,out,out+8);
}
static double uniform(void){return r(thug_crt_random()*0x1.0002p-15f);}
static float signed_random(void){double u=uniform();return (float)r(r(u+u)-1);}
static int32_t segments(void *p){typedef int32_t (*Count)(void *);return ((Count *)ptr(p,0))[2](p);}
static void record_dimensions(void *p,uint32_t index){
 for(unsigned j=0;j<4;j++)put(ptr(p,0xf8),index*48+24+j*4,word(p,0xb4+j*4));
 if(word(p,0xc4)!=0x3f800000)for(unsigned j=0;j<4;j++){
  void *records=ptr(p,0xf8);*fp(records,index*48+24+j*4)=(float)r((double)*fp(records,index*48+24+j*4)**fp(p,0xc4));
 }
 put(ptr(p,0xf8),index*48+40,0);
 double u=uniform();*fp(ptr(p,0xf8),index*48+44)=(float)r(r(u*r((double)*fp(p,0xcc)-*fp(p,0xc8)))+*fp(p,0xc8));
}
/* 00496fe0. Complete emission, including frozen records, shared/separate random
 * vectors, elliptical distribution, previous-position spread and world space.
 * Float spills mirror the original x87 register/stack schedule. */
void thug_particle_emit_draft(void *p,uint32_t count){
 if(((uint8_t *)p)[0x125])return;
 uint32_t first=word(p,0x8c),end=first+count,capacity=word(p,0x7c);
 if((int32_t)end>(int32_t)capacity)end=capacity;put(p,0x8c,end);
 float basis[16];thug_particle_basis_draft(p,basis);
 for(uint32_t i=first;(int32_t)i<(int32_t)end;i++){
  if(!((uint8_t *)p)[0x12c]){
   record_dimensions(p,i);
   for(int32_t s=0;s<segments(p);s++)for(unsigned j=0;j<3;j++)put(ptr(p,0x11c),(word(p,0x7c)*(uint32_t)s+i)*12+j*4,0);
   continue;
  }
  float random[3]={signed_random(),signed_random(),signed_random()};
  double spread=r(r((double)*fp(p,0xa4)*.25)*0x1.921fb6p+1f);
  double dx=r(random[0]*spread),dy=r(spread*random[1]),dz=r(1-r(r(dy*dy)+r(dx*dx)));
  float zterm[3],yterm[3],xterm[2],direction[3],velocity[3];
  for(unsigned j=0;j<3;j++){zterm[j]=(float)r(basis[8+j]*dz);yterm[j]=(float)r(basis[4+j]*dy);}
  for(unsigned j=0;j<2;j++)xterm[j]=(float)r(basis[j]*dx);
  double px=r((double)xterm[0]+yterm[0]);float py=(float)r((double)xterm[1]+yterm[1]),pz=(float)r(r(basis[2]*dx)+yterm[2]);
  direction[0]=(float)r(px+zterm[0]);direction[1]=(float)r((double)py+zterm[1]);direction[2]=(float)r((double)pz+zterm[2]);
  double speed=r(r(uniform()*r((double)*fp(p,0x94)-*fp(p,0x90)))+*fp(p,0x90));
  for(unsigned j=0;j<3;j++)velocity[j]=(float)r(direction[j]*speed);
  if(((uint8_t *)p)[0x128])for(unsigned j=0;j<3;j++)random[j]=signed_random();
  if(((uint8_t *)p)[0x129]){
   double inverse=r(1/r(__builtin_sqrt(r(r((double)random[1]*random[1])+r((double)random[0]*random[0])))));
   for(unsigned j=0;j<2;j++)random[j]=(float)r(r(__builtin_fabs(random[j])*inverse)*random[j]);
  }
  dx=r((double)random[0]**fp(p,0x98));dy=r((double)random[1]**fp(p,0x9c));dz=r((double)random[2]**fp(p,0xa0));
  for(unsigned j=0;j<3;j++)zterm[j]=(float)r(basis[8+j]*dz);
  for(unsigned j=0;j<2;j++)yterm[j]=(float)r(basis[4+j]*dy);
  double yz=r(basis[6]*dy);float xz=(float)r(basis[2]*dx);
  float xy[2]={(float)r(r(basis[0]*dx)+yterm[0]),(float)r(r(basis[1]*dx)+yterm[1])};
  float position[3]={(float)r((double)xy[0]+zterm[0]),(float)r((double)xy[1]+zterm[1]),(float)r(r((double)xz+yz)+zterm[2])};
  if(((uint8_t *)p)[0x131]){
   float delta[3];for(unsigned j=0;j<3;j++)delta[j]=(float)r((double)*fp(p,0x30+j*4)-*fp(p,0x20+j*4));
   double distance=r(r(r((double)delta[2]*delta[2])+r((double)delta[1]*delta[1]))+r((double)delta[0]*delta[0]));
   if(distance!=0){double u=uniform(),weight=r(r(r(r(u+u)-1)+1)*.5);
    for(unsigned j=0;j<3;j++){double d=r(delta[j]*weight);if(j<2)d=(float)d;position[j]=(float)r(d+position[j]);}
   }
  }
  for(unsigned j=0;j<3;j++)put(ptr(p,0xf8),i*48+12+j*4,word(p,0xa8+j*4));
  record_dimensions(p,i);
  for(unsigned j=0;j<3;j++)*fp(ptr(p,0xf8),i*48+j*4)=velocity[j];
  for(int32_t s=0;s<segments(p);s++){
   float value[3];for(unsigned j=0;j<3;j++)value[j]=((uint8_t *)p)[0x126]?(float)r((double)position[j]+*fp(p,0x20+j*4)):position[j];
   for(unsigned j=0;j<3;j++)*fp(ptr(p,0x11c),(word(p,0x7c)*(uint32_t)s+i)*12+j*4)=value[j];
  }
 }
}

#include "../../src/collision/probe.h"
#include "../../src/core/line.h"
/* 00410980 / 00412230: collision-instance vertex virtuals used for lighting. */
float *thug_collision_static_vertex_draft(const ThugCollisionInstance *p,float *out,uint32_t index){
 float vertex[4];thug_collision_vertex(p->geometry,vertex,index);
 out[0]=vertex[0];put(out,4,word(vertex,4));put(out,8,word(vertex,8));out[3]=1;return out;
}
float *thug_collision_moving_vertex_draft(const ThugMovingCollisionInstance *p,float *out,uint32_t index){
 float vertex[4],rotated[4];thug_collision_vertex(p->base.geometry,vertex,index);vertex[3]=0;
 thug_matrix_rotate_vector(p->orientation,rotated,vertex);
 double x=r((double)rotated[0]+p->position[0]),y=r((double)rotated[1]+p->position[1]),z=r((double)rotated[2]+p->position[2]);
 float w=(float)r((double)rotated[3]+p->position[3]);out[3]=w;out[0]=(float)x;out[1]=(float)y;out[2]=(float)z;return out;
}
static uint32_t corner(const ThugCollisionObject *g,uint32_t face,unsigned i){
 if(g->small_faces)return ((const uint8_t *)g->faces)[face*8+4+i];
 uint16_t v;__builtin_memcpy(&v,(const char *)g->faces+face*10+4+2*i,2);return v;
}
static double length_difference(const float *a,const float *b,int spill){
 double x=r((double)a[0]-b[0]),y=r((double)a[1]-b[1]),z=r((double)a[2]-b[2]);
 double sum=r(r(r(z*z)+r(y*y))+r(x*x));if(spill)sum=(float)sum;
 return r(__builtin_sqrt(sum));
}
/* 004174a0. Interpolate the collision mesh's vertex-light bytes at the hit.
 * The original ignores the line-intersection return, requiring nondegenerate
 * hit geometry for defined results. A miss has the exact default value .5. */
double thug_collision_probe_light_draft(const ThugCollisionProbe *p){
 if(!p->result.hit)return .5;
 const ThugCollisionInstance *instance=p->result.instance;const ThugCollisionObject *g=instance->geometry;
 uint32_t face=p->result.surface.face;float hit[3]={p->result.surface.point[0],p->result.surface.point[1],p->result.surface.point[2]},vertices[3][4],light[3];
 for(unsigned i=0;i<3;i++){
  float vertex[4];typedef float *(*Vertex)(const void *,float *,uint32_t);
  ((Vertex *)(uintptr_t)instance->methods)[9](instance,vertex,corner(g,face,i));
  vertices[i][3]=1;for(unsigned j=0;j<3;j++)vertices[i][j]=(float)r((double)vertex[j]-hit[j]);
  light[i]=(float)r(g->vertex_aux[corner(g,face,i)]*0x1.010102p-8f);
 }
 float origin[4]={0,0,0,1},a[8],b[8],point_a[4],point_b[4],amount_a,amount_b;
 thug_collision_segment_copy(a,vertices[0],origin);thug_collision_segment_copy(b,vertices[1],vertices[2]);
 thug_segment_closest_points(a,b,point_a,point_b,&amount_a,&amount_b,0);
 double first=length_difference(point_a,vertices[1],1),second=length_difference(vertices[2],vertices[1],1);
 double from_zero=length_difference(vertices[0],origin,0),across=length_difference(point_a,vertices[0],0);
 double ratio=r(from_zero/across),edge=r(first/second);
 double value=r(r(r(r((double)light[2]-light[1])*edge)+light[1])-light[0]);
 return r(r(value*ratio)+light[0]);
}

#include "../../src/script/params.h"
static float parameter(const ThugScriptStructure *s,uint32_t key,float value){thug_script_get_float(s,key,&value,0);return value;}
static uint32_t integer(const ThugScriptStructure *s,uint32_t key,uint32_t value){thug_script_get_integer(s,key,&value,0);return value;}
static void command_vector(const ThugScriptStructure *s,uint32_t key,float out[4]){
 if(thug_script_get_vector(s,key,out,0))return;
 out[0]=parameter(s,0x7323e97c,0);out[1]=parameter(s,0x0424d9ea,0);out[2]=parameter(s,0x9d2d8850,0);
}
static int32_t colors(void *p){typedef int32_t (*Count)(void *);return ((Count *)ptr(p,0))[3](p);}
/* 00497b00. All particle script commands, including the real emitter and
 * collision/light query. The original BSP globals use the existing explicit
 * query context; script is an unused original argument. */
uint8_t thug_particle_command_draft(void *p,uint32_t name,const ThugScriptStructure *s,void *script,ThugCollisionQuery *query){
 (void)script;float a,b,c,d,v[4];uint32_t value;
 switch(name){
 case 0x8ffdef38:
  a=parameter(s,0x73e5bad0,0);b=parameter(s,0x0ab21af0,a);c=parameter(s,0x055ce396,0);
  thug_particle_extents_draft(p,word(&a,0),word(&b,0),word(&c,0));break;
 case 0x63274395:case 0xd3f1d333:
  a=parameter(s,0x5e84e22f,0);b=parameter(s,0x6289dd76,a);
  put(p,name==0x63274395?0x90:0xc8,word(&a,0));put(p,name==0x63274395?0x94:0xcc,word(&b,0));
  if(name==0xd3f1d333)((uint8_t *)p)[0x12c]=1;break;
 case 0x7911855b:a=parameter(s,0x834a5f87,0);put(p,0xa4,word(&a,0));break;
 case 0x35b65bd4:a=parameter(s,0x2013c0c6,1);put(p,0x70,word(&a,0));break;
 case 0x2e66815e:a=parameter(s,0x5b1d3822,1);put(p,0xc4,word(&a,0));break;
 case 0x2a479569:
  a=parameter(s,0x745523aa,0);b=parameter(s,0xf95d2e5f,a);put(p,0xb4,word(&a,0));put(p,0xb8,word(&b,0));
  c=a;d=thug_script_get_float(s,0x68cd967d,&c,0)?c:b;d=parameter(s,0xe5c59b88,d);
  put(p,0xbc,word(&c,0));put(p,0xc0,word(&d,0));break;
 case 0x099cd17b:
  command_vector(s,0x7f261953,v);for(unsigned i=0;i<3;i++)put(p,0x20+4*i,word(v,4*i));break;
 case 0xa075ee45:
  command_vector(s,0x68977cd7,v);thug_particle_acceleration_draft(p,word(v,0),word(v,4),word(v,8));break;
 case 0xb373fb6e:
  command_vector(s,0xb990d003,v);
  if(v[0]!=0||v[1]!=1||v[2]!=0)thug_particle_direction_draft(p,word(v,0),word(v,4),word(v,8));break;
 case 0x1cfbf078:
  command_vector(s,0xff7ebaf6,v);for(unsigned i=0;i<3;i++)v[i]=(float)r((double)v[i]*0x1.1df46ap-6f);
  thug_particle_angles_draft(p,word(v,0),word(v,4),word(v,8));break;
 case 0xe985a9a6:case 0xdb8621f7:
  value=(int32_t)integer(s,name==0xe985a9a6?0x9d2e07b3:0xe9c4252a,0)>0;
  thug_particle_flag_draft(p,name==0xe985a9a6?8:4,value);((uint8_t *)p)[name==0xe985a9a6?0x129:0x128]=(uint8_t)value;break;
 case 0xe3309ab5:((uint8_t *)p)[0x126]=integer(s,0,0)==1;break;
 case 0xfbb6720d:
  value=0;thug_script_get_boolean(s,0x6c4e18eb,&value,0);
  a=parameter(s,0x4eedfae7,0);b=parameter(s,0xd7e4ab5d,0);put(p,0x80,value);
  *fp(p,0x84)=(float)r((double)a*a);*fp(p,0x88)=(float)r((double)b*b);break;
 case 0x482482c6:put(p,0x8c,0);break;
 case 0x711b1a6a:thug_particle_emit_draft(p,integer(s,0x23bc5091,1));break;
 case 0x514b2584:{
  uint32_t index;int32_t first,last;
  if(thug_script_get_integer(s,0xfec1c2fb,&index,0))first=last=(int32_t)index;else{last=colors(p)-1;first=0;}
  static const uint32_t keys[3][4]={{0x18a762f2,0x757a8619,0x05107296,0x9c19232c},{0xd07ee8fa,0xbda30c11,0xcdc9f89e,0x54c0a924},{0x043fd725,0x69e233ce,0x1988c741,0x808196fb}};
  if(first<colors(p)&&last<colors(p))for(int32_t i=first;i<last+1;i++)if(i<colors(p)){
   for(unsigned group=0;group<3;group++)for(unsigned channel=0;channel<4;channel++)if(thug_script_get_integer(s,keys[group][channel],&value,0)){
    uint8_t byte=(uint8_t)value;if(channel==3)byte>>=1;
    unsigned offset=group==0?0x114:group==1?0x110:0x10c;
    ((uint8_t *)ptr(p,offset))[i*4+channel]=byte;
    if(group==0)((uint8_t *)p)[0x12d]=1;
    if(group==2&&!((uint8_t *)p)[0x12d])((uint8_t *)ptr(p,0x114))[i*4+channel]=byte;
   }
  }
  thug_script_get_float(s,0x856bc5e2,fp(p,0x108),0);break;
 }
 case 0x96896315:
  if(thug_script_has_flag(s,0x652f5d69))((uint8_t *)p)[0x132]=1;
  else{
   ((uint8_t *)p)[0x132]=0;ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
   for(unsigned i=0;i<4;i++)put(probe.segment,4*i,word(p,0x20+4*i));
   probe.segment[1]=(float)r((double)*fp(p,0x24)+1);
   for(unsigned i=0;i<4;i++)put(probe.segment,16+4*i,word(p,0x20+4*i));
   probe.segment[5]=(float)r((double)*fp(p,0x24)-4800);
   if(thug_collision_probe_query(&probe,1,0,query)){double light=thug_collision_probe_light_draft(&probe);*fp(p,0xec)=(float)r(light+light);}
   thug_collision_probe_release(&probe);
  }break;
 }
 return 1;
}
