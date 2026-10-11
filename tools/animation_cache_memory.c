/* Test-only extension of the existing heap adapter. Named-heap selection and
 * contiguous availability are host allocator services, not game callbacks. */
#include "script_values_memory.c"
void fixture_animation_cache_scope(uint32_t *context,uint32_t enter) {
    if(enter==7)record(context,5,0x8f21a798,1,context[9]);
    fixture_values_scope(context,enter);
}
uint32_t fixture_animation_cache_available(uint32_t *context) {
    uint32_t result=context[8];record(context,4,result,0,0);return result;
}
