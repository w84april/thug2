#ifndef THUG_GAME_MOVING_CONTACT_H
#define THUG_GAME_MOVING_CONTACT_H
#include "skater.h"
typedef struct ThugMovingContact {
    ThugObjectReference reference;
    float orientation[16], position[4], displacement[4], rotation[16];
    uint8_t orientation_changed, padding_ad[3];
} ThugMovingContact;
/* Construction requires a live owner, as in the original. */
ThugMovingContact *thug_moving_contact_initialize(ThugMovingContact *, ThugSkaterBody *owner);
uint8_t thug_moving_contact_update(ThugMovingContact *, const float position[4]);
void thug_skater_moving_contact_release(ThugSkaterGroundGate *, const ThugMemory *);
uint32_t thug_skater_moving_contact_age(const ThugSkaterGroundGate *);
uint8_t thug_skater_has_moving_contact(ThugSkaterGroundGate *, const ThugMemory *);
uint8_t thug_skater_moving_contact_acquire(ThugSkaterGroundGate *, ThugCollisionProbe *, const ThugMemory *);
ThugMovingContact *thug_skater_moving_contact_set_owner(ThugSkaterGroundGate *, ThugSkaterBody *, const ThugMemory *);
void thug_skater_adjust_moving_contact(ThugSkaterPhysics *, const ThugMemory *);
void thug_skater_store_contact_relative(ThugSkaterGroundGate *, const ThugMemory *);
float *thug_skater_contact_world_position(const ThugSkaterGroundGate *, float out[4]);
#endif
