/* Explicit test-only virtual dispatch witnesses. No game component behavior
 * or successful scene initialization is supplied by these callbacks. */
#include <stdint.h>
static uint32_t *const control=(void *)0x1980000,*const log=(void *)0x1981000;
static uint32_t read(uint32_t p,uint32_t offset){return p?*(uint32_t *)(uintptr_t)(p+offset):0;}
static void observe(uint32_t kind,uint32_t self,uint32_t arg,uint32_t arg2){
    uint32_t n=log[0]++,owner=kind>=7?self:read(self,12),*row=log+16+n*12;
    row[0]=kind;row[1]=self;row[2]=arg;row[3]=arg2;row[4]=owner;
    row[5]=read(owner,0x104);row[6]=read(self,0x10);row[7]=read(self,0x14);
    row[8]=read(owner,0x100);row[9]=read(0x186e000,0x44);row[10]=0;row[11]=0;
    if(kind==control[1]&&n==control[2]){
        if(control[3])*(uint32_t *)(uintptr_t)control[3]=control[4];
        if(control[5])*(uint32_t *)(uintptr_t)control[5]=control[6];
    }
}
void *fixture_composite_factory(void *memory){(void)memory;observe(1,0,0,0);return (void *)(uintptr_t)control[0];}
void fixture_composite_initialize(void *p,void *parameters){observe(2,(uintptr_t)p,(uintptr_t)parameters,0);}
void fixture_composite_finalize(void *p){observe(3,(uintptr_t)p,0,0);}
void fixture_composite_moved(void *p,void *q,void *d,void *m){(void)q;(void)d;(void)m;observe(4,(uintptr_t)p,0,0);}
void fixture_composite_before_delete(void *p){observe(5,(uintptr_t)p,0,0);}
void *fixture_composite_delete(void *p,uint32_t flags,void *m){(void)m;observe(6,(uintptr_t)p,flags,0);return p;}
void fixture_composite_add(void *p,void *descriptor,void *overrides,void *d,void *m){(void)d;(void)m;observe(7,(uintptr_t)p,(uintptr_t)descriptor,(uintptr_t)overrides);}
void fixture_composite_add_alt(void *p,void *descriptor,void *overrides,void *d,void *m){(void)d;(void)m;observe(8,(uintptr_t)p,(uintptr_t)descriptor,(uintptr_t)overrides);}
