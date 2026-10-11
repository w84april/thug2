#include "../../src/core/memory.h"
#include "../../src/script/params.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
/* Constructor identities only. Virtual destruction/allocation through these
 * tables is unavailable; no virtual behavior is supplied by this draft. */
const void *const thug_heap_gap_methods_draft[]={0};
const void *const thug_heap_base_methods_draft[]={0};
const void *const thug_heap_sentinel_methods_draft[]={0};
const void *const thug_heap_block_methods_draft[]={0};
const void *const thug_heap_methods_draft[]={0};
const void *const thug_particle_manager_methods_draft[]={0};
const void *const thug_particle_list_methods_draft[]={0};
const char thug_particle_heap_name_draft[]="FlxParticles";
void *thug_allocator_registry_draft;
float thug_particle_time_scale_draft;
/* 005bc620. The process allocator is already initialized. Raw storage uses
 * the established platform port; it is deliberately not zero-filled here. */
void *thug_heap_gap_construct_draft(void *p,uint32_t size,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_heap_gap_methods_draft);
 if(size){uint32_t n=size&~15u;void *start=m->allocate(m->context,n,1);
  put(p,12,(uintptr_t)start+n);put(p,4,(uintptr_t)start);put(p,8,n);put(p,20,0);put(p,16,0);}
 return p;
}
/* 005bc4e0. Selection uses bit 1 of mode; the boundary uses exact mode==1. */
void thug_heap_gap_attach_draft(void *gap,void *heap){
 put(gap,16+4*((word(heap,0x28)>>1)&1),(uintptr_t)heap);
 put(heap,0x2c,word(gap,word(heap,0x28)==1?4:12));
}
/* 005ba260. Initialize and link the embedded sentinel and first free block. */
void *thug_heap_base_construct_draft(void *p,void *gap,uint32_t mode,const char *name){
 put(p,0,(uintptr_t)thug_heap_base_methods_draft);
 for(unsigned o=4;o<=0x20;o+=4)put(p,o,0);
 put(p,0x24,(uintptr_t)gap);put(p,0x28,mode);put(p,0x34,(uintptr_t)name);
 void *a=(char *)p+0x38,*b=(char *)p+0x4c;
 put(a,4,0xffffffff);put(a,8,0);put(a,12,(uintptr_t)a);put(a,16,(uintptr_t)a);put(a,0,(uintptr_t)thug_heap_sentinel_methods_draft);
 put(b,0,(uintptr_t)thug_heap_block_methods_draft);put(b,4,(uintptr_t)b);put(b,8,0);put(b,12,(uintptr_t)b);put(b,16,(uintptr_t)b);put(b,20,0);
 thug_heap_gap_attach_draft(gap,p);
 put(b,16,(uintptr_t)a);put(b,12,word(a,12));put((void *)(uintptr_t)word(a,12),16,(uintptr_t)b);put(a,12,(uintptr_t)b);put(p,0x30,(uintptr_t)b);
 return p;
}
/* 005ba520. Remaining bytes, including 65..67, retain their input value. */
void *thug_heap_construct_draft(void *p,void *gap,uint32_t mode,const char *name){
 thug_heap_base_construct_draft(p,gap,mode,name);put(p,0x6c,0);((uint8_t *)p)[0x64]=0;
 put(p,0,(uintptr_t)thug_heap_methods_draft);put(p,0x68,0xffffffff);return p;
}
/* 005bb4e0. The caller supplies a registry with space for another heap. */
void *thug_heap_registry_create_draft(void *registry,void *gap,uint32_t mode,const char *name,const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x98,m);if(p)thug_heap_construct_draft(p,gap,mode,name);
 put(registry,4*word(registry,0xc0),(uintptr_t)p);put(registry,0xc0,word(registry,0xc0)+1);return p;
}
/* 0049af20. Uses real QB settings, allocator registration and list sentinel.
 * This constructs the manager; particle creation and rendering remain absent. */
void *thug_particle_manager_construct_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_particle_manager_methods_draft);
 uint32_t size=thug_script_get_global_integer(0x91cb7552,0);if(!size)size=0x5000;
 void *gap=thug_allocate_zeroed(0x18,m);if(gap)thug_heap_gap_construct_draft(gap,size,m);put(p,4,(uintptr_t)gap);
 void *heap=thug_heap_registry_create_draft(thug_allocator_registry_draft,gap,1,thug_particle_heap_name_draft,m);
 put(p,8,(uintptr_t)heap);put(p,12,0);put(p,16,0);
 void *list=thug_allocate_zeroed(0x14,m);if(list){put(list,4,0xffffffff);put(list,8,0);put(list,12,(uintptr_t)list);put(list,16,(uintptr_t)list);put(list,0,(uintptr_t)thug_particle_list_methods_draft);}
 put(p,20,(uintptr_t)list);for(unsigned o=24;o<=36;o+=4)put(p,o,0x3f800000);
 double rate=thug_script_get_global_number(0x3214c818,0);
 thug_particle_time_scale_draft=rate==0?60:(float)thug_platform_round_x87_single(60.0/rate);return p;
}
