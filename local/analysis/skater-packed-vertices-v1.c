/* Asset-scoped 004d5940 integration. No complete-function credit: the rare
 * diagnostic geometry shape is unsupported and traps. The WebGL adapter uses
 * these original rest vertices; original weighted pose/frame work is separate. */
#include <stdint.h>
#include "../../src/platform/math.h"
extern void *(*thug_mesh_crt_allocate_draft)(uint32_t);
extern void *thug_mesh_vertex_buffer_create_draft(uint32_t,uint32_t,uint32_t);
static uint32_t word(const void *p,unsigned o){uint32_t n;__builtin_memcpy(&n,(const char *)p+o,4);return n;}
static void put(void *p,unsigned o,uint32_t n){__builtin_memcpy((char *)p+o,&n,4);}
static uint16_t half(const void *p,unsigned o){uint16_t n;__builtin_memcpy(&n,(const char *)p+o,2);return n;}
static float unpack(uint32_t n,unsigned shift,unsigned width,uint32_t scale_bits){
    uint32_t mask=(1u<<width)-1,part=(n>>shift)&mask;
    int32_t value=(part&(1u<<(width-1)))?(int32_t)part-(int32_t)(1u<<width):(int32_t)part;
    float scale;__builtin_memcpy(&scale,&scale_bits,4);
    return (float)thug_platform_round_x87_single((double)value*scale);
}
void thug_mesh_load_packed_skin_v1(void *mesh,const void *input,uint32_t size,void *aux){
    (void)size;uint32_t passes=word((void *)(uintptr_t)word(mesh,0x14),8),count=half(mesh,0x22),weights=1;
    if(passes>4||(count==640&&half(mesh,0x24)==1699))__builtin_trap();
    uint8_t stride=((uint8_t *)mesh)[0x18];uint8_t *out=thug_mesh_crt_allocate_draft(count*76);put(mesh,0x94,(uintptr_t)out);
    for(uint32_t i=0;i<count;i++){
        const uint8_t *p=(const uint8_t *)input+i*stride;uint8_t *v=out+i*76;
        for(unsigned j=0;j<3;j++)put(v,j*4,word(p,j*4));
        uint32_t normal=word(p,24),weight=word(p,12);
        for(unsigned j=0;j<3;j++){
            float n=unpack(normal,j==0?0:j==1?11:22,j==2?10:11,j==2?0x3b004020:0x3a802008);
            __builtin_memcpy(v+12+j*4,&n,4);
            float w=unpack(weight,j==0?0:j==1?11:22,j==2?10:11,j==2?0x3b004020:0x3a802008);
            __builtin_memcpy(v+64+j*4,&w,4);
        }
        put(v,24,word(p,28));for(unsigned j=0;j<passes*2;j++)put(v,28+j*4,word(p,32+j*4));
        for(unsigned j=0;j<4;j++)v[60+j]=(int16_t)half(p,16+j*2)/3;
        float second,third;__builtin_memcpy(&second,v+68,4);__builtin_memcpy(&third,v+72,4);
        if(weights<2&&second!=0)weights=2;if(weights<3&&third!=0)weights=3;
    }
    put(mesh,0xa4,passes);put(mesh,0xa8,weights);
    put(mesh,0x38,(passes<<8)|0x52);((uint8_t *)mesh)[0x18]=28+passes*8;
    put(mesh,0x78,word(mesh,0x78)|1);
    put(mesh,0xcc,(uintptr_t)thug_mesh_vertex_buffer_create_draft(((uint8_t *)mesh)[0x18]*count,word(mesh,0x74),word(mesh,0x78)));
    if(aux)put(aux,8,word(aux,8)+(count*((uint8_t *)mesh)[0x18]+31&~31u));
}
