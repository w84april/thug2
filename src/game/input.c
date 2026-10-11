#include "skater.h"
#include "../core/timing.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>
const void *thug_input_manager;

/* 0x0051ea40. The original checksum arrives in EAX; only AL is the result. */
uint8_t thug_input_is_direction(uint32_t name) {
    switch(name) {
    case 0xb7231a95:case 0x85981897:case 0x4b358aeb:case 0x786b8b68:
    case 0xa50950c5:case 0xbc6b118f:case 0xd8847efa:case 0xe3006fc4:return 1;
    default:return 0;
    }
}

/* 0x0051eb80. Clear pending marks only in the active portion of the ring. */
void thug_skater_clear_input_marks(ThugSkaterNameContext *context) {
    int32_t slot=context->history_head;
    for(uint32_t i=0;i<context->history_count;++i) {
        context->history[slot].consumed=0;
        if(--slot<0)slot+=100;
    }
}

/* 0x0051ec40. Arguments are consecutive members, regardless of their types.
 * Read the next link after writing each output, retaining overlapping writes. */
uint32_t thug_skater_read_trigger_arguments(const ThugSkaterNameContext *context,
    const ThugScriptComponent *member,int32_t count,uint32_t *output) {
    for(int32_t i=0;i<count;++i) {
        uint32_t key=member->value;
        if(key==0x03749393)key=context->matched_input[1];
        else if(key==0x7473a305)key=context->matched_input[2];
        else if(key==0x9a7dc229)key=context->matched_input[0];
        output[i]=key;member=member->next;
    }
    if((member->type_and_flags&0xfe)==2)return member->value;
    return thug_script_get_global_integer(member->value,1);
}

/* 0x0051ecc0. Forward word copies, not a snapshot or memmove. */
void thug_skater_set_matched_input(ThugSkaterNameContext *context,const uint32_t keys[3]) {
    context->matched_input[0]=keys[0];context->matched_input[1]=keys[1];context->matched_input[2]=keys[2];
}

/* 0x0051f7a0. An intervening eligible third key rejects a partial match.
 * Equal keys never complete. Failure retains any consumed marks. */
uint8_t thug_skater_match_two_inputs(ThugSkaterNameContext *context,uint32_t first,
    uint32_t second,uint32_t window,uint32_t mask) {
    int32_t slot=context->history_head;uint8_t seen_first=0,seen_second=0;
    for(uint32_t i=0;i<context->history_count;++i) {
        ThugInputHistoryEntry *entry=&context->history[slot];uint32_t time=entry->time;
        if(thug_frame_time()-time>=window)return 0;
        if(!(entry->mask&mask)&&entry->type==1) {
            if(entry->key==first) { entry->consumed=1;if(seen_second)return 1;seen_first=1; }
            else if(entry->key==second) { entry->consumed=1;if(seen_first)return 1;seen_second=1; }
            else if(seen_first||seen_second)return 0;
        }
        if(--slot<0)slot+=100;
    }
    return 0;
}

_Static_assert(offsetof(ThugSkaterNameContext,trigger_gate)==0x20,"Trigger gate owner");
_Static_assert(offsetof(ThugSkaterNameContext,trigger_scale)==0x28,"Trigger window scale owner");
/* 0x0051fda0. Eighteen trigger selectors share a reverse history walk, but
 * retain distinct transitions and exits. Expiry preserves marks; exhaustion
 * generally clears them. PressTwoAnyOrder and the three-record selector are
 * exceptions. Unknown selector names remain literal checksums. */
uint8_t thug_skater_match_trick_input(ThugSkaterNameContext *context,const ThugScriptStructure *trigger,
    uint32_t commit,uint32_t ignore,uint32_t scale_window) {
    if(!trigger)return 0;
    if(context->trigger_gate->blocked_498||context->trigger_gate->blocked_499)return 0;
    const ThugScriptComponent *member=thug_script_find_name_or_flag(trigger,0);
    if(!member)return 0;
    uint32_t selector=member->value,keys[3]={0,0,0};member=member->next;
    if(selector==0xa8123ecf) {
        uint32_t second=member->next->value,third=member->next->next->value;
        return thug_skater_named_button(context,member->value)&&
            thug_skater_named_button(context,second)&&thug_skater_named_button(context,third);
    }
    int32_t count;uint32_t previous_direction=0;
    switch(selector) {
    case 0xb6258557:
        for(uint32_t i=0;i<3;++i)if(thug_input_is_direction(context->matched_input[i]))previous_direction=context->matched_input[i];
        /* fall through */
    case 0x823b8342:case 0x61b8fce2:case 0x7fa5cdbb:count=1;break;
    case 0xa2e042d7:case 0xac2b1445:case 0xc1ad35c0:case 0xf630dae5:case 0x3fe7c311:count=3;break;
    case 0x14fe9b7d:case 0x2c434c90:case 0x395ec2d4:case 0x3c3028f4:
    case 0x3f369070:case 0x696e5e66:case 0x7d482318:case 0xffb718bd:count=2;break;
    default:goto failed;
    }
    uint32_t window=thug_skater_read_trigger_arguments(context,member,count,keys);
    if(selector==0x14fe9b7d||selector==0x3c3028f4) {
        if(selector==0x14fe9b7d&&thug_skater_named_button(context,keys[1])) {
            int32_t slot=context->history_head;
            for(uint32_t i=0;i<context->history_count;++i) {
                ThugInputHistoryEntry *entry=&context->history[slot];
                if(entry->type==1&&entry->key==keys[1]) { entry->consumed=1;break; }
                if(--slot<0)slot+=100;
            }
            if(!thug_skater_consume_recent_input(context,keys[0],window,ignore))goto failed;
        } else {
            if(selector==0x3c3028f4&&(!thug_skater_named_button(context,keys[0])||!thug_skater_named_button(context,keys[1])))goto failed;
            if(!thug_skater_match_two_inputs(context,keys[0],keys[1],window,ignore))goto failed;
        }
        goto commit_match;
    }
    if(selector==0x696e5e66) {
        int32_t found[3]={-1,-1,-1},slot=context->history_head;uint32_t n=0;
        for(uint32_t i=0;i<context->history_count;++i) {
            const ThugInputHistoryEntry *entry=&context->history[slot];uint32_t key=entry->key;
            if(!(entry->mask&ignore)&&key!=0xbc6b118f&&key!=0xe3006fc4&&key!=0x85981897&&key!=0x4b358aeb) {
                found[n++]=slot;if(n==3)break;
            }
            if(--slot<0)slot+=100;
        }
        if(n<3)return 0;
        for(uint32_t i=0;i<3;++i) { uint32_t time=context->history[found[i]].time;if(thug_frame_time()-time>=window)return 0; }
        ThugInputHistoryEntry *a=&context->history[found[0]],*b=&context->history[found[1]],*c=&context->history[found[2]];
        if(a->type!=2||a->key!=keys[1]||b->type!=1||b->key!=keys[1]||c->type!=2||c->key!=keys[0])goto failed;
        a->consumed=1;b->consumed=1;c->consumed=1;goto commit_match;
    }
    if(selector==0x823b8342&&(uint8_t)scale_window&&context->trigger_scale->window_scale<1.0) {
        double value=(int32_t)window;
        if((int32_t)window<0)value=thug_platform_round_x87_single(value+4294967296.0);
        window=thug_truncate_double_low_word(thug_platform_round_x87_single(value/context->trigger_scale->window_scale));
    }
    uint32_t state=0;uint8_t first=0,second=0,third=0,found=0;
    int32_t slot=context->history_head,found_slot=0;
    for(uint32_t i=0;i<context->history_count;++i) {
        ThugInputHistoryEntry *entry=&context->history[slot];uint32_t time=entry->time;
        if(thug_frame_time()-time>=window) {
            if(selector==0xb6258557)break;
            return 0;
        }
        uint8_t available=!(entry->mask&ignore);
        uint32_t key=entry->key,type=entry->type;
        switch(selector) {
        case 0x823b8342:case 0x61b8fce2:
            if(available&&type==(selector==0x823b8342?1u:2u)&&key==keys[0]) {
                entry->mask|=commit;thug_skater_set_matched_input(context,keys);return 1;
            }
            break;
        case 0xb6258557:
            if(available&&type==1) {
                if(key==keys[0]) { found=1;found_slot=slot; }
                else if(thug_input_is_direction(key)) {
                    if(key!=previous_direction)return 0;
                    entry->consumed=1;
                }
            }
            break;
        case 0x3f369070:
            if(available&&key==keys[0]) {
                if(type==2) { entry->consumed=1;first=second=0; }
                else if(type==1) { entry->consumed=1;if(second)goto commit_match;first=1; }
            }
            if(available&&key==keys[1]) {
                if(type==2) { entry->consumed=1;first=second=0; }
                else if(type==1) { entry->consumed=1;if(first)goto commit_match;second=1; }
            }
            break;
        case 0x395ec2d4:case 0xac2b1445:
            if(!first&&available&&type==2&&key==keys[0]) { entry->consumed=1;first=1; }
            if(!second&&available&&type==2&&key==keys[1]) { entry->consumed=1;second=1; }
            if(selector==0xac2b1445&&!third&&available&&type==1&&key==keys[2]) { entry->consumed=1;third=1; }
            if(first) {
                if(second) { if(selector==0x395ec2d4||third)goto commit_match; }
                else if(available&&type==1&&key==keys[0])return 0;
            } else if(second&&available&&type==1&&key==keys[1])return 0;
            break;
        case 0x7fa5cdbb:case 0x7d482318:case 0xffb718bd:
            if(!state) {
                uint32_t desired_type=selector==0x7d482318?1:2;
                uint32_t desired_key=selector==0x7fa5cdbb?keys[0]:keys[1];
                if(available&&type==desired_type&&key==desired_key) { entry->consumed=1;state=1; }
            } else if(available&&type==1&&key==keys[0]) {
                entry->consumed=1;
                if(selector==0x7fa5cdbb) { thug_skater_commit_input_marks(context,commit);return 1; }
                goto commit_match;
            }
            break;
        case 0x2c434c90:
            if(available&&((state==0&&type==2&&key==keys[1])||(state>0&&type==1&&key==keys[0]))) {
                entry->consumed=1;if(++state==3)goto commit_match;
            }
            break;
        case 0xc1ad35c0:
            if(available&&type==1&&key==keys[2-state]) { entry->consumed=1;if(++state==3)goto commit_match; }
            break;
        case 0x3fe7c311: {
            uint32_t desired_key=state==0?keys[2]:state<3?keys[1]:keys[0];
            if(available&&type==((state==1||state==3)?2u:1u)&&key==desired_key) {
                entry->consumed=1;if(++state==5)goto commit_match;
            }
            break;
        }
        case 0xa2e042d7:
            if(state==0) {
                if(available&&type==1) {
                    if(key==keys[2]) { entry->consumed=1;state=1; }
                    else if(key==keys[1]) { entry->consumed=1;state=2; }
                }
            } else if(state<3) {
                if(available&&type==1&&key==keys[state==1?1:2]) { entry->consumed=1;state=3; }
            } else if(available&&key==keys[0]&&type==(state==3?2u:1u)) {
                entry->consumed=1;if(++state==5)goto commit_match;
            }
            break;
        case 0xf630dae5:
            if(state==0) {
                if(available&&type==1&&key==keys[2]) { entry->consumed=1;state=1; }
            } else if(available) {
                if(state==1) {
                    if(key==keys[1]) { if(type==2)return 0;if(type==1) { entry->consumed=1;state=2; } }
                    else if(key==keys[0]) { if(type==2)return 0;if(type==1) { entry->consumed=1;state=3; } }
                } else if(key==keys[state==2?0:1]) {
                    if(type==2)return 0;
                    if(type==1) { entry->consumed=1;goto commit_match; }
                }
            }
            break;
        }
        if(--slot<0)slot+=100;
    }
    if(selector==0xb6258557&&found) { context->history[found_slot].mask|=commit;goto commit_match; }
    if(selector==0x3f369070)return 0;
failed:
    thug_skater_clear_input_marks(context);return 0;
commit_match:
    thug_skater_commit_input_marks(context,commit);
    thug_skater_set_matched_input(context,keys);return 1;
}
/* 0x0044e630. Stored logical-device mapping; callers supply a valid slot. */
uint32_t thug_input_device_id(const void *manager, uint32_t slot) {
    return ((const uint32_t *)manager)[0x110 / 4 + slot];
}
_Static_assert(offsetof(ThugInputButton, timestamp) == 4, "Button timestamp");
_Static_assert(offsetof(ThugSkaterInput, button_60) == 0x60, "Button 60");
_Static_assert(offsetof(ThugSkaterInput, button_80) == 0x80, "Button 80");
_Static_assert(offsetof(ThugSkaterInput, button_1c0) == 0x1c0, "Button 1c0");
_Static_assert(offsetof(ThugInputButton, pending_14) == 0x14, "Button pending word");
_Static_assert(offsetof(ThugInputButton, pending_10) == 0x10, "Button latch");
_Static_assert(sizeof(ThugSkaterInput) == 0x200, "Sixteen input button records");
/* 0x0046c270. The original priority is not address order. Button names live
 * beyond the recovered button prefix, at +0x18 in each 0x20-byte record. */
ThugInputButton *thug_input_find_button(ThugSkaterInput *input, uint32_t name) {
    static const uint16_t order[] = {0,0x20,0x40,0x60,0x160,0x140,0x180,0x1a0,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x1c0,0x1e0};
    for (unsigned i=0;i<sizeof(order)/sizeof(order[0]);++i) {
        uint8_t *button = (uint8_t *)input+order[i];
        uint32_t checksum; __builtin_memcpy(&checksum,button+0x18,4);
        if (checksum == name) return (ThugInputButton *)button;
    }
    return NULL;
}

/* 0x0046b7e0. Clear only the one-byte latch. */
void thug_input_button_clear_latch(ThugInputButton *button) { button->pending_10 = 0; }

/* 0x0046b7f0. Other button fields, including both timestamps, are retained. */
void thug_input_button_clear_pending(ThugInputButton *button) { button->pending_14 = 0; }

/* 0x0046b920. The saved timestamp is read before the timer call. */
uint32_t thug_input_button_elapsed(const ThugInputButton *button) {
    uint32_t previous = button->timestamp;
    return thug_elapsed_time() + (thug_timer_offset - previous);
}
/* 0x0046b900. The second timestamp has the same unsigned timer arithmetic. */
uint32_t thug_input_button_elapsed_8(const ThugInputButton *button) {
    uint32_t previous=button->timestamp_8;
    return thug_elapsed_time()+(thug_timer_offset-previous);
}

_Static_assert(offsetof(ThugSkaterNameContext, history) == 0x38, "Input history");
_Static_assert(offsetof(ThugSkaterNameContext, history_count) == 0x998, "Input history count");
_Static_assert(offsetof(ThugSkaterNameContext, matched_input) == 0x99c, "Matched input triplet");
_Static_assert(offsetof(ThugSkaterNameContext, button_state) == 0xa00, "Named input state");
_Static_assert(offsetof(ThugSkaterNameContext, name) == 0x1331, "Skater name retained");
uint32_t thug_input_button_names[22] = {
    0,0xbc6b118f,0xe3006fc4,0x85981897,0x4b358aeb,0xb7231a95,0xa50950c5,
    0xd8847efa,0x786b8b68,0x2b489a86,0x321c9756,0x7323e97c,0x20689278,
    0x26b0c991,0xbfb9982b,0xc8bea8bd,0xf2f1f64e,0x6bf8a7f4,0x1cff9762,
    0x767a45d7,0xbd30325b,0x9d2d8850
};
/* 0x0044e5a0 / 0x0051ecf0. Index zero is the unmatched-name state. */
uint32_t thug_input_button_index(uint32_t name) {
    for (uint32_t i = 1; i < 22; ++i) if (thug_input_button_names[i] == name) return i;
    return 0;
}
uint8_t thug_skater_named_button(const ThugSkaterNameContext *context, uint32_t name) {
    return context->button_state[thug_input_button_index(name)];
}
/* 0x0051f6b0. Valid history has at most 100 entries and a head in 0..99.
 * A consumed entry can match again; only the mask filters prior use. */
uint8_t thug_skater_consume_recent_input(ThugSkaterNameContext *context, uint32_t name, uint32_t window, uint32_t mask) {
    int32_t slot = context->history_head;
    for (uint32_t i = 0; i < context->history_count; ++i) {
        ThugInputHistoryEntry *entry = &context->history[slot];
        uint32_t time = entry->time;
        if (thug_frame_time()-time >= window) return 0;
        if (!(entry->mask & mask) && entry->type == 1 && entry->key == name) {
            entry->consumed = 1; return 1;
        }
        if (--slot < 0) slot += 100;
    }
    return 0;
}

/* 0x0051ebd0. Commit every pending mark in the active history, including marks
 * retained by an earlier failed match. Unmarked entries keep their masks. */
void thug_skater_commit_input_marks(ThugSkaterNameContext *context,uint32_t mask) {
    int32_t slot=context->history_head;
    for(uint32_t i=0;i<context->history_count;++i) {
        ThugInputHistoryEntry *entry=&context->history[slot];
        if(entry->consumed) { uint32_t combined=entry->mask|mask;entry->consumed=0;entry->mask=combined; }
        if(--slot<0)slot+=100;
    }
}

/* 0x0051f9b0. The two-entry proximity test deliberately uses signed physical
 * indices, not ring distance. Failure retains marks; the final accepted entry
 * is not itself marked. Valid history uses at most 100 slots. */
uint8_t thug_skater_match_rotation_input(ThugSkaterNameContext *context,const uint32_t keys[3],uint32_t override) {
    int32_t slot=context->history_head,first=0;
    uint32_t state=0;
    for(uint32_t i=0;i<context->history_count;++i) {
        ThugInputHistoryEntry *entry=&context->history[slot];
        uint32_t time=entry->time;
        if(thug_frame_time()-time>=1000)return 0;
        if(state==0) {
            if(!(entry->mask&0x100)&&entry->type==1&&entry->key==keys[1]) {
                state=1;first=slot;entry->consumed=1;
            }
        } else if(state==1) {
            if(first-slot>2)return 0;
            if(entry->type==2&&entry->key==keys[2])return 0;
            if(!(entry->mask&0x100)&&entry->type==1&&entry->key==keys[0]) {
                state=2;entry->consumed=1;
            }
        } else {
            if(entry->type==2&&entry->key==keys[2])return 0;
            if((entry->type==1&&entry->key==keys[2])||(uint8_t)override) {
                thug_skater_commit_input_marks(context,0x100);
                context->matched_input[0]=keys[0];context->matched_input[1]=keys[1];context->matched_input[2]=keys[2];
                return 1;
            }
        }
        if(--slot<0)slot+=100;
    }
    return 0;
}

/* 0x0051fb90. No speculative clearing of marks:
 * partial matches, expired histories and unsuccessful searches retain them. */
uint8_t thug_skater_match_release_input(ThugSkaterNameContext *context,
        uint32_t key, uint32_t alternate, uint32_t commit) {
    int32_t slot = context->history_head;
    unsigned state = 0;
    uint32_t saved_key = 0;
    for (uint32_t i = 0; i < context->history_count; ++i) {
        ThugInputHistoryEntry *entry = &context->history[slot];
        if (thug_frame_time() - entry->time >= 1000) return 0;
        if (!entry->mask) {
            if (state == 0 && entry->type == 2 && entry->key == key &&
                    (!(uint8_t)alternate || entry->key == 0x20689278 ||
                     entry->key == 0x2b489a86 || entry->key == 0x321c9756)) {
                saved_key = entry->key;
                entry->consumed = 1;
                state = 1;
            } else if ((uint8_t)alternate && state == 1 &&
                    entry->type == 1 && entry->key == saved_key) {
                entry->consumed = 1;
                state = 2;
            } else if (state == ((uint8_t)alternate ? 2u : 1u) &&
                    entry->type == 1 && entry->key == key) {
                entry->consumed = 1;
                if ((uint8_t)commit) {
                    uint32_t arguments[3] = {key, alternate, commit};
                    thug_skater_commit_input_marks(context, UINT32_MAX);
                    thug_skater_set_matched_input(context, arguments);
                }
                return 1;
            }
        }
        if (--slot < 0) slot += 100;
    }
    return 0;
}
