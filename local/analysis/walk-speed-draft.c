/* Candidate animation-speed dependencies of the shared walking frame. */
#include "../../src/game/animation.h"
#include "../../src/game/stats.h"
#include "../../src/network/queue.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
extern void thug_animation_channel_times_draft(void *,float *,float *,float *);
/* 0047e850,484 contiguous bytes including two skipped alignment instructions.
 * Intrusive-list sentinels and finite, nonzero relative timeline spans are contracts. */
void thug_animation_state_speed_draft(ThugAnimationState *state,float speed,uint32_t send,uint32_t all,uint32_t relative,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 ThugAnimationChannel *channel=state->first_channel;
 if(channel->id==UINT32_MAX)return;
 if(!(uint8_t)all&&__builtin_fabs(R(R((double)channel->speed*60.0)-speed))<.05000000074505806f)return;
 if((uint8_t)send&&!state->network_block){
  ThugNetworkState *network=thug_network_state;ThugPlayerState *player=thug_player_find(network,state->body->object_id);
  if(player&&thug_player_flag_1(player)){
   ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
   if(client){
    /* Three trailing bytes are unspecified in the original stack payload too. */
    uint8_t payload[8];__builtin_memcpy(payload,&speed,4);payload[4]=(uint8_t)state->body->object_id;
    ThugMessageSpec spec;thug_message_spec_initialize(&spec);spec.id=0x41;spec.length=8;spec.data=payload;
    thug_queue_send_first(client,&spec,diagnostics,memory);
   }
  }
 }
 if((uint8_t)all){
  if((uint8_t)relative){
   float first,current,last;thug_animation_channel_times_draft(state->first_channel,&first,&current,&last);
   float factor=(float)R((double)speed/R((double)last-first));channel=state->first_channel;
   while(channel->id!=UINT32_MAX){
    thug_animation_channel_times_draft(channel,&first,&current,&last);
    channel->speed=(float)R(R(R((double)last-first)*factor)*.01666666753590107f);channel=channel->previous;
   }
  }else{
   float value=(float)R((double)speed*.01666666753590107f);channel=state->first_channel;
   while(channel->id!=UINT32_MAX){channel->speed=value;channel=channel->previous;}
  }
 }else state->first_channel->speed=(float)R((double)speed*.01666666753590107f);
}
/* 00419b90,21 bytes. Forward a live component state to its speed helper. */
void thug_animation_component_speed_draft(ThugAnimationComponent *component,float speed,uint32_t send,uint32_t all,uint32_t relative,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 if(component->state->id!=UINT32_MAX)thug_animation_state_speed_draft(component->state,speed,send,all,relative,diagnostics,memory);
}
