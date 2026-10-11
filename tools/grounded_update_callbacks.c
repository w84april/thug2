#include <stdint.h>
#define W(a) (*(uint32_t *)(uintptr_t)(a))
uint8_t fixture_grounded_native(uint32_t params,uint32_t script) {
    uint32_t obs=0x1655000,phys=0x1991000,mode=0x1640000;
    uint32_t n=W(obs),name=W(script+0xc8),body=W(phys+12),state=W(phys+0x1528);
    W(obs)=n+1;uint32_t *r=(uint32_t *)(uintptr_t)(obs+64+n*48);
    r[0]=name;r[1]=W(script+0xbc);r[2]=body;r[3]=state;r[4]=W(state+0x18);r[5]=W(mode+0x18);r[6]=W(mode+0x54);r[7]=W(mode+0x15c);r[8]=W(body+0x4c);r[9]=W(body+0x50);r[10]=W(body+0x54);r[11]=params;
    if(!W(obs+16)||W(obs+16)==name) { uint32_t target=W(obs+4);if(target) { if(W(obs+12)==1)*(uint8_t *)(uintptr_t)target=W(obs+8);else W(target)=W(obs+8); } }
    return 1;
}
