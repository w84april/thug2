/* Explicit test-only initializer/factory breakpoints: no allocation, component, or success. */
#include <stdint.h>
void *fixture_factory_431f60(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x431f60;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41a5b0(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41a5b0;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_41c920(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x41c920;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_433d90(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x433d90;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}
void *fixture_factory_4f3550(void *memory){(void)memory;volatile uint32_t *p=(void *)0x100e000; p[0]=0x4f3550;p[1]=*(uint32_t *)0x100c010;p[2]=0x100c000;p[3]=1;__builtin_trap();}

void fixture_model_buffer(unsigned key,const void *data,unsigned size,const void *companion,void *dictionary,unsigned offset,unsigned skin,unsigned flag,void *memory){
 (void)memory;volatile unsigned *p=(void *)0x100e000;p[0]=0x48c030;p[1]=key;p[2]=(unsigned long)data;p[3]=1;
 p[4]=size;p[5]=(unsigned long)companion;p[6]=(unsigned long)dictionary;p[7]=offset;p[8]=skin;p[9]=flag;__builtin_trap();
}
