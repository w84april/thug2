#ifndef THUG_GAME_PROFILE_H
#define THUG_GAME_PROFILE_H
#include "stats.h"
typedef struct { uint8_t unknown[0x5c]; ThugScriptStructure parameters; } ThugProfile;
typedef struct { uint8_t unknown[0x14]; ThugProfile *profiles[2]; uint32_t selected; } ThugProfileManager;
typedef struct { uint32_t trick, combo; uint8_t special, padding[3]; } ThugProfileBinding;
/* Original global7ce4b4. Indexed access retains valid-memory preconditions. */
extern ThugProfileManager *thug_profile_manager;
ThugProfile *thug_profile_current(const ThugProfileManager *);
ThugProfile *thug_profile_at(const ThugProfileManager *, uint32_t);
ThugProfile *thug_game_profile(const ThugGameContext *, const ThugScriptStructure *);
ThugProfile *thug_game_profile_at(const ThugGameContext *, uint32_t);
ThugScriptStructure *thug_profile_parameters(const ThugProfile *, uint32_t);
uint32_t thug_profile_binding_count(const ThugProfile *);
ThugProfileBinding *thug_profile_binding_initialize(ThugProfileBinding *);
/* Required QB structures/checksums and a valid index are caller contracts.
 * The original writes three uninitialized padding bytes; the port zeros them. */
void thug_profile_binding(const ThugProfile *, ThugProfileBinding *, int32_t);
#endif
