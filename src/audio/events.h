#ifndef THUG_AUDIO_EVENTS_H
#define THUG_AUDIO_EVENTS_H
#include "device.h"
#include "../game/skater.h"
typedef struct ThugSoundComponent {
    ThugObjectComponent component;
    uint32_t unknown_14, state;
    uint8_t unknown_1c[2], state_flag, unknown_1f[5];
    float impact_volume;
} ThugSoundComponent;
void thug_sound_dispatch_impact(uint32_t event, uint32_t material, const float position[4],
    float volume, float pitch, float selection, uint32_t network,
    const ThugDiagnostics *, const ThugMemory *);
void thug_sound_component_impact(const ThugSoundComponent *, float intensity, uint32_t material,
    const ThugDiagnostics *, const ThugMemory *);
void thug_sound_component_land(const ThugSoundComponent *, float intensity, uint32_t material,
    const ThugDiagnostics *, const ThugMemory *);
#endif
