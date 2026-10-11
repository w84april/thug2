#include "objectives.h"
#include "profile.h"
#include "../script/operators.h"
#include <stddef.h>
static uint32_t word(const void *p) { uint32_t v; __builtin_memcpy(&v,p,4); return v; }
/* 0x00555b50. Capture the profile, key-label table, binding map and count once.
 * Required strings must exist; integer bindings require a local skater. */
uint8_t thug_objective_text_tables(const ThugScriptArray *combos, ThugScriptArray *keys,
    ThugScriptArray *tricks, int32_t special_index, const ThugMemory *memory) {
    const ThugScriptStructure *labels = thug_script_get_global_structure(0x8856c817,1);
    const ThugGameContext *game = thug_game_context;
    ThugProfile *profile = thug_game_profile(game,NULL);
    ThugScriptStructure *map = thug_profile_parameters(profile,0xd544aa2d);
    int32_t count = (int32_t)combos->count;
    const char *key_text, *trick_text;
    for (int32_t i = 0; i < count; ++i) {
        uint32_t combo = (uint32_t)(uintptr_t)thug_script_array_structure(combos,i), trick = 0, slot = 0;
        uint8_t integer = thug_script_get_integer(map,combo,&slot,0);
        if (!integer && !thug_script_get_checksum(map,combo,&trick,0)) {
            int32_t available = (int32_t)thug_profile_binding_count(profile), j = 0;
            ThugProfileBinding binding;
            for (; j < available; ++j) { thug_profile_binding(profile,&binding,j); if (binding.combo == combo) break; }
            if (j == available || available < 1) return 0;
            trick = binding.trick;
        }
        thug_script_get_text(labels,combo,&key_text,1);
        if (integer) {
            ThugSkaterBody *skater = thug_game_local_skater(game);
            if (skater) {
                uint32_t entry = word((const void *)((uintptr_t)skater + 0x17c + slot*4));
                const ThugScriptStructure *parameters = (const ThugScriptStructure *)(uintptr_t)word((const void *)(uintptr_t)(entry+4));
                thug_script_get_text(parameters,0xa1dc81f9,&trick_text,1);
            }
        } else if (special_index > -1) {
            ThugScriptArray *specials = thug_script_get_global_array(0xffd7913f,1);
            thug_script_get_text(thug_script_array_structure(specials,special_index),0xa1dc81f9,&trick_text,1);
        } else {
            ThugScriptStructure *parameters;
            thug_script_get_structure(thug_script_get_global_structure(trick,1),0x7031f10c,&parameters,1);
            thug_script_get_text_forward(parameters,0xa1dc81f9,&trick_text,1);
        }
        thug_script_array_set_word(keys,i,(uint32_t)(uintptr_t)thug_script_string_copy(key_text,memory));
        thug_script_array_set_word(tricks,i,(uint32_t)(uintptr_t)thug_script_string_copy(trick_text,memory));
    }
    return 1;
}
/* The original sprintf receives no varargs. Only literal/%% replacement
 * formats have defined argument-free behavior. Cursor advancement below is
 * by FORMAT length, not the number of emitted characters. */
static void argument_free_format(char *out, const char *format) {
    while (*format) { if (*format == '%' && format[1] == '%') ++format; *out++ = *format++; }
    *out = 0;
}
static uint32_t text_length(const char *s) { uint32_t n = 0; while (s[n]) ++n; return n; }
/* 0x00554890. One/two-digit indices, original array order and untouched gaps. */
void thug_objective_expand_text(const char *in, char *out, const ThugScriptArray *keys,
    const ThugScriptArray *tricks, uint32_t unused_capacity) {
    (void)unused_capacity;
    while (*in) {
        if (in[0] == '\\' && (in[1] == 't' || in[1] == 'k') && in[2] >= '0' && in[2] <= '9') {
            uint32_t index = (uint8_t)in[2]-'0', consumed = 3;
            if (in[3] >= '0' && in[3] <= '9') { index = index*10+(uint8_t)in[3]-'0'; ++consumed; }
            const char *replacement = thug_script_array_text(in[1] == 't' ? tricks : keys,(int32_t)(index-1));
            argument_free_format(out,replacement);
            out += text_length(replacement); in += consumed;
        } else *out++ = *in++;
    }
    *out = 0;
}
static void destroy_array(ThugScriptArray *array, const ThugMemory *memory) {
    thug_script_array_clear_storage(array,memory); memory->release(memory->context,array);
}
/* 0x00556a00. Save original text once, resolve actual bindings, rewrite each
 * field in original order and release all temporary owned strings/arrays. */
uint8_t thug_objective_update_text(ThugObjective *objective, const ThugMemory *memory) {
    ThugScriptArray *combos = NULL;
    if (!thug_script_get_array(objective->parameters,0x79704516,&combos,0)) return 0;
    const uint32_t source_keys[] = {0x0c5d7e6b,0x4bc5229d,0x63981d6f,0xda441d9a,0x1b3b4dd8};
    const uint32_t saved_keys[] = {0x01f238b1,0x89e9c617,0x988330d3,0xb0d7628f,0xe0206064};
    for (unsigned i = 0; i < 5; ++i) {
        if (!thug_script_has_name_or_flag(objective->parameters,saved_keys[i])) {
            const char *text;
            if (thug_script_get_text(objective->parameters,source_keys[i],&text,0))
                thug_script_set_string(objective->parameters,saved_keys[i],text,memory);
            else if (!i) {
                ThugScriptArray *array;
                if (thug_script_get_array(objective->parameters,source_keys[i],&array,0))
                    thug_script_set_array_copy(objective->parameters,saved_keys[i],array,memory);
            }
        }
    }
    uint32_t special = UINT32_MAX;
    if (thug_script_has_flag(objective->parameters,0x8e6014f6)) thug_script_get_integer(objective->parameters,0x0b502200,&special,1);
    ThugScriptArray *keys = thug_script_array_initialize(memory->allocate(memory->context,12,1));
    ThugScriptArray *tricks = thug_script_array_initialize(memory->allocate(memory->context,12,1));
    uint32_t count = combos->count;
    thug_script_array_set_size(keys,count,3,memory); thug_script_array_set_size(tricks,count,3,memory);
    uint8_t success = thug_objective_text_tables(combos,keys,tricks,(int32_t)special,memory);
    if (success) {
        char buffer[512]; const char *text;
        if (thug_script_get_text(objective->parameters,saved_keys[0],&text,0)) {
            thug_objective_expand_text(text,buffer,keys,tricks,512);
            /* Original00556d1c reloads the INPUT pointer, not the formatted buffer. */
            thug_script_set_string(objective->parameters,source_keys[0],text,memory);
        } else {
            ThugScriptArray *source = NULL;
            if (thug_script_get_array(objective->parameters,saved_keys[0],&source,0)) {
                int32_t length = (int32_t)source->count;
                ThugScriptArray *copy = thug_script_array_initialize(memory->allocate(memory->context,12,1));
                thug_script_array_set_size(copy,(uint32_t)length,3,memory);
                for (int32_t i = 0; i < length; ++i) {
                    thug_objective_expand_text(thug_script_array_text(source,i),buffer,keys,tricks,512);
                    thug_script_array_set_word(copy,i,(uint32_t)(uintptr_t)thug_script_string_copy(buffer,memory));
                }
                thug_script_set_array_copy(objective->parameters,source_keys[0],copy,memory);
                thug_script_array_clear(copy,memory); destroy_array(copy,memory);
            }
        }
        for (unsigned i = 1; i < 5; ++i) {
            if (thug_script_get_text(objective->parameters,saved_keys[i],&text,0)) {
                thug_objective_expand_text(text,buffer,keys,tricks,512);
                thug_script_set_string(objective->parameters,source_keys[i],buffer,memory);
            }
        }
    }
    thug_script_array_clear(keys,memory); thug_script_array_clear(tricks,memory);
    destroy_array(keys,memory); destroy_array(tricks,memory);
    return success;
}
