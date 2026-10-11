/* Test-only terminal CRT heap/GPU services; no game helper is replaced. */
#include <stdint.h>
static uint32_t word(uint32_t p) {uint32_t v;__builtin_memcpy(&v,(void *)(uintptr_t)p,4);return v;}
void fixture_projection_crt_free(uint32_t *context,void *allocation) {
    uint32_t a=(uintptr_t)allocation,*log=(uint32_t *)(uintptr_t)(context[3]+context[2]++*48);
    uint32_t valid=a>=context[4]&&a<=context[5]-16;
    log[0]=2;log[1]=a;log[2]=1;log[3]=0;
    for(uint32_t i=0;i<4;++i)log[4+i]=valid?word(a+i*4):0;
    log[8]=valid;log[9]=context[6];log[10]=context[6]?word(context[6]):0;log[11]=0;
}
uint32_t fixture_projection_get(uint32_t *device,uint32_t stream,uint32_t *buffer,uint32_t *offset,uint32_t *stride) {
    if(stream)__builtin_trap();
    *buffer=0;*offset=0;*stride=0;
    ++*(uint32_t *)(uintptr_t)device[1];return 0;
}
