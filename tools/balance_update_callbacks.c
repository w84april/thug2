#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
#define B(a) (*(uint8_t *)(uintptr_t)(a))
uint8_t fixture_balance_native(uint32_t params,uint32_t script) {
    uint32_t obs=0x19f2000,balance=0x19f0000,component=0x19f0100,controller=0x19c0900,score=0x18e1000,tricks=0x19f0800;
    uint32_t n=W(obs);W(obs)=n+1;uint32_t name=W(script+0xc8),first=params?W(params+4):0;
    uint32_t *r=(uint32_t *)(uintptr_t)(obs+64+n*48);
    r[0]=name;r[1]=W(script+0xbc);r[2]=W(balance+0x24);r[3]=W(balance+0x30);r[4]=W(balance+0x34);r[5]=W(component+0x18);r[6]=W(controller+0x28);r[7]=W(score+0x5c);r[8]=first;r[9]=first?W(first+4):0;r[10]=first?W(first+8):0;r[11]=B(tricks+0x28);
    if(!W(obs+16)||W(obs+16)==name) { uint32_t target=W(obs+4);if(target) { if(W(obs+12)==1)B(target)=W(obs+8);else W(target)=W(obs+8); } }
    return 1;
}
