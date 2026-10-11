#ifndef THUG_GAME_ANIMATION_H
#define THUG_GAME_ANIMATION_H
#include "assets.h"
#include "skater.h"
typedef struct ThugAnimationChannel ThugAnimationChannel;
typedef struct ThugAnimationController ThugAnimationController;
typedef struct ThugAnimationEvent ThugAnimationEvent;
typedef struct {
    ThugAnimationChannel *(*dispose)(ThugAnimationChannel *,uint32_t,const ThugMemory *);
    uint32_t unavailable_4;
    void (*update)(ThugAnimationChannel *,const ThugDiagnostics *,const ThugMemory *);
    void (*timeline)(ThugAnimationChannel *,uint32_t,float,float,uint32_t,float,float);
    uint32_t unavailable_10;
    uint32_t (*command)(ThugAnimationChannel *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
} ThugAnimationChannelMethods;
typedef struct {
    ThugAnimationController *(*dispose)(ThugAnimationController *,uint32_t,const ThugMemory *);
    uint32_t unavailable_4[2];
    uint32_t (*command)(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
    void (*configure)(ThugAnimationController *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
    void (*update)(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
} ThugAnimationControllerMethods;
struct ThugAnimationController {
    const ThugAnimationControllerMethods *methods;
    ThugAnimationChannel *channel;
    uint32_t unknown_8, unknown_c, name;
};
typedef struct {
    ThugAnimationController base;
    uint32_t values[5];
    float position;
    ThugAnimationReader *reader;
    void *animation;
    uint32_t animation_namespace;
} ThugBalanceAnimationController;
struct ThugAnimationChannel {
    const ThugAnimationChannelMethods *methods;
    uintptr_t id;
    uint32_t unknown_8;
    ThugAnimationChannel *previous,*next;
    float start,current,end,speed;
    uint32_t direction,loop;
    uint8_t flag_2c,unknown_2d[3];
    uint32_t animation_name,unknown_34,unknown_38;
    ThugAnimationController *controllers[6];
    int32_t count;
    float fade_rate,fade_value,fade_direction;
    ThugSkaterBody *body;
    ThugAnimationEvent *events;
    uint32_t event_count;
    uint8_t events_enabled,unknown_71[3];
};
typedef struct ThugAnimationState {
    uint32_t unknown_0,id;
    uint32_t unknown_8;
    struct ThugAnimationState *next;
    uint8_t unknown_10[0x10];
    ThugAnimationChannel *first_channel;
    uint32_t unknown_24, network_block;
    uint8_t unknown_2c[0x24];
    uint32_t animation_namespace,unknown_54,events;
    uint8_t unknown_5c[0xc];
    ThugSkaterBody *body;
} ThugAnimationState;
typedef struct {
    ThugObjectComponent base;
    uint8_t unknown_14[0x20];
    ThugAnimationState *state;
} ThugAnimationComponent;
typedef struct {
    ThugObjectComponent base;
    uint8_t unknown_14_to_1b[8];
    ThugAnimationComponent *animation;
} ThugSkaterFlipComponent;
uint8_t thug_animation_state_set_flipped(ThugAnimationState *,uint32_t id,uint32_t flipped,
    uint32_t time,uint32_t send,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_animation_component_set_flipped(ThugAnimationComponent *,uint32_t id,uint32_t flipped,
    uint32_t time,uint32_t send,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_toggle_flip(ThugSkaterFlipComponent *,const ThugDiagnostics *,const ThugMemory *);
extern uint8_t thug_animation_last_balance;
void thug_animation_set_balance(ThugAnimationState *,float,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void thug_animation_component_set_balance(ThugAnimationComponent *,float,uint32_t,const ThugDiagnostics *,const ThugMemory *);
extern const ThugAnimationChannelMethods thug_animation_channel_base_methods,thug_animation_channel_methods,thug_animation_link_methods;
extern const ThugAnimationControllerMethods thug_animation_controller_base_methods,thug_balance_animation_methods;
ThugAnimationChannel *thug_animation_timeline_initialize(ThugAnimationChannel *);
void thug_animation_set_timeline(ThugAnimationChannel *,uint32_t name,float first,float second,uint32_t loop,float unused,float speed);
ThugAnimationController *thug_animation_controller_initialize(ThugAnimationController *,ThugAnimationChannel *);
void thug_animation_controller_destroy(ThugAnimationController *);
void thug_animation_controller_configure(ThugAnimationController *,const ThugScriptStructure *);
ThugSkaterBody *thug_animation_channel_body(const ThugAnimationChannel *);
ThugSkaterBody *thug_animation_controller_body(const ThugAnimationController *);
uint32_t thug_animation_component_namespace(const ThugAnimationComponent *);
uint32_t thug_animation_component_events(const ThugAnimationComponent *);
uint8_t thug_animation_component_all_flipped(const ThugAnimationComponent *);
ThugAnimationController *thug_balance_animation_initialize(ThugAnimationController *,ThugAnimationChannel *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_balance_animation_command(ThugAnimationController *,uint32_t command,const ThugScriptStructure *,void *script,const ThugDiagnostics *);
double thug_animation_advance_time(ThugAnimationChannel *);
void thug_animation_update_time(ThugAnimationChannel *);
uint8_t thug_animation_timeline_finished(const ThugAnimationChannel *);
void thug_animation_offset_time(ThugAnimationChannel *,float delta);
ThugAnimationChannel *thug_animation_channel_initialize(ThugAnimationChannel *,ThugSkaterBody *);
void thug_animation_timeline_destroy(ThugAnimationChannel *);
ThugAnimationChannel *thug_animation_timeline_delete(ThugAnimationChannel *,uint32_t,const ThugMemory *);
void thug_animation_insert_controller(ThugAnimationChannel *,ThugAnimationController *,int32_t priority);
ThugAnimationController *thug_animation_find_controller(const ThugAnimationChannel *,uint32_t name);
void thug_animation_remove_controller(ThugAnimationChannel *,ThugAnimationController *,const ThugMemory *);
void thug_balance_animation_destroy(ThugAnimationController *,const ThugMemory *);
ThugAnimationController *thug_balance_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
void thug_animation_configure_controller(ThugAnimationController *,const ThugScriptStructure *);
typedef struct {
    void *(*dispose)(ThugAnimationEvent *,uint32_t,const ThugMemory *);
    uint32_t (*crosses)(const ThugAnimationEvent *,float,float,uint32_t);
    uint8_t (*trigger)(ThugAnimationEvent *,ThugReferencedObject *,const ThugDiagnostics *,const ThugMemory *);
} ThugAnimationEventMethods;
struct ThugAnimationEvent {
    const ThugAnimationEventMethods *methods;
    int32_t frame;
    uint8_t enabled,unknown_9[3];
    uint32_t event;
    ThugScriptStructure *parameters;
};
extern const ThugAnimationEventMethods thug_animation_event_methods,thug_animation_event_base_methods;
ThugAnimationEvent *thug_animation_event_initialize(ThugAnimationEvent *);
void thug_animation_event_set_enabled(ThugAnimationEvent *,uint32_t);
void thug_animation_event_setup(ThugAnimationEvent *,uint32_t frame,uint32_t event,const ThugScriptStructure *,const ThugMemory *);
void thug_animation_event_destroy(ThugAnimationEvent *,const ThugMemory *);
void *thug_animation_event_delete(ThugAnimationEvent *,uint32_t,const ThugMemory *);
void *thug_animation_event_base_delete(ThugAnimationEvent *,uint32_t,const ThugMemory *);
uint32_t thug_animation_event_crosses(const ThugAnimationEvent *,float from,float to,uint32_t inclusive);
uint8_t thug_animation_event_trigger(ThugAnimationEvent *,ThugReferencedObject *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_animation_event_emit(ThugAnimationEvent *,ThugReferencedObject *,const ThugDiagnostics *,const ThugMemory *);
void thug_animation_clear_events(ThugAnimationChannel *,const ThugMemory *);
void thug_animation_load_events(ThugAnimationChannel *,uint32_t name,const ThugMemory *);
void thug_animation_reset_events(ThugAnimationChannel *);
void thug_animation_update_events(ThugAnimationChannel *,float from,float to,const ThugDiagnostics *,const ThugMemory *);
/* File event construction and disposal are recovered. Their action/transform
 * trigger methods are not wired until those gameplay paths are recovered. */
extern const ThugAnimationEventMethods thug_animation_file_word_methods[5],thug_animation_file_transform_methods;
void thug_animation_file_event_destroy(ThugAnimationEvent *);
void *thug_animation_file_event_delete(ThugAnimationEvent *,uint32_t,const ThugMemory *);
ThugAnimationEvent *thug_animation_transform_event_initialize(ThugAnimationEvent *,uint32_t,const float *,const float *,uint32_t);
ThugAnimationEvent *thug_animation_parse_file_event(const uint8_t **,const ThugMemory *);
void thug_skater_sync_flip(ThugSkaterFlipComponent *,const ThugDiagnostics *,const ThugMemory *);
#endif
