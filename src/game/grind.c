#include "grind.h"
#include "balance.h"
#include "../script/params.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single

_Static_assert(offsetof(ThugBalanceContext,balances)==0x24,"Balance array offset");
/* 005799d0. The second score receiver is reloaded after the first
 * meter hide can run synchronous script callbacks. */
void thug_balance_stop(ThugBalance *b,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugScore *score=b->score_component->score;
    if(score) {
        thug_score_display_balance_normal(score,0,0,d,m);
        thug_score_display_balance_manual(b->score_component->score,0,0,d,m);
    }
    b->left_button=b->right_button=0;
}
/* 004f8ee0. Reset each balance before clearing the mode and byte flag. */
void thug_balance_context_stop(ThugBalanceContext *c,const ThugDiagnostics *d,const ThugMemory *m) {
    for(unsigned i=0;i<4;++i)thug_balance_stop(c->balances+i,d,m);
    c->parameters.mode=0;*(uint8_t *)&c->parameters.unknown_1c=0;
}
/* 004f8f20. Select the original balance position by mode checksum. */
double thug_balance_position(const ThugBalanceContext *c) {
    unsigned i;
    switch(c->parameters.mode) {
        case 0x8d10119d:case 0x255ed86f:i=1;break;
        case 0x0ac90769:case 0xef24413b:i=0;break;
        case 0x3506ce64:i=3;break;
        case 0xa549b57b:i=2;break;
        default:return 0;
    }
    return c->balances[i].position;
}
/* 005627b0. Per-index saturated counts and the original wrapped
 * denominator of the repetition multiplier. The signed upper gate is retained. */
void thug_score_record_rail(ThugScore *score,int32_t index) {
    if(index>=2500){score->multiplier_154c=1;return;}
    score->unknown_1538++;score->value_153c++;
    uint8_t *combo=(uint8_t *)score+0x1b0+(intptr_t)index;
    if(!*combo){score->unknown_1540++;score->value_1544++;}
    if(*combo!=255)++*combo;
    uint8_t *total=(uint8_t *)score+0xb74+(intptr_t)index;
    if(!*total)score->value_1548++;
    if(*total!=255)++*total;
    int32_t threshold=thug_script_get_global_integer(0x6ee127b7,0);
    if((int32_t)*total>threshold) {
        int32_t denominator=(int32_t)((uint32_t)*total-(uint32_t)threshold+1);
        double value=R(R((double)(21-(int32_t)*combo)*.05000000074505806)/denominator);
        score->multiplier_154c=(float)value;
        if(.10000000149011612>value)value=.10000000149011612;
        score->multiplier_154c=(float)value;
    } else score->multiplier_154c=1;
}
/* 0043da70. ECX seeds the output slot; retain it if the required
 * property does not write a value. Cdecl name argument follows the saved seed. */
double thug_walk_parameter(uint32_t saved_ecx,uint32_t name) {
    float value;__builtin_memcpy(&value,&saved_ecx,4);
    const ThugScriptStructure *params=thug_script_get_global_structure(0x6775e538,0);
    thug_script_get_float(params,name,&value,1);return value;
}
/* 0046ba50. Internal contract: the low-byte weighted index addresses
 * one of the sixteen immutable entries. High argument bits are ignored. */
uint32_t thug_grind_trick_variant(uint32_t a,uint32_t b,uint32_t c,uint32_t d) {
    static const uint32_t values[16]={0,1,2,2,3,5,7,7,4,6,8,8,4,6,8,8};
    return values[(uint8_t)a+2*(uint8_t)b+4*(uint8_t)c+8*(uint8_t)d];
}
#undef R

#include "animation.h"
#include "stats.h"
#include "../network/queue.h"
#include <stddef.h>

_Static_assert(offsetof(ThugPendingFlip,physics)==0x24,"Pending flip physics offset");
static float negated(float x) {
    uint32_t word;__builtin_memcpy(&word,&x,4);word^=0x80000000;
    if((word&0x7f800000)==0x7f800000&&(word&0x7fffff))word|=0x400000;
    __builtin_memcpy(&x,&word,4);return x;
}
/* 004fe120: negate the two orientation axes, refresh the physics
 * matrix and toggle the low byte. Preserve original lane write order. */
void thug_skater_reverse_orientation(ThugSkaterPhysics *p) {
    for(unsigned row=2;;row=0) {
        float *v=p->body->orientation+4*row;
        float x=negated(v[0]),y=negated(v[1]),z=negated(v[2]);
        v[2]=z;v[3]=negated(v[3]);v[0]=x;v[1]=y;
        if(!row)break;
    }
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
    p->unknown_34c_to_34f[0]=!p->unknown_34c_to_34f[0];
}
/* 00511390: message 2a carries the raw flag byte. Read the returned
 * old flag after the actual queue/diagnostic path. Time is unused. */
uint8_t thug_skater_set_board_rotated(ThugPendingFlip *c,uint32_t id,uint32_t rotated,uint32_t time,uint32_t send,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)time;
    if((uint8_t)send) {
        ThugNetworkState *network=thug_network_state;
        ThugPlayerState *player=thug_player_find(network,id);
        if(player&&(uint8_t)thug_player_flag_1(player)) {
            ThugMessageSpec spec;thug_message_spec_initialize(&spec);
            ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
            uint8_t payload[2]={(uint8_t)id,(uint8_t)rotated};
            spec.data=payload;spec.length=2;spec.id=0x2a;
            thug_queue_send_first(client,&spec,d,m);
        }
    }
    uint8_t previous=c->base.unknown_14_to_1b[4];
    c->base.unknown_14_to_1b[4]=(uint8_t)rotated;return previous;
}
/* 00511570: consume the three pending flags in their original order. */
void thug_skater_apply_pending_flip(ThugPendingFlip *c,const ThugDiagnostics *d,const ThugMemory *m) {
    if(c->base.unknown_14_to_1b[5]) {
        thug_skater_toggle_flip(&c->base,d,m);c->base.unknown_14_to_1b[5]=0;
    }
    if(c->base.unknown_14_to_1b[6]) {
        thug_skater_reverse_orientation(c->physics);c->base.unknown_14_to_1b[6]=0;
    }
    if(c->base.unknown_14_to_1b[7]) {
        ThugPlayerState *player=thug_player_find(thug_network_state,((ThugSkaterBody *)c->base.base.owner)->object_id);
        ThugNetworkState *network=thug_network_state;
        ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
        uint32_t time=client->time,rotated=!c->base.unknown_14_to_1b[4],id=((ThugSkaterBody *)c->base.base.owner)->object_id;
        thug_skater_set_board_rotated(c,id,rotated,time,1,d,m);
        uint8_t *completion=c->completion;c->base.unknown_14_to_1b[7]=0;completion[0x1f4]=0;return;
    }
    c->completion[0x1f4]=0;
}

#include "skater.h"
#include "animation.h"
#include "../script/lifetime.h"
#include "../script/params.h"
struct ThugPendingFlip;
void thug_skater_apply_pending_flip(struct ThugPendingFlip *,const ThugDiagnostics *,const ThugMemory *);
static ThugScriptInstance *body_script(const ThugSkaterBody *body) {
    ThugScriptInstance *script;__builtin_memcpy(&script,(const uint8_t *)body+0x10,4);return script;
}
/* 005004b0: allocate the actual body script when absent, select the
 * GrindTrickList category/flag entry, apply pending flips, then run the script. */
void thug_skater_start_grind_script(ThugSkaterPhysics *p,uint32_t category,uint32_t a,uint32_t b,uint32_t c,uint32_t e,const ThugDiagnostics *d,const ThugMemory *m) {
    if(!body_script(p->body)) {
        ThugScriptInstance *script=thug_script_allocate(sizeof(*script),m);
        if(script)thug_script_initialize(script);
        __builtin_memcpy((uint8_t *)p->body+0x10,&script,4);
    }
    if(p->parameter_mode_fallback) {
        ThugSkaterBody *body=p->body;
        thug_script_setup_named(body_script(body),0xf7ca3f78,0,(ThugReferencedObject *)body,d,m);
    } else {
        uint32_t selected=category<=8?category:0;
        ThugScriptArray *table=thug_script_get_global_array(0x2ab3341d,0);
        ThugScriptArray *variants=(void *)thug_script_array_structure(table,selected);
        uint32_t mask=((uint8_t)a!=0)|(((uint8_t)b!=0)<<1)|(((uint8_t)c!=0)<<2)|(((uint8_t)e!=0)<<3);
        uint32_t zero=0;__builtin_memcpy((uint8_t *)p+0x3a8,&zero,4);
        struct ThugPendingFlip *flip=(void *)thug_object_find_component(p->body,0x488af07a);
        thug_skater_apply_pending_flip(flip,d,m);
        ThugSkaterBody *body=p->body;ThugScriptInstance *script=body_script(body);
        uint32_t name=(uint32_t)(uintptr_t)thug_script_array_structure(variants,mask);
        thug_script_setup_named(script,name,0,(ThugReferencedObject *)body,d,m);
    }
    thug_script_execute(body_script(p->body),d,m);
    p->state->unknown_e0=1;
}

#include "../core/memory.h"
#include <stdint.h>
#include <stddef.h>


struct ThugTrickNode {
    const ThugTrickNodeMethods *methods;
    uint32_t value,unknown_8;
    ThugTrickNode *next,*previous;
    uint32_t name,flags,parameter,name_20,parameter_24,related;
    uint8_t disabled;
};
struct ThugTrickLists { uint8_t unknown[0x24];ThugTrickNode *primary,*primary_previous;uint8_t sentinel[12];ThugTrickNode *secondary; };
_Static_assert(offsetof(ThugTrickLists,secondary)==0x38,"Secondary list head");
ThugTrickNode *thug_trick_primary_delete(ThugTrickNode *,uint32_t,const ThugMemory *);
ThugTrickNode *thug_trick_secondary_delete(ThugTrickNode *,uint32_t,const ThugMemory *);
const ThugTrickNodeMethods thug_trick_primary_methods={thug_trick_primary_delete};
const ThugTrickNodeMethods thug_trick_secondary_methods={thug_trick_secondary_delete};
/* Original 511e50 / 511e70. Preserve the write and reload order. */
static void unlink_node(ThugTrickNode *n,const ThugTrickNodeMethods *methods) {
    ThugTrickNode *previous=n->previous,*next=n->next;
    n->methods=methods;previous->next=next;
    next=n->next;previous=n->previous;next->previous=previous;
    n->next=n;n->previous=n;
}
void thug_trick_primary_destroy(ThugTrickNode *n) { unlink_node(n,&thug_trick_primary_methods); }
void thug_trick_secondary_destroy(ThugTrickNode *n) { unlink_node(n,&thug_trick_secondary_methods); }
/* Original 511e90 / 511ed0; their inlined unlink reads previous first. */
static ThugTrickNode *delete_node(ThugTrickNode *n,uint32_t flags,const ThugMemory *m,const ThugTrickNodeMethods *methods) {
    ThugTrickNode *previous=n->previous,*next=n->next;
    n->methods=methods;previous->next=next;
    previous=n->previous;next=n->next;next->previous=previous;
    n->next=n;n->previous=n;
    if((uint8_t)flags&1)m->release(m->context,n);
    return n;
}
ThugTrickNode *thug_trick_primary_delete(ThugTrickNode *n,uint32_t flags,const ThugMemory *m) {return delete_node(n,flags,m,&thug_trick_primary_methods);}
ThugTrickNode *thug_trick_secondary_delete(ThugTrickNode *n,uint32_t flags,const ThugMemory *m) {return delete_node(n,flags,m,&thug_trick_secondary_methods);}
static ThugTrickNode *first(ThugTrickNode *n) {return n->value==UINT32_MAX?NULL:n;}
/* Original 511f60. Select after clearing the requested flags. Capture primary
 * next before either destructor, and remove only the first secondary match. */
void thug_tricks_cancel(ThugTrickLists *lists,uint32_t select,uint32_t clear,const ThugMemory *m) {
    ThugTrickNode *n=first(lists->primary);
    while(n) {
        ThugTrickNode *next=first(n->next);n->flags&=~clear;
        if(n->flags&select) {
            uint32_t related=n->related;
            if(related) {
                ThugTrickNode *s=first(lists->secondary);
                while(s) {
                    ThugTrickNode *following=first(s->next);
                    if(!s->disabled&&s->name_20==n->name&&s->related==related&&s->parameter_24==n->parameter) {
                        s->methods->dispose(s,1,m);break;
                    }
                    s=following;
                }
            }
            n->methods->dispose(n,1,m);
        }
        n=next;
    }
}

#include "skater.h"
#include "../script/lifetime.h"
#include "../script/params.h"
#include "../script/operators.h"
#include "../script/delivery.h"
#include "../core/checksum.h"
#include <stddef.h>
struct ThugPendingFlip;
void thug_skater_apply_pending_flip(struct ThugPendingFlip *,const ThugDiagnostics *,const ThugMemory *);
static uint32_t word(const void *p) { uint32_t v;__builtin_memcpy(&v,p,4);return v; }
static void store(void *p,uint32_t v) { __builtin_memcpy(p,&v,4); }
static void *pointer(const void *p) {return (void *)(uintptr_t)word(p);}
/* Original 00461350. The script instance is reloaded after setup and wait
 * clearing. Successful allocation uses the original fixed-pool/heap adapter. */
ThugScriptInstance *thug_object_set_script(ThugReferencedObject *owner,uint32_t name,const ThugScriptStructure *params,const ThugDiagnostics *d,const ThugMemory *m) {
    uint8_t *body=(void *)owner;ThugScriptInstance *script=pointer(body+0x10);
    if(!script) {
        script=thug_script_allocate(sizeof(*script),m);
        if(script)thug_script_initialize(script);
        store(body+0x10,(uintptr_t)script);
    }
    thug_script_setup_named(script,name,params,owner,d,m);
    thug_script_clear_wait(pointer(body+0x10));
    return pointer(body+0x10);
}
/* Original 00522e80. Loaded trick metadata supplies Scripts or a Template
 * (directly or through TrickSlot). Formatted names fit the original 100 bytes.
 * The fixed CRT %s%s adapter retains its null-string spelling. */
uint8_t thug_skater_run_pending_trick(ThugSkaterNameContext *component,uint32_t a,uint32_t b,uint32_t c,uint32_t e,const ThugDiagnostics *d,const ThugMemory *m) {
    uint8_t *p=(void *)component;
    if(!p[0x12b0])return 0;
    uint32_t key=word(p+0x12b4);p[0x12b0]=0;
    ThugScriptArray *table=thug_script_get_global_array(key,0);if(!table)return 0;
    ThugScriptStructure *entry=thug_script_array_structure(table,word(p+0x12b8));
    ThugScriptArray *scripts=NULL,*template=NULL;const char *prefix=NULL;
    thug_script_get_array(entry,0x22e168c1,&scripts,0);
    thug_script_get_array(entry,0x689fe07c,&template,0);
    thug_script_get_text(entry,0x6c4e7971,&prefix,0);
    if(!scripts&&!template) {
        uint32_t slot=0;thug_script_get_checksum(entry,0xa92a2280,&slot,0);
        if(slot) {
            uint32_t mapped=0;thug_script_get_checksum(pointer(p+0xa28),slot,&mapped,0);
            if(mapped) {
                ThugScriptStructure *replacement=thug_script_get_global_structure(mapped,0);
                if(replacement) {
                    thug_script_get_array(replacement,0x22e168c1,&scripts,0);
                    thug_script_get_array(replacement,0x689fe07c,&template,0);
                    thug_script_get_text(replacement,0x6c4e7971,&prefix,0);
                }
            }
        }
    }
    uint32_t mask=((uint8_t)a!=0)|(((uint8_t)b!=0)<<1)|(((uint8_t)c!=0)<<2)|(((uint8_t)e!=0)<<3),name;
    if(scripts)name=(uintptr_t)thug_script_array_structure(scripts,mask);
    else {
        const char *suffix=thug_script_array_text(template,mask);char text[100],*out=text;
        if(!prefix)prefix="(null)";if(!suffix)suffix="(null)";
        while(*prefix)*out++=*prefix++;while(*suffix)*out++=*suffix++;*out=0;
        name=thug_crc32_string(text);
    }
    ThugScriptStructure *params=NULL;thug_script_get_structure(entry,0x7031f10c,&params,0);
    uint8_t *body=pointer(p+12);
    if(word(body+0x18)==0xbaf9b341)store((uint8_t *)pointer(p+0x28)+0x3a8,0);
    p[0xa24]=p[0x12c4];thug_skater_apply_pending_flip(pointer(p+0x2c),d,m);
    thug_object_set_script((void *)body,name,params,d,m);
    thug_script_execute(pointer(body+0x10),d,m);
    ((uint8_t *)pointer(p+0x30))[0xe0]=1;
    uint32_t count=word(p+0x13ac)+1;store(p+0x13ac,count);
    if((int32_t)count>3)thug_object_broadcast_event(pointer(p+12),0x94182a08,NULL,0,d,m);
    return 1;
}
