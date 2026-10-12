#include <stdint.h>
#include <stdarg.h>
void fixture_walk_floor_print(void *context,const char *format,...){
 uint32_t *c=context,n=c[0]++;uint8_t *row=(uint8_t *)context+16+n*128;
 for(unsigned i=0;i<128;i++)row[i]=0;
 for(unsigned i=0;i<63&&format[i];i++)row[i]=format[i];
 va_list args;va_start(args,format);
 if(format[0]=='T'){
  *(uint32_t *)(row+64)=va_arg(args,uint32_t);
  for(unsigned i=0;i<6;i++){double v=va_arg(args,double);__builtin_memcpy(row+72+i*8,&v,8);}
 }else{
  const char *file=va_arg(args,const char *);uint32_t line=va_arg(args,uint32_t);const char *message=va_arg(args,const char *);
  for(unsigned i=0;i<31&&file[i];i++)row[64+i]=file[i];for(unsigned i=0;i<28&&message[i];i++)row[96+i]=message[i];
  __builtin_memcpy(row+124,&line,4);
 }va_end(args);
 if(c[1])*(uint32_t *)(uintptr_t)c[1]=c[2];
}
