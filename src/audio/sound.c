#include "sound.h"
#include "../core/checksum.h"
#include "../core/random.h"
#include "../platform/math.h"
#include <stddef.h>

_Static_assert(sizeof(ThugSoundMaterial) == 8, "Material record");
_Static_assert(sizeof(ThugSoundEvent) == 12, "Sound event record");
_Static_assert(sizeof(ThugSoundDescriptor) == 132, "Sound descriptor");
_Static_assert(sizeof(ThugSoundVolume) == 24, "Channel volume prefix");
_Static_assert(sizeof(ThugSoundAsset) == 28, "Loaded sound record");
ThugObjectLookupTable thug_sound_materials, thug_sound_events;
uint32_t thug_sound_device, thug_sound_mode;
ThugSoundConfiguration *thug_sound_configuration;
float thug_sound_default_distance;
int32_t thug_sound_asset_count_a, thug_sound_asset_count_b;
ThugSoundAsset thug_sound_assets_a[256], thug_sound_assets_b[256];

/* 0x00444310. Valid callers supply a registered byte ID. The original
 * dereferences a null record on a miss; no new missing-ID policy is added. */
uint32_t thug_sound_event_parameter(uint32_t event_id) {
    uint32_t key = (uint8_t)event_id;
    const ThugSoundEvent *event = thug_object_table_find(&thug_sound_events, &key, 0);
    return event->parameter_name;
}
/* 0x00444360, 0x004443b0. These searches reset and retain the shared iterator.
 * A null record terminates the search, including in a collision chain. */
uint32_t thug_sound_material_name(uint32_t material_id) {
    thug_sound_materials.iteration_bucket = UINT32_MAX;
    thug_sound_materials.iteration_node = NULL;
    while (thug_object_table_next(&thug_sound_materials)) {
        ThugObjectLookupNode *node = thug_sound_materials.iteration_node;
        if (!node || !node->value) break;
        const ThugSoundMaterial *material = node->value;
        if (material->id == (uint8_t)material_id) return material->structure_name;
    }
    return 0;
}
uint8_t thug_sound_event_id(uint32_t event_name) {
    thug_sound_events.iteration_bucket = UINT32_MAX;
    thug_sound_events.iteration_node = NULL;
    while (thug_object_table_next(&thug_sound_events)) {
        ThugObjectLookupNode *node = thug_sound_events.iteration_node;
        if (!node || !node->value) break;
        const ThugSoundEvent *event = node->value;
        if (event->event_name == event_name) return event->id;
    }
    return 0;
}
/* 0x00444400, 0x00444480. Both absent material definitions and absent named
 * structures fall back to the default material. A successful null value stays
 * successful, just as in the script structure getter. */
uint8_t thug_sound_material_settings(uint32_t material_id, ThugScriptStructure **out, uint32_t property) {
    ThugScriptStructure *s = thug_script_get_global_structure(thug_sound_material_name(material_id), 0);
    if (s && thug_script_get_structure(s, property, out, 0)) return 1;
    s = thug_script_get_global_structure(0x5b80cfcb, 0);
    return s && thug_script_get_structure(s, property, out, 0);
}
uint8_t thug_sound_get_material_settings(ThugScriptStructure **out, uint32_t material_id, uint32_t property) {
    return thug_sound_material_settings(material_id, out, property);
}
/* 0x00444760. Valid array entries have integer weights. Both passes traverse
 * backwards; sums and subtractions wrap at 32 bits. Even an empty array draws
 * from the original PRNG. Direct structures do not draw. */
ThugScriptStructure *thug_sound_select_weighted(const ThugScriptStructure *s) {
    ThugScriptStructure *choice;
    if (thug_script_get_structure(s, 0x25f654c8, &choice, 0)) return choice;
    ThugScriptArray *array;
    thug_script_get_array(s, 0x25f654c8, &array, 1);
    uint32_t sum = 0, weight;
    for (uint32_t i = array->count; i;) {
        choice = thug_script_array_structure(array, (int32_t)--i);
        thug_script_get_integer(choice, 0xdbc4c4db, &weight, 1);
        sum += weight;
    }
    uint32_t random = (uint32_t)thug_random_range(sum);
    for (uint32_t i = array->count; i;) {
        choice = thug_script_array_structure(array, (int32_t)--i);
        thug_script_get_integer(choice, 0xdbc4c4db, &weight, 1);
        random -= weight;
        if ((int32_t)random < 0) return choice;
    }
    return NULL;
}
/* 0x00444830. Select an ordered intensity at or below the threshold, or an
 * absent threshold. Unordered comparisons advance. A direct structure bypasses
 * weighting. TEST AH,41 / JNP accepts exactly one of the less/equal bits. */
ThugScriptStructure *thug_sound_select_impact(const ThugScriptStructure *s, uint32_t event_id, float intensity) {
    uint32_t name = thug_sound_event_parameter(event_id);
    ThugScriptStructure *choice;
    if (thug_script_get_structure(s, name, &choice, 0)) return choice;
    ThugScriptArray *array;
    thug_script_get_array(s, name, &array, 1);
    for (uint32_t i = 0; i < array->count; ++i) {
        choice = thug_script_array_structure(array, (int32_t)i);
        float threshold;
        if (!thug_script_get_float(choice, 0x9ee9a09a, &threshold, 0) || intensity <= threshold)
            return thug_sound_select_weighted(choice);
    }
    return NULL;
}
/* 0x0047b010. The device word is tested but never dereferenced. */
uint8_t thug_sound_disabled(void) {
    return !thug_sound_device || thug_sound_mode == 2 || thug_sound_mode == 6;
}
/* 0x004445b0. Valid paths fit the original 104-byte buffer. Preserve the
 * untouched path tail and defaults on missing optional parameters. The CRC
 * thunk at 0x00472e60 targets the already recovered string checksum. */
uint8_t thug_sound_build_descriptor(const ThugScriptStructure *s, ThugSoundDescriptor *out) {
    if (thug_sound_disabled()) return 0;
    out->value_70 = out->value_74 = out->value_7c = out->value_80 = 100;
    out->value_78 = 0; out->path[0] = 0; out->checksum = 0; out->value_6c = 100;
    const char *path;
    if (!thug_script_get_text(s, 0x07713c7b, &path, 0)) return 0;
    char *destination = out->path;
    do { *destination++ = *path; } while (*path++);
    const char *basename = out->path;
    for (const char *p = out->path; *p; ++p) if (*p == '/' || *p == '\\') basename = p + 1;
    out->checksum = thug_crc32_string(basename);
    thug_script_get_float(s, 0xfa3e14c5, &out->value_6c, 0);
    thug_script_get_float(s, 0x1c5ebb24, &out->value_70, 0);
    thug_script_get_float(s, 0x0693daaf, &out->value_74, 0);
    thug_script_get_float(s, 0x4391992d, &out->value_78, 0);
    thug_script_get_float(s, 0xf573682f, &out->value_7c, 0);
    thug_script_get_float(s, 0x312ccbcf, &out->value_80, 0);
    return 1;
}
/* 0x0047b030. Only the 24-byte volume prefix is initialized. */
ThugSoundVolume *thug_sound_volume_initialize(ThugSoundVolume *volume) {
    volume->format = thug_sound_configuration ? thug_sound_configuration->volume_format : 0;
    for (unsigned i = 0; i < 5; ++i) volume->channels[i] = 0;
    return volume;
}
/* 0x0047ac50. x87 rounds each product's significand while retaining its wide
 * exponent; only the final store rounds to float. */
void thug_sound_volume_scale(ThugSoundVolume *volume, float scale) {
    unsigned count = volume->format == 2 ? 5 : 2;
    for (unsigned i = 0; i < count; ++i) {
        double product = thug_platform_round_x87_single((double)scale * volume->channels[i]);
        volume->channels[i] = (float)thug_platform_round_x87_single(product * (double)0.01f);
    }
}
/* 0x0047acf0. Format 3 is never classified as silent. */
uint8_t thug_sound_volume_silent(const ThugSoundVolume *volume) {
    if (volume->channels[0] != 0 || volume->channels[1] != 0) return 0;
    if (volume->format == 2 && (volume->channels[2] != 0 || volume->channels[3] != 0 || volume->channels[4] != 0)) return 0;
    return volume->format != 3;
}
/* 0x0047b2c0. Signed counts, first array before second, first match wins.
 * Loaded counts are bounded by the two original 256-entry arenas. */
ThugSoundAsset *thug_sound_find_asset(uint32_t checksum) {
    if (thug_sound_disabled()) return NULL;
    for (int32_t i = 0; i < thug_sound_asset_count_a; ++i) if (thug_sound_assets_a[i].checksum == checksum) return thug_sound_assets_a + i;
    for (int32_t i = 0; i < thug_sound_asset_count_b; ++i) if (thug_sound_assets_b[i].checksum == checksum) return thug_sound_assets_b + i;
    return NULL;
}
/* 0x0047b760. A missing asset returns zero; a present zero distance uses the
 * default. Disabled audio also uses the default, including its NaN value. */
double thug_sound_asset_distance(uint32_t checksum) {
    if (thug_sound_disabled()) return thug_sound_default_distance;
    const ThugSoundAsset *asset = thug_sound_find_asset(checksum);
    if (!asset) return 0;
    return asset->distance == 0 ? thug_sound_default_distance : asset->distance;
}
