#include "stats.h"
/* 0x00580480. The owner must exist; its current modifier may be null. */
ThugStatModifier *thug_skater_stat_modifier(const ThugSkaterBody *body) {
    return body->modifier_owner->modifier;
}
#include "../platform/math.h"
#include <stddef.h>

_Static_assert(offsetof(ThugPlayerState, flags) == 0x1d0, "Player flags");
_Static_assert(offsetof(ThugNetworkState, players) == 0x11c, "Player list");
_Static_assert(offsetof(ThugGameContext, difficulty) == 0x38c, "Difficulty pointer");
_Static_assert(offsetof(ThugGameContext, stat_override) == 0x3d0, "Stat override");
_Static_assert(offsetof(ThugSkaterStats, values) == 0x290, "Stat values");
_Static_assert(offsetof(ThugSkaterBody, stat_modifier_selector) == 0x110, "Body modifier selector");
_Static_assert(offsetof(ThugSkaterState, stat_modifier_selector) == 0x28, "State modifier selector");
ThugNetworkState *thug_network_state;
/* 0x00533f90. Independent of the connection-based active-network predicate. */
uint32_t thug_network_flag_1(const ThugNetworkState *state) { return state->flags & 1; }
/* 0x005480c0, 0x00543300 and 0x005434b0. The last getter requires the
 * complete skater object behind the identifier-only public prefix. */
ThugConnectionState *thug_network_first_connection(const ThugNetworkState *state) { return state->first_connection; }
uint32_t thug_player_flag_1(const ThugPlayerState *player) { return player->flags & 1; }
uint32_t thug_player_network_index(const ThugPlayerState *player) {
    uint32_t index; __builtin_memcpy(&index,(const uint8_t *)player->object+0x2bc,4); return index;
}
/* 0x005845c0. Both additions use the low halfword; aliased counters add twice. */
uint16_t *thug_gameplay_add_points(ThugGameplayFlags *state, uint32_t amount) {
    uint8_t *p = (void *)state; uint32_t level; uint16_t value;
    __builtin_memcpy(&level,p+0x630,4);
    __builtin_memcpy(&value,p+0x5d8,2); value = (uint16_t)(value+amount); __builtin_memcpy(p+0x5d8,&value,2);
    uint8_t *target = (void *)((uintptr_t)p+(0x584+2*level));
    __builtin_memcpy(&value,target,2); value = (uint16_t)(value+amount); __builtin_memcpy(target,&value,2);
    return (uint16_t *)target;
}
/* 0x00584620. The level byte is updated before the total, including aliasing. */
void thug_gameplay_add_completion(ThugGameplayFlags *state) {
    uint8_t *p = (void *)state; uint32_t level; __builtin_memcpy(&level,p+0x630,4);
    ++*(uint8_t *)((uintptr_t)p+(0x5dc+level)); ++p[0x5ee];
}
ThugGameSettings *thug_game_settings;
ThugGameContext *thug_game_context;
ThugObjectLookupManager *thug_object_lookup_manager;
uint8_t thug_last_gameplay_flag;

/* 0x00456f90, 0x0044e4f0. These inspect stored state, without networking I/O. */
uint8_t thug_connection_flag_8(const ThugConnectionState *c) { return (c->flags >> 3) & 1; }
uint8_t thug_network_is_active(const ThugNetworkState *n) {
    if (!(n->flags & 12)) return 0;
    if (n->first_connection && !thug_connection_flag_8(n->first_connection)) return 1;
    return n->second_connection && !thug_connection_flag_8(n->second_connection);
}
/* 0x00543320, 0x00543490, 0x005433b0. Flag meanings remain unidentified. */
uint8_t thug_player_is_hidden(const ThugPlayerState *p) { return (p->flags >> 2) & 1; }
uint8_t thug_player_flag_80(const ThugPlayerState *p) { return (p->flags >> 7) & 1; }
uint8_t thug_player_flags_7800(const ThugPlayerState *p) { return (p->flags & 0x7800) != 0; }
/* 0x00537010. Sentinel player -1 terminates; a null player also returns null,
 * but retains its node in the iterator. A valid current node is required. */
ThugPlayerState *thug_player_next(const ThugNetworkState *n, ThugPlayerIterator *it, uint32_t include_hidden) {
    (void)n;
    for (;;) {
        ThugPlayerNode *next = it->node->next;
        it->node = (uintptr_t)next->player == UINT32_MAX ? NULL : next;
        ThugPlayerState *player = it->node ? it->node->player : NULL;
        if ((uint8_t)include_hidden || !player || !thug_player_is_hidden(player)) return player;
    }
}
/* 0x005372c0. Same first-node and hidden-player handling as the next method. */
ThugPlayerState *thug_player_first(const ThugNetworkState *n, ThugPlayerIterator *it, uint32_t include_hidden) {
    it->node = (ThugPlayerNode *)&n->players;
    return thug_player_next(n, it, include_hidden);
}
/* 0x00533070. Only AL is defined. */
uint8_t thug_network_slot(const ThugNetworkState *n) { return ((const uint8_t *)n)[0x38]; }
/* 0x0053aea0. The incoming identifier is truncated to sixteen bits. */
ThugPlayerState *thug_player_find(const ThugNetworkState *n, uint32_t id) {
    ThugPlayerIterator it = { 0, (ThugPlayerNode *)&n->players };
    ThugPlayerState *player = thug_player_next(n, &it, 0);
    while (player) {
        if (player->object && player->object->id == (uint16_t)id) return player;
        player = thug_player_next(n, &it, 0);
    }
    return NULL;
}
/* 0x00553220, 0x005532a0. Absent settings use the initialized zero. */
uint8_t thug_settings_flag(const ThugGameSettings *s, uint32_t name) {
    uint32_t value = 0;
    thug_script_get_boolean(&s->parameters, name, &value, 0); return value != 0;
}
uint32_t thug_settings_mode(const ThugGameSettings *s) {
    uint32_t value = 0;
    thug_script_get_checksum(&s->parameters, 0xa1dc81f9, &value, 0); return value;
}
/* 0x00553190. PUSH ECX initializes the output slot to this pointer. When the
 * setting is absent the disabled assert leaves that exact word in the slot. */
uint32_t thug_settings_player_count(const ThugGameSettings *s) {
    uint32_t value = (uint32_t)(uintptr_t)s;
    thug_script_get_boolean(&s->parameters, 0x6dc3d6f1, &value, 1); return value;
}
/* 0x00564d90, 0x00559050. Unknown or absent difficulty values map to one. */
ThugDifficultySettings *thug_game_difficulty_settings(const ThugGameContext *g) { return g->difficulty; }
uint32_t thug_game_difficulty(const ThugDifficultySettings *s, uint32_t force_default) {
    uint32_t name = (uint8_t)force_default ? 0x4da4937b : thug_settings_mode(thug_game_settings), value;
    if (!thug_script_get_integer(s->parameters, name, &value, 0)) return 1;
    return value <= 2 ? value : 1;
}
/* 0x005651f0, 0x005a1180. Preserve the original unsigned count comparison. */
uint8_t thug_game_is_multiplayer(const ThugGameContext *g) {
    (void)g;
    return thug_network_is_active(thug_network_state) || thug_settings_player_count(thug_game_settings) > 1;
}
uint8_t thug_game_is_split_screen(uint32_t unused_0, uint32_t unused_1) {
    (void)unused_0; (void)unused_1;
    return thug_game_is_multiplayer(thug_game_context) && !thug_network_is_active(thug_network_state);
}
/* 0x00565bb0. The flag's textual name is not yet identified. Collision events
 * use this predicate to skip a flagged node in an active multiplayer context. */
uint32_t thug_script_multiplayer_gate(const ThugScriptStructure *node) {
    if (!thug_script_has_flag(node, 0x68910ac6)) return 0;
    return thug_network_is_active(thug_network_state)
        || thug_settings_player_count(thug_game_settings) > 1;
}
/* 0x00584cc0. The argument is a script name, not the bit index itself. */
uint8_t thug_gameplay_flag(const ThugGameplayFlags *flags, uint32_t name) {
    uint32_t index = thug_script_get_global_integer(name, 0), word;
    uintptr_t at = (uintptr_t)flags + 0x5f0 + (uint32_t)((int32_t)index >> 5) * 4;
    const uint8_t *in = (const uint8_t *)at;
    uint8_t *out = (uint8_t *)&word;
    for (unsigned i = 0; i < 4; ++i) out[i] = in[i];
    thug_last_gameplay_flag = (word & (UINT32_C(1) << (index & 31))) != 0;
    return thug_last_gameplay_flag;
}
/* 0x005843a0. Unlike the getter, this takes an index directly and does not
 * update 0x007ce4fd. Signed word indexing matches SAR EDX,5. */
void thug_gameplay_flag_set(ThugGameplayFlags *flags, uint32_t index) {
    uintptr_t at = (uintptr_t)flags + 0x5f0 + (uint32_t)((int32_t)index >> 5) * 4;
    uint8_t *bytes = (uint8_t *)at;
    uint32_t word;
    uint8_t *copy = (uint8_t *)&word;
    for (unsigned i = 0; i < 4; ++i) copy[i] = bytes[i];
    word |= UINT32_C(1) << (index & 31);
    for (unsigned i = 0; i < 4; ++i) bytes[i] = copy[i];
}

static void *table_find(const ThugObjectLookupTable *table, uint32_t key) {
    uint32_t slot = key & ((UINT32_C(1) << (table->shift & 31)) - 1);
    ThugObjectLookupNode *node = (ThugObjectLookupNode *)((uintptr_t)table->buckets + slot * 12);
    for (; node; node = node->next) if (node->key == key && node->value) return node->value;
    return NULL;
}
/* 0x00462050, 0x00462120, 0x004619f0. Null-valued entries do not match. */
void *thug_object_table_find(const ThugObjectLookupTable *table, const uint32_t *key, uint32_t unused) {
    (void)unused; return table_find(table, *key);
}
void *thug_object_manager_find(const ThugObjectLookupManager *manager, uint32_t key) {
    void *value = table_find(manager->primary, key);
    return value ? value : thug_object_table_find(manager->secondary, &key, 1);
}
void *thug_object_find_global(const void *unused, uint32_t key) {
    (void)unused; return thug_object_manager_find(thug_object_lookup_manager, key);
}

/* 0x00580490. Multiplayer substitutions precede gameplay flags and the +3 bonus. */
double thug_skater_stat(const ThugSkaterStats *s, uint32_t index) {
    float value = thug_game_context->stat_override;
    if (value == 0) {
        value = s->values[index];
        if (value == -1) value = (float)thug_script_get_global_number(0x6357d57c, 0);
    }
    if (thug_network_is_active(thug_network_state)) {
        const ThugPlayerState *player = thug_player_find(thug_network_state, s->object_id);
        value = player && thug_player_flag_80(player) ? 1 :
            player && thug_player_flags_7800(player) ? 6 : 10;
    } else if (thug_game_is_split_screen(0, 0)) {
        const ThugPlayerState *player = thug_player_find(thug_network_state, s->object_id);
        if (player && thug_player_flag_80(player)) value = 1;
    }
    if (thug_gameplay_flag(thug_game_context->gameplay_flags,
            thug_script_get_global_integer(0x6b0f24bc, 0))) value = 15;
    return s->modifier_owner->modifier->active ? thug_platform_round_x87_single((double)value + 3) : value;
}
static double interpolate(const ThugScriptPair *pair, double stat) {
    double value = thug_platform_round_x87_single((double)pair->y - pair->x);
    value = thug_platform_round_x87_single(value * stat);
    value = thug_platform_round_x87_single(value * (double)0.1f);
    return thug_platform_round_x87_single(value + pair->x);
}
/* 0x005805b0. Keep each x87 operation and each float-local store in order. */
double thug_skater_evaluate_stat_parameter(const ThugSkaterStats *s, const ThugScriptStructure *parameters) {
    ThugScriptPair base, modifier;
    thug_script_pair_initialize(&base); thug_script_pair_initialize(&modifier);
    thug_script_get_pair(parameters, 0, &base, 0);
    uint32_t index;
    double stat = thug_script_get_integer(parameters, 0, &index, 0) ? thug_skater_stat(s, index) : 10;
    float value = (float)interpolate(&base, stat);
    uint8_t state_selector = s->physics->state->stat_modifier_selector;
    if ((s->physics->body->stat_modifier_selector ? state_selector != 0 : state_selector == 0)
            && thug_script_get_pair(parameters, 0x9016b4e7, &modifier, 0)) {
        double factor = interpolate(&modifier, thug_skater_stat(s, 6));
        if (factor < 0) factor = 0;
        else if (factor > 1) factor = 1;
        value = (float)thug_platform_round_x87_single(factor * value);
    }
    uint32_t difficulty = thug_game_difficulty(thug_game_difficulty_settings(thug_game_context), 0);
    if (thug_settings_flag(thug_game_settings, 0x5a2c589a)) ++difficulty;
    if (difficulty != 1) {
        thug_script_pair_initialize(&modifier);
        if (thug_script_get_pair(parameters, 0xba8fb854, &modifier, 0)) {
            if (difficulty == 0) value = (float)thug_platform_round_x87_single((double)modifier.x * value);
            else if (difficulty == 2) value = (float)thug_platform_round_x87_single((double)modifier.y * value);
        }
    }
    float limit;
    if (thug_script_get_float(parameters, 0x8069179f, &limit, 0)) {
        if (base.x < base.y) { if (value > limit) return limit; }
        else if (value < limit) return limit;
    }
    return value;
}
/* 0x00580790. Select the body's parameter set, then fall back to a global struct. */
double thug_skater_stat_parameter(const ThugSkaterStats *s, uint32_t name) {
    const ThugSkaterBody *body = thug_object_find_global(NULL, s->object_id);
    const ThugScriptStructure *parameters = thug_skater_parameter_set(body);
    ThugScriptStructure *entry = NULL;
    if (!thug_script_get_structure(parameters, name, &entry, 0)) entry = thug_script_get_global_structure(name, 0);
    return thug_skater_evaluate_stat_parameter(s, entry);
}
/* 0x005807f0. A missing nested structure passes the initialized null through
 * to the evaluator; this wrapper has no global-parameter fallback. */
double thug_skater_structure_stat_parameter(const ThugSkaterStats *s, uint32_t name, const ThugScriptStructure *parameters) {
    ThugScriptStructure *entry = NULL;
    thug_script_get_structure(parameters,name,&entry,0);
    return thug_skater_evaluate_stat_parameter(s,entry);
}
