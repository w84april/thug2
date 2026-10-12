/* Test-only native QB observer; no collision or script behavior is replaced. */
#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
uint8_t fixture_trigger_native(uint32_t params,uint32_t script){
 uint32_t state=0x1a22000,p=0x18c0000,n=W(state);W(state)=n+1;
 uint32_t *row=(void *)(uintptr_t)(state+128+n*48);
 row[0]=params;row[1]=W(script+0xb8);row[2]=W(p+0x28);row[3]=W(p+12);
 for(unsigned i=0;i<4;i++){row[4+i]=W(p+0x18+i*4);row[8+i]=W(W(p+12)+0x4c+i*4);}
 if(!W(state+4)||!n)for(uint32_t i=0;i<W(state+8);i++)W(W(state+16+i*8))=W(state+20+i*8);
 return 1;
}
