/* Test-only native predicate: records actual parsed parameters and script owner,
 * optionally mutates the first integer, and returns a configured full word. */
#include <stdint.h>
uint32_t fixture_parser_predicate(uint32_t *parameters, void *script) {
    uint32_t *context=(uint32_t *)(uintptr_t)0x1800400;
    uint32_t *log=context+4+context[0]++*6;
    uint32_t *first=(uint32_t *)(uintptr_t)parameters[1];
    log[0]=(uintptr_t)parameters;log[1]=(uintptr_t)script;log[2]=(uintptr_t)first;
    log[3]=first?first[1]:0;log[4]=first?(*(uint8_t *)first)>>1:0;log[5]=first?first[2]:0;
    if(first&&log[4]==1)first[2]^=context[2];
    return context[1];
}
