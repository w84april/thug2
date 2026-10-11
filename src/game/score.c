#include "score.h"
#include "font.h"
#include "drawing.h"
#include "animation.h"
#include "balance.h"
#include "../core/checksum.h"
#include "../core/number.h"
#include "../script/delivery.h"
#include "../script/schedule.h"
#include "../script/values.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(offsetof(ThugScore, entries) == 0x4c, "Trick entries");
_Static_assert(offsetof(ThugScore, special_colors) == 0x75, "Special meter colors");
_Static_assert(offsetof(ThugScore, special_interpolator_rate) == 0x88, "Special rate");
_Static_assert(offsetof(ThugScore, values_b74) == 0xb74, "Combo history");
_Static_assert(offsetof(ThugScore, multiplier_154c) == 0x154c, "Combo multiplier");
_Static_assert(offsetof(ThugScore, balance_curve) == 0x94, "Balance curve");
_Static_assert(offsetof(ThugScore, balance_curve_step) == 0x184, "Balance curve spacing");
_Static_assert(offsetof(ThugScore, manual_position_x) == 0x1a8, "Manual meter position");
static uint32_t word(const void *at) { uint32_t v; __builtin_memcpy(&v, at, 4); return v; }
/* 0x00561b40. The alternate score counts owned objects for the signed player ID. */
uint32_t thug_score_current(const ThugScore *score) {
    if (!thug_network_flag_1(thug_network_state)) return word((const uint8_t *)score+0xc);
    ThugGameSettings *settings = thug_game_settings;
    if (!thug_script_get_global_integer(0x2f507903,0) && !thug_settings_flag(settings,0x11941568))
        return word((const uint8_t *)score+0xc);
    int16_t id; __builtin_memcpy(&id,(const uint8_t *)score+8,2);
    return thug_objective_owned_count(thug_objective_objects,(uint32_t)(int32_t)id);
}
/* 0x00561890. The original requires the numeric widget to exist. Its lookup
 * reference is released before formatting, text replacement and notification. */
void thug_score_update_numeric_text(ThugScore *score, int32_t points, float multiplier,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    int16_t skater_id; __builtin_memcpy(&skater_id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)skater_id);
    uint32_t screen = body ? thug_skater_screen_id(body) : 0;
    ThugObjectReference reference; thug_ui_find(&reference,screen+0xf4d3a70e,0);
    ThugUiText *widget = (ThugUiText *)reference.object;
    thug_object_reference_destroy(&reference);
    char text[128];
    if (!points) { text[0] = ' '; text[1] = 0; }
    else {
        int32_t integer = (int32_t)thug_truncate_low_word(multiplier);
        const char *in = thug_text_integer(points); char *out = text;
        while ((*out = *in++)) ++out;
        if (multiplier != 0) {
            *out++ = ' '; *out++ = 'X'; *out++ = ' ';
            if ((double)multiplier == (double)integer) thug_text_signed_decimal(out,integer);
            else thug_text_fixed_one(out,multiplier);
        }
    }
    thug_ui_set_text(widget,text,memory);
    thug_script_run_sync(0xa611bb15,NULL,NULL,0,diagnostics,memory);
}
static void score_word(ThugScore *score, uint32_t offset, uint32_t value) {
    __builtin_memcpy((uint8_t *)score+offset,&value,4);
}
static char *spin_copy(char *out,const char *text) {
    while((*out=*text++))++out;
    return out;
}
/* 0x00563f30. Angle storage and Cab renaming precede the increase test.
 * Preserve live entry reads after diagnostic/UI callbacks and the original
 * fixed sprintf formats; valid entry strings fit their original buffers. */
void thug_score_update_spin(ThugScore *score,int32_t angle,const ThugDiagnostics *d,const ThugMemory *m) {
    if(!score->value_5c||(int32_t)score->index_6c<0)return;
    int16_t id;__builtin_memcpy(&id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body=thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    uint8_t flipped=thug_animation_component_all_flipped((void *)thug_object_find_component(body,0x7149b753));
    uint32_t magnitude=angle<0?0u-(uint32_t)angle:(uint32_t)angle;
    uint32_t slop=thug_truncate_double_low_word(thug_skater_get_parameter(0x50c5cc2f,0,NULL));
    int32_t half_turns=(int32_t)(magnitude+slop)/180;
    uint32_t side=((angle>=0)==!!flipped)?0:1;
    static const char *const sides[]={"FS","BS","FS Cab","BS Cab"};
    uint8_t *entry=score->entries.items[score->index_6c];
    __builtin_memcpy(entry+12,&angle,4);
    entry=score->entries.items[score->index_6c];
    uint32_t name=thug_crc32_string((const char *)entry+0x1c);
    uint8_t renamed=0;
    if(name==0x28c6399c||name==0x8bf1b0cb||name==0x428485bb) {
        if(half_turns==1) { __builtin_memcpy(entry+0x1c,"Half\\_Cab",10);renamed=1; }
        else if(half_turns==2) { __builtin_memcpy(entry+0x1c,"Cabalerial",11);renamed=1; }
        else if(half_turns>2) { entry[0x1c]=0;side+=2; }
    }
    entry=score->entries.items[score->index_6c];
    if((int32_t)word(entry+8)>=half_turns)return;
    if(score->debug_score&&d&&d->print)
        d->print(d->context,"New spin value %d:\n",(int32_t)((uint32_t)half_turns*180));
    void **slot=score->entries.items+score->index_6c;
    entry=*slot;
    if(word(entry+0x10)==0x9b65d7b8&&half_turns%2==1)side^=1;
    uint32_t flags=word(entry+0x18);
    uint32_t more=(int32_t)((uint32_t)score->entries.count-1)>(int32_t)score->index_6c;
    uint32_t color=flags&0x80?3:flags&0x20?2:0;
    entry=*slot;
    char *out=(char *)entry+0x5c;
    if(color) { *out++='\\';*out++='c';*out++=(char)('0'+color); }
    out=spin_copy(out,sides[side]);out=spin_copy(out,"\\_");
    uint32_t degrees=(uint32_t)half_turns*180;
    if(!renamed) { thug_text_signed_decimal(out,(int32_t)degrees);while(*out)++out;out=spin_copy(out,"\\_"); }
    out=spin_copy(out,(const char *)entry+0x1c);
    if(color)out=spin_copy(out,"\\c0");
    if(more)out=spin_copy(out,"\\_+ ");
    *out=0;
    thug_score_update_combo_text(score,0,d,m);
    entry=score->entries.items[score->index_6c];__builtin_memcpy(entry+8,&half_turns,4);
    thug_score_recalculate(score,d,m);
    ThugTimedTricks *tricks=(void *)thug_object_find_component(body,0x4ff8dac6);
    float spin=(float)(int32_t)degrees;uint32_t spin_bits;__builtin_memcpy(&spin_bits,&spin,4);
    thug_timed_tricks_set_spin(tricks,spin_bits);
    uint32_t points=score->value_14;float multiplier;__builtin_memcpy(&multiplier,&score->value_60,4);
    score_word(score,0x10,0);
    thug_score_update_numeric_text(score,(int32_t)points,multiplier,d,m);
    thug_object_broadcast_event((ThugReferencedObject *)body,0x68b887bb,NULL,0,d,m);
}
/* 0x00564be0. Separator entries do not receive rotation scoring. */
void thug_score_update_spin_if_trick(ThugScore *score,int32_t angle,const ThugDiagnostics *d,const ThugMemory *m) {
    if(score->value_5c&&(int32_t)score->index_6c>=0&&!(word((uint8_t *)score->entries.items[score->index_6c]+0x18)&2))
        thug_score_update_spin(score,angle,d,m);
}
/* 0x00563080. Valid curve indices select adjacent points. Required sprite and
 * child lookups retain the original unchecked internal lifetime contract. */
void thug_score_display_balance(ThugScore *score, uint32_t enabled, float value, uint32_t manual,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    int16_t id; __builtin_memcpy(&id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    ThugObjectReference reference;
    thug_ui_find(&reference,thug_skater_screen_id(body)+0xa4db8a4b,0);
    ThugUiSprite *widget = (void *)reference.object;
    thug_object_reference_destroy(&reference);
    uint32_t active = 0;
    thug_ui_object_get_integer(&widget->layout.element.base,0xc22eb9a0,&active);
    if ((uint8_t)enabled != !!active) {
        ThugScriptStructure *parameters = thug_script_structure_allocate(8,memory);
        if (parameters) thug_script_structure_initialize(parameters);
        thug_script_set_checksum(parameters,0x40c698af,thug_skater_screen_id(body)+0xa4db8a4b,memory);
        thug_script_run_sync((uint8_t)enabled ? 0xba95da16 : 0x58783b40,parameters,NULL,0,diagnostics,memory);
        if (parameters) {
            thug_script_structure_destroy(parameters,memory); thug_script_structure_free(parameters,memory);
        }
    }
    thug_ui_object_set_checksum(&widget->layout.element.base,0x863a07e2,
        (uint8_t)manual ? 0xef24413b : 0x530be001,memory);
    double magnitude = __builtin_fabs((double)value);
    double inverse = thug_platform_round_x87_single(1.0 / score->balance_curve_step);
    int32_t index = (int32_t)thug_truncate_double_low_word(thug_platform_round_x87_single(inverse*magnitude));
    double distance = thug_platform_round_x87_single(magnitude -
        thug_platform_multiply_x87_single(index,score->balance_curve_step));
    const ThugBalanceCurvePoint *point = score->balance_curve+index;
    double x = thug_platform_round_x87_single((double)point[1].x-point[0].x);
    x = thug_platform_round_x87_single(x*inverse); x = thug_platform_round_x87_single(x*distance);
    score->balance_x = (float)thug_platform_round_x87_single(x+point[0].x);
    double y = thug_platform_round_x87_single((double)point[1].y-point[0].y);
    y = thug_platform_round_x87_single(y*inverse); y = thug_platform_round_x87_single(y*distance);
    score->balance_y = (float)thug_platform_round_x87_single(y+point[0].y);
    score->balance_angle = (float)thug_platform_round_x87_single((double)value * -45.0);
    ThugUiSprite *child = (void *)widget->layout.element.children.object;
    if ((uint8_t)manual) {
        thug_ui_set_position(&widget->layout,score->manual_position_x,score->manual_position_y,1);
        thug_ui_sprite_set_rotation(widget,-90,1);
    } else {
        thug_ui_set_position(&widget->layout,score->balance_position_x,score->balance_position_y,1);
        thug_ui_sprite_set_rotation(widget,0,1);
    }
    y = thug_platform_round_x87_single((double)widget->layout.height * 0.5);
    y = thug_platform_round_x87_single(y+score->balance_y);
    if ((uint8_t)manual) y = thug_platform_round_x87_single(y+50.0);
    float child_y = (float)y;
    x = thug_platform_round_x87_single((double)widget->layout.width * 0.5);
    if ((uint8_t)manual) x = thug_platform_round_x87_single(x-80.0);
    x = thug_platform_round_x87_single(value >= 0 ? x+score->balance_x : x-score->balance_x);
    thug_ui_set_position(&child->layout,(float)x,child_y,1);
    thug_ui_sprite_set_rotation(child,-score->balance_angle,1);
}
/* 0x00563370 and 0x00563390. */
void thug_score_display_balance_normal(ThugScore *score, uint32_t enabled, float value,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_score_display_balance(score,enabled,value,0,diagnostics,memory);
}
void thug_score_display_balance_manual(ThugScore *score, uint32_t enabled, float value,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_score_display_balance(score,enabled,value,1,diagnostics,memory);
}
/* 0x00562760. Compare and store the raw low byte, then broadcast only changes. */
void thug_score_set_special(ThugScore *score, uint32_t enabled,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (score->unknown_74 == (uint8_t)enabled) return;
    score->unknown_74 = (uint8_t)enabled;
    int16_t id; __builtin_memcpy(&id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    if (body) thug_object_broadcast_event((ThugReferencedObject *)body,
        score->unknown_74 ? 0xd0cd8081 : 0x7ccf5ee2,NULL,0,diagnostics,memory);
}
static double combo_value(const ThugScore *score) {
    float multiplier; __builtin_memcpy(&multiplier,&score->value_60,4);
    return thug_platform_multiply_x87_single((int32_t)score->value_14,multiplier);
}
/* 0x00562e40. Valid entries have nonnegative repetition/spin table indices.
 * Integer products wrap before signed division. Diagnostic/event callbacks
 * may change the score, entry count or multiplier before subsequent reads. */
void thug_score_recalculate(ThugScore *score,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!score->value_5c) { score_word(score,0x24,0); score_word(score,0x20,0); return; }
    static const uint32_t spins[] = {2,3,4,5,6,7}, repetitions[] = {100,75,50,25,10};
    uint32_t multiplier = 2;
    score->value_14 = 0;
    for (int32_t i = 0; i < (int32_t)score->value_5c; ++i) {
        const uint8_t *entry = score->entries.items[i];
        uint32_t flags = word(entry+0x18);
        if (flags & 2) multiplier = 2;
        else if (!i || (word((const uint8_t *)score->entries.items[i-1]+0x18) & 2)) {
            int32_t spin = (int32_t)word(entry+8);
            multiplier = flags & 256 ? (uint32_t)spin+1 : spin < 6 ? spins[spin] : 7;
        }
        int32_t repeat = (int32_t)word(entry+4);
        uint32_t reduction = repeat < 5 ? repetitions[repeat] : 10;
        int32_t value = (int32_t)(reduction * multiplier * word(entry)) / 200;
        if (word(entry+0x14)) value = (int32_t)((uint32_t)value * 120) / 100;
        if (((const uint8_t *)score)[0x8c] && diagnostics && diagnostics->print)
            diagnostics->print(diagnostics->context,"base %d reduction mult %.2f spin mult %.1f score = %i %s\n",
                (int32_t)word(entry),thug_platform_multiply_x87_single((int32_t)reduction,(double)0.01f),
                thug_platform_multiply_x87_single((int32_t)multiplier,0.5),value,(const char *)entry+0x1c);
        score->value_14 += (uint32_t)value;
    }
    if (((const uint8_t *)score)[0x8c] && diagnostics && diagnostics->print)
        diagnostics->print(diagnostics->context,"   total %d\n",(int32_t)score->value_14);
    if (thug_script_get_global_integer(0xb23d1fb5,0)) {
        double value = combo_value(score);
        int32_t previous = (int32_t)word((const uint8_t *)score+0x24);
        if (value > previous) {
            score->unknown_70 += thug_truncate_double_low_word(thug_platform_round_x87_single(value-previous));
            if ((int32_t)score->unknown_70 < 0) {
                thug_score_set_special(score,0,diagnostics,memory);
                score->unknown_70 = 0;
            }
            if ((int32_t)score->unknown_70 >= 3000) {
                thug_score_set_special(score,1,diagnostics,memory);
                score->unknown_70 = 3000;
            }
        }
    }
    uint32_t total = thug_truncate_double_low_word(combo_value(score));
    score_word(score,0x20,total); score_word(score,0x24,total);
}
/* 0x00564270. The current balance trick stops accumulating after ten trailing
 * nonseparator entries or the original score/component gates. */
void thug_score_add_balance(ThugScore *score, uint32_t points,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    int32_t count = (int32_t)score->value_5c;
    if (count <= 0) return;
    const uint8_t *last = score->entries.items[count-1];
    if (!last[0x1c]) return;
    int32_t consecutive = 0;
    for (int32_t i = count-1; i > 0; --i) {
        if (word((const uint8_t *)score->entries.items[i]+0x18) & 2) break;
        ++consecutive;
    }
    if (consecutive > 10 || (!(word(last+0x18) & 2) && (int32_t)word(last) > 20000)) return;
    int16_t id; __builtin_memcpy(&id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    const uint8_t *component = (const void *)thug_object_find_component(body,0x9f9cc949);
    if (component && component[0x1c]) return;
    uint8_t *entry = score->entries.items[score->value_5c-1];
    uint32_t base = word(entry)+points; __builtin_memcpy(entry,&base,4);
    thug_score_recalculate(score,diagnostics,memory);
    thug_score_update_combo_text(score,0,diagnostics,memory);
    int32_t value = (int32_t)score->value_14;
    float multiplier; __builtin_memcpy(&multiplier,&score->value_60,4);
    score_word(score,0x10,0);
    thug_score_update_numeric_text(score,value,multiplier,diagnostics,memory);
}
/* 0x00564a10. Both history arrays, owned lists, screen text, special state and
 * the local score component reset in the original order. */
void thug_score_reset(ThugScore *score, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!thug_game_context) return;
    int16_t id; __builtin_memcpy(&id,(uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    if (diagnostics && diagnostics->print) diagnostics->print(diagnostics->context,"Score::RESET ...............\n");
    score_word(score,0x1538,0); score_word(score,0x1540,0);
    for (uint32_t i = 0; i < 625; ++i) score_word(score,0x1b0+i*4,0);
    score->value_153c = score->value_1548 = score->value_1544 = 0;
    for (uint32_t i = 0; i < 625; ++i) score->values_b74[i] = 0;
    score->multiplier_154c = 1;
    thug_score_combo_clear(score,memory);
    ThugObjectiveManager *map = (void *)((uint8_t *)score+0x38);
    thug_score_map_clear(&map,memory);
    if (body && ((uint8_t *)body)[0xbc]) {
        thug_score_update_combo_text(score,0,diagnostics,memory);
        thug_score_update_numeric_text(score,0,0,diagnostics,memory);
    }
    uint32_t mode = thug_settings_mode(thug_game_settings);
    score_word(score,0xc,mode == 0xbff33600 || thug_settings_mode(thug_game_settings) == 0x3d6d444f ? 100 : 0);
    score->value_14 = 0; score_word(score,0x20,0); score_word(score,0x24,0);
    score_word(score,0x70,0); score_word(score,0x34,0);
    if (score->unknown_74) {
        score->unknown_74 = 0;
        __builtin_memcpy(&id,(uint8_t *)score+8,2);
        body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
        if (body) thug_object_broadcast_event((ThugReferencedObject *)body,
            score->unknown_74 ? 0xd0cd8081 : 0x7ccf5ee2,NULL,0,diagnostics,memory);
    }
    score_word(score,0x18,0); score_word(score,0x10,0);
    thug_score_configure_special(score);
    __builtin_memcpy(&id,(uint8_t *)score+8,2);
    body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);
    if (body && ((uint8_t *)body)[0xbc])
        thug_score_event_reset((ThugScoreEventComponent *)thug_object_find_component(body,0x8bce7e66),diagnostics,memory);
}
/* 0x00561670. The original stack array holds at most 250 entry texts. The
 * temporary lookup reference ends before rebuilding and running the QB script. */
void thug_score_update_combo_text(ThugScore *score, uint32_t clear,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    int16_t skater_id; __builtin_memcpy(&skater_id,(const uint8_t *)score+8,2);
    ThugSkaterBody *body = thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)skater_id);
    uint32_t screen = body ? thug_skater_screen_id(body) : 0;
    ThugObjectReference reference; thug_ui_find(&reference,screen+0x44727dae,0);
    ThugUiMultiline *widget = (ThugUiMultiline *)reference.object;
    thug_object_reference_destroy(&reference);
    if (!widget) return;
    const char *texts[250];
    int32_t count = (uint8_t)clear ? 0 : score->entries.count;
    void **entries = score->entries.items;
    for (int32_t i = 0; i < count; ++i) texts[i] = (const char *)entries[i]+0x5c;
    thug_ui_multiline_set_text(widget,texts,(uint32_t)count,diagnostics,memory);
    thug_script_run_sync(0xd4491be1,NULL,NULL,0,diagnostics,memory);
}
/* 0x00566600. The original repeats read-only list scans; a single pass retains
 * its first match on a valid list ending in a nonnull body=-1 sentinel. */
ThugSkaterBody *thug_game_skater_by_id(const ThugGameContext *game, uint32_t id) {
    for (ThugSkaterNode *n = game->skaters; (uintptr_t)n->body != UINT32_MAX; n = n->next)
        if (n->body->object_id == id) return n->body;
    return NULL;
}
/* 0x0057fec0. This word overlaps the still-unnamed extended body values. */
uint32_t thug_skater_screen_id(const ThugSkaterBody *body) { return word((const uint8_t *)body + 0x2b8); }
/* 0x00562920. Capture the signed count, reread holder/storage per release. */
void thug_score_entries_clear(ThugScoreEntryArray **holder, const ThugMemory *memory) {
    int32_t count = (*holder)->count;
    for (int32_t i = 0; i < count; ++i) memory->release(memory->context, (*holder)->items[i]);
    (*holder)->count = 0;
}
/* 0x00563020. The second history block is cleared, not the first one. */
void thug_score_combo_clear(ThugScore *score, const ThugMemory *memory) {
    score->value_14 = 0;
    ThugScoreEntryArray *entries = &score->entries;
    thug_score_entries_clear(&entries, memory);
    score->index_68 = score->index_6c = UINT32_MAX;
    score->value_5c = score->value_60 = 0;
    score->value_153c = score->value_1548 = score->value_1544 = 0;
    for (uint32_t i = 0; i < 625; ++i) score->values_b74[i] = 0;
    score->value_28 = 0; score->multiplier_154c = 1;
}
/* 0x00562970. Clear cache before reading key; a miss retains count/tail/index.
 * The node is freed before decrementing the count; payload ownership is separate. */
void thug_score_map_remove(ThugObjectiveManager *map, const uint32_t *key, const ThugMemory *memory) {
    ThugObjectiveLink *node = map->objectives, *previous = NULL;
    map->cached_objective = NULL;
    if (!node) return;
    uint32_t wanted = word(key);
    while (node->key != wanted) { previous = node; node = node->next; if (!node) return; }
    if (previous) previous->next = node->next; else map->objectives = node->next;
    if (map->unknown_8 == (uint32_t)(uintptr_t)node) map->unknown_8 = (uint32_t)(uintptr_t)previous;
    memory->release(memory->context, node);
    map->objective_count = (int32_t)((uint32_t)map->objective_count - 1);
}
/* 0x005633e0. Repeated index-zero retrieval uses the real shared lookup/cache.
 * Valid list length must cover the initially captured positive count. */
void thug_score_map_clear(ThugObjectiveManager **holder, const ThugMemory *memory) {
    int32_t count = (*holder)->objective_count;
    int32_t index = 0;
    for (int32_t i = 0; i < count; ++i) {
        uint32_t key;
        void *value = thug_objective_at(*holder, &index, &key);
        thug_score_map_remove(*holder, &key, memory);
        if (value) memory->release(memory->context, value);
    }
}
/* 0x005612d0. Color arrays are required; raw words narrow to bytes. */
void thug_score_configure_special(ThugScore *score) {
    const ThugScriptArray *colors = thug_script_get_global_array(0x2e8b9f1c, 1);
    for (int32_t i = 0; i < 3; ++i) {
        const ThugScriptArray *color = (const void *)thug_script_array_structure(colors, i);
        for (int32_t j = 0; j < 4; ++j)
            score->special_colors[i][j] = (uint8_t)(uintptr_t)thug_script_array_structure(color, j);
    }
    score->special_interpolator_rate = (float)thug_script_get_global_number(0x3abcda81, 1);
}
/* 0x00518390. The guard is a spawned-script ID lookup, not a listener count. */
void thug_score_event_reset(ThugScoreEventComponent *component, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const uint8_t *owner = component->base.owner;
    if (thug_script_find_spawned(word(owner + 0x2bc) + 0x83321dea)) {
        owner = component->base.owner;
        thug_event_emit((ThugEventManager *)thug_object_lookup_manager, 0x813cc576,
            word(owner + 0x2bc) + 0x83321dea, word(owner + 0x14), NULL, 0, -1, diagnostics, memory);
    }
    component->value_18 = 0;
}
