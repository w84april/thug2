#include "balance.h"
#include "profile.h"
#include "../script/values.h"
#include "../script/schedule.h"
#include "../script/delivery.h"
#include "../script/lifetime.h"
#include "../core/timing.h"
#include "../core/random.h"
#include "../core/number.h"
#include "../platform/math.h"
#include "animation.h"
#include <stddef.h>
_Static_assert(offsetof(ThugBalanceParameters, parameters) == 0x20, "Balance parameters");
_Static_assert(sizeof(ThugTimedTrick) == 0x24, "Timed trick record");
_Static_assert(offsetof(ThugTimedTricks, enabled) == 0x9f4, "Timed trick enable");
_Static_assert(offsetof(ThugTimedTricks, available) == 0xa90, "Timed trick availability");
_Static_assert(offsetof(ThugTimedTricks, spin_bits) == 0xa58, "Timed trick spin");
_Static_assert(offsetof(ThugGameContext, identifier_378) == 0x378, "Game exclusion identifier");
/* 0x004f90a0. Explicit parameters take precedence even for an unknown mode. */
double thug_balance_parameter(const ThugBalanceParameters *balance, uint32_t name) {
    if (balance->parameters)
        return thug_skater_structure_stat_parameter(balance->base.owner,name,balance->parameters);
    uint32_t set;
    switch (balance->mode) {
        case 0x8d10119d: case 0x255ed86f: set = 0x6b7fdadd; break;
        case 0x0ac90769: case 0xef24413b: set = 0xb8cc8633; break;
        case 0x3506ce64: set = 0xfc87cc01; break;
        case 0xa549b57b: set = 0xbe615d0a; break;
        default: return 0;
    }
    const ThugSkaterBody *body = balance->base.owner;
    return thug_skater_structure_stat_parameter(body,name,thug_script_get_global_structure(set,0));
}
/* 0x0051c950. PUSH ECX seeds the required checksum's output slot. The game
 * exclusion receiver is captured before reading the career setting. */
uint8_t thug_timed_tricks_enabled(const ThugTimedTricks *tricks) {
    if (!tricks->available) return 0;
    const ThugGameContext *game = thug_game_context;
    if (!thug_settings_flag(thug_game_settings,0x1ded1ea4) || !tricks->enabled
        || game->identifier_378 == 0xe92ecafe) return 0;
    ThugProfile *profile = thug_game_profile_at(thug_game_context,0);
    uint32_t mode = (uint32_t)(uintptr_t)tricks;
    thug_script_get_checksum_legacy(&profile->parameters,0xa1dc81f9,&mode,1);
    return mode == 0x0a7be964;
}
/* 0x0051cac0. No float arithmetic: retain the argument's raw bits. */
void thug_timed_tricks_set_spin(ThugTimedTricks *tricks,uint32_t spin_bits) {
    if(thug_timed_tricks_enabled(tricks))tricks->spin_bits=spin_bits;
}
/* 0x0051ce80. Copy strings into owned parameters, run the original synchronous
 * notification, then mark the record and release those parameters. */
void thug_timed_trick_complete(ThugTimedTricks *tricks, uint32_t index,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!thug_timed_tricks_enabled(tricks)) return;
    ThugScriptStructure *parameters = thug_script_structure_allocate(8,memory);
    if (parameters) thug_script_structure_initialize(parameters);
    ThugTimedTrick *record = &tricks->records[index];
    thug_script_set_string(parameters,0x61414d56,record->name,memory);
    thug_script_set_integer(parameters,0xe288a7cb,(uint32_t)record->threshold,memory);
    if (record->extra_text) thug_script_set_string(parameters,0xc257d69a,record->extra_text,memory);
    thug_script_set_integer(parameters,0x7f8c98fe,index,memory);
    thug_script_run_sync(0x55e516c8,parameters,NULL,0,diagnostics,memory);
    record->completed = 1;
    if (parameters) {
        thug_script_structure_destroy(parameters,memory);
        thug_script_structure_free(parameters,memory);
    }
}
/* 0x0051d6a0. Re-check the enable predicate for every completion. The parent
 * still sends its aggregate notification if a nested completion was gated off. */
void thug_timed_tricks_check_balance(ThugTimedTricks *tricks, uint32_t mode, float elapsed, uint32_t unused,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)unused;
    if (!thug_timed_tricks_enabled(tricks)) return;
    uint32_t type;
    switch (mode) {
        case 0x8d10119d: case 0x255ed86f: type = 0xc1336019; break;
        case 0x0ac90769: case 0xef24413b: type = 0xd9ffc141; break;
        case 0xa549b57b: type = 0xb67cff14; break;
        default: return;
    }
    uint8_t changed = 0;
    for (uint32_t i=0;i<70;++i) {
        const ThugTimedTrick *record = &tricks->records[i];
        if (!record->disabled && !record->completed && record->type == type
            && (double)record->threshold <= (double)elapsed) {
            thug_timed_trick_complete(tricks,i,diagnostics,memory); changed = 1;
        }
    }
    if (changed) thug_script_run_sync(0x41b03551,NULL,NULL,0,diagnostics,memory);
}

_Static_assert(offsetof(ThugBalance,elapsed)==0x24,"Balance timers");
_Static_assert(offsetof(ThugBalance,animate)==0x54,"Balance display flags");
#define R thug_platform_round_x87_single
/* 0x00579cc0. Required components, named buttons and valid meter curve indices
 * are internal contracts. Notifications may change fields read later here. */
void thug_balance_update(ThugBalance *b,const ThugDiagnostics *d,const ThugMemory *m) {
    float dt=(float)thug_frame_duration();
    if(!b->left_button||!b->right_button)return;
    ThugNetworkState *network=thug_network_state;
    if(thug_network_first_connection(network))thug_player_find(network,b->body->object_id);
    if(b->recovery>(double).009999999776482582f) {
        float decay=(float)thug_balance_parameter(b->parameters,0x1231ae3c);
        double denominator=thug_balance_parameter(b->parameters,0xa4362662);
        double next=R((double)b->recovery-R(R(R((double)decay/denominator)*dt)*60));
        b->recovery=(float)next;if(next<0)b->recovery=0;
    }
    thug_score_add_balance(b->score_component->score,b->points,d,m);
    b->elapsed=(float)R((double)dt+b->elapsed);b->total_elapsed=(float)R((double)dt+b->total_elapsed);
    ThugTimedTricks *tricks=(void *)thug_object_find_component(b->body,0x4ff8dac6);
    thug_timed_tricks_check_balance(tricks,b->parameters->mode,b->elapsed,0,d,m);
    float growth=(float)thug_balance_parameter(b->parameters,0x06851748);
    float rate=(float)thug_balance_parameter(b->parameters,0xa9fef5ab);
    double scale=thug_balance_parameter(b->parameters,0xb6a634f3);
    scale=R(scale+R((double)rate*b->total_elapsed));
    double drift=R(R(R(R(R((double)growth*scale)*dt)*60)+1)*b->position);
    b->position=(float)R(drift+R(R(R(scale*b->velocity)*dt)*60));
    uint8_t left=thug_input_find_button((ThugSkaterInput *)((uint8_t *)b->input+0x20),b->left_button)->pressed;
    uint8_t right=thug_input_find_button((ThugSkaterInput *)((uint8_t *)b->input+0x20),b->right_button)->pressed;
    if(!left&&!right)b->released=1;
    uint32_t ramp=thug_script_get_global_integer(0x8cc8f176,1);
    uint32_t start=b->start_time,elapsed=thug_elapsed_time()+thug_timer_offset-start;
    if(!b->released&&elapsed>thug_script_get_global_integer(0x07da1621,1))b->released=1;
    double next;
    if(left&&b->released) {
        float factor=1;if(b->position<0&&elapsed<ramp)factor=(float)(elapsed/ramp);
        next=thug_balance_parameter(b->parameters,0x61ad5596);
        next=R((double)b->velocity-R(R(R(next*factor)*dt)*60));
    } else if(right&&b->released) {
        float factor=1;if(b->position>0&&elapsed<ramp)factor=(float)(elapsed/ramp);
        next=thug_balance_parameter(b->parameters,0x61ad5596);
        next=R(R(R(R(next*factor)*dt)*60)+b->velocity);
    } else {
        float speed=__builtin_fabsf(b->velocity);
        if(thug_balance_parameter(b->parameters,0xef27e8ff)>speed) {
            uint32_t limit=thug_truncate_double_low_word(thug_balance_parameter(b->parameters,0x32eb3308))|1;
            float random=(float)thug_random_range(limit);
            next=R(thug_sign_nonnegative(b->velocity)*random);
        } else {
            float random=(float)thug_random_range(50);
            next=R(R(R(thug_sign_nonnegative(b->velocity)*random)*(double).009999999776482582f)+b->velocity);
        }
    }
    b->velocity=(float)next;
    ThugReferencedObject *owner=(ThugReferencedObject *)b->body;
    if(!owner->unknown_8_to_10[2]) {
        ThugScriptInstance *script=thug_script_allocate(0xf4,m);
        if(script)thug_script_initialize(script);
        ((ThugReferencedObject *)b->body)->unknown_8_to_10[2]=(uint32_t)(uintptr_t)script;
    }
    float magnitude=__builtin_fabsf(b->position);
    if(thug_balance_parameter(b->parameters,0xf81ab0e9)<magnitude) {
        thug_object_emit_event((ThugReferencedObject *)b->body,b->position>0?0xd77b6ff9:0x47d44b84,NULL,d,m);
        b->position=0;b->parameters->mode=0;
    }
    if(b->animate) {
        uint8_t reverse=b->reverse;
        if(b->flip_with_state) {
            ThugSkaterPhysics *physics=(void *)thug_object_find_component(b->body,0x5bd63b29);
            if(physics->state->stat_modifier_selector)reverse=!reverse;
        }
        ThugAnimationComponent *animation=(void *)thug_object_find_component(b->body,0x7149b753);
        if(animation) {
            double value=reverse?R(4096-(double)b->position):R((double)b->position+4096);
            thug_animation_component_set_balance(animation,(float)R(value*.0001220703125),1,d,m);
        }
    }
    float value=(float)R((double)b->position*-.000244140625);
    if(!b->hide_meter&&b->parameters->mode&&b->score_component->score) {
        uint32_t left=b->left_button,right=b->right_button;
        if((left==0xbc6b118f||left==0xe3006fc4)&&(right==0xbc6b118f||right==0xe3006fc4))
            thug_score_display_balance_manual(b->score_component->score,1,value,d,m);
        else thug_score_display_balance_normal(b->score_component->score,1,value,d,m);
    }
}
