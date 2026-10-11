/* Explicit test-only initializer/factory breakpoints: no allocation, component, or success. */
#include <stdint.h>
void *fixture_factory_431f60(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x431f60;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41a5b0(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41a5b0;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41c920(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41c920;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_433d90(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x433d90;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_4f3550(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x4f3550;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}

void fixture_vertex_load(void *mesh,const void *data,unsigned size,void *aux,void *memory){
 (void)memory;volatile unsigned *p=(void *)0x100e000;p[0]=0x4d5c30;p[1]=(unsigned long)mesh;p[2]=(unsigned long)data;p[3]=1;p[4]=size;p[5]=(unsigned long)aux;__builtin_trap();
}
