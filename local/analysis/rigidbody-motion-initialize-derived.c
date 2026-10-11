#include "../../src/game/nodes.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/script/delivery.h"
#include "../../src/core/checksum.h"
#include "../../src/core/line.h"
/* Included after the preserved core definitions in the derived translation unit. */
void thug_quaternion_basis_draft(const float *,float *);
uint32_t thug_rigidbody_initialization_constant_draft; /* 006939d0 */
/* 00477010. The text overload uses the game's normalized checksum routine. */
uint8_t thug_script_get_vector_text_draft(const ThugScriptStructure *s,const char *name,float out[4],uint32_t required){
 return thug_script_get_vector(s,thug_crc32_string(name),out,required);
}
static double length_squared(const float *v){return r(r(r((double)v[2]*v[2])+r((double)v[0]*v[0]))+r((double)v[1]*v[1]));}
/* 0042f050. Initialized successful heap and valid internal parameter graphs.
 * Preserve reverse traversal, x87 PC24 operations and the original float spills. */
void thug_rigidbody_initialize_draft(void *p,const ThugScriptStructure *s,const ThugMemory *m){
 uint32_t mode;put(p,0x10c,0);
 if(thug_script_get_checksum(s,0x61fbb62c,&mode,0)){
  if(mode==0x4484b712)put(p,0x10c,0);else if(mode==0x7b01911c)put(p,0x10c,2);else if(mode==0x99a34896)put(p,0x10c,1);
 }
 for(unsigned i=0;i<4;i++){put(p,0x120+i*4,i==3?0x3f800000:0);put(p,0x140+i*4,i==3?0x3f800000:0);}
 for(unsigned i=0;i<16;i++)put(p,0x150+i*4,i%5==0?0x3f800000:0);
 void *owner=pointer(p,12);for(unsigned i=0;i<4;i++)put(p,0x110+i*4,word(owner,0x4c+i*4));
 float q[4];thug_matrix_quaternion_draft(q,fp(owner,0x6c));for(unsigned i=0;i<4;i++)put(p,0x130+i*4,word(q,i*4));
 thug_quaternion_scale_length_draft(fp(p,0x130),1);thug_quaternion_basis_draft(fp(p,0x130),fp(p,0x150));
 thug_script_get_vector(s,0x0c4c809e,fp(p,0x120),0);thug_script_get_vector(s,0xfb1a83b2,fp(p,0x140),0);thug_script_get_vector(s,0x737612c6,fp(p,0xa0),0);
 if(!thug_script_get_float(s,0x6fae5c9a,fp(p,0x20),0))thug_script_get_vector(s,0x6fae5c9a,fp(p,0x1c),0);
 const uint32_t first[][2]={{0x60b4860d,0x2c},{0xf9d75930,0x30},{0xf1ecb30f,0x34},{0xde76c3a7,0x38},{0x9da897cf,0x3c}};
 for(unsigned i=0;i<5;i++)thug_script_get_float(s,first[i][0],fp(p,first[i][1]),0);
 const uint32_t squared[][2]={{0xc11e4dd8,0x58},{0xa457ece3,0x5c}};
 for(unsigned i=0;i<2;i++)if(thug_script_has_name_or_flag(s,squared[i][0])){float *v=fp(p,squared[i][1]);thug_script_get_float(s,squared[i][0],v,0);*v=(float)r((double)*v**v);}
 const uint32_t second[][2]={{0x3390d1e5,0x50},{0x5a18f61f,0x54},{0x85f112c1,0x40},{0x8ab2db68,0x44}};
 for(unsigned i=0;i<4;i++)thug_script_get_float(s,second[i][0],fp(p,second[i][1]),0);
 if(thug_script_has_name_or_flag(s,0xe9156e6d)){float degrees;thug_script_get_float(s,0xe9156e6d,&degrees,0);double angle=r((double)degrees*0.01745329238474369);*fp(p,0x48)=(float)thug_platform_cos(angle);*fp(p,0x4c)=(float)thug_platform_sin(angle);}
 thug_script_get_float(s,0x1f4d0ca5,fp(p,0xc0),0);
 const uint32_t checksums[]={0x58cdc0f0,0x2d075f90,0x571917fa,0xccb84047};
 for(unsigned i=0;i<4;i++)thug_script_get_checksum(s,checksums[i],(uint32_t *)fp(p,0xc4+4*i),0);
 if(thug_script_has_name_or_flag(s,0x0dd85bda)){
  ThugScriptStructure *value;thug_script_get_structure(s,0x0dd85bda,&value,1);ThugScriptStructure *copy=thug_script_structure_allocate(8,m);
  if(copy)thug_script_structure_initialize(copy);put(p,0xd4,(uintptr_t)copy);thug_script_structure_merge(copy,value,m);
 }
 if(thug_script_has_name_or_flag(s,0x94956e48)){uint32_t name;thug_script_get_checksum(s,0x94956e48,&name,1);thug_rigidbody_sound_profile_draft(p,name,m);}
 put(p,0xf4,thug_script_has_flag(s,0x5e51924f)?word(p,0xf4)|1:word(p,0xf4)&~1u);
 if(thug_script_has_name_or_flag(s,0xb77be94a)){
  ThugScriptArray *a;thug_script_get_array(s,0xb77be94a,&a,1);put_half(p,0x9c,(uint16_t)a->count);void *old=pointer(p,0x98);if(old)m->release(m->context,old);
  void *records=m->allocate(m->context,(uint32_t)half(p,0x9c)*36,1);if(records)for(unsigned i=0;i<half(p,0x9c);i++)thug_segment_initialize((char *)records+i*36);put(p,0x98,(uintptr_t)records);
  uint32_t *items=thug_script_array_items(a);
  for(unsigned i=0;i<half(p,0x9c);i++){void *v=(void *)(uintptr_t)items[i],*out=(char *)pointer(p,0x98)+i*36;for(unsigned j=0;j<3;j++)put(out,4*j,word(v,4+4*j));put(out,12,0);((uint8_t *)out)[32]=1;}
 }
 unsigned shape=half(p,0x8c)?4:0;
 if(thug_script_has_name_or_flag(s,0xccbfea8c)){ThugScriptArray *a;thug_script_get_array(s,0xccbfea8c,&a,0);thug_rigidbody_points_draft(p,a,m);shape=4;}
 if(thug_script_has_name_or_flag(s,0x5b6a8d18)){ThugScriptArray *a;thug_script_get_array(s,0x5b6a8d18,&a,0);thug_rigidbody_spheres_draft(p,a,m);shape=4;}
 if(thug_script_has_flag(s,0xf756b7c5))shape=0;else if(thug_script_has_flag(s,0x1cb1a2b6))shape=1;else if(thug_script_has_flag(s,0x64fba415))shape=2;else if(thug_script_has_flag(s,0x20689278))shape=3;
 switch(shape){
 case 0:{float top[4]={32,32,16,1},bottom[4];thug_script_get_vector_text_draft(s,"dimensions",top,0);__builtin_memcpy(bottom,top,16);thug_script_get_vector_text_draft(s,"top_dimensions",top,0);thug_script_get_vector_text_draft(s,"bottom_dimensions",bottom,0);for(unsigned i=0;i<4;i++){top[i]=(float)r((double)top[i]*.5);bottom[i]=(float)r((double)bottom[i]*.5);}thug_rigidbody_box_draft(p,top,bottom,m);break;}
 case 1:{float height=42,width=32;thug_script_get_float(s,0x0ab21af0,&height,0);thug_script_get_float(s,0x055ce396,&width,0);thug_rigidbody_pyramid_draft(p,(float)r((double)height*.5),(float)r((double)width*.5),m);break;}
 case 2:{float top=12,bottom,height=60;uint32_t count=6;thug_script_get_float(s,0xc48391a5,&top,0);bottom=top;thug_script_get_float(s,0x937e3b29,&top,0);thug_script_get_float(s,0xe2ac8c3a,&bottom,0);thug_script_get_float(s,0x0ab21af0,&height,0);thug_script_get_integer(s,0x4055f24a,&count,0);thug_rigidbody_cylinder_draft(p,top,bottom,(float)r((double)height*.5),(int32_t)count,m);break;}
 case 3:{float size[4]={32,32,16,1};thug_script_get_vector(s,0x1d82745a,size,0);for(unsigned i=0;i<4;i++)size[i]=(float)r((double)size[i]*.5);thug_rigidbody_prism_draft(p,size,m);break;}
 }
 if(thug_script_has_name_or_flag(s,0xc35cac0d)){
  ThugScriptArray *a;thug_script_get_array(s,0xc35cac0d,&a,0);void *old=pointer(p,0x88);if(old)m->release(m->context,old);put(p,0x88,(uintptr_t)m->allocate(m->context,(uint32_t)half(p,0x8c)*20,1));uint32_t *items=thug_script_array_items(a);
  for(unsigned i=half(p,0x8c);i;){--i;const ThugScriptStructure *entry=(void *)(uintptr_t)items[i];uint8_t *out=(uint8_t *)pointer(p,0x88)+i*20;
   if(thug_script_has_name_or_flag(entry,0x806fff30))out[16]=0;else{out[16]=1;thug_script_get_vector(entry,0,(float *)out,1);}}
 }
 if(thug_script_has_name_or_flag(s,0x9d2d0915)){
  float angles[4],matrix[16];thug_node_angles(s,angles);thug_matrix_euler_draft(matrix,angles);
  for(unsigned kind=0;kind<2;kind++)for(unsigned i=half(p,kind?0x94:0x8c);i;){--i;float *v=fp(pointer(p,kind?0x90:0x60),i*(kind?20:16));double rotated[3];
   for(unsigned axis=0;axis<3;axis++){double x=r((double)matrix[axis]*v[0]),y=r((double)matrix[4+axis]*v[1]),z=r((double)matrix[8+axis]*v[2]);rotated[axis]=kind?r(r(y+z)+x):r(r(x+y)+z);}
   v[2]=(float)rotated[2];v[0]=(float)rotated[0];v[1]=(float)rotated[1];
  }
 }
 float center[4]={0,0,0,1};if(thug_script_has_name_or_flag(s,0x737612c6)&&thug_script_has_name_or_flag(s,0x737612c6))thug_script_get_vector(s,0x737612c6,center,0);
 if(center[0]==0&&center[1]==0&&center[2]==0){
  for(unsigned kind=0;kind<2;kind++)for(unsigned i=half(p,kind?0x94:0x8c);i;){--i;float *v=fp(pointer(p,kind?0x90:0x60),i*(kind?20:16));for(unsigned j=0;j<4;j++)center[j]=(float)r((double)center[j]+v[j]);}
  double reciprocal=r(1.0/(int32_t)(half(p,0x8c)+half(p,0x94)));for(unsigned j=0;j<4;j++)center[j]=(float)r((double)center[j]*reciprocal);
 }
 float offset[4]={0,0,0,1};thug_script_get_vector(s,0x851211b0,offset,0);for(unsigned j=0;j<4;j++)*fp(p,0xb0+j*4)=(float)r((double)offset[j]-center[j]);
 const unsigned ptrs[]={0x60,0x90,0x98},counts[]={0x8c,0x94,0x9c},strides[]={16,20,36};
 for(unsigned kind=0;kind<3;kind++)for(unsigned i=half(p,counts[kind]);i;){--i;float *v=fp(pointer(p,ptrs[kind]),i*strides[kind]);for(unsigned j=0;j<4;j++)v[j]=(float)r((double)v[j]-center[j]);}
 if(!thug_script_get_float(s,0x967cd3ae,fp(p,0x18),0)){
  float radius=0;for(unsigned kind=0;kind<2;kind++)for(unsigned i=half(p,counts[kind]);i;){--i;float *v=fp(pointer(p,ptrs[kind]),i*strides[kind]);double length=r(__builtin_sqrt(length_squared(v)));if(kind)length=r(length+v[4]);float candidate=(float)length;if(!(radius>candidate))radius=candidate;}
  if(radius>30){double scaled=r((double)radius*0.03333333507180214);*fp(p,0x18)=(float)r((double)*fp(p,0x18)/r(scaled*scaled));}
 }
 if(thug_script_has_flag(s,0xa92b9954))put(p,0xf4,word(p,0xf4)|2);thug_rigidbody_initialization_constant_draft=0x429a0000;
 put(p,0x198,0);for(unsigned kind=0;kind<2;kind++)for(unsigned i=half(p,counts[kind]);i;){--i;float *v=fp(pointer(p,ptrs[kind]),i*strides[kind]);double candidate=length_squared(v);if(kind){candidate=r(r(__builtin_sqrt(candidate))+v[4]);candidate=r(candidate*candidate);}if(candidate>*fp(p,0x198))*fp(p,0x198)=(float)candidate;}
 put(p,0x194,0);*fp(p,0x198)=(float)r(r(__builtin_sqrt(*fp(p,0x198)))+1);
 double rotated[3];for(unsigned axis=0;axis<3;axis++)rotated[axis]=r(r(r((double)*fp(p,0x170+4*axis)**fp(p,0xb8))+r((double)*fp(p,0x160+4*axis)**fp(p,0xb4)))+r((double)*fp(p,0x150+4*axis)**fp(p,0xb0)));
 *fp(p,0x110)=(float)r((double)*fp(p,0x110)-rotated[0]);*fp(p,0x114)=(float)r((double)*fp(p,0x114)-rotated[1]);*fp(p,0x118)=(float)r((double)*fp(p,0x118)-(float)rotated[2]);*fp(p,0x11c)=(float)r((double)*fp(p,0x11c)-*fp(p,0xbc));
}
static void initialize_entry(void *p,const ThugScriptStructure *s){thug_rigidbody_initialize_draft(p,s,thug_component_services?thug_component_services->memory:thug_event_services->memory);}
void *thug_rigidbody_delete_draft(void *,uint32_t,const ThugMemory *);
static void update_pending(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)q;(void)d;(void)m;__builtin_trap();}
static void empty(void *p){(void)p;}
static uint32_t unhandled(void *p,uint32_t key,ThugScriptStructure *s,ThugScriptInstance *i){return thug_animation_unhandled_command(p,key,s,i,0,0);}
const ThugComponentMethods thug_rigidbody_methods_draft={.dispose=thug_rigidbody_delete_draft,.update=update_pending,.initialize=initialize_entry,.finalize=thug_rigidbody_finalize_draft,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor,.checksum=unhandled};
