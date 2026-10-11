/* Test-only terminal QB observer. Mutations model a callback changing live lists. */
#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
uint8_t fixture_gap_end_native(uint32_t params,uint32_t script){
 uint32_t p=0x1985000,n=W(p);W(p)=n+1;
 uint32_t *row=(void *)(uintptr_t)(p+128+n*16);
 row[0]=params;row[1]=W(script+0xc8);row[2]=W(0x1929024);row[3]=W(0x1929038);
 if(!W(p+4)||!n)for(uint32_t i=0;i<W(p+8);i++)W(W(p+16+i*8))=W(p+20+i*8);
 return 1;
}
