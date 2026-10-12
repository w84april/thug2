/* 0047b4e0. Reuse the existing original voice search and device stop routines. */
#include "../../src/audio/device.h"
extern int32_t thug_sound_find_voice_draft(const ThugSoundConfiguration *,uint32_t);
extern void thug_audio_stop_slot_draft(uint32_t);
uint8_t thug_sound_stop_draft(const ThugSoundConfiguration *manager,uint32_t key){
 if(thug_sound_disabled())return 1;
 int32_t index=thug_sound_find_voice_draft(manager,key);if(index<0)return 0;
 thug_audio_stop_slot_draft((uint32_t)index);return 1;
}
