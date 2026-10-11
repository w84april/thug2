#ifndef THUG_SCRIPT_PARAMS_H
#define THUG_SCRIPT_PARAMS_H
#include <stdint.h>

typedef struct ThugScriptSymbol {
    uint8_t flags, type;
    uint16_t unknown_2;
    uint32_t name, unknown_8, value;
    struct ThugScriptSymbol *next;
} ThugScriptSymbol;
typedef struct ThugScriptComponent {
    uint8_t type_and_flags, padding[3];
    uint32_t name, value;
    struct ThugScriptComponent *next;
} ThugScriptComponent;
typedef struct {
    uint32_t unknown_0;
    ThugScriptComponent *first;
} ThugScriptStructure;
typedef struct {
    uint8_t tag, padding[3];
    float x, y;
} ThugScriptPair;
typedef struct {
    uint32_t unknown_0, count, value_or_items;
} ThugScriptArray;

/* Original 0x006f3624 points at 4096 buckets. Set by the script loader. */
extern ThugScriptSymbol **thug_script_symbol_buckets;
ThugScriptSymbol *thug_script_resolve_symbol(uint32_t name);
/* Double preserves the exact integer returned in x87 ST(0), before callers round. */
double thug_script_get_global_number(uint32_t name, uint32_t assert_missing);
ThugScriptStructure *thug_script_get_global_structure(uint32_t name, uint32_t assert_missing);
ThugScriptArray *thug_script_get_global_array(uint32_t name, uint32_t assert_missing);
ThugScriptArray *thug_script_get_global_array_text(const char *, uint32_t);
uint32_t thug_script_get_global_value_text(const char *, uint32_t);
uint8_t thug_script_get_typed(const ThugScriptStructure *, uint32_t name, uint32_t type, void *output);
uint8_t thug_script_get_float(const ThugScriptStructure *, uint32_t name, float *output, uint32_t assert_missing);
uint32_t thug_script_get_global_integer(uint32_t name, uint32_t assert_missing);
uint8_t thug_script_get_integer(const ThugScriptStructure *, uint32_t, uint32_t *, uint32_t);
uint8_t thug_script_get_boolean(const ThugScriptStructure *, uint32_t, uint32_t *, uint32_t);
uint8_t thug_script_get_structure(const ThugScriptStructure *, uint32_t, ThugScriptStructure **, uint32_t);
uint8_t thug_script_get_text(const ThugScriptStructure *, uint32_t, const char **, uint32_t);
uint8_t thug_script_get_text_forward(const ThugScriptStructure *, uint32_t, const char **, uint32_t);
uint8_t thug_script_get_checksum_legacy(const ThugScriptStructure *, uint32_t, uint32_t *, uint32_t);
uint8_t thug_script_get_array_legacy(const ThugScriptStructure *, uint32_t, ThugScriptArray **, uint32_t);
uint8_t thug_script_get_array(const ThugScriptStructure *, uint32_t, ThugScriptArray **, uint32_t);
ThugScriptComponent *thug_script_find_name_or_flag(const ThugScriptStructure *, uint32_t);
uint32_t thug_script_has_name_or_flag(const ThugScriptStructure *, uint32_t);
uint8_t thug_script_get_checksum(const ThugScriptStructure *, uint32_t, uint32_t *, uint32_t);
uint8_t thug_script_get_checksum_string(const ThugScriptStructure *, const char *, uint32_t *, uint32_t);
ThugScriptPair *thug_script_pair_initialize(ThugScriptPair *);
uint8_t thug_script_get_pair(const ThugScriptStructure *, uint32_t, ThugScriptPair *, uint32_t);
ThugScriptStructure *thug_script_array_structure(const ThugScriptArray *, int32_t index);
uint8_t thug_script_has_flag(const ThugScriptStructure *, uint32_t flag);
uint8_t thug_script_get_vector(const ThugScriptStructure *,uint32_t,float out[4],uint32_t);
#endif
