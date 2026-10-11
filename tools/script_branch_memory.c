/* Test-only heap service for script random-choice cache records. */
#include <stdint.h>
static void record(uint32_t *context,uint32_t kind,uint32_t a,uint32_t b,uint32_t c) {
    uint32_t *log=(uint32_t *)(uintptr_t)(context[3]+context[2]++*16);
    log[0]=kind;log[1]=a;log[2]=b;log[3]=c;
}
void *fixture_branch_allocate(uint32_t *context,uint32_t size,uint32_t route) {
    uint32_t address=context[0];
    if(address+size+16>context[1])__builtin_trap();
    context[0]+=size+16;
    uint8_t *bytes=(uint8_t *)(uintptr_t)address;
    for(uint32_t i=0;i<size;i++)bytes[i]=0xa5;
    record(context,1,size,route,address);return bytes;
}
void fixture_branch_release(uint32_t *context,void *pointer) {
    record(context,2,(uintptr_t)pointer,0,0);
}
