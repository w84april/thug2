/* Test-only formatted diagnostic boundary. It records the literal and the
 * score state before reset, with optional mutation to check read ordering. */
#include <stdint.h>
void fixture_score_print(uint32_t *context, const char *format, ...) {
    uint32_t *score=(uint32_t *)(uintptr_t)context[1];
    uint32_t *record=context+4+context[0]++*4, hash=0;
    for(const unsigned char *s=(const void *)format;*s;++s)hash=hash*33+*s;
    record[0]=hash;record[1]=score[0x1538/4];record[2]=score[0x54/4];record[3]=score[0x38/4];
    if(context[2])*(uint32_t *)(uintptr_t)context[2]=context[3];
}
