#include "components.h"
#include "nodes.h"
#include "grind.h"
#include "../script/schedule.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t rw(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void ww(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static float rf(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void wf(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}

/* 00461410. Spawned bytecode owns a live reference but does not execute here.
 * This wrapper shares the original contract: native-only symbols return null
 * from the spawn routine and are not valid input to this object wrapper. */
ThugScriptInstance *thug_object_spawn_attached_script(ThugReferencedObject *owner,uint32_t name,
    ThugScriptStructure *parameters,uint32_t user_value,uint32_t owner_active_only,
    const ThugDiagnostics *d,const ThugMemory *m) {
    ThugScriptInstance *script=thug_script_spawn(name,parameters,0,0,UINT32_MAX,user_value,0,0,0,owner_active_only,d,m);
    if(script->owner.object){thug_object_reference_unlink(script->owner.object,&script->owner);script->owner.object=0;}
    script->owner.object=owner;
    if(owner)thug_object_reference_link(owner,&script->owner);
    return script;
}
/* 00424020. SpawnObjScript has precedence over the replace-current-script key.
 * The node ID is saved even when neither command is present. */
void thug_motion_arrive_at_node(ThugObjectComponent *component,uint32_t name,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugScriptStructure *node=thug_node_find(name,0),*parameters=0;uint32_t script;
    ww(component,0x1e8,name);
    if(thug_script_get_checksum(node,0x3aefe377,&script,0)){
        thug_script_get_structure(node,0x7031f10c,&parameters,0);
        thug_object_spawn_attached_script(component->owner,script,parameters,0,0,d,m);
        return;
    }
    if(thug_script_get_checksum(node,0x86125749,&script,0)){
        thug_script_get_structure(node,0x7031f10c,&parameters,0);
        thug_object_set_script(component->owner,script,parameters,d,m);
    }
}
/* 004269f0. The original passes all four target lanes by value, then name.
 * Extended-exponent x87 intermediates keep their 24-bit rounding order. */
uint8_t thug_motion_move_to_position(ThugObjectComponent *component,const ThugScriptStructure *parameters,
    ThugScriptInstance *script,float x,float y,float z,float w,uint32_t name) {
    (void)script;
    wf(component,0x108,x);wf(component,0x10c,y);wf(component,0x110,z);wf(component,0x114,w);
    ThugSkaterBody *body=component->owner;
    double dx=R((double)rf(component,0x108)-body->position[0]);
    double dy=R((double)rf(component,0x10c)-body->position[1]);
    double dz=R((double)rf(component,0x110)-body->position[2]);
    ww(component,0x124,0);
    double sum=R(R(dz*dz)+R(dy*dy));sum=R(R(dx*dx)+sum);
    wf(component,0x118,(float)R(__builtin_sqrt(sum)));
    for(unsigned i=0;i<4;++i)ww(component,0x18c+4*i,rw(body,0x4c+4*i));
    uint32_t flags=rw(component,0x18);
    ww(component,0x11c,0);ww(component,0x128,0);ww(component,0x18,(flags&~16u)|8);
    float time;
    if(thug_script_get_float(parameters,0x906b67ba,&time,0)){
        wf(component,0x20,(float)R((double)rf(component,0x118)/time));return 0;
    }
    float speed;
    if(thug_script_get_float(parameters,0xf0d90109,&speed,0)){
        unsigned units=2;
        if(!thug_script_has_flag(parameters,0x2ce7ee02)){
            if(thug_script_has_flag(parameters,0xaad7c80f))units=1;
            else if(thug_script_has_flag(parameters,0xa18b8f32))units=0;
        }
        thug_script_get_float(parameters,0x85894a84,(float *)((uint8_t *)component+0x124),0);
        double converted=speed;
        if(units==2){
            converted=R(R(converted*63360.0)*0x1.234568p-12);
            wf(component,0x124,(float)R(R((double)rf(component,0x124)*63360.0)*0x1.234568p-12));
        }else if(units==1){
            converted=R(converted*12.0);wf(component,0x124,(float)R((double)rf(component,0x124)*12.0));
        }
        if(rf(component,0x124)==0)wf(component,0x20,(float)converted);
        else {wf(component,0x120,(float)converted);ww(component,0x20,0);}
        return 0;
    }
    body=component->owner;
    for(unsigned i=0;i<4;++i)ww(body,0x4c+4*i,rw(component,0x108+4*i));
    ww(component,0x18,rw(component,0x18)&~8u);
    if(name&&thug_script_has_flag(parameters,0x90a91232))
        thug_motion_orient_to_node(component,thug_node_find(name,1));
    return 1;
}
/* 00426c10. Only a nonzero Name enters the movement and arrival path. */
void thug_motion_move_to_node(ThugObjectComponent *component,const ThugScriptStructure *parameters,
    ThugScriptInstance *script,const ThugDiagnostics *d,const ThugMemory *m) {
    uint32_t name=0;thug_script_get_checksum(parameters,0xa1dc81f9,&name,0);
    if(name){
        float point[4];thug_node_position_by_name(name,point);
        if(thug_motion_move_to_position(component,parameters,script,point[0],point[1],point[2],point[3],name))
            thug_motion_arrive_at_node(component,name,d,m);
        else ww(component,0x128,name);
    }
}
/* 004274d0. Recognized commands return one independently of missing Name. */
uint32_t thug_motion_command(ThugObjectComponent *component,uint32_t command,const ThugScriptStructure *parameters,
    ThugScriptInstance *script,const ThugDiagnostics *d,const ThugMemory *m) {
    if(command!=0x8819dd8b)return 2;
    thug_motion_move_to_node(component,parameters,script,d,m);return 1;
}
#undef R
