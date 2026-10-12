/* Unverified startup candidates. Original clip/controller callees are reused. */
#include "../../src/game/animation_controllers.h"
#include "../../src/game/ui.h"
#include "../../src/script/params.h"
#include "../../src/script/values.h"
static ThugScriptStructure *parameters(const ThugMemory *m){ThugScriptStructure *s=thug_script_structure_allocate(8,m);return s?thug_script_structure_initialize(s):0;}
static void release_parameters(ThugScriptStructure *s,const ThugMemory *m){if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}}
static void set_float(ThugScriptStructure *s,uint32_t key,float value,const ThugMemory *m){uint32_t bits;__builtin_memcpy(&bits,&value,4);thug_script_set_float_bits(s,key,bits,m);}
static void create_controller(ThugAnimationChannel *c,uint32_t type,const ThugScriptStructure *bone,uint32_t mirrored,const ThugDiagnostics *d,const ThugMemory *m){
    ThugScriptStructure *s=parameters(m);thug_script_set_checksum(s,0x7321a8d6,type,m);
    if(bone)thug_script_set_structure_copy(s,0,bone,m);
    if(type==0xdf5c091a)thug_script_set_integer(s,0x0c7a712c,(uint8_t)mirrored,m);
    thug_animation_create_controller(c,s,d,m);release_parameters(s,m);
}
static void controller_commands(ThugAnimationChannel *c,uint32_t command,ThugScriptStructure *s,const ThugDiagnostics *d,const ThugMemory *m){
    for(int32_t i=0;i<c->count;i++){ThugAnimationController *controller=c->controllers[i];controller->methods->command(controller,command,s,0,d,m);}
}
/* 004823c0, eight original stack arguments. Ghidra misses cleanup on481c00
 * and consequently mislabels the clip checksum as an unaff_retaddr. */
void thug_animation_channel_start_clip_v1(ThugAnimationChannel *c,uint32_t name,float first,float last,uint32_t loop,float fade,float speed,uint32_t mirrored,const ThugScriptStructure *options,const ThugDiagnostics *d,const ThugMemory *m){
    thug_animation_clear_events(c,m);thug_animation_load_events(c,name,m);c->unknown_38=2;
    uint32_t rate=0x3c888889;__builtin_memcpy(&c->fade_rate,&rate,4);
    create_controller(c,loop==3?0x6d941203:0xcb4533ff,0,0,d,m);
    float weight=0;uint32_t secondary=name;
    if(options){
        ThugScriptStructure *bone=0;
        if(thug_script_get_checksum(options,0xd697a799,&secondary,0)||thug_script_has_flag(options,0x1b92121c)){
            thug_script_get_float(options,0xc6ae16ac,&weight,0);create_controller(c,0x7e1940a1,0,0,d,m);
        }
        if(thug_script_get_structure(options,0xaeeec12e,&bone,0))create_controller(c,0x26205db6,bone,0,d,m);
    }
    create_controller(c,0xdf5c091a,0,mirrored,d,m);
    ThugScriptStructure *s=parameters(m);set_float(s,0x4d747fa0,0,m);controller_commands(c,0xd0209498,s,d,m);release_parameters(s,m);
    s=parameters(m);thug_script_set_checksum(s,0x6c2bfb7f,name,m);set_float(s,0xd16b61e6,first,m);set_float(s,0xab81bb3d,last,m);thug_script_set_integer(s,0xcd8d7c1b,loop,m);set_float(s,0x8f0d24ed,fade,m);set_float(s,0xf0d90109,speed,m);thug_script_set_checksum(s,0xd697a799,secondary,m);set_float(s,0xc6ae16ac,weight,m);
    controller_commands(c,0xaf2fae19,s,d,m);release_parameters(s,m);
}
/* 004616f0: ensure owner parameters, then merge the optional supplied structure. */
void thug_ui_object_merge_parameters_v1(ThugUiObjectBase *object,const ThugScriptStructure *s,const ThugMemory *m){
    thug_ui_object_ensure_parameters(object,m);thug_script_structure_merge_optional(object->parameters,s,m);
}
