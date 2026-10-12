/* Channel creation for original Animation startup. No clip playback claim. */
#include "../../src/game/animation_controllers.h"
#include "../../src/platform/math.h"
extern uint32_t thug_animation_channel_pool_index;
extern ThugFixedPool *thug_animation_channel_pools[2];
int32_t thug_animation_channel_limit_v1;
/* 00481ee0: initialized allocator; the second argument is unused. */
void *thug_animation_channel_allocate_v1(uint32_t size,uint32_t unused,const ThugMemory *m){
    (void)unused;ThugFixedPool *pool=thug_animation_channel_pools[thug_animation_channel_pool_index];
    return pool?thug_pool_allocate(pool):m->allocate(m->context,size,1);
}
/* 00481990: callers consume the low boolean byte. */
uint8_t thug_animation_channel_is_fading_v1(const ThugAnimationChannel *c){return c->unknown_38==1;}
/* 00481b40: zero duration clears the state before the transition check.
 * Existing header names +58 fade_rate, +5c fade_value and +60 fade_direction.
 * This original routine stores duration at +5c; +60 holds its weight. */
uint8_t thug_animation_channel_begin_fade_v1(ThugAnimationChannel *c,float duration){
    if(duration==0)c->unknown_38=0;
    if(c->unknown_38==2){c->unknown_38=1;c->fade_value=duration;return 1;}
    return 0;
}
static ThugAnimationChannel *live(ThugAnimationChannel *c){return c->id==UINT32_MAX?0:c;}
/* 0047de20: original list order and live sentinel links. */
void thug_animation_state_begin_channel_v1(ThugAnimationState *state,float duration,const ThugMemory *m){
    int32_t visited=0;ThugAnimationChannel *c=live(state->first_channel);
    while(c){ThugAnimationChannel *next=live(c->previous);++visited;
        if(visited>=thug_animation_channel_limit_v1){
            c->next->previous=c->previous;c->previous->next=c->next;c->previous=c->next=c;
            c->methods->dispose(c,1,m);
        }
        c=next;
    }
    int32_t count=0;for(c=live(state->first_channel);c;c=live(c->previous))++count;
    ThugAnimationChannel *first=live(state->first_channel);
    if(count && first && thug_animation_channel_begin_fade_v1(first,duration)){
        float sum=0;for(c=live(first->previous);c;c=live(c->previous))if(thug_animation_channel_is_fading_v1(c)){
            double product=thug_platform_round_x87_single((double)c->fade_direction*c->fade_value);
            sum=(float)thug_platform_round_x87_single(product+sum);
        }
        first->fade_direction=(float)thug_platform_round_x87_single(thug_platform_round_x87_single(1.0-sum)/first->fade_value);
    }
    ThugAnimationChannel *created=thug_animation_channel_allocate_v1(0x74,0,m);
    if(created)created=thug_animation_channel_initialize(created,state->body);
    /* Original unchecked allocation failure cannot satisfy the live graph. */
    created->next=(ThugAnimationChannel *)((char *)state+0x14);
    created->previous=state->first_channel;state->first_channel->next=created;state->first_channel=created;
}
