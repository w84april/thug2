/* Original Input startup, intrusive device tasks and controller force feedback. */
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/game/drawing.h"
#include "../../src/script/delivery.h"
#include "../../src/network/queue.h"
#include "../../src/game/objectives.h"
#include "../../src/platform/math.h"
#include "../../src/core/number.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint8_t *bytes(void *p){return p;}
extern const uintptr_t thug_task_base_methods_draft[3],thug_task_node_methods_draft[1];
extern const uintptr_t thug_input_task_methods_draft[3],thug_input_task_base_methods_draft[3];
extern const ThugComponentMethods thug_input_methods_draft;
void *thug_task_base_construct_draft(void *,uint32_t,const ThugMemory *);
void *thug_input_pad_construct_draft(void *);
void thug_input_primary_task_draft(void *,const ThugDiagnostics *,const ThugMemory *);
void thug_input_secondary_task_draft(void *,const ThugMemory *);
void thug_component_suspend_update_draft(void *);
static const ThugMemory *memory(void){return thug_component_services?thug_component_services->memory:thug_event_services->memory;}

/* 00406850 /004069b0. */
uint8_t thug_task_linked_draft(const void *p){void *n=ptr(p,8);return ptr(n,0x10)!=n;}
void thug_task_list_changed_draft(void *p){bytes(p)[0x1c]=1;}
/* 004068f0. Reload both neighbors and the list after earlier writes. */
void thug_task_unlink_draft(void *p){
    void *list=ptr(p,0xc);
    if(list){
        put(list,0,word(list,0)+1);thug_task_list_changed_draft(ptr(p,0xc));
        void *n=ptr(p,8);
        put(ptr(n,0x10),0xc,word(n,0xc));put(ptr(n,0xc),0x10,word(n,0x10));
        put(n,0xc,(uintptr_t)n);put(n,0x10,(uintptr_t)n);
        list=ptr(p,0xc);put(list,0,word(list,0)-1);put(p,0xc,0);
    }
}
/* ABI bridge for an original unlink method used as a task update. */
void thug_task_unlink_frame_bridge_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){(void)d;(void)m;thug_task_unlink_draft(p);}
/* 00406a00 /00406860. */
void thug_task_node_destroy_draft(void *p){
    void *previous=ptr(p,0x10);uint32_t next=word(p,0xc);
    put(p,0,(uintptr_t)thug_task_node_methods_draft);put(previous,0xc,next);
    put(ptr(p,0xc),0x10,word(p,0x10));put(p,0xc,(uintptr_t)p);put(p,0x10,(uintptr_t)p);
}
void *thug_task_node_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_task_node_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 00406930 /00406980. */
void thug_task_base_destroy_draft(void *p,const ThugMemory *m){
    put(p,0,(uintptr_t)thug_task_base_methods_draft);thug_task_unlink_draft(p);
    void *n=ptr(p,8);
    if(n)((void *(*)(void *,uint32_t,const ThugMemory *))(uintptr_t)word(ptr(n,0),0))(n,1,m);
}
void *thug_task_base_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_task_base_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 00406a50. Preserve padding after the one-byte changed flag. */
void *thug_task_list_construct_draft(void *p){
    void *n=bytes(p)+4;put(p,0,0);put(n,4,UINT32_MAX);put(n,8,0);
    put(n,0xc,(uintptr_t)n);put(n,0x10,(uintptr_t)n);put(n,0,(uintptr_t)thug_task_node_methods_draft);
    put(p,0x18,0);bytes(p)[0x1c]=0;return p;
}
/* 00406a80 /00406c90. Original priority insertion and wrapped visit stamp. */
void thug_task_list_add_draft(void *list,void *task){
    put(list,0,word(list,0)+1);thug_objective_queue_insert((void *)(bytes(list)+4),ptr(task,8));
    put(task,0xc,(uintptr_t)list);put(task,0x10,word(list,0x18)-1);
    uint32_t locks=word(list,0)-1;bytes(list)[0x1c]=1;put(list,0,locks);
}
void thug_task_wrapper_add_draft(void *wrapper,void *task){thug_task_list_add_draft(ptr(wrapper,0x34),task);}
/* 00406ac0. Capture next before dispatch, restart on mutation, and mark masked
 * tasks visited too. The first original argument is intentionally unused. */
void thug_task_list_update_draft(void *list,uint32_t unused,uint32_t mask,const ThugDiagnostics *d,const ThugMemory *m){
    (void)unused;
    if(word(list,0))return;
    put(list,0x18,word(list,0x18)+1);
    do{
        void *node=ptr(list,0x10);void *task=word(node,4)==UINT32_MAX?0:ptr(node,4);
        bytes(list)[0x1c]=0;
        while(task){
            void *next_node=ptr(node,0xc);void *next=word(next_node,4)==UINT32_MAX?0:ptr(next_node,4);
            if(!word(task,4)&&word(task,0x10)!=word(list,0x18)){
                uint32_t flags=word(task,0x14);put(task,0x10,word(list,0x18));
                if(!(mask&flags))((void (*)(void *,const ThugDiagnostics *,const ThugMemory *))(uintptr_t)word(ptr(task,0),0))(task,d,m);
            }
            if(bytes(list)[0x1c])break;
            task=next;node=next_node;
        }
    }while(bytes(list)[0x1c]);
}
/* 00406bb0. Detach all tasks while holding the list lock; do not free them. */
void thug_task_list_clear_draft(void *list){
    put(list,0,word(list,0)+1);
    for(;;){
        void *node=ptr(list,0x10);void *task=word(node,4)==UINT32_MAX?0:ptr(node,4);
        if(!task)break;
        thug_task_unlink_draft(task);bytes(list)[0x1c]=1;
    }
    put(list,0,word(list,0)-1);
}
/* Host bridges preserve the original one-argument task callback ABI. */
static const ThugEventServices *task_services;
void thug_input_primary_task_bridge_draft(void *task){thug_input_primary_task_draft(task,task_services->diagnostics,task_services->memory);}
void thug_input_secondary_task_bridge_draft(void *task){thug_input_secondary_task_draft(task,task_services->memory);}
/* 00577270. */
void thug_input_task_execute_draft(void *task,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugEventServices services={d,m},*old=task_services;task_services=&services;
    ((void (*)(void *))(uintptr_t)word(task,0x24))(task);task_services=old;
}
/* 00577280 /00536670. */
void thug_input_task_destroy_draft(void *task,const ThugMemory *m){
    put(task,0,(uintptr_t)thug_input_task_base_methods_draft);thug_task_base_destroy_draft(task,m);
}
void *thug_input_task_delete_draft(void *task,uint32_t flags,const ThugMemory *m){
    thug_input_task_destroy_draft(task,m);if((uint8_t)flags&1)m->release(m->context,task);return task;
}
/* 005ba1d0, shared zero-result method. */
uint32_t thug_task_zero_draft(void *task){(void)task;return 0;}
static void abstract_run(void *p,const ThugDiagnostics *d,const ThugMemory *m){(void)p;(void)d;(void)m;__builtin_trap();}
static uint32_t abstract_query(void *p){(void)p;__builtin_trap();}
const uintptr_t thug_task_base_methods_draft[3]={(uintptr_t)abstract_run,(uintptr_t)abstract_query,(uintptr_t)thug_task_base_delete_draft};
const uintptr_t thug_task_node_methods_draft[1]={(uintptr_t)thug_task_node_delete_draft};
const uintptr_t thug_input_task_base_methods_draft[3]={(uintptr_t)abstract_run,(uintptr_t)abstract_query,(uintptr_t)thug_input_task_delete_draft};
const uintptr_t thug_input_task_methods_draft[3]={(uintptr_t)thug_input_task_execute_draft,(uintptr_t)thug_task_zero_draft,(uintptr_t)thug_input_task_delete_draft};

/* Original DirectInput effect ABI. These two COM methods are the hardware
 * boundary; the recovered calculations and complete descriptor remain here. */
typedef struct ThugInputEffect ThugInputEffect;
typedef struct {
    uint32_t unused[6];
    uint32_t (*set_parameters)(ThugInputEffect *,const uint32_t *,uint32_t);
    uint32_t unused_1c;
    uint32_t (*stop)(ThugInputEffect *);
} ThugInputEffectMethods;
struct ThugInputEffect {const ThugInputEffectMethods *methods;};
ThugInputEffect *thug_input_effects_draft[2]; /* 007d6668 */
uint32_t thug_input_effect_axes_draft[2]; /* 007d42c8 */
uint32_t thug_input_effect_scales_draft[4]; /* 007d42d0 */
static double unsigned_x87(uint32_t n){return (int32_t)n<0?R((double)(int32_t)n+0x1p32):(int32_t)n;}
/* 005f3a50. Complete force-feedback arithmetic and effect descriptor. */
void thug_input_set_actuators_draft(uint32_t index,uint32_t first,uint32_t second){
    if(!thug_input_effects_draft[index])return;
    if(!first&&!second){ThugInputEffect *e=thug_input_effects_draft[index];e->methods->stop(e);return;}
    double scale=unsigned_x87(thug_input_effect_scales_draft[2*index]);
    uint32_t a=thug_truncate_double_low_word(R(R(unsigned_x87(first)*scale)*0x1p-16));
    uint32_t b=thug_truncate_double_low_word(R(R(unsigned_x87(second)*unsigned_x87(thug_input_effect_scales_draft[2*index+1]))*0x1p-16));
    uint32_t direction[2]={0,0},magnitude;
    if(thug_input_effect_axes_draft[index]==1)magnitude=thug_truncate_double_low_word(R(R(unsigned_x87(a)/scale)*10000));
    else{
        direction[0]=a;direction[1]=b;double x=unsigned_x87(a),y=unsigned_x87(b);
        magnitude=thug_truncate_double_low_word(R(R(R(__builtin_sqrt(R(R(x*x)+R(y*y))))/scale)*10000));
    }
    uint32_t effect[14]={0};ThugInputEffect *e=thug_input_effects_draft[index];
    effect[0]=0x38;effect[1]=0x12;effect[7]=2;effect[9]=(uintptr_t)direction;
    effect[11]=4;effect[12]=(uintptr_t)&magnitude;
    e->methods->set_parameters(e,effect,0x20000140);
}
/* 005bccb0 /005bdad0. */
void thug_input_device_enable_vibration_draft(void *device){bytes(device)[0xc0]=0;}
void thug_input_device_disable_vibration_draft(void *device){
    if(!bytes(device)[0xc0]){
        if(word(device,0xd4)==2&&(bytes(device)[0xc4]&2)){
            for(int32_t i=0;i<(int32_t)word(device,0xcc);i++)bytes(device)[0x5c+i]=0;
            thug_input_set_actuators_draft(word(device,0xc),0,0);
        }
        bytes(device)[0xc0]=1;
    }
}
/* 0043d5c0. */
void thug_vibration_bind_device_draft(void *component,void *device){
    uint8_t enabled=bytes(component)[0x18];put(component,0x34,(uintptr_t)device);
    if(enabled)thug_input_device_enable_vibration_draft(device);else thug_input_device_disable_vibration_draft(device);
}

void *thug_input_device_manager_draft; /* 00696d40 */
/* 0041f1b0. Input task allocation uses host heap scope8, originally allocator
 * +5d4. Task20 retains its construction slot even when its device is rebound. */
void thug_input_bind_device_draft(void *p,uint32_t device,const ThugMemory *m){
    if(!word(p,0x490)){
        m->temp_scope(m->context,8);
        for(uint32_t i=0;i<2;i++){
            void *task=thug_allocate_zeroed(0x2c,m);
            if(task){
                thug_task_base_construct_draft(task,UINT32_MAX,m);put(task,0x20,i);
                put(task,0,(uintptr_t)thug_input_task_methods_draft);
                put(task,0x24,(uintptr_t)(i?thug_input_secondary_task_bridge_draft:thug_input_primary_task_bridge_draft));
                put(task,0x28,(uintptr_t)p);
            }
            put(p,0x490+4*i,(uintptr_t)task);
            void *manager=thug_input_device_manager_draft;
            thug_task_wrapper_add_draft(bytes(manager)+8+word(task,0x20)*0x84,task);
            uint8_t *slot=bytes(manager)+word(task,0x20)*0x84;
            put(task,0x18,(uintptr_t)(slot+0x44));put(task,0x1c,word(slot,4));
        }
        m->temp_scope(m->context,0);
    }
    void *manager=thug_input_device_manager_draft,*task=ptr(p,0x490);
    thug_task_unlink_draft(task);uint8_t *slot=bytes(manager)+device*0x84;
    thug_task_wrapper_add_draft(slot+8,task);put(task,0x18,(uintptr_t)(slot+0x44));put(task,0x1c,word(slot,4));
    manager=thug_input_device_manager_draft;task=ptr(p,0x494);
    thug_task_unlink_draft(task);thug_task_wrapper_add_draft(bytes(manager)+0x8c,task);
    put(task,0x18,(uintptr_t)(bytes(manager)+0xc8));put(task,0x1c,word(manager,0x88));
    void *vibration=thug_object_find_component(ptr(p,0xc),0x404eb936);
    if(vibration)thug_vibration_bind_device_draft(vibration,ptr(ptr(p,0x490),0x1c));
}
/* 0041f390. Optional Player takes precedence over the raw controller slot. */
void thug_input_initialize_draft(void *p,const ThugScriptStructure *parameters,const ThugMemory *m){
    uint32_t device;
    if(thug_script_get_integer(parameters,0x67e6859a,&device,0))
        thug_input_bind_device_draft(p,thug_input_device_id(thug_input_device_manager_draft,device),m);
    else if(thug_script_get_integer(parameters,0xb30d9965,&device,0))thug_input_bind_device_draft(p,device,m);
    thug_script_get_checksum(parameters,0xb9b1e3b6,(void *)(bytes(p)+0x49c),0);
}
/* 0041e850 /0041eec0. The constructor leaves494 and the flags untouched. */
void *thug_input_construct_draft(void *p){
    thug_component_construct(p);put(p,0,(uintptr_t)&thug_input_methods_draft);
    thug_input_pad_construct_draft(bytes(p)+0x20);thug_input_pad_construct_draft(bytes(p)+0x258);
    put(p,4,0x27d7cd28);put(p,0x490,0);put(p,0x49c,0);return p;
}
void *thug_input_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x4a0,m);return p?thug_input_construct_draft(p):0;}
/* 0041e710 /0041e8c0. */
void thug_input_destroy_draft(void *p,const ThugMemory *m){
    put(p,0,(uintptr_t)&thug_input_methods_draft);
    for(unsigned off=0x490;off<=0x494;off+=4){
        if(word(p,off)){
            if(thug_task_linked_draft(ptr(p,off)))thug_task_unlink_draft(ptr(p,off));
            void *task=ptr(p,off);
            if(task)((void *(*)(void *,uint32_t,const ThugMemory *))(uintptr_t)word(ptr(task,0),8))(task,1,m);
        }
    }
    thug_component_destroy(p);
}
void *thug_input_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
    thug_input_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 0041e7c0 /0041e7d0. Original two-argument command ABI. */
uint32_t thug_input_enable_events_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;bytes(p)[0x49a]=1;return 1;}
uint32_t thug_input_disable_events_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;bytes(p)[0x49a]=0;return 1;}
static void input_initialize(void *p,const ThugScriptStructure *s){thug_input_initialize_draft(p,s,memory());}
static void input_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;thug_component_suspend_update_draft(p);}
static void empty(void *p){thug_draw_style_noop(p);}
static uint32_t unhandled(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){return thug_animation_unhandled_command(p,name,s,script,0,0);}
const ThugComponentMethods thug_input_methods_draft={
    thug_input_delete_draft,input_frame,input_initialize,empty,empty,thug_component_refresh,
    thug_component_empty_two,thug_component_suspend,thug_component_empty_one,
    thug_component_empty_frame_bridge,thug_component_empty_one,thug_component_descriptor,unhandled
};
