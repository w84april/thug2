/* Test-only native/virtual/output boundaries. Concrete script execution is in
 * the recovered module; these callbacks expose passed values and state changes. */
#include <stdint.h>
#include <stdarg.h>
#define CONTEXT ((uint32_t *)(uintptr_t)0x1830000)
static uint32_t command(uint32_t kind,void *owner,uint32_t name,uint32_t *parameters,uint32_t *script) {
    uint32_t *c=CONTEXT,*log=c+8+c[0]++*10;
    uint32_t *first=parameters?(uint32_t *)(uintptr_t)parameters[1]:0;
    log[0]=kind;log[1]=(uintptr_t)owner;log[2]=name;log[3]=(uintptr_t)parameters;log[4]=(uintptr_t)script;
    log[5]=(uintptr_t)first;log[6]=first?first[1]:0;log[7]=first?first[2]:0;log[8]=script[3];log[9]=script[50];
    if(c[2]==1){script[41]=1;script[38]=c[3];}
    if(c[2]==2)script[3]=0;
    if(c[2]==3&&first)first[2]^=c[3];
    if(c[2]==4)script[58]=c[3];
    if(c[2]==5)script[3]=c[3];
    return c[1];
}
uint32_t fixture_execute_native(uint32_t *parameters,uint32_t *script){return command(0,0,0,parameters,script);}
uint32_t fixture_execute_object(void *owner,uint32_t descriptor,uint32_t *parameters,uint32_t *script){return command(1,owner,descriptor,parameters,script);}
uint32_t fixture_execute_member(void *owner,uint32_t name,uint32_t *parameters,uint32_t *script){return command(2,owner,name,parameters,script);}
uint32_t fixture_execute_component(void *owner,uint32_t descriptor,uint32_t *parameters,uint32_t *script){return command(3,owner,descriptor,parameters,script);}
void fixture_execute_print(uint32_t *c,const char *format,...){
    uint32_t *log=c+4+c[0]++*8;va_list args;va_start(args,format);const char *text=va_arg(args,const char *);va_end(args);
    log[0]=(uintptr_t)format;log[1]=(uintptr_t)text;
    uint8_t *copy=(uint8_t *)(log+2);for(unsigned i=0;i<24;i++){copy[i]=*text;if(*text)text++;}
}
