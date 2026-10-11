#include "voices.h"
#include "../platform/math.h"
_Static_assert(sizeof(ThugSoundVoiceParameters) == 44, "Voice parameters");
_Static_assert(sizeof(ThugSoundVoice) == 60, "Voice record");
_Static_assert(sizeof(ThugAudioSlot) == 24, "Audio device slot");
_Static_assert(sizeof(ThugSoundPending) == 20, "Pending sound prefix");
ThugSoundVoice thug_sound_voices[48];
ThugAudioSlot thug_audio_slots[48];
uint32_t thug_audio_slot_count, thug_audio_slot_cursor;
ThugSoundPending *thug_sound_pending;

/* 0x0047c7e0. The active flag alone does not establish a live buffer. */
uint8_t thug_audio_slot_active(uint32_t index) {
    return thug_audio_slots[index].active && thug_audio_slots[index].buffer;
}
/* 0x0047c720. The initialized count must be in 1..48. Prefer the first
 * inactive slot with the same cached asset. Otherwise use the last inactive
 * slot in the circular scan; if all are busy, use cursor+1. Cursor arithmetic
 * wraps before the unsigned remainder, as in the original DIV instruction. */
uint32_t thug_audio_choose_slot(const void *cached_asset) {
    uint32_t start = thug_audio_slot_cursor, count = thug_audio_slot_count;
    uint32_t chosen = (start + 1) % count;
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t index = (start + i) % count;
        if (thug_audio_slots[index].active) continue;
        if (thug_audio_slots[index].cached_asset == cached_asset) {
            thug_audio_slot_cursor = index; return index;
        }
        chosen = index;
    }
    thug_audio_slot_cursor = chosen;
    return chosen;
}
/* 0x0047bab0. Only the first matching voice record is examined. Pending IDs
 * remain reserved even while audio is disabled, and may reserve ID zero. */
uint8_t thug_sound_id_available(uint32_t id) {
    if (!thug_sound_disabled() && id) {
        for (uint32_t i = 0; i < 48; ++i) if (thug_sound_voices[i].id == id) {
            if (thug_audio_slot_active(i)) return 0;
            break;
        }
    }
    for (const ThugSoundPending *p = thug_sound_pending; p; p = p->next) if (p->id == id) return 0;
    return 1;
}
/* 0x0047bb20. Search consecutive IDs with 32-bit wrap, without reserving one. */
uint32_t thug_sound_available_id(uint32_t first) {
    while (!thug_sound_id_available(first)) ++first;
    return first;
}
static uint32_t float_word(float value) { uint32_t word; __builtin_memcpy(&word, &value, 4); return word; }
static float word_float(uint32_t word) { float value; __builtin_memcpy(&value, &word, 4); return value; }
static uint32_t loaded_float_word(uint32_t word) {
    if ((word & 0x7f800000) == 0x7f800000 && (word & 0x7fffff)) word |= 0x400000;
    return word;
}
/* 0x0047af40. Raw control copies precede x87 loads for the derived fields.
 * Keep that order for overlapping inputs. The default path leaves six
 * intermediate fields untouched; it does not zero the whole record. */
void thug_sound_voice_parameters(ThugSoundVoiceParameters *out, const ThugSoundAsset *asset, const ThugSoundPlaybackControls *controls) {
    if (controls) {
        out->value_8 = controls->value_0;
        out->value_c = controls->value_4;
        uint32_t distance = controls->distance;
        if (word_float(distance) == 0) distance = float_word(asset->distance);
        out->distance = loaded_float_word(distance);
        out->value_20 = 0; out->value_24 = 0;
        out->value_18 = loaded_float_word(out->value_8);
        out->value_10 = out->value_18;
        out->value_1c = loaded_float_word(out->value_c);
        out->value_14 = out->value_1c;
        out->flags = controls->flags;
        out->checksum = asset->checksum;
    } else {
        out->value_8 = 0x42c80000; out->value_c = 0x42c80000;
        out->distance = 0; out->flags = 0; out->checksum = asset->checksum;
    }
}
/* 0x0047b480. The initial 50 percent scale is unconditional when enabled.
 * Asset multipliers are compared with the raw 100.0 bit pattern. */
void thug_sound_apply_asset_settings(ThugSoundVolume *volume, float *pitch, const ThugSoundAsset *asset) {
    if (thug_sound_disabled()) return;
    thug_sound_volume_scale(volume, 50);
    if (asset->unknown_c != 0x42c80000) thug_sound_volume_scale(volume, word_float(asset->unknown_c));
    if (asset->unknown_8 != 0x42c80000) {
        double product = thug_platform_round_x87_single((double)*pitch * word_float(asset->unknown_8));
        *pitch = (float)thug_platform_round_x87_single(product * (double)0.01f);
    }
}
