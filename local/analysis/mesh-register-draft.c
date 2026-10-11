#include "../../src/core/lookup.h"
#include "../../src/core/bounds.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
/* 004d5900. All three center words are captured before any destination write.
 * The last two original arguments are unused, even when they are null. */
void thug_mesh_set_bounds_draft(void *mesh,const void *center,uint32_t radius,const void *minimum,const void *maximum){
    (void)minimum;(void)maximum;uint32_t x=word(center,0),y=word(center,4),z=word(center,8);
    put(mesh,4,x);put(mesh,8,y);put(mesh,12,z);put(mesh,16,radius);
}
/* Distinct identity from the mesh-list sentinel at64a438. */
const uintptr_t thug_model_mesh_node_methods_draft[1]={0};
/* 004b52f0. A valid list and successful allocation are original contracts. */
void thug_model_geometry_append_mesh_draft(void *geometry,void *mesh,const ThugMemory *m){
    m->temp_scope(m->context,2);void *node=thug_allocate_zeroed(20,m);
    if(node){put(node,0,(uintptr_t)thug_model_mesh_node_methods_draft);put(node,4,(uintptr_t)mesh);put(node,8,0);put(node,12,(uintptr_t)node);put(node,16,(uintptr_t)node);}
    void *head=pointer(geometry,0x38);put(node,16,word(head,16));put(node,12,(uintptr_t)head);
    put(pointer(head,16),12,(uintptr_t)node);put(head,16,(uintptr_t)node);m->temp_scope(m->context,0);
}
#define R thug_platform_round_x87_single
/* 004de340. Preserve x87 single-precision significands with wide exponents.
 * Z's difference and X's half-extent spill to float32 at the original points;
 * squared extents are accumulated Z, Y, then X. */
void thug_model_scene_data_bounds_draft(void *p){
    double dx=R((double)number(p,0x54)-number(p,0x44));
    double dy=R((double)number(p,0x58)-number(p,0x48));
    float dz=(float)R((double)number(p,0x5c)-number(p,0x4c));
    float x=(float)R(dx*0.5);double y=R(dy*0.5),z=R((double)dz*0.5);
    float cx=(float)R((double)x+number(p,0x44)),cy=(float)R(y+number(p,0x48)),cz=(float)R(z+number(p,0x4c));
    put_number(p,0x64,cx);put_number(p,0x68,cy);put_number(p,0x6c,cz);
    double squared=R(R(R(z*z)+R(y*y))+R((double)x*x));
    put_number(p,0x70,(float)R(__builtin_sqrt(squared)));
}
