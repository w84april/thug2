/* Explicit test-only initializer/factory breakpoints: no allocation, component, or success. */
#include <stdint.h>
void *fixture_factory_431f60(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x431f60;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41a5b0(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41a5b0;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41c920(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41c920;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_433d90(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x433d90;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_4f3550(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x4f3550;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}

int fixture_model_file(void *asset,const char *name,unsigned async,unsigned x,unsigned options,unsigned params,void *memory){
 (void)memory;volatile unsigned *p=(void *)0x100e000;const unsigned char *o=(void *)(unsigned long)options;
 p[0]=0x409eb0;p[1]=(unsigned long)asset;p[2]=params;p[3]=1;p[4]=async&255;p[5]=x;
 p[6]=o[0];__builtin_memcpy((void *)(p+7),o+4,4);__builtin_memcpy((void *)(p+8),o+8,4);p[9]=o[16];p[10]=o[17];
 unsigned n=0;volatile char *out=(void *)0x100e040;do{out[n]=name[n];}while(name[n++]);p[11]=n-1;__builtin_trap();
}
