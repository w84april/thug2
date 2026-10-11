#ifndef THUG_GAME_GRIND_H
#define THUG_GAME_GRIND_H
#include "balance.h"
#include "animation.h"
#include "../script/lifetime.h"
typedef struct { ThugBalanceParameters parameters;ThugBalance balances[4]; } ThugBalanceContext;
typedef struct ThugPendingFlip { ThugSkaterFlipComponent base;uint8_t *completion;ThugSkaterPhysics *physics; } ThugPendingFlip;
typedef struct ThugTrickNode ThugTrickNode;
typedef struct ThugTrickLists ThugTrickLists;
typedef struct { ThugTrickNode *(*dispose)(ThugTrickNode *,uint32_t,const ThugMemory *); } ThugTrickNodeMethods;
extern const ThugTrickNodeMethods thug_trick_primary_methods,thug_trick_secondary_methods;
void thug_balance_stop(ThugBalance *,const ThugDiagnostics *,const ThugMemory *);
void thug_balance_context_stop(ThugBalanceContext *,const ThugDiagnostics *,const ThugMemory *);
double thug_balance_position(const ThugBalanceContext *);
void thug_score_record_rail(ThugScore *,int32_t index);
double thug_walk_parameter(uint32_t saved_ecx,uint32_t name);
uint32_t thug_grind_trick_variant(uint32_t,uint32_t,uint32_t,uint32_t);
void thug_skater_reverse_orientation(ThugSkaterPhysics *);
uint8_t thug_skater_set_board_rotated(ThugPendingFlip *,uint32_t id,uint32_t rotated,uint32_t time,uint32_t send,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_apply_pending_flip(ThugPendingFlip *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_start_grind_script(ThugSkaterPhysics *,uint32_t category,uint32_t,uint32_t,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void thug_trick_primary_destroy(ThugTrickNode *);
void thug_trick_secondary_destroy(ThugTrickNode *);
ThugTrickNode *thug_trick_primary_delete(ThugTrickNode *,uint32_t,const ThugMemory *);
ThugTrickNode *thug_trick_secondary_delete(ThugTrickNode *,uint32_t,const ThugMemory *);
void thug_tricks_cancel(ThugTrickLists *,uint32_t select,uint32_t clear,const ThugMemory *);
ThugScriptInstance *thug_object_set_script(ThugReferencedObject *,uint32_t,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_skater_run_pending_trick(ThugSkaterNameContext *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
#endif
