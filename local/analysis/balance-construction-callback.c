/* Test-only user-defined QB native observer. No engine callee is substituted. */
#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
uint8_t fixture_balance_construct_native(uint32_t params,uint32_t script){
 uint32_t state=0x1a24000,n=W(state),p=W(state+12);W(state)=n+1;
 uint32_t *row=(void *)(uintptr_t)(state+128+n*32);
 row[0]=params;row[1]=W(script+0xb8);row[2]=p;row[3]=W(p);row[4]=W(p+0x24);row[5]=W(p+0x50);row[6]=W(p+0x38);row[7]=W(p+0x34);
 if(!W(state+4)||!n)for(uint32_t i=0;i<W(state+8);i++)W(W(state+16+i*8))=W(state+20+i*8);
 return 1;
}
