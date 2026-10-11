/* Derived from pinned configuration; continue into original texture loading. */
#include "../../src/game/components.h"
#include "../../src/script/delivery.h"
#include "../../src/core/bounds.h"
#include "../../src/core/checksum.h"
#include "../../src/core/lookup.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static void put_half(void *p,unsigned o,uint16_t v){__builtin_memcpy((uint8_t *)p+o,&v,2);}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
extern const uintptr_t thug_model_geometry_lights_methods_draft[];
typedef struct {void *(*dispose)(void *,uint32_t,const ThugMemory *);uintptr_t unavailable[27];} GeometryMethods;
extern const GeometryMethods thug_model_geometry_base_methods_draft;
extern uint32_t thug_model_virtual_delete_draft(void *,const ThugMemory *);
ThugObjectLookupTable thug_model_texture_table_draft; /* embedded original700f04 */

/* 0048dd60 /0048e130 /0048e220: base geometry owns only its +c allocation.
 * The destructor intentionally retains that pointer after release. */
void *thug_model_geometry_base_construct_draft(void *p){
    put(p,0,(uintptr_t)&thug_model_geometry_base_methods_draft);
    put(p,4,0);put(p,8,0);put(p,12,0);((uint8_t *)p)[16]=0;return p;
}
void thug_model_geometry_base_destroy_draft(void *p,const ThugMemory *m){
    put(p,0,(uintptr_t)&thug_model_geometry_base_methods_draft);
    if(word(p,12))m->release(m->context,pointer(p,12));
}
void *thug_model_geometry_base_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_model_geometry_base_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
const GeometryMethods thug_model_geometry_base_methods_draft={.dispose=thug_model_geometry_base_delete_draft};
/* 004b4460 /004b2a20: actual PC geometry construction, without inventing its
 * mesh loading or drawing virtuals. The table identity already has real +6c. */
void *thug_model_geometry_construct_draft(void *p){
    thug_model_geometry_base_construct_draft(p);put(p,0,(uintptr_t)thug_model_geometry_lights_methods_draft);
    thug_bounds_reset((ThugBounds *)((uint8_t *)p+0x14));
    put(p,0x38,0);put(p,0x3c,0);put(p,0x4c,0);put(p,0x44,0xdeadbeef);
    put(p,0x54,0x3f800000);put(p,0x58,0x3f800000);put(p,0x5c,0x3f800000);put(p,0x60,0x3f800000);
    ((uint8_t *)p)[0x48]=1;return p;
}
void *thug_model_geometry_create_draft(const ThugMemory *m){
    void *p=thug_allocate_zeroed(0x64,m);return p?thug_model_geometry_construct_draft(p):0;
}
/* 004ecc30: range is [first,last). Reload links between the two splice
 * stores, preserve the sentinel and return last through the caller's slot. */
void thug_model_list_erase_draft(void *p,void **output,void *first,void *last,const ThugMemory *m){
    void *node=first;
    while(node!=last){
        void *old=node,*head=pointer(p,0);node=pointer(old,4);
        if(old!=head){
            put(pointer(old,8),4,(uintptr_t)node);
            put(pointer(old,4),8,word(old,8));
            m->release(m->context,old);put(p,4,word(p,4)-1);
        }
    }*output=node;
}
/* 0048c3c0: the preliminary5480a0 is a real bare RET. */
uint32_t thug_model_geometry_release_draft(void *p,const ThugMemory *m){return thug_model_virtual_delete_draft(p,m);}
/* 0049efd0: unsigned16-bit reference decrement; unlink only at exactly zero. */
uint32_t thug_model_texture_release_draft(void *p,const ThugMemory *m){
    put_half(p,8,half(p,8)-1);
    if(!half(p,8)){
        uint32_t key=word(p,4);thug_object_table_remove(&thug_model_texture_table_draft,&key,m);
        thug_model_virtual_delete_draft(p,m);return 1;
    }return 0;
}
/* 00494ba0: dispose geometry, optional model object and its texture reference,
 * then release parts and list nodes. Capture the old sentinel for iteration;
 * reload the list for erase after callbacks. Asset lookup counts are retained. */
void thug_model_renderer_reset_draft(void *p,const ThugMemory *m){
    void *head=pointer(p,0x10),*node=head?pointer(head,4):0;
    while(node!=head){
        thug_model_geometry_release_draft(pointer(pointer(node,0),0),m);
        void *owned=pointer(pointer(node,0),12);
        if(owned){
            void *texture=pointer(owned,4);thug_model_virtual_delete_draft(owned,m);
            thug_model_texture_release_draft(texture,m);
        }
        m->release(m->context,pointer(node,0));node=pointer(node,4);
    }
    void *live=pointer(p,0x10),*unused;
    thug_model_list_erase_draft((uint8_t *)p+0x10,&unused,live?pointer(live,4):0,live,m);
    put_half(p,0x46,0);put_half(p,0x48,0);put_half(p,0x4a,0);
}
/* 00492ee0: sequential raw copies, followed by live source comparisons.
 * Equality is bitwise; the fourth scale word does not affect bit3. */
uint32_t thug_model_renderer_scale_draft(void *p,const void *scale){
    for(unsigned i=0;i<4;i++)put(p,0x1c+i*4,word(scale,i*4));
    uint8_t scaled=word(scale,0)!=0x3f800000||word(scale,4)!=0x3f800000||word(scale,8)!=0x3f800000;
    ((uint8_t *)p)[0x44]^=(scaled<<3^((uint8_t *)p)[0x44])&8;return 1;
}
/* 00476d50: unlike4766d0, its FLD/FSTP quiets signaling NaNs. */
uint32_t thug_model_parameter_float_draft(const ThugScriptStructure *s,uint32_t key,void *out,uint32_t required){
    (void)required;uint32_t value;
    if(thug_script_get_typed(s,key,2,&value)){put(out,0,quiet(value));return 1;}return 0;
}
/* 00487b00: scalar Scale, then vector Scale, then independent X/Y/Z keys.
 * Uniform X passes through x87; Y/Z retain the getter's raw word. */
uint32_t thug_model_parse_scale_draft(void *out,const ThugScriptStructure *s){
    if(thug_script_has_name_or_flag(s,0x13b9da7b)){
        uint32_t value;
        if(thug_script_get_float(s,0x13b9da7b,(float *)&value,0)){
            put(out,0,quiet(value));put(out,4,value);put(out,8,value);put(out,12,0x3f800000);return 1;
        }
        if(thug_script_get_vector(s,0x13b9da7b,out,0))return 1;
    }
    uint32_t x=thug_model_parameter_float_draft(s,0x7323e97c,out,0);
    uint32_t y=thug_model_parameter_float_draft(s,0x0424d9ea,(uint8_t *)out+4,0);
    uint32_t z=thug_model_parameter_float_draft(s,0x9d2d8850,(uint8_t *)out+8,0);
    return x||y||z;
}
/* 00402080: ASCII uppercase conversion only, preserving slash direction. */
void thug_model_path_lower_draft(char *p){for(;*p;p++)if((uint8_t)*p>='A'&&(uint8_t)*p<='Z')*p+=32;}
/* 00487a70: the two original sprintf formats, for non-overlapping buffers
 * with enough caller-owned storage. A slash suppresses name repetition/extension. */
void thug_model_path_draft(const char *name,const char *extension,char *out){
    uint32_t has_path=0;for(const char *p=name;*p;p++)if(*p=='/'||*p=='\\')has_path=1;
    const char *prefix="models\\";while(*prefix)*out++=*prefix++;
    for(const char *p=name;*p;p++)*out++=*p;
    if(!has_path){*out++='\\';for(const char *p=name;*p;p++)*out++=*p;while(*extension)*out++=*extension++;}
    *out=0;
}

/* Partial00420d10: configuration through the TEXT-model load request. Other
 * source branches and the post-load tail remain unavailable and trap. Neither
 * this prefix nor4214f0 is counted as a complete recovered routine. Context
 * arguments retain the component/parameters for explicit boundary inspection. */
void thug_model_texture_load_prefix_draft(void *,const ThugScriptStructure *,void *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
void (*thug_model_load_pending_draft)(void *,const ThugScriptStructure *,void *,const char *,
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t)=thug_model_texture_load_prefix_draft;
void *thug_model_renderer_sphere_draft(void *,void *);
void (*thug_model_renderer_ready_pending_draft)(void *,const ThugScriptStructure *);
void thug_model_level_object_draft(void *,uint32_t,const ThugMemory *);
void thug_model_configuration_prefix_draft(void *p,const ThugScriptStructure *s){
    const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
    thug_model_renderer_reset_draft(pointer(p,0x208),m);
    uint32_t scale[4]={0x3f800000,0x3f800000,0x3f800000,0x3f800000};
    if(thug_model_parse_scale_draft(scale,s))thug_model_renderer_scale_draft(pointer(p,0x208),scale);
    uint32_t kind=0;thug_script_get_checksum(s,0x12b4e660,&kind,0);
    if(kind==0xb7b3bd86){uint32_t key;if(!thug_script_get_checksum(s,0xa1dc81f9,&key,1))__builtin_trap();thug_model_level_object_draft(p,key,m);goto ready;}
    uint32_t assets=1,option=0,source;
    thug_script_get_integer(s,0xc63c8d38,&assets,0);thug_script_get_integer(s,0xf891ac27,&option,0);
    if(thug_script_get_checksum(s,0x153a84de,&source,0))__builtin_trap();
    if(thug_script_get_checksum(s,0x86bd5b8f,&source,0))__builtin_trap();
    if(thug_script_get_checksum(s,0x7dd037b3,&source,0))__builtin_trap();
    const char *name;
    if(!thug_script_get_text(s,0x286a8d26,&name,0)&&!thug_script_get_text(s,0xb974f2fc,&name,0))__builtin_trap();
    if(thug_crc32_string(name)==0x806fff30)__builtin_trap(); /* unrecovered post-load tail */
    const char *extension=thug_script_get_checksum(s,0x09794932,&source,0)?".skin":".mdl";
    char path[512];thug_model_path_draft(name,extension,path);thug_model_path_lower_draft(path);
    uint32_t flag=thug_script_has_flag(s,0x6c37fdc7);
    if(!thug_model_load_pending_draft)__builtin_trap();
    thug_model_load_pending_draft(p,s,pointer(p,0x208),path,0,assets!=0,option,flag,0,1,0);
    if(thug_model_load_pending_draft!=thug_model_texture_load_prefix_draft)__builtin_trap();
    if(thug_model_renderer_ready_pending_draft){thug_model_renderer_ready_pending_draft(p,s);__builtin_trap();}
    /* Original421191 tail. The update/lighting and skeleton-cache paths still
     * stop explicitly; the training collectible does not take either path. */
ready:
    if(word(pointer(p,12),0x104)&0x20)__builtin_trap();
    uint32_t sphere[4];void *value=thug_model_renderer_sphere_draft(pointer(p,0x208),sphere);
    for(unsigned i=0;i<4;i++)put(p,0x18+i*4,word(value,i*4));
    if(thug_script_get_global_integer(0x74ff5cb4,0))__builtin_trap(); /*420350*/
}
