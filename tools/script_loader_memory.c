/* Test-only heap: successful allocations, with top-of-arena releases rewinding
 * storage. This bounds whole-file encoder scratch without replacing any codec.
 * Out-of-order releases remain reserved until the fixture resets. */
#include "script_values_memory.c"
void *fixture_loader_allocate(uint32_t *context, uint32_t size, uint32_t route) {
    uint32_t header=context[0], address=header+16;
    if(address+size+16>context[1])__builtin_trap();
    uint32_t *h=(uint32_t *)(uintptr_t)header;
    h[0]=context[8];h[1]=size;h[2]=route;h[3]=0xabcdef01;
    context[8]=address;context[0]=(address+size+3)&~3u;
    uint8_t *bytes=(uint8_t *)(uintptr_t)address;
    for(uint32_t i=0;i<size;i++)bytes[i]=0xa5;
    record(context,1,size,route,address);return bytes;
}
void fixture_loader_release(uint32_t *context,void *pointer) {
    record(context,2,(uintptr_t)pointer,0,0);
    if((uintptr_t)pointer==context[8]&&pointer){
        context[0]=(uintptr_t)pointer-16;
        context[8]=*(uint32_t *)(uintptr_t)context[0];
    }
}
