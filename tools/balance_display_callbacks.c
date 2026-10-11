/* Test-only native command reached through the real show/hide QB scripts. */
#include <stdint.h>
#define WORD(at) (*(uint32_t *)(uintptr_t)(at))
uint32_t fixture_balance_display_native(uint32_t parameters, uint32_t script) {
    uint32_t *context=(void *)(uintptr_t)0x18fac00;
    uint32_t n=context[0]++, *row=context+16+n*12;
    uint32_t first=parameters?WORD(parameters+4):0, score=context[4],widget=context[5],body=context[6];
    row[0]=WORD(script+0xc8);row[1]=first?WORD(first+4):0;row[2]=first?WORD(first+8):0;
    row[3]=first?*(uint8_t *)(uintptr_t)first:0;
    row[4]=WORD(widget+0x14);row[5]=WORD(widget+8);row[6]=WORD(widget+0x58);row[7]=WORD(body+0x2b8);
    row[8]=WORD(score+0x184);row[9]=WORD(score+0x18c);row[10]=WORD(score+0x190);row[11]=WORD(score+0x194);
    if(context[1] && (!context[3] || !n))WORD(context[1])=context[2];
    return 1;
}
