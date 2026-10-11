#ifndef THUG_GAME_OBJECTIVES_H
#define THUG_GAME_OBJECTIVES_H
#include "stats.h"
#include "../network/queue.h"
#include "../platform/diagnostics.h"
/* The object that holds difficulty parameters also owns the objective list. */
typedef ThugDifficultySettings ThugObjectiveManager;
typedef struct ThugObjective ThugObjective;
typedef struct ThugScriptInstance ThugScriptInstance;
typedef struct ThugObjectiveChild {
    uint32_t id;
    struct ThugObjectiveChild *next;
    uint8_t completed, unknown_9_to_b[3];
} ThugObjectiveChild;
/* Recovered slots of the base/event tables. Unrecovered slots stay uncallable. */
typedef struct {
    uint32_t unknown_0[3];
    uint8_t (*is_active)(const ThugObjective *);
    uint32_t unknown_10[7];
    uint8_t (*activate)(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
    void (*mark_active)(ThugObjective *);
    uint8_t (*deactivate)(ThugObjective *, uint32_t, uint32_t, const ThugDiagnostics *, const ThugMemory *);
    void (*mark_inactive)(ThugObjective *);
    uint8_t (*win)(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
    uint32_t unknown_40[3];
    uint8_t (*set_flag)(ThugObjective *, uint32_t, uint32_t, uint32_t, const ThugDiagnostics *, const ThugMemory *);
    uint32_t unknown_50;
    uint8_t (*is_beaten)(const ThugObjective *);
    uint32_t unknown_58[2];
    uint8_t (*is_initialized)(const ThugObjective *);
    uint8_t (*has_selection_flag)(const ThugObjective *);
    void (*mark_beaten)(ThugObjective *);
} ThugObjectiveMethods;
extern const ThugObjectiveMethods thug_objective_base_methods, thug_objective_event_methods;
struct ThugObjective {
    ThugQueueNode queue_node;
    uint8_t unknown_14_to_1b[8];
    ThugScriptStructure *parameters, *state;
    uint32_t unknown_24;
    ThugObjectiveChild *children;
    const uint32_t *parent_id;
    uint32_t unknown_30;
    int32_t level, index;
    uint8_t unknown_3c_to_43[8];
    uint32_t activation_count;
    uint32_t best_time;
    int32_t best_score;
    uint32_t timer, unknown_54;
    int32_t target_count, completed_count;
    uint32_t value_60;
    uint8_t unknown_64_to_6b[8], flags, state_flags;
};
struct ThugObjectiveLink {
    uint32_t key;
    ThugObjective *objective;
    ThugObjectiveLink *next;
};
typedef struct { uint32_t entries[512], count; } ThugObjectiveNotifications;
typedef struct { uint8_t unknown[8]; ThugObjectLookupTable all_objects, table; } ThugObjectiveObjectTable;
extern ThugObjectiveObjectTable *thug_objective_objects;
void thug_object_count_owned_callback(void *, void *);
uint32_t thug_objective_owned_count(const ThugObjectiveObjectTable *, uint32_t owner);
extern const char thug_objective_id_key[];
void *thug_objective_object_find(const ThugObjectiveObjectTable *, uint32_t name);
uint8_t thug_objective_notifications_clear(ThugObjectiveNotifications *);
ThugObjectiveManager *thug_objective_manager(void);
ThugScriptStructure *thug_objective_parameters(const ThugObjective *);
/* Internal callers provide enough list nodes for indexed access. Optional key
 * output can alias manager state; its write precedes the final value read. */
ThugObjective *thug_objective_at(ThugObjectiveManager *, const int32_t *index, uint32_t *key);
ThugObjective *thug_objective_find(ThugObjectiveManager *, const uint32_t *key);
int32_t thug_game_current_level(const ThugGameplayFlags *);
uint8_t thug_objective_unavailable(const ThugObjectiveManager *, int32_t index, int32_t level);
uint32_t thug_objective_is_disabled(const ThugObjective *);
uint32_t thug_objective_state_flag(const ThugObjective *, uint32_t name, uint32_t nested);
uint32_t thug_objective_id(const ThugObjective *);
/* This lookup requires the original array parameter to be present. */
ThugScriptStructure *thug_objective_event_parameters(const ThugObjective *, uint32_t event);
/* The list must terminate in the original nonnull node with body=-1. */
ThugSkaterBody *thug_game_local_skater(const ThugGameContext *);
uint8_t thug_objective_is_active(const ThugObjective *);
void thug_objective_mark_active(ThugObjective *);
void thug_objective_mark_inactive(ThugObjective *);
uint8_t thug_objective_is_initialized(const ThugObjective *);
uint8_t thug_objective_has_selection_flag(const ThugObjective *);
uint8_t thug_objective_is_beaten(const ThugObjective *);
/* Grouped states require their original count/target integer fields. */
uint8_t thug_objective_is_complete(const ThugObjective *);
void thug_objective_reset_timer(ThugObjective *);
ThugObjective *thug_objective_get(ThugObjectiveManager *, uint32_t id, uint32_t unused);
/* Parent links are acyclic and every nonzero parent ID must resolve. */
uint32_t thug_objective_root_id(const ThugObjective *);
/* Descending order along the previous links; nodes must be unlinked. */
void thug_objective_queue_insert(ThugQueueNode *, ThugQueueNode *);
void thug_objective_manager_enqueue(ThugObjectiveManager *, ThugObjective *);
void thug_objective_initialize_state(ThugObjective *, const ThugScriptStructure *, const ThugMemory *);
uint8_t thug_objective_text_tables(const ThugScriptArray *, ThugScriptArray *, ThugScriptArray *, int32_t, const ThugMemory *);
/* Strings/buffers and marker indices must be valid. Replacement strings are
 * argument-free printf formats: literals and %% only. The capacity is unused
 * in the original, so the caller must provide sufficient output space. */
void thug_objective_expand_text(const char *, char *, const ThugScriptArray *, const ThugScriptArray *, uint32_t);
/* Replacements must fit the original 512-byte temporary buffer. */
uint8_t thug_objective_update_text(ThugObjective *, const ThugMemory *);
/* Loaded difficulty entries and any initialization script must be valid;
 * synchronous scripts must terminate. Text uses the contracts above. */
void thug_objective_initialize(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
/* Initial parent_id storage is required; nonzero parent IDs must resolve.
 * Reset-score players require their real score and local UI components. */
uint8_t thug_objective_activate(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_objective_manager_activate(ThugObjectiveManager *, uint32_t id, uint32_t allow_missing, const ThugDiagnostics *, const ThugMemory *);
/* Original native QB ABI. The dispatcher supplies scoped platform services;
 * direct calls require the same service binding and the required id parameter. */
uint32_t thug_script_goal_activate(ThugScriptStructure *, ThugScriptInstance *);
uint32_t thug_script_goal_deactivate(ThugScriptStructure *, ThugScriptInstance *);
uint32_t thug_script_goal_clear_last(ThugScriptStructure *, ThugScriptInstance *);
void thug_objective_mark_beaten(ThugObjective *);
uint8_t thug_objective_run_handler(ThugObjective *, uint32_t name, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_unlock(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_manager_unlock(ThugObjectiveManager *, uint32_t id, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_unlock_targets(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_objective_reward_amount(const ThugObjective *);
void thug_objective_manager_add_reward(ThugObjectiveManager *, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_build_rewards(ThugObjective *, ThugScriptStructure *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_objective_win(ThugObjective *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_objective_set_flag(ThugObjective *, uint32_t name, uint32_t value, uint32_t group, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_handle_event(ThugObjective *, uint32_t event, const ThugDiagnostics *, const ThugMemory *);
void thug_objective_manager_notify(ThugObjectiveManager *, uint32_t event, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_objective_notify(ThugObjectiveNotifications *, uint32_t key, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_set_notification_flag(ThugSkaterNameContext *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_notify(ThugSkaterNameContext *, uint32_t key, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_script_goal_set_flag(ThugScriptStructure *, ThugScriptInstance *);
uint8_t thug_objective_manager_win(ThugObjectiveManager *, uint32_t id, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_script_goal_win(ThugScriptStructure *, ThugScriptInstance *);
/* Original reset loops never advance past a member named num_flags. Such
 * states do not terminate; ordinary flat training state stores it in params. */
void thug_objective_clear_members(ThugScriptStructure *);
void thug_objective_clear_state(ThugObjective *, const ThugMemory *);
/* Child/parent graphs must be acyclic; uninitialize requires resolved children. */
void thug_objective_reset_children(ThugObjective *);
void thug_objective_uninitialize(ThugObjective *, uint32_t recursive, uint32_t depth, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_objective_deactivate(ThugObjective *, uint32_t unused, uint32_t reset_parent, const ThugDiagnostics *, const ThugMemory *);
#endif
