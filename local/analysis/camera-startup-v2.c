/* Native camera storage and synchronization; full skater-camera updates remain. */
#include "../../src/game/components.h"
#include "../../src/game/ui.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void real(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static float bits(uint32_t v){float f;__builtin_memcpy(&f,&v,4);return f;}
float thug_camera_default_fov_v2,thug_camera_display_ratio_v2;
uint8_t thug_camera_far_override_v2;
uint32_t thug_camera_far_frames_v2;
double thug_camera_get_default_fov_v2(void){return thug_camera_default_fov_v2;}
double thug_camera_get_display_ratio_v2(void){return thug_camera_display_ratio_v2;}
/* 00485aa0. Retain the original float stores and PC=24 arithmetic boundaries.
 * SDK tan/atan replace FPTAN/FPATAN; physical x87 accuracy is not claimed. */
void thug_camera_projection_v2(void *p){
 float angle=(float)R((double)number(p,0xac)*bits(0x3c0efa35));
 double tangent=thug_platform_tan(angle);
 double scaled=R(thug_camera_display_ratio_v2*R(tangent/number(p,0xc0)));
 double degrees=R(thug_platform_atan2(scaled,1)*bits(0x42e52ee0));
 real(p,0xb0,(float)degrees);
 float vertical=(float)thug_platform_tan(R(degrees*bits(0x3c0efa35)));
 double global_angle=R(R((double)thug_camera_default_fov_v2*.5)*bits(0x3c8efa35));
 real(p,0xb4,(float)R(vertical/thug_platform_tan(global_angle)));
}
void *thug_camera_object_delete_v2(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
const ThugUiObjectMethods thug_camera_object_methods_v2={.dispose=thug_camera_object_delete_v2,.receive_event=thug_ui_object_event_bridge};
void *thug_camera_object_construct_v2(void *p){
 thug_ui_object_initialize(p);put(p,0,(uintptr_t)&thug_camera_object_methods_v2);
 real(p,0xc0,1);real(p,0xac,thug_camera_default_fov_v2);thug_camera_projection_v2(p);
 for(unsigned i=0;i<16;++i)put(p,0x6c+i*4,i%5==0?0x3f800000:0);
 real(p,0xb8,12);real(p,0xbc,12000);
 if(thug_camera_far_override_v2)real(p,0xbc,(float)R((double)thug_camera_far_frames_v2*30));
 for(unsigned i=0;i<4;++i){put(p,0x5c+i*4,i==3?0x3f800000:0);put(p,0x4c+i*4,i==3?0x3f800000:0);}return p;
}
void thug_camera_object_destroy_v2(void *p,const ThugDiagnostics *d,const ThugMemory *m){put(p,0,(uintptr_t)&thug_camera_object_methods_v2);thug_ui_object_destroy(p,d,m);}
void *thug_camera_object_delete_v2(void *p,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m){thug_camera_object_destroy_v2(p,d,m);if(flags&1)m->release(m->context,p);return p;}
void thug_camera_set_position_draft(void *,const float *);
float *thug_camera_set_orientation_draft(void *,const float *);
/* 0041b8a0 snapshots owner position and orientation before storing cached state. */
void thug_camera_component_update_v2(void *p){
 uint32_t position[4];void *owner=ptr(p,12);__builtin_memcpy(position,(char *)owner+0x4c,16);
 float orientation[16];thug_matrix_copy(orientation,(float *)((char *)owner+0x6c));
 owner=ptr(p,12);thug_matrix_copy((float *)((char *)owner+0xc0),orientation);
 thug_camera_set_position_draft(ptr(p,0x18),(float *)position);
 thug_camera_set_orientation_draft(ptr(p,0x18),orientation);
}
/* 0041b810 copies live owner state without changing the owner's cached matrix. */
void thug_camera_component_sync_v2(void *p){
 void *owner=ptr(p,12);thug_camera_set_position_draft(ptr(p,0x18),(float *)((char *)owner+0x4c));
 owner=ptr(p,12);thug_camera_set_orientation_draft(ptr(p,0x18),(float *)((char *)owner+0x6c));
}
void *thug_camera_component_delete_v2(void *,uint32_t,const ThugMemory *);
static void pending_initialize(void *p,const ThugScriptStructure *s){(void)p;(void)s;__builtin_trap();}
static void update_bridge(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_camera_component_update_v2(p);}
const ThugComponentMethods thug_camera_component_methods_v2={.dispose=thug_camera_component_delete_v2,.update=update_bridge,.initialize=pending_initialize,.finalize=thug_camera_component_sync_v2,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.descriptor=thug_component_descriptor_base};
void *thug_camera_component_construct_v2(void *p,const ThugMemory *m){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_camera_component_methods_v2);put(p,4,0xc4e311fa);
 void *camera=thug_allocate_zeroed(0xc4,m);if(camera)camera=thug_camera_object_construct_v2(camera);put(p,0x18,(uintptr_t)camera);return p;
}
void *thug_camera_component_create_v2(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1c,m);return p?thug_camera_component_construct_v2(p,m):0;}
void thug_camera_component_destroy_v2(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 put(p,0,(uintptr_t)&thug_camera_component_methods_v2);void *camera=ptr(p,0x18);
 if(camera)(*(const ThugUiObjectMethods **)camera)->dispose(camera,1,d,m);thug_component_destroy(p);
}
void *thug_camera_component_delete_v2(void *p,uint32_t flags,const ThugMemory *m){
 thug_camera_component_destroy_v2(p,0,m);if(flags&1)m->release(m->context,p);return p;
}
/* 00524c50. Walk-camera ownership links use repeated live owner reads. */
void thug_walk_camera_bind_owner_v2(void *p,void *owner){
 if(!owner){put(p,0x9c,0);put(p,0xa0,0);put(p,0xa4,0);return;}
 put(p,0x9c,(uintptr_t)owner);void *walk=thug_object_find_component(owner,0x726e85aa);
 owner=ptr(p,0x9c);put(p,0xa0,(uintptr_t)walk);put(p,0xa4,(uintptr_t)thug_object_find_component(owner,0xd9151d4d));
}
