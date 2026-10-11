/* Test host formatted-output boundary; preserves varargs without printing. */
#include <stdint.h>
#include <stdarg.h>
static void copy(uint8_t *out,const char *s,unsigned n){for(unsigned i=0;i<n;i++)out[i]=0;for(unsigned i=0;i+1<n&&s[i];i++)out[i]=s[i];}
void fixture_skater_print(void *context,const char *format,...){
 uint32_t *log=context;uint8_t *row=(uint8_t *)context+16+128*log[0]++;
 for(unsigned i=0;i<128;i++)row[i]=0;
 va_list a;va_start(a,format);const char *file=va_arg(a,const char *);uint32_t line=va_arg(a,uint32_t),value=va_arg(a,uint32_t);va_end(a);
 copy(row,format,64);copy(row+64,file,48);__builtin_memcpy(row+112,&line,4);__builtin_memcpy(row+116,&value,4);
 if(log[1])*(uint32_t *)(uintptr_t)log[1]=log[2];
}
