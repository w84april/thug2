#include "animation.h"
#include "stats.h"
#include "../core/vector.h"
#include "../network/queue.h"

/* 004317c0 / 004317e0: preserve the original forward word copies, including
 * overlap. These only update stored shadow vectors; they do not render it. */
void thug_shadow_set_position(void *shadow,const float position[4]) {
    thug_vector_copy((float *)((uint8_t *)shadow+0x1c),position);
}
void thug_shadow_set_up(void *shadow,const float up[4]) {
    thug_vector_copy((float *)((uint8_t *)shadow+0x2c),up);
}
/* 00580880: 004619f0 ignores the supplied component registry and reloads the
 * separate general lookup manager at006f0fc0. */
void *thug_skater_camera_object(const ThugSkaterBody *body) {
    uint32_t index;__builtin_memcpy(&index,(const uint8_t *)body+0x2bc,4);
    return thug_object_find_global(thug_component_type_registry,
        index==1?0xe17b231a:0x967c138c);
}
/* 00511420: copy the current skating-state flip to every animation state and
 * the network queue, without toggling the skating state or its timestamp. */
void thug_skater_sync_flip(ThugSkaterFlipComponent *component,const ThugDiagnostics *d,const ThugMemory *m) {
    uint32_t index;__builtin_memcpy(&index,(const uint8_t *)component->base.owner+0x2bc,4);
    ThugQueueClient *client=thug_network_get_client(thug_network_state,index);
    ThugSkaterState *state=(void *)thug_object_find_component(component->base.owner,0x43686585);
    uint32_t time=client->time,flipped=state->stat_modifier_selector;
    const ThugSkaterBody *body=component->base.owner;
    thug_animation_component_set_flipped(component->animation,body->object_id,flipped,time,1,d,m);
}
