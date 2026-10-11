#ifndef THUG_SCRIPT_BRANCHES_H
#define THUG_SCRIPT_BRANCHES_H
#include "runtime.h"
#include "../core/memory.h"
typedef struct ThugScriptBranchState {
    ThugScriptInstance *script;
    const uint8_t *offsets;
    uint16_t count, unknown_a;
    uint32_t type;
    uint16_t index;
    uint8_t order[66];
    uint32_t last_choice;
    struct ThugScriptBranchState *next, *previous;
} ThugScriptBranchState;
/* 6f2358, 6f235c, 6f2360. The original cache retains at most 100 records. */
extern ThugScriptBranchState *thug_script_branch_first, *thug_script_branch_last;
extern uint32_t thug_script_branch_count;
ThugScriptBranchState *thug_script_branch_find(const uint8_t *offsets, uint32_t type, uint32_t count);
ThugScriptBranchState *thug_script_branch_allocate(const ThugMemory *);
void thug_script_branch_shuffle(ThugScriptBranchState *, uint8_t avoid_previous);
void thug_script_branch_detach(ThugScriptInstance *);
/* Advance through jumps and random choices until a different token is reached.
 * Internal contract: valid terminating bytecode, valid weights/choice counts,
 * successful allocation. This is not a bounds-checked file parser. */
const uint8_t *thug_script_resolve_branches(const uint8_t *, const ThugMemory *);
#endif
