#ifndef THUG_AUDIO_DEVICE_H
#define THUG_AUDIO_DEVICE_H
#include "voices.h"
/* Legacy device ABI. Floating arguments are passed as raw 32-bit words, just
 * as at the original COM call sites. Platform implementations supply these
 * methods; their behavior is not supplied by recovered game code. */
typedef struct ThugAudioBuffer ThugAudioBuffer;
typedef struct ThugAudioSpatialBuffer ThugAudioSpatialBuffer;
typedef struct ThugAudioListener ThugAudioListener;
typedef struct ThugAudioDevice ThugAudioDevice;
typedef struct {
    uint32_t size, flags, bytes, reserved;
    void *format;
    uint32_t algorithm[4];
} ThugAudioBufferDescription;
typedef struct {
    uint32_t unknown_0, frequency, unknown_8[3];
    ThugAudioBufferDescription description;
    uint32_t unknown_38;
    uint8_t *samples;
} ThugAudioSample;
typedef struct { ThugAudioSample *sample; uint32_t loop; } ThugAudioSampleBinding;
typedef struct {
    uint32_t (*query)(ThugAudioBuffer *, const uint32_t *, ThugAudioSpatialBuffer **);
    uint32_t unused_4;
    uint32_t (*release)(ThugAudioBuffer *);
    uint32_t unused_c[8];
    uint32_t (*lock)(ThugAudioBuffer *, uint32_t, uint32_t, uint8_t **, uint32_t *, uint8_t **, uint32_t *, uint32_t);
    uint32_t (*play)(ThugAudioBuffer *, uint32_t, uint32_t, uint32_t);
    uint32_t (*seek)(ThugAudioBuffer *, uint32_t);
    uint32_t unused_38;
    uint32_t (*volume)(ThugAudioBuffer *, uint32_t);
    uint32_t (*pan)(ThugAudioBuffer *, uint32_t);
    uint32_t (*frequency)(ThugAudioBuffer *, uint32_t);
    uint32_t (*stop)(ThugAudioBuffer *);
    uint32_t (*unlock)(ThugAudioBuffer *, uint8_t *, uint32_t, uint8_t *, uint32_t);
} ThugAudioBufferMethods;
struct ThugAudioBuffer { const ThugAudioBufferMethods *methods; };
typedef struct {
    uint32_t unused_0[2];
    uint32_t (*release)(ThugAudioSpatialBuffer *);
    uint32_t unused_c[13];
    uint32_t (*minimum_distance)(ThugAudioSpatialBuffer *, uint32_t, uint32_t);
    uint32_t (*maximum_distance)(ThugAudioSpatialBuffer *, uint32_t, uint32_t);
    uint32_t unused_48;
    uint32_t (*position)(ThugAudioSpatialBuffer *, uint32_t, uint32_t, uint32_t, uint32_t);
} ThugAudioSpatialMethods;
struct ThugAudioSpatialBuffer { const ThugAudioSpatialMethods *methods; };
typedef struct {
    uint32_t unused_0[13];
    uint32_t (*orientation)(ThugAudioListener *, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
    uint32_t unused_38[3];
    uint32_t (*commit)(ThugAudioListener *);
} ThugAudioListenerMethods;
struct ThugAudioListener { const ThugAudioListenerMethods *methods; };
typedef struct {
    uint32_t unused_0[3];
    uint32_t (*create)(ThugAudioDevice *, ThugAudioBufferDescription *, ThugAudioBuffer **, uint32_t);
} ThugAudioDeviceMethods;
struct ThugAudioDevice { const ThugAudioDeviceMethods *methods; };
extern ThugAudioListener *thug_audio_listener;
extern uint8_t thug_audio_spatial_enabled, thug_audio_frequency_enabled, thug_sound_debug_mode;
extern float thug_audio_master_volume;
extern uint32_t thug_audio_play_attempts;
extern const uint32_t thug_audio_spatial_iid[4];
void thug_audio_apply_settings(uint32_t index, const ThugSpatialSoundVolume *, float pitch);
int32_t thug_audio_play_buffer(const ThugAudioSampleBinding *, const ThugSpatialSoundVolume *, float pitch);
uint32_t thug_sound_play(const ThugSoundConfiguration *, uint32_t checksum, ThugSpatialSoundVolume *, float pitch, uint32_t name, const ThugSoundPlaybackControls *, const char *filename);
#endif
