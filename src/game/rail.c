#include "rail.h"
#include "nodes.h"
#include "stats.h"
#include "moving_contact.h"
#include "collision_events.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include <stddef.h>
_Static_assert(offsetof(ThugRailNode,next)==0x40,"Rail link offset");
_Static_assert(offsetof(ThugRailNode,name)==0x4c,"Rail name offset");
_Static_assert(offsetof(ThugSkaterPhysics,rail_transform)==0x230,"Rail transform offset");
_Static_assert(offsetof(ThugSkaterPhysics,rail_name)==0x240,"Rail name offset");
_Static_assert(offsetof(ThugSkaterState,rail_separated_time)==0x54,"Rail time offset");
/* 0057cb60. Untransformed copies are forward, including overlap. */
float *thug_rail_point(const ThugObjectTransform *transform,float out[4],const ThugRailNode *node) {
    if(!transform->changed)return thug_vector_copy(out,node->position);
    float value[4];thug_matrix_transform_vector(transform->matrix,value,node->position);
    uint32_t x;__builtin_memcpy(&x,value,4);
    if((x&0x7f800000)==0x7f800000&&(x&0x7fffff))x|=0x400000;
    __builtin_memcpy(out,&x,4);
    for(unsigned i=1;i<4;++i)__builtin_memcpy(out+i,value+i,4);
    return out;
}
static void mark(ThugSkaterState *state) {
    if(state->rail_separated!=1) { state->rail_separated=1;state->rail_separated_time=thug_elapsed_time()+thug_timer_offset; }
}
/* 00500020. Retain the original rail adjacency gate and all four endpoint
 * distances. The middle argument is unused; only the force low byte is read. */
uint8_t thug_skater_rail_eligible(ThugSkaterPhysics *p,ThugRailNode *candidate,uint32_t unused,uint32_t force) {
    (void)unused;
    ThugSkaterState *state=p->state;
    ThugRailNode *previous=p->rail_node;
    if(state->mode==1&&state->transfer_flag_a8&&state->state_flag_d0&&
       (previous==candidate||previous==candidate->next||previous==candidate->previous))return 0;
    if(!previous)mark(state);
    else if(previous!=candidate&&previous!=candidate->next&&previous!=candidate->previous) {
        if(thug_skater_orientation_context->identifier==0xd443a2bc||!previous->next||!candidate->next)mark(state);
        else {
            ThugObjectTransform *transform=p->rail_transform;
            float from[4],to[4],differences[4][4];
            thug_rail_point(transform,to,candidate);thug_rail_point(transform,from,previous);
            thug_vector_difference(differences[0],from,to);
            thug_rail_point(transform,to,candidate->next);thug_rail_point(transform,from,previous);
            thug_vector_difference(differences[1],from,to);
            ThugRailNode *old_next=previous->next;
            thug_rail_point(transform,to,candidate);thug_rail_point(transform,from,old_next);
            thug_vector_difference(differences[2],from,to);
            old_next=previous->next;
            thug_rail_point(transform,to,candidate->next);thug_rail_point(transform,from,old_next);
            thug_vector_difference(differences[3],from,to);
            unsigned i=0;
            for(;i<4;++i)if(!(__builtin_fabs(thug_vector_length(differences[i]))>6))break;
            if(i==4)mark(p->state);
        }
    }
    state=p->state;
    if(!state->rail_separated) {
        uint32_t timestamp=p->rail_reentry_time,delay=p->rail_retry_delay;
        if(thug_elapsed_time()+thug_timer_offset-timestamp<=delay)return 0;
    }
    if((uint8_t)force)return 1;
    if(p->state->mode==4)return 0;
    if(!p->state->transition_flag_38)return 1;
    return p->body->velocity[1]>0;
}

/* 005092e0. Follow predecessor links to the first TriggerScript
 * property. An explicit zero stops the search. The two cycle guards retain
 * the original start pointer and half-speed predecessor traversal. */
void thug_skater_rail_event(ThugSkaterPhysics *p,const uint32_t events[3],
    const ThugDiagnostics *d,const ThugMemory *m) {
    ThugRailNode *start=p->rail_node,*rail=start;
    if(!rail)return;
    if(!p->rail_transform)p->rail_transform=thug_game_context->rail_transform;
    ThugScriptStructure *node=thug_node_find(rail->name,0);
    if(!node)return;
    uint32_t script=0;
    if(!thug_script_get_checksum(node,0x2ca8a299,&script,0)) {
        ThugRailNode *slow=rail;unsigned alternate=0;
        rail=rail->previous;
        while(rail&&rail!=start&&rail!=slow) {
            node=thug_node_find(rail->name,1);
            if(thug_script_get_checksum(node,0x2ca8a299,&script,0))break;
            rail=rail->previous;
            if(alternate)slow=slow->previous;
            alternate^=1;
        }
    }
    if(!script)return;
    uint32_t name=0;thug_script_get_checksum(node,0xa1dc81f9,&name,1);
    ThugSkaterState *state=p->state;
    uint8_t changed=name!=p->ground_value_244;
    if(state->rail_node_changed!=changed) {
        state->rail_node_changed=changed;state->rail_node_changed_time=thug_elapsed_time()+thug_timer_offset;
    }
    p->rail_name=name;p->ground_value_244=name;
    ThugSkaterGroundGate *gate=p->ground_gate;
    ThugReferencedObject *owner=0;
    if(gate->contact) {
        owner=gate->contact->reference.object;
        if(!owner)thug_skater_moving_contact_release(gate,m);
    }
    thug_collision_event_start(p->collision_events,events,p->rail_name,0,owner,d,m);
}
