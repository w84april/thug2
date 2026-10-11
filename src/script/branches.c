#include "branches.h"
#include "../core/random.h"
#include <stddef.h>
_Static_assert(sizeof(ThugScriptBranchState) == 0x60, "Script branch record");
_Static_assert(offsetof(ThugScriptBranchState, last_choice) == 0x54, "Branch last choice");
ThugScriptBranchState *thug_script_branch_first, *thug_script_branch_last;
uint32_t thug_script_branch_count;

/* 0x0046f870. Keep cached random choices, but allow a later script to claim them. */
void thug_script_branch_detach(ThugScriptInstance *script) {
    for (ThugScriptBranchState *s = thug_script_branch_first; s; s = s->next)
        if (s->script == script) s->script = NULL;
}

/* 0x0046f7a0. The x86 helper receives these arguments in EBX, EDI and ESI.
 * An unowned matching record can be claimed by the current script. */
ThugScriptBranchState *thug_script_branch_find(const uint8_t *offsets, uint32_t type, uint32_t count) {
    ThugScriptInstance *current = thug_script_current();
    for (ThugScriptBranchState *s = thug_script_branch_first; s; s = s->next)
        if (s->offsets == offsets && s->type == type && s->count == count
            && (s->script == current || !s->script)) return s;
    return NULL;
}

/* 0x00470bb0. Remove the oldest allocation when the signed count reaches 100,
 * then prepend the new record. PC pool/heap services use the memory adapter. */
ThugScriptBranchState *thug_script_branch_allocate(const ThugMemory *memory) {
    if ((int32_t)thug_script_branch_count >= 100) {
        ThugScriptBranchState *previous = thug_script_branch_last->previous;
        --thug_script_branch_count;
        memory->release(memory->context, thug_script_branch_last);
        thug_script_branch_last = previous;
        if (previous) previous->next = NULL;
    }
    ThugScriptBranchState *s = memory->allocate(memory->context, sizeof(*s), 1);
    ++thug_script_branch_count;
    s->previous = NULL;
    s->next = thug_script_branch_first;
    thug_script_branch_first = s;
    if (s->next) s->next->previous = s;
    else thug_script_branch_last = s;
    return s;
}

/* 0x0046f8a0. Ten swaps per choice, two random calls each. The final optional
 * swap prevents the first entry from repeating the previous cycle's last. */
void thug_script_branch_shuffle(ThugScriptBranchState *s, uint8_t avoid_previous) {
    uint8_t previous = *((uint8_t *)s + 0x11 + s->count);
    for (uint32_t remaining = s->count * 10u; remaining; --remaining) {
        int32_t a = thug_random_range(s->count), b = thug_random_range(s->count);
        uint8_t value = s->order[a];
        s->order[a] = s->order[b]; s->order[b] = value;
    }
    if (avoid_previous && s->order[0] == previous) {
        int32_t other = thug_random_range(s->count - 1u) + 1;
        uint8_t value = s->order[0];
        s->order[0] = s->order[other]; s->order[other] = value;
    }
}

static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static uint16_t read16(const uint8_t *p) { return (uint16_t)p[0] | (uint16_t)p[1] << 8; }
static const uint8_t *relative32(const uint8_t *p) {
    return (const uint8_t *)((uintptr_t)p + 4u + read32(p));
}

/* 0x00470c60. Relative offsets and arithmetic wrap as 32-bit words. Weighted
 * branches use signed 16-bit weights. Cached choices are keyed by the offset
 * table, token type, full count argument and current script. */
const uint8_t *thug_script_resolve_branches(const uint8_t *p, const ThugMemory *memory) {
    for (;;) {
        uint8_t token = *p;
        if (token == 0x2e) { p = relative32(p + 1); continue; }
        if (token == 0x49) { ++p; p += read16(p); continue; }
        if (token == 0x2f || token == 0x37) {
            uint32_t count = read32(p + 1), total = 0, choice = 0;
            const uint8_t *weights = p + 5;
            for (uint32_t i = 0; i < count; ++i) total += (uint32_t)(int32_t)(int16_t)read16(weights + i * 2);
            uint32_t remaining = (uint32_t)(token == 0x2f ? thug_random_range(total) : thug_random_alternate_range(total));
            remaining -= (uint32_t)(int32_t)(int16_t)read16(weights);
            while ((int32_t)remaining >= 0) {
                ++choice;
                remaining -= (uint32_t)(int32_t)(int16_t)read16(weights + choice * 2);
            }
            p = relative32(weights + count * 2 + choice * 4);
            continue;
        }
        if (token != 0x40 && token != 0x41) return p;
        uint32_t count = read32(p + 1), choice;
        const uint8_t *offsets = p + 5 + count * 2;
        ThugScriptBranchState *s = thug_script_branch_find(offsets, token, count);
        if (!s) {
            s = thug_script_branch_allocate(memory);
            s->offsets = offsets; s->type = token; s->count = (uint16_t)count;
            if (token == 0x40) s->last_choice = thug_random_range(count);
            else {
                s->index = 0;
                for (uint32_t i = 0; i < s->count; ++i) s->order[i] = (uint8_t)i;
                thug_script_branch_shuffle(s, 0);
            }
        }
        s->script = thug_script_current();
        if (token == 0x40) {
            uint32_t random = (uint32_t)thug_random_range(count), retries = 0;
            while ((random & 0xffff) == s->last_choice) {
                if (++retries > 100) break;
                random = (uint32_t)thug_random_range(count);
            }
            choice = random & 0xffff; s->last_choice = choice;
        } else {
            ++s->index;
            if (s->index >= s->count) { thug_script_branch_shuffle(s, 1); s->index = 0; }
            choice = s->order[s->index];
        }
        p = relative32(offsets + choice * 4);
    }
}
