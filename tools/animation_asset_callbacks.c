/* Test-only diagnostic observer. Mutations model an external I/O producer and
 * asset scheduler at a deterministic boundary; they are not game commands. */
#include <stdint.h>
#include <stdarg.h>
void fixture_animation_diagnostics(void *context,const char *format,...) {
    uint32_t *p=context,n=p[0]++,hash=0;
    for (const unsigned char *s=(const unsigned char *)format;*s;++s) hash=hash*33+*s;
    uint32_t kind= format[17]=='w' ? 1 : format[17]=='g' ? 2 : 3;
    va_list args;va_start(args,format);
    uint32_t a=va_arg(args,uint32_t),b=kind==3 ? 0 : va_arg(args,uint32_t);va_end(args);
    uint32_t *row=p+16+n*8;
    row[0]=hash;row[1]=kind;row[2]=a;row[3]=b;
    row[4]=p[2] ? *(uint32_t *)(uintptr_t)p[2] : 0;
    row[5]=row[6]=row[7]=0;
    if (kind==1 && p[1]) *(uint8_t *)(uintptr_t)p[1]=1;
    if (p[2] && n==p[3]) *(uint32_t *)(uintptr_t)p[2]=4;
    if (p[4] && n==p[6]) *(uint32_t *)(uintptr_t)p[4]=p[5];
}
