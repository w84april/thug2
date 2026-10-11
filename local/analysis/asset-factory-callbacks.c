/* Test-only virtual dispatch witnesses, never shipped as class loaders. */
#include <stdint.h>
#include <stdarg.h>
#define CONTROL ((uint32_t *)(uintptr_t)0x1806500)
static uint32_t word(uint32_t at){uint32_t v;__builtin_memcpy(&v,(void *)(uintptr_t)at,4);return v;}
static void set(uint32_t at,uint32_t v){__builtin_memcpy((void *)(uintptr_t)at,&v,4);}
static void record(uint32_t op,uint32_t self,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){
    uint32_t *p=CONTROL;if(p[0]>=128)__builtin_trap();uint32_t *r=(void *)(uintptr_t)(p[1]+p[0]++*80);
    r[0]=op;r[1]=self;r[2]=a;r[3]=b;r[4]=c;r[5]=d;r[6]=e;r[7]=0;
    for(unsigned i=0;i<8;i++)r[8+i]=word(self+i*4);
    r[16]=word(p[9]+0x28);r[17]=word(p[9]+0x34);r[18]=word(p[10]+8);r[19]=word(self+0x34);
}
uint32_t fixture_asset_load(uint32_t a,uint32_t name,uint32_t async,uint32_t x,uint32_t y,uint32_t z,uint32_t memory){
    (void)memory;record(1,a,name,async,x,y,z);set(a+16,CONTROL[3]);set(a+8,4);return CONTROL[2];
}
uint32_t fixture_asset_dispose(uint32_t a,uint32_t flags,uint32_t memory){
    (void)memory;record(2,a,flags,0,0,0,0);set(a+0x18,word(a+0x18)^0x55aa55aa);return a;
}
uint32_t fixture_asset_data(uint32_t a){record(3,a,0,0,0,0,0);return word(a+16);}
uint32_t fixture_asset_ready(uint32_t a){
    record(4,a,0,0,0,0,0);CONTROL[6]++;
    if(CONTROL[7])set(a+16,CONTROL[7]);
    *(uint8_t *)(uintptr_t)CONTROL[8]=1;
    return CONTROL[6]>CONTROL[5];
}
void fixture_asset_diagnostic(uint32_t context,const char *message,...){
    va_list args;va_start(args,message);uint32_t a=va_arg(args,uint32_t),b=va_arg(args,uint32_t);va_end(args);
    (void)context;uint32_t count=CONTROL[11]++;if(count>=32)__builtin_trap();
    uint32_t *r=(void *)((uint8_t *)CONTROL+0x300+count*16);
    r[0]=message[17]=='w'?1:2;r[1]=a;r[2]=b;r[3]=0;
}
