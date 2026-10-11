#include "animation.h"
#include "../core/number.h"
#include "../platform/math.h"
#include "../script/values.h"
#include "../script/delivery.h"
#include <stddef.h>
_Static_assert(sizeof(ThugAnimationEvent)==0x14,"Animation event record");
_Static_assert(offsetof(ThugAnimationChannel,events)==0x68,"Animation event array");
const ThugAnimationEventMethods thug_animation_event_base_methods={.dispose=thug_animation_event_base_delete,.crosses=thug_animation_event_crosses};
const ThugAnimationEventMethods thug_animation_event_methods={.dispose=thug_animation_event_delete,.crosses=thug_animation_event_crosses,.trigger=thug_animation_event_emit};
/* 0x00481a20, 0x00486150 and 0x004865d0. */
ThugAnimationEvent *thug_animation_event_initialize(ThugAnimationEvent *event) {
    event->methods=&thug_animation_event_methods; event->parameters=NULL; return event;
}
void thug_animation_event_set_enabled(ThugAnimationEvent *event,uint32_t enabled) { event->enabled=(uint8_t)enabled; }
void thug_animation_event_setup(ThugAnimationEvent *event,uint32_t frame,uint32_t name,const ThugScriptStructure *parameters,const ThugMemory *memory) {
    event->frame=(int32_t)frame; event->enabled=0; event->event=name;
    ThugScriptStructure *owned=thug_script_structure_allocate(8,memory);
    if (owned) thug_script_structure_initialize(owned);
    event->parameters=owned; thug_script_structure_merge_optional(owned,parameters,memory);
}
/* 0x00486560. */
void thug_animation_event_destroy(ThugAnimationEvent *event,const ThugMemory *memory) {
    event->methods=&thug_animation_event_methods;
    if (event->parameters) {
        thug_script_structure_destroy(event->parameters,memory);
        thug_script_structure_free(event->parameters,memory); event->parameters=NULL;
    }
    event->methods=&thug_animation_event_base_methods;
}
/* 0x00481db0. C loops express the compiler's forward construction/reverse
 * destruction helpers. This port does not implement MSVC exception unwinding. */
void *thug_animation_event_delete(ThugAnimationEvent *event,uint32_t flags,const ThugMemory *memory) {
    if ((uint8_t)flags&2) {
        uint32_t *header=(uint32_t *)event-1;
        for (uint32_t i=*header;i;--i) thug_animation_event_destroy(event+i-1,memory);
        if ((uint8_t)flags&1) memory->release(memory->context,header);
        return header;
    }
    thug_animation_event_destroy(event,memory);
    if ((uint8_t)flags&1) memory->release(memory->context,event);
    return event;
}
/* 0x004819f0. */
void *thug_animation_event_base_delete(ThugAnimationEvent *event,uint32_t flags,const ThugMemory *memory) {
    event->methods=&thug_animation_event_base_methods;
    if ((uint8_t)flags&1) memory->release(memory->context,event);
    return event;
}
/* 0x004860c0. FILD preserves the full signed frame before comparing to float
 * endpoints; only the second endpoint is optionally excluded. */
uint32_t thug_animation_event_crosses(const ThugAnimationEvent *event,float from,float to,uint32_t inclusive) {
    double frame=event->frame;
    if (from<to) return frame>=from && ((uint8_t)inclusive ? frame<=to : frame<to);
    return frame<=from && ((uint8_t)inclusive ? frame>=to : frame>to);
}
/* 0x00486160 and 0x00486440. Disable before delivery; handlers may re-enable. */
uint8_t thug_animation_event_trigger(ThugAnimationEvent *event,ThugReferencedObject *owner,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    if (!event->enabled) return 0;
    const ThugAnimationEventMethods *methods=event->methods; event->enabled=0;
    return methods->trigger(event,owner,diagnostics,memory);
}
uint8_t thug_animation_event_emit(ThugAnimationEvent *event,ThugReferencedObject *owner,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    thug_object_emit_event(owner,event->event,event->parameters,diagnostics,memory); return 1;
}
/* 0x00481bb0. Count clears before callbacks; a zero-sized allocated array still
 * uses its header, but a zero channel count bypasses cleanup entirely. */
void thug_animation_clear_events(ThugAnimationChannel *channel,const ThugMemory *memory) {
    if (channel->event_count && channel->events) {
        ThugAnimationEvent *events=channel->events; uint32_t *header=(uint32_t *)events-1;
        channel->event_count=0;
        if (*header) events->methods->dispose(events,3,memory);
        else memory->release(memory->context,header);
        channel->events=NULL;
    }
}
/* 0x00481c00. The caller clears the previous array. Required event checksums,
 * valid arrays and successful storage allocation are internal contracts. */
void thug_animation_load_events(ThugAnimationChannel *channel,uint32_t name,const ThugMemory *memory) {
    ThugAnimationComponent *component=(ThugAnimationComponent *)thug_object_find_component(channel->body,0x7149b753);
    if (!component) return;
    uint32_t set=thug_animation_component_events(component); if (!set) return;
    const ThugScriptStructure *definitions=thug_script_get_global_structure(set,1); if (!definitions) return;
    ThugScriptArray *array;
    if (!thug_script_get_array(definitions,name,&array,0)) return;
    uint32_t count=array->count; channel->event_count=count;
    if (!count) return;
    uint32_t *header=thug_allocate_array_storage(count*0x14+4,memory);
    ThugAnimationEvent *events=NULL;
    if (header) {
        *header=count; events=(ThugAnimationEvent *)(header+1);
        for (uint32_t i=0;i<count;++i) thug_animation_event_initialize(events+i);
    }
    channel->events=events;
    for (uint32_t i=0;i<channel->event_count;++i) {
        const ThugScriptStructure *entry=thug_script_array_structure(array,i);
        uint32_t frame=0;
        if (!thug_script_get_integer(entry,0x4a07c332,&frame,0)) {
            float seconds=0; thug_script_get_float(entry,0x906b67ba,&seconds,1);
            frame=thug_truncate_double_low_word(thug_platform_round_x87_single((double)seconds*60.0));
        }
        uint32_t event; thug_script_get_checksum(entry,0xc451f558,&event,1);
        ThugScriptStructure *parameters=NULL; thug_script_get_structure(entry,0x7031f10c,&parameters,0);
        thug_animation_event_setup(channel->events+i,frame,event,parameters,memory);
        thug_animation_event_set_enabled(channel->events+i,1);
    }
}
/* 0x004819a0. */
void thug_animation_reset_events(ThugAnimationChannel *channel) {
    for (uint32_t i=0;i<channel->event_count;++i) thug_animation_event_set_enabled(channel->events+i,1);
}
/* 0x00481e10. The wrap comparison uses unspilled PC24 values. Event callbacks
 * can replace the array, change the count or change the owner for later events. */
void thug_animation_update_events(ThugAnimationChannel *channel,float from,float to,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    if (!channel->events_enabled || channel->unknown_38!=2) return;
    double first=thug_platform_round_x87_single((double)from*60.0);
    double second=thug_platform_round_x87_single((double)to*60.0);
    float start=(float)first,finish=(float)second;
    if (channel->direction==0 ? first>second : second>first) {
        thug_animation_reset_events(channel); __builtin_memcpy(&start,&channel->start,4);
    }
    for (uint32_t i=0;i<channel->event_count;++i) {
        thug_animation_event_set_enabled(channel->events+i,1);
        ThugAnimationEvent *event=channel->events+i;
        if (event->methods->crosses(event,start,finish,0))
            thug_animation_event_trigger(channel->events+i,(ThugReferencedObject *)channel->body,diagnostics,memory);
    }
}
