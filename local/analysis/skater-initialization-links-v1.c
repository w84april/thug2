/* Post-construction startup dependencies; no full initializer claim. */
#include "../../src/game/components.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
void *thug_motion_construct_draft(void *);
void *thug_object_proximity_construct_draft(void *);
void *thug_object_sound_construct_draft(void *);
void *thug_lockobj_construct_draft(void *);
void thug_composite_add_component_draft(void *,void *);
/* Identity only: none of the light component virtual methods is recovered here. */
const uint32_t thug_object_light_pending_methods_v1[13]={0};
/* 00433c10. Raw construction preserves every other payload word. */
void *thug_object_light_construct_v1(void *p){
 thug_component_construct(p);put(p,0x24,0);put(p,0x28,0);
 put(p,0,(uintptr_t)thug_object_light_pending_methods_v1);put(p,4,0x0f1641e3);return p;
}
/* 0057b2f0. One cdecl owner argument, not the decompiler's inferred fastcall.
 * Valid startup requires successful internal allocations. */
void thug_skater_add_shared_components_v1(void *owner,const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x24c,m);if(p)p=thug_motion_construct_draft(p);thug_composite_add_component_draft(owner,p);
 p=thug_allocate_zeroed(0x30,m);if(p)p=thug_object_proximity_construct_draft(p);thug_composite_add_component_draft(owner,p);
 p=thug_allocate_zeroed(0xc0,m);if(p)p=thug_object_sound_construct_draft(p);thug_composite_add_component_draft(owner,p);
 p=thug_allocate_zeroed(0x2c,m);if(p)p=thug_object_light_construct_v1(p);thug_composite_add_component_draft(owner,p);
 p=thug_allocate_zeroed(0x90,m);if(p)p=thug_lockobj_construct_draft(p);thug_composite_add_component_draft(owner,p);
}
/* 004fa3c0. Setting a null owner clears links without changing camera state.
 * Each nonnull lookup reads the stored owner at its original point. */
void thug_skater_camera_bind_owner_v1(void *p,void *owner){
 put(p,0x170,(uintptr_t)owner);
 if(!owner){put(p,0x174,0);put(p,0x178,0);return;}
 void *state=thug_object_find_component(owner,0x43686585);
 owner=ptr(p,0x170);put(p,0x174,(uintptr_t)state);
 void *trick=thug_object_find_component(owner,0xd9151d4d);
 put(p,0x28,3);put(p,0x178,(uintptr_t)trick);
}
/* 00525e60. Camera owner must be nonnull; a missing camera component is valid. */
void thug_walk_bind_camera_v1(void *p,void *camera){
 put(p,0x175c,(uintptr_t)camera);
 put(p,0x1760,(uintptr_t)thug_object_find_component(camera,0xc7d37ec2));
}
