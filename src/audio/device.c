#include "device.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(sizeof(ThugAudioSample) == 64, "Audio sample header");
_Static_assert(offsetof(ThugAudioBufferMethods, lock) == 0x2c, "Buffer ABI");
_Static_assert(offsetof(ThugAudioBufferMethods, unlock) == 0x4c, "Buffer ABI end");
_Static_assert(offsetof(ThugAudioSpatialMethods, position) == 0x4c, "Spatial ABI");
_Static_assert(offsetof(ThugAudioListenerMethods, commit) == 0x44, "Listener ABI");
ThugAudioListener *thug_audio_listener;
uint8_t thug_audio_spatial_enabled, thug_audio_frequency_enabled, thug_sound_debug_mode;
float thug_audio_master_volume;
uint32_t thug_audio_play_attempts;
const uint32_t thug_audio_spatial_iid[4] = {0x279afa86,0x11ce4981,0x200021a5,0x60e50baf};
static uint32_t word(float value) { uint32_t bits; __builtin_memcpy(&bits, &value, 4); return bits; }
static uint32_t clamped_volume(uint32_t value) {
    int32_t signed_value = (int32_t)value;
    return signed_value < -10000 ? (uint32_t)-10000 : signed_value > 0 ? 0 : value;
}
static double log10_x87(double value) { return thug_platform_log2(value) * 0x1.34413509f79ffp-2; }
static void orient_listener(const float forward[4]) {
    ThugAudioListener *listener = thug_audio_listener;
    listener->methods->orientation(listener, word(forward[0]), word(forward[1]), word(forward[2]), 0, 0xbf800000, 0, 1);
}
/* 0x0047cd70. Preserve the original device calls, order and state reads.
 * 3D mode commits listener updates and returns without changing frequency.
 * The stereo path retains the game's positive logarithmic pan calculation. */
void thug_audio_apply_settings(uint32_t index, const ThugSpatialSoundVolume *volume, float pitch) {
    ThugAudioSlot *slot = thug_audio_slots + index;
    if (!slot->buffer) return;
    if (thug_audio_spatial_enabled && volume->volume.format == 3 && slot->spatial_buffer) {
        ThugCamera *nearest = thug_camera_nearest(volume->position, NULL);
        ThugCamera *primary = thug_camera_at_viewport(0);
        float relative[4], forward[4];
        thug_vector_difference(relative, volume->position, thug_camera_position(nearest));
        if (nearest != primary && primary) {
            thug_vector_negated(forward, thug_camera_orientation(primary) + 8);
            orient_listener(forward);
            float nearest_forward[4], primary_forward[4];
            thug_vector_negated(nearest_forward, thug_camera_orientation(nearest) + 8);
            thug_vector_negated(primary_forward, thug_camera_orientation(primary) + 8);
            float angle = (float)R24(thug_vector_angle_degrees(nearest_forward, primary_forward) * (double)0.01745329238474369f);
            thug_vector_rotate_y(relative, angle);
        } else {
            thug_vector_negated(forward, thug_camera_orientation(nearest) + 8);
            orient_listener(forward);
        }
        ThugAudioSpatialBuffer *spatial = slot->spatial_buffer;
        spatial->methods->minimum_distance(spatial, word(volume->distance), 1);
        spatial = slot->spatial_buffer;
        spatial->methods->maximum_distance(spatial, 0x42b40000, 1);
        spatial = slot->spatial_buffer;
        spatial->methods->position(spatial, word(relative[0]), word(relative[1]), word(relative[2]), 1);
        uint32_t gain = (uint32_t)-10000;
        double master = R24((double)thug_audio_master_volume * (double)0.01f);
        if (master > 0) {
            double logarithm = thug_platform_log2(master) * 0x1.62e42fefa39efp-1;
            gain = clamped_volume(thug_truncate_double_low_word(R24(logarithm * (double)14.426950454711914f)) * 100);
        }
        ThugAudioBuffer *buffer = slot->buffer;
        buffer->methods->volume(buffer, volume->volume.channels[0] > 0 || volume->volume.channels[1] > 0 ? gain : (uint32_t)-10000);
        if (thug_audio_listener) thug_audio_listener->methods->commit(thug_audio_listener);
        return;
    }
    uint32_t pan = 0, gain = (uint32_t)-10000;
    float left = volume->volume.channels[0], right = volume->volume.channels[1];
    if (left > 0 || right > 0) {
        double maximum = left, ratio;
        if (left < right) { maximum = right; ratio = R24((double)right / left); }
        else ratio = R24((double)left / right);
        pan = thug_truncate_double_low_word(R24(log10_x87(ratio) * 1000));
        double level = R24(R24(maximum * thug_audio_master_volume) * (double)0.01f);
        if (level > 0) gain = clamped_volume(thug_truncate_double_low_word(R24(log10_x87(R24(level * (double)0.01f)) * 2000)));
    }
    ThugAudioBuffer *buffer = slot->buffer;
    buffer->methods->volume(buffer, gain);
    buffer = slot->buffer;
    buffer->methods->pan(buffer, pan);
    if (pitch != 0) {
        uint32_t frequency;
        if (pitch == 100) frequency = slot->base_frequency;
        else {
            /* FILD signed, followed by the original conditional 2^32 add. */
            double base = (double)(int32_t)slot->base_frequency;
            if ((int32_t)slot->base_frequency < 0) base = R24(base + 0x1p32);
            double product = thug_platform_multiply_x87_single(base, pitch);
            frequency = thug_truncate_double_low_word(R24(product * (double)0.01f));
            if ((int32_t)frequency > 200000) frequency = 200000;
            else if ((int32_t)frequency < 100) frequency = 100;
        }
        if (frequency != slot->current_frequency) {
            slot->current_frequency = frequency;
            if (thug_audio_frequency_enabled) {
                buffer = slot->buffer; buffer->methods->frequency(buffer, frequency);
            }
        }
    }
}
static void copy_sample(uint8_t *destination, const uint8_t *source, uint32_t size) {
    uint32_t words = size / 4;
    for (uint32_t i = 0; i < words; ++i) {
        uint32_t value; __builtin_memcpy(&value, source + i*4, 4); __builtin_memcpy(destination + i*4, &value, 4);
    }
    for (uint32_t i = words*4; i < size; ++i) destination[i] = source[i];
}
/* 0x0047d130. Lock failure still caches the sample and proceeds to playback.
 * The active byte and play-attempt counter are written even on play failure.
 * Callback results and writes are authoritative; buffer pointers are reread. */
int32_t thug_audio_play_buffer(const ThugAudioSampleBinding *binding, const ThugSpatialSoundVolume *volume, float pitch) {
    if (!binding->sample) return -1;
    uint32_t index = thug_audio_choose_slot(binding->sample);
    if ((int32_t)index < 0) return -1;
    ThugAudioSlot *slot = thug_audio_slots + index;
    ThugAudioBuffer *buffer = slot->buffer;
    if (slot->active && buffer) buffer->methods->stop(buffer);
    if (binding->sample != slot->cached_asset) {
        ThugAudioSpatialBuffer *spatial = slot->spatial_buffer;
        if (spatial) spatial->methods->release(spatial);
        buffer = slot->buffer;
        slot->spatial_buffer = NULL;
        if (buffer) buffer->methods->release(buffer);
        slot->buffer = NULL; slot->cached_asset = NULL;
        binding->sample->description.flags = thug_audio_spatial_enabled && volume->volume.format == 3 ? 0x400b0 : 0x400e0;
        for (unsigned i = 0; i < 4; ++i) binding->sample->description.algorithm[i] = 0;
        ThugAudioDevice *device = (ThugAudioDevice *)(uintptr_t)thug_sound_device;
        if (device->methods->create(device, &binding->sample->description, (ThugAudioBuffer **)&slot->buffer, 0)) return -1;
        if (thug_audio_spatial_enabled && volume->volume.format == 3) {
            buffer = slot->buffer;
            buffer->methods->query(buffer, thug_audio_spatial_iid, (ThugAudioSpatialBuffer **)&slot->spatial_buffer);
        }
        buffer = slot->buffer;
        uint8_t *first, *second;
        uint32_t first_size, second_size;
        if (!buffer->methods->lock(buffer, 0, binding->sample->description.bytes, &first, &first_size, &second, &second_size, 2)) {
            copy_sample(first, binding->sample->samples, first_size);
            if (second) copy_sample(second, binding->sample->samples + first_size, second_size);
            buffer = slot->buffer;
            buffer->methods->unlock(buffer, first, first_size, second, second_size);
        }
        slot->cached_asset = binding->sample;
    }
    slot->base_frequency = binding->sample->frequency;
    slot->current_frequency = 0;
    thug_audio_apply_settings(index, volume, pitch);
    buffer = slot->buffer;
    buffer->methods->seek(buffer, 0);
    buffer = slot->buffer;
    uint32_t result = buffer->methods->play(buffer, 0, 0, (uint8_t)binding->loop != 0);
    ++thug_audio_play_attempts;
    slot->active = 1;
    return result ? -1 : (int32_t)index;
}
/* 0x0047bd20. The sixth stack argument (filename) is unused in this specimen.
 * Preserve both global-setting reads, voice naming and ID assignment order. */
uint32_t thug_sound_play(const ThugSoundConfiguration *configuration, uint32_t checksum, ThugSpatialSoundVolume *volume, float pitch, uint32_t name, const ThugSoundPlaybackControls *controls, const char *filename) {
    (void)configuration; (void)filename;
    if (thug_sound_disabled()) return 0;
    ThugSoundAsset *asset = thug_sound_find_asset(checksum);
    if (!asset) return 0;
    if (!name) name = checksum;
    if (!thug_sound_debug_mode && thug_script_get_global_integer(0xd7bb618d, 0) && !controls) thug_sound_id_available(name);
    thug_sound_apply_asset_settings(&volume->volume, &pitch, asset);
    int32_t index = thug_audio_play_buffer((const ThugAudioSampleBinding *)&asset->unknown_14, volume, pitch);
    if (index == -1) return 0;
    ThugSoundVoice *voice = thug_sound_voices + index;
    voice->name = name; voice->id = thug_sound_available_id(name); voice->asset = asset;
    thug_sound_voice_parameters(&voice->parameters, asset, controls);
    if (!thug_sound_debug_mode) thug_script_get_global_integer(0xd7bb618d, 0);
    return voice->id;
}
