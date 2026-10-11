#include "../../src/game/components.h"
#include "../../src/game/skater.h"
#include "../../src/game/attachment.h"
#include "../../src/game/nodes.h"
#include "../../src/game/grind.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/core/matrix.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put_number(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
#define R thug_platform_round_x87_single
/* 0041a640. */
float *thug_model_matrix_identity_draft(float *out){for(unsigned i=0;i<16;i++)put(out,i*4,i%5?0:0x3f800000);return out;}
/* 00420590. The signed timer conversion is exact until a negative value adds
 * 2^32 under PC24. FSIN uses the existing explicitly named platform adapter. */
double thug_model_transform_channel_draft(void *p){
    uint8_t flags=((uint8_t *)p)[0x14];if(!(flags&1))return 0;
    uint32_t elapsed=(flags&4?thug_frame_time():thug_elapsed_time()+thug_timer_offset)-word(p,4);
    double t=(int32_t)elapsed;if((int32_t)elapsed<0)t=R(t+0x1p32);
    float duration=number(p,0);
    if(t>duration){
        if(((uint8_t *)p)[0x14]&2)return R((double)number(p,12)+number(p,8));
        ((uint8_t *)p)[0x14]&=~1u;return 0;
    }
    int32_t curve=word(p,16);
    if(!curve)return R(R(R((double)number(p,12)/duration)*t)+number(p,8));
    double phase=R(R(t/duration)*(double)1.5707963705062866f),value;
    if(curve<0)value=R(1.0-thug_platform_sin(R((double)1.5707963705062866f-phase)));
    else{value=thug_platform_sin(phase);for(int32_t i=1;i<curve;i++)value=R(value*value);}
    return R(R(value*number(p,12))+number(p,8));
}
/* 004213e0. The active-group byte reflects entries active BEFORE evaluating
 * them, so it can remain set for one call after the final entry expires. */
double thug_model_transform_channels_draft(void *p){
    float total=0;
    if(((uint8_t *)p)[0x90]){
        ((uint8_t *)p)[0x90]=0;
        for(unsigned i=0;i<6;i++){
            void *entry=(uint8_t *)p+i*24;
            if(((uint8_t *)entry)[20]&1){((uint8_t *)p)[0x90]=1;total=(float)R(thug_model_transform_channel_draft(entry)+(double)total);}
        }
    }return total;
}
float *thug_sound_transform_draft(float *,const float *,const float *);
/* 004215f0. Keep the original matrix multiplication backend, arithmetic order,
 * pivot correction, live source reads, and return value (owner position). */
void *thug_model_transform_matrix_draft(void *component,float *out){
    thug_matrix_copy(out,(float *)((uint8_t *)pointer(component,12)+0xc0));
    put(out,0x30,0);put(out,0x34,0);put(out,0x38,0);put(out,0x3c,0x3f800000);
    if(((uint8_t *)component)[0x1f4]){
        for(unsigned group=0;group<2;group++)for(unsigned i=0;i<4;i++){
            unsigned o=(group?0:0x20)+i*4;put(out,o,quiet(word(out,o))^0x80000000);
        }
    }
    float rotation[16],temp[16],delta[4]={0,0,0,0};uint8_t untouched=1;
    for(unsigned axis=0;axis<3;axis++){
        unsigned o=0x38+axis*0x94;
        if(!((uint8_t *)component)[o+0x90])continue;
        float degrees=(float)thug_model_transform_channels_draft((uint8_t *)component+o);
        if(degrees==0)continue;
        if(untouched)thug_model_matrix_identity_draft(rotation);untouched=0;
        float radians=(float)R((double)degrees*(double)0.01745329238474369f);
        if(axis==0)thug_matrix_rotation_x(temp,radians);
        else if(axis==1)thug_matrix_rotation_y(temp,radians);
        else thug_matrix_rotation_z(temp,radians);
        thug_matrix_multiply(rotation,rotation,temp);
    }
    if(!untouched){
        for(unsigned i=0;i<4;i++)put(delta,i*4,word(component,0x28+i*4));
        if(delta[0]!=0||delta[1]!=0||delta[2]!=0){
            float v[4];thug_sound_transform_draft(v,delta,rotation);
            for(unsigned i=0;i<4;i++)delta[i]=(float)R((double)delta[i]-v[i]);
            thug_sound_transform_draft(v,delta,out);for(unsigned i=0;i<4;i++)put(delta,i*4,word(v,i*4));
        }
        thug_matrix_multiply(out,rotation,out);
    }
    void *owner=pointer(component,12);
    for(unsigned i=0;i<4;i++)put(out,0x30+i*4,word(owner,0x4c+i*4));
    for(unsigned i=0;i<4;i++)put_number(out,0x30+i*4,(float)R((double)delta[i]+number(out,0x30+i*4)));
    for(unsigned i=0;i<4;i++)put_number(out,0x30+i*4,(float)R((double)number(component,0x1f8+i*4)+number(out,0x30+i*4)));
    put(out,0x3c,0x3f800000);return (uint8_t *)owner+0x4c;
}
/* 004204b0. Reload the owner before each actual component lookup. */
void thug_model_component_finalize_draft(void *p){
    put(p,0x20c,(uintptr_t)thug_object_find_component(pointer(p,12),0x222756d5));
    put(p,0x210,(uintptr_t)thug_object_find_component(pointer(p,12),0x7149b753));
    put(p,0x214,(uintptr_t)thug_object_find_component(pointer(p,12),0xce0ca665));
}
/* 004b4630. Render instances preserve the exact low enabled byte; uninstanced
 * mesh arrays set/clear bit6, with live mesh-array and unsigned-count reloads. */
void thug_model_geometry_enabled_draft(void *p,uint32_t enabled){
    void *instance=pointer(p,0x4c);uint8_t value=enabled;
    if(instance){((uint8_t *)instance)[0x4c]=value;return;}
    void *array=pointer(p,0x3c);((uint8_t *)p)[0x48]=value;
    if(array)for(uint32_t i=0;i<word(p,0x40);i++){
        void *mesh=pointer(pointer(p,0x3c),i*4);put(mesh,0,value?word(mesh,0)|0x40:word(mesh,0)&~0x40u);
    }
}
/* 004b47b0. Matrix copy is followed by a live instance reload and forward
 * REP MOVSD bone copies. The final two arguments are unused by the PC body. */
uint8_t thug_model_geometry_transform_pc_draft(void *p,const float *matrix,const void *bones,uint32_t count,uint32_t ignored,uint32_t part){
    (void)ignored;(void)part;void *instance=pointer(p,0x4c);
    if(instance){
        thug_matrix_copy((float *)((uint8_t *)instance+4),matrix);
        void *out=pointer(pointer(p,0x4c),0x44);uint32_t bytes=count<<6;
        for(uint32_t i=0;i<(bytes>>2);i++)put(out,i*4,word(bones,i*4));
    }return 1;
}
/* 0048df30. */
uint8_t thug_model_geometry_transform_draft(void *p,const float *matrix,const void *bones,uint32_t count,uint32_t map,uint32_t part){
    typedef struct{uintptr_t unused[28];uint8_t(*transform)(void *,const float *,const void *,uint32_t,uint32_t,uint32_t);} Methods;
    return ((const Methods *)pointer(p,0))->transform(p,matrix,bones,count,map,part);
}
/* 00419ca0. */
uint32_t thug_model_animation_active_draft(void *animation){
    void *renderer=pointer(pointer(animation,0x20),0x208);
    return renderer&&(((uint8_t *)renderer)[0x44]&6)==2;
}
/* 0049f4a0, the actual PC renderer bone-map virtual. */
uint32_t thug_model_renderer_bone_map_draft(void *renderer,uint32_t count){(void)renderer;(void)count;return 0;}
void thug_render_set_enabled_draft(void *,uint32_t);
/* Partial00493090: all ordinary model transforms, including bone arrays and
 * scaling. The mode1 skeleton-debug drawing dependency remains unavailable. */
uint8_t thug_model_renderer_update_prefix_draft(void *p,float *matrix,uint32_t no_bones,void *provider){
    uint8_t ordinary=word(p,4)==0;void *head=pointer(p,0x10),*node=head?pointer(head,4):0;unsigned index=0;
    while(node!=head){
        uint32_t enabled=ordinary&&(((uint8_t *)p)[0x44]&2)&&(word(p,0x18)&(1u<<(index&31)));
        thug_render_set_enabled_draft(pointer(pointer(node,0),0),enabled!=0);node=pointer(node,4);index++;
    }
    if(((uint8_t *)p)[0x44]&8)for(unsigned row=0;row<3;row++){
        double factor=number(p,0x1c+row*4);
        for(unsigned i=0;i<4;i++)put_number(matrix,row*16+i*4,(float)R(factor*number(matrix,row*16+i*4)));
    }
    uint32_t mode=word(p,4);
    if(mode==0){
        put(matrix,12,0);put(matrix,28,0);put(matrix,44,0);put(matrix,60,0x3f800000);
        void *bones=0;uint32_t count=0,map=0;
        if(provider&&!(uint8_t)no_bones){
            bones=pointer(provider,4);count=word(provider,0x14); /* actual5480c0 /4a2ba0 */
            typedef struct{uintptr_t unused[2];uint32_t(*bone_map)(void *,uint32_t);} Methods;
            map=((const Methods *)pointer(p,0))->bone_map(p,count);
        }
        head=pointer(p,0x10);index=0;
        for(node=head?pointer(head,4):0;node!=head;node=pointer(node,4)){
            thug_model_geometry_transform_draft(pointer(pointer(node,0),0),matrix,bones,count,map,provider&&!(uint8_t)no_bones?index:0);index++;
        }
    }else if(mode==1&&provider)__builtin_trap(); /* unrecovered4a31e0 skeleton debug draw */
    /* Modes2/3/4/6 return; mode5/default calls the actual5480a0 bare RET. */
    return 1;
}
/* Partial004219f0. Normal model and skeletal transforms are recovered here;
 * the alternate attachment-object branch remains an explicit missing path. */
void thug_model_update_prefix_draft(void *p){
    if(((uint8_t *)p)[0x234])__builtin_trap();
    void *renderer=pointer(p,0x208);
    if(!renderer||(((uint8_t *)renderer)[0x44]&6)!=2)return;
    float matrix[16];thug_model_transform_matrix_draft(p,matrix);
    void *skeleton=pointer(p,0x20c),*provider=skeleton?thug_attachment_provider_points(skeleton):0;
    uint32_t animated=word(p,0x20c)!=0;
    if(word(p,0x210))animated=thug_model_animation_active_draft(pointer(p,0x210));
    thug_model_renderer_update_prefix_draft(pointer(p,0x208),matrix,!(uint8_t)animated,provider);
}
void thug_model_update_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_model_update_prefix_draft(p);}
/* Partial00420480: actual update virtual; missing lighting must not succeed. */
void thug_model_component_moved_prefix_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    ((const ThugComponentMethods *)pointer(p,0))->update(p,q,d,m);
    void *renderer=pointer(p,0x208);if(renderer&&word(renderer,0x2c))__builtin_trap(); /*48e660*/
}
void *thug_composite_create_from_array_draft(void *,ThugScriptArray *,ThugScriptStructure *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void *thug_lockobj_construct_draft(void *);
void *thug_component_b87c8e43_construct_draft(void *);
void thug_composite_add_component_draft(void *,void *);
void thug_composite_finalize_draft(void *,const ThugDiagnostics *,const ThugMemory *);
/* Partial00468cb0 orchestration, now executing the complete actual two training
 * node paths. Dependent Model update/configuration retain explicit missing paths. */
void *thug_gameobject_create_prefix_draft(ThugScriptStructure *node,uint32_t ignored,const ThugDiagnostics *d,const ThugMemory *m){
    (void)ignored;void *manager=thug_component_type_registry;
    ThugScriptArray *array=thug_script_get_global_array(0x735a20ba,0);
    void *object=thug_composite_create_from_array_draft(manager,array,node,0,d,m);
    void *component=thug_allocate_zeroed(0x90,m);if(component)component=thug_lockobj_construct_draft(component);
    thug_composite_add_component_draft(object,component);
    thug_script_run_sync(0xf3b84da6,node,object,0,d,m);
    component=thug_allocate_zeroed(0x4c,m);if(component)component=thug_component_b87c8e43_construct_draft(component);
    thug_composite_add_component_draft(object,component);
    typedef struct{uintptr_t unused[8];void(*finalize)(void *,const ThugDiagnostics *,const ThugMemory *);} Methods;
    ((const Methods *)pointer(object,0))->finalize(object,d,m);
    uint32_t color;
    if(thug_script_get_integer(node,0x99a9b716,&color,0)){
        uint32_t name=thug_node_name(node);ThugScriptStructure *s=thug_script_structure_allocate(8,m);
        if(s)s=thug_script_structure_initialize(s);
        thug_script_set_checksum(s,0xa1dc81f9,name,m);thug_script_set_integer(s,0x99a9b716,color,m);
        thug_script_run_sync(0x413b766d,s,object,0,d,m);
        if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
    }
    component=thug_object_find_component(object,0x286a8d26);
    if(component)thug_model_component_moved_prefix_draft(component,0,d,m);
    uint32_t trigger;ThugScriptStructure *params=0;
    if(thug_script_get_checksum(node,0x2ca8a299,&trigger,0)){
        thug_script_get_structure(node,0x7031f10c,&params,0);thug_object_set_script(object,trigger,params,d,m);
    }
    return object;
}
