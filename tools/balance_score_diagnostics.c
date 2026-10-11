/* Test-only diagnostic boundary. Record typed arguments and callback ordering;
 * optional mutation checks later game reads. No scoring behavior is substituted. */
#include <stdint.h>
#include <stdarg.h>
static uint32_t hash(const char *text) {
    uint32_t value=0;
    while (*text) value=value*33+(unsigned char)*text++;
    return value;
}
void fixture_balance_score_print(uint32_t *context, const char *format, ...) {
    uint32_t n=context[0]++, *record=context+8+n*12;
    const uint32_t *score=(const void *)(uintptr_t)context[1];
    for (unsigned i=0;i<12;++i) record[i]=0;
    record[0]=hash(format);
    va_list args;va_start(args,format);
    record[1]=(uint32_t)va_arg(args,int);
    if (format[0]=='b') {
        double repeat=va_arg(args,double),spin=va_arg(args,double);
        __builtin_memcpy(record+2,&repeat,8);__builtin_memcpy(record+4,&spin,8);
        record[6]=(uint32_t)va_arg(args,int);record[7]=hash(va_arg(args,const char *));
    }
    va_end(args);
    record[8]=score[0x14/4];record[9]=score[0x5c/4];record[10]=score[0x70/4];
    record[11]=((const uint8_t *)score)[0x74];
    if (context[2] && (!context[4] || context[4]==n+1))
        *(uint32_t *)(uintptr_t)context[2]=context[3];
}
/* This address belongs to the test arena, never to the recovered engine. */
uint32_t fixture_balance_event(uint32_t parameters, uint32_t script) {
    (void)parameters;(void)script;
    uint32_t *context=(void *)(uintptr_t)0x18f8200;
    const uint32_t *score=(const void *)(uintptr_t)context[4];
    uint32_t n=context[0]++, *record=context+8+n*4;
    record[0]=score[0x14/4];record[1]=score[0x60/4];record[2]=score[0x70/4];
    record[3]=((const uint8_t *)score)[0x74];
    if (context[1] && (!context[3] || !n)) *(uint32_t *)(uintptr_t)context[1]=context[2];
    return 1;
}
