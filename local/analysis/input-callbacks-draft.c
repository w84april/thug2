/* Original Input component's packet callbacks and targeted button events. */
#include "../../src/game/ui.h"
#include "../../src/script/delivery.h"
#include "../../src/script/values.h"
#include "../../src/core/number.h"
#include "../../src/core/timing.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float flt(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
void thug_input_pad_clear_draft(void *);
void thug_input_pad_update_draft(void *,const uint8_t *);
/* 006fa7d0 is distinct from the other network singleton at 007cce14. */
ThugNetworkState *thug_input_network_state_draft;

/* 00460820. This appends/replaces parameters; it does not clear destination. */
void thug_object_copy_parameters_draft(const void *p,ThugScriptStructure *to,const ThugMemory *m){
    const ThugScriptStructure *source=ptr(p,0x20);
    if(source)thug_script_structure_merge_optional(to,source,m);
}
/* 0041ebf0. The integer deadline test differs from the pad's float comparison. */
void thug_input_button_event_draft(void *p,const uint8_t *packet,uint32_t index,uint32_t mask,
    uint32_t press,uint32_t release,const void *button,const ThugDiagnostics *d,const ThugMemory *m){
    uint8_t *b=p;
    if(button){
        uint32_t deadline=thug_truncate_double_low_word(flt(button,0x1c));
        if(thug_frame_time()<deadline)return;
    }
    if(packet[index]){
        if(!(word(p,0x18)&mask)&&b[0x49a]&&!b[0x498]&&!b[0x499])
            thug_object_emit_event(ptr(p,0xc),press,0,d,m);
        put(p,0x1c,word(p,0x1c)|mask);
    }else if((word(p,0x18)&mask)&&b[0x49a]&&!b[0x498]&&!b[0x499])
        thug_object_emit_event(ptr(p,0xc),release,0,d,m);
}
/* 0041eca0. Ordered events, with state reloaded after each synchronous handler. */
void thug_input_packet_events_draft(void *p,const uint8_t *packet,const ThugDiagnostics *d,const ThugMemory *m){
    static const struct {uint32_t index,mask,press,release,button;} events[]={
        {6,0x40,0x5c8faa09,0xb27804a2,0x20},
        {7,0x80,0xd26adae9,0xaef7dfd3,0x40},
        {5,0x20,0xb4f2adba,0xc86fa880,0x60},
        {4,0x10,0x0edbbc2b,0xc8abf89c,0x80},
        {9,0x200,0xb069b600,0xe5aae06b,0x160},
        {11,0x800,0xa93dbbd0,0xfcfeedbb,0x180},
        {8,0x100,0x7f695a77,0x7b684919,0x1a0},
        {10,0x400,0x42717176,0xbbbef674,0x1c0},
        {12,0x1000,0xc6547217,0x28a3dcbc,0xa0},
        {14,0x4000,0x5f5d23ad,0xb1aa8d06,0xc0},
        {16,0x10000,0x285a133b,0xc6adbd90,0xe0},
        {13,0x2000,0x12154dc8,0xfce2e363,0x100},
        {15,0x8000,0x8b1c1c72,0x65ebb2d9,0x120},
        {17,0x20000,0xfc1b2ce4,0x12ec824f,0x140},
        {22,0x400000,0x33947317,0xf5e437a0,0},
        {23,0x800000,0xf8de049b,0x3eae402c,0},
        {24,0x1000000,0xac7f105a,0x55b09758,0}
    };
    put(p,0x18,word(p,0x1c));put(p,0x1c,0);
    for(unsigned i=0;i<17;i++){
        const void *button=events[i].button?(uint8_t *)p+events[i].button:0;
        thug_input_button_event_draft(p,packet,events[i].index,events[i].mask,
            events[i].press,events[i].release,button,d,m);
    }
}
static void *find_and_unlink(uint32_t name){
    ThugObjectReference ref;
    thug_ui_find(&ref,name,0);void *object=ref.object;
    if(ref.object)thug_object_reference_unlink(ref.object,&ref);
    return object;
}
/* 0041ef20. Valid modal UI objects provide the cdc00e63 checksum. The original
 * reads an uninitialized stack word when it is absent; that malformed-state
 * path is outside this recovered contract, and traps instead of inventing it. */
uint8_t thug_input_ui_blocked_draft(const ThugMemory *m){
    if(!thug_network_is_active(thug_input_network_state_draft))return 0;
    if(find_and_unlink(0x2edb780f))return 1;
    void *modal=find_and_unlink(0x56a1eae3);
    if(modal){
        ThugScriptStructure *parameters=thug_script_structure_allocate(8,m);
        if(parameters)thug_script_structure_initialize(parameters);
        thug_object_copy_parameters_draft(modal,parameters,m);
        uint32_t mode;
        uint8_t found=thug_script_get_checksum(parameters,0xcdc00e63,&mode,0);
        if(parameters){thug_script_structure_destroy(parameters,m);thug_script_structure_free(parameters,m);}
        if(!found)__builtin_trap();
        if(mode==0xf649d637)return 1;
    }
    return find_and_unlink(0x31631b98)!=0;
}
/* 0041f090. Primary packet events precede the UI gate and pad decoding. */
void thug_input_primary_packet_draft(void *p,const uint8_t *packet,const ThugDiagnostics *d,const ThugMemory *m){
    uint8_t *b=p;
    if(word(ptr(p,0xc),0x104)&1)return;
    thug_input_packet_events_draft(p,packet,d,m);
    uint8_t blocked=thug_input_ui_blocked_draft(m);
    if(b[0x498]||b[0x499]||blocked){
        thug_input_pad_clear_draft(b+0x20);
        if(blocked)put(p,0x1c,0);
    }else thug_input_pad_update_draft(b+0x20,packet);
}
/* 0041f100. Secondary pad deliberately generates no primary button events. */
void thug_input_secondary_packet_draft(void *p,const uint8_t *packet,const ThugMemory *m){
    uint8_t *b=p;
    if(word(ptr(p,0xc),0x104)&1)return;
    uint8_t blocked=thug_input_ui_blocked_draft(m);
    if(b[0x498]||b[0x499]||blocked){
        thug_input_pad_clear_draft(b+0x258);
        if(blocked)put(p,0x1c,0);
    }else thug_input_pad_update_draft(b+0x258,packet);
}
/* 0041f170 / 0041f190. Original cdecl callbacks take the task as an argument. */
void thug_input_primary_task_draft(void *task,const ThugDiagnostics *d,const ThugMemory *m){
    thug_input_primary_packet_draft(ptr(task,0x28),ptr(task,0x18),d,m);
}
void thug_input_secondary_task_draft(void *task,const ThugMemory *m){
    thug_input_secondary_packet_draft(ptr(task,0x28),ptr(task,0x18),m);
}
