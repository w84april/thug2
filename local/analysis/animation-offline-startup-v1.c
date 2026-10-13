/* Uncredited partial integration of47f260 for offline Animation startup.
 * Network emission is explicitly unsupported. The constructor creates the
 * one known channel type, so its seventh virtual slot can be devirtualized.
 * Existing six-slot headers/tables and all earlier proofs stay unchanged. */
#include "../../src/game/animation_controllers.h"
#include "../../src/game/ui.h"
#include "../../src/script/operators.h"
extern void thug_gap_list_clear_draft(void *,const ThugMemory *);
extern void thug_animation_state_begin_channel_v1(ThugAnimationState *,float,const ThugMemory *);
extern void thug_animation_channel_start_clip_v1(ThugAnimationChannel *,uint32_t,float,float,uint32_t,float,float,uint32_t,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
extern void thug_animation_state_prepare_clip_v1(ThugAnimationState *,uint32_t,const ThugMemory *);
void thug_animation_state_start_clip_offline_v1(ThugAnimationState *state,uint32_t name,uint32_t send,float first,float last,uint32_t loop,float fade,float speed,const ThugScriptStructure *options,const ThugDiagnostics *d,const ThugMemory *m){
    if((uint8_t)send&&state->network_block==0)__builtin_trap();
    if(!name)name=0x1ca1ff20;
    if(fade==0||!((uint8_t *)state)[0x4c])thug_gap_list_clear_draft((char *)state+0x14,m);
    thug_animation_state_begin_channel_v1(state,fade,m);
    ThugAnimationChannel *channel=state->first_channel;
    if(channel->methods!=&thug_animation_channel_methods)__builtin_trap();
    thug_animation_channel_start_clip_v1(channel,name,first,last,loop,fade,speed,(state->unknown_54>>29)&0xffffff01,options,d,m);
    ThugScriptStructure *parameters=((ThugUiObjectBase *)state->body)->parameters;
    if(parameters)thug_script_remove_name(parameters,0x5db4115f,m);
    thug_animation_state_prepare_clip_v1(state,name,m);
}
