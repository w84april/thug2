/* Test-only observation of the external vertex-buffer Lock service. */
#include <stdint.h>
uint32_t fixture_decal_vertex_lock(uint32_t *device,uint32_t offset,uint32_t size,uint32_t *output,uint32_t flags) {
    uint32_t *control=(uint32_t *)(uintptr_t)device[1];
    uint32_t n=control[0]++,*buffer=(uint32_t *)(uintptr_t)control[5],*log=control+8+n*10;
    log[0]=(uint32_t)(uintptr_t)device;log[1]=offset;log[2]=size;
    log[3]=(uint32_t)(uintptr_t)output;log[4]=flags;log[5]=*output;
    log[6]=buffer[4];log[7]=buffer[5];log[8]=buffer[6];log[9]=0;
    if(control[2]!=UINT32_MAX)*output=control[2];
    if(control[3])*(uint32_t *)(uintptr_t)control[3]=control[4];
    return control[1];
}
