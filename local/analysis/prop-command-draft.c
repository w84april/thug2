#include "../../src/game/components.h"
#include "../../src/game/ui.h"
#include "../../src/script/lifetime.h"
#include "../../src/script/delivery.h"
#include "../../src/script/operators.h"
#include "../../src/script/values.h"
#include "../../src/core/checksum.h"
#include <stddef.h>

/* Original fixed-argument virtual/member ABI uses the existing host scope.
 * The scope is supplied by the interpreter/frame entry, never a game stub. */
static const ThugMemory *mem(void){return thug_event_services->memory;}
static const ThugDiagnostics *diag(void){return thug_event_services->diagnostics;}
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
typedef struct {
    void *(*dispose)(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
    void (*parameters)(void *,ThugScriptStructure *);
    uint32_t (*descriptor)(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
    uint32_t (*checksum)(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);
    void (*empty)(void *,void *);
    void (*event)(void *,ThugEvent *);
    void (*defer)(void *,const ThugDiagnostics *,const ThugMemory *);
    uint32_t (*active)(void *);
    void (*finalize)(void *,const ThugDiagnostics *,const ThugMemory *);
    void (*add)(void *,ThugScriptStructure *,ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
} ObjectMethods;
static const ObjectMethods *methods(const void *p){return pointer(p,0);}

/* 00476c60. Text getter with a low-byte assertion flag. */
uint32_t thug_script_get_text_legacy_draft(const ThugScriptStructure *s,uint32_t name,const char **out,uint32_t flag){
    return thug_script_get_text(s,name,out,(uint8_t)flag!=0);
}
/* 0045d7f0, descriptor c2404947. This specimen only looks up optional text. */
uint32_t thug_composite_text_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)p;(void)script;const char *text;thug_script_get_text_legacy_draft(s,0,&text,0);return 1;
}
/* 0045d810. The descriptor itself is passed unchanged, without node overrides. */
uint32_t thug_composite_create_component_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;methods(p)->add(p,s,0,diag(),mem());return 1;
}
/* 0045dbf0. Missing required Name retains the initialized zero type. */
uint32_t thug_composite_contains_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;uint32_t type=0;thug_script_get_checksum(s,0xa1dc81f9,&type,1);
    return thug_object_find_component(p,type)!=0;
}
/* 0045d830/0045dbc0. SetPosition does not issue moved notifications. */
uint32_t thug_composite_set_position_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;thug_script_get_vector(s,0xb9d31b0a,(void *)((uint8_t *)p+0x4c),0);return 1;
}
uint32_t thug_composite_get_position_command_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)s;uint32_t z=word(p,0x54),y=word(p,0x50),x=word(p,0x4c);
    thug_script_set_vector_bits(script->arguments,0x7f261953,x,y,z,mem());return 1;
}
/* 0045d850. Direct member pointers include the signed/wrapping receiver
 * adjustment; the fallback uses only the first descriptor word. */
uint32_t thug_composite_descriptor_draft(void *p,const ThugScriptCommand *c,ThugScriptStructure *s,ThugScriptInstance *script){
    typedef uint32_t (*Member)(void *,ThugScriptStructure *,ThugScriptInstance *);
    Member member=(Member)(uintptr_t)word(c,8);
    if(member)return (uint8_t)member((void *)((uintptr_t)p+word(c,12)),s,script);
    return (uint8_t)methods(p)->checksum(p,c->name,s,script);
}
/* 004608f0. Unknown base commands return true in the actual executable. */
uint32_t thug_object_checksum_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;
    if(name==0x6c63c7c5)methods(p)->parameters(p,s);
    else if(name==0xc6870028)methods(p)->defer(p,diag(),mem());
    return 1;
}
/* 0045e450. Component return values are three-state WORDS. Only 0/1 stop
 * traversal; every other value falls through along the live next link. */
uint32_t thug_composite_checksum_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
    for(ThugObjectComponent *c=pointer(p,0x100);c;c=c->next){
        uint32_t result=((const ThugComponentMethods *)(uintptr_t)c->unknown_0)->checksum(c,name,s,script);
        if(result==0)return 0;if(result==1)return 1;
    }
    return thug_object_checksum_draft(p,name,s,script);
}

/* 00476420 /00478ab0. The copy constructor has separate signed high-water
 * statistics; ordinary constructor/destructor counters are not inferred. */
uint32_t thug_script_copy_structure_count_draft,thug_script_copy_structure_peak_draft;
uint32_t thug_script_structure_empty_draft(const ThugScriptStructure *s){return s->first==0;}
ThugScriptStructure *thug_script_structure_copy_construct_draft(ThugScriptStructure *s,const ThugScriptStructure *source){
    thug_script_structure_initialize(s);
    if(s!=source){thug_script_structure_clear(s,mem());thug_script_structure_merge(s,source,mem());}
    uint32_t count=++thug_script_copy_structure_count_draft;
    if((int32_t)count>(int32_t)thug_script_copy_structure_peak_draft)thug_script_copy_structure_peak_draft=count;
    return s;
}
/* 0045f820. Only the original two flag bytes are initialized. */
ThugScriptEventTable *thug_script_events_initialize_draft(ThugScriptEventTable *t){
    t->count=0;t->entries=0;t->alive=1;t->active_calls=0;t->stop_iteration=0;return t;
}
extern void thug_script_subscribe_draft(ThugObjectLookupManager *,uint32_t,ThugScriptInstance *,const ThugMemory *);
/* 0045fa10. Capture the entry pointer, but reload the signed count each time. */
void thug_script_events_subscribe_draft(ThugScriptEventTable *t,ThugScriptInstance *script){
    ThugScriptEventEntry *e=t->entries;
    for(uint32_t i=0;(int32_t)i<(int32_t)t->count;i++,e++)
        if(e->event&&e->script&&e->script!=0xc377c572)
            thug_script_subscribe_draft(thug_object_lookup_manager,e->event,script,mem());
}
static void dispose_structure(ThugScriptStructure *s){thug_script_structure_destroy(s,mem());thug_script_structure_free(s,mem());}
static void copy_entry(ThugScriptEventEntry *to,const ThugScriptEventEntry *from){
    to->event=from->event;to->script=from->script;to->group=from->group;to->parameters=from->parameters;to->flags=from->flags;
}
/* 0045ff50. Remove tombstones, preserving all other entry words and live
 * array/count reloads after allocation and parameter disposal. */
void thug_script_events_compact_draft(ThugScriptEventTable *t){
    if(!t->entries)return;uint32_t count=t->count,removed=0;
    for(uint32_t i=0;(int32_t)i<(int32_t)count;i++)if(t->entries[i].script==0xc377c572)removed++;
    if(!removed)return;uint32_t kept=count-removed;t->stop_iteration=1;
    if(!kept){
        for(uint32_t i=0;(int32_t)i<(int32_t)t->count;i++)if(t->entries[i].parameters){dispose_structure(t->entries[i].parameters);t->entries[i].parameters=0;}
        mem()->release(mem()->context,t->entries);t->entries=0;t->count=0;return;
    }
    mem()->temp_scope(mem()->context,6);ThugScriptEventEntry *next=mem()->allocate(mem()->context,kept*20,1);
    mem()->temp_scope(mem()->context,0);ThugScriptEventEntry *out=next;
    for(uint32_t i=0;(int32_t)i<(int32_t)t->count;i++){
        ThugScriptEventEntry *entry=t->entries+i;
        if(entry->script!=0xc377c572)copy_entry(out++,entry);
        else if(entry->parameters){dispose_structure(entry->parameters);t->entries[i].parameters=0;}
    }
    mem()->release(mem()->context,t->entries);t->count=kept;t->entries=next;
}
/* 004601a0. New entries precede old ones. Replacement tombstones old events
 * before copying parameters, and retains poison/padding in the new flag word. */
void thug_script_events_add_draft(ThugScriptEventTable *t,ThugScriptArray *array,uint32_t replace){
    uint32_t incoming=array->count;
    if((uint8_t)replace&&!incoming){
        if(t->entries){
            for(uint32_t i=0;(int32_t)i<(int32_t)t->count;i++)if(t->entries[i].parameters)dispose_structure(t->entries[i].parameters);
            mem()->release(mem()->context,t->entries);t->entries=0;t->count=0;t->stop_iteration=1;
        }return;
    }
    mem()->temp_scope(mem()->context,6);
    ThugScriptEventEntry *next=mem()->allocate(mem()->context,(t->count+incoming)*20,1);
    uint32_t used=0;
    for(uint32_t i=0;(int32_t)i<(int32_t)incoming;i++){
        ThugScriptStructure *s=thug_script_array_structure(array,(int32_t)i);
        ThugScriptComponent *event=thug_script_next_component(s,0),*script=thug_script_next_component(s,event);
        if((uint8_t)replace)thug_script_events_remove(t,event->value,mem());
        ThugScriptEventEntry *entry=next+i;ThugScriptStructure *params;
        if(thug_script_get_structure(s,0x7031f10c,&params,0)){
            ThugScriptStructure *copy=thug_script_structure_allocate(8,mem());
            entry->parameters=copy?thug_script_structure_copy_construct_draft(copy,params):0;
        }else entry->parameters=0;
        if(!thug_script_get_checksum(s,0x923fbb3a,&entry->group,0))entry->group=0x1ca1ff20;
        uint8_t flag=thug_script_has_flag(s,0x80367192);
        *(uint8_t *)&entry->flags=(*(uint8_t *)&entry->flags&0xfc)|(flag&1);
        entry->event=event->value;entry->script=script->value;t->stop_iteration=1;used++;
    }
    if(t->entries)for(uint32_t i=0;(int32_t)i<(int32_t)t->count;i++)copy_entry(next+used++,t->entries+i);
    mem()->release(mem()->context,t->entries);t->entries=next;t->count=used;mem()->temp_scope(mem()->context,0);
}
/* 004734e0. The replacement argument tests the full WORD before passing a
 * boolean to the table, unlike the table's own low-byte ABI. */
void thug_script_set_events_draft(ThugScriptInstance *script,ThugScriptArray *array,uint32_t replace){
    mem()->temp_scope(mem()->context,6);
    if(!script->events){ThugScriptEventTable *t=mem()->allocate(mem()->context,16,1);script->events=t?thug_script_events_initialize_draft(t):0;}
    else thug_script_events_unsubscribe(script->events,script,mem());
    thug_script_events_add_draft(script->events,array,replace!=0);
    thug_script_events_compact_draft(script->events);thug_script_events_subscribe_draft(script->events,script);
    mem()->temp_scope(mem()->context,0);
}
/* 00461290. Preserve selected-pool semantics and assign the owned script
 * before calling its complete named setup. */
void thug_object_ensure_script_draft(ThugUiObjectBase *p){
    if(!p->object.unknown_8_to_10[2]){
        mem()->temp_scope(mem()->context,1);ThugScriptInstance *script=thug_script_allocate(0xf4,mem());
        if(script)script=thug_script_initialize(script);p->object.unknown_8_to_10[2]=(uintptr_t)script;
        thug_script_setup_named(script,0x3f5cdb8a,0,&p->object,diag(),mem());mem()->temp_scope(mem()->context,0);
    }
}
/* 00460c20. Remove both named and anonymous-value parameters for each live
 * array item. A null array removes the entire owned structure. */
void thug_object_remove_parameters_draft(ThugUiObjectBase *p,ThugScriptArray *array){
    ThugScriptStructure *s=p->parameters;if(!s)return;
    if(array){
        for(uint32_t i=0;i<array->count;i++){
            uint32_t name=(uintptr_t)thug_script_array_structure(array,(int32_t)i);
            thug_script_remove_name(p->parameters,name,mem());thug_script_remove_unnamed_value(p->parameters,name,mem());
        }
        if(!thug_script_structure_empty_draft(p->parameters))return;s=p->parameters;
    }
    if(s)dispose_structure(s);p->parameters=0;
}
/* 00461710. Handler replacement, parameter merging, then parameter removal
 * occur in that order using the real optional QB getters. */
void thug_object_apply_parameters_draft(void *object,ThugScriptStructure *s){
    ThugUiObjectBase *p=object;uint32_t replace=thug_script_has_flag(s,0x3f93a1ef);ThugScriptArray *array;
    if(thug_script_get_array(s,0x475bf03c,&array,0)){
        thug_object_ensure_script_draft(p);thug_script_set_events_draft((void *)(uintptr_t)p->object.unknown_8_to_10[2],array,replace);
    }
    ThugScriptStructure *params;
    if(thug_script_get_structure(s,0x90436bd9,&params,0)){
        thug_ui_object_ensure_parameters(p,mem());thug_script_structure_merge_optional(p->parameters,params,mem());
    }
    if(thug_script_get_array(s,0x8225d629,&array,0))thug_object_remove_parameters_draft(p,array);
}
/* 0044bd30. GotParam queries the running script's arguments, including its
 * anonymous flags, with missing unnamed input defaulting to name zero. */
uint32_t thug_script_got_parameter_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
    uint32_t name=0;thug_script_get_checksum(s,0,&name,0);return thug_script_has_name_or_flag(script->arguments,name);
}
/* 0044a260. Both optional checksums default to zero. */
uint32_t thug_script_checksums_equal_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;uint32_t a=0,b=0;thug_script_get_checksum(s,0x174841bc,&a,0);thug_script_get_checksum(s,0x8e411006,&b,0);return a==b;
}
/* 0044a2c0. StringEquals compares normalized CHECKSUMS, not string bytes.
 * Both required strings must exist, as in the original live script contract. */
uint32_t thug_script_strings_equal_draft(const ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;const char *a,*b;
    if(!thug_script_get_text_legacy_draft(s,0x174841bc,&a,1)||!thug_script_get_text_legacy_draft(s,0x8e411006,&b,1))__builtin_trap();
    uint32_t second=thug_crc32_string(b);return thug_crc32_string(a)==second;
}
