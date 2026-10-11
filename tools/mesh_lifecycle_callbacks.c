/* Test-only terminal graphics/CRT interfaces. */
#include <stdint.h>
static uint32_t word(uint32_t p) {uint32_t v;__builtin_memcpy(&v,(void *)(uintptr_t)p,4);return v;}
static void record(uint32_t *control,uint32_t kind,uint32_t a,uint32_t b,uint32_t c,uint32_t d) {
    uint32_t *out=(uint32_t *)((uint8_t *)control+0x1800+control[0]++*48),mesh=control[5];
    out[0]=kind;out[1]=a;out[2]=b;out[3]=c;out[4]=d;
    out[5]=word(mesh);out[6]=word(mesh+0xbc);out[7]=word(mesh+0xcc);
    for(uint32_t i=0;i<4;++i)out[8+i]=kind==3&&a>=0x1800000&&a<0x1840000-16?word(a+i*4):0;
    if(kind==3&&a==control[2]&&control[2]) {
        *(uint32_t *)(uintptr_t)control[3]=control[4];control[2]=0;
    }
}
uint32_t fixture_mesh_get(uint32_t *device,uint32_t stream,uint32_t *buffer,uint32_t *offset,uint32_t *stride) {
    uint32_t *control=(uint32_t *)(uintptr_t)device[1];
    *buffer=control[1];*offset=7;*stride=16;
    record(control,0,(uintptr_t)device,stream,control[1],0);return 0x80004005;
}
uint32_t fixture_mesh_set(uint32_t *device,uint32_t stream,uint32_t buffer,uint32_t offset,uint32_t stride) {
    uint32_t *control=(uint32_t *)(uintptr_t)device[1];
    record(control,1,(uintptr_t)device,stream,buffer,offset|stride);return 0x80004005;
}
uint32_t fixture_mesh_release(uint32_t *object) {
    record((uint32_t *)(uintptr_t)object[1],2,(uintptr_t)object,0,0,0);return 17;
}
void fixture_mesh_crt_free(uint32_t *control,void *allocation) {
    record(control,3,(uintptr_t)allocation,0,0,0);
}
