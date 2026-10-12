#include <stdint.h>
#include <stdarg.h>
/* Record all original diagnostic arguments in the same normalized test buffer. */
void fixture_walk_critical_print(void *context,const char *format,...){
 uint32_t *c=context,n=c[0]++;uint8_t *row=(uint8_t *)context+16+n*192;
 for(unsigned i=0;i<192;i++)row[i]=0;
 for(unsigned i=0;i<63&&format[i];i++)row[i]=format[i];
 va_list args;va_start(args,format);const char *file=va_arg(args,const char *);uint32_t line=va_arg(args,uint32_t);
 for(unsigned i=0;i<31&&file[i];i++)row[64+i]=file[i];
 if(format[0]=='D'){for(unsigned i=0;i<3;i++){double value=va_arg(args,double);__builtin_memcpy(row+96+i*8,&value,8);}}
 else{const char *message=va_arg(args,const char *);for(unsigned i=0;i<88&&message[i];i++)row[96+i]=message[i];}
 __builtin_memcpy(row+188,&line,4);va_end(args);
 if(c[1])*(uint32_t *)(uintptr_t)c[1]=c[2];
}
