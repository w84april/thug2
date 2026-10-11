#include "wall_marks.h"
#include "stats.h"
#include "../core/random.h"
#include "../network/queue.h"
#include "../platform/math.h"
#include "../collision/probe.h"
#include "../core/vector.h"
#include "../script/params.h"
#include <stddef.h>
_Static_assert(offsetof(ThugWallMarkEmitter,plain_texture)==0x1c,"Wall-mark texture offset");
const char thug_wall_mark_empty_texture[]=""; /* 0x006469b4 */
static void copy_words(void *out,const void *in,uint32_t count) {
    for(uint32_t i=0;i<count;++i){uint32_t word;__builtin_memcpy(&word,(const uint8_t *)in+i*4,4);__builtin_memcpy((uint8_t *)out+i*4,&word,4);}
}
/* 0x0051dbc0. Complete projection and optional queued network notification.
 * The two original unwritten packet padding bytes are explicitly zero in the
 * port; the oracle seeds only those automatic-storage bytes to the same value. */
void thug_wall_mark_emit(ThugWallMarkEmitter *emitter,uint32_t kind_arg,const float input_from[4],
    const float input_to[4],int32_t size,uint32_t send_arg,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    float from[4],to[4];copy_words(from,input_from,4);copy_words(to,input_to,4);
    float angle=(float)thug_platform_round_x87_single(thug_script_get_global_number(0x2d7df904,0)*0x1.1df46ap-6f);
    uint8_t kind=(uint8_t)kind_arg;
    float rotation=0;
    if(kind)rotation=(float)thug_platform_round_x87_single((double)(thug_random_range(90)-45)*0x1.1df46ap-6f);
    float extent=(float)(double)size;
    thug_decal_project_scene(from,to,extent,extent,rotation,angle,5000,thug_wall_mark_empty_texture,
        0x54628ed7,0,0,kind?emitter->rotated_texture:emitter->plain_texture,memory);
    if((uint8_t)send_arg) {
        ThugMessageSpec spec;thug_message_spec_initialize(&spec);
        ThugNetworkState *network=thug_network_state;
        if(thug_network_is_active(network)) {
            uint8_t packet[40];packet[0]=*((uint8_t *)emitter->owner+0x14);packet[1]=kind;packet[2]=packet[3]=0;
            copy_words(packet+4,from,4);copy_words(packet+20,to,4);copy_words(packet+36,&size,1);
            spec.data=packet;spec.length=40;spec.id=0x99;spec.group=10;spec.delivery=2;
            thug_queue_send_first(thug_network_get_client(network,0),&spec,diagnostics,memory);
        }
    }
}

#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugWallContactMark,emitter)==0x34,"Contact emitter offset");
const char thug_wall_contact_missing[]="No contact found for sticker?\n";
const char thug_wall_contact_emitting[]="sticker.............................\n";
static float read_float(const void *p,uint32_t offset) {
    float value;__builtin_memcpy(&value,(const uint8_t *)p+offset,4);return value;
}
static void *read_pointer(const void *p,uint32_t offset) {
    void *value;__builtin_memcpy(&value,(const uint8_t *)p+offset,4);return value;
}
/* 0x0051ddf0. Probe the wall, arm or emit a mark, and release the temporary
 * moving-object reference. W products retain the x87 exponent range until
 * their final stores; the X/Z bias uses distinct original spill boundaries. */
uint8_t thug_wall_contact_mark(ThugWallContactMark *effect,uint32_t kind_arg,uint32_t direction_arg,
    uint32_t height_arg,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    if(effect->cooldown>0) {effect->cooldown=(float)R24((double)effect->cooldown-1);return 0;}
    if(effect->inhibit>0)return 0;
    ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
    uint8_t kind=(uint8_t)kind_arg;
    const ThugScriptStructure *settings=thug_script_get_global_structure(0x6775e538,0);
    float distance,direction[4];
    thug_script_get_float(settings,kind?0x7b5e76c4:0xe7ab5365,&distance,1);
    if(!kind&&(uint8_t)direction_arg)thug_component_copy_direction(effect->direction,direction);
    else {
        const void *body=read_pointer(effect->body_component,12);
        if(kind) {direction[0]=-read_float(body,0x7c);direction[2]=-read_float(body,0x84);direction[3]=read_float(body,0x88);}
        else {direction[0]=read_float(body,0xac);direction[2]=read_float(body,0xb4);direction[3]=read_float(body,0xb8);}
    }
    direction[1]=0;thug_vector_normalize(direction);
    float origin[4];__builtin_memcpy(origin,(const uint8_t *)effect->owner+0x4c,16);
    origin[1]=(float)R24((double)origin[1]+(kind?30.0f:((uint8_t)height_arg?20.0f:50.0f)));
    thug_collision_probe_set_flags(&probe,0x3000,0);
    for(unsigned i=0;i<4;++i) {
        double behind=R24((double)direction[i]*12),ahead=R24((double)direction[i]*distance);
        if(i!=3){behind=(float)behind;ahead=(float)ahead;}
        probe.segment[i]=(float)R24((double)origin[i]-behind);
        probe.segment[i+4]=(float)R24(ahead+origin[i]);
    }
    uint8_t hit=thug_collision_probe_query(&probe,1,0,query);
    if(hit) {
        float from[4],to[4];
        double nx=R24((double)probe.normal[0]*12),ny=R24((double)probe.normal[1]*12);
        double nz=R24((double)probe.normal[2]*12),nw=R24((double)probe.normal[3]*12);
        to[0]=(float)R24((double)probe.point[0]-(float)nx);
        to[1]=(float)R24((double)probe.point[1]-ny);
        to[2]=(float)R24((double)probe.point[2]-nz);
        to[3]=(float)R24((double)probe.point[3]-(float)nw);
        from[0]=(float)R24(R24((double)probe.point[0]+(float)nx)+1);
        from[1]=(float)R24((double)probe.point[1]+(float)ny);
        from[2]=(float)R24((double)(float)R24((double)probe.point[2]+nz)+1);
        from[3]=(float)R24((double)probe.point[3]+(float)nw);
        if(!effect->armed) {
            if(kind){effect->armed=1;effect->inhibit=10;}
            else {
                if(diagnostics&&diagnostics->print)diagnostics->print(diagnostics->context,thug_wall_contact_emitting);
                thug_wall_mark_emit(effect->emitter,1,from,to,30,1,diagnostics,memory);
            }
        } else {
            thug_wall_mark_emit(effect->emitter,1,from,to,30,1,diagnostics,memory);
            effect->armed=0;
        }
    } else if(diagnostics&&diagnostics->print)diagnostics->print(diagnostics->context,thug_wall_contact_missing);
    if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
    return hit;
}
#undef R24
