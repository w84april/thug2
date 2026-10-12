/* Camera descriptor storage candidates; initialized heap required.
 * Pending tables are identity-only and establish no virtual lifecycle. */
#include "../../src/game/components.h"
#include "../../src/game/skater.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
const uint32_t thug_skater_camera_pending_methods_v1[13]={0};
const uint32_t thug_skater_camera_object_pending_methods_v1[13]={0};
const uint32_t thug_skater_camera_roll_pending_methods_v1[13]={0};
/* 005902e0: actually only MOV EAX,ECX / RET, leaves all98h bytes untouched. */
void *thug_camera_extra_storage_construct_v1(void *p){return p;}
/* 004fa4b0 */
void *thug_skater_camera_construct_storage_v1(void *p,const ThugMemory *m){
 thug_component_construct(p);put(p,0,(uintptr_t)thug_skater_camera_pending_methods_v1);put(p,4,0x5e43a604);put(p,0x24,0);
 void *extra=m->allocate(m->context,0x98,1);if(extra)extra=thug_camera_extra_storage_construct_v1(extra);put(p,0x16c,(uintptr_t)extra);
 for(unsigned i=0;i<4;i++)put(p,(unsigned[]){0x108,0x2c,0xec,0xf0}[i],0x3f800000);
 put(p,0x170,0);put(p,0x174,0);put(p,0x178,0);put(p,0x110,0x3d800000);put(p,0xe4,0x3e800000);put(p,0xe8,0x3f000000);put(p,0xf4,0x3dcccccd);return p;
}
/* 004fa800 */
void *thug_skater_camera_create_storage_v1(const ThugMemory *m){void *p=thug_allocate_zeroed(0x17c,m);return p?thug_skater_camera_construct_storage_v1(p,m):0;}
/* 004e42e0 */
void *thug_skater_camera_object_create_storage_v1(const ThugMemory *m){void *p=thug_allocate_zeroed(0x44,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)thug_skater_camera_object_pending_methods_v1);put(p,4,0x81c7122d);}return p;}
/* 00525dc0 */
void *thug_skater_camera_roll_create_storage_v1(const ThugMemory *m){void *p=thug_allocate_zeroed(0xa8,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)thug_skater_camera_roll_pending_methods_v1);put(p,4,0xc7d37ec2);put(p,0x24,0);put(p,0x28,0);put(p,0x2c,0);put(p,0x30,0x3f800000);}return p;}
/* 004f9a20: bind the first CameraObject component, including absent result. */
void thug_skater_camera_bind_object_v1(void *p){put(p,0x168,(uintptr_t)thug_object_find_component((void *)(uintptr_t)word(p,12),0x81c7122d));}
