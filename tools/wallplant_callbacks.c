/* Fixture-only native QB observer. The original interpreter invokes it. */
#include <stdint.h>
uint32_t fixture_wallplant_native(void *parameters,uint32_t *script) {
 (void)parameters;
 uint32_t *p=(void *)(uintptr_t)0x18e0000,*o=(void *)(uintptr_t)0x18e6400;
 uint32_t *body=(void *)(uintptr_t)p[3],*state=(void *)(uintptr_t)p[0x1528/4];
 uint32_t *row=o+16+o[0]++*8;
 row[0]=script[0xc8/4];row[1]=(uintptr_t)body;row[2]=(uintptr_t)state;row[3]=p[0x1518/4];
 row[4]=body[0xb0/4];row[5]=p[0x4e8/4];row[6]=state[0xc0/4];row[7]=state[0xb0/4];
 if(o[1])for(uint32_t i=0;i<o[3];++i)((uint8_t *)(uintptr_t)o[1])[i]=o[2]>>(8*i);
 return 1;
}
