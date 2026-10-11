#ifndef THUG_AUDIO_VOICES_H
#define THUG_AUDIO_VOICES_H
#include "sound.h"
typedef struct {
    uint32_t checksum, distance, value_8, value_c, value_10, value_14;
    uint32_t value_18, value_1c, value_20, value_24, flags;
} ThugSoundVoiceParameters;
typedef struct { uint32_t value_0, value_4, distance, flags; } ThugSoundPlaybackControls;
typedef struct {
    uint32_t id, name;
    ThugSoundAsset *asset;
    ThugSoundVoiceParameters parameters;
    uint32_t unknown_38;
} ThugSoundVoice;
typedef struct {
    void *buffer, *spatial_buffer;
    uint32_t base_frequency, current_frequency;
    uint8_t active, padding[3];
    void *cached_asset;
} ThugAudioSlot;
typedef struct ThugSoundPending {
    uint32_t id, unknown_4, unknown_8, unknown_c;
    struct ThugSoundPending *next;
} ThugSoundPending;
extern ThugSoundVoice thug_sound_voices[48];
extern ThugAudioSlot thug_audio_slots[48];
extern uint32_t thug_audio_slot_count, thug_audio_slot_cursor;
extern ThugSoundPending *thug_sound_pending;
uint8_t thug_audio_slot_active(uint32_t index);
uint32_t thug_audio_choose_slot(const void *cached_asset);
uint8_t thug_sound_id_available(uint32_t id);
uint32_t thug_sound_available_id(uint32_t first);
void thug_sound_voice_parameters(ThugSoundVoiceParameters *, const ThugSoundAsset *, const ThugSoundPlaybackControls *);
void thug_sound_apply_asset_settings(ThugSoundVolume *, float *pitch, const ThugSoundAsset *);
#endif
