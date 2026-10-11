/* Derived from the pinned lifecycle source; see build-prop-sound-draft.py. */
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/game/drawing.h"
#include "../../src/audio/device.h"
#include "../../src/platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
static uint32_t rw(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void ww(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static float rf(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void wf(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)rw(p,o);}
static void vector(void *p,unsigned o,float x,float y,float z){wf(p,o,x);wf(p,o+4,y);wf(p,o+8,z);wf(p,o+12,1);}
static const ThugComponentMethods *methods(const void *p){return ptr(p,0);}
extern const ThugComponentMethods thug_suspend_methods_draft,thug_motion_methods_draft,
 thug_object_proximity_methods_draft,thug_object_sound_methods_draft,
 thug_lockobj_methods_draft,thug_component_b87c8e43_methods_draft;
static void set_methods(void *p,const ThugComponentMethods *m){ww(p,0,(uintptr_t)m);}

/* 00433f50. The squared distance uses the unspilled PC24 product. */
void *thug_suspend_construct_draft(void *p){
    thug_component_construct(p);set_methods(p,&thug_suspend_methods_draft);ww(p,4,0xce0ca665);
    double distance=R(thug_script_get_global_number(0xad501995,0)*12);
    wf(p,0x1c,(float)distance);((uint8_t *)p)[0x18]=1;ww(p,0x28,10);ww(p,0x44,3);
    wf(p,0x20,(float)R(distance*distance));return p;
}
/* 00434000. Parameter and global lookups retain their original precedence.
 * The three original assertions call the already recovered bare RET5480a0.
 * Comparisons have no data effect; keeping their PC24 temporaries prevents
 * accidentally squaring a float-spilled distance instead. */
void thug_suspend_initialize_draft(void *p,const ThugScriptStructure *s){
    float *distance=(void *)((uint8_t *)p+0x1c);
    if(thug_script_get_float(s,0xe4279ba2,distance,0)){
        if(*distance==0&&!thug_script_get_float(s,0x4eedfae7,distance,0))
            *distance=(float)thug_script_get_global_number(0xad501995,0);
        ((uint8_t *)p)[0x18]=0;double v=R((double)*distance*12);
        *distance=(float)v;wf(p,0x20,(float)R(v*v));
    }
    if(thug_script_has_flag(s,0xcb839dc1))((uint8_t *)p)[0x18]=1;
    if(thug_script_get_global_integer(0x95edc6f6,0)){
        ww(p,0x34,0x49742400);ww(p,0x38,0x49742410);ww(p,0x3c,0x49742420);ww(p,0x40,0x49742430);return;
    }
    wf(p,0x34,50);wf(p,0x3c,1000001);wf(p,0x40,1000002);
    thug_script_get_float(s,0x4eedfae7,(void *)((uint8_t *)p+0x34),0);
    wf(p,0x38,(float)R((double)rf(p,0x34)+75));
    thug_script_get_float(s,0xd7e4ab5d,(void *)((uint8_t *)p+0x38),0);
    thug_script_get_float(s,0xa0e39bcb,(void *)((uint8_t *)p+0x3c),0);
    thug_script_get_float(s,0x3e870e68,(void *)((uint8_t *)p+0x40),0);
    double a=R((double)rf(p,0x34)*12),b=R((double)rf(p,0x38)*12);
    wf(p,0x34,(float)a);wf(p,0x38,(float)b);
    wf(p,0x3c,(float)R((double)rf(p,0x3c)*12));wf(p,0x40,(float)R((double)rf(p,0x40)*12));
    if(a>=b)thug_draw_style_noop(p);
    if(rf(p,0x38)>=rf(p,0x3c))thug_draw_style_noop(p);
    if(rf(p,0x3c)>=rf(p,0x40))thug_draw_style_noop(p);
    wf(p,0x34,(float)R(thug_script_get_global_number(0xd3d072f9,0)*rf(p,0x34)));
    wf(p,0x38,(float)R(thug_script_get_global_number(0x0432f2a1,0)*rf(p,0x38)));
}
/* 004341c0 /00433e50. */
void thug_suspend_finalize_draft(void *p){ww(p,0x2c,(uintptr_t)thug_object_find_component(ptr(p,12),0x286a8d26));}
void thug_suspend_update_draft(void *p){thug_component_suspend(p,1);}
/* 00433e10/00433fd0/00434290. */
void thug_suspend_destroy_draft(void *p){set_methods(p,&thug_suspend_methods_draft);thug_component_destroy(p);}
void *thug_suspend_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_suspend_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
void *thug_suspend_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x4c,m);return p?thug_suspend_construct_draft(p):0;}

/* 00423d00. Reset only the explicitly owned fields, preserving the rest. */
void thug_motion_reset_draft(void *p){
    for(unsigned o=0x12c;o<=0x18c;o+=16)vector(p,o,0,0,0);
    vector(p,0x108,0,0,0);
    const unsigned zeros[]={0x118,0x11c,0x20,0x120,0x124,0x24,0x28,0x2c,0x30,0x34,0x1a4,0x1a8,0x1ac,0x1c4,0x1c8,0x18,0x1c};
    for(unsigned i=0;i<sizeof(zeros)/sizeof(*zeros);i++)ww(p,zeros[i],0);
    for(unsigned o=0x40;o<=0x60;o+=16)vector(p,o,0,0,0);
    for(unsigned o=0x74;o<=0xf4;o+=16)vector(p,o,0,0,0);
}
/* 00424aa0 and the inlined constructor in00426650. */
void *thug_motion_construct_draft(void *p){
    thug_component_construct(p);set_methods(p,&thug_motion_methods_draft);
    ww(p,0x19c,0);ww(p,0x1a0,0);ww(p,4,0x0a015e17);ww(p,0x1ec,0);ww(p,0x104,0);
    ((uint8_t *)p)[0x70]=1;thug_motion_reset_draft(p);return p;
}
void *thug_motion_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x24c,m);return p?thug_motion_construct_draft(p):0;}
/* 00426720. Name defaults to zero; the real recovered orientation helper runs. */
void thug_motion_initialize_draft(void *p,const ThugScriptStructure *s){
    uint32_t name=0;thug_script_get_checksum(s,0xa1dc81f9,&name,0);
    ww(p,0x1e8,name);ww(p,0x1e4,name);thug_motion_orient_to_node(p,s);
}
/* 00424ae0. Owned path object uses its actual virtual destructor; the other
 * two owned buffers are released in original order and cleared afterwards. */
void thug_motion_destroy_draft(void *p,const ThugMemory *m){
    set_methods(p,&thug_motion_methods_draft);void *child=ptr(p,0x1ec);
    if(child){methods(child)->dispose(child,1,m);ww(p,0x1ec,0);}
    child=ptr(p,0x1cc);if(child){m->release(m->context,child);ww(p,0x1cc,0);}
    child=ptr(p,0x1f0);if(child){thug_draw_style_noop(child);m->release(m->context,child);ww(p,0x1f0,0);}
    thug_component_destroy(p);
}
/* 004266f0. */
void *thug_motion_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_motion_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;}

/* 004ec370/004ec420/004ec240/004ec390. */
void *thug_object_proximity_construct_draft(void *p){thug_component_construct(p);set_methods(p,&thug_object_proximity_methods_draft);ww(p,4,0x1d5b1ae6);return p;}
void *thug_object_proximity_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x30,m);return p?thug_object_proximity_construct_draft(p):0;}
void thug_object_proximity_destroy_draft(void *p){set_methods(p,&thug_object_proximity_methods_draft);thug_component_destroy(p);}
void *thug_object_proximity_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_object_proximity_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}

/* 0046ab90. Unlike named activation, this lookup requires an initialized
 * proximity manager. Retain first-match ordering and live next links. */
extern void *thug_proximity_manager_draft;
void *thug_proximity_find_draft(uint32_t name){
    for(void *p=ptr(thug_proximity_manager_draft,0);p;p=ptr(p,0xa4))if(rw(p,0)==name)return p;
    return 0;
}
/* 00432d90/00433100/00432ca0. */
void *thug_object_sound_construct_draft(void *p){
    thug_component_construct(p);ww(p,0xb8,0);ww(p,0xbc,0);set_methods(p,&thug_object_sound_methods_draft);ww(p,4,0x07713c7b);
    vector(p,0x98,0,0,0);vector(p,0xa8,0,0,0);return p;
}
void *thug_object_sound_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0xc0,m);return p?thug_object_sound_construct_draft(p):0;}
void thug_object_sound_initialize_draft(void *p,const ThugScriptStructure *s){uint32_t name;if(thug_script_get_checksum(s,0x08470f2e,&name,0))ww(p,0xbc,(uintptr_t)thug_proximity_find_draft(name));}
/* 0047ad80. The name fallback still reads both script flags in their original
 * short-circuit order, even though neither changes the selected voice. */
int32_t thug_sound_find_voice_draft(const ThugSoundConfiguration *config,uint32_t id){
    (void)config;
    for(unsigned i=0;i<48;i++)if(thug_sound_voices[i].id==id&&thug_audio_slot_active(i))return i;
    for(unsigned i=0;i<48;i++)if(thug_sound_voices[i].name==id&&thug_audio_slot_active(i)){
        if(!thug_script_get_global_integer(0x6d2e270e,0))thug_script_get_global_integer(0xd7bb618d,0);
        return i;
    }
    return -1;
}
/* 0047c7a0. Device stop return is ignored and the active byte stays unchanged. */
void thug_audio_stop_slot_draft(uint32_t i){ThugAudioBuffer *b=thug_audio_slots[i].buffer;if(b)b->methods->stop(b);}
uint32_t thug_sound_pending_count_draft; /* 006f85bc */
/* 0047bb50. Capture the successor before callbacks, then unlink using LIVE
 * next/previous pointers. Pool records are unlinked, not heap-freed. */
void thug_sound_remove_owner_draft(const ThugSoundConfiguration *config,void *owner){
    void *current=thug_sound_pending;
    while(current){
        void *next=ptr(current,0x10);
        if(ptr(current,12)==owner){
            uint32_t id=rw(current,0);ww(current,8,0);
            if(!thug_sound_disabled()&&id){
                for(unsigned i=0;i<48;i++)if(thug_sound_voices[i].id==id){
                    if(thug_audio_slot_active(i)&&!thug_sound_disabled()){
                        int32_t found=thug_sound_find_voice_draft(config,rw(current,0));
                        if(found>=0)thug_audio_stop_slot_draft((uint32_t)found);
                    }
                    break;
                }
            }
            void *live_next=ptr(current,0x10);if(live_next)ww(live_next,0x14,rw(current,0x14));
            void *previous=ptr(current,0x14);
            if(previous)ww(previous,0x10,rw(current,0x10));else thug_sound_pending=ptr(current,0x10);
            --thug_sound_pending_count_draft;
        }
        current=next;
    }
}
/* 00432df0/00433160. */
void thug_object_sound_destroy_draft(void *p){set_methods(p,&thug_object_sound_methods_draft);thug_sound_remove_owner_draft(thug_sound_configuration,p);thug_component_destroy(p);}
void *thug_object_sound_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_object_sound_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}

/* 0041f500/0041ff20/0041f400/0041f440. */
void *thug_lockobj_construct_draft(void *p){thug_component_construct(p);((uint8_t *)p)[0x8c]&=~4u;set_methods(p,&thug_lockobj_methods_draft);ww(p,4,0x5cb5cb7e);return p;}
void *thug_lockobj_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x90,m);return p?thug_lockobj_construct_draft(p):0;}
void thug_lockobj_destroy_draft(void *p){set_methods(p,&thug_lockobj_methods_draft);thug_component_destroy(p);}
void *thug_lockobj_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_lockobj_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 0041aad0/0041adc0/0041a810/0041a880. Type name not yet resolved. */
void *thug_component_b87c8e43_construct_draft(void *p){thug_component_construct(p);set_methods(p,&thug_component_b87c8e43_methods_draft);ww(p,4,0xb87c8e43);vector(p,0x18,10,10,10);vector(p,0x28,-10,-10,-10);vector(p,0x38,0,0,0);return p;}
void *thug_component_b87c8e43_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x4c,m);return p?thug_component_b87c8e43_construct_draft(p):0;}
void thug_component_b87c8e43_destroy_draft(void *p){set_methods(p,&thug_component_b87c8e43_methods_draft);thug_component_destroy(p);}
void *thug_component_b87c8e43_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_component_b87c8e43_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 0051b970. Dispatches the concrete suspend virtual, unlike direct433e50. */
void thug_component_suspend_update_draft(void *p){methods(p)->suspend(p,1);}

/* Typed ABI bridges are not new game routines. Zero slots explicitly remain
 * unavailable: notably Motion/Proximity updates, Sound moved/update, LockObj
 * initialization/update and several checksum commands. Never return synthetic
 * success for them or finalize Sound through a replacement empty callback. */
static void empty(void *p){thug_draw_style_noop(p);}
static void empty_init(void *p,const ThugScriptStructure *s){thug_component_empty_one(p,(void *)s);}
static void empty_suspend(void *p,uint32_t flag){thug_component_empty_one(p,(void *)(uintptr_t)flag);}
static uint32_t unhandled(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *script){return thug_animation_unhandled_command(p,n,s,script,0,0);}
static void suspend_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_suspend_update_draft(p);}
static void virtual_suspend_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
#define COMMON .unknown_10=empty,.refresh=thug_component_refresh,.unknown_20=thug_component_empty_one,.unknown_28=thug_component_empty_one
const ThugComponentMethods thug_suspend_methods_draft={.dispose=thug_suspend_delete_draft,.update=suspend_frame,.initialize=thug_suspend_initialize_draft,.finalize=thug_suspend_finalize_draft,COMMON,.unknown_18=thug_component_empty_two,.suspend=empty_suspend,.moved=thug_component_empty_frame_bridge,.descriptor=thug_component_descriptor,.checksum=unhandled};
void thug_motion_frame_prefix_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
const ThugComponentMethods thug_motion_methods_draft={.update=thug_motion_frame_prefix_draft,.dispose=thug_motion_delete_draft,.initialize=thug_motion_initialize_draft,.finalize=empty,COMMON,.suspend=thug_component_suspend,.moved=thug_component_empty_frame_bridge,.descriptor=thug_component_descriptor};
void thug_motion_frame_proximity_boundary_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
const ThugComponentMethods thug_object_proximity_methods_draft={.update=thug_motion_frame_proximity_boundary_draft,.dispose=thug_object_proximity_delete_draft,.initialize=empty_init,.finalize=empty,COMMON,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.moved=thug_component_empty_frame_bridge,.descriptor=thug_component_descriptor,.checksum=unhandled};
void thug_object_sound_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_object_sound_moved_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
const ThugComponentMethods thug_object_sound_methods_draft={.update=thug_object_sound_frame_draft,.moved=thug_object_sound_moved_draft,.dispose=thug_object_sound_delete_draft,.initialize=thug_object_sound_initialize_draft,.finalize=empty,COMMON,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.descriptor=thug_component_descriptor};
void thug_lockobj_initialize_entry_draft(void *,const ThugScriptStructure *);
const ThugComponentMethods thug_lockobj_methods_draft={.initialize=thug_lockobj_initialize_entry_draft,.dispose=thug_lockobj_delete_draft,.finalize=empty,COMMON,.unknown_18=thug_component_empty_two,.suspend=empty_suspend,.moved=thug_component_empty_frame_bridge,.descriptor=thug_component_descriptor_base};
const ThugComponentMethods thug_component_b87c8e43_methods_draft={.dispose=thug_component_b87c8e43_delete_draft,.update=virtual_suspend_frame,.initialize=empty_init,.finalize=empty,COMMON,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.moved=thug_component_empty_frame_bridge,.descriptor=thug_component_descriptor_base};
