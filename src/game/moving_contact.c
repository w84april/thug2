#include "moving_contact.h"


#include "../core/matrix.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>
/* 0x004fc400. Capture the timestamp before reading the timer. */
uint32_t thug_skater_moving_contact_age(const ThugSkaterGroundGate *gate) {
    uint32_t timestamp=gate->release_time;
    return thug_elapsed_time()+thug_timer_offset-timestamp;
}
_Static_assert(offsetof(ThugMovingContact, orientation) == 0xc, "Contact orientation");
_Static_assert(offsetof(ThugMovingContact, position) == 0x4c, "Contact position");
_Static_assert(offsetof(ThugMovingContact, displacement) == 0x5c, "Contact displacement");
_Static_assert(offsetof(ThugMovingContact, rotation) == 0x6c, "Contact rotation");
_Static_assert(offsetof(ThugMovingContact, orientation_changed) == 0xac, "Contact flag");
_Static_assert(offsetof(ThugSkaterGroundGate, contact) == 0x18, "Contact pointer");
_Static_assert(offsetof(ThugSkaterGroundGate, released_owner) == 0x6c, "Released owner");
_Static_assert(offsetof(ThugSkaterGroundGate, release_time) == 0x70, "Release time");
_Static_assert(offsetof(ThugSkaterState, moving_contact_locked) == 0x88, "Moving contact lock");

/* 0x00416e70. Rotation storage and padding remain uninitialized. */
ThugMovingContact *thug_moving_contact_initialize(ThugMovingContact *contact, ThugSkaterBody *owner) {
    contact->reference.previous = contact->reference.next = NULL;
    contact->reference.object = (ThugReferencedObject *)owner;
    if (owner) thug_object_reference_link((ThugReferencedObject *)owner, &contact->reference);
    owner = (ThugSkaterBody *)contact->reference.object;
    thug_matrix_copy(contact->orientation, owner->orientation);
    thug_vector_copy(contact->position, owner->position);
    contact->displacement[0] = contact->displacement[1] = contact->displacement[2] = 0;
    contact->displacement[3] = 1;
    contact->orientation_changed = 0;
    return contact;
}

static void affine(float matrix[16]) {
    matrix[12] = matrix[13] = matrix[14] = 0; matrix[15] = 1;
    matrix[3] = matrix[7] = matrix[11] = 0;
}

/* 0x00416f00. Translation is measured before the rotation comparison. An
 * orientation change also carries the point around the owner's saved position. */
uint8_t thug_moving_contact_update(ThugMovingContact *contact, const float position[4]) {
    ThugSkaterBody *owner = (ThugSkaterBody *)contact->reference.object;
    if (!owner) return 0;
    thug_vector_difference(contact->displacement, owner->position, contact->position);
    if (thug_matrix_equal(contact->orientation, owner->orientation)) contact->orientation_changed = 0;
    else {
        contact->orientation_changed = 1;
        float relative[4], transformed[4], inverse[16];
        thug_vector_difference(relative, position, contact->position);
        thug_matrix_copy(inverse, contact->orientation); affine(inverse);
        thug_matrix_rigid_inverse(inverse);
        thug_matrix_copy(contact->rotation, owner->orientation); affine(contact->rotation);
        thug_matrix_multiply(contact->rotation, contact->rotation, inverse);
        thug_matrix_transform_vector(contact->rotation, transformed, relative);
        for (unsigned i = 0; i < 4; ++i) {
            double delta = thug_platform_round_x87_single((double)transformed[i]-relative[i]);
            if (i >= 2) delta = (float)delta;
            contact->displacement[i] = (float)thug_platform_round_x87_single(delta+contact->displacement[i]);
        }
        thug_matrix_copy(contact->orientation, owner->orientation);
    }
    thug_vector_copy(contact->position, owner->position);
    return 1;
}

/* 0x00427c70. The allocator observes the detached reference and retained
 * component pointer. Clear that pointer and record time only after release. */
void thug_skater_moving_contact_release(ThugSkaterGroundGate *component, const ThugMemory *memory) {
    ThugMovingContact *contact = component->contact;
    if (!contact) return;
    component->released_owner = contact->reference.object;
    thug_object_reference_destroy(&contact->reference);
    memory->release(memory->context, contact);
    component->contact = NULL;
    component->release_time = thug_elapsed_time() + thug_timer_offset;
}
/* 0x00427cb0. A dead owner's contact is disposed during this query. */
uint8_t thug_skater_has_moving_contact(ThugSkaterGroundGate *component, const ThugMemory *memory) {
    if (!component->contact) return 0;
    if (component->contact->reference.object) return 1;
    thug_skater_moving_contact_release(component, memory);
    return 0;
}

/* 0x00427cd0. Report only a newly acquired contact. Reuse a live matching
 * owner, release a changed/dead owner, and clear contact on a static surface. */
uint8_t thug_skater_moving_contact_acquire(ThugSkaterGroundGate *component, ThugCollisionProbe *probe, const ThugMemory *memory) {
    if (thug_collision_probe_has_moving_object(probe)) {
        ThugMovingContact *contact = component->contact;
        if (contact && (!contact->reference.object || contact->reference.object != thug_collision_probe_moving_object(probe)))
            thug_skater_moving_contact_release(component, memory);
        contact = component->contact;
        if (contact) {
            if (contact->reference.object) return 0;
            thug_skater_moving_contact_release(component, memory);
        }
        contact = memory->allocate(memory->context, sizeof(*contact), 1);
        component->contact = contact ? thug_moving_contact_initialize(contact,
            (ThugSkaterBody *)thug_collision_probe_moving_object(probe)) : NULL;
        return 1;
    }
    if (component->contact) thug_skater_moving_contact_release(component, memory);
    return 0;
}
/* 0x0043eb80. An explicit owner always replaces the old contact, even when it
 * names the same object. The allocator supplies fresh storage for its constructor. */
ThugMovingContact *thug_skater_moving_contact_set_owner(ThugSkaterGroundGate *component,
    ThugSkaterBody *owner,const ThugMemory *memory) {
    if(component->contact)thug_skater_moving_contact_release(component,memory);
    ThugMovingContact *contact=memory->allocate(memory->context,sizeof(*contact),1);
    component->contact=contact?thug_moving_contact_initialize(contact,owner):NULL;
    return component->contact;
}
/* 0x005021d0. Its caller requires successful contact allocation. Each velocity
 * lane is read/subtracted/stored in order, including the fourth lane. */
void thug_skater_adjust_moving_contact(ThugSkaterPhysics *physics, const ThugMemory *memory) {
    if (physics->state->moving_contact_locked) return;
    if (!thug_skater_moving_contact_acquire(physics->ground_gate, &physics->surface_probe, memory)) return;
    const ThugSkaterBody *owner = (ThugSkaterBody *)physics->ground_gate->contact->reference.object;
    float *velocity = physics->body->velocity;
    for (unsigned i = 0; i < 4; ++i)
        velocity[i] = (float)thug_platform_round_x87_single((double)velocity[i]-owner->velocity[i]);
}

/* 0x00427dd0. Release a dead contact before looking up its retained owner.
 * The general inverse is followed by rotation, not affine translation. */
void thug_skater_store_contact_relative(ThugSkaterGroundGate *component,const ThugMemory *memory) {
    ThugSkaterBody *owner=0;
    if(component->contact) {
        owner=(void *)component->contact->reference.object;
        if(!owner)thug_skater_moving_contact_release(component,memory);
    }
    if(!owner)owner=(void *)component->released_owner;
    if(!owner)return;
    float position[4],matrix[16],transformed[4];
    thug_vector_copy(position,owner->position);thug_matrix_copy(matrix,owner->orientation);
    for(unsigned i=0;i<4;++i)
        component->relative_position[i]=(float)thug_platform_round_x87_single((double)component->body->position[i]-position[i]);
    thug_matrix_inverse(matrix);
    thug_matrix_rotate_vector(matrix,transformed,component->relative_position);
    thug_vector_copy(component->relative_position,transformed);
}

static float quiet_lane(float value) {
    uint32_t bits;__builtin_memcpy(&bits,&value,4);
    if((bits&0x7f800000)==0x7f800000&&(bits&0x7fffff))bits|=0x400000;
    __builtin_memcpy(&value,&bits,4);return value;
}
/* 00427a00. Use the retained owner at +6c, independently of the live contact.
 * Snapshot input before output writes; original x87 loads quiet only X/Y on
 * the untranslated path, while Z/W retain their raw bit patterns. */
float *thug_skater_contact_world_position(const ThugSkaterGroundGate *component,float out[4]) {
    float position[4];__builtin_memcpy(position,component->relative_position,16);
    position[1]=quiet_lane(position[1]);
    if(component->released_owner) {
        float matrix[16],rotated[4];
        thug_matrix_copy(matrix,((const ThugSkaterBody *)component->released_owner)->orientation);
        thug_matrix_rotate_vector(matrix,rotated,position);
        const ThugSkaterBody *owner=(const void *)component->released_owner;
        for(unsigned i=0;i<4;++i)
            position[i]=(float)thug_platform_round_x87_single((double)rotated[i]+owner->position[i]);
    }
    position[0]=quiet_lane(position[0]);
    __builtin_memcpy(out,position,16);return out;
}
