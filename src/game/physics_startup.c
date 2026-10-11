#include "skater.h"
#include "../core/matrix.h"

/* 004fc5c0: the component's script initialization method. The parameter
 * structure is unused. Preserve reloads and the original individual stores. */
void thug_skater_initialize_physics(ThugSkaterPhysics *p,const ThugScriptStructure *parameters) {
    (void)parameters;
    p->friction=(float)thug_skater_get_parameter(0x78f80ec4,1,p->body);
    float *position=p->body->position;
    position[0]=0;position[1]=0;position[2]=0;position[3]=1;
    float *basis=p->body->orientation;
    for(unsigned i=0;i<16;++i)basis[i]=(i%5)==0?1:0;
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
    p->orientation_source[0]=0;p->orientation_source[1]=1;
    p->orientation_source[2]=0;p->orientation_source[3]=1;
    for(unsigned i=0;i<4;++i)p->orientation_target[i]=p->orientation_source[i];
    for(unsigned i=0;i<4;++i)p->orientation_previous[i]=p->orientation_source[i];
    p->airborne_flag_2ec=0;p->projectile_count=0;
}

/* 004fc690: finalize component links in original lookup/store order. */
void thug_skater_link_physics(ThugSkaterPhysics *p) {
    p->input=(void *)thug_object_find_component(p->body,0x27d7cd28);
    p->sound=(void *)thug_object_find_component(p->body,0x187574fa);
    p->collision_events=(void *)thug_object_find_component(p->body,0xe594f0a2);
    p->name_context=(void *)thug_object_find_component(p->body,0x270f56e1);
    p->orientation_gate=(void *)thug_object_find_component(p->body,0x52d61a0d);
    p->score_component=(void *)thug_object_find_component(p->body,0xd262802f);
    p->mode_context=(void *)thug_object_find_component(p->body,0x589e5fb3);
    p->state=(void *)thug_object_find_component(p->body,0x43686585);
    p->ground_gate=(void *)thug_object_find_component(p->body,0x408d2aa9);
    p->wall_gate=(void *)thug_object_find_component(p->body,0xd9151d4d);
    p->transfer_motion=(void *)thug_object_find_component(p->body,0x726e85aa);
    p->wall_mark=(void *)thug_object_find_component(p->body,0x380d909a);
}
