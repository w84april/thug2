#include "decal.h"
#include "../platform/math.h"
#include "../core/random.h"
#include <stddef.h>

_Static_assert(sizeof(ThugGeometryStack)==0x4008,"Geometry work stack");
_Static_assert(offsetof(ThugDecalProjection,type)==0x38,"Projection type");
_Static_assert(offsetof(ThugDecalProjection,flag)==0x40,"Projection flag");
_Static_assert(offsetof(ThugDecalBuffer,vertices)==0x3410,"Triangle records");
_Static_assert(sizeof(ThugDecalBuffer)==0x7c10,"Decal buffer");
_Static_assert(sizeof(ThugRenderMesh)==0xd8,"Mesh storage");
_Static_assert(offsetof(ThugVertexBufferDeviceMethods,lock)==0x2c,"Vertex-buffer lock slot");

static uint32_t read_word(const void *p) { uint32_t value;__builtin_memcpy(&value,p,4);return value; }
static void write_word(void *p,uint32_t value) { __builtin_memcpy(p,&value,4); }
ThugObjectLookupTable *thug_decal_buffers;
/* 004b9a60. Keep table iteration state and untouched UV/timer storage. The
 * browser supplies initialized host memory and a single CRT random stream. */
ThugDecalBuffer *thug_decal_find_or_create(void *texture,const ThugMemory *memory) {
    thug_decal_buffers->iteration_bucket=UINT32_MAX;thug_decal_buffers->iteration_node=NULL;
    for (;;) {
        ThugObjectLookupTable *table=thug_decal_buffers;
        if (!thug_object_table_next(table) || !table->iteration_node || !table->iteration_node->value) break;
        ThugDecalBuffer *buffer=table->iteration_node->value;
        ThugRenderMaterial *material=(ThugRenderMaterial *)(uintptr_t)read_word((uint8_t *)buffer+0x1c0c);
        if (read_word(material->storage+0x30)==(uintptr_t)texture) return buffer;
    }
    ThugRenderMaterial *material=memory->allocate(memory->context,0x110,1);
    thug_render_material_initialize(material);
    write_word(material->storage+0x20,texture?4:0);
    uint32_t first=thug_crt_random(),second=thug_crt_random();
    write_word(material->storage+0x30,(uintptr_t)texture);write_word(material->storage,first*second);
    write_word(material->storage+8,1);material->storage[0xd]=1;material->storage[0x11]=0x14;
    write_word(material->storage+0x80,5);
    for (uint32_t i=0x40;i<0x4c;i+=4) write_word(material->storage+i,0x3f000000);
    write_word(material->storage+0x90,0x20002);write_word(material->storage+0xe0,0);material->storage[0x10]=1;
    ThugDecalBuffer *buffer=memory->allocate(memory->context,0x7c10,1);
    write_word((uint8_t *)buffer+0x1c00,0);write_word((uint8_t *)buffer+0x1c0c,(uintptr_t)material);
    for (uint32_t i=0;i<256;++i) buffer->remaining[i]=0;
    for (uint32_t i=0;i<768;++i) {
        buffer->vertices[i].position[0]=0;buffer->vertices[i].color=0x80808080;
        buffer->vertices[i].position[1]=0;buffer->vertices[i].position[2]=0;
    }
    uint32_t key=(uintptr_t)buffer;thug_object_table_insert(thug_decal_buffers,&key,buffer,memory);return buffer;
}
/* The original REP operations copy a word at a time before their byte tail.
 * A bytewise copy or memmove changes propagation for overlapping storage. */
static void copy_forward(void *destination,const void *source,uint32_t size) {
    uint8_t *out=destination;const uint8_t *in=source;uint32_t i=0;
    for(;i<size/4*4;i+=4)write_word(out+i,read_word(in+i));
    for(;i<size;++i)out[i]=in[i];
}
/* 0x00490cd0. First free slot wins; otherwise retain the first largest signed
 * wrapping age. The original reads slot zero even when count is zero. */
uint32_t thug_decal_choose_slot(const ThugDecalBuffer *buffer,uint32_t count) {
    int32_t greatest=(int32_t)(buffer->initial[0]-buffer->remaining[0]);uint32_t best=0;
    for(uint32_t i=0;i<count;++i) {
        uint32_t remaining=buffer->remaining[i];if(!remaining)return i;
        int32_t age=(int32_t)(buffer->initial[i]-remaining);
        if(age>greatest) { greatest=age;best=i; }
    }
    return best;
}
/* 0x00490d20. Padding has a deliberate byte pattern, not uninitialized data. */
void thug_geometry_stack_initialize(ThugGeometryStack *stack) {
    stack->cursor=0;stack->width=0;
    for(uint32_t i=0;i<sizeof(stack->data);i+=4)write_word(stack->data+i,0x03030303);
}
/* 0x00490d50 / 0x00490d80. Valid callers keep the fixed stack within capacity. */
void thug_geometry_stack_push(ThugGeometryStack *stack,const void *record) {
    copy_forward(stack->data+stack->cursor,record,stack->width);
    stack->cursor+=stack->width;
}
void thug_geometry_stack_pop(ThugGeometryStack *stack,void *record) {
    uint32_t width=stack->width;stack->cursor-=width;
    copy_forward(record,stack->data+stack->cursor,width);
}
/* 0x00490e40. The last three padding bytes remain untouched. */
ThugDecalProjection *thug_decal_projection_initialize(ThugDecalProjection *p) {
    for(uint32_t i=0;i<0x40;i+=4)write_word((uint8_t *)p+i,0);
    p->from[3]=1;p->to[3]=1;p->type=0x54628ed7;p->flag=0;return p;
}
/* 0x004b7f30. Retain all position, color and UV bits in a degenerate triangle. */
void thug_decal_collapse_triangle(ThugDecalBuffer *buffer,uint32_t slot) {
    ThugDecalVertex *first=&buffer->vertices[slot*3];
    copy_forward(first+1,first,24);copy_forward(first+2,first,24);
}
/* 0x004d1a90. Only the original constructor's fields are initialized. */
ThugRenderMaterial *thug_render_material_initialize(ThugRenderMaterial *p) {
    uint8_t *b=p->storage;
    write_word(b+8,0);
    for(uint32_t i=0;i<4;++i)write_word(b+0xf0+i*4,0);
    b[0xe]=0;b[0xf]=0;write_word(b+0x18,0);b[0x11]=0;
    for(uint32_t i=0;i<4;++i)write_word(b+0xc0+i*4,0x10001);
    for(uint32_t i=0;i<4;++i) {
        write_word(b+0x20+i*4,0);write_word(b+0x30+i*4,0);write_word(b+0xd0+i*4,0);
        write_word(b+0xa0+i*8,0x40400000);write_word(b+0xa4+i*8,0x40400000);
    }
    return p;
}
/* 0x004d4be0. Mesh format/layout setup; no GPU resource is allocated here. */
ThugRenderMesh *thug_render_mesh_initialize(ThugRenderMesh *p) {
    uint8_t *b=(uint8_t *)p;write_word(b,0);b[0x1a]=1;b[0x19]=0;
    for(uint32_t i=0;i<3;++i) { write_word(b+0xcc+i*4,0);write_word(b+0xbc+i*4,0); }
    for(uint32_t i=0;i<8;++i) { write_word(b+0x54+i*4,0);b[0x24+i*2]=0;b[0x25+i*2]=0; }
    static const uint8_t words[]={0xc8,0x8c,0x48,0x4c,0x90,0x38,0x44,0xac,0xb0,0xb4,0xb8,0x94,0xa0};
    for(uint32_t i=0;i<sizeof(words);++i)write_word(b+words[i],0);
    b[0x1c]=0;b[0x1e]=0;b[0x1d]=0;b[0x18]=0;
    b[0x1f]=0xff;write_word(b+0x9c,UINT32_MAX);write_word(b+0x98,UINT32_MAX);
    write_word(b,read_word(b)|0x40);b[0x1b]=0xff;write_word(b+0x50,5);return p;
}
/* 0x004a2ba0 / 0x0049f540. Optional texture tables retain generic lookup rules. */
ThugRenderMesh *thug_render_geometry_mesh(const ThugRenderGeometry *geometry) { return geometry->mesh; }
void *thug_texture_dictionary_find(const ThugTextureDictionary *dictionary,uint32_t name) {
    return dictionary->textures?thug_object_table_find(dictionary->textures,&name,1):NULL;
}
/* 0x004d4090. Write the CPU address before changing the remembered lock range.
 * Raw output writes preserve aliases with size and range words. */
uint32_t thug_vertex_buffer_lock(ThugVertexBuffer *buffer,uint32_t offset,uint32_t size,void **output,uint32_t flags) {
    write_word(output,(uint32_t)(uintptr_t)buffer->data+offset);
    buffer->last_offset=offset;buffer->last_size=size;
    if(!size)buffer->last_size=buffer->size;
    buffer->last_flags=flags;
    if(flags&0x2000)return buffer->device->methods->lock(buffer->device,offset,size,output,flags);
    return 0;
}
/* 0x004d42f0. The offset, size and flags arguments are unused. */
uint32_t thug_index_buffer_lock(const ThugIndexBuffer *buffer,uint32_t offset,uint32_t size,void **output,uint32_t flags) {
    (void)offset;(void)size;(void)flags;write_word(output,(uint32_t)(uintptr_t)buffer->data);return 0;
}
/* 0x00528560. Four sequential raw-word copies, including overlapping output. */
void *thug_component_copy_direction(const void *component,void *output) {
    copy_forward(output,(const uint8_t *)component+0x48,16);return output;
}

#define R24 thug_platform_round_x87_single
/* 0x004b7fa0. Ordered exclusions deliberately retain the original degenerate
 * and unordered cases. Numerators spill separately from the final cross term. */
uint8_t thug_decal_segments_overlap(float ax,float ay,float bx,float by,float cx,float cy,float dx,float dy) {
    float abx=bx-ax,aby=by-ay,acx=ax-cx,acy=ay-cy;
    double dcx=R24((double)cx-dx),dcy=R24((double)cy-dy);
    float numerator=(float)R24(R24(acx*dcy)-R24(acy*dcx));
    float denominator=(float)R24(R24(aby*dcx)-R24(dcy*abx));
    if(denominator>0) { if(numerator<0||numerator>denominator)return 0; }
    else if(numerator>0||numerator<denominator)return 0;
    double other=R24(R24((double)acy*abx)-R24((double)acx*aby));
    if(denominator>0) { if(other<0||other>denominator)return 0; }
    else if(other>0||other<denominator)return 0;
    return 1;
}
/* 0x004b88d0. Original square-edge tests, vertex tests, then corner-in-triangle
 * tests. Do not replace this with a conventional predicate: degenerate segment
 * acceptance and distinct wide/stored cross products are observable. */
uint8_t thug_decal_triangle_in_square(float ax,float ay,float bx,float by,float cx,float cy) {
    if((ax<-1&&bx<-1&&cx<-1)||(ax>1&&bx>1&&cx>1)||
       (ay<-1&&by<-1&&cy<-1)||(ay>1&&by>1&&cy>1))return 0;
    static const float corners[4][2]={{-1,-1},{1,-1},{1,1},{-1,1}};
    for(uint32_t i=0;i<4;++i) {
        const float *p=corners[i],*q=corners[(i+1)%4];
        if(thug_decal_segments_overlap(ax,ay,bx,by,p[0],p[1],q[0],q[1])||
           thug_decal_segments_overlap(bx,by,cx,cy,p[0],p[1],q[0],q[1])||
           thug_decal_segments_overlap(cx,cy,ax,ay,p[0],p[1],q[0],q[1]))return 1;
    }
    if((ax>=-1&&ax<=1&&ay>=-1&&ay<=1)||(bx>=-1&&bx<=1&&by>=-1&&by<=1)||
       (cx>=-1&&cx<=1&&cy>=-1&&cy<=1))return 1;
    double abx=R24((double)ax-bx),aby=R24((double)ay-by);
    double cbx=R24((double)cx-bx),cby=R24((double)cy-by);
    float stored_cbx=(float)cbx,stored_cby=(float)cby;
    float reference=(float)R24(R24(aby*cbx)-R24(cby*abx));
    for(uint32_t i=0;i<4;++i) {
        double px=R24((double)corners[i][0]-bx),py=R24((double)corners[i][1]-by);
        double cross=R24(R24(py*stored_cbx)-R24(stored_cby*px));
        if(!(R24(cross*reference)>=0))continue;
        double acx=R24((double)ax-cx),acy=R24((double)ay-cy);
        float bcx=(float)R24((double)bx-cx),bcy=(float)R24((double)by-cy);
        px=R24((double)corners[i][0]-cx);py=R24((double)corners[i][1]-cy);
        double ref=R24(R24((double)bcy*(float)acx)-R24(acy*bcx));
        cross=R24(R24(py*acx)-R24((float)acy*px));
        if(!(R24(cross*ref)>=0))continue;
        double bax=R24((double)bx-ax),bay=R24((double)by-ay);
        float cax=(float)R24((double)cx-ax),cay=(float)R24((double)cy-ay);
        px=R24((double)corners[i][0]-ax);py=R24((double)corners[i][1]-ay);
        ref=R24(R24((double)cay*(float)bax)-R24(bay*cax));
        cross=R24(R24(py*bax)-R24((float)bay*px));
        if(R24(cross*ref)>=0)return 1;
    }
    return 0;
}

ThugGeometryStack thug_decal_work_stack;            /* 0x006fc4a0 */
uint8_t thug_decal_scratch_vertices[6][128];        /* 0x007052c0 */
float thug_decal_area_threshold=82944;                   /* 0x0067ddf0 */
static float read_float(const uint8_t *p) { float value;__builtin_memcpy(&value,p,4);return value; }
static void write_float(uint8_t *p,float value) { __builtin_memcpy(p,&value,4); }
static float midpoint(float a,float b) { return (float)R24(R24(R24((double)b-a)*0.5)+a); }
/* 0x004b8220, including the fall-through region Ghidra labels 004b8232.
 * Each step emits one triangle or pushes four smaller triangles. The caller
 * drains the fixed stack and supplies fitting output/vertex-format storage. */
uint8_t thug_decal_subdivide(void **output,const ThugRenderMesh *format) {
    ThugGeometryStack *stack=&thug_decal_work_stack;
    if(!stack->cursor)return 0;
    uint8_t *ca=thug_decal_scratch_vertices[0],*bc=thug_decal_scratch_vertices[1],*ab=thug_decal_scratch_vertices[2];
    uint8_t *a=thug_decal_scratch_vertices[3],*b=thug_decal_scratch_vertices[4],*c=thug_decal_scratch_vertices[5];
    thug_geometry_stack_pop(stack,c);thug_geometry_stack_pop(stack,b);thug_geometry_stack_pop(stack,a);
    double dx=R24((double)read_float(b)-read_float(a));
    double dy=R24((double)read_float(b+4)-read_float(a+4)),dz=R24((double)read_float(b+8)-read_float(a+8));
    float stored_y=(float)dy,stored_z=(float)dz;
    float ex=(float)R24((double)read_float(c)-read_float(a)),ey=(float)R24((double)read_float(c+4)-read_float(a+4));
    double ez=R24((double)read_float(c+8)-read_float(a+8));
    float cross_x=(float)R24(R24(ez*dy)-R24(ey*dz)),cross_y=(float)R24(R24(dz*ex)-R24(ez*dx));
    double cross_z=R24(R24(ey*dx)-R24(dy*ex));
    double area=R24(R24(R24(cross_z*cross_z)+R24((double)cross_y*cross_y))+R24((double)cross_x*cross_x));
    uint32_t width=stack->width;
    if(area>thug_decal_area_threshold) {
        copy_forward(ab,a,width);write_float(ab,(float)R24(R24(dx*0.5)+read_float(a)));
        copy_forward(bc,b,width);write_float(ab+4,(float)R24(R24((double)stored_y*0.5)+read_float(a+4)));
        write_float(ab+8,(float)R24(R24((double)stored_z*0.5)+read_float(a+8)));copy_forward(ca,c,width);
        for(uint32_t i=0;i<12;i+=4)write_float(bc+i,midpoint(read_float(b+i),read_float(c+i)));
        for(uint32_t i=0;i<12;i+=4)write_float(ca+i,midpoint(read_float(c+i),read_float(a+i)));
        uint32_t offset=format->color_offset;
        if(offset)for(uint32_t i=offset;i<offset+4;++i) {
            ab[i]=(uint8_t)(a[i]+((int)b[i]-a[i])/2);
            bc[i]=(uint8_t)(b[i]+((int)c[i]-b[i])/2);
            ca[i]=(uint8_t)(c[i]+((int)a[i]-c[i])/2);
        }
        offset=format->uv_offset;
        if(offset)for(uint32_t i=offset;i<offset+8;i+=4) {
            write_float(ab+i,midpoint(read_float(a+i),read_float(b+i)));
            write_float(bc+i,midpoint(read_float(b+i),read_float(c+i)));
            write_float(ca+i,midpoint(read_float(c+i),read_float(a+i)));
        }
        const uint8_t *vertices[]={a,ab,ca,ab,b,bc,ab,bc,ca,ca,bc,c};
        for(uint32_t i=0;i<12;++i)thug_geometry_stack_push(stack,vertices[i]);
    } else {
        const uint8_t *vertices[]={a,b,c};
        for(uint32_t i=0;i<3;++i) {
            copy_forward((void *)(uintptr_t)read_word(output),vertices[i],width);
            write_word(output,read_word(output)+width);
        }
    }
    return 1;
}
#undef R24

uint32_t thug_decal_reserved_slots=128; /* 0067dde0, original initial value 128 */
uint32_t thug_decal_fade_step=8;      /* 0067dde4, original initial value 8 */
static void store_word(uint8_t *p,uint32_t v) { __builtin_memcpy(p,&v,4); }
/* 00490ec0. EAX supplies elapsed time; one cdecl stack argument is the buffer. */
void thug_decal_advance_lifetime(uint32_t elapsed,ThugDecalBuffer *buffer) {
    uint8_t *data=(uint8_t *)buffer;int32_t active=0;
    store_word(data+0x1c00,UINT32_MAX);
    for(uint32_t i=0;i<256;++i) {
        uint32_t remaining=buffer->remaining[i];
        if((int32_t)remaining<0)continue;
        remaining-=elapsed;buffer->remaining[i]=remaining;
        if((int32_t)remaining<=0) {
            buffer->remaining[i]=0;thug_decal_collapse_triangle(buffer,i);
        } else { store_word(data+0x1c00,i);++active; }
    }
    if(active<(int32_t)(256-thug_decal_reserved_slots))return;
    int32_t greatest=(int32_t)(buffer->initial[0]-buffer->remaining[0]),selected=-1;
    for(uint32_t i=0;i<256;++i)if(buffer->initial[i]&&buffer->remaining[i]) {
        int32_t age=(int32_t)(buffer->initial[i]-buffer->remaining[i]);
        if(age>=greatest) {greatest=age;selected=(int32_t)i;}
    }
    if(selected<0)return;
    /* Reload the selected record each iteration: zeroing its counter can change
     * which later records compare equal during this same sweep. */
    for(uint32_t i=0;i<256;++i) {
        if(buffer->remaining[i]!=buffer->remaining[selected]||buffer->initial[i]!=buffer->initial[selected])continue;
        uint32_t step=thug_decal_fade_step,zero=0;
        uint32_t offsets[]={0x1003+i*12,0x1007+i*12,0x100b+i*12,0x341f+i*72,0x3437+i*72,0x344f+i*72};
        for(uint32_t j=0;j<6;++j) {
            uint8_t alpha=data[offsets[j]];
            if(!alpha)++zero;
            else {int32_t next=(int32_t)((uint32_t)alpha-step);data[offsets[j]]=next>0?(uint8_t)next:0;}
        }
        if(zero==6)buffer->remaining[i]=0;
    }
}

#include "../platform/math.h"
#include "../core/number.h"
#define R24 thug_platform_round_x87_single
/* Layout/capacity also confirmed by the 150-element constructor at 644c90. */
ThugDecalLight thug_decal_lights[150];                  /* 006faf80 */
int32_t thug_decal_light_count;                     /* 006faef4 */
static uint32_t load_word(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4);return v;}
static float load_float(const uint8_t *p) {float v;__builtin_memcpy(&v,p,4);return v;}
static double distance_squared(const uint8_t *position,const ThugDecalLight *light) {
    double x=R24((double)load_float(position)-light->position[0]);
    double y=R24((double)load_float(position+4)-light->position[1]);
    double z=R24((double)load_float(position+8)-light->position[2]);
    return R24(R24(R24(z*z)+R24(y*y))+R24(x*x));
}
/* 0048f620. Select at most three lights using only the first position. */
void thug_decal_light_colors(const uint32_t *source,uint32_t *output,const float *positions,const float *normal,uint32_t count) {
    uint32_t selected[3],n=0;const uint8_t *p=(const uint8_t *)positions;
    for(int32_t i=0;i<thug_decal_light_count&&n<3;++i) {
        const ThugDecalLight *l=&thug_decal_lights[i];
        if(normal) {
            double x=R24((double)load_float(p)-l->position[0]);
            double y=R24((double)load_float(p+4)-l->position[1]);
            double z=R24((double)load_float(p+8)-l->position[2]);
            double dot=R24(R24(R24(y*normal[1])+R24(z*normal[2]))+R24(x*normal[0]));
            if(!(dot<=0))continue;
        }
        if(l->intensity>0&&R24((double)l->radius*l->radius)>=distance_squared(p,l))selected[n++]=(uint32_t)i;
    }
    uint8_t *out=(uint8_t *)output;const uint8_t *in=(const uint8_t *)source;
    if(!n) {for(uint32_t i=0;i<count;++i)store_word(out+i*4,load_word(in+i*4));return;}
    for(uint32_t i=0;i<count;++i) {
        double sum[3]={0,0,0};uint32_t changed=0;
        for(uint32_t j=0;j<n;++j) {
            const ThugDecalLight *l=&thug_decal_lights[selected[j]];
            float squared=(float)distance_squared(p+i*16,l);
            if(squared<R24((double)l->radius*l->radius)) {
                double strength=R24(R24(R24((double)l->radius-R24(__builtin_sqrt(squared)))/l->radius)*l->intensity);
                for(uint32_t k=0;k<3;++k)sum[k]=R24(sum[k]+R24(strength*((l->color>>(k*8))&255)));
                changed=1;
            }
        }
        if(changed) {
            uint32_t color=load_word(in+i*4),result=color&0xff000000;
            sum[1]=(float)sum[1];sum[2]=(float)sum[2];
            for(uint32_t k=0;k<3;++k) {
                double value=R24(sum[k]+((color>>(k*8))&255));
                if(value>255)value=255;
                result|=(thug_truncate_double_low_word(value)&255)<<(k*8);
            }
            store_word(out+i*4,result);
        }
    }
}
/* 004b87b0. Lighting uses the first vertex position for all three colors. */
void thug_decal_refresh_colors(ThugDecalBuffer *buffer) {
    uint8_t *data=(uint8_t *)buffer;
    for(int32_t i=0;i<=(int32_t)load_word(data+0x1c00);++i) {
        uint8_t *first=data+0x3410+i*72;uint32_t colors[3];float positions[12]={0};
        for(uint32_t j=0;j<3;++j) {
            colors[j]=load_word(data+0x1000+i*12+j*4);
            for(uint32_t k=0;k<3;++k)__builtin_memcpy(positions+j*4+k,first+k*4,4);
        }
        thug_decal_light_colors((const uint32_t *)(data+0x1000+i*12),colors,positions,0,3);
        for(uint32_t j=0;j<3;++j) {
            uint32_t c=colors[j];store_word(first+j*24+12,(c&0xff00ff00)|((c&255)<<16)|((c>>16)&255));
        }
    }
}
#undef R24
