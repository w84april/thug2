#ifndef THUG_GAME_STATS_H
#define THUG_GAME_STATS_H
#include "skater.h"
#include "../core/lookup.h"

/* Only prefixes/fields reached by the recovered stat path are named here. */
typedef struct { uint8_t unknown[0x1e84]; uint32_t flags; } ThugConnectionState;
typedef struct { uint8_t unknown[0x14]; uint32_t id; } ThugObjectIdentifier;
typedef struct {
    uint8_t unknown_0_to_13[0x14];
    ThugObjectIdentifier *object;
    uint8_t unknown_18_to_1cf[0x1b8];
    uint32_t flags;
} ThugPlayerState;
typedef struct ThugPlayerNode {
    uint32_t unknown_0;
    ThugPlayerState *player;
    uint32_t unknown_8;
    struct ThugPlayerNode *next;
} ThugPlayerNode;
typedef struct { uint32_t unknown_0; ThugPlayerNode *node; } ThugPlayerIterator;
typedef struct {
    uint32_t flags;
    ThugConnectionState *first_connection, *second_connection;
    uint8_t unknown_c_to_11b[0x110];
    ThugPlayerNode players;
} ThugNetworkState;
typedef struct { uint32_t unknown_0; ThugScriptStructure parameters; } ThugGameSettings;
typedef struct ThugObjectiveLink ThugObjectiveLink;
typedef struct {
    int32_t objective_count;
    ThugObjectiveLink *objectives;
    uint32_t unknown_8;
    ThugObjectiveLink *cached_objective;
    int32_t cached_index;
    uint8_t unknown_14_to_2b[0x18];
    uint32_t last_goal;
    uint8_t unknown_30_to_37[8];
    uint32_t value_38, value_3c, value_40;
    uint8_t unknown_44_to_397[0x354];
    ThugScriptStructure *parameters;
} ThugDifficultySettings;
typedef struct { uint8_t unknown[0x5f0]; uint32_t words[]; } ThugGameplayFlags;
typedef struct ThugSkaterNode {
    uint32_t unknown_0;
    ThugSkaterBody *body;
    uint32_t unknown_8;
    struct ThugSkaterNode *next;
} ThugSkaterNode;
typedef struct {
    uint8_t unknown_0_to_1f[0x20];
    ThugGameplayFlags *gameplay_flags;
    ThugObjectTransform *rail_transform;
    uint8_t unknown_28_to_33[0xc];
    ThugSkaterNode *skaters;
    uint8_t unknown_38_to_377[0x340];
    uint32_t identifier_378;
    uint8_t unknown_37c_to_38b[0x10];
    ThugDifficultySettings *difficulty;
    uint8_t unknown_390_to_3cf[0x40];
    float stat_override;
} ThugGameContext;
typedef struct {
    uint32_t unknown_0, unknown_4;
    ThugObjectLookupTable *primary, *secondary;
    ThugObjectLookupTable *listeners;
} ThugObjectLookupManager;
typedef struct { float remaining; uint8_t unknown_4_to_73[0x70]; uint8_t active; } ThugStatModifier;
typedef struct ThugStatModifierOwner { uint8_t unknown[0x18]; ThugStatModifier *modifier; } ThugStatModifierOwner;
/* 0x00504b40 calls the stat path with its body pointer: stats belong to that
 * same skater object, not a separate component. Keep the old API type as an alias. */
typedef ThugSkaterBody ThugSkaterStats;

/* Lifted globals: 7cce14, 7ce470, 7ce478, 6f0fc0 and 7ce4fd respectively. */
extern ThugNetworkState *thug_network_state;
extern ThugGameSettings *thug_game_settings;
extern ThugGameContext *thug_game_context;
extern ThugObjectLookupManager *thug_object_lookup_manager;
extern uint8_t thug_last_gameplay_flag;

uint8_t thug_connection_flag_8(const ThugConnectionState *);
uint8_t thug_network_is_active(const ThugNetworkState *);
uint32_t thug_network_flag_1(const ThugNetworkState *);
ThugConnectionState *thug_network_first_connection(const ThugNetworkState *);
uint32_t thug_player_flag_1(const ThugPlayerState *);
uint32_t thug_player_network_index(const ThugPlayerState *);
uint8_t thug_player_is_hidden(const ThugPlayerState *);
uint8_t thug_player_flag_80(const ThugPlayerState *);
uint8_t thug_player_flags_7800(const ThugPlayerState *);
ThugPlayerState *thug_player_next(const ThugNetworkState *, ThugPlayerIterator *, uint32_t include_hidden);
ThugPlayerState *thug_player_first(const ThugNetworkState *, ThugPlayerIterator *, uint32_t include_hidden);
uint8_t thug_network_slot(const ThugNetworkState *);
ThugPlayerState *thug_player_find(const ThugNetworkState *, uint32_t id);
uint8_t thug_settings_flag(const ThugGameSettings *, uint32_t name);
uint32_t thug_settings_mode(const ThugGameSettings *);
uint32_t thug_settings_player_count(const ThugGameSettings *);
ThugDifficultySettings *thug_game_difficulty_settings(const ThugGameContext *);
uint32_t thug_game_difficulty(const ThugDifficultySettings *, uint32_t force_default);
uint8_t thug_game_is_multiplayer(const ThugGameContext *);
uint8_t thug_game_is_split_screen(uint32_t unused_0, uint32_t unused_1);
uint32_t thug_script_multiplayer_gate(const ThugScriptStructure *);
uint8_t thug_gameplay_flag(const ThugGameplayFlags *, uint32_t name);
void thug_gameplay_flag_set(ThugGameplayFlags *, uint32_t index);
uint16_t *thug_gameplay_add_points(ThugGameplayFlags *, uint32_t amount);
void thug_gameplay_add_completion(ThugGameplayFlags *);
void *thug_object_table_find(const ThugObjectLookupTable *, const uint32_t *key, uint32_t unused);
void *thug_object_manager_find(const ThugObjectLookupManager *, uint32_t key);
void *thug_object_find_global(const void *unused, uint32_t key);
/* Caller supplies valid indices, loaded parameter structures and complete object
 * links. These functions preserve the original unchecked internal contracts. */
double thug_skater_stat(const ThugSkaterStats *, uint32_t index);
ThugStatModifier *thug_skater_stat_modifier(const ThugSkaterBody *);
double thug_skater_evaluate_stat_parameter(const ThugSkaterStats *, const ThugScriptStructure *);
double thug_skater_stat_parameter(const ThugSkaterStats *, uint32_t name);
double thug_skater_structure_stat_parameter(const ThugSkaterStats *, uint32_t name, const ThugScriptStructure *);
#endif
