#ifndef THUG_AUDIO_JUMP_H
#define THUG_AUDIO_JUMP_H
#include "events.h"
void thug_sound_jump_for_state(const ThugSoundComponent *,float,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void thug_sound_component_jump(const ThugSoundComponent *,float,uint32_t,const ThugDiagnostics *,const ThugMemory *);
#endif
