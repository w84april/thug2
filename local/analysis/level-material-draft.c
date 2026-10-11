#include "../../src/graphics/decal.h"
/* Platform file operations, not recovered Windows handle implementations.
 * Comparison providers expose bounded resident files and record every request. */
uint32_t (*thug_scene_file_read_draft)(void *,uint32_t,uint32_t,void *);
uint32_t (*thug_scene_file_seek_draft)(void *,int32_t,uint32_t);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint32_t take(void *file){uint32_t v;thug_scene_file_read_draft(&v,4,1,file);return v;}
static uint8_t byte(void *file){uint8_t v;thug_scene_file_read_draft(&v,1,1,file);return v;}
static void *texture_resource(const ThugObjectLookupTable *textures,uint32_t key){
    void *wrapper=thug_object_table_find(textures,&key,0);
    if(!wrapper)return 0;
    void *resource=pointer(wrapper,16);
    return ((const uint8_t *)wrapper)[8]&1?pointer(resource,0):resource;
}
/* 004d3390,2086 bytes. File-stream counterpart of recovered004d2cb0.
 * Internal contract: initialized allocator, successful allocations/reads,
 * complete file records, at most four passes. Preserve all file-read grouping,
 * seeks, duplicate allocation, texture indirection and retained storage. */
ThugObjectLookupTable *thug_material_file_parse_draft(void *file,const ThugObjectLookupTable *textures,const ThugMemory *m){
    uint32_t count=take(file),shift=2,slots=4;
    while(slots<=count*2&&shift<12){slots<<=1;shift++;}
    ThugObjectLookupTable *table=m->allocate(m->context,24,1);
    if(table)thug_object_table_initialize(table,shift,m);
    for(uint32_t material_index=0;material_index<count;material_index++){
        ThugRenderMaterial *material=m->allocate(m->context,0x110,1);
        if(material)thug_render_material_initialize(material);
        uint8_t *b=material->storage;
        put(b,0,take(file));put(b,4,take(file));put(b,8,take(file));b[16]=take(file);b[12]=byte(file);
        put(b,0x1c,take(file));uint8_t explicit_sort=byte(file);b[13]=byte(file);
        int32_t limit=(int32_t)take(file);b[17]=limit>16?16:limit;
        if(byte(file)){put(b,0x14,take(file));put(b,0x18,take(file));}
        put(b,0x10c,take(file));
        if(number(b,0x10c)>0)thug_scene_file_read_draft(b+0x100,12,1,file);
        uint32_t neutral=1;
        for(uint32_t pass=0;pass<word(b,8);pass++){
            uint32_t key=take(file);put(b,0x20+pass*4,take(file));(void)byte(file);
            thug_scene_file_read_draft(b+0x40+pass*16,12,1,file);
            if(neutral&&(word(b,0x40+pass*16)!=0x3f000000||word(b,0x44+pass*16)!=0x3f000000||word(b,0x48+pass*16)!=0x3f000000))neutral=0;
            uint32_t blend_alpha[2];thug_scene_file_read_draft(blend_alpha,8,1,file);
            uint32_t blend=blend_alpha[0],alpha=blend_alpha[1];put(b,0x80+pass*4,(blend&0xffffff)|(alpha<<24));
            put_number(b,0x4c+pass*16,(float)alpha*0.0078125f);
            if(pass==0&&!explicit_sort&&(word(b,0x80)&0xffffff))b[13]=1;
            uint32_t u=take(file),v=take(file);put(b,0x90+pass*4,(v<<16)|u);
            thug_scene_file_read_draft(b+0xa0+pass*8,8,1,file);put(b,0xc0+pass*4,take(file));
            if(word(b,0x20+pass*4)&1){
                b[14]=1;void *animation=m->allocate(m->context,48,1);
                if(animation){__builtin_memset(animation,0,48);put(animation,32,0x3f800000);}
                put(b,0xd0+pass*4,(uintptr_t)animation);
                thug_scene_file_read_draft(animation,32,1,file);
            }
            if(pass==0&&(word(b,0x20)&2)){
                uint32_t channels=take(file);put(b,0xf0,channels);
                put(b,0xf4,(uintptr_t)m->allocate(m->context,channels*12,1));
                put(b,0xf8,(uintptr_t)m->allocate(m->context,channels*4,1));
                for(uint32_t channel=0;channel<channels;channel++){
                    uint32_t n=take(file),mode=take(file);void *records=pointer(b,0xf4);
                    put(records,channel*12,n);put(records,channel*12+4,mode);
                    void *keys=m->allocate(m->context,n*8,1);put(pointer(b,0xf4),channel*12+8,(uintptr_t)keys);
                    thug_scene_file_read_draft(keys,8,n,file);
                }
            }
            if(word(b,0x20+pass*4)&0x800){
                if(!word(b,0xfc)){void *animation=m->allocate(m->context,68,1);put(b,0xfc,(uintptr_t)animation);__builtin_memset(animation,0,68);b[15]=1;}
                uint32_t frames=take(file);(void)take(file);uint32_t rate=take(file),mode=take(file);
                void *animation=pointer(b,0xfc);put(animation,4+pass*4,frames);put(animation,0x14+pass*4,mode);put(animation,0x24+pass*4,rate);
                void *keys=m->allocate(m->context,frames*8,1);put(pointer(b,0xfc),0x34+pass*4,(uintptr_t)keys);
                for(int32_t frame=0;frame<(int32_t)frames;frame++){
                    keys=pointer(pointer(b,0xfc),0x34+pass*4);put(keys,(uint32_t)frame*8,take(file));
                    uint32_t name=take(file);if(!frame)key=name;
                    void *resource=texture_resource(textures,name);
                    put(pointer(pointer(b,0xfc),0x34+pass*4),(uint32_t)frame*8+4,(uintptr_t)resource);
                }
            }
            if(!key){put(b,0x30+pass*4,0);thug_scene_file_seek_draft(file,16,1);}
            else{
                put(b,0x30+pass*4,(uintptr_t)texture_resource(textures,key));
                (void)take(file);(void)take(file);uint32_t raw=take(file);(void)take(file);
                float bias=number(&raw,0)+8.0f;put_number(b,0xe0+pass*4,bias>0?0:bias);
            }
        }
        if(neutral)put(b,0x20,word(b,0x20)|0x10000000);
        if(number(b,0x10c)>0)put(b,0x20,word(b,0x20)|0x100);
        uint32_t key=word(b,0);
        if(!thug_object_table_find(table,&key,0))thug_object_table_insert(table,(const uint32_t *)b,material,m);
    }
    return table;
}
