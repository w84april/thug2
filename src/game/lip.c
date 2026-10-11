#include "rail.h"
#include "nodes.h"
#include "moving_contact.h"
#include "collision_events.h"
#include "balance.h"
#include "objectives.h"
#include "../core/timing.h"
#include "../core/vector.h"
static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4);return v;}
static void flag(void *base,unsigned offset,uint8_t value) {
    uint8_t *at=(uint8_t *)base+offset;
    if(*at!=value) { *at=value;uint32_t time=thug_elapsed_time()+thug_timer_offset;__builtin_memcpy(at+4,&time,4); }
}
/* 0050bf50. Full lip state: moving contact, lip balance, release
 * triggers and rail notification. Original callees remain actual engine code. */
void thug_skater_update_lip(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    flag(p->state,0x78,0);flag(p->state,0xa8,0);flag(p->state,0x80,0);
    ThugSkaterGroundGate *gate=p->ground_gate;ThugSkaterBody *body=p->body;
    p->ground_flag_2e4=0;
    if(gate->contact) {
        if(!gate->contact->reference.object||!thug_moving_contact_update(gate->contact,body->position))
            thug_skater_moving_contact_release(gate,m);
        else {
            float point[4];body=p->body;
            thug_skater_contact_world_position(p->ground_gate,point);thug_vector_copy(body->position,point);
            thug_skater_contact_world_position(p->ground_gate,point);thug_vector_copy(p->state_saved_position,point);
            if(p->ground_gate->contact->orientation_changed) {
                thug_matrix_multiply(p->body->orientation,p->body->orientation,p->ground_gate->contact->rotation);
                thug_matrix_multiply(p->cached_orientation,p->cached_orientation,p->ground_gate->contact->rotation);
            }
        }
    }
    if(p->mode_context->identifier==0xa549b57b) {
        if(thug_gameplay_flag(thug_game_context->gameplay_flags,0xcd09e062)) {
            ThugGameplayFlags *flags=thug_game_context->gameplay_flags;
            uint32_t index=thug_script_get_global_integer(0xcd09e062,0);thug_gameplay_flag_set(flags,index);
            ((ThugBalance *)((uint8_t *)p->mode_context+0xd4))->position=0;
            ((ThugBalance *)((uint8_t *)p->mode_context+0xd4))->velocity=0;
            thug_last_gameplay_flag=1;
        }
        thug_balance_update((void *)((uint8_t *)p->mode_context+0xd4),d,m);
    }
    ThugSkaterState *state=p->state;
    if(!state->drag_coefficient_selector&&p->input->button_1c0.pressed)flag(state,0x20,1);
    if(thug_skater_handle_input_release(p,d,m)) {
        flag(p->state,0xd8,1);
        const uint32_t first[3]={7,2,0},second[3]={7,4,0};
        thug_skater_rail_event(p,first,d,m);thug_skater_rail_event(p,second,d,m);
    }
    if(p->rail_node&&word((uint8_t *)p->rail_transform+0x44)) {
        ThugScriptStructure *node=thug_node_find(p->rail_node->name,1);
        thug_script_get_checksum(node,0xa1dc81f9,&p->rail_name,1);
        thug_skater_notify(p->name_context,p->rail_name,d,m);
    }
    p->rail_update_time=thug_elapsed_time()+thug_timer_offset;
}
