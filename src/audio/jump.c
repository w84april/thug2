#include "jump.h"
#include "../platform/math.h"
/* Original 00518d60. The explicit state argument controls
 * ordinary/rail/slide selection; it is not read from the component here. */
void thug_sound_jump_for_state(const ThugSoundComponent *component,float intensity,uint32_t material,uint32_t state,
    const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    uint32_t name=state==4?(component->state_flag?0x8bb1ab02:0x8f5791b0):0x129ab922;
    const ThugSkaterBody *owner=component->component.owner;
    float percentage=(float)thug_platform_round_x87_single((double)intensity*100);
    float volume=(float)thug_platform_round_x87_single((double)percentage*component->impact_volume);
    uint8_t event=thug_sound_event_id(name);
    thug_sound_dispatch_impact(event,material,owner->position,volume,percentage,percentage,1,diagnostics,memory);
}
/* 00518ee0. Capture the component's current state before the explicit entry. */
void thug_sound_component_jump(const ThugSoundComponent *component,float intensity,uint32_t material,
    const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    thug_sound_jump_for_state(component,intensity,material,component->state,diagnostics,memory);
}
