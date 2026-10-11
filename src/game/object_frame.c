#include "components.h"
#include "../script/execute.h"


static uint32_t word_at(const void *p,unsigned offset) {
    uint32_t word;__builtin_memcpy(&word,(const uint8_t *)p+offset,4);return word;
}
static void store_word(void *p,unsigned offset,uint32_t value) {
    __builtin_memcpy((uint8_t *)p+offset,&value,4);
}
static ThugObjectFrameStep method(const void *p,unsigned slot) {
    ThugObjectFrameStep step;
    const uint8_t *table=(const void *)(uintptr_t)word_at(p,0);
    __builtin_memcpy(&step,table+slot,4);return step;
}
/* 0045d920. Script execution and virtual methods may replace the component
 * head, suspend/delete the object, or rewrite the current component's next.
 * Keep the separate early-return and loop-break cleanup behavior. */
static void update_components(ThugSkaterBody *body,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    if(word_at(body,0x104)&1)return;
    if(!(word_at(body,0x104)&2)) {
        ThugScriptInstance *script=(void *)(uintptr_t)word_at(body,0x10);
        if(script)thug_script_execute(script,d,m);
        if(word_at(body,8)&1)return;
        method(body,0x28)(body,q,d,m);
    }
    ThugObjectComponent *component=body->components;
    while(component) {
        if(!(component->unknown_8&1)) {
            method(component,4)(component,q,d,m);
            if(word_at(body,8)&1)break;
        }
        component=component->next;
    }
    body->position[3]=1;
    store_word(body,0x104,word_at(body,0x104)&0xfffffff7);
}
/* 0045e4c0. The low-byte notify flag controls callbacks, but the moved bit is
 * always set first. This notification does not skip suspended components. */
static void mark_moved(ThugSkaterBody *body,uint32_t notify,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    store_word(body,0x104,word_at(body,0x104)|8);
    if(!(uint8_t)notify)return;
    for(ThugObjectComponent *component=body->components;component;component=component->next)
        method(component,0x24)(component,q,d,m);
}
/* Host scopes preserve the original game body and its early-return behavior. */
void thug_object_update_components(ThugSkaterBody *body,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
    update_components(body,q,d,m);thug_component_services=previous;
}
void thug_object_mark_moved(ThugSkaterBody *body,uint32_t notify,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
    mark_moved(body,notify,q,d,m);thug_component_services=previous;
}
/* Typed adapters for the actual 00510830 update and original bare RET5480a0.
 * They are not additional recovered routines or a complete component table. */
void thug_component_physics_frame_bridge(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
    thug_skater_update_movement(p,q,d,m);thug_component_services=previous;
}
void thug_component_empty_frame_bridge(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)p;(void)q;(void)d;(void)m;
}
