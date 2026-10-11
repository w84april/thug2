#include "../../src/graphics/mesh.h"
#include "../../src/core/bounds.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint32_t take(const uint8_t **p){uint32_t v=word(*p,0);*p+=4;return v;}
static void copy(void *destination,const void *source,uint32_t bytes){
 uint8_t *d=destination;const uint8_t *s=source;uint32_t n=bytes&~3u;
 for(uint32_t i=0;i<n;i+=4)put(d,i,word(s,i));for(uint32_t i=n;i<bytes;i++)d[i]=s[i];
}
extern void (*thug_mesh_bounds_pending_draft)(void *);
void thug_mesh_set_bounds_draft(void *,const void *,uint32_t,const void *,const void *);
void thug_model_geometry_append_mesh_draft(void *,void *,const ThugMemory *);
void thug_mesh_buffer_prefix_draft(void *,const uint8_t **,uint32_t,void *,void *,const ThugMemory *);
/* Partial004c6650: the standard path now completes, including all meshes,
 * temporary index releases, recount and caller cursor. Transform and layered
 * material paths remain unavailable and trap at their original call sites. */
void thug_model_sector_mesh_prefix_draft(void *sector,const uint8_t **input,const ThugMemory *m){
    uint8_t *geometry=pointer(sector,0x14);const uint8_t *p=*input;put(sector,4,take(&p));
    uint32_t bone=take(&p);put(sector,0x1c,take(&p));put(geometry,0x40,take(&p));
    for(unsigned i=0;i<3;i++)put(geometry,0x14+i*4,take(&p));put(geometry,0x20,0x3f800000);
    for(unsigned i=0;i<3;i++)put(geometry,0x24+i*4,take(&p));put(geometry,0x30,0x3f800000);p+=16;
    if(word(sector,0x1c)&0x800000)p+=40;
    for(uint32_t mesh_index=0;mesh_index<word(geometry,0x40);mesh_index++){
        void *mesh=m->allocate(m->context,216,1);if(mesh)thug_render_mesh_initialize(mesh);
        union {uint32_t words[10];float values[10];} raw;uint32_t *bounds=raw.words;for(unsigned i=0;i<10;i++)bounds[i]=take(&p);
        uint32_t flags=take(&p);if(flags&0x400)put(mesh,0,word(mesh,0)|2);if(flags&0x20000)put(mesh,0,word(mesh,0)|0x20000);
        uint32_t key=take(&p),strips=take(&p);if(strips>8)__builtin_trap();void *indices[8]={0};
        for(unsigned i=0;i<strips;i++){
            uint32_t n=take(&p);m->temp_scope(m->context,2);indices[i]=m->allocate(m->context,n*2,1);m->temp_scope(m->context,0);copy(indices[i],p,n*2);p+=n*2;
        }
        uint16_t serial=mesh_index;__builtin_memcpy((uint8_t *)mesh+0x20,&serial,2);
        thug_mesh_buffer_prefix_draft(mesh,&p,key,pointer(pointer(geometry,0x34),0x280),0,m);
        if(thug_mesh_bounds_pending_draft){thug_mesh_bounds_pending_draft(mesh);__builtin_trap();}
        thug_mesh_set_bounds_draft(mesh,bounds,bounds[3],bounds+4,bounds+7);
        thug_bounds_expand((ThugBounds *)((uint8_t *)pointer(pointer(geometry,0x34),0x280)+0x44),raw.values+4);
        thug_bounds_expand((ThugBounds *)((uint8_t *)pointer(pointer(geometry,0x34),0x280)+0x44),raw.values+7);
        if(word(sector,0x1c)&0x800000)__builtin_trap(); /* missing4d7580 /4cebe0 */
        if(word(sector,0x1c)&0x200000)put(mesh,0,word(mesh,0)|0x200);
        thug_model_geometry_append_mesh_draft(geometry,mesh,m);((uint8_t *)mesh)[0x1f]=bone;
        /* 4d0d30's no-effect branch; optional layers are not substituted. */
        void *material=pointer(mesh,0x14);
        if(material&&((word(material,0x20)&0x8000000)||word(material,0x18)))__builtin_trap();
        for(unsigned i=0;i<8;i++)m->release(m->context,indices[i]);
    }
    uint32_t count=0;void *node=pointer(pointer(geometry,0x38),12);
    while(word(node,4)!=0xffffffff&&node){node=pointer(node,12);count++;}
    put(geometry,0x40,count);*input=p;
}
