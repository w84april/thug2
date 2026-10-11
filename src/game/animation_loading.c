#include "animation_cache.h"
#include "animation.h"
#include "../core/matrix.h"
#include <stddef.h>

static uint32_t word(const void *p) { uint32_t v;__builtin_memcpy(&v,p,4);return v; }
static uint16_t half(const void *p) { uint16_t v;__builtin_memcpy(&v,p,2);return v; }
static void set_word(void *p,uint32_t v) { __builtin_memcpy(p,&v,4); }
static const uint8_t *advance(const uint8_t *p,uint32_t n) { return (const uint8_t *)((uintptr_t)p+n); }
static const uint8_t *aligned(const uint8_t *p) { return (const uint8_t *)(((uintptr_t)p+3)&~(uintptr_t)3); }
/* 64880c,648818,648824,648830,64883c; action methods remain unavailable. */
const ThugAnimationEventMethods thug_animation_file_word_methods[5]={
    {.dispose=thug_animation_file_event_delete,.crosses=thug_animation_event_crosses},
    {.dispose=thug_animation_file_event_delete,.crosses=thug_animation_event_crosses},
    {.dispose=thug_animation_file_event_delete,.crosses=thug_animation_event_crosses},
    {.dispose=thug_animation_file_event_delete,.crosses=thug_animation_event_crosses},
    {.dispose=thug_animation_file_event_delete,.crosses=thug_animation_event_crosses}
};
const ThugAnimationEventMethods thug_animation_file_transform_methods={.dispose=thug_animation_file_event_delete};
/* 0x004819e0 and 0x00486460. The file-event destructor owns no payload. */
void thug_animation_file_event_destroy(ThugAnimationEvent *event) { event->methods=&thug_animation_event_base_methods; }
void *thug_animation_file_event_delete(ThugAnimationEvent *event,uint32_t flags,const ThugMemory *memory) {
    thug_animation_file_event_destroy(event);if((uint8_t)flags&1)memory->release(memory->context,event);return event;
}
/* 0x00486490. Rotation uses the fixed +X quarter-turn before position axis
 * conversion. The input snapshots happen after the constructor's first writes. */
ThugAnimationEvent *thug_animation_transform_event_initialize(ThugAnimationEvent *event,uint32_t frame,const float *rotation,const float *position,uint32_t flag) {
    uint8_t *out=(uint8_t *)event;set_word(out+4,frame);out[8]=0;
    event->methods=&thug_animation_file_transform_methods;
    set_word(out+12,0);set_word(out+16,0);set_word(out+20,0);set_word(out+24,0x3f800000);
    float axis[4]={1,0,0,1},turn[4],q[4];
    thug_quaternion_axis_angle(turn,axis,1.5707963705062866f);
    for(uint32_t i=0;i<4;i++)set_word(q+i,word(rotation+i));
    thug_quaternion_multiply(q,turn);
    set_word(out+16,word(q+1));set_word(out+12,word(q));set_word(out+20,word(q+2));set_word(out+24,word(q+3));
    set_word(out+28,word(position));set_word(out+32,word(position+2));
    uint32_t y=word(position+1);if((y&0x7f800000)==0x7f800000&&(y&0x7fffff))y|=0x400000;
    set_word(out+36,y^0x80000000);set_word(out+40,0x3f800000);out[44]=(uint8_t)flag;return event;
}
/* 0x00486680. Unknown types skip their declared payload and return null.
 * Known types consume fixed payloads, independent of the declared size. */
ThugAnimationEvent *thug_animation_parse_file_event(const uint8_t **cursor,const ThugMemory *memory) {
    const uint8_t *p=*cursor;uint32_t frame=word(p),kind=word(p+4),size=word(p+8);p+=12;*cursor=p;
    if(kind<1||kind>7) { *cursor=advance(p,size);return NULL; }
    if(kind==2||kind==7) {
        float position[4],rotation[4];
        for(uint32_t i=0;i<4;i++)set_word(position+i,word(p+i*4));p+=16;*cursor=p;
        for(uint32_t i=0;i<4;i++)set_word(rotation+i,word(p+i*4));p+=16;*cursor=p;
        ThugAnimationEvent *event=thug_allocate_array_storage(0x30,memory);
        return event?thug_animation_transform_event_initialize(event,frame,rotation,position,kind==7):NULL;
    }
    uint32_t value=kind==3?0:word(p);*cursor=advance(p,kind==3?32:4);
    ThugAnimationEvent *event=thug_allocate_array_storage(kind==3?12:16,memory);if(!event)return NULL;
    uint32_t index=kind==1?0:kind==4?1:kind==3?2:kind==5?3:4;
    event->frame=(int32_t)frame;event->enabled=0;event->methods=&thug_animation_file_word_methods[index];
    if(kind!=3)set_word((uint8_t *)event+12,value);return event;
}
/* 0x00482af0. Flags, key counts and the high reference bits survive. */
ThugKeyframeAnimation *thug_keyframe_animation_initialize(ThugKeyframeAnimation *a) {
    a->references&=0xfe00;a->duration=0;a->bone_count=0;a->rotation_table=0;
    a->rotation_keys=0;a->translation_keys=0;a->bone_keys=0;a->bone_map=0;
    a->rotation_lengths=0;a->translation_lengths=0;a->event_count=0;a->events=0;a->cache=0;a->bone_mask=0;return a;
}
/* 0x00482b30. Preserve pointers and count after releasing ownership. */
void thug_keyframe_animation_destroy(ThugKeyframeAnimation *a,const ThugMemory *memory) {
    for(int32_t i=0;i<a->event_count;i++) { ThugAnimationEvent *e=a->events[i];if(e)e->methods->dispose(e,1,memory); }
    if(a->events)memory->release(memory->context,a->events);
    if(a->cache) { ThugAnimationCacheManager *m=thug_animation_cache_instance();if(m)thug_animation_cache_remove(m,a,memory); }
}
static uint8_t parse_events(ThugKeyframeAnimation *a,const uint8_t *header,const uint8_t *cursor,const ThugMemory *memory) {
    uint32_t count=word(header+12);
    if(!count)a->events=NULL;
    else {
        a->events=memory->allocate(memory->context,count*4,0);
        for(uint32_t i=0;i<word(header+12);i++) {
            ThugAnimationEvent *event=thug_animation_parse_file_event(&cursor,memory);
            if(!event)return 0;
            a->events[i]=event;
        }
    }
    a->event_count=(int16_t)half(header+12);return 1;
}
static const uint8_t *skip_mask(const uint8_t *p) {
    uint32_t value=word(p)-1;
    int32_t groups=(int32_t)value/32;
    return advance(p,(uint32_t)groups*4+8);
}
/* 0x00484200. Compressed streams point into the borrowed input buffer. */
uint8_t thug_keyframe_animation_parse_compressed(ThugKeyframeAnimation *a,const void *input,const ThugMemory *memory) {
    const uint8_t *header=input,*p=header+16;
    a->bone_count=word(header);a->rotation_count=(int16_t)half(header+4);a->translation_count=(int16_t)half(header+8);
    uint32_t rotation_bytes=word(p);p+=4;uint32_t translation_bytes=word(p);p+=4;
    a->rotation_lengths=(const uint16_t *)p;p=advance(p,a->bone_count*2);
    a->translation_lengths=(const uint16_t *)p;p=aligned(advance(p,a->bone_count*2));
    uint32_t flags=a->flags;a->bone_map=0;
    if(flags&0x2000) { a->rotation_table=p;p+=0x600; }
    if(flags&0x80000) { a->bone_mask=p;p=skip_mask(p); }
    p=aligned(p);
    if(!(flags&0x9000000)) { a->rotation_keys=p;p=advance(p,rotation_bytes);a->translation_keys=p;p=advance(p,translation_bytes); }
    return parse_events(a,header,aligned(p),memory);
}
/* 0x00484370. Fixed-width keys use 8 or 16 bytes depending on flags. */
uint8_t thug_keyframe_animation_parse_fixed(ThugKeyframeAnimation *a,const void *input,const ThugMemory *memory) {
    const uint8_t *header=input,*p=header+16;
    a->bone_count=word(header);a->rotation_count=(int16_t)half(header+4);a->translation_count=(int16_t)half(header+8);
    uint32_t flags=a->flags;
    if(flags&0x1000000) { a->bone_map=p;p=advance(p,a->bone_count*4); }else a->bone_map=0;
    if(flags&0x80000) { a->bone_mask=p;p=skip_mask(p); }
    a->bone_keys=p;p=aligned(advance(p,a->bone_count*(flags&0x400000?4:2)));
    uint32_t stride=flags&0x9000000?16:8;
    a->rotation_keys=p;p=advance(p,(uint32_t)(int32_t)a->rotation_count*stride);
    a->translation_keys=p;p=advance(p,(uint32_t)(int32_t)a->translation_count*stride);
    return parse_events(a,header,aligned(p),memory);
}
/* 0x004856c0. Version, length and the third original argument are unused.
 * Buffer bounds must be validated by the port before entering this old parser. */
uint8_t thug_keyframe_animation_load_buffer(ThugKeyframeAnimation *a,const void *input,uint32_t size,uint32_t unused,const ThugMemory *memory) {
    (void)size;(void)unused;const uint8_t *p=input;set_word(&a->duration,word(p+8));a->flags=word(p+4);
    uint8_t result=0;
    if(a->flags&0x10000000)result=thug_keyframe_animation_parse_fixed(a,p+12,memory);
    else if(word(p+4)&0x800000)result=thug_keyframe_animation_parse_compressed(a,p+12,memory);
    if(a->flags&0x800)thug_keyframe_animation_build_cache(a,thug_animation_cache_format(thug_animation_cache_instance()),memory);
    return result;
}
/* 0x004809f0. Manager allocation/heap creation belongs to a separate caller. */
void thug_animation_cache_initialize(ThugAnimationCacheManager *m,uint32_t alignment,uint32_t format,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++) {
        ThugAnimationCacheBlock *b=thug_allocate_zeroed(0x168,memory);
        if(b) { b->flags&=0xa000;b->rotations=0;b->translations=0;b->animation=0;b->bone_count=0;b->rotation_stride=0;b->translation_stride=0;b->allocated=0;b->payload=0;b->storage=0;b->format=0; }
        m->blocks[i]=b;
    }
    m->alignment=alignment;m->format=format;
}
