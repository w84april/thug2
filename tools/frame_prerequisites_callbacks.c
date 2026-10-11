/* Diagnostic output is a host boundary. Record its arguments and optionally
 * mutate the same state that the original caller reads after it returns. */
#include <stdint.h>
#include <stdarg.h>
static uint32_t hash(const char *s) { uint32_t h=0;while(*s)h=h*33+(unsigned char)*s++;return h; }
void fixture_frame_print(uint32_t *context,const char *format,...) {
    uint32_t n=context[0]++,*record=context+8+n*8;
    const uint32_t *physics=(const void *)(uintptr_t)context[1];
    va_list args;va_start(args,format);
    record[0]=hash(format);record[1]=hash(va_arg(args,const char *));
    record[2]=va_arg(args,unsigned);record[3]=hash(va_arg(args,const char *));
    va_end(args);
    record[4]=physics[0x318/4];record[5]=physics[0x31c/4];
    record[6]=context[2];record[7]=context[3];
    if(context[2])*(uint32_t *)(uintptr_t)context[2]=context[3];
}
