#include "decal.h"
#include "mesh.h"
#include "../core/d3dx.h"
#include "../core/matrix.h"
#include "../core/vector.h"
#include "../core/random.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4);return v;}
static uint16_t half(const void *p) {uint16_t v;__builtin_memcpy(&v,p,2);return v;}
static void store(void *p,uint32_t v) {__builtin_memcpy(p,&v,4);}
static void *pointer(const void *p) {return (void *)(uintptr_t)word(p);}
static void copy_words(void *out,const void *in,uint32_t words) {
    for(uint32_t i=0;i<words;++i)store((uint8_t *)out+i*4,word((const uint8_t *)in+i*4));
}
static double length3(double x,double y,double z) {
    return R24(__builtin_sqrt(R24(R24(R24(x*x)+R24(y*y))+R24(z*z))));
}
static uint8_t projected_triangle(const ThugDecalVertex *triangle) {
    float xy[6];
    for(uint32_t i=0;i<3;++i)for(uint32_t j=0;j<2;++j)
        xy[i*2+j]=(float)R24(R24((double)triangle[i].uv[j]+triangle[i].uv[j])-1);
    return thug_decal_triangle_in_square(xy[0],xy[1],xy[2],xy[3],xy[4],xy[5]);
}
static void save_uv(ThugDecalBuffer *buffer,uint32_t slot,const ThugDecalVertex *triangle) {
    uint8_t *out=(uint8_t *)buffer+0x1c10+slot*24;
    for(uint32_t i=0;i<3;++i)copy_words(out+i*8,triangle[i].uv,2);
}
/* 0x004b9c30. Both lists are original arguments; this body uses only the first.
 * The descriptor is argument THREE and its previous-point path mutates both
 * endpoints. Recovered geometry/math/allocation/subdivision/mesh cleanup run
 * intact; GPU and initialized heap services are supplied by the platform. */
ThugDecalBuffer *thug_decal_project(ThugRenderGeometry *const *geometries,const void *unused,
    ThugDecalProjection *projection,const ThugMemory *memory) {
    (void)unused;
    double dz=R24((double)projection->to[2]-projection->from[2]);
    float dy=(float)R24((double)projection->to[1]-projection->from[1]);
    float dx=(float)R24((double)projection->to[0]-projection->from[0]);
    float direction[3]={dx,dy,(float)dz};
    double length=length3(dx,dy,dz);float distance=(float)length;
    if(length>0) {
        double inverse=R24(1/length);
        direction[0]=(float)R24((double)dx*inverse);direction[1]=(float)R24((double)dy*inverse);
        direction[2]=(float)R24(dz*inverse);
    }
    float cosine=(float)thug_platform_cos(projection->angle),up[4],height;
    if(projection->previous) {
        double z=R24((double)projection->from[2]-projection->previous[2]);
        double y=R24((double)projection->from[1]-projection->previous[1]);
        float x=(float)R24((double)projection->from[0]-projection->previous[0]);
        up[0]=x;up[1]=(float)y;up[2]=(float)z;up[3]=1;
        height=(float)length3(x,y,z);
        projection->from[0]=(float)R24((double)projection->from[0]-x);
        projection->from[1]=(float)R24((double)projection->from[1]-y);
        projection->from[2]=(float)R24((double)projection->from[2]-z);
        projection->from[3]=(float)R24((double)projection->from[3]-1);
        projection->to[0]=(float)R24((double)projection->to[0]-x);
        projection->to[1]=(float)R24((double)projection->to[1]-y);
        projection->to[2]=(float)R24((double)projection->to[2]-z);
        projection->to[3]=(float)R24((double)projection->to[3]-1);
        thug_vector_normalize(up);
    } else {
        if(__builtin_fabsf(direction[1])>0.5f) {
            double angle=projection->rotation;
            if(projection->rotation==0)angle=R24(R24((double)thug_crt_random()*0x1.921fb6p+2f)*0x1.0002p-15f);
            up[0]=(float)thug_platform_sin(angle);up[1]=0;up[2]=(float)thug_platform_cos(angle);
        } else {up[0]=0;up[1]=1;up[2]=0;}
        up[3]=1;height=projection->width;
    }
    float view[16],ortho[16],transform[16];
    thug_d3dx_look_at_rh(view,projection->from,projection->to,up);
    thug_d3dx_ortho_rh(ortho,projection->width,height,0.1f,distance);
    thug_matrix_multiply(transform,view,ortho);
    ThugDecalBuffer *buffer=NULL;
    for(;*geometries;++geometries) {
        uint8_t *container=(uint8_t *)thug_render_geometry_mesh(*geometries);
        if(!container)continue;
        for(uint32_t mesh_index=0;mesh_index<word(container+0x40);++mesh_index) {
            ThugRenderMesh *mesh=((ThugRenderMesh **)pointer(container+0x3c))[mesh_index];
            uint8_t *m=(uint8_t *)mesh;
            if(mesh->flags&2)continue;
            void *vertices,*indices;
            thug_vertex_buffer_lock(pointer(m+0xcc),0,0,&vertices,0x10);
            thug_index_buffer_lock(pointer(m+0x54),0,0,&indices,0x10);
            uint32_t a=half(indices),b=half((uint8_t *)indices+2),c=0;
            for(uint32_t n=2;n<half(m+0x24);a=b,b=c,++n) {
                c=half((uint8_t *)indices+n*2);
                if(a==b||a==c||b==c)continue;
                uint32_t index[3]={a,b,c};float projected[3][3];
                for(uint32_t i=0;i<3;++i)
                    thug_d3dx_transform_coordinate(projected[i],(float *)((uint8_t *)vertices+index[i]*mesh->stride),transform);
                if((projected[0][2]<-1&&projected[1][2]<-1&&projected[2][2]<-1)||
                   (projected[0][2]>1&&projected[1][2]>1&&projected[2][2]>1))continue;
                if(!thug_decal_triangle_in_square(projected[0][0],projected[0][1],projected[1][0],projected[1][1],projected[2][0],projected[2][1]))continue;
                if(!buffer) {
                    uint8_t *texture=projection->texture;void *image=pointer(texture+0x10);
                    if(word(texture+8)&1)image=pointer(image);
                    buffer=thug_decal_find_or_create(image,memory);
                }
                uint32_t slot=thug_decal_choose_slot(buffer,256);
                ThugDecalVertex *triangle=buffer->vertices+slot*3;
                for(uint32_t i=0;i<3;++i)copy_words(triangle[i].position,(uint8_t *)vertices+index[i]*mesh->stride,3);
                double cx=R24((double)triangle[2].position[0]-triangle[0].position[0]);
                double cy=R24((double)triangle[2].position[1]-triangle[0].position[1]);
                double cz=R24((double)triangle[2].position[2]-triangle[0].position[2]);
                double bz=R24((double)triangle[1].position[2]-triangle[0].position[2]);
                float by=(float)R24((double)triangle[1].position[1]-triangle[0].position[1]);
                float bx=(float)R24((double)triangle[1].position[0]-triangle[0].position[0]);
                float normal[3]={(float)R24(R24(bz*cy)-R24((double)by*cz)),
                    (float)R24(R24((double)bx*cz)-R24(bz*cx)),(float)R24(R24((double)by*cx)-R24((double)bx*cy))};
                thug_d3dx_normalize3(normal,normal);
                double dot=R24(R24(R24((double)normal[2]*direction[2])+R24((double)normal[1]*direction[1]))+R24((double)normal[0]*direction[0]));
                /* Ordered <= rejects; unordered results pass this original test. */
                if(__builtin_fabs(dot)<=cosine)continue;
                buffer->remaining[slot]=projection->lifetime>=0?
                    thug_truncate_double_low_word(R24((double)projection->lifetime*1000)):0x7fffffff;
                for(uint32_t i=0;i<3;++i)for(uint32_t j=0;j<2;++j)
                    triangle[i].uv[j]=(float)R24(R24((double)projected[i][j]+1)*0.5);
                save_uv(buffer,slot,triangle);
                for(uint32_t i=0;i<3;++i)
                    triangle[i].color=(word((uint8_t *)vertices+index[i]*mesh->stride+mesh->color_offset)&0xffffff)|0x80000000;
                double ex=R24((double)triangle[1].position[0]-triangle[0].position[0]);
                double ey=R24((double)triangle[1].position[1]-triangle[0].position[1]);
                double ez=R24((double)triangle[1].position[2]-triangle[0].position[2]);
                float fz=(float)R24((double)triangle[2].position[2]-triangle[0].position[2]);
                float fy=(float)R24((double)triangle[2].position[1]-triangle[0].position[1]);
                double fx=R24((double)triangle[2].position[0]-triangle[0].position[0]);
                float area_z=(float)R24(R24((double)fy*ex)-R24(fx*ey));
                float area_y=(float)R24(R24(fx*ez)-R24((double)fz*ex));
                double area_x=R24(R24((double)fz*ey)-R24((double)fy*ez));
                double area=R24(R24(R24(area_x*area_x)+R24((double)area_y*area_y))+R24((double)area_z*area_z));
                thug_decal_area_threshold=(float)R24(area*0x1p-7);
                thug_geometry_stack_initialize(&thug_decal_work_stack);thug_decal_work_stack.width=24;
                for(uint32_t i=0;i<3;++i)thug_geometry_stack_push(&thug_decal_work_stack,triangle+i);
                uint8_t *subdivided=memory->allocate(memory->context,0x2000,1);
                for(uint32_t i=0;i<0x2000;i+=4)store(subdivided+i,0);
                ThugRenderMesh *format=memory->allocate(memory->context,0xd8,1);
                thug_render_mesh_initialize(format);format->color_offset=12;format->uv_offset=16;
                void *end=subdivided;while(thug_decal_subdivide(&end,format)) {}
                uint8_t accepted=0;
                for(ThugDecalVertex *part=(ThugDecalVertex *)subdivided;(void *)part!=end;part+=3) {
                    if(!projected_triangle(part))continue;
                    accepted=1;
                    buffer->remaining[slot]=thug_truncate_double_low_word(R24((double)projection->lifetime*1000));
                    buffer->initial[slot]=thug_truncate_double_low_word(R24((double)projection->lifetime*1000));
                    triangle=buffer->vertices+slot*3;
                    for(uint32_t i=0;i<3;++i)copy_words(triangle[i].position,part[i].position,3);
                    for(uint32_t i=0;i<3;++i)copy_words(triangle[i].uv,part[i].uv,2);
                    save_uv(buffer,slot,triangle);
                    for(uint32_t i=0;i<3;++i)triangle[i].color=(part[i].color&0xffffff)|0x80000000;
                    for(uint32_t i=0;i<3;++i) {
                        uint32_t gray=triangle[i].color&255;
                        store((uint8_t *)buffer+0x1000+slot*12+i*4,0x80000000|gray|gray<<8|gray<<16);
                    }
                    store((uint8_t *)buffer+0x800+slot*4,word(&projection->height));
                    store((uint8_t *)buffer+0xc00+slot*4,word(&projection->width));
                    slot=thug_decal_choose_slot(buffer,256);
                }
                if(!accepted) {buffer->remaining[slot]=0;thug_decal_collapse_triangle(buffer,slot);}
                thug_mesh_destroy(format,memory);memory->release(memory->context,format);memory->release(memory->context,subdivided);
            }
        }
    }
    return buffer;
}
#undef R24
