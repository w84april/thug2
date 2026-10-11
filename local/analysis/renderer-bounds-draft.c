#include <stdint.h>
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
/* 004b4760. Capture all source words before writing. X is a raw MOV;
 * Y, Z and radius pass through FLD/FSTP and quiet signaling NaNs. */
void *thug_model_geometry_sphere_pc_draft(void *geometry,void *out){
    void *instance=pointer(geometry,0x4c),*header=instance?pointer(instance,0x58):0;
    if(header){
        uint32_t r=quiet(word(header,0x70)),x=word(header,0x64),z=quiet(word(header,0x6c)),y=quiet(word(header,0x68));
        put(out,4,y);put(out,0,x);put(out,8,z);put(out,12,r);
    }else{put(out,4,0);put(out,8,0);put(out,12,0x461c4000);put(out,0,0);}
    return out;
}
/* 0048de90. Return the caller's output, irrespective of the virtual's result. */
void *thug_model_geometry_sphere_draft(void *geometry,void *out){
    typedef struct{uintptr_t unused[17];void *(*sphere)(void *,void *);} Methods;
    ((const Methods *)pointer(geometry,0))->sphere(geometry,out);return out;
}
#define R thug_platform_round_x87_single
/* 004bae30. The list supplies radii; the returned fourth word is a diameter.
 * Preserve the x87 PC24 significands, wider exponents and original spills.
 * A nonzero part count requires a valid nonempty circular part list. */
void *thug_model_renderer_sphere_pc_draft(void *renderer,void *out){
    uint16_t count;__builtin_memcpy(&count,(uint8_t *)renderer+0x46,2);
    if(!count){for(unsigned i=0;i<4;i++)put(out,i*4,0);return out;}
    void *head=pointer(renderer,0x10),*node=head?pointer(head,4):0;
    uint32_t current[4],next[4];
    thug_model_geometry_sphere_draft(pointer(pointer(node,0),0),current);
    head=pointer(renderer,0x10);node=pointer(node,4);
    while(node!=head){
        thug_model_geometry_sphere_draft(pointer(pointer(node,0),0),next);
        double nx=number(next,0);
        float dx=(float)R(nx-number(current,0));
        float dy=(float)R((double)number(next,4)-number(current,4));
        float dz=(float)R((double)number(next,8)-number(current,8));
        float dr=(float)R((double)number(next,12)-number(current,12));
        double squared=R(R(R((double)dz*dz)+R((double)dy*dy))+R((double)dx*dx));
        float distance=(float)R(__builtin_sqrt(squared));
        if(R((double)number(next,12)+distance)<=number(current,12)){
            /* TEST AH,41 / JNP includes ordered equality and excludes NaNs. */
        }else if(R((double)number(current,12)+distance)<=number(next,12)){
            put(current,0,quiet(next[0]));for(unsigned i=1;i<4;i++)current[i]=next[i];
        }else{
            double sx=R(nx+number(current,0)),sy=R((double)number(next,4)+number(current,4));
            float sz=(float)R((double)number(next,8)+number(current,8));
            float sr=(float)R((double)number(next,12)+number(current,12));
            double ratio=R((double)dr/distance),px=R((double)dx*ratio);
            float py=(float)R((double)dy*ratio),pz=(float)R((double)dz*ratio);
            float x=(float)R(px+sx),y=(float)R((double)py+sy);
            double z=R((double)pz+sz);
            put_number(current,8,(float)R(z*0.5));
            put_number(current,0,(float)R((double)x*0.5));
            put_number(current,4,(float)R((double)y*0.5));
            put_number(current,12,(float)R(R((double)sr+distance)*0.5));
        }
        node=pointer(node,4);
    }
    float diameter=(float)R((double)number(current,12)*2.0);
    put(out,0,quiet(current[0]));put(out,4,current[1]);put_number(out,12,diameter);put(out,8,current[2]);return out;
}
/* 00492f30. Cache invalidation bit is set only after the virtual returns.
 * Both copying sequences read each word immediately before its write. */
void *thug_model_renderer_sphere_draft(void *renderer,void *out){
    if(!(((uint8_t *)renderer)[0x44]&1)){
        typedef struct{uintptr_t unused[12];void *(*sphere)(void *,void *);} Methods;
        uint32_t temp[4];void *value=((const Methods *)pointer(renderer,0))->sphere(renderer,temp);
        for(unsigned i=0;i<4;i++)put(renderer,0x34+i*4,word(value,i*4));
        ((uint8_t *)renderer)[0x44]|=1;
    }
    for(unsigned i=0;i<4;i++)put(out,i*4,word(renderer,0x34+i*4));return out;
}
