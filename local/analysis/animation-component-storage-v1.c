/* 0041a410/0041a5b0. Initialized-heap animation component storage only.
 * Identity tables do not claim virtual lifecycle or complete QB initialization. */
#include "../../src/game/components.h"
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
/* Neither table is dispatched by this storage candidate. */
const uint32_t thug_animation_component_pending_methods_v1[13]={0};
const uint32_t thug_animation_component_embedded_pending_methods_v1[1]={0};
void *thug_animation_component_construct_storage_v1(void *p,const ThugMemory *m){
 thug_component_construct(p);void *embedded=(char *)p+0x28;
 put(p,0,(uintptr_t)thug_animation_component_pending_methods_v1);
 put(p,0x2c,0xffffffff);put(p,0x30,0);put(p,0x34,(uintptr_t)embedded);put(p,0x38,(uintptr_t)embedded);
 put(embedded,0,(uintptr_t)thug_animation_component_embedded_pending_methods_v1);put(p,0x40,0);
 void *node=m->allocate(m->context,12,1);if(node){put(node,4,(uintptr_t)node);put(node,8,(uintptr_t)node);}
 put(p,0x3c,(uintptr_t)node);put(p,4,0x7149b753);return p;
}
void *thug_animation_component_create_storage_v1(const ThugMemory *m){void *p=thug_allocate_zeroed(0x44,m);return p?thug_animation_component_construct_storage_v1(p,m):0;}
