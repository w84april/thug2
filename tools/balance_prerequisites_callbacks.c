/* Test-only native observer executed by the original timed-trick QB dispatch. */
#include <stdint.h>
#define WORD(at) (*(uint32_t *)(uintptr_t)(at))
#define BYTE(at) (*(uint8_t *)(uintptr_t)(at))
static uint32_t hash(uint32_t at) {
    uint32_t h=0; if (at) for (const uint8_t *p=(void *)(uintptr_t)at;*p;++p) h=h*33+*p;
    return h;
}
uint32_t fixture_timed_trick_native(uint32_t parameters,uint32_t script) {
    uint32_t *c=(void *)(uintptr_t)0x19c0c00, n=c[0]++, *row=c+16+n*16;
    uint32_t i=0xffffffff,threshold=0,name=0,extra=0,count=0;
    for (uint32_t p=parameters?WORD(parameters+4):0;p;p=WORD(p+12)) {
        ++count;
        switch (WORD(p+4)) {
            case 0x7f8c98fe:i=WORD(p+8);break;
            case 0xe288a7cb:threshold=WORD(p+8);break;
            case 0x61414d56:name=WORD(p+8);break;
            case 0xc257d69a:extra=WORD(p+8);break;
        }
    }
    uint32_t timed=c[6],record=i<70?timed+0x1c+i*36:0;
    row[0]=WORD(script+0xc8);row[1]=count;row[2]=i;row[3]=threshold;
    row[4]=hash(name);row[5]=hash(extra);row[6]=record?BYTE(record+12):0;
    row[7]=record?WORD(record+16):0;row[8]=record?WORD(record):0;
    row[9]=WORD(timed+0xa90);row[10]=BYTE(timed+0x9f4);row[11]=i<69?WORD(record+44):0;
    row[12]=row[13]=row[14]=row[15]=0;
    if(c[1]&&(!c[3]||!n)&&(!c[5]||c[5]==row[0])) {
        if(c[4]==1)BYTE(c[1])=(uint8_t)c[2];else WORD(c[1])=c[2];
    }
    return 1;
}
