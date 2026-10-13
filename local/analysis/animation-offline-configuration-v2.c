/* Uncredited offline subset of 00480410. Required namespace and ready clip
 * are caller contracts; network-emitting initial-loop changes are unsupported.
 * This is an integration adapter, not a complete original function claim. */
#include "../../src/game/animation_controllers.h"
#include "../../src/game/assets.h"
#include "../../src/game/ui.h"
#include "../../src/script/params.h"
extern uint32_t thug_model_parameter_float_draft(const ThugScriptStructure *,uint32_t,void *,uint32_t);
extern void thug_gap_list_clear_draft(void *,const ThugMemory *);
extern void thug_animation_state_enable_channel_events_v1(void *,uint32_t);
extern void thug_animation_state_start_clip_offline_v1(ThugAnimationState *,uint32_t,uint32_t,float,float,uint32_t,float,float,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
static void store_word(void *p,unsigned offset,uint32_t value){__builtin_memcpy((char *)p+offset,&value,4);}
void thug_animation_state_configure_offline_v2(ThugAnimationState *state,const ThugScriptStructure *parameters,const ThugDiagnostics *d,const ThugMemory *m){
    uint8_t *bytes=(void *)state;
    thug_script_get_checksum_legacy(parameters,0x5cfccf35,&state->network_block,0);
    thug_model_parameter_float_draft(parameters,0x4d786f62,bytes+0x30,0);
    uint32_t integer=0,namespace=0;
    thug_script_get_integer(parameters,0x3d836c96,&integer,0);store_word(state,0x2c,integer);
    thug_script_get_checksum_legacy(parameters,0x5b8c6dc2,&state->events,0);
    if(!thug_script_get_checksum(parameters,0x52a864b0,&namespace,0)&&
       !thug_script_get_checksum(parameters,0x09794932,&namespace,1))__builtin_trap();
    state->animation_namespace=namespace;
    thug_animation_state_start_clip_offline_v1(state,0x1ca1ff20,0,0,1000,0,.3f,1,0,d,m);
    thug_gap_list_clear_draft(bytes+0x14,m);bytes[0x44]=0;store_word(state,0x48,0);
    if(bytes[0x60]){bytes[0x60]=0;uint32_t owner_script;__builtin_memcpy(&owner_script,(char *)state->body+0x10,4);ThugScriptInstance *script=(void *)(uintptr_t)owner_script;if(script)thug_script_clear_wait(script);}
    store_word(state,0x64,0);store_word(state,0x5c,0);bytes[0x4e]=0;
    uint32_t name=0x1ca1ff20;
    uint8_t initial=thug_script_get_checksum_legacy(parameters,0xeae64b47,&name,0);
    const float *asset=thug_animation_find(state->animation_namespace+name,0,d);
    if(!asset)__builtin_trap();
    thug_animation_state_start_clip_offline_v1(state,name,0,0,*asset,0,.3f,1,0,d,m);
    if(initial){
        if(!state->network_block)__builtin_trap();
        if(state->first_channel->id!=UINT32_MAX)state->first_channel->loop=1;
    }
    if(thug_script_has_flag(parameters,0xcf466aa2))bytes[0x4c]=1;
    thug_animation_state_enable_channel_events_v1(state,thug_script_has_flag(parameters,0xe1b3f630));
}
