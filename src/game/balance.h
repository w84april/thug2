#ifndef THUG_GAME_BALANCE_H
#define THUG_GAME_BALANCE_H
#include "stats.h"
#include "score.h"
#include "../core/memory.h"
typedef struct {
    ThugObjectComponent base;
    uint32_t unknown_14, mode, unknown_1c;
    ThugScriptStructure *parameters;
} ThugBalanceParameters;
typedef struct {
    uint32_t type, unknown_4;
    int32_t threshold;
    uint8_t completed, unknown_d[3];
    uint32_t disabled;
    const char *name, *extra_text;
    uint32_t unknown_1c, unknown_20;
} ThugTimedTrick;
typedef struct {
    uint8_t unknown_0[0x1c];
    ThugTimedTrick records[70];
    uint8_t enabled, unknown_9f5[0x63];
    uint32_t spin_bits;
    uint8_t unknown_a5c[0x34];
    uint32_t available;
} ThugTimedTricks;
typedef struct ThugBalanceScoreComponent { ThugObjectComponent base; uint32_t unknown_14; ThugScore *score; } ThugBalanceScoreComponent;
typedef struct {
    uint32_t unknown_0;
    ThugSkaterBody *body;
    ThugBalanceParameters *parameters;
    ThugBalanceScoreComponent *score_component;
    ThugSkaterInput *input;
    uint8_t unknown_14[0x10];
    float elapsed,total_elapsed,unknown_2c,position,velocity,recovery;
    uint8_t released,unknown_3d[3];
    uint32_t start_time,left_button,right_button,points,unknown_50;
    uint8_t animate,hide_meter,flip_with_state,reverse;
} ThugBalance;
void thug_balance_update(ThugBalance *,const ThugDiagnostics *,const ThugMemory *);
double thug_balance_parameter(const ThugBalanceParameters *, uint32_t name);
uint8_t thug_timed_tricks_enabled(const ThugTimedTricks *);
void thug_timed_tricks_set_spin(ThugTimedTricks *,uint32_t spin_bits);
/* Original internal contracts: valid record indices and loaded terminating QB.
 * Notifications run before the completion write, and may change later records. */
void thug_timed_trick_complete(ThugTimedTricks *, uint32_t index, const ThugDiagnostics *, const ThugMemory *);
void thug_timed_tricks_check_balance(ThugTimedTricks *, uint32_t mode, float elapsed, uint32_t unused,
    const ThugDiagnostics *, const ThugMemory *);
#endif
