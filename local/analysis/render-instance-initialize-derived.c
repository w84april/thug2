/* Derived from pinned initializer prefix; bind the next recovered configuration prefix. */
#include "../../src/game/components.h"
#include "../../src/game/attachment.h"
#include "../../src/game/stats.h"
#include "../../src/script/delivery.h"
#include "../../src/graphics/decal.h"
#include "../../src/game/assets.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
typedef struct {
    void *(*dispose)(void *,uint32_t,const ThugMemory *);
    uintptr_t unavailable_4_to_20[8];
    void (*ambient)(void *,uint32_t);
    void (*directional)(void *,uint32_t,uint32_t);
    uintptr_t unavailable_2c;
} LightMethods;
typedef struct {
 uintptr_t unused0[3];uint8_t (*load)(void *,void *,void *,uint32_t,const ThugMemory *);
 uintptr_t unused10[23];void (*lights)(void *,void *);uintptr_t unused70[4];uint32_t (*flag16)(void *,uint32_t);
} GeometryMethods;
uint8_t thug_model_geometry_load_instance_draft(void *,void *,void *,uint32_t,const ThugMemory *);
uint32_t thug_model_virtual_true_draft(void *,uint32_t);
extern const LightMethods thug_model_light_base_methods_draft,thug_model_light_methods_draft;
const GeometryMethods thug_model_geometry_lights_methods_draft={.load=thug_model_geometry_load_instance_draft,.lights=thug_component_empty_one,.flag16=thug_model_virtual_true_draft};
_Static_assert(offsetof(LightMethods,ambient)==0x24,"Original light methods");
_Static_assert(offsetof(GeometryMethods,lights)==0x6c,"Original geometry light method");
uint32_t thug_model_light_factor_count_draft; /* 006faae0 */
uint32_t thug_model_directional_count_draft; /* 006faae4 */

/* 00532eb0 /00492e90 /0048e4d0. Preserve raw pointers and the flag's low bit. */
void *thug_model_renderer_lights_draft(const void *p){return pointer(p,0x2c);}
void thug_model_renderer_flag32_draft(void *p,uint32_t value){
    uint8_t *b=(uint8_t *)p+0x44;*b^=((uint8_t)value<<5^*b)&0x20;
}
uint32_t thug_model_light_position_draft(void *p,void *position){put(p,0x18,(uintptr_t)position);return 1;}
/* 0048df20. The PC geometry's actual +6c slot is the already recovered
 * bare RET4. Other geometry virtuals remain explicitly unavailable here. */
void thug_model_geometry_set_lights_draft(void *p,void *light){
    ((const GeometryMethods *)pointer(p,0))->lights(p,light);
}
/* 00492dd0. The skeleton source uses existing +8/+4 accessors. Capture the
 * renderer method table before storing +8, but reload the source after calls. */
uint32_t thug_model_renderer_bind_skeleton_draft(void *p,void *skeleton){
    if(!word(p,12)){
        uint32_t value=(uintptr_t)thug_render_geometry_mesh(skeleton);
        const uint32_t *methods=pointer(p,0);put(p,8,value);
        value=(uintptr_t)thug_render_geometry_mesh(skeleton);
        ((uint32_t (*)(void *,uint32_t))(uintptr_t)methods[1])(p,value);
        put(p,12,(uintptr_t)thug_network_first_connection(skeleton));
    }return 1;
}
/* 004b61f0/004b6210. Enable uses the low BYTE; x86 shifts mask to five bits. */
void thug_model_light_ambient_draft(void *p,uint32_t enabled){
    uint32_t flags=word(p,0x1c);put(p,0x1c,(uint8_t)enabled?flags|1:flags&~1u);
}
void thug_model_light_directional_draft(void *p,uint32_t index,uint32_t enabled){
    uint32_t mask=2u<<(index&31),flags=word(p,0x1c);put(p,0x1c,(uint8_t)enabled?flags|mask:flags&~mask);
}
/* 0048de30/0048e4c0. Actual live virtual forwarding. */
void thug_model_light_set_ambient_draft(void *p,uint32_t enabled){((const LightMethods *)pointer(p,0))->ambient(p,enabled);}
void thug_model_light_set_directional_draft(void *p,uint32_t index,uint32_t enabled){((const LightMethods *)pointer(p,0))->directional(p,index,enabled);}
/* 0048e5b0. Counts are unsigned and reloaded after allocation/in each loop. */
void *thug_model_light_base_construct_draft(void *p,const ThugMemory *m){
    put(p,0,(uintptr_t)&thug_model_light_base_methods_draft);put(p,12,0);put(p,8,0);put(p,0x10,0x3f800000);
    uint32_t bytes=thug_model_light_factor_count_draft*4;put(p,0x14,(uintptr_t)m->allocate(m->context,bytes,1));
    for(uint32_t i=0;i<thug_model_light_factor_count_draft;i++)put(pointer(p,0x14),i*4,0x3f800000);
    put(p,4,0);put(p,0x18,0);return p;
}
/* 0048e630. Reset the vtable before releasing the retained factor array. */
void thug_model_light_base_destroy_draft(void *p,const ThugMemory *m){
    void *array=pointer(p,0x14);put(p,0,(uintptr_t)&thug_model_light_base_methods_draft);
    if(array){m->release(m->context,array);put(p,0x14,0);}
}
/* 004b6270. Real derived lighting owns a pointer array and four-word vectors. */
void *thug_model_light_construct_draft(void *p,const ThugMemory *m){
    thug_model_light_base_construct_draft(p,m);put(p,0,(uintptr_t)&thug_model_light_methods_draft);put(p,0x1c,0);
    uint32_t count=thug_model_directional_count_draft;put(p,0x28,(uintptr_t)m->allocate(m->context,count*4,1));
    count=thug_model_directional_count_draft;put(p,0x2c,(uintptr_t)m->allocate(m->context,count*16,1));
    thug_model_light_set_ambient_draft(p,0);
    for(uint32_t i=0,offset=0;i<thug_model_directional_count_draft;i++,offset+=16){
        thug_model_light_set_directional_draft(p,i,0);void *at=(uint8_t *)pointer(p,0x2c)+offset;
        put(at,0,0);put(at,4,0x3f800000);put(at,8,0);put(at,12,0x3f800000);
    }put(p,0x20,2);return p;
}
/* 004b6360/004b67b0. Derived arrays release in order, then the base array. */
void thug_model_light_destroy_draft(void *p,const ThugMemory *m){
    void *array=pointer(p,0x28);put(p,0,(uintptr_t)&thug_model_light_methods_draft);
    if(array){m->release(m->context,array);put(p,0x28,0);}
    array=pointer(p,0x2c);if(array){m->release(m->context,array);put(p,0x2c,0);}
    thug_model_light_base_destroy_draft(p,m);
}
void *thug_model_light_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_model_light_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 004b6b10/0048ea80. Raw route-one allocation, not zeroed allocation. */
void *thug_model_light_create_draft(const ThugMemory *m){void *p=m->allocate(m->context,0x30,1);return p?thug_model_light_construct_draft(p,m):0;}
void *thug_model_light_factory_draft(const ThugMemory *m){return thug_model_light_create_draft(m);}
/* 004b6920/0048c080. Generic null-tolerant virtual deletion returns AL=1. */
uint32_t thug_model_virtual_delete_draft(void *p,const ThugMemory *m){if(p)((const LightMethods *)pointer(p,0))->dispose(p,1,m);return 1;}
uint32_t thug_model_light_release_draft(void *p,const ThugMemory *m){return thug_model_virtual_delete_draft(p,m);}
/* 00493bd0. Capture the list head after construction, before installing lights. */
uint32_t thug_model_renderer_create_lights_draft(void *p,const ThugMemory *m){
    void *light=thug_model_light_factory_draft(m),*head=pointer(p,0x10);put(p,0x2c,(uintptr_t)light);
    for(void *node=head?pointer(head,4):0;node!=head;node=pointer(node,4))
        thug_model_geometry_set_lights_draft(pointer(pointer(node,0),0),pointer(p,0x2c));
    return 1;
}
/* 00493c10. Reload the head after destruction; old owned light is not retained. */
uint32_t thug_model_renderer_remove_lights_draft(void *p,const ThugMemory *m){
    thug_model_light_release_draft(pointer(p,0x2c),m);void *head=pointer(p,0x10);put(p,0x2c,0);
    for(void *node=head?pointer(head,4):0;node!=head;node=pointer(node,4))
        thug_model_geometry_set_lights_draft(pointer(pointer(node,0),0),0);
    return 1;
}
const LightMethods thug_model_light_base_methods_draft={0};
const LightMethods thug_model_light_methods_draft={.dispose=thug_model_light_delete_draft,.ambient=thug_model_light_ambient_draft,.directional=thug_model_light_directional_draft};

/* 004214f0 up to its call to00420d10. The configuration/loading dependency
 * remains unavailable: a test-only breakpoint may be attached, but it must
 * not manufacture configuration results. This prefix is not counted among
 * the completely recovered routines until the real callee is supplied. */
void thug_model_configuration_prefix_draft(void *,const ThugScriptStructure *);
void (*thug_model_configuration_pending_draft)(void *,const ThugScriptStructure *)=thug_model_configuration_prefix_draft;
extern uint32_t thug_asset_set_key_draft(ThugAsset *,uint32_t);
void thug_model_initialize_prefix_draft(void *p,const ThugScriptStructure *s){
    const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
    if(thug_script_has_flag(s,0x10079f2d)){
        if(!thug_model_renderer_lights_draft(pointer(p,0x208))){
            thug_model_renderer_create_lights_draft(pointer(p,0x208),m);void *light=thug_model_renderer_lights_draft(pointer(p,0x208));
            thug_model_light_position_draft(light,(uint8_t *)pointer(p,12)+0x4c);
            uint32_t enabled=1;thug_script_get_integer(s,0xd223b8bd,&enabled,0);thug_asset_set_key_draft(light,(uint32_t)enabled);
        }
    }else if(thug_model_renderer_lights_draft(pointer(p,0x208)))thug_model_renderer_remove_lights_draft(pointer(p,0x208),m);
    void *skeleton=thug_object_find_component(pointer(p,12),0x222756d5);
    if(skeleton){void *renderer=pointer(p,0x208);thug_model_renderer_bind_skeleton_draft(renderer,thug_attachment_provider_points(skeleton));}
    uint32_t flag=0;thug_script_get_integer(s,0x2a1f92c0,&flag,0);thug_model_renderer_flag32_draft(pointer(p,0x208),flag!=0);
    if(!thug_model_configuration_pending_draft)__builtin_trap();
    thug_model_configuration_pending_draft(p,s);
}
