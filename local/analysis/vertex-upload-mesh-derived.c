#include "../../src/graphics/mesh.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static void put_half(void *p,unsigned o,uint16_t v){__builtin_memcpy((uint8_t *)p+o,&v,2);}
static uint32_t take(const uint8_t **p){uint32_t v=word(*p,0);*p+=4;return v;}
static void copy(void *destination,const void *source,uint32_t bytes){
    uint8_t *d=destination;const uint8_t *s=source;uint32_t n=bytes&~3u;
    for(uint32_t i=0;i<n;i+=4)put(d,i,word(s,i));for(uint32_t i=n;i<bytes;i++)d[i]=s[i];
}
/* New host port for original CRT malloc624031. The existing CRT-release port
 * remains in thug_mesh_crt_heap; this must not use the game allocator. */
void *(*thug_mesh_crt_allocate_draft)(uint32_t);
static void *crt_allocate(uint32_t n){if(!thug_mesh_crt_allocate_draft)__builtin_trap();return thug_mesh_crt_allocate_draft(n);}
typedef struct {uint32_t unused[27];uint32_t (*create_index)(void *,uint32_t,uint32_t,uint32_t,uint32_t,void **,uint32_t);} IndexDeviceMethods;
typedef struct {uint32_t unused[11];int32_t (*lock)(void *,uint32_t,uint32_t,void **,uint32_t);uint32_t (*unlock)(void *);} IndexMethods;
/* 004d4270: device HRESULT is ignored; CPU bytes and registry still allocate.
 * Valid callers supply successful CRT allocations. The final word is retained. */
void *thug_mesh_index_buffer_construct_draft(void *p,uint32_t size,uint32_t usage,uint32_t format){
    put(p,12,0);const IndexDeviceMethods *methods=(const void *)thug_mesh_device->methods;
    methods->create_index(thug_mesh_device,size,usage|8,format,0,(void **)((uint8_t *)p+12),0);
    put(p,0,size);put(p,4,usage);put(p,8,format);put(p,16,(uintptr_t)crt_allocate(size));
    ThugMeshResourceLink *link=crt_allocate(12),*head=thug_mesh_index_registry;
    link->value=p;link->next=head;link->previous=0;thug_mesh_index_registry=link;
    if(head)head->previous=link;return p;
}
/* 004d4300: upload the CPU copy only if the GPU lock succeeds. Alwaysreturn0. */
uint32_t thug_mesh_index_buffer_upload_draft(void *p){
    void *device=pointer(p,12);const IndexMethods *methods=pointer(device,0);void *out;
    if(methods->lock(device,0,0,&out,0)>=0){
        copy(out,pointer(p,16),word(p,0));device=pointer(p,12);methods=pointer(device,0);methods->unlock(device);
    }return 0;
}
/* 004de420: search material values by their own key, preserving iterator state
 * and the original early stop on a null value. This is not generic key lookup. */
void *thug_mesh_find_material_draft(void *header,uint32_t key){
    ThugObjectLookupTable *table=pointer(header,0x18);if(!table)return 0;
    table->iteration_bucket=0xffffffff;table->iteration_node=0;
    for(;;){
        table=pointer(header,0x18);if(!thug_object_table_next(table)||!table->iteration_node||!table->iteration_node->value)return 0;
        void *material=table->iteration_node->value;if(word(material,0)==key)return material;
    }
}
/* Original global FVF substitutions at775b64..775b78, supplied by runtime. */
uint32_t thug_mesh_vertex_formats_draft[6];
void (*thug_mesh_vertex_load_pending_draft)(void *,const void *,uint32_t,void *,const ThugMemory *);
void thug_mesh_vertex_load_draft(void *,const void *,uint32_t,void *);
uint32_t thug_mesh_shader_code_draft(uint32_t);
uint32_t thug_mesh_shader_skip_draft(const uint8_t **);
uint8_t thug_mesh_shader_conversion_enabled_draft;
void (*thug_mesh_bounds_pending_draft)(void *);
/* Partial4d5cc0: the standard vertex path now returns after shader selection
 * and temporary stream release. Compression/alternate loading/conversion trap. */
void thug_mesh_buffer_prefix_draft(void *mesh,const uint8_t **input,uint32_t material_key,void *header,void *aux,const ThugMemory *m){
    const uint8_t *p=*input;uint8_t *b=mesh;
    for(unsigned slot=0;slot<8;slot++){
        uint16_t count=half(p,0);p+=2;put_half(b,0x24+slot*2,count);
        if(count){
            void *buffer=crt_allocate(24);if(buffer)thug_mesh_index_buffer_construct_draft(buffer,(uint32_t)count*2,0,0x65);
            put(b,0x54+slot*4,(uintptr_t)buffer);copy(pointer(buffer,16),p,(uint32_t)count*2);p+=(uint32_t)half(b,0x24+slot*2)*2;
            thug_mesh_index_buffer_upload_draft(buffer);
        }
    }
    b[0x18]=*p++;put_half(b,0x22,half(p,0));p+=2;b[0x1a]=*p++;
    uint32_t sizes[3];void *data[3];
    for(unsigned stream=0;stream<b[0x1a];stream++){
        if(stream>=3)__builtin_trap();uint8_t compressed=*p++;sizes[stream]=take(&p);
        data[stream]=m->allocate(m->context,sizes[stream],1);copy(data[stream],p,sizes[stream]);p+=sizes[stream];
        if(compressed)__builtin_trap(); /* missing4d47f0, no manufactured decoder */
    }
    for(unsigned slot=0;slot<2;slot++){
        uint32_t code=take(&p);put(b,0x38+slot*4,code>=1&&code<=6?thug_mesh_vertex_formats_draft[6-code]:code);
    }
    b[0x1d]=*p++;b[0x1c]=*p++;b[0x1e]=*p++;uint8_t palette=*p++;
    put(b,0x74,0);put(b,0x78,0);
    if(palette){uint32_t n=half(b,0x22);void *v=m->allocate(m->context,n,1);put(b,0x8c,(uintptr_t)v);copy(v,p,n);p+=n;aux=0;put(b,0x74,0x200);put(b,0x78,word(b,0x78)|2);}
    uint32_t passes=take(&p);
    if((int32_t)passes>1){void *v=m->allocate(m->context,passes*4,1);put(b,0x48,(uintptr_t)v);copy(v,p,passes*4);p+=passes*4;}
    void *material=thug_mesh_find_material_draft(header,material_key);put(b,0x14,(uintptr_t)material);
    if(material&&(((uint8_t *)material)[0x20]&0x10))put(b,0,word(b,0)|0x100);
    b[0x1a]=1;
    if(!word(b,0x38)){put(b,0x74,0x200);__builtin_trap();} /* missing4d5940 */
    if(thug_mesh_vertex_load_pending_draft){thug_mesh_vertex_load_pending_draft(mesh,data[0],sizes[0],aux,m);__builtin_trap();}
    thug_mesh_vertex_load_draft(mesh,data[0],sizes[0],aux);
    uint32_t shader=take(&p);
    if(shader==1){put(mesh,0x44,thug_mesh_shader_skip_draft(&p));if(thug_mesh_shader_conversion_enabled_draft)__builtin_trap();}
    else put(mesh,0x44,thug_mesh_shader_code_draft(shader));
    *input=p;for(unsigned stream=0;stream<b[0x1a];stream++)m->release(m->context,data[stream]);
}
/* Partial4c6650: stops before4d5900 mesh bounds, preserving the caller
 * cursor until the full routine returns. No parser return or mesh registration. */
void thug_model_sector_mesh_prefix_draft(void *sector,const uint8_t **input,const ThugMemory *m){
    uint8_t *geometry=pointer(sector,0x14);const uint8_t *p=*input;put(sector,4,take(&p));
    p+=4;put(sector,0x1c,take(&p));put(geometry,0x40,take(&p));
    for(unsigned i=0;i<3;i++)put(geometry,0x14+i*4,take(&p));put(geometry,0x20,0x3f800000);
    for(unsigned i=0;i<3;i++)put(geometry,0x24+i*4,take(&p));put(geometry,0x30,0x3f800000);p+=16;
    if(word(sector,0x1c)&0x800000)p+=40;
    if(!word(geometry,0x40))__builtin_trap();
    void *mesh=m->allocate(m->context,216,1);if(mesh)thug_render_mesh_initialize(mesh);
    p+=40;uint32_t flags=take(&p);
    if(flags&0x400)put(mesh,0,word(mesh,0)|2);if(flags&0x20000)put(mesh,0,word(mesh,0)|0x20000);
    uint32_t material_key=take(&p),strips=take(&p);if(strips>8)__builtin_trap();
    for(unsigned i=0;i<strips;i++){
        uint32_t n=take(&p);m->temp_scope(m->context,2);void *indices=m->allocate(m->context,n*2,1);m->temp_scope(m->context,0);copy(indices,p,n*2);p+=n*2;
    }
    put_half(mesh,0x20,0);void *header=pointer(pointer(geometry,0x34),0x280);
    thug_mesh_buffer_prefix_draft(mesh,&p,material_key,header,0,m);
    if(thug_mesh_bounds_pending_draft)thug_mesh_bounds_pending_draft(mesh);
    __builtin_trap();
}
