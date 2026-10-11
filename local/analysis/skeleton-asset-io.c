/* Comparison-only resident-file provider. Not original game code and not a
 * production browser filesystem. Async completion is dispatched by the test
 * after load returns, through the recovered original asset callback. */
#include <stdint.h>
static uint32_t get(uint32_t p){uint32_t v;__builtin_memcpy(&v,(void *)(uintptr_t)p,4);return v;}
static void record(uint32_t *c,uint32_t op,uint32_t a,uint32_t b,uint32_t d,const char *name){
    if(c[3]>=64)__builtin_trap();
    uint32_t *r=(void *)(uintptr_t)(c[4]+c[3]++*320),file=c[2],asset=c[7];
    r[0]=op;r[1]=a;r[2]=b;r[3]=d;r[4]=c[0];r[5]=c[1];r[6]=file;r[7]=get(file+0x14);
    r[8]=get(file+8);r[9]=get(file+12);r[10]=get(file+16);
    r[11]=get(asset+8);r[12]=get(asset+0x24);r[13]=get(c[6]+8);r[14]=get(asset+0x20);r[15]=get(asset+0x10);
    uint8_t *text=(uint8_t *)(r+16);for(unsigned i=0;i<256;i++)text[i]=0;
    if(name){unsigned i=0;do{if(i==256)__builtin_trap();text[i]=(uint8_t)name[i];}while(name[i++]);}
}
void *fixture_io_open(uint32_t *c,const char *name,uint32_t sync,uint32_t priority){
    record(c,1,sync,priority,0,name);return c[5]?0:(void *)(uintptr_t)c[2];
}
uint32_t fixture_io_size(uint32_t *c,void *file){record(c,2,(uintptr_t)file,0,0,0);return c[1];}
uint32_t fixture_io_read(uint32_t *c,void *file,void *out,uint32_t width,uint32_t count){
    record(c,3,(uintptr_t)out,width,count,0);
    if((uintptr_t)file!=c[2]||width!=1||count!=c[1])__builtin_trap();
    for(uint32_t i=0;i<count;i++)((uint8_t *)out)[i]=((const uint8_t *)(uintptr_t)c[0])[i];return count;
}
uint8_t fixture_io_close(uint32_t *c,void *file){record(c,4,(uintptr_t)file,0,0,0);return 1;}
