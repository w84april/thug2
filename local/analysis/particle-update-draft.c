#include "../../src/game/camera.h"
#include "../../src/game/components.h"
#include "../../src/core/number.h"
#include "../../src/script/lifetime.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static double r(double x){return thug_platform_round_x87_single(x);}
int32_t thug_particle_viewport_count_draft; /* 00701378 */
float thug_particle_view_matrix_draft[16]; /* 00786bd0 */
float thug_particle_view_near_draft; /* 00786ca8 */
float thug_particle_view_planes_draft[4]; /* 00786e20 */
/* 004a06d0 / 004a09c0: numbered active viewport, rather than a direct slot. */
ThugViewport *thug_particle_viewport_draft(uint32_t index){
 uint32_t found=0;for(unsigned i=0;i<10;i++)if(thug_viewport_mapping[i]>=0){if(found==index)return thug_viewports[thug_viewport_mapping[i]];++found;}return 0;
}
ThugCamera *thug_particle_camera_draft(uint32_t index){return thug_particle_viewport_draft(index)->camera;}
/* 00496b40. The far branch returns the minimum field directly; only the
 * interpolated count is clamped to the supplied current particle count. */
uint32_t thug_particle_distance_count_draft(const void *p,uint32_t count){
 float near=number(p,0x84),far=number(p,0x88);
 if(!(near<far)||thug_particle_viewport_count_draft>1)return count;
 ThugCamera *camera=thug_particle_camera_draft(0);if(!camera)return count;
 const float *position=thug_camera_position(camera);
 double x=r((double)number(p,0x20)-position[0]),y=r((double)number(p,0x24)-position[1]),z=r((double)number(p,0x28)-position[2]);
 float distance=(float)r(r(r(z*z)+r(y*y))+r(x*x));
 if(distance<near)return count;uint32_t minimum=word(p,0x80);if(distance>far)return minimum;
 double ratio=r(r((double)far-distance)/r((double)far-near));
 uint32_t difference=word(p,0x7c)-minimum;
 uint32_t value=thug_truncate_double_low_word(r(r(ratio*(int32_t)difference)+(int32_t)minimum));
 return (int32_t)count<(int32_t)value?count:value;
}
/* 005e1616: selected original D3DX SSE Vec3Transform backend. Both aligned
 * and unaligned matrix loads have identical four-lane arithmetic. */
float *thug_particle_vector3_transform_sse_draft(float *out,const float *in,const float *matrix){
 float result[4];for(unsigned i=0;i<4;i++){
  float z=in[2]*matrix[8+i],x=in[0]*matrix[i],y=in[1]*matrix[4+i];
  float zt=z+matrix[12+i],xy=x+y;result[i]=xy+zt;
 }
 __builtin_memcpy(out,result,16);return out;
}
/* 005bf19f: lifted initialized D3DX dispatch slot684fdc, matching the SSE
 * startup selection already used by recovered matrix multiplication. */
float *(*thug_particle_vector3_transform_draft)(float *,const float *,const float *)=thug_particle_vector3_transform_sse_draft;
float *thug_particle_vector3_transform_entry_draft(float *out,const float *in,const float *m){return thug_particle_vector3_transform_draft(out,in,m);}
/* 004db570 plus 004b2310 and 0048c490 forwarding wrappers. */
uint32_t thug_particle_sphere_culled_pc_draft(const float *center,float radius){
 float p[4];thug_particle_vector3_transform_entry_draft(p,center,thug_particle_view_matrix_draft);
 if(r((double)radius-p[2])<thug_particle_view_near_draft)return 1;
 double z=r((double)thug_particle_view_planes_draft[0]*p[2]),x=r((double)thug_particle_view_planes_draft[2]*p[0]);
 if(r(z-x)>radius||radius<r(z+x))return 1;
 z=r((double)thug_particle_view_planes_draft[1]*p[2]);double y=r((double)thug_particle_view_planes_draft[3]*p[1]);
 if(r(y+z)>radius||radius<r(z-y))return 1;return 0;
}
uint32_t thug_particle_sphere_culled_forward_draft(const float *p,float radius){return thug_particle_sphere_culled_pc_draft(p,radius);}
uint32_t thug_particle_sphere_culled_draft(const float *p,float radius){return thug_particle_viewport_count_draft>1?0:thug_particle_sphere_culled_forward_draft(p,radius);}
extern const void *const thug_particle_base_methods_draft[],*const thug_particle_base_node_methods_draft[],*const thug_particle_buffer_methods_draft[],*const thug_particle_buffer_node_methods_draft[],*const thug_particle_point_methods_draft[],*const thug_particle_point_node_methods_draft[];
const void *const thug_particle_unlinked_node_methods_draft[]={0}; /* 00649420 identity */
extern void *thug_cutscene_context_draft;
void *thug_particle_find_draft(const void *,uint32_t);
/* 004d2bd0: complete material-owned array release, retaining original fields. */
void thug_particle_material_data_destroy_draft(void *p,const ThugMemory *m){
 if(word(p,0xf4)){
  for(uint32_t i=0;i<word(p,0xf0);i++)m->release(m->context,ptr(ptr(p,0xf4),i*12+8));
  m->release(m->context,ptr(p,0xf4));
 }
 if(word(p,0xf8))m->release(m->context,ptr(p,0xf8));
 for(unsigned o=0xd0;o<0xe0;o+=4)if(word(p,o))m->release(m->context,ptr(p,o));
 if(word(p,0xfc)){for(unsigned o=0x34;o<0x44;o+=4)m->release(m->context,ptr(ptr(p,0xfc),o));m->release(m->context,ptr(p,0xfc));}
}
/* 004d9cd0. */
void thug_particle_material_destroy_draft(void *p,const ThugMemory *m){void *v=ptr(p,0);if(v){thug_particle_material_data_destroy_draft(v,m);m->release(m->context,v);}}
/* 0049ad60. Null is allowed, and the manager receiver is unused. */
void thug_particle_manager_unlink_draft(void *manager,void *p){
 (void)manager;if(!p)return;void *node=(char *)p+12;
 put(ptr(node,16),12,word(node,12));put(ptr(node,12),16,word(node,16));put(node,12,(uintptr_t)node);put(node,16,(uintptr_t)node);
}
/* 00498690. Array record destructor5480a0 is an actual bare RET, so the
 * original reverse destruction loop has no observable record side effects. */
void thug_particle_destroy_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_particle_base_methods_draft);put(p,12,(uintptr_t)thug_particle_base_node_methods_draft);
 for(unsigned o=0xfc;o<=0x100;o+=4){void *v=ptr(p,o);if(v){thug_script_destroy(v,d,m);thug_script_free(v,m);}}
 void *parameters=ptr(p,0x104);if(parameters){thug_script_structure_destroy(parameters,m);thug_script_structure_free(parameters,m);}
 for(unsigned o=0x10c;o<=0x11c;o+=4){if(o==0x118)continue;void *v=ptr(p,o);if(v)m->release(m->context,v);}
 void *records=ptr(p,0xf8);if(records)m->release(m->context,(char *)records-4);
 thug_particle_manager_unlink_draft(thug_cutscene_context_draft,p);
 put(p,12,(uintptr_t)thug_particle_unlinked_node_methods_draft);thug_particle_manager_unlink_draft(0,p);
 thug_reference_target_destroy(p);
}
/* 0049b600 and004c2260: derived-to-base destruction order. */
void thug_particle_buffer_destroy_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_particle_buffer_methods_draft);put(p,12,(uintptr_t)thug_particle_buffer_node_methods_draft);thug_particle_destroy_draft(p,d,m);
}
void thug_particle_point_destroy_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_particle_point_methods_draft);put(p,12,(uintptr_t)thug_particle_point_node_methods_draft);
 void *v=ptr(p,0x134);if(v){thug_particle_material_destroy_draft(v,m);m->release(m->context,v);}thug_particle_buffer_destroy_draft(p,d,m);
}
/* 004c2af0 /0049b630: deleting wrappers; release is governed by low flag bit. */
void *thug_particle_point_delete_draft(void *p,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m){thug_particle_point_destroy_draft(p,d,m);if(flags&1)m->release(m->context,p);return p;}
void *thug_particle_buffer_delete_draft(void *p,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m){thug_particle_buffer_destroy_draft(p,d,m);if(flags&1)m->release(m->context,p);return p;}
/* 0049ad90 and0049adb0: actual class deletion or delayed-deletion flags. */
void thug_particle_manager_delete_draft(void *manager,uint32_t name,const ThugDiagnostics *d,const ThugMemory *m){
 void *p=thug_particle_find_draft(manager,name);if(p){typedef void *(*Delete)(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);((Delete *)ptr(p,0))[0](p,1,d,m);}
}
void thug_particle_manager_expire_draft(void *manager,uint32_t name){void *p=thug_particle_find_draft(manager,name);if(p){((uint8_t *)p)[0x125]=1;put(p,0x120,word(p,0x120)|1);}}

/* 0049bb80 /0049bb50 /0049bba0: original trail-buffer count and lifetime.
 * Rendering slots stay unavailable; frame execution uses these actual methods. */
int32_t thug_particle_trail_segments_draft(const void *p){return (int32_t)word(p,0x134);}
void *thug_particle_trail_delete_draft(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
int32_t thug_particle_four_colors_draft(void *);
const void *const thug_particle_trail_methods_draft[]={[0]=thug_particle_trail_delete_draft,[2]=thug_particle_trail_segments_draft,[3]=thug_particle_four_colors_draft};
const void *const thug_particle_trail_node_methods_draft[]={0};
void thug_particle_trail_destroy_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_particle_trail_methods_draft);put(p,12,(uintptr_t)thug_particle_trail_node_methods_draft);thug_particle_destroy_draft(p,d,m);
}
void *thug_particle_trail_delete_draft(void *p,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m){thug_particle_trail_destroy_draft(p,d,m);if(flags&1)m->release(m->context,p);return p;}
void thug_particle_advance_setup_draft(void *,const ThugDiagnostics *,const ThugMemory *);
void thug_particle_bounds_draft(void *);
void thug_particle_emit_draft(void *,uint32_t);
void thug_particle_position_get_draft(void *,uint32_t,uint32_t,uint32_t *,uint32_t *,uint32_t *);
void thug_particle_position_set_draft(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
double thug_collision_probe_light_draft(const ThugCollisionProbe *);
extern float thug_particle_time_scale_draft;
static void store_float(void *p,unsigned o,double value){float f=(float)value;put(p,o,word(&f,0));}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
static int32_t segment_count(void *p){typedef int32_t (*Count)(void *);return ((Count *)ptr(p,0))[2](p);}
static void remove_record(void *p,uint32_t index,void *record,int culled){
 uint32_t last=word(p,0x8c)-1;put(p,0x8c,last);void *source=(char *)ptr(p,0xf8)+last*48;
 for(unsigned j=0;j<12;j++)put(record,j*4,word(source,j*4));
 for(int32_t s=0;s<segment_count(p);s++){
  if(culled){uint32_t x,y,z;thug_particle_position_get_draft(p,word(p,0x8c),s,&x,&y,&z);thug_particle_position_set_draft(p,index,s,x,y,z);}
  else{
   void *from=(char *)ptr(p,0x11c)+(word(p,0x8c)+word(p,0x7c)*(uint32_t)s)*12;
   uint32_t x=word(from,0),y=quiet(word(from,4)),z=quiet(word(from,8));
   void *to=(char *)ptr(p,0x11c)+(index+word(p,0x7c)*(uint32_t)s)*12;put(to,4,y);put(to,0,x);put(to,8,z);
  }
  void *unused=(char *)ptr(p,0x11c)+(word(p,0x8c)+word(p,0x7c)*(uint32_t)s)*12;
  put(unused,0,0x44800000);put(unused,4,0x44800000);put(unused,8,0x44800000);
 }
}
/* 004987f0. Full particle simulation update, including offscreen expiry,
 * scripts, real collision lighting, trail history, count reduction and disposal.
 * All platform/script/collision services remain explicit, as elsewhere in C. */
void thug_particle_update_draft(void *p,float elapsed,uint32_t paused,ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m){
 if((((uint8_t *)p)[0x125]&&!word(p,0x8c))||(word(p,0x78)&&!thug_script_find_object(word(p,0x78)))){
  typedef void *(*Delete)(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);((Delete *)ptr(p,0))[0](p,1,d,m);return;
 }
 if((uint8_t)paused||!((uint8_t *)p)[0x12f])return;
 thug_particle_advance_setup_draft(p,d,m);thug_particle_bounds_draft(p);((uint8_t *)p)[0x130]=1;
 int culled=thug_particle_viewport_count_draft==1&&thug_particle_camera_draft(0)&&((uint8_t *)p)[0x133]&&thug_particle_sphere_culled_draft((float *)((char *)p+0x50),number(p,0x5c));
 if(culled)((uint8_t *)p)[0x130]=0;
 if(culled&&number(p,0x70)==0){
  void *records=ptr(p,0xf8);for(int32_t i=0;i<(int32_t)word(p,0x8c);i++){
   void *record=(char *)records+(uint32_t)i*48;double age=r((double)elapsed+number(record,40));store_float(record,40,age);
   if(age>number(record,44)){remove_record(p,(uint32_t)i,record,1);--i;}
  }return;
 }
 if(number(p,0x70)!=0){
  double accumulator=r((double)elapsed+number(p,0x74));store_float(p,0x74,accumulator);
  uint32_t count=thug_truncate_double_low_word(r(accumulator*number(p,0x70)));
  if(count){store_float(p,0x74,r(accumulator-r((double)(int32_t)count/number(p,0x70))));thug_particle_emit_draft(p,count);}
 }
 if(word(p,0x100))thug_script_execute(ptr(p,0x100),d,m);
 if(!((uint8_t *)p)[0x12c]||elapsed==0)return;
 if(((uint8_t *)p)[0x132]){
  ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
  for(unsigned i=0;i<4;i++){put(probe.segment,4*i,word(p,0x20+4*i));put(probe.segment,16+4*i,word(p,0x20+4*i));}
  store_float(probe.segment,4,r((double)number(p,0x24)+1));store_float(probe.segment,20,r((double)number(p,0x24)-4800));
  if(thug_collision_probe_query(&probe,0,0,query)){double light=thug_collision_probe_light_draft(&probe);store_float(p,0xec,r(light+light));}
  thug_collision_probe_release(&probe);
 }
 float step=(float)r((double)thug_particle_time_scale_draft*elapsed);void *records=ptr(p,0xf8);
 for(int32_t i=0;i<(int32_t)word(p,0x8c);i++){
  void *record=(char *)records+(uint32_t)i*48;store_float(record,40,r((double)elapsed+number(record,40)));
  for(unsigned j=0;j<3;j++)store_float(record,j*4,r(r((double)step*number(record,12+j*4))+number(record,j*4)));
  for(int32_t s=segment_count(p)-1;s>0;s--){
   void *from=(char *)ptr(p,0x11c)+(word(p,0x7c)*(uint32_t)(s-1)+(uint32_t)i)*12;
   uint32_t x=word(from,0),y=quiet(word(from,4)),z=quiet(word(from,8));
   void *to=(char *)ptr(p,0x11c)+(word(p,0x7c)*(uint32_t)s+(uint32_t)i)*12;put(to,0,x);put(to,4,y);put(to,8,z);
  }
  void *position=(char *)ptr(p,0x11c)+(uint32_t)i*12;
  double dx=r((double)step*number(record,0)),dy=r((double)step*number(record,4)),dz=r((double)step*number(record,8));
  store_float(position,0,r(dx+number(position,0)));store_float(position,4,r(dy+number(position,4)));store_float(position,8,r(dz+number(position,8)));
 }
 records=ptr(p,0xf8);for(int32_t i=0;i<(int32_t)word(p,0x8c);i++){
  void *record=(char *)records+(uint32_t)i*48;if(number(record,40)>number(record,44)){remove_record(p,(uint32_t)i,record,0);--i;}
 }
 int32_t target=(int32_t)thug_particle_distance_count_draft(p,word(p,0x8c));records=ptr(p,0xf8);
 for(int32_t i=0;i<(int32_t)word(p,0x8c);i++)if(target<(int32_t)word(p,0x8c)){remove_record(p,(uint32_t)i,(char *)records+(uint32_t)i*48,0);--i;}
 for(unsigned j=0;j<4;j++)put(p,0x30+4*j,word(p,0x20+4*j));
}
