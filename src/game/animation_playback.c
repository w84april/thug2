#include "animation_controllers.h"
#include "stats.h"
#include "../core/number.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include "../network/queue.h"
#include "../script/values.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
_Static_assert(sizeof(ThugStandardAnimationController)==0x28,"Standard controller allocation");
_Static_assert(offsetof(ThugAnimationControllerMethods,update)==0x14,"Controller update slot");
_Static_assert(offsetof(ThugAnimationChannelMethods,command)==0x14,"Channel command slot");
uint32_t thug_standard_animation_pool_index,thug_animation_channel_pool_index;
ThugFixedPool *thug_standard_animation_pools[2],*thug_animation_channel_pools[2];
ThugObjectLookupManager *thug_animation_objects;
static void configure(ThugAnimationController *c,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; thug_animation_configure_controller(c,p);
}
const ThugAnimationControllerMethods thug_standard_animation_methods={.dispose=thug_standard_animation_delete,.command=thug_standard_animation_command,.configure=configure,.update=thug_standard_animation_update};
/* 0x004a4500. The extra word at +14 is deliberately untouched. */
ThugAnimationController *thug_standard_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugStandardAnimationController *c=(ThugStandardAnimationController *)base;
    thug_animation_controller_initialize(base,channel);base->methods=&thug_standard_animation_methods;
    c->reader=thug_create_animation_reader(m);c->animation=thug_animation_reader_set_mode(c->reader,0,d);
    c->animation_namespace=thug_animation_component_namespace((ThugAnimationComponent *)thug_object_find_component(thug_animation_controller_body(base),0x7149b753));
    c->animation=NULL;c->cache_index=-1;return base;
}
/* 0x004a4590. Cache unpin precedes reader destruction. */
void thug_standard_animation_destroy(ThugAnimationController *base,const ThugMemory *m) {
    ThugStandardAnimationController *c=(ThugStandardAnimationController *)base;base->methods=&thug_standard_animation_methods;
    if(c->animation)thug_keyframe_animation_unpin(c->animation,c->cache_index,m);
    if(c->reader) { thug_release_animation_reader(c->reader,m);c->reader=NULL; }
    c->animation=NULL;thug_animation_controller_destroy(base);
}
/* 0x004a4f30 and 0x004a5600. Pool selection mirrors the original two slots. */
void *thug_standard_animation_allocate(uint32_t size,uint32_t unused,const ThugMemory *m) {
    (void)unused;ThugFixedPool *pool=thug_standard_animation_pools[thug_standard_animation_pool_index];
    return pool?thug_pool_allocate(pool):m->allocate(m->context,size,1);
}
void thug_standard_animation_free(ThugAnimationController *c,const ThugMemory *m) {
    ThugFixedPool *pool=thug_standard_animation_pools[thug_standard_animation_pool_index];
    if(pool&&thug_pool_contains(pool,c)) { thug_pool_release(pool,c);return; }
    pool=thug_standard_animation_pools[thug_standard_animation_pool_index^1];
    if(pool&&thug_pool_contains(pool,c))thug_pool_release(pool,c);else m->release(m->context,c);
}
/* 0x004a55e0. */
ThugAnimationController *thug_standard_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_standard_animation_destroy(c,m);if((uint8_t)flags&1)thug_standard_animation_free(c,m);return c;
}
/* 0x004a4670. Required setup fields and live assets are caller contracts. */
uint32_t thug_standard_animation_command(ThugAnimationController *base,uint32_t command,const ThugScriptStructure *p,void *script,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)script;ThugStandardAnimationController *c=(ThugStandardAnimationController *)base;
    switch(command) {
        case 0x92267217:thug_keyframe_animation_build_cache(c->animation,thug_animation_cache_format(thug_animation_cache_instance()),m);return 1;
        case 0x5f495ae0:c->animation=thug_animation_reader_set_mode(c->reader,0,d);return 2;
        case 0xaf2fae19: {
            uint32_t name,loop;float first,last,unused,speed;
            thug_script_get_checksum(p,0x6c2bfb7f,&name,1);
            thug_script_get_float(p,0xd16b61e6,&first,1);thug_script_get_float(p,0xab81bb3d,&last,1);
            thug_script_get_integer(p,0xcd8d7c1b,&loop,1);thug_script_get_float(p,0x8f0d24ed,&unused,1);thug_script_get_float(p,0xf0d90109,&speed,1);
            thug_animation_set_timeline(base->channel,name,first,last,loop,unused,speed);
            c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d);
            c->cache_index=(int32_t)thug_keyframe_animation_pin(c->animation,m);return 1;
        }
        case 0xc68365eb: {
            uint32_t name;thug_script_get_checksum(p,0x98549ba4,&name,1);
            if(c->animation)thug_keyframe_animation_unpin(c->animation,c->cache_index,m);
            if(c->reader) { thug_release_animation_reader(c->reader,m);c->reader=NULL; }
            c->reader=thug_create_animation_reader(m);thug_animation_reader_set_mode(c->reader,0,d);
            c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d);
            c->cache_index=(int32_t)thug_keyframe_animation_pin(c->animation,m);return 1;
        }
        default:return 2;
    }
}
/* 0x00481fb0. Known types require successful allocation, as on PC. */
ThugAnimationController *thug_animation_create_controller(ThugAnimationChannel *channel,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    uint32_t type,priority=500;thug_script_get_checksum(p,0x7321a8d6,&type,1);
    ThugAnimationController *c=NULL;
    switch(type) {
        case 0x6d941203:c=thug_allocate_zeroed(0x38,m);if(c)thug_balance_animation_initialize(c,channel,d,m);break;
        case 0x659bf355:c=thug_allocate_zeroed(0x24,m);if(c)thug_timed_animation_initialize(c,channel,d,m);break;
        case 0x26205db6:c=thug_allocate_zeroed(0x1a4,m);if(c)thug_bone_animation_initialize(c,channel,NULL);break;
        case 0x7e1940a1:c=thug_allocate_zeroed(0x24,m);if(c)thug_weighted_animation_initialize(c,channel,NULL,d,m);break;
        case 0xdf5c091a:c=thug_allocate_zeroed(0x18,m);if(c)thug_flag_animation_initialize(c,channel);priority=100;break;
        case 0xcfc5b380:c=thug_allocate_zeroed(0x854,m);if(c)thug_pose_animation_initialize(c,channel);break;
        case 0xcb4533ff:c=thug_standard_animation_allocate(0x28,0,m);if(c)thug_standard_animation_initialize(c,channel,d,m);break;
        default:return NULL;
    }
    thug_script_get_integer(p,0x9d5923d8,&priority,0);c->methods->configure(c,p,d,m);
    c->unknown_c=priority;thug_animation_insert_controller(channel,c,(int32_t)priority);return c;
}
/* 0x00481870, 0x00481f20. Destructors may change the live controller count. */
void thug_animation_clear_controllers(ThugAnimationChannel *c,const ThugMemory *m) {
    for(int32_t i=0;i<c->count;i++) { ThugAnimationController *controller=c->controllers[i];if(controller)controller->methods->dispose(controller,1,m);c->controllers[i]=NULL; }
    c->count=0;
}
void thug_animation_channel_destroy(ThugAnimationChannel *c,const ThugMemory *m) {
    c->methods=&thug_animation_channel_methods;thug_animation_clear_controllers(c,m);thug_animation_clear_events(c,m);thug_animation_timeline_destroy(c);
}
/* 0x00482360 and 0x00482340. */
void thug_animation_channel_free(ThugAnimationChannel *c,const ThugMemory *m) {
    ThugFixedPool *pool=thug_animation_channel_pools[thug_animation_channel_pool_index];
    if(pool&&thug_pool_contains(pool,c)) { thug_pool_release(pool,c);return; }
    pool=thug_animation_channel_pools[thug_animation_channel_pool_index^1];
    if(pool&&thug_pool_contains(pool,c))thug_pool_release(pool,c);else m->release(m->context,c);
}
ThugAnimationChannel *thug_animation_channel_delete(ThugAnimationChannel *c,uint32_t flags,const ThugMemory *m) {
    thug_animation_channel_destroy(c,m);if((uint8_t)flags&1)thug_animation_channel_free(c,m);return c;
}
/* 0x00482200. Special commands run before forwarding through the live list. */
uint32_t thug_animation_channel_command(ThugAnimationChannel *c,uint32_t command,const ThugScriptStructure *p,void *script,const ThugDiagnostics *d,const ThugMemory *m) {
    if(command==0x83654874) { thug_animation_create_controller(c,p,d,m);return 1; }
    if(command==0x986d274e) {
        uint32_t name;thug_script_get_checksum(p,0x40c698af,&name,1);
        ThugAnimationController *controller=thug_animation_find_controller(c,name);if(controller)thug_animation_remove_controller(c,controller,m);
    } else if(command==0xc68365eb) {
        uint32_t name;float length;thug_script_get_checksum(p,0x98549ba4,&name,1);thug_script_get_float(p,0x79a07f3f,&length,1);
        uint8_t keep=thug_script_has_flag(p,0xd3d40a85);c->animation_name=name;
        thug_animation_clear_events(c,m);thug_animation_load_events(c,c->animation_name,m);
        float offset=0;
        if(keep) { double current=c->current;c->current=0;offset=(float)R(R(current/c->end)*length); }
        __builtin_memcpy(&c->end,&length,4);c->start=0;thug_animation_offset_time(c,offset);
    }
    for(int32_t i=0;i<c->count;i++) { ThugAnimationController *controller=c->controllers[i];uint32_t result=controller->methods->command(controller,command,p,script,d,m);if(result!=2)return result; }
    return 2;
}
/* 0x00481ac0. Fade comparisons retain the unspilled PC24 exponent. */
void thug_animation_channel_update(ThugAnimationChannel *c,const ThugDiagnostics *d,const ThugMemory *m) {
    c->flag_2c=0;
    if(c->unknown_38==1) {
        double value=R((double)c->fade_value-R(R(thug_frame_duration()*60.0)*c->fade_rate));c->fade_value=(float)value;
        if(value<=0||R(value*c->fade_direction)<0)c->unknown_38=0;
    }
    if(c->unknown_38==1||c->unknown_38==2)
        for(int32_t i=0;i<c->count;i++) { ThugAnimationController *controller=c->controllers[i];controller->methods->update(controller,d,m); }
}
/* 0x004a4620. Refresh the reader only on a strict backward time step. */
void thug_standard_animation_update(ThugAnimationController *base,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugStandardAnimationController *c=(ThugStandardAnimationController *)base;float before=base->channel->current;
    base->channel->current=(float)thug_animation_advance_time(base->channel);
    thug_animation_update_events(base->channel,before,base->channel->current,d,m);
    if(base->channel->current<before)c->animation=thug_animation_reader_set_mode(c->reader,0,d);
}
/* 0x004a4ef0. */
void thug_timed_animation_update(ThugAnimationController *base,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)m;ThugTimedAnimationController *c=(ThugTimedAnimationController *)base;float before=c->timeline->current;
    c->timeline->current=(float)thug_animation_advance_time(c->timeline);
    if(c->timeline->current<before)c->animation=thug_animation_reader_set_mode(c->reader,0,d);
}
/* 0x004a5180. Two nested periodic phases, with the original integer reduction.
 * The platform adapter replaces FSIN; physical x87 transcendental accuracy is
 * not claimed. All surrounding PC24 arithmetic and float spills are retained. */
static double phase(float frequency) {
    int32_t time=(int32_t)(thug_elapsed_time()+thug_timer_offset);
    double value=thug_platform_multiply_x87_single(time,frequency);
    double integer=(int32_t)thug_truncate_double_low_word(value);
    value=R(value-R(R(integer*0.0625)*16.0));return thug_platform_sin(R(value*(double)6.2831854820251465f));
}
double thug_balance_animation_position(ThugAnimationController *base) {
    ThugBalanceAnimationController *c=(ThugBalanceAnimationController *)base;float values[5];__builtin_memcpy(values,c->values,20);
    ThugAnimationChannel *channel=base->channel;float position=c->position;
    double distance=__builtin_fabs(R((double)position-R(R((double)channel->start+channel->end)*.5)));
    double scale=R(R(R(R((double)values[4]-1)/R(R((double)channel->end-channel->start)*.5))*distance)+1);
    float first=(float)R(scale*values[0]),second=(float)R(scale*values[1]);
    if(R(R((double)position-first)-second)<channel->start)position=(float)R(R((double)second+first)+channel->start);
    if(R(R((double)position+second)+first)>channel->end)position=(float)R(R((double)channel->end-first)-second);
    float amplitude=(float)R(R(phase(values[2])*second)+first);
    double result=R(R(phase(values[3])*amplitude)+position);channel=base->channel;
    if(result<channel->start)result=channel->start;if(result>channel->end)result=channel->end;return result;
}
/* 0x004a52e0. */
void thug_balance_animation_update(ThugAnimationController *base,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)m;ThugBalanceAnimationController *c=(ThugBalanceAnimationController *)base;float before=base->channel->current;
    base->channel->current=(float)thug_balance_animation_position(base);
    if(base->channel->current<before)c->animation=thug_animation_reader_set_mode(c->reader,0,d);
}
/* 0x00488100. Disabled records still track their target position. */
void thug_bone_animation_update(ThugAnimationController *base,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d;(void)m;ThugBoneAnimationController *c=(ThugBoneAnimationController *)base;
    for(uint32_t i=0;i<4;i++) {
        ThugBoneAnimationRecord *r=&c->records[i];if(r->use_vector)continue;
        ThugSkaterBody *body=thug_object_manager_find(thug_animation_objects,r->target);if(!body)continue;
        double x=R((double)r->offset[0]+body->position[0]),y=R((double)r->offset[1]+body->position[1]);
        float z=(float)R((double)body->position[2]+r->offset[2]),w=(float)R((double)r->offset[3]+body->position[3]);
        r->vector[2]=z;r->vector[3]=w;r->vector[0]=(float)x;r->vector[1]=(float)y;
    }
}
/* 0x005480a0. Shared empty update method. */
void thug_animation_controller_idle(ThugAnimationController *c,const ThugDiagnostics *d,const ThugMemory *m) { (void)c;(void)d;(void)m; }

uint8_t thug_animation_last_balance;
_Static_assert(offsetof(ThugAnimationState,first_channel)==0x20,"Animation channel head");
_Static_assert(offsetof(ThugAnimationState,body)==0x68,"Animation owner");
/* 0x0047e280. Network clamping changes the value subsequently sent to the
 * channel. The first channel is re-read after allocating its parameters. */
void thug_animation_set_balance(ThugAnimationState *state,float value,uint32_t send,
    const ThugDiagnostics *d,const ThugMemory *m) {
    if((uint8_t)send&&!state->network_block) {
        ThugNetworkState *network=thug_network_state;
        ThugPlayerState *player=thug_player_find(network,state->body->object_id);
        if(player&&thug_player_flag_1(player)) {
            ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
            if(value<0)value=0;else if(value>1)value=1;
            uint8_t packed=(uint8_t)thug_truncate_double_low_word(R((double)value*255));
            uint8_t data[2]={(uint8_t)state->body->object_id,packed};
            if(thug_animation_last_balance!=packed) {
                ThugMessageSpec spec;thug_message_spec_initialize(&spec);
                spec.id=0x2b;spec.length=2;spec.data=data;spec.replace=1;
                thug_queue_send_first(client,&spec,d,m);thug_animation_last_balance=data[1];
            }
        }
    }
    if(state->first_channel->id!=UINT32_MAX) {
        ThugScriptStructure *p=thug_script_structure_allocate(8,m);
        if(p)thug_script_structure_initialize(p);
        uint32_t bits;__builtin_memcpy(&bits,&value,4);thug_script_set_float_bits(p,0x4d747fa0,bits,m);
        ThugAnimationChannel *channel=state->first_channel;
        channel->methods->command(channel,0xd0209498,p,NULL,d,m);
        if(p) { thug_script_structure_destroy(p,m);thug_script_structure_free(p,m); }
    }
}
/* 0x00419bd0. The original uses an allocated sentinel, not a NULL state. */
void thug_animation_component_set_balance(ThugAnimationComponent *c,float value,uint32_t send,
    const ThugDiagnostics *d,const ThugMemory *m) {
    if(c->state->id!=UINT32_MAX)thug_animation_set_balance(c->state,value,send,d,m);
}
