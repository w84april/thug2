#include "events.h"
#include "../core/number.h"
#include "../game/stats.h"
#include "../network/queue.h"
#include "../script/tokens.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugSoundComponent, impact_volume) == 0x24, "Sound component volume");
static float remap(float intensity, float maximum, float minimum) {
    if (minimum == 0 && maximum == 100) return intensity;
    double value = R24((double)maximum - minimum);
    value = R24(value * intensity);
    value = R24(value * (double)0.01f);
    return (float)R24(value + minimum);
}
/* 0x00444bb0. Event fallback precedes clip selection. The network notification
 * precedes attenuation/playback and does not test network-active state here.
 * Original packet byte 11 is unwritten stack padding; define it as zero, as
 * with the recovered script-spawn packet. The volume destructor is a bare RET. */
void thug_sound_dispatch_impact(uint32_t event, uint32_t material, const float position[4],
    float volume, float pitch, float selection, uint32_t network,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (thug_sound_disabled()) return;
    ThugSoundConfiguration *configuration = thug_sound_configuration;
    ThugNetworkState *state = thug_network_state;
    ThugScriptStructure *settings;
    if (!thug_sound_get_material_settings(&settings, material, 0x5c969c50)) return;
    if (!thug_script_has_name_or_flag(settings, thug_sound_event_parameter(event))) {
        ThugScriptStructure *fallback = thug_script_get_global_structure(0x64967688, 1);
        thug_script_get_structure(fallback, 0x5c969c50, &settings, 1);
    }
    ThugScriptStructure *choice = thug_sound_select_impact(settings, event, selection);
    if (!choice) return;
    ThugSoundDescriptor descriptor;
    if (!thug_sound_build_descriptor(choice, &descriptor)) return;
    if ((uint8_t)network) {
        ThugMessageSpec spec; thug_message_spec_initialize(&spec);
        ThugQueueClient *client = thug_network_get_client(state, 0);
        uint8_t payload[12];
        payload[6] = (uint8_t)event; payload[7] = (uint8_t)material;
        for (unsigned i = 0; i < 3; ++i)
            thug_script_write_half(payload + i*2, (uint16_t)thug_truncate_double_low_word(position[i]));
        payload[8] = (uint8_t)thug_truncate_double_low_word(volume);
        payload[9] = (uint8_t)thug_truncate_double_low_word(pitch);
        payload[10] = (uint8_t)thug_truncate_double_low_word(selection);
        payload[11] = 0;
        spec.data = payload; spec.length = 12; spec.id = 0x35;
        thug_queue_send_first(client, &spec, diagnostics, memory);
    }
    ThugSpatialSoundVolume spatial;
    thug_sound_volume_initialize(&spatial.volume);
    float range = (float)thug_sound_asset_distance(descriptor.checksum);
    thug_sound_spatialize(configuration, &spatial, position, range, 0, NULL, NULL);
    thug_sound_volume_scale(&spatial.volume, remap(volume, descriptor.value_74, descriptor.value_78));
    if (!thug_sound_volume_silent(&spatial.volume)) {
        float adjusted_pitch = remap(pitch, descriptor.value_6c, descriptor.value_70);
        thug_sound_play(configuration, descriptor.checksum, &spatial, adjusted_pitch, 0, NULL, descriptor.path);
    }
}
/* 0x00518dd0. Spill the percentage before applying the component's volume
 * scale. Pitch and clip selection both receive the unscaled percentage. */
void thug_sound_component_impact(const ThugSoundComponent *component, float intensity, uint32_t material,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    const ThugSkaterBody *owner = component->component.owner;
    float percentage = (float)R24((double)intensity * 100);
    float volume = (float)R24((double)percentage * component->impact_volume);
    uint8_t event = thug_sound_event_id(0x67d72d44);
    thug_sound_dispatch_impact(event, material, owner->position, volume, percentage, percentage, 1, diagnostics, memory);
}
/* 0x00518cf0. Grinding and sliding select distinct landing events. The owner
 * and both rounded percentages are captured before the event-table lookup. */
void thug_sound_component_land(const ThugSoundComponent *component, float intensity, uint32_t material,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint32_t name = component->state == 4
        ? (component->state_flag ? 0x840278cc : 0x80e4427e) : 0x1d296aec;
    const ThugSkaterBody *owner = component->component.owner;
    float percentage = (float)R24((double)intensity * 100);
    float volume = (float)R24((double)percentage * component->impact_volume);
    uint8_t event = thug_sound_event_id(name);
    thug_sound_dispatch_impact(event, material, owner->position, volume, percentage, percentage, 1, diagnostics, memory);
}
