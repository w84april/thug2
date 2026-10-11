/* Test-only formatted diagnostic observation; no input/game behavior here. */
#include <stdint.h>
#include <stdarg.h>
void fixture_input_command_print(uint32_t *context,const char *format,...){
    va_list args;va_start(args,format);const char *file=va_arg(args,const char *);
    uint32_t line=va_arg(args,unsigned);double value=va_arg(args,double);va_end(args);
    uint8_t *row=(uint8_t *)context+16+128*context[0]++;
    for(unsigned i=0;i<128;i++)row[i]=0;
    for(unsigned i=0;format[i]&&i<31;i++)row[i]=format[i];
    for(unsigned i=0;file[i]&&i<63;i++)row[32+i]=file[i];
    __builtin_memcpy(row+96,&line,4);__builtin_memcpy(row+104,&value,8);
    if(context[1])*(uint32_t *)(uintptr_t)context[1]=context[2];
}
