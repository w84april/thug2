#include "../../src/graphics/decal.h"
#include "../../src/core/bounds.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint32_t take(const uint8_t **p){uint32_t v=word(*p,0);*p+=4;return v;}
static void *texture_resource(const ThugObjectLookupTable *textures,uint32_t key){
    void *wrapper=thug_object_table_find(textures,&key,0);
    if(!wrapper)return 0;
    void *resource=pointer(wrapper,16);
    return ((const uint8_t *)wrapper)[8]&1?pointer(resource,0):resource;
}
/* 004d2cb0,1746 contiguous bytes. The existing004d1a90 material constructor,
 * lookup constructor and insertion are reused. Internal contract: initialized
 * heap, successful allocations, complete data and at most four material passes.
 * All unspecified fields and allocated keyframe-work arrays retain their bytes.
 * Duplicate materials still allocate/parse; only their table insertion is skipped. */
ThugObjectLookupTable *thug_material_buffer_parse_draft(const uint8_t **input,const ThugObjectLookupTable *textures,const ThugMemory *m){
    const uint8_t *p=*input;uint32_t count=take(&p),shift=2,slots=4;
    while(slots<=count*2&&shift<12){slots<<=1;shift++;}
    ThugObjectLookupTable *table=m->allocate(m->context,24,1);
    if(table)thug_object_table_initialize(table,shift,m);
    for(uint32_t material_index=0;material_index<count;material_index++){
        ThugRenderMaterial *material=m->allocate(m->context,0x110,1);
        if(material)thug_render_material_initialize(material);
        uint8_t *b=material->storage;
        put(b,0,take(&p));put(b,4,take(&p));put(b,8,take(&p));b[16]=take(&p);b[12]=*p++;
        put(b,0x1c,take(&p));uint8_t explicit_sort=*p++;b[13]=*p++;
        int32_t limit=(int32_t)take(&p);b[17]=limit>16?16:limit;
        if(*p++){put(b,0x14,take(&p));put(b,0x18,take(&p));}
        put(b,0x10c,take(&p));
        if(number(b,0x10c)>0){for(unsigned i=0;i<3;i++)put(b,0x100+i*4,take(&p));}
        uint32_t neutral=1;
        for(uint32_t pass=0;pass<word(b,8);pass++){
            uint32_t key=take(&p);put(b,0x20+pass*4,take(&p));p++;
            for(unsigned i=0;i<3;i++)put(b,0x40+pass*16+i*4,take(&p));
            if(neutral&&(word(b,0x40+pass*16)!=0x3f000000||word(b,0x44+pass*16)!=0x3f000000||word(b,0x48+pass*16)!=0x3f000000))neutral=0;
            uint32_t blend=take(&p),alpha=take(&p);put(b,0x80+pass*4,(blend&0xffffff)|(alpha<<24));
            put_number(b,0x4c+pass*16,(float)alpha*0.0078125f);
            if(pass==0&&!explicit_sort&&(word(b,0x80)&0xffffff))b[13]=1;
            uint32_t u=take(&p),v=take(&p);put(b,0x90+pass*4,(v<<16)|u);
            put(b,0xa0+pass*8,take(&p));put(b,0xa4+pass*8,take(&p));put(b,0xc0+pass*4,take(&p));
            if(word(b,0x20+pass*4)&1){
                b[14]=1;void *animation=m->allocate(m->context,48,1);
                if(animation){__builtin_memset(animation,0,48);put(animation,32,0x3f800000);}
                put(b,0xd0+pass*4,(uintptr_t)animation);
                for(unsigned i=0;i<8;i++)put(animation,i*4,take(&p));
            }
            if(pass==0&&(word(b,0x20)&2)){
                uint32_t channels=take(&p);put(b,0xf0,channels);
                put(b,0xf4,(uintptr_t)m->allocate(m->context,channels*12,1));
                put(b,0xf8,(uintptr_t)m->allocate(m->context,channels*4,1));
                for(uint32_t channel=0;channel<channels;channel++){
                    uint32_t n=take(&p),mode=take(&p);void *records=pointer(b,0xf4);
                    put(records,channel*12,n);put(records,channel*12+4,mode);
                    void *keys=m->allocate(m->context,n*8,1);put(pointer(b,0xf4),channel*12+8,(uintptr_t)keys);
                    __builtin_memcpy(keys,p,n*8);p+=n*8;
                }
            }
            if(word(b,0x20+pass*4)&0x800){
                if(!word(b,0xfc)){void *animation=m->allocate(m->context,68,1);put(b,0xfc,(uintptr_t)animation);__builtin_memset(animation,0,68);b[15]=1;}
                uint32_t frames=take(&p);p+=4;uint32_t rate=take(&p),mode=take(&p);
                void *animation=pointer(b,0xfc);put(animation,4+pass*4,frames);put(animation,0x14+pass*4,mode);put(animation,0x24+pass*4,rate);
                void *keys=m->allocate(m->context,frames*8,1);put(pointer(b,0xfc),0x34+pass*4,(uintptr_t)keys);
                for(int32_t frame=0;frame<(int32_t)frames;frame++){
                    keys=pointer(pointer(b,0xfc),0x34+pass*4);put(keys,(uint32_t)frame*8,take(&p));
                    uint32_t name=take(&p);if(!frame)key=name;
                    void *resource=texture_resource(textures,name);
                    put(pointer(pointer(b,0xfc),0x34+pass*4),(uint32_t)frame*8+4,(uintptr_t)resource);
                }
            }
            if(!key)put(b,0x30+pass*4,0);
            else{
                put(b,0x30+pass*4,(uintptr_t)texture_resource(textures,key));
                float bias=number(p,8)+8.0f;put_number(b,0xe0+pass*4,bias>0?0:bias);
            }
            p+=16;
        }
        if(neutral)put(b,0x20,word(b,0x20)|0x10000000);
        if(number(b,0x10c)>0)put(b,0x20,word(b,0x20)|0x100);
        uint32_t key=word(b,0);
        if(!thug_object_table_find(table,&key,0))thug_object_table_insert(table,(const uint32_t *)b,material,m);
    }
    *input=p;return table;
}
/* 004de300: scene data header, retaining all unspecified fields. */
void *thug_model_scene_data_initialize_draft(void *data){
    uint8_t *b=data;thug_bounds_reset((ThugBounds *)(b+0x44));
    const uint8_t offsets[]={0,0x20,0x24,0x28,0x34,0x1c,0x18,0x74,0x78,0x7c,0x80};
    for(unsigned i=0;i<sizeof(offsets);i++)put(b,offsets[i],0);
    b[0x40]=0;put(b,0x30,0xffffffff);put(b,0x2c,0xffffffff);return data;
}
/* Partial48c030/4b3ad0/4b3490: execute the real header/material path and stop
 * at the missing scene constructor. No geometry/result/cleanup is invented. */
void (*thug_model_scene_constructor_pending_draft)(void *,uint32_t,const ThugMemory *);
void *thug_model_scene_construct_draft(void *,uint32_t,const ThugMemory *);
void thug_model_scene_load_geometry_prefix_draft(void *,void *,const uint8_t *,uint32_t,const ThugMemory *);
void (*thug_model_scene_ready_pending_draft)(void *);
void thug_model_geometry_load_prefix_draft(uint32_t key,const void *data,uint32_t size,const void *companion,void *dictionary,uint32_t offset,uint32_t skin,uint32_t flag,const ThugMemory *m){
    (void)key;(void)size;(void)companion;(void)offset;(void)skin;(void)flag;
    void *header=m->allocate(m->context,132,1);if(header)thug_model_scene_data_initialize_draft(header);
    ((uint8_t *)header)[0x40]=0;const uint8_t *p=(const uint8_t *)data+12;
    put(header,0x18,(uintptr_t)thug_material_buffer_parse_draft(&p,pointer(dictionary,12),m));
    uint32_t count=take(&p),shift=1,slots=2;
    while(slots<count*2&&shift<12){slots<<=1;shift++;}
    void *scene=m->allocate(m->context,644,1);
    if(thug_model_scene_constructor_pending_draft){thug_model_scene_constructor_pending_draft(scene,shift,m);__builtin_trap();}
    thug_model_scene_construct_draft(scene,shift,m);
    thug_model_scene_load_geometry_prefix_draft(scene,header,p,count,m);
    if(thug_model_scene_ready_pending_draft)thug_model_scene_ready_pending_draft(scene);
    __builtin_trap(); /* 4b3490 returned;4b3ad0 continuation4b3b1c pending */
}
