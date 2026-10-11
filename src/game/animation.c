#include "animation_controllers.h"
#include "../platform/math.h"
#include "../core/timing.h"
#include "../network/queue.h"
#include <stddef.h>
_Static_assert(sizeof(ThugAnimationChannel)==0x74,"Animation channel allocation");
_Static_assert(sizeof(ThugBalanceAnimationController)==0x38,"Balance controller allocation");
_Static_assert(offsetof(ThugAnimationComponent,state)==0x34,"Animation component state");
const ThugAnimationChannelMethods thug_animation_link_methods;
static void update_base(ThugAnimationChannel *c,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; thug_animation_update_time(c);
}
const ThugAnimationChannelMethods thug_animation_channel_base_methods={.dispose=thug_animation_timeline_delete,.update=update_base,.timeline=thug_animation_set_timeline};
const ThugAnimationChannelMethods thug_animation_channel_methods={.dispose=thug_animation_channel_delete,.update=thug_animation_channel_update,.timeline=thug_animation_set_timeline,.command=thug_animation_channel_command};
const ThugAnimationControllerMethods thug_animation_controller_base_methods;
static uint32_t balance_command(ThugAnimationController *c,uint32_t n,const ThugScriptStructure *p,void *s,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)m; return thug_balance_animation_command(c,n,p,s,d);
}
static void balance_configure(ThugAnimationController *c,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; thug_animation_configure_controller(c,p);
}
const ThugAnimationControllerMethods thug_balance_animation_methods = {.dispose=thug_balance_animation_delete,.command=balance_command,.configure=balance_configure,.update=thug_balance_animation_update};
static float quiet_bound(float value) {
    uint32_t bits; __builtin_memcpy(&bits,&value,4);
    if ((bits&0x7f800000)==0x7f800000 && (bits&0x7fffff)) bits|=0x400000;
    __builtin_memcpy(&value,&bits,4); return value;
}
/* 0x00481650. The list links initially point at the channel itself. */
ThugAnimationChannel *thug_animation_timeline_initialize(ThugAnimationChannel *channel) {
    channel->id=(uintptr_t)channel; channel->unknown_8=0;
    channel->previous=channel->next=channel;
    channel->methods=&thug_animation_channel_base_methods;
    channel->start=channel->current=channel->end=channel->speed=0;
    channel->direction=0; channel->loop=1; channel->flag_2c=0;
    channel->animation_name=0xf60c9090; return channel;
}
/* 0x004814b0. Keep PC24 rounding and the wider exponent before comparisons.
 * Wrap loops require a range and increment for which the original terminates. */
double thug_animation_advance_time(ThugAnimationChannel *channel) {
    #define R thug_platform_round_x87_single
    float next=0,boundary=0; double wrapped=0;
    channel->flag_2c=0;
    if (channel->loop==3) return 0;
    if (channel->direction==0) {
        double value=R(R(R(thug_frame_duration()*60.0)*channel->speed)+channel->current);
        next=(float)value; channel->flag_2c=value>channel->end;
        if (channel->start==channel->end) wrapped=channel->end;
        else {
            wrapped=R(R((double)next-channel->end)+channel->start);
            while (wrapped>channel->end) wrapped=R(R(wrapped-channel->end)+channel->start);
        }
        boundary=channel->end;
    } else if (channel->direction==UINT32_MAX) {
        double value=R((double)channel->current-R(R(thug_frame_duration()*60.0)*channel->speed));
        next=(float)value; channel->flag_2c=value<channel->start;
        if (channel->start==channel->end) wrapped=channel->end;
        else {
            wrapped=R(R((double)next-channel->start)+channel->end);
            while (wrapped<channel->start) wrapped=R(R(wrapped-channel->start)+channel->end);
        }
        boundary=channel->start;
    }
    if (channel->flag_2c && channel->loop==0) wrapped=boundary;
    else if (channel->flag_2c && channel->loop==2) {
        wrapped=boundary; channel->direction=channel->direction ? 0 : UINT32_MAX;
    } else if (!channel->flag_2c || channel->loop!=1) wrapped=next;
    if (wrapped<channel->start) wrapped=channel->start;
    if (wrapped>channel->end) wrapped=channel->end;
    return wrapped;
    #undef R
}
/* 0x004816b0. Preserve raw speed while the timeline validates an offset. */
void thug_animation_offset_time(ThugAnimationChannel *channel,float delta) {
    double value=thug_platform_round_x87_single((double)delta+channel->current);
    uint32_t speed; __builtin_memcpy(&speed,&channel->speed,4); channel->speed=0;
    channel->current=(float)value;
    channel->current=(float)thug_animation_advance_time(channel);
    __builtin_memcpy(&channel->speed,&speed,4);
}
/* 0x00481830, 0x00481690 and 0x004816e0. */
ThugAnimationChannel *thug_animation_channel_initialize(ThugAnimationChannel *channel,ThugSkaterBody *body) {
    thug_animation_timeline_initialize(channel);
    channel->count=0; channel->events=NULL; channel->event_count=0; channel->body=body;
    channel->methods=&thug_animation_channel_methods;
    channel->events_enabled=1; channel->unknown_38=2; return channel;
}
void thug_animation_timeline_destroy(ThugAnimationChannel *channel) {
    channel->methods=&thug_animation_link_methods;
    channel->next->previous=channel->previous;
    channel->previous->next=channel->next;
    channel->previous=channel->next=channel;
}
ThugAnimationChannel *thug_animation_timeline_delete(ThugAnimationChannel *channel,uint32_t flags,const ThugMemory *memory) {
    thug_animation_timeline_destroy(channel);
    if ((uint8_t)flags&1) memory->release(memory->context,channel);
    return channel;
}
/* 0x00481a30. Descending signed priorities, stable for ties. */
void thug_animation_insert_controller(ThugAnimationChannel *channel,ThugAnimationController *controller,int32_t priority) {
    int32_t i=0,count=channel->count;
    while (i<count && priority<=(int32_t)channel->controllers[i]->unknown_c) ++i;
    for (int32_t j=count;j>i;--j) channel->controllers[j]=channel->controllers[j-1];
    channel->controllers[i]=controller; ++channel->count;
}
/* 0x00481a80. */
ThugAnimationController *thug_animation_find_controller(const ThugAnimationChannel *channel,uint32_t name) {
    for (int32_t i=0;i<channel->count;++i) if (channel->controllers[i]->name==name) return channel->controllers[i];
    return NULL;
}
/* 0x004818b0. Deletion can change the count; the final stale slot is retained. */
void thug_animation_remove_controller(ThugAnimationChannel *channel,ThugAnimationController *controller,const ThugMemory *memory) {
    for (int32_t i=0;i<channel->count;++i) if (channel->controllers[i]==controller) {
        if (controller) controller->methods->dispose(controller,1,memory);
        channel->controllers[i]=NULL;
        for (int32_t j=i;j<channel->count-1;++j) channel->controllers[j]=channel->controllers[j+1];
        --channel->count; return;
    }
}
/* 0x004a4a80 and 0x004a50e0. */
void thug_balance_animation_destroy(ThugAnimationController *controller,const ThugMemory *memory) {
    ThugBalanceAnimationController *balance=(ThugBalanceAnimationController *)controller;
    controller->methods=&thug_balance_animation_methods;
    if (balance->reader) { thug_release_animation_reader(balance->reader,memory); balance->reader=NULL; }
    if (balance->animation) balance->animation=NULL;
    thug_animation_controller_destroy(controller);
}
ThugAnimationController *thug_balance_animation_delete(ThugAnimationController *controller,uint32_t flags,const ThugMemory *memory) {
    thug_balance_animation_destroy(controller,memory);
    if ((uint8_t)flags&1) memory->release(memory->context,controller);
    return controller;
}
/* 0x004a4610, shared forwarding configure virtual. */
void thug_animation_configure_controller(ThugAnimationController *controller,const ThugScriptStructure *parameters) {
    thug_animation_controller_configure(controller,parameters);
}
/* 0x00481430. Equal/unordered endpoints take the reverse branch. The current
 * endpoint is a raw word copy, while the bounds travel through x87. */
void thug_animation_set_timeline(ThugAnimationChannel *channel,uint32_t name,float first,float second,uint32_t loop,float unused,float speed) {
    (void)unused;
    channel->start=quiet_bound(first<second ? first : second);
    __builtin_memcpy(&channel->current,&first,4);
    channel->end=quiet_bound(first<second ? second : first);
    channel->speed=(float)thug_platform_round_x87_single((double)speed*(double)0.01666666753590107f);
    channel->direction=first<second ? 0 : UINT32_MAX;
    channel->loop=loop; channel->flag_2c=0; channel->animation_name=name;
}
/* 0x00481710, 0x00481730 and 0x00481740. */
ThugAnimationController *thug_animation_controller_initialize(ThugAnimationController *controller,ThugAnimationChannel *channel) {
    controller->channel=channel; controller->methods=&thug_animation_controller_base_methods;
    controller->name=controller->unknown_8=controller->unknown_c=0; return controller;
}
void thug_animation_controller_destroy(ThugAnimationController *controller) { controller->methods=&thug_animation_controller_base_methods; }
void thug_animation_controller_configure(ThugAnimationController *controller,const ThugScriptStructure *parameters) {
    thug_script_get_checksum(parameters,0x40c698af,&controller->name,0);
}
/* 0x004819d0 and 0x00481760. */
ThugSkaterBody *thug_animation_channel_body(const ThugAnimationChannel *channel) { return channel->body; }
ThugSkaterBody *thug_animation_controller_body(const ThugAnimationController *controller) { return thug_animation_channel_body(controller->channel); }
/* 0x00419ab0 and 0x00419ad0. A valid sentinel node is required, as on PC. */
uint32_t thug_animation_component_namespace(const ThugAnimationComponent *component) {
    return component->state->id==UINT32_MAX ? 0 : component->state->animation_namespace;
}
uint32_t thug_animation_component_events(const ThugAnimationComponent *component) {
    return component->state->id==UINT32_MAX ? 0 : component->state->events;
}
/* 0x00419c70. A valid chain ends at the id -1 sentinel. Empty chains return
 * true, and every ordinary node contributes bit29 even after a false result. */
uint8_t thug_animation_component_all_flipped(const ThugAnimationComponent *component) {
    uint8_t flipped=1;
    for(const ThugAnimationState *state=component->state;state->id!=UINT32_MAX;state=state->next)
        flipped&=(state->unknown_54>>29)&1;
    return flipped;
}
/* 0x0047dc40. The packet retains the raw flag byte, while the stored bit is
 * boolean. Read the old bit after the network path and return that old value. */
uint8_t thug_animation_state_set_flipped(ThugAnimationState *state,uint32_t id,uint32_t flipped,
    uint32_t time,uint32_t send,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)time;
    uint8_t flag=(uint8_t)flipped;
    if((uint8_t)send&&!state->network_block) {
        ThugNetworkState *network=thug_network_state;
        ThugPlayerState *player=thug_player_find(network,id);
        if(player&&(uint8_t)thug_player_flag_1(player)) {
            ThugMessageSpec spec;thug_message_spec_initialize(&spec);
            ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
            uint8_t payload[2]={(uint8_t)id,flag};
            spec.data=payload;spec.length=2;spec.id=0x2c;
            thug_queue_send_first(client,&spec,d,m);
        }
    }
    uint32_t previous=state->unknown_54;
    state->unknown_54=(previous&0xdfffffff)|(flag?0x20000000:0);
    return (previous>>29)&1;
}
/* 0x00419c10. Like the original, a valid sentinel is required. Every node is
 * updated even after an earlier one reported its old flip bit set. */
uint8_t thug_animation_component_set_flipped(ThugAnimationComponent *component,uint32_t id,uint32_t flipped,
    uint32_t time,uint32_t send,const ThugDiagnostics *d,const ThugMemory *m) {
    uint8_t previous=0;
    for(ThugAnimationState *state=component->state;state->id!=UINT32_MAX;state=state->next)
        previous|=thug_animation_state_set_flipped(state,id,flipped,time,send,d,m);
    return previous;
}
/* 0x005114f0. Reload the state component after obtaining the current client's
 * timestamp. Client lookup is unconditional, including offline configurations. */
void thug_skater_toggle_flip(ThugSkaterFlipComponent *component,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugSkaterState *state=(void *)thug_object_find_component(component->base.owner,0x43686585);
    uint8_t value=!state->stat_modifier_selector;
    if(state->stat_modifier_selector!=value) {
        state->stat_modifier_selector=value;
        state->stat_modifier_time=thug_elapsed_time()+thug_timer_offset;
    }
    uint32_t index;__builtin_memcpy(&index,(const uint8_t *)component->base.owner+0x2bc,4);
    ThugQueueClient *client=thug_network_get_client(thug_network_state,index);
    state=(void *)thug_object_find_component(component->base.owner,0x43686585);
    uint32_t time=client->time;
    uint32_t flipped=state->stat_modifier_selector;
    const ThugSkaterBody *body=component->base.owner;
    thug_animation_component_set_flipped(component->animation,body->object_id,flipped,time,1,d,m);
}
/* 0x004a49f0. Reader allocation precedes owner/component lookup. */
ThugAnimationController *thug_balance_animation_initialize(ThugAnimationController *controller,ThugAnimationChannel *channel,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    ThugBalanceAnimationController *balance=(ThugBalanceAnimationController *)controller;
    thug_animation_controller_initialize(controller,channel);
    controller->methods=&thug_balance_animation_methods; balance->position=0;
    for (uint32_t i=0;i<5;++i) balance->values[i]=0;
    balance->reader=thug_create_animation_reader(memory);
    balance->animation=thug_animation_reader_set_mode(balance->reader,0,diagnostics);
    const ThugSkaterBody *body=thug_animation_controller_body(controller);
    balance->animation_namespace=thug_animation_component_namespace((const ThugAnimationComponent *)thug_object_find_component(body,0x7149b753));
    return controller;
}
/* 0x004a4af0. All four command branches; required setup fields are an internal
 * contract. Optional parameter groups commit only after every getter succeeds. */
uint32_t thug_balance_animation_command(ThugAnimationController *controller,uint32_t command,const ThugScriptStructure *parameters,void *script,const ThugDiagnostics *diagnostics) {
    ThugBalanceAnimationController *balance=(ThugBalanceAnimationController *)controller;
    (void)script;
    switch (command) {
        case 0xaf2fae19: {
            uint32_t name,loop; float first,second,unused,speed;
            thug_script_get_checksum(parameters,0x6c2bfb7f,&name,1);
            thug_script_get_float(parameters,0xd16b61e6,&first,1);
            thug_script_get_float(parameters,0xab81bb3d,&second,1);
            thug_script_get_integer(parameters,0xcd8d7c1b,&loop,1);
            thug_script_get_float(parameters,0x8f0d24ed,&unused,1);
            thug_script_get_float(parameters,0xf0d90109,&speed,1);
            thug_animation_set_timeline(controller->channel,name,first,second,loop,unused,speed);
            balance->animation=thug_animation_reader_select(balance->reader,balance->animation_namespace+name,diagnostics);
            return 1;
        }
        case 0x5f495ae0:
            balance->animation=thug_animation_reader_set_mode(balance->reader,0,diagnostics);
            return 2;
        case 0xd0209498: {
            float value;
            if (thug_script_get_float(parameters,0x4d747fa0,&value,0)) {
                if (value<0) value=0; else if (value>1) value=1;
                double position=thug_platform_round_x87_single((double)controller->channel->end-controller->channel->start);
                position=thug_platform_round_x87_single(position*value);
                balance->position=(float)thug_platform_round_x87_single(position+controller->channel->start);
            }
            return 1;
        }
        case 0xea6d0efd: {
            float values[5];
            const uint32_t names[5]={0xfd266a26,0x642f3b9c,0x0f43fd49,0x964aacf3,0xf90b0824};
            for (uint32_t i=0;i<5;++i) if (!thug_script_get_float(parameters,names[i],&values[i],0)) return 1;
            __builtin_memcpy(balance->values,values,sizeof(values));
            return 1;
        }
        default: return 2;
    }
}

/* 0x00481640 and 0x004813f0. Completion is ordered endpoint equality. */
void thug_animation_update_time(ThugAnimationChannel *channel) { channel->current=(float)thug_animation_advance_time(channel); }
uint8_t thug_animation_timeline_finished(const ThugAnimationChannel *channel) {
    if (channel->loop) return 0;
    return channel->current==(channel->direction ? channel->start : channel->end);
}
