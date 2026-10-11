/* Derived from pinned Model construction; only initializer prefix binding added. */
#include "../../src/game/components.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}

/* Only recovered slots are bound. Loading, drawing and destruction remain
 * unavailable until their original implementations are recovered. */
typedef uint32_t (*RendererOne)(void *,uint32_t);
typedef struct {
    uintptr_t unavailable_0;
    RendererOne at_4;
    uintptr_t unavailable_8;
    RendererOne at_c;
    uintptr_t unavailable_10;
    RendererOne at_14,at_18,at_1c;
    uintptr_t unavailable_20_to_34[6];
} RendererMethods;
extern const RendererMethods thug_model_renderer_base_methods_draft,thug_model_renderer_methods_draft;
extern const ThugComponentMethods thug_model_component_methods_draft;
_Static_assert(offsetof(RendererMethods,at_c)==12,"Original renderer dispatch");

/* 005bc7f0. This actual shared virtual returns AL=1 and pops one argument. */
uint32_t thug_model_virtual_true_draft(void *p,uint32_t ignored){(void)p;(void)ignored;return 1;}

/* 00494c40. Allocate the real circular-list sentinel; preserve unspecified
 * bytes, including the sentinel value and unused adjacent halfwords. */
void *thug_model_renderer_base_construct_draft(void *p,const ThugMemory *m){
    put(p,0,(uintptr_t)&thug_model_renderer_base_methods_draft);put(p,0x14,0);
    void *head=m->allocate(m->context,12,1);
    if(head){put(head,4,(uintptr_t)head);put(head,8,(uintptr_t)head);}
    put(p,0x10,(uintptr_t)head);put(p,8,0);put(p,12,0);
    if(word(p,4)!=6){
        const RendererMethods *methods=(void *)(uintptr_t)word(p,0);
        if((uint8_t)methods->at_c(p,6))put(p,4,6);
    }
    uint8_t flags=((uint8_t *)p)[0x44];
    ((uint8_t *)p)[0x46]=0;((uint8_t *)p)[0x47]=0;
    flags=(flags&0xfb)|2;put(p,0x30,0x6607dd3e);((uint8_t *)p)[0x44]=flags;
    for(unsigned o=0x1c;o<=0x28;o+=4)put(p,o,0x3f800000);
    ((uint8_t *)p)[0x44]&=0xc6;put(p,0x2c,0);return p;
}
/* 004bad90,004b29c0,0048bfa0. The public factory's argument is ignored by
 * its original unconditional jump; both allocations retain original routes. */
void *thug_model_renderer_construct_draft(void *p,const ThugMemory *m){
    thug_model_renderer_base_construct_draft(p,m);put(p,0,(uintptr_t)&thug_model_renderer_methods_draft);put(p,0x4c,0);return p;
}
void *thug_model_renderer_create_draft(const ThugMemory *m){
    void *p=thug_allocate_zeroed(0x50,m);return p?thug_model_renderer_construct_draft(p,m):0;
}
void *thug_model_renderer_factory_draft(uint32_t ignored,const ThugMemory *m){
    (void)ignored;return thug_model_renderer_create_draft(m);
}
/* 00420bf0. Three embedded six-entry groups initialize only their low two
 * flag bits and trailing active byte. All other group data is retained. */
void *thug_model_component_construct_draft(void *p,const ThugMemory *m){
    thug_component_construct(p);put(p,0,(uintptr_t)&thug_model_component_methods_draft);put(p,4,0x286a8d26);
    put(p,0x208,(uintptr_t)thug_model_renderer_factory_draft(1,m));
    put(p,0x28,0);put(p,0x2c,0);put(p,0x30,0);put(p,0x34,0x3f800000);
    for(unsigned group=0;group<3;group++){
        for(unsigned entry=0;entry<6;entry++)((uint8_t *)p)[0x4c+group*0x94+entry*0x18]&=0xfc;
        ((uint8_t *)p)[0xc8+group*0x94]=0;
    }
    put(p,0x228,0);((uint8_t *)p)[0x235]=0;
    put(p,0x1f8,0);put(p,0x1fc,0);put(p,0x200,0);put(p,0x204,0x3f800000);put(p,0x22c,0x3f800000);
    return p;
}
/* 00421490. The model owns the renderer created by its constructor. */
void *thug_model_component_create_draft(const ThugMemory *m){
    void *p=thug_allocate_zeroed(0x238,m);return p?thug_model_component_construct_draft(p,m):0;
}
const RendererMethods thug_model_renderer_base_methods_draft={
    .at_4=thug_model_virtual_true_draft,.at_c=thug_model_virtual_true_draft,
    .at_14=thug_model_virtual_true_draft,.at_18=thug_model_virtual_true_draft,.at_1c=thug_model_virtual_true_draft
};
const RendererMethods thug_model_renderer_methods_draft={
    .at_4=thug_model_virtual_true_draft,.at_c=thug_model_virtual_true_draft,
    .at_14=thug_model_virtual_true_draft,.at_18=thug_model_virtual_true_draft,.at_1c=thug_model_virtual_true_draft
};
void thug_model_initialize_prefix_draft(void *,const ThugScriptStructure *);
const ThugComponentMethods thug_model_component_methods_draft={
    .initialize=thug_model_initialize_prefix_draft,
    .refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,
    .suspend=thug_component_suspend,.unknown_28=thug_component_empty_one,
    .descriptor=thug_component_descriptor_base
};
