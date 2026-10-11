#ifndef THUG_GAME_JUMP_H
#define THUG_GAME_JUMP_H
#include "components.h"
extern const uint32_t thug_jump_rail_events[3];
void thug_skater_jump_turn(ThugSkaterPhysics *);
void thug_skater_jump(ThugSkaterPhysics *,const ThugScriptStructure *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_skater_jump_command(ThugSkaterPhysics *,const ThugScriptStructure *,ThugScriptInstance *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
/* Fixed original member ABI; caller supplies scoped component services. */
uint32_t thug_skater_jump_member(void *,ThugScriptStructure *,ThugScriptInstance *);
#endif
