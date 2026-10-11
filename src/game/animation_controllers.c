#include "animation_controllers.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../platform/math.h"
#include "../script/values.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
_Static_assert(sizeof(ThugAnimationController)==0x14,"Controller prefix");
_Static_assert(sizeof(ThugTimedAnimationController)==0x24,"Timed controller");
_Static_assert(sizeof(ThugWeightedAnimationController)==0x24,"Weighted controller");
_Static_assert(sizeof(ThugBoneAnimationRecord)==0x64,"Bone record stride");
_Static_assert(sizeof(ThugBoneAnimationController)==0x1a4,"Bone controller");
_Static_assert(sizeof(ThugPoseAnimationController)==0x854,"Pose controller allocation");
static void configure_base(ThugAnimationController *c,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; thug_animation_configure_controller(c,p);
}
const ThugAnimationControllerMethods thug_timed_animation_methods={.dispose=thug_timed_animation_delete,.command=thug_timed_animation_command,.configure=thug_timed_animation_configure,.update=thug_timed_animation_update};
const ThugAnimationControllerMethods thug_weighted_animation_methods={.dispose=thug_weighted_animation_delete,.command=thug_weighted_animation_command,.configure=configure_base,.update=thug_animation_controller_idle};
const ThugAnimationControllerMethods thug_flag_animation_methods={.dispose=thug_flag_animation_delete,.command=thug_animation_unhandled_command,.configure=thug_flag_animation_configure,.update=thug_animation_controller_idle};
const ThugAnimationControllerMethods thug_pose_animation_methods={.dispose=thug_pose_animation_delete,.command=thug_animation_unhandled_command,.configure=configure_base,.update=thug_animation_controller_idle};
const ThugAnimationControllerMethods thug_bone_animation_methods={.dispose=thug_bone_animation_delete,.command=thug_bone_animation_command,.configure=thug_bone_animation_configure,.update=thug_bone_animation_update};
static float quiet(float value) {
    uint32_t word; __builtin_memcpy(&word,&value,4);
    if ((word&0x7f800000)==0x7f800000 && (word&0x7fffff)) word|=0x400000;
    __builtin_memcpy(&value,&word,4); return value;
}
/* 0x0047d620 and 0x00419af0. An existing asset and a valid sentinel are required. */
double thug_animation_state_duration(const ThugAnimationState *state,uint32_t name,const ThugDiagnostics *diagnostics) {
    const float *data=thug_animation_find(state->animation_namespace+name,0,diagnostics); return (double)quiet(*data);
}
double thug_animation_component_duration(const ThugAnimationComponent *component,uint32_t name,const ThugDiagnostics *diagnostics) {
    if (component->state->id==UINT32_MAX) return 0;
    return thug_animation_state_duration(component->state,name,diagnostics);
}
/* 0x00487770. Flag precedence is loop, ping-pong, then balance. */
uint8_t thug_animation_parse_loop(uint32_t *out,const ThugScriptStructure *p) {
    *out=0;
    if (thug_script_has_flag(p,0x4f792e6c)) *out=1;
    else if (thug_script_has_flag(p,0x3153e314)) *out=2;
    else if (thug_script_has_flag(p,0x6d941203)) *out=3;
    return 1;
}
/* 0x004877e0. Numeric endpoints override named endpoints. Frame numbers first
 * truncate to a signed integer, then multiply by the original float 1/60. */
uint8_t thug_animation_parse_range(float *first,float *last,float current,float duration,const ThugScriptStructure *p,uint32_t unused) {
    (void)unused; float start=0,end=duration; uint32_t name=0;
    const uint32_t keys[2]={0x46e55e8f,0x28782d3b}; float *ends[2]={&start,&end};
    for (unsigned i=0;i<2;++i) {
        name=0;
        if (thug_script_get_checksum(p,keys[i],&name,0)) switch (name) {
            case 0x6086aa70: *ends[i]=0; break;
            case 0x230ccbf4: __builtin_memcpy(ends[i],&current,4); break;
            case 0x617fe530: *ends[i]=(float)R((double)duration*.5); break;
            case 0xff03cc4e: __builtin_memcpy(ends[i],&duration,4); break;
        }
    }
    for (unsigned i=0;i<2;++i) {
        float number=0;
        if (thug_script_get_float(p,keys[i],&number,0)) {
            if (thug_script_has_flag(p,0xd029f619)) __builtin_memcpy(ends[i],&number,4);
            else *ends[i]=(float)R((double)(int32_t)thug_truncate_double_low_word(number)*(double)0.01666666753590107f);
        }
    }
    if (thug_script_has_flag(p,0xf8cfd515)) { *first=quiet(end); *last=quiet(start); }
    else { *first=quiet(start); *last=quiet(end); }
    return 1;
}
/* 0x004a5350. The owned timeline is only the 0x34-byte base prefix. */
ThugAnimationController *thug_timed_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugTimedAnimationController *c=(ThugTimedAnimationController *)base;
    thug_animation_controller_initialize(base,channel); base->methods=&thug_timed_animation_methods;
    c->reader=thug_create_animation_reader(m); c->animation=thug_animation_reader_set_mode(c->reader,0,d);
    c->animation_namespace=thug_animation_component_namespace((ThugAnimationComponent *)thug_object_find_component(thug_animation_controller_body(base),0x7149b753));
    ThugAnimationChannel *timeline=thug_allocate_zeroed(0x34,m);
    c->timeline=timeline ? thug_animation_timeline_initialize(timeline) : NULL; c->animation=NULL; return base;
}
/* 0x004a4d50 and 0x004a5400. */
void thug_timed_animation_destroy(ThugAnimationController *base,const ThugMemory *m) {
    ThugTimedAnimationController *c=(ThugTimedAnimationController *)base; base->methods=&thug_timed_animation_methods;
    if (c->reader) { thug_release_animation_reader(c->reader,m); c->reader=NULL; }
    if (c->timeline) { c->timeline->methods->dispose(c->timeline,1,m); c->timeline=NULL; }
    if (c->animation) c->animation=NULL;
    thug_animation_controller_destroy(base);
}
ThugAnimationController *thug_timed_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_timed_animation_destroy(c,m); if ((uint8_t)flags&1) m->release(m->context,c); return c;
}
/* 0x004a4dd0. The range is based on zero and the selected asset duration. */
void thug_timed_animation_configure(ThugAnimationController *base,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)m; ThugTimedAnimationController *c=(ThugTimedAnimationController *)base;
    thug_animation_controller_configure(base,p); uint32_t name; thug_script_get_checksum(p,0x6c2bfb7f,&name,1);
    const ThugAnimationComponent *component=(ThugAnimationComponent *)thug_object_find_component(thug_animation_controller_body(base),0x7149b753);
    float duration=(float)thug_animation_component_duration(component,name,d),first=0,last=0;
    thug_animation_parse_range(&first,&last,0,duration,p,0); uint32_t loop; thug_animation_parse_loop(&loop,p);
    float speed=1,offset=0; thug_script_get_float(p,0xf0d90109,&speed,0); thug_script_get_float(p,0x230ccbf4,&offset,0);
    c->timeline->methods->timeline(c->timeline,name,first,last,loop,0,speed);
    if (offset!=0) thug_animation_offset_time(c->timeline,offset);
    c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d);
}
/* 0x004a54a0. All five commands, including the refresh fallthrough result. */
uint32_t thug_timed_animation_command(ThugAnimationController *base,uint32_t command,const ThugScriptStructure *p,void *script,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugTimedAnimationController *c=(ThugTimedAnimationController *)base;
    switch(command) {
        case 0x5f495ae0: c->animation=thug_animation_reader_set_mode(c->reader,0,d); return 2;
        case 0x6aaeb76f: {
            float offset; thug_script_get_float(p,0x06c9f278,&offset,1);
            double speed=c->timeline->speed; c->timeline->speed=0;
            float saved=(float)R(speed*60.0);
            c->timeline->current=(float)R((double)offset+c->timeline->current);
            c->timeline->methods->update(c->timeline,d,m);
            c->timeline->speed=(float)R((double)saved*(double)0.01666666753590107f); return 1;
        }
        case 0xbd4edd44: { float speed; thug_script_get_float(p,0xf0d90109,&speed,1); c->timeline->speed=(float)R((double)speed*(double)0.01666666753590107f); return 1; }
        case 0xf5e2b871: c->timeline->direction=c->timeline->direction ? 0 : UINT32_MAX; return 1;
        case 0xd63a1b81: {
            ThugScriptInstance *instance=script; uint32_t word; __builtin_memcpy(&word,&c->timeline->current,4);
            thug_script_set_float_bits(instance->arguments,0xaaecb346,word,m);
            thug_script_set_checksum(instance->arguments,0x659bf355,c->timeline->animation_name,m);
            ThugScriptStructure *out=instance->arguments; uint8_t finished=thug_animation_timeline_finished(c->timeline);
            thug_script_set_integer(out,0x4966cc11,finished,m); return 1;
        }
        default: return 2;
    }
}
/* 0x004a5010, 0x004a4820 and 0x004a50b0. */
ThugAnimationController *thug_weighted_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel,ThugSkaterBody *owner,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugWeightedAnimationController *c=(ThugWeightedAnimationController *)base;
    thug_animation_controller_initialize(base,channel); base->methods=&thug_weighted_animation_methods;
    base->unknown_8=(uintptr_t)(channel ? thug_animation_controller_body(base) : owner);
    c->reader=thug_create_animation_reader(m); c->animation=thug_animation_reader_set_mode(c->reader,0,d);
    c->animation_namespace=thug_animation_component_namespace((ThugAnimationComponent *)thug_object_find_component((ThugSkaterBody *)(uintptr_t)base->unknown_8,0x7149b753));
    c->animation=NULL; c->weight=0; return base;
}
void thug_weighted_animation_destroy(ThugAnimationController *base,const ThugMemory *m) {
    ThugWeightedAnimationController *c=(ThugWeightedAnimationController *)base; base->methods=&thug_weighted_animation_methods;
    if (c->reader) { thug_release_animation_reader(c->reader,m); c->reader=NULL; }
    c->animation=NULL; thug_animation_controller_destroy(base);
}
ThugAnimationController *thug_weighted_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_weighted_animation_destroy(c,m); if ((uint8_t)flags&1) m->release(m->context,c); return c;
}
/* 0x004a4890. */
uint32_t thug_weighted_animation_command(ThugAnimationController *base,uint32_t command,const ThugScriptStructure *p,void *script,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)script; ThugWeightedAnimationController *c=(ThugWeightedAnimationController *)base; uint32_t name;
    switch(command) {
        case 0x5f495ae0: c->animation=thug_animation_reader_set_mode(c->reader,0,d); return 2;
        case 0x5e3f0f17:
            name=0;
            if (!thug_script_get_checksum(p,0xd697a799,&name,0)) thug_script_get_checksum(p,0x6c2bfb7f,&name,0);
            if (name) c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d);
            thug_script_get_float(p,0xc6ae16ac,&c->weight,1); return 1;
        case 0xaf2fae19:
            if (!thug_script_get_checksum(p,0xd697a799,&name,0)) thug_script_get_checksum(p,0x6c2bfb7f,&name,1);
            thug_script_get_float(p,0xc6ae16ac,&c->weight,0);
            c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d); return 1;
        case 0xc68365eb:
            thug_script_get_checksum(p,0x98549ba4,&name,1);
            if (c->reader) { thug_release_animation_reader(c->reader,m); c->reader=NULL; }
            c->reader=thug_create_animation_reader(m); thug_animation_reader_set_mode(c->reader,0,d);
            c->animation=thug_animation_reader_select(c->reader,c->animation_namespace+name,d); return 1;
        default: return 2;
    }
}
/* 0x004e2c50, 0x004e2c80, 0x004e2cf0 and 0x004e2c90. */
ThugAnimationController *thug_flag_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel) {
    ThugFlagAnimationController *c=(ThugFlagAnimationController *)base; thug_animation_controller_initialize(base,channel);
    c->first=c->second=0; base->methods=&thug_flag_animation_methods; return base;
}
void thug_flag_animation_destroy(ThugAnimationController *base) { base->methods=&thug_flag_animation_methods; thug_animation_controller_destroy(base); }
ThugAnimationController *thug_flag_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_flag_animation_destroy(c); if ((uint8_t)flags&1) m->release(m->context,c); return c;
}
void thug_flag_animation_configure(ThugAnimationController *base,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; ThugFlagAnimationController *c=(ThugFlagAnimationController *)base; thug_animation_controller_configure(base,p); uint32_t value;
    if (thug_script_get_integer(p,0x0c7a712c,&value,0)) c->first=value!=0;
    if (thug_script_get_integer(p,0x6ea3704a,&value,0)) c->second=value!=0;
}
/* 0x004a5730, 0x004a4d20, 0x004a5320 and shared 0x0051adc0. */
ThugAnimationController *thug_pose_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel) {
    ThugPoseAnimationController *c=(ThugPoseAnimationController *)base; thug_animation_controller_initialize(base,channel); base->methods=&thug_pose_animation_methods;
    for (unsigned i=0;i<64;++i) { c->vectors[i][0]=c->vectors[i][1]=c->vectors[i][2]=0; c->vectors[i][3]=1; } return base;
}
void thug_pose_animation_destroy(ThugAnimationController *base) { base->methods=&thug_pose_animation_methods; thug_animation_controller_destroy(base); }
ThugAnimationController *thug_pose_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_pose_animation_destroy(c); if ((uint8_t)flags&1) m->release(m->context,c); return c;
}
uint32_t thug_animation_unhandled_command(ThugAnimationController *c,uint32_t command,const ThugScriptStructure *p,void *s,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)c; (void)command; (void)p; (void)s; (void)d; (void)m; return 2;
}
/* 0x00488300. Only three of four trailing flag bytes are initialized. */
ThugAnimationController *thug_bone_animation_initialize(ThugAnimationController *base,ThugAnimationChannel *channel,ThugSkaterBody *owner) {
    ThugBoneAnimationController *c=(ThugBoneAnimationController *)base; thug_animation_controller_initialize(base,channel); base->methods=&thug_bone_animation_methods;
    for (unsigned i=0;i<4;++i) { float *q=c->records[i].quaternion; q[0]=q[1]=q[2]=0; q[3]=1; }
    base->unknown_8=(uintptr_t)(channel ? thug_animation_controller_body(base) : owner);
    for (unsigned i=0;i<4;++i) {
        ThugBoneAnimationRecord *r=c->records+i; r->enabled=0; r->flag=1; r->name=UINT32_MAX; r->target=r->index=0; r->scale=1;
        float *vectors[4]={r->rotation,r->velocity,r->vector,r->quaternion};
        for (unsigned j=0;j<4;++j) { vectors[j][0]=vectors[j][1]=vectors[j][2]=0; vectors[j][3]=1; }
        r->use_vector=1;
    } return base;
}
/* 0x00487d40 and 0x004880d0. */
void thug_bone_animation_destroy(ThugAnimationController *base) { base->methods=&thug_bone_animation_methods; thug_animation_controller_destroy(base); }
ThugAnimationController *thug_bone_animation_delete(ThugAnimationController *c,uint32_t flags,const ThugMemory *m) {
    thug_bone_animation_destroy(c); if ((uint8_t)flags&1) m->release(m->context,c); return c;
}
/* 0x00487d60, 0x00487d90, 0x00487dc0 and 0x00487de0. */
uint32_t thug_bone_animation_find(const ThugBoneAnimationController *c,uint32_t name) {
    for (uint32_t i=0;i<4;++i) if(c->records[i].name==name) return i; return UINT32_MAX;
}
uint8_t thug_bone_animation_all_enabled(const ThugBoneAnimationController *c) {
    for (unsigned i=0;i<4;++i) if(c->records[i].name!=UINT32_MAX && !c->records[i].enabled) return 0; return 1;
}
void thug_bone_animation_enable_all(ThugBoneAnimationController *c) { for (unsigned i=0;i<4;++i) if(c->records[i].name!=UINT32_MAX)c->records[i].enabled=1; }
void thug_bone_animation_disable_all(ThugBoneAnimationController *c) { for (unsigned i=0;i<4;++i) if(c->records[i].name!=UINT32_MAX)c->records[i].enabled=0; }
/* 0x00488170 and 0x00488220. Sequential raw word copies retain overlap effects. */
void thug_bone_animation_set_rotation(ThugBoneAnimationController *c,const float *source) {
    for (unsigned i=0;i<4;++i) if(c->records[i].name!=UINT32_MAX) for(unsigned j=0;j<4;++j) __builtin_memcpy(c->records[i].rotation+j,source+j,4);
}
void thug_bone_animation_set_velocity(ThugBoneAnimationController *c,const float *source) {
    for (unsigned i=0;i<4;++i) if(c->records[i].name!=UINT32_MAX) for(unsigned j=0;j<4;++j) __builtin_memcpy(c->records[i].velocity+j,source+j,4);
}
/* 0x00488950. Valid record indices are an internal contract. */
void thug_bone_animation_setup(ThugBoneAnimationController *c,uint32_t all,uint32_t index,const ThugScriptStructure *p) {
    if (thug_script_has_name_or_flag(p,0x0c5f37cd)) {
        if ((uint8_t)all) thug_bone_animation_enable_all(c); else c->records[index].enabled=1;
    } else if (thug_script_has_name_or_flag(p,0xb0bab2ae)) {
        if ((uint8_t)all) thug_bone_animation_disable_all(c); else c->records[index].enabled=0;
    }
    ThugBoneAnimationRecord *r=c->records+index;
    thug_script_get_checksum(p,0xcab94088,&r->name,0);
    if (thug_script_get_checksum(p,0x4acee3f7,&r->target,0)) { r->use_vector=0; r->offset[0]=r->offset[1]=r->offset[2]=0; r->offset[3]=1; }
    if (thug_script_get_vector(p,0xdc741bad,r->vector,0)) r->use_vector=1;
    if (thug_script_get_vector(p,0x1f07cf31,r->offset,0)) r->use_vector=0;
    thug_script_get_integer(p,0x7af07905,&r->index,0); thug_script_get_float(p,0xf832aabe,&r->scale,0);
    float vector[4];
    if (thug_script_get_vector(p,0x0b405328,vector,0)) {
        thug_vector_degrees_to_radians(vector);
        if ((uint8_t)all) thug_bone_animation_set_rotation(c,vector); else for(unsigned j=0;j<4;++j)__builtin_memcpy(r->rotation+j,vector+j,4);
    }
    if (thug_script_get_vector(p,0x0a4cc99c,vector,0)) {
        thug_vector_degrees_to_radians(vector);
        if ((uint8_t)all) thug_bone_animation_set_velocity(c,vector); else for(unsigned j=0;j<4;++j)__builtin_memcpy(r->velocity+j,vector+j,4);
    }
    r->flag=!thug_script_has_flag(p,0xd4a8cd5f);
}
/* 0x00488b20. Configuration applies to record zero, not all records. */
void thug_bone_animation_configure(ThugAnimationController *base,const ThugScriptStructure *p,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)d; (void)m; thug_animation_controller_configure(base,p); thug_bone_animation_setup((ThugBoneAnimationController *)base,0,0,p);
}
/* 0x00488b40. Selection precedence: numeric index, name, all, default zero. */
uint32_t thug_bone_animation_command(ThugAnimationController *base,uint32_t command,const ThugScriptStructure *p,void *s,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)s; (void)d; (void)m; ThugBoneAnimationController *c=(ThugBoneAnimationController *)base;
    if (command!=0x20d24e9a && command!=0x027b2b1c && command!=0x4599fb80 && command!=0xb040e943) return 2;
    uint32_t index=0; uint8_t all=0;
    if (!thug_script_get_integer(p,0x7f8c98fe,&index,0)) {
        uint32_t name;
        if (thug_script_get_checksum(p,0x40c698af,&name,0)) index=thug_bone_animation_find(c,name);
        else all=thug_script_has_name_or_flag(p,0xc4e78e22)!=0;
    }
    if (command==0xb040e943) { thug_bone_animation_setup(c,all,index,p); return 1; }
    if (command==0x027b2b1c) return all ? thug_bone_animation_all_enabled(c) : c->records[index].enabled!=0;
    if (all) { if(command==0x20d24e9a)thug_bone_animation_enable_all(c); else thug_bone_animation_disable_all(c); }
    else c->records[index].enabled=command==0x20d24e9a;
    return 1;
}
