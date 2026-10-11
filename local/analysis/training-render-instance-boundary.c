/* Explicit test-only initializer/factory breakpoints: no allocation, component, or success. */
#include <stdint.h>
void *fixture_factory_431f60(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x431f60;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41a5b0(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41a5b0;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41c920(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41c920;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_433d90(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x433d90;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_4f3550(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x4f3550;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}

void fixture_renderer_ready(void *component,void *params){
 volatile unsigned *p=(void *)0x100e000;p[0]=0x421191;p[1]=(unsigned long)component;p[2]=*(unsigned *)((unsigned char *)component+0x208);p[3]=1;p[4]=(unsigned long)params;p[5]=0;__builtin_trap();
}
