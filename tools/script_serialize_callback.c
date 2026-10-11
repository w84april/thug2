#include <stdint.h>
void fixture_serialize_callback(void) {
    uint32_t *c=(uint32_t *)(uintptr_t)0x1800400, count=c[0], mode=c[1], value=c[3];
    uint32_t *node=(uint32_t *)(uintptr_t)c[8+count], *log=c+0xc0+count*6;
    log[0]=(uintptr_t)node; log[1]=mode;
    for(unsigned i=0;i<4;++i)log[i+2]=node[i];
    c[0]=count+1;
    if(mode==1)node[2]^=value;
    if(mode==2)node[3]=0;
    if(mode==3)*(uint8_t *)node=16;
    if(mode==4)node[2]=0;
    if(mode==5)node[1]=value;
}
