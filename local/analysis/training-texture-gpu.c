/* Comparison-only heap/GPU port, not a renderer or recovered game function. */
#include "../../tools/script_values_memory.c"
#define BASE 0x1000000u
#define CONTROL (BASE+0xf1300)
#define GPU_LOG (BASE+0xf1400)
#define TEXTURES (BASE+0xf3000)
#define TEXTURE_METHODS (BASE+0xf1200)
static uint32_t *at(uint32_t p){return (uint32_t *)(uintptr_t)p;}
static void put(uint32_t p,uint32_t v){__builtin_memcpy((void *)(uintptr_t)p,&v,4);}
void *fixture_texture_allocate(uint32_t *c,uint32_t size,uint32_t route){
    void *p=fixture_values_allocate(c,size,route);put((uintptr_t)p-16,BASE+0x600);return p;
}

static uint32_t *event(uint32_t op){
    uint32_t *c=at(CONTROL);if(c[0]>=200)__builtin_trap();uint32_t *log=at(GPU_LOG+c[0]++*64);
    for(unsigned i=0;i<16;i++)log[i]=0;log[0]=op;log[15]=word(BASE+0x28);return log;
}
uint32_t fixture_texture_create(uint32_t device,uint32_t w,uint32_t h,uint32_t mips,uint32_t usage,uint32_t format,uint32_t pool,uint32_t output,uint32_t shared){
    uint32_t *c=at(CONTROL);if(c[1]>=32)__builtin_trap();uint32_t p=TEXTURES+c[1]++*0x1000;
    uint32_t *log=event(1);uint32_t args[]={device,w,h,mips,usage,format,pool,output,shared,p};
    for(unsigned i=0;i<10;i++)log[1+i]=args[i];put(p,TEXTURE_METHODS);put(output,p);return 0;
}
uint32_t fixture_texture_lock(uint32_t p,uint32_t level,uint32_t output,uint32_t rect,uint32_t flags){
    if(level>=8)__builtin_trap();uint32_t bytes=p+0x100+level*0x100,pitch=word(CONTROL+8);
    uint32_t *log=event(2);uint32_t args[]={p,level,rect,flags,pitch,bytes};
    for(unsigned i=0;i<6;i++)log[1+i]=args[i];put(output,pitch);put(output+4,bytes);return 0;
}
uint32_t fixture_texture_unlock(uint32_t p,uint32_t level){uint32_t *log=event(3);log[1]=p;log[2]=level;return 0;}

uint32_t fixture_texture_scope(const void *p){if((uintptr_t)p<0x1b00000||(uintptr_t)p>=0x2e00000)__builtin_trap();uint32_t *log=event(4);log[1]=(uintptr_t)p;return 1;}
