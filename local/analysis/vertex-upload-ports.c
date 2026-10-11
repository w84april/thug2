/* Comparison-only CRT/GPU ports. CRT has a separate arena and event log. */
#include "../../tools/script_values_memory.c"
#ifndef CRT_CONTEXT
#define CRT_CONTEXT 0x1813000u
#define INDEX_CONTROL 0x1818000u
#define INDEX_LOG 0x1819000u
#define INDEX_METHODS 0x181c000u
#define INDEX_DEVICES 0x1960000u
#endif
static void put(uint32_t a,uint32_t v){__builtin_memcpy((void *)(uintptr_t)a,&v,4);}
void *fixture_mesh_crt_allocate(uint32_t size){
 uint32_t *c=(void *)CRT_CONTEXT;if(c[8]&&!--c[8]){record(c,1,size,2,0);return 0;}
 return fixture_values_allocate(c,size,2);
}
static uint32_t *event(uint32_t op){
    uint32_t *c=(void *)INDEX_CONTROL;if(c[0]>=128)__builtin_trap();uint32_t *log=(void *)(INDEX_LOG+c[0]++*64);
    for(unsigned i=0;i<16;i++)log[i]=0;log[0]=op;return log;
}
uint32_t fixture_index_create(uint32_t device,uint32_t size,uint32_t usage,uint32_t format,uint32_t pool,uint32_t output,uint32_t shared){
    uint32_t *c=(void *)INDEX_CONTROL;if(c[1]>=8||size>0x7000)__builtin_trap();
    uint32_t p=INDEX_DEVICES+c[1]++*0x8000,*log=event(1);
    uint32_t args[]={device,size,usage,format,pool,shared,word(output),p,c[2],c[5]};
    for(unsigned i=0;i<10;i++)log[1+i]=args[i];
    if(c[5]){put(p,INDEX_METHODS);put(output,p);}return c[2];
}
uint32_t fixture_index_lock(uint32_t device,uint32_t offset,uint32_t size,uint32_t output,uint32_t flags){
    uint32_t *c=(void *)INDEX_CONTROL,*log=event(2);uint32_t data=device+0x100+c[7];
    uint32_t args[]={device,offset,size,flags,c[3],data,c[6]};for(unsigned i=0;i<7;i++)log[1+i]=args[i];
    if(c[6])put(output,data);
    if(c[8]){put(c[8]+20,c[9]);put(c[8]+12,c[10]);put(c[8]+8,c[11]);put(c[8]+24,c[12]);}
    return c[3];
}
uint32_t fixture_index_unlock(uint32_t device){uint32_t *c=(void *)INDEX_CONTROL,*log=event(3);log[1]=device;log[2]=c[4];if(c[8])log[3]=word(c[8]+24);return c[4];}
