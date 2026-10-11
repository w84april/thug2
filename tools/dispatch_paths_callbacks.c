/* Observe the formatted host boundary, including its promoted double. */
#include <stdint.h>
#include <stdarg.h>
static uint32_t hash(const char *s) { uint32_t h=0;while(*s)h=h*33+(unsigned char)*s++;return h; }
void fixture_dispatch_print(uint32_t *context,const char *format,...) {
    uint32_t n=context[0]++,*row=context+8+n*10;
    const uint32_t *physics=(const void *)(uintptr_t)context[1];
    va_list args;va_start(args,format);double value=va_arg(args,double);va_end(args);
    row[0]=hash(format);__builtin_memcpy(row+1,&value,8);
    row[3]=physics[0x350/4];row[4]=physics[0x354/4];row[5]=physics[0x358/4];row[6]=physics[0x3ac/4];
    row[7]=context[2];row[8]=context[3];row[9]=context[4];
    if(context[2]&&n<context[4])*(uint32_t *)(uintptr_t)context[2]=context[3];
}
