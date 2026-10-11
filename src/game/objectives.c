#include "objectives.h"
#include "score.h"
#include "profile.h"
#include "../core/number.h"
#include "../platform/math.h"
#include "../script/operators.h"
#include "../script/values.h"
#include "../script/schedule.h"
#include "../script/delivery.h"
#include <stddef.h>
_Static_assert(offsetof(ThugDifficultySettings, parameters) == 0x398, "Difficulty parameters retained");
_Static_assert(offsetof(ThugObjectiveManager, cached_objective) == 0xc, "Cached objective");
_Static_assert(offsetof(ThugObjectiveManager, cached_index) == 0x10, "Cached index");
_Static_assert(offsetof(ThugObjectiveManager, last_goal) == 0x2c, "Last selected goal");
_Static_assert(offsetof(ThugObjectiveManager, value_40) == 0x40, "Completion counter");
_Static_assert(offsetof(ThugObjective, best_score) == 0x4c, "Best score");
_Static_assert(offsetof(ThugObjective, flags) == 0x6c, "Objective flags");
_Static_assert(offsetof(ThugObjective, state_flags) == 0x6d, "Objective state flags");
_Static_assert(offsetof(ThugObjective, target_count) == 0x58, "Objective target count");
_Static_assert(offsetof(ThugObjective, activation_count) == 0x44, "Activation count");
_Static_assert(offsetof(ThugObjective, value_60) == 0x60, "Activation reset word");
_Static_assert(offsetof(ThugObjective, parent_id) == 0x2c, "Objective parent link");
_Static_assert(offsetof(ThugObjectiveChild, completed) == 8, "Child completion byte");
_Static_assert(offsetof(ThugObjectiveMethods, is_active) == 0xc, "Activity virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, activate) == 0x2c, "Activation virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, win) == 0x3c, "Completion virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, set_flag) == 0x4c, "Goal flag virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, mark_beaten) == 0x68, "Beaten setter virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, deactivate) == 0x34, "Deactivation virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, mark_inactive) == 0x38, "Inactive virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, is_beaten) == 0x54, "Beaten virtual slot");
_Static_assert(offsetof(ThugObjectiveMethods, is_initialized) == 0x60, "Initialized virtual slot");
_Static_assert(offsetof(ThugObjectiveObjectTable, table) == 0x20, "Object lookup table");
_Static_assert(offsetof(ThugObjectiveNotifications, count) == 0x800, "Notification count");
_Static_assert(offsetof(ThugGameContext, skaters) == 0x34, "Skater list");
_Static_assert(offsetof(ThugGameContext, difficulty) == 0x38c, "Manager pointer retained");
const char thug_objective_id_key[] = "goal_id";
ThugObjectiveObjectTable *thug_objective_objects;
/* These slots coincide in original tables 0x0064ddd0 and 0x0064ea30. */
#define OBJECTIVE_METHODS { .is_active = thug_objective_is_active, .mark_active = thug_objective_mark_active, \
    .activate = thug_objective_activate, .win = thug_objective_win, .set_flag = thug_objective_set_flag, \
    .deactivate = thug_objective_deactivate, .mark_inactive = thug_objective_mark_inactive, \
    .is_beaten = thug_objective_is_beaten, .is_initialized = thug_objective_is_initialized, \
    .has_selection_flag = thug_objective_has_selection_flag, .mark_beaten = thug_objective_mark_beaten }
const ThugObjectiveMethods thug_objective_base_methods = OBJECTIVE_METHODS;
const ThugObjectiveMethods thug_objective_event_methods = OBJECTIVE_METHODS;
#undef OBJECTIVE_METHODS
static const ThugObjectiveMethods *methods(const ThugObjective *o) { return (const void *)o->queue_node.methods; }
static uint32_t word(const void *p) { uint32_t value; __builtin_memcpy(&value,p,4); return value; }
static int32_t index_value(const int32_t *p) { return (int32_t)word(p); }

/* 0x00556330. Required named states contain integers. Changing between two
 * different nonzero values still increments the count, as in the original. */
uint8_t thug_objective_set_flag(ThugObjective *o, uint32_t name, uint32_t value, uint32_t group,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t automatic = thug_script_has_flag(o->parameters,0x2d4c5829) && !methods(o)->is_beaten(o);
    if (!methods(o)->is_active(o) && !automatic) return 0;
    ThugObjectiveManager *manager = thug_objective_manager();
    if ((o->flags & 0x20) || thug_objective_unavailable(manager,o->index,o->level)) return 0;
    ThugScriptStructure *state = o->state;
    if (group) thug_script_get_structure(o->state,group,&state,1);
    uint8_t found = 0;
    if (thug_script_has_name_or_flag(state,name)) {
        uint32_t previous;
        thug_script_get_integer(state,name,&previous,1);
        thug_script_set_integer(state,name,value,memory);
        if (previous != value) {
            if (group) {
                uint32_t count;
                thug_script_get_integer(state,0xcf6cd3c1,&count,1);
                thug_script_set_integer(state,0xcf6cd3c1,count+(value ? 1u : UINT32_MAX),memory);
            } else o->completed_count = (int32_t)((uint32_t)o->completed_count+(value ? 1u : UINT32_MAX));
            if (value && !thug_script_has_flag(o->parameters,0x524566e3))
                thug_script_run_sync(0x5ed34deb,NULL,NULL,0,diagnostics,memory);
            if (thug_script_has_flag(o->parameters,0xfd7ae1f4))
                thug_script_run_sync(0xf2e85a34,o->parameters,NULL,0,diagnostics,memory);
            thug_script_set_integer(o->parameters,0xcf6cd3c1,(uint32_t)o->completed_count,memory);
        }
        found = 1;
    }
    if (automatic && !thug_script_has_flag(o->parameters,0xefc35592)) {
        if (thug_objective_is_complete(o)) {
            manager = thug_objective_manager();
            thug_objective_manager_win(manager,thug_objective_id(o),diagnostics,memory);
        } else if (!group && thug_script_has_flag(o->parameters,0xd76c173e) &&
                   !thug_script_has_flag(o->parameters,0x5bc07eaa)) {
            ThugScriptStructure *parameters = thug_script_structure_allocate(8,memory);
            if (parameters) thug_script_structure_initialize(parameters);
            thug_script_structure_merge_optional(parameters,o->parameters,memory);
            thug_script_run_sync(0x96de9a0c,parameters,NULL,0,diagnostics,memory);
            if (parameters) { thug_script_structure_destroy(parameters,memory); thug_script_structure_free(parameters,memory); }
        }
    }
    return found;
}
/* 0x00559670: GoalManager_SetGoalFlag; the two unnamed required parameters
 * have different types. Capture the manager before reading script parameters. */
uint32_t thug_script_goal_set_flag(ThugScriptStructure *parameters, ThugScriptInstance *script) {
    (void)script;
    ThugObjectiveManager *manager = thug_game_difficulty_settings(thug_game_context);
    uint32_t id, name, value, group = 0;
    thug_script_get_checksum(parameters,0xa1dc81f9,&id,1);
    thug_script_get_checksum(parameters,0,&name,1);
    thug_script_get_integer(parameters,0,&value,1);
    thug_script_get_checksum(parameters,0x5b8ab877,&group,0);
    ThugObjective *o = thug_objective_find(manager,&id);
    return o ? methods(o)->set_flag(o,name,value,group,thug_event_services->diagnostics,thug_event_services->memory) : 0;
}
/* 0x00576520. The event parameter structure survives activation. The score
 * multiplier retains x87 PC24 precision before the original integer conversion. */
void thug_objective_handle_event(ThugObjective *o, uint32_t event,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptStructure *parameters = thug_objective_event_parameters(o,event);
    if (!parameters || methods(o)->is_beaten(o) || thug_objective_is_disabled(o)) return;
    ThugSkaterBody *body = thug_game_local_skater(thug_game_context);
    if (!body) return;
    ThugObjectComponent *component = thug_object_find_component(body,0x43686585);
    ThugObjectComponent *score_component = thug_object_find_component(body,0xd262802f);
    uint8_t active = *((const uint8_t *)component+0xe0);
    ThugScore *score = (void *)(uintptr_t)word((const uint8_t *)score_component+0x18);
    if (!active) {
        float multiplier; __builtin_memcpy(&multiplier,&score->value_60,4);
        double product = thug_platform_multiply_x87_single((double)(int32_t)score->value_14, multiplier);
        if ((int32_t)thug_truncate_double_low_word(product) <= 0) return;
    }
    if (!methods(o)->is_active(o)) {
        ThugObjectiveManager *manager = thug_objective_manager();
        thug_objective_manager_activate(manager,thug_objective_id(o),0,diagnostics,memory);
    }
    uint32_t name;
    thug_script_get_checksum(parameters,0x2e0b1465,&name,1);
    if (!thug_objective_state_flag(o,name,0)) methods(o)->set_flag(o,name,1,0,diagnostics,memory);
}
/* 0x00559150. The initial signed count is retained across all goal callbacks. */
void thug_objective_manager_notify(ThugObjectiveManager *manager, uint32_t event,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    int32_t count = manager->objective_count;
    for (int32_t i = 0; i < count; ++i) {
        uint32_t key;
        ThugObjective *o = thug_objective_at(manager,&i,&key);
        if (thug_script_has_flag(thug_objective_parameters(o),0xefc35592))
            thug_objective_handle_event(o,event,diagnostics,memory);
    }
}
/* 0x00588a20. Duplicate detection uses the captured count; insertion uses the
 * count after callbacks. Only the low return byte is defined and it is zero. */
uint8_t thug_objective_notify(ThugObjectiveNotifications *notifications, uint32_t key,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint32_t count = notifications->count;
    if (count > 512) count = 512;
    const uint8_t *object = thug_objective_object_find(thug_objective_objects,key);
    if (!object) return 0;
    uint32_t id = word(object+0x14);
    if (!id) return 0;
    for (uint32_t i = 0; i < count; ++i) if (notifications->entries[i] == id) return 0;
    thug_objective_manager_notify(thug_objective_manager(),id,diagnostics,memory);
    notifications->entries[notifications->count & 511] = id;
    ++notifications->count;
    return 0;
}
/* 0x005232a0 / 0x00522370. Notification state belongs to this component;
 * its current event key is read through the object pointer at offset 28. */
void thug_skater_set_notification_flag(ThugSkaterNameContext *component, uint32_t value,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t *bytes = (uint8_t *)component;
    bytes[0x13b0] = (uint8_t)value;
    ThugObjectiveNotifications *notifications = (void *)(bytes+0x13b4);
    if (!(uint8_t)value) thug_objective_notifications_clear(notifications);
    else {
        const uint8_t *object = (const void *)(uintptr_t)word(bytes+0x28);
        thug_objective_notify(notifications,word(object+0x1b0),diagnostics,memory);
    }
}
void thug_skater_notify(ThugSkaterNameContext *component, uint32_t key,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t *bytes = (uint8_t *)component;
    if (bytes[0x13b0]) thug_objective_notify((void *)(bytes+0x13b4),key,diagnostics,memory);
}

/* 0x00588120. A false predicate still writes back the original count. */
void thug_object_count_owned_callback(void *value, void *context) {
    uint32_t *count = context; const uint8_t *object = value;
    uint32_t increment = object[0x40] && count[1] == word(object+0x3c);
    count[0] += increment;
}
/* 0x00588400. */
uint32_t thug_objective_owned_count(const ThugObjectiveObjectTable *objects, uint32_t owner) {
    uint32_t context[2] = {0, owner};
    thug_object_table_visit(&objects->all_objects,thug_object_count_owned_callback,context);
    return context[0];
}

/* 0x005555e0. All parent links are visited, not just the first ancestor chain.
 * Every nonzero parent ID must resolve and the parent graph must be acyclic. */
void thug_objective_mark_beaten(ThugObjective *o) {
    o->flags |= thug_network_is_active(thug_network_state) && thug_settings_mode(thug_game_settings) == 0xec200eaa ? 8 : 4;
    ThugObjectiveManager *manager = thug_objective_manager();
    for (const uint32_t *parent = o->parent_id; parent && *parent; parent = (const void *)(uintptr_t)word(parent+1)) {
        ThugObjective *p = thug_objective_get(manager,*parent,1);
        methods(p)->mark_beaten(p);
    }
}
/* 0x00554a80. */
uint8_t thug_objective_run_handler(ThugObjective *o, uint32_t name, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!thug_script_get_checksum(o->parameters,name,&name,0)) return 0;
    thug_script_run_sync(name,o->parameters,NULL,0,diagnostics,memory); return 1;
}
/* 0x00557a40. Clearing the disabled flag precedes every network/state check. */
void thug_objective_unlock(ThugObjective *o, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!(o->flags & 0x20)) return;
    o->flags &= 0xdf;
    if (thug_network_is_active(thug_network_state)) return;
    if (!methods(o)->is_beaten(o) || thug_settings_mode(thug_game_settings) == 0x4c10de52 ||
        thug_script_has_flag(o->parameters,0x4e863e93) || thug_script_has_flag(o->parameters,0x981d3ad0))
        thug_objective_initialize(o,diagnostics,memory);
    thug_objective_run_handler(o,0x951b4f10,diagnostics,memory);
}
/* 0x005588d0. The original requires the requested goal to exist. */
void thug_objective_manager_unlock(ThugObjectiveManager *manager, uint32_t id, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_objective_unlock(thug_objective_find(manager,&id),diagnostics,memory);
}
/* 0x00555fb0. Capture array count once; ignore zero entries only in array form. */
void thug_objective_unlock_targets(ThugObjective *o, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugObjectiveManager *manager = thug_objective_manager();
    uint32_t id = 0; ThugScriptArray *array = NULL;
    if (thug_script_get_checksum(o->parameters,0x0232844a,&id,0))
        thug_objective_manager_unlock(manager,id,diagnostics,memory);
    else if (thug_script_get_array(o->parameters,0x0232844a,&array,0)) {
        int32_t count = (int32_t)array->count;
        for (int32_t i = 0; i < count; ++i) {
            id = (uint32_t)(uintptr_t)thug_script_array_structure(array,i);
            if (id) thug_objective_manager_unlock(manager,id,diagnostics,memory);
        }
    }
}
/* 0x00556050. Scalar amount wins over the difficulty-indexed array. */
uint32_t thug_objective_reward_amount(const ThugObjective *o) {
    uint32_t value; ThugScriptArray *array = NULL;
    if (thug_script_get_integer(o->parameters,0xbaffb052,&value,0)) return value;
    if (thug_script_get_array(o->parameters,0xbaffb052,&array,0)) {
        int32_t index = (int32_t)thug_game_difficulty(thug_objective_manager(),0);
        if (index >= 0 && index < (int32_t)array->count) return (uint32_t)(uintptr_t)thug_script_array_structure(array,index);
    }
    return 0;
}
/* 0x00557e40. Both counters are written before invoking the notification. */
void thug_objective_manager_add_reward(ThugObjectiveManager *manager, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ++manager->value_38; ++manager->value_3c;
    thug_script_run_sync(0x888ef05e,NULL,NULL,0,diagnostics,memory);
}

/* 0x00555df0. Reward templates can be modified in place before merging. The
 * network pointer is captured before the manager's notification script. */
void thug_objective_build_rewards(ThugObjective *o, ThugScriptStructure *out,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugObjectiveManager *manager = thug_objective_manager();
    ThugNetworkState *network = thug_network_state;
    if (!thug_script_has_flag(o->parameters,0x981d3ad0)) thug_objective_manager_add_reward(manager,diagnostics,memory);
    thug_script_set_checksum(out,0,0xc7fef529,memory);
    if (thug_network_is_active(network)) return;
    if (thug_script_has_flag(o->parameters,0xb6432d23) && !thug_script_has_flag(o->parameters,0x8e6014f6)) {
        int32_t count = (int32_t)thug_profile_binding_count(thug_game_profile(thug_game_context,NULL));
        int32_t limit = (int32_t)thug_script_get_global_integer(0x20297d6f,0);
        if (count <= limit) {
            uint32_t value = 0; thug_script_get_integer(o->parameters,0xbc678826,&value,0);
            if (value == 1) {
                thug_script_set_integer(o->parameters,0xbc678826,0,memory);
                thug_script_set_checksum(o->parameters,0,0x65ca5ffc,memory);
                thug_script_set_integer(o->parameters,0xb45fd352,1,memory);
            }
        }
    }
    ThugScriptStructure *templates = thug_script_get_global_structure(0x67f6e334,1), *reward = NULL;
    uint32_t id = 0;
    thug_script_get_checksum_string(o->parameters,thug_objective_id_key,&id,1);
    thug_script_get_structure(templates,id,&reward,0);
    if (reward) {
        if (thug_script_has_flag(reward,0xde569045)) {
            thug_script_remove_name(reward,0xde569045,memory);
            thug_script_set_integer(reward,0xde569045,1,memory);
        }
        thug_script_structure_merge(out,reward,memory);
    } else if (thug_script_has_flag(o->parameters,0xde569045)) thug_script_set_integer(out,0xde569045,1,memory);
    else if (thug_script_get_integer(o->parameters,0xde569045,&id,0)) thug_script_set_integer(out,0xde569045,id,memory);
}

/* The same selected structure pool used by original operator new409030.
 * Successful allocation is an internal caller contract, as in the executable. */
static ThugScriptStructure *reward_structure(const ThugMemory *memory) {
    ThugScriptStructure *s = thug_script_structure_allocate(8, memory);
    return s ? thug_script_structure_initialize(s) : NULL;
}

/* 0x005576d0. Complete child progression and leaf completion, including score
 * records, reward ownership, unlocks, handlers and career/classic progress. */
uint8_t thug_objective_win(ThugObjective *o, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_set_integer(o->parameters,0xc22a2b72,0,memory);
    ThugObjectiveChild *child = o->children;
    if (child->id) {
        ThugObjectiveManager *manager = thug_objective_manager();
        methods(o)->deactivate(o,0,1,diagnostics,memory);
        thug_objective_uninitialize(o,0,0,diagnostics,memory);
        thug_objective_initialize(thug_objective_get(manager,child->id,1),diagnostics,memory);
        thug_objective_manager_activate(manager,child->id,0,diagnostics,memory);
        child->completed = 1; return 1;
    }
    thug_script_set_checksum(o->parameters,0,0xc309cad1,memory);
    ThugNetworkState *network = thug_network_state;
    uint8_t improved = 0;
    uint32_t kind;
    if (!thug_network_is_active(network) && thug_script_get_checksum(o->parameters,0x96963902,&kind,0)) {
        uint32_t value;
        if (kind == 0xcd66c8ae) {
            if (!thug_script_get_integer(o->parameters,0xfc9630ab,&value,0)) {
                ThugSkaterBody *body = thug_game_local_skater(thug_game_context);
                ThugObjectComponent *component = thug_object_find_component(body,0xd262802f);
                ThugScore *score = (void *)(uintptr_t)word((uint8_t *)component+0x18);
                value = thug_script_has_flag(o->parameters,0xc63432a7) ? word((uint8_t *)score+0x20) : thug_score_current(score);
            }
            if ((int32_t)value > o->best_score) { o->best_score = (int32_t)value; improved = 1; }
        } else if (kind == 0x906b67ba && o->value_60 < o->best_time) {
            value = o->value_60; o->best_time = value; improved = 1;
        }
        if (improved) thug_script_set_integer(o->parameters,0xc22a2b72,value,memory);
    }
    uint8_t awarded = 0;
    if (!methods(o)->is_beaten(o) && !thug_network_is_active(network)) {
        ThugScriptStructure *reward = reward_structure(memory);
        thug_objective_build_rewards(o,reward,diagnostics,memory);
        if (improved) thug_script_set_checksum(reward,0,0xe7b8254f,memory);
        thug_script_set_structure(o->parameters,0x128b3088,reward,memory);
        thug_objective_unlock_targets(o,diagnostics,memory); awarded = 1;
    } else thug_script_remove_name(o->parameters,0x128b3088,memory);
    if (improved) thug_script_set_checksum(o->parameters,0,0xe7b8254f,memory);
    else thug_script_remove_unnamed_value(o->parameters,0xe7b8254f,memory);
    uint32_t script;
    if (thug_script_get_checksum(o->parameters,0x90ff204d,&script,0)) thug_script_run_sync(script,o->parameters,NULL,0,diagnostics,memory);
    uint8_t testing = thug_script_has_flag(o->parameters,0x54d3cac1);
    if (methods(o)->is_active(o)) methods(o)->deactivate(o,0,1,diagnostics,memory);
    if (!testing) {
        methods(o)->mark_beaten(o);
        if (awarded) {
            ThugGameplayFlags *state = thug_game_context->gameplay_flags;
            if (thug_settings_flag(thug_game_settings,0x1ded1ea4)) {
                thug_gameplay_add_points(state,thug_objective_reward_amount(o));
                ThugScriptStructure *parameters = reward_structure(memory);
                thug_script_set_integer(parameters,0x35a1c616,thug_objective_reward_amount(o),memory);
                thug_script_run_sync(0x7cf09270,parameters,NULL,0,diagnostics,memory);
                if (parameters) { thug_script_structure_destroy(parameters,memory); thug_script_structure_free(parameters,memory); }
            } else if (thug_settings_flag(thug_game_settings,0x5a2c589a)) thug_gameplay_add_completion(state);
        }
    }
    if (thug_network_is_active(network)) thug_objective_uninitialize(o,0,0,diagnostics,memory);
    thug_script_remove_unnamed_value(o->parameters,0xc309cad1,memory);
    return 1;
}

/* 0x00558030. The notification's first word retains the captured network
 * pointer's upper bytes, exactly as the original reused stack local does. */
uint8_t thug_objective_manager_win(ThugObjectiveManager *manager, uint32_t id, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugNetworkState *network = thug_network_state;
    ThugObjective *o = thug_objective_find(manager,&id);
    if (!o) return 0;
    uint32_t root = id;
    const uint32_t *parent = o->parent_id;
    while (parent && *parent) {
        root = *parent;
        parent = thug_objective_find(manager,&root)->parent_id;
    }
    if (root == manager->last_goal && !o->children->id) manager->last_goal = 0;
    if (!methods(o)->is_beaten(o)) {
        if (!o->children->id && thug_network_is_active(network)) {
            ThugMessageSpec spec; thug_message_spec_initialize(&spec);
            ThugQueueClient *client = thug_network_get_client(network,0);
            uint32_t payload[2]; payload[0] = ((uint32_t)(uintptr_t)network & 0xffffff00u) | thug_network_slot(network);
            payload[1] = thug_objective_root_id(o);
            spec.id = 0x6e; spec.length = 8; spec.group = 8; spec.data = (const uint8_t *)payload; spec.delivery = 2;
            thug_queue_send_first(client,&spec,diagnostics,memory);
        } else if (!o->children->id && !thug_script_has_flag(thug_objective_parameters(o),0x981d3ad0)) ++manager->value_40;
    }
    methods(o)->win(o,diagnostics,memory);
    return 1;
}
/* 0x00559310: GoalManager_WinGoal. The id is required by the original caller. */
uint32_t thug_script_goal_win(ThugScriptStructure *parameters, ThugScriptInstance *script) {
    (void)script;
    ThugObjectiveManager *manager = thug_game_difficulty_settings(thug_game_context);
    uint32_t id; thug_script_get_checksum(parameters,0xa1dc81f9,&id,1);
    return thug_objective_manager_win(manager,id,thug_event_services->diagnostics,thug_event_services->memory);
}

/* 0x00588380. Matching null values are skipped, and only five shift bits count. */
void *thug_objective_object_find(const ThugObjectiveObjectTable *objects, uint32_t name) {
    uint32_t slot = name & ((UINT32_C(1) << (objects->table.shift & 31))-1);
    ThugObjectLookupNode *node = (ThugObjectLookupNode *)((uintptr_t)objects->table.buckets+slot*12u);
    while (node) { if (node->key == name && node->value) return node->value; node = node->next; }
    return NULL;
}
/* 0x00588180. Old entries are deliberately retained. Only AL is defined. */
uint8_t thug_objective_notifications_clear(ThugObjectiveNotifications *notifications) { notifications->count = 0; return 1; }
/* 0x005591b0. The complete original wrapper uses the existing context getter. */
ThugObjectiveManager *thug_objective_manager(void) { return thug_game_difficulty_settings(thug_game_context); }
/* 0x00553e90. */
ThugScriptStructure *thug_objective_parameters(const ThugObjective *objective) { return objective->parameters; }

/* 0x00557f10. Forward indexed traversal reuses its cached node. The index
 * pointer is reread after cache writes, and the final node is reread after key. */
ThugObjective *thug_objective_at(ThugObjectiveManager *manager, const int32_t *index, uint32_t *key) {
    if (manager->cached_objective) {
        int32_t wanted = index_value(index);
        if (manager->cached_index != wanted) {
            if (manager->cached_index < wanted) {
                do {
                    manager->cached_index = (int32_t)((uint32_t)manager->cached_index+1);
                    manager->cached_objective = manager->cached_objective->next;
                } while (manager->cached_index < index_value(index));
            } else manager->cached_objective = NULL;
        }
    }
    if (!manager->cached_objective) {
        int32_t wanted = index_value(index);
        ThugObjectiveLink *node = manager->objectives;
        for (int32_t remaining = wanted; remaining > 0; --remaining) node = node->next;
        manager->cached_index = wanted;
        manager->cached_objective = node;
    }
    if (key) { uint32_t value = manager->cached_objective->key; __builtin_memcpy(key,&value,4); }
    return manager->cached_objective->objective;
}
/* 0x00561430. Clear cache first; a missing key leaves the traversed count. */
ThugObjective *thug_objective_find(ThugObjectiveManager *manager, const uint32_t *key) {
    ThugObjectiveLink *node = manager->objectives;
    manager->cached_objective = NULL; manager->cached_index = 0;
    while (node) {
        if (node->key == word(key)) { manager->cached_objective = node; return node->objective; }
        manager->cached_index = (int32_t)((uint32_t)manager->cached_index+1);
        node = node->next;
    }
    return NULL;
}
/* 0x00584130. Field 630 follows the existing flag words at 5f0. */
int32_t thug_game_current_level(const ThugGameplayFlags *flags) { return (int32_t)flags->words[16]; }
/* 0x00559110. The unchecked grid uses ten columns and 32-bit address math. */
uint8_t thug_objective_unavailable(const ThugObjectiveManager *manager, int32_t index, int32_t level) {
    if (index == -1) return 0;
    if (level == -1) level = thug_game_current_level(thug_game_context->gameplay_flags);
    uint32_t offset = 0x4c+4*((uint32_t)index+10*(uint32_t)level);
    return word((const void *)((uintptr_t)manager+offset)) == 0;
}
/* 0x00554220. The manager wrapper is called even when bit 20 short-circuits. */
uint32_t thug_objective_is_disabled(const ThugObjective *objective) {
    ThugObjectiveManager *manager = thug_objective_manager();
    return (objective->flags & 0x20) || thug_objective_unavailable(manager, objective->index, objective->level);
}
/* 0x005541e0. PUSH ECX seeds the integer local with this. A missing nested
 * structure retains its incoming name word, as in the unchecked original. */
uint32_t thug_objective_state_flag(const ThugObjective *objective, uint32_t name, uint32_t nested) {
    ThugScriptStructure *state = objective->state;
    if (nested) { ThugScriptStructure *value = (ThugScriptStructure *)(uintptr_t)nested; thug_script_get_structure(state,nested,&value,1); state = value; }
    uint32_t value = (uint32_t)(uintptr_t)objective;
    thug_script_get_integer(state,name,&value,1);
    return value != 0;
}
/* 0x00554280. The textual key and initialized zero are both significant. */
uint32_t thug_objective_id(const ThugObjective *objective) {
    uint32_t id = 0;
    thug_script_get_checksum_string(objective->parameters,thug_objective_id_key,&id,1);
    return id;
}
/* 0x005764b0. Missing per-item checksums retain the preceding value (initially
 * the requested event); the captured signed count controls iteration. */
ThugScriptStructure *thug_objective_event_parameters(const ThugObjective *objective, uint32_t event) {
    ThugScriptArray *array;
    thug_script_get_array(objective->parameters,0x3cce31f0,&array,1);
    int32_t count = (int32_t)array->count;
    uint32_t value = event;
    for (int32_t i = 0; i < count; ++i) {
        ThugScriptStructure *entry = thug_script_array_structure(array,i);
        thug_script_get_checksum(entry,0x3c95ccd7,&value,1);
        if (value == event) return entry;
    }
    return NULL;
}
/* 0x00566520. No writes or callbacks occur in the original repeated scans;
 * traversing once preserves the first flagged body in a valid sentinel list. */
ThugSkaterBody *thug_game_local_skater(const ThugGameContext *game) {
    for (ThugSkaterNode *node = game->skaters; (uintptr_t)node->body != UINT32_MAX; node = node->next)
        if (node->body->parameter_sets_enabled) return node->body;
    return NULL;
}

/* Concrete slots shared by the base and event objectives: 0x00553f90,
 * 0x00553f50, 0x00553f60, 0x005519f0 and 0x00554460. */
uint8_t thug_objective_is_active(const ThugObjective *o) { return o->state_flags & 1; }
void thug_objective_mark_active(ThugObjective *o) { o->state_flags |= 1; }
void thug_objective_mark_inactive(ThugObjective *o) { o->state_flags &= 0xfe; }
uint8_t thug_objective_is_initialized(const ThugObjective *o) { return o->flags & 1; }
uint8_t thug_objective_has_selection_flag(const ThugObjective *o) {
    return thug_script_has_flag(o->parameters, 0xdbeb46e2);
}
/* 0x00555590. The second mode is checked even when networking is inactive. */
uint8_t thug_objective_is_beaten(const ThugObjective *o) {
    if (thug_network_is_active(thug_network_state)
        && thug_settings_mode(thug_game_settings) == 0xec200eaa) return (o->flags >> 3) & 1;
    return (o->flags >> (thug_settings_mode(thug_game_settings) == 0x1c471c60 ? 3 : 2)) & 1;
}
/* 0x00554110. Grouped counts are signed. The next member is captured before
 * reading a group's required integers; unrelated members are skipped. */
uint8_t thug_objective_is_complete(const ThugObjective *o) {
    uint32_t target = (uint32_t)o->target_count;
    thug_script_get_integer(o->parameters, 0x1171a555, &target, 0);
    if (!thug_script_has_flag(o->state, 0xe462e527))
        return target != 0 && o->completed_count >= (int32_t)target;
    uint32_t count, required;
    for (ThugScriptComponent *c = thug_script_next_component(o->state, NULL); c;) {
        ThugScriptComponent *next = thug_script_next_component(o->state, c);
        if ((c->type_and_flags & 0xfe) == 0x14) {
            ThugScriptStructure *group = (ThugScriptStructure *)(uintptr_t)c->value;
            thug_script_get_integer(group, 0xcf6cd3c1, &count, 1);
            thug_script_get_integer(group, 0xb3790f33, &required, 1);
            if ((int32_t)count < (int32_t)required) return 0;
        }
        c = next;
    }
    return 1;
}
/* 0x00553ea0. Missing duration uses 120; multiplication/addition wrap as words. */
void thug_objective_reset_timer(ThugObjective *o) {
    uint32_t untimed = 0;
    thug_script_get_integer(o->parameters, 0xf0e712d2, &untimed, 0);
    if (untimed == 1) return;
    o->timer = 120;
    uint32_t duration;
    if (thug_script_get_integer(o->parameters, 0x906b67ba, &duration, 0)) o->timer = duration;
    o->timer = o->timer * 1000u + 20u;
    o->state_flags &= 0xef;
}
/* 0x00557f90. The second stack argument is unused, even on a lookup miss. */
ThugObjective *thug_objective_get(ThugObjectiveManager *manager, uint32_t id, uint32_t unused) {
    (void)unused; return thug_objective_find(manager, &id);
}
/* 0x00555540. Resolve each parent through the actual cache-mutating lookup. */
uint32_t thug_objective_root_id(const ThugObjective *o) {
    ThugObjectiveManager *manager = thug_objective_manager();
    while (o->parent_id && *o->parent_id) o = thug_objective_get(manager, *o->parent_id, 1);
    return thug_objective_id(o);
}
/* 0x0045a540. Traverse the previous links, then insert at the first priority
 * no greater than this node. Both sentinels and input nodes retain their data. */
void thug_objective_queue_insert(ThugQueueNode *sentinel, ThugQueueNode *node) {
    int32_t priority = (int32_t)node->priority;
    ThugQueueNode *at = sentinel;
    do { at = at->previous; }
    while ((uintptr_t)at->value != UINT32_MAX && (int32_t)at->priority > priority);
    if ((uintptr_t)at->value == UINT32_MAX) at = sentinel;
    node->next = at->next;
    node->previous = at;
    at->next->previous = node;
    at->next = node;
}
/* 0x0055dbe0. The queue header is embedded at manager+18. */
void thug_objective_manager_enqueue(ThugObjectiveManager *manager, ThugObjective *o) {
    thug_objective_queue_insert((ThugQueueNode *)((uint8_t *)manager + 0x18), &o->queue_node);
}
/* 0x005566d0. Rebuild objective state from a flat name array or named groups.
 * Group arrays/counts/IDs are required original parameters. Successful heap
 * allocation and acyclic, separately owned source/state graphs are required. */
void thug_objective_initialize_state(ThugObjective *o, const ThugScriptStructure *parameters, const ThugMemory *memory) {
    thug_script_structure_clear(o->state, memory);
    o->target_count = 0;
    ThugScriptArray *array;
    if (thug_script_get_array(parameters, 0xcc3c4cc4, &array, 0)) {
        if (((uint8_t *)&array->unknown_0)[1] == 10) {
            thug_script_set_checksum(o->state, 0, 0xe462e527, memory);
            int32_t count = (int32_t)array->count;
            for (int32_t i = 0; i < count; ++i) {
                ThugScriptStructure *entry = thug_script_array_structure(array, i);
                uint32_t name;
                thug_script_get_checksum(entry, 0x5b8ab877, &name, 1);
                ThugScriptStructure *group = thug_script_structure_initialize(thug_script_structure_allocate(8, memory));
                ThugScriptArray *items;
                thug_script_get_array(entry, 0xcc3c4cc4, &items, 1);
                int32_t item_count = (int32_t)items->count;
                for (int32_t j = 0; j < item_count; ++j)
                    thug_script_set_integer(group, (uint32_t)(uintptr_t)thug_script_array_structure(items, j), 0, memory);
                thug_script_set_integer(group, 0xb3790f33, (uint32_t)item_count, memory);
                thug_script_set_integer(group, 0xcf6cd3c1, 0, memory);
                thug_script_set_structure_copy(o->state, name, group, memory);
                thug_script_structure_destroy(group, memory);
                thug_script_structure_free(group, memory);
            }
        } else {
            for (uint32_t i = 0; i < array->count; ++i) {
                thug_script_set_integer(o->state, (uint32_t)(uintptr_t)thug_script_array_structure(array, (int32_t)i), 0, memory);
                o->target_count = (int32_t)((uint32_t)o->target_count + 1);
            }
        }
    }
    thug_script_set_integer(o->parameters, 0xb3790f33, (uint32_t)o->target_count, memory);
}

/* 0x00557270. State is rebuilt only when a difficulty array is present. The
 * initialization script runs before text conversion and flag changes. A failed
 * text update does not prevent initialization; untimed zero retains bit 10. */
void thug_objective_initialize(ThugObjective *o, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    memory->temp_scope(memory->context, 5);
    ThugScriptArray *difficulty;
    if (thug_script_get_array(o->parameters, 0x85104ab3, &difficulty, 0)) {
        uint32_t index = thug_game_difficulty(thug_objective_manager(), 0);
        thug_script_structure_merge(o->parameters, thug_script_array_structure(difficulty, (int32_t)index), memory);
        thug_objective_initialize_state(o, o->parameters, memory);
    }
    uint32_t script;
    if (thug_script_get_checksum(o->parameters, 0x398b1b8b, &script, 0))
        thug_script_run_sync(script, o->parameters, NULL, 0, diagnostics, memory);
    thug_objective_update_text(o, memory);
    o->flags |= 1;
    uint32_t untimed = 0;
    thug_script_get_integer(o->parameters, 0xf0e712d2, &untimed, 0);
    if (untimed) o->state_flags |= 0x10;
    if (thug_script_has_name_or_flag(o->parameters, 0x79bbffcb)) o->flags &= 0xbf;
    memory->temp_scope(memory->context, 0);
}

/* 0x00557360. Capture the manager and network before score/script calls. Parent
 * uninitialization, this initialization, scripts and queue insertion retain
 * their original order; already-active goals leave all state untouched. */
uint8_t thug_objective_activate(ThugObjective *o, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (methods(o)->is_active(o)) return 0;
    memory->temp_scope(memory->context,5);
    ThugObjectiveManager *manager = thug_objective_manager();
    o->value_60 = 0; ++o->activation_count;
    ThugNetworkState *network = thug_network_state;
    if (thug_script_has_flag(o->parameters,0x4599b58c)) {
        ThugPlayerIterator iterator;
        for (ThugPlayerState *player = thug_player_first(network,&iterator,0); player;
             player = thug_player_next(network,&iterator,0)) {
            ThugObjectComponent *component = thug_object_find_component((const ThugSkaterBody *)player->object,0xd262802f);
            ThugScore *score = (void *)(uintptr_t)word((const uint8_t *)component+0x18);
            thug_score_reset(score,diagnostics,memory);
        }
    }
    const uint32_t *parent = o->parent_id;
    ThugObjective *root = NULL;
    if (*parent) {
        do {
            if (!*parent) break;
            root = thug_objective_get(manager,*parent,1);
            parent = root->parent_id;
        } while (parent);
    }
    if (root) {
        if (o->unknown_14_to_1b[4] & 2) {
            double seconds = thug_platform_round_x87_single((double)(int32_t)root->timer*(double)0.001f);
            o->timer = thug_truncate_double_low_word(seconds)*1000u;
        } else thug_objective_reset_timer(o);
        if (methods(root)->is_initialized(root)) {
            thug_objective_uninitialize(root,0,0,diagnostics,memory);
            if (methods(o)->is_initialized(o)) {
                thug_objective_uninitialize(o,0,0,diagnostics,memory);
                thug_objective_initialize(o,diagnostics,memory);
            }
        }
    } else thug_objective_reset_timer(o);
    if (!methods(o)->is_initialized(o)) thug_objective_initialize(o,diagnostics,memory);
    o->flags &= 0x7f;
    thug_script_remove_unnamed_value(o->parameters,0x7100155d,memory);
    uint32_t script;
    if (thug_script_get_checksum(o->parameters,0x4999fb52,&script,0))
        thug_script_run_sync(script,o->parameters,NULL,0,diagnostics,memory);
    if (!thug_network_is_active(network)) o->flags |= 2;
    methods(o)->mark_active(o);
    thug_objective_manager_enqueue(manager,o);
    memory->temp_scope(memory->context,0);
    return 1;
}

/* 0x00557fc0. Both missing-goal paths return AL=0. Eligibility consults the
 * current global manager; last_goal belongs to the captured caller's manager. */
uint8_t thug_objective_manager_activate(ThugObjectiveManager *manager, uint32_t id, uint32_t allow_missing,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)allow_missing;
    ThugObjective *o = thug_objective_find(manager, &id);
    uint8_t activated = 0;
    if (o && !thug_objective_is_disabled(o)) {
        activated = methods(o)->activate(o, diagnostics, memory);
        if (activated && methods(o)->has_selection_flag(o) && !*o->parent_id)
            manager->last_goal = id;
    }
    return activated;
}

/* 0x00559230: GoalManager_ActivateGoal. Preserve the original callable ABI. */
uint32_t thug_script_goal_activate(ThugScriptStructure *parameters, ThugScriptInstance *script) {
    (void)script;
    ThugObjectiveManager *manager = thug_game_difficulty_settings(thug_game_context);
    uint32_t id;
    thug_script_get_checksum(parameters, 0xa1dc81f9, &id, 1);
    uint32_t allow_missing = thug_script_has_flag(parameters, 0x9ac8d54f) != 0;
    return thug_objective_manager_activate(manager, id, allow_missing,
        thug_event_services->diagnostics, thug_event_services->memory);
}

/* 0x00559290: GoalManager_DeactivateGoal. Success means the goal was found,
 * including when its virtual deactivation returns zero for an inactive goal. */
uint32_t thug_script_goal_deactivate(ThugScriptStructure *parameters, ThugScriptInstance *script) {
    (void)script;
    ThugObjectiveManager *manager = thug_game_difficulty_settings(thug_game_context);
    uint32_t id;
    thug_script_get_checksum(parameters, 0xa1dc81f9, &id, 1);
    ThugObjective *o = thug_objective_find(manager, &id);
    if (o) methods(o)->deactivate(o, 0, 1, thug_event_services->diagnostics, thug_event_services->memory);
    return o != NULL;
}

/* 0x005592f0: GoalManager_ClearLastGoal. */
uint32_t thug_script_goal_clear_last(ThugScriptStructure *parameters, ThugScriptInstance *script) {
    (void)parameters; (void)script;
    thug_game_difficulty_settings(thug_game_context)->last_goal = 0;
    return 1;
}

/* 0x00554030. The reserved-name branch really skips advancement as well as
 * the value write. Preserve this original nonterminating case explicitly. */
void thug_objective_clear_members(ThugScriptStructure *state) {
    for (ThugScriptComponent *c = thug_script_next_component(state, NULL); c;) {
        ThugScriptComponent *next = thug_script_next_component(state, c);
        if (c->name != 0xb3790f33) { c->value = 0; c = next; }
    }
}
/* 0x00554070. Only type10 members are traversed for grouped states. The
 * outer next pointer is captured before clearing a group. No values are freed. */
void thug_objective_clear_state(ThugObjective *o, const ThugMemory *memory) {
    if (thug_script_has_flag(o->state, 0xe462e527)) {
        for (ThugScriptComponent *c = thug_script_next_component(o->state, NULL); c;) {
            ThugScriptComponent *next = thug_script_next_component(o->state, c);
            if ((c->type_and_flags & 0xfe) == 0x14)
                thug_objective_clear_members((ThugScriptStructure *)(uintptr_t)c->value);
            c = next;
        }
    } else thug_objective_clear_members(o->state);
    o->completed_count = 0;
    thug_script_set_integer(o->parameters, 0xcf6cd3c1, 0, memory);
}
/* 0x00553e50. Missing children are tolerated here. Clear their link flag before
 * lookup, and read each next pointer after the recursive call. */
void thug_objective_reset_children(ThugObjective *o) {
    ThugObjectiveManager *manager = thug_objective_manager();
    for (ThugObjectiveChild *link = o->children; link && link->id; link = link->next) {
        link->completed = 0;
        ThugObjective *child = thug_objective_get(manager, link->id, 1);
        if (child) thug_objective_reset_children(child);
    }
}
/* 0x00554bd0. Active objectives deactivate through their actual virtual slot.
 * Unlike the reset helper, recursive uninitialization requires every child. */
void thug_objective_uninitialize(ThugObjective *o, uint32_t recursive, uint32_t depth,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (methods(o)->is_active(o)) methods(o)->deactivate(o, 1, 1, diagnostics, memory);
    uint32_t script;
    if (thug_script_get_checksum(o->parameters, 0xd4e0306a, &script, 0))
        thug_script_run_sync(script, o->parameters, NULL, 0, diagnostics, memory);
    o->flags &= 0xfe;
    if ((uint8_t)recursive) {
        ThugObjectiveManager *manager = thug_objective_manager();
        for (ThugObjectiveChild *link = o->children; link && link->id; link = link->next)
            thug_objective_uninitialize(thug_objective_get(manager, link->id, 1), recursive, depth + 1, diagnostics, memory);
    }
}
/* 0x00557560. Script calls and the optional root reinitialization precede
 * queue unlinking. An inactive objective returns without any mutation. */
uint8_t thug_objective_deactivate(ThugObjective *o, uint32_t unused, uint32_t reset_parent,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)unused;
    if (!methods(o)->is_active(o)) return 0;
    if (thug_script_has_flag(o->parameters, 0xb394c01c))
        thug_script_remove_name(o->parameters, 0x79704516, memory);
    methods(o)->mark_inactive(o);
    if (!thug_script_has_flag(o->parameters, 0xa36700ef)) thug_objective_clear_state(o, memory);
    thug_objective_reset_children(o);
    uint32_t script;
    if (thug_script_get_checksum(o->parameters, 0x01c92cac, &script, 0))
        thug_script_run_sync(script, o->parameters, NULL, 0, diagnostics, memory);
    if (!thug_script_has_flag(o->parameters, 0x38221df4))
        thug_script_remove_unnamed_value(o->parameters, 0x54d3cac1, memory);
    if (!thug_script_has_flag(o->parameters, 0xc309cad1)
        && !thug_script_has_flag(o->parameters, 0x38221df4)) {
        thug_script_run_sync(0x719ae783, o->parameters, NULL, 0, diagnostics, memory);
        if ((uint8_t)reset_parent && o->parent_id && *o->parent_id) {
            thug_objective_uninitialize(o, 0, 0, diagnostics, memory);
            ThugObjectiveManager *manager = thug_objective_manager();
            const uint32_t *id = o->parent_id;
            ThugObjective *parent = NULL;
            while (id && *id) { parent = thug_objective_get(manager, *id, 1); id = parent->parent_id; }
            if (parent && !methods(parent)->is_beaten(parent)) thug_objective_initialize(parent, diagnostics, memory);
        }
    }
    o->queue_node.next->previous = o->queue_node.previous;
    o->queue_node.previous->next = o->queue_node.next;
    o->queue_node.previous = &o->queue_node;
    o->queue_node.next = &o->queue_node;
    return 1;
}
