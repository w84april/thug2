#ifndef THUG_GAME_SCORE_H
#define THUG_GAME_SCORE_H
#include "objectives.h"
typedef struct { void **items; uint32_t capacity; int32_t count; } ThugScoreEntryArray;
typedef struct { float unknown_0, x, y; } ThugBalanceCurvePoint;
typedef struct {
    uint8_t unknown_0_to_13[0x14];
    uint32_t value_14;
    uint8_t unknown_18_to_27[0x10];
    uint32_t value_28;
    uint8_t unknown_2c_to_4b[0x20];
    ThugScoreEntryArray entries;
    uint32_t unknown_58, value_5c, value_60, unknown_64, index_68, index_6c, unknown_70;
    uint8_t unknown_74, special_colors[3][4], unknown_81_to_87[7];
    float special_interpolator_rate;
    uint8_t debug_score, unknown_8d[7];
    ThugBalanceCurvePoint balance_curve[20];
    float balance_curve_step;
    uint32_t unknown_188;
    float balance_x, balance_y, balance_angle;
    uint32_t unknown_198;
    float balance_position_x, balance_position_y;
    uint32_t unknown_1a4;
    float manual_position_x, manual_position_y;
    uint8_t unknown_1b0_to_b73[0x9c4];
    uint32_t values_b74[625], unknown_1538, value_153c, unknown_1540, value_1544, value_1548;
    float multiplier_154c;
} ThugScore;
typedef struct { ThugObjectComponent base; uint32_t unknown_14, value_18; } ThugScoreEventComponent;
ThugSkaterBody *thug_game_skater_by_id(const ThugGameContext *, uint32_t id);
uint32_t thug_skater_screen_id(const ThugSkaterBody *);
void thug_score_entries_clear(ThugScoreEntryArray **, const ThugMemory *);
void thug_score_combo_clear(ThugScore *, const ThugMemory *);
void thug_score_update_combo_text(ThugScore *, uint32_t clear, const ThugDiagnostics *, const ThugMemory *);
void thug_score_update_numeric_text(ThugScore *, int32_t points, float multiplier, const ThugDiagnostics *, const ThugMemory *);
void thug_score_reset(ThugScore *, const ThugDiagnostics *, const ThugMemory *);
void thug_score_set_special(ThugScore *, uint32_t enabled, const ThugDiagnostics *, const ThugMemory *);
void thug_score_recalculate(ThugScore *, const ThugDiagnostics *, const ThugMemory *);
void thug_score_add_balance(ThugScore *, uint32_t points, const ThugDiagnostics *, const ThugMemory *);
void thug_score_update_spin(ThugScore *,int32_t angle,const ThugDiagnostics *,const ThugMemory *);
void thug_score_update_spin_if_trick(ThugScore *,int32_t angle,const ThugDiagnostics *,const ThugMemory *);
void thug_score_display_balance(ThugScore *, uint32_t enabled, float value, uint32_t manual, const ThugDiagnostics *, const ThugMemory *);
void thug_score_display_balance_normal(ThugScore *, uint32_t enabled, float value, const ThugDiagnostics *, const ThugMemory *);
void thug_score_display_balance_manual(ThugScore *, uint32_t enabled, float value, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_score_current(const ThugScore *);
/* This uses the same original indexed-list template as the objective manager;
 * only its first five words are accessed. Payload pointers are opaque here. */
void thug_score_map_remove(ThugObjectiveManager *, const uint32_t *key, const ThugMemory *);
void thug_score_map_clear(ThugObjectiveManager **, const ThugMemory *);
void thug_score_configure_special(ThugScore *);
void thug_score_event_reset(ThugScoreEventComponent *, const ThugDiagnostics *, const ThugMemory *);
#endif
