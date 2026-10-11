#include <stdint.h>
#define WORD(a) (*(uint32_t *)(uintptr_t)(a))
#define BYTE(a) (*(uint8_t *)(uintptr_t)(a))
uint8_t fixture_animation_event_native(uint32_t params,uint32_t script) {
    uint32_t state=0x19cf000,channel=0x19c0800,events=0x19c9004;
    uint32_t n=WORD(state);WORD(state)=n+1;
    uint32_t *row=(uint32_t *)(uintptr_t)(state+128+n*64);
    row[0]=WORD(channel+0x6c);row[1]=WORD(channel+0x64);row[2]=WORD(channel+0x68);
    row[3]=WORD(script+0xc8);row[4]=WORD(script+0xbc);row[5]=params?WORD(params+4):0;
    for (uint32_t i=0;i<8;++i) row[6+i]=BYTE(events+i*20+8);
    row[14]=row[15]=0;
    if (!n) for(uint32_t off=4;off<=28;off+=12) {
        uint32_t at=WORD(state+off),value=WORD(state+off+4),width=WORD(state+off+8);
        if(at) { if(width==1) BYTE(at)=value; else WORD(at)=value; }
    }
    return 1;
}
