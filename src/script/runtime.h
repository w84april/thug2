#ifndef THUG_SCRIPT_RUNTIME_H
#define THUG_SCRIPT_RUNTIME_H
#include "params.h"
#include "../core/memory.h"
#include "../collision/probe.h"

typedef struct ThugScriptInstance ThugScriptInstance;
typedef struct ThugScriptWaitOwner ThugScriptWaitOwner;
typedef struct ThugScriptEventTable ThugScriptEventTable;
typedef struct {
    const uint8_t *start, *end;
    uint8_t finite, first_repeat, padding[2];
    uint32_t remaining;
} ThugScriptLoop;
typedef struct {
    uint32_t checksum;
    ThugScriptStructure *arguments;
    const uint8_t *instruction;
    ThugReferencedObject *owner;
    ThugScriptLoop *loop;
    uint32_t deferred_checksum;
    ThugScriptWaitOwner *wait_owner;
    uint32_t wait_remaining_bits, wait_argument, wait_frames, wait_type_bits;
    uint8_t flags, padding[3];
} ThugScriptCallFrame;
typedef struct {
    uint32_t unrecovered_slots[6];
    void (*update_wait)(ThugScriptWaitOwner *, ThugScriptInstance *, uint32_t argument);
} ThugScriptWaitMethods;
struct ThugScriptWaitOwner {
    const ThugScriptWaitMethods *methods;
    uint32_t unknown_4, flags;
};
struct ThugScriptInstance {
    ThugScriptInstance *next, *previous;
    uint32_t unknown_8;
    const uint8_t *instruction;
    ThugScriptStructure *parameters, *arguments;
    ThugScriptLoop *loop;
    uint8_t local_control_storage[16];
    uint8_t *control_storage;
    uint32_t call_depth;
    uint8_t local_call_storage[96];
    uint8_t *call_storage;
    uint32_t wait_frames;
    uint8_t waited, unknown_9d_to_9f[3];
    float wait_remaining;
    uint32_t wait_type, wait_argument;
    ThugScriptWaitOwner *wait_owner;
    uint32_t serial;
    uint8_t flags, unknown_b5_to_b7[3];
    uint32_t node_id;
    ThugObjectReference owner;
    uint32_t checksum;
    uint8_t flags_cc, unknown_cd_to_cf[3];
    uint32_t unknown_d0, unknown_d4, completion_checksum;
    ThugScriptStructure *completion_arguments;
    ThugScriptEventTable *events;
    uint32_t unknown_e4, unknown_e8;
    ThugReferenceTarget reference_target;
};

/* Lifted globals 6f3530, 6f3538, 6f353c, 6f3540 and 6f352c. Execution is
 * declared in execute.h; the producer/reset of the shared wait gate is separate. */
extern ThugScriptInstance *thug_current_script, *thug_script_list;
extern uint32_t thug_script_count, thug_script_next_serial;
extern uint8_t thug_script_wait_gate;
ThugScriptInstance *thug_script_current(void);
ThugScriptInstance *thug_script_next(const ThugScriptInstance *);
ThugScriptInstance *thug_script_find_spawned(uint32_t user_value);
ThugScriptInstance *thug_script_find_serial(uint32_t serial);
void thug_script_set_interrupt_checksum(ThugScriptInstance *, uint32_t);
void thug_script_clear_deferred(ThugScriptInstance *);
void thug_script_detach_owner(ThugScriptInstance *, const ThugReferencedObject *);
uint32_t thug_script_get_interrupt_checksum(const ThugScriptInstance *);
ThugScriptInstance *thug_script_initialize(ThugScriptInstance *);
uint8_t thug_script_has_instruction(const ThugScriptInstance *);
void thug_script_clear_wait(ThugScriptInstance *);
void thug_script_set_object_wait(ThugScriptInstance *, uint32_t type, ThugScriptWaitOwner *, uint32_t argument);
void thug_script_update_wait(ThugScriptInstance *);
ThugScriptStructure *thug_script_snapshot_arguments(const ThugScriptInstance *, const ThugScriptStructure *, const ThugMemory *);
void thug_script_skip_switch(ThugScriptInstance *);
void thug_script_begin_loop(ThugScriptInstance *, const ThugMemory *);
void thug_script_repeat_loop(ThugScriptInstance *, const ThugMemory *);
void thug_script_break_loop(ThugScriptInstance *, const ThugMemory *);
void thug_script_select_case(ThugScriptInstance *, const ThugMemory *);
uint8_t thug_script_return(ThugScriptInstance *, const ThugScriptStructure *values, const ThugMemory *);
void thug_script_clear_component_wait(ThugScriptInstance *,const ThugScriptWaitOwner *);
void thug_script_clear_component_waits(const ThugScriptWaitOwner *);
#endif
