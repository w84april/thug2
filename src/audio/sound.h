#ifndef THUG_AUDIO_SOUND_H
#define THUG_AUDIO_SOUND_H
#include "../core/lookup.h"
#include "../script/params.h"
#include "../game/camera.h"

typedef struct { uint8_t id, padding[3]; uint32_t structure_name; } ThugSoundMaterial;
typedef struct { uint8_t id, padding[3]; uint32_t event_name, parameter_name; } ThugSoundEvent;
typedef struct {
    char path[104];
    uint32_t checksum;
    float value_6c, value_70, value_74, value_78, value_7c, value_80;
} ThugSoundDescriptor;
typedef struct { float channels[5]; uint32_t format; } ThugSoundVolume;
typedef struct { ThugSoundVolume volume; float position[4], distance; } ThugSpatialSoundVolume;
typedef struct { uint32_t unknown_0, volume_format; } ThugSoundConfiguration;
typedef struct {
    uint32_t checksum, unknown_4, unknown_8, unknown_c;
    float distance;
    uint32_t unknown_14, unknown_18;
} ThugSoundAsset;

/* Original globals; registration, device startup and asset loading are separate. */
extern ThugObjectLookupTable thug_sound_materials, thug_sound_events;
extern uint32_t thug_sound_device, thug_sound_mode;
extern ThugSoundConfiguration *thug_sound_configuration;
extern float thug_sound_default_distance;
extern int32_t thug_sound_asset_count_a, thug_sound_asset_count_b;
extern ThugSoundAsset thug_sound_assets_a[256], thug_sound_assets_b[256];
uint32_t thug_sound_event_parameter(uint32_t event_id);
uint32_t thug_sound_material_name(uint32_t material_id);
uint8_t thug_sound_event_id(uint32_t event_name);
uint8_t thug_sound_material_settings(uint32_t, ThugScriptStructure **, uint32_t);
uint8_t thug_sound_get_material_settings(ThugScriptStructure **, uint32_t, uint32_t);
ThugScriptStructure *thug_sound_select_weighted(const ThugScriptStructure *);
ThugScriptStructure *thug_sound_select_impact(const ThugScriptStructure *, uint32_t, float);
uint8_t thug_sound_build_descriptor(const ThugScriptStructure *, ThugSoundDescriptor *);
uint8_t thug_sound_disabled(void);
ThugSoundVolume *thug_sound_volume_initialize(ThugSoundVolume *);
void thug_sound_volume_scale(ThugSoundVolume *, float);
uint8_t thug_sound_volume_silent(const ThugSoundVolume *);
ThugSoundAsset *thug_sound_find_asset(uint32_t);
double thug_sound_asset_distance(uint32_t);
extern uint8_t thug_sound_suppressed_a, thug_sound_suppressed_b;
double thug_sound_volume_peak(const ThugSoundVolume *);
uint8_t thug_sound_spatialize(const ThugSoundConfiguration *, ThugSpatialSoundVolume *, const float position[4], float range, uint32_t curve, const ThugCamera *, const float *range_origin);
#endif
