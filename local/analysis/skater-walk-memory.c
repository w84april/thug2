/* Derived test allocator: context[8]==1 returns null without advancing the heap. */
/* Test-only heap adapter. Snapshot payload/header words and a watched list
 * pointer at each call, so disposal order and relinking are observable. */
#include <stdint.h>
static uint32_t word(uint32_t address) {
    const uint8_t *p=(const uint8_t *)(uintptr_t)address;
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
static void record(uint32_t *context,uint32_t kind,uint32_t a,uint32_t b,uint32_t c) {
    uint32_t *log=(uint32_t *)(uintptr_t)(context[3]+context[2]++*48);
    uint32_t pointer=kind==2?a:c;
    uint32_t valid=pointer>=context[4]&&pointer<=context[5]-16;
    log[0]=kind;log[1]=a;log[2]=b;log[3]=c;
    for(unsigned i=0;i<4;i++)log[4+i]=valid?word(pointer+i*4):0;
    log[8]=valid;log[9]=context[6];log[10]=context[6]?word(context[6]):0;log[11]=0;
}
void *fixture_values_allocate(uint32_t *context,uint32_t size,uint32_t route) {
    if(context[8]==1){record(context,1,size,route,0);return 0;}
    uint32_t address=context[0];
    if(address+size+16>context[1])__builtin_trap();
    context[0]=(address+size+19)&~3u;
    uint8_t *bytes=(uint8_t *)(uintptr_t)address;
    for(uint32_t i=0;i<size;i++)bytes[i]=0xa5;
    record(context,1,size,route,address);return bytes;
}
void fixture_values_release(uint32_t *context,void *pointer) {
    record(context,2,(uintptr_t)pointer,0,0);
}
void fixture_values_scope(uint32_t *context,uint32_t enter) {
    context[7]=enter;record(context,3,enter,0,0);
}
