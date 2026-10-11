/* Test-only gameplay event boundaries; the recovered dispatcher/executor run. */
#include <stdint.h>
#define C ((uint32_t *)(uintptr_t)0x1830000)
#define W(a) (*(uint32_t *)(uintptr_t)(a))
static void observe(uint32_t kind,uint32_t owner,uint32_t script,uint32_t *event) {
    uint32_t p=C[4],body=W(p+12),state=W(p+0x1528),*log=C+32+C[0]++*24;
    log[0]=kind;log[1]=owner;log[2]=script;
    for(unsigned i=0;i<5;++i)log[3+i]=event?event[i]:0;
    log[8]=body;log[9]=state;log[10]=W(p+0x4e0);log[11]=W(p+0x4e4);
    log[12]=*(uint8_t *)(uintptr_t)(state+0xb8);log[13]=W(state+0xbc);log[14]=W(C[8]);log[15]=W(C[9]);
    for(unsigned i=0;i<4;++i){log[16+i]=W(body+0xac+i*4);log[20+i]=W(p+0x130+i*4);}
    uint32_t mode=C[1],address=C[2],value=C[3];
    if(mode==1)*(uint8_t *)(uintptr_t)address=(uint8_t)value;
    if(mode==2)W(address)=value;
    if(mode==3)W(p+12)=value;
    if(mode==4)W(p+0x1528)=value;
    if(mode==5)W(C[8])=value;
    if(mode==6){if(event)event[2]=0x200;else *(uint8_t *)(uintptr_t)address=(uint8_t)value;}
}
void fixture_rebound_object(uint32_t owner,uint32_t *event){observe(2,owner,0,event);}
void fixture_rebound_receiver(uint32_t owner,uint32_t *event){observe(1,owner,0,event);}
uint32_t fixture_rebound_native(uint32_t parameters,uint32_t script){(void)parameters;observe(0,0,script,0);return 1;}
