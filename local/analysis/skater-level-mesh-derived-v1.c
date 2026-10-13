extern void thug_mesh_load_packed_skin_v1(void *,const void *,unsigned,void *);
#include "../../src/graphics/mesh.h"
extern uint32_t (*thug_scene_file_read_draft)(void *,uint32_t,uint32_t,void *);
extern uint32_t (*thug_scene_file_seek_draft)(void *,int32_t,uint32_t);
extern void *(*thug_mesh_crt_allocate_draft)(uint32_t);
extern uint32_t thug_mesh_vertex_formats_draft[6];
extern uint8_t thug_mesh_shader_conversion_enabled_draft;
void *thug_mesh_index_buffer_construct_draft(void *,uint32_t,uint32_t,uint32_t);
uint32_t thug_mesh_index_buffer_upload_draft(void *);
void *thug_mesh_find_material_draft(void *,uint32_t);
void thug_mesh_vertex_load_draft(void *,const void *,uint32_t,void *);
uint32_t thug_mesh_shader_code_draft(uint32_t);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static uint32_t take(void *file){uint32_t v;thug_scene_file_read_draft(&v,4,1,file);return v;}
static uint8_t byte(void *file){uint8_t v;thug_scene_file_read_draft(&v,1,1,file);return v;}
/* 004da6d0: PC consumes two words, then seeks over the shader payload. */
uint32_t thug_mesh_file_shader_skip_draft(void *file){
    (void)take(file);uint32_t size=take(file);thug_scene_file_seek_draft(file,(int32_t)size,1);return 0;
}
/* 004d6100 file-stream mesh loader, standard vertex path. Internal contract:
 * complete records, 1..3 streams, successful initialized allocators. Missing
 * vertex correction4d4350, packed vertices4d5940 and shader conversion4ddc00
 * explicitly trap. This routine is not counted as a complete recovery yet. */
void thug_mesh_file_parse_draft(void *mesh,void *file,uint32_t key,void *header,void *aux,uint32_t dynamic,const ThugMemory *m){
    uint8_t *b=mesh;
    for(unsigned slot=0;slot<8;slot++){
        thug_scene_file_read_draft(b+0x24+slot*2,2,1,file);uint16_t n=half(b,0x24+slot*2);
        if(n){
            void *buffer=thug_mesh_crt_allocate_draft(24);
            if(buffer)thug_mesh_index_buffer_construct_draft(buffer,(uint32_t)n*2,0,0x65);
            put(b,0x54+slot*4,(uintptr_t)buffer);
            thug_scene_file_read_draft(pointer(buffer,16),2,(uint32_t)(int32_t)(int16_t)n,file);
            thug_mesh_index_buffer_upload_draft(buffer);
        }
    }
    thug_scene_file_read_draft(b+0x18,1,1,file);thug_scene_file_read_draft(b+0x22,2,1,file);thug_scene_file_read_draft(b+0x1a,1,1,file);
    uint32_t sizes[3];void *data[3];
    for(unsigned stream=0;stream<b[0x1a];stream++){
        if(stream>=3)__builtin_trap();uint8_t correction=byte(file);sizes[stream]=take(file);
        data[stream]=m->allocate(m->context,sizes[stream],1);thug_scene_file_read_draft(data[stream],sizes[stream],1,file);
        if(correction)__builtin_trap();
    }
    for(unsigned slot=0;slot<2;slot++){uint32_t code=take(file);put(b,0x38+slot*4,code>=1&&code<=6?thug_mesh_vertex_formats_draft[6-code]:code);}
    thug_scene_file_read_draft(b+0x1d,1,1,file);thug_scene_file_read_draft(b+0x1c,1,1,file);thug_scene_file_read_draft(b+0x1e,1,1,file);
    uint8_t palette=byte(file);put(b,0x74,0);put(b,0x78,0);
    if(palette){uint32_t n=half(b,0x22);void *v=m->allocate(m->context,n,1);put(b,0x8c,(uintptr_t)v);thug_scene_file_read_draft(v,1,n,file);aux=0;put(b,0x74,0x200);put(b,0x78,word(b,0x78)|2);}
    if((uint8_t)dynamic)put(b,0x74,0x200);
    uint32_t passes=take(file);
    if((int32_t)passes>1){void *v=m->allocate(m->context,passes*4,1);put(b,0x48,(uintptr_t)v);thug_scene_file_read_draft(v,4,passes,file);}
    void *material=thug_mesh_find_material_draft(header,key);put(b,0x14,(uintptr_t)material);
    if(material&&(((uint8_t *)material)[0x20]&0x10))put(b,0,word(b,0)|0x100);
    b[0x1a]=1;
    if(!word(b,0x38)){put(b,0x74,0x200);thug_mesh_load_packed_skin_v1(mesh,data[0],sizes[0],aux);}
    else thug_mesh_vertex_load_draft(mesh,data[0],sizes[0],aux);
    uint32_t shader=take(file);
    if(shader==1){put(b,0x44,thug_mesh_file_shader_skip_draft(file));if(thug_mesh_shader_conversion_enabled_draft)__builtin_trap();}
    else put(b,0x44,thug_mesh_shader_code_draft(shader));
    for(unsigned stream=0;stream<b[0x1a];stream++)m->release(m->context,data[stream]);
}
