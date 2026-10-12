/* Test-only external audio buffer Stop observer; no game routine is replaced. */
#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
uint32_t fixture_looping_sound_stop(uint32_t buffer){
 uint32_t s=0x1a22000,n=W(s),p=W(s+12);W(s)=n+1;
 uint32_t *row=(void *)(uintptr_t)(s+128+n*32);
 row[0]=buffer;row[1]=p;row[2]=W(p+24);row[3]=W(p);row[4]=W(p+8);row[5]=*(uint8_t *)(uintptr_t)(p+0xfd);row[6]=W(s+4);row[7]=n;
 for(uint32_t i=0;i<W(s+8);i++)W(W(s+16+i*8))=W(s+20+i*8);
 return W(s+4);
}
