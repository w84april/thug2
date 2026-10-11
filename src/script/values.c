#include "values.h"
#include <stddef.h>
/* Original structure allocator selection 6f3614/6f361c. Other value pools
 * remain disabled by the current loader contract. */
uint32_t thug_script_structure_pool_index;
ThugFixedPool *thug_script_structure_pools[2];
/* 0x00409030. Host memory services replace the original heap initialization.
 * A selected pool takes precedence even when it is empty; size is for the heap. */
void *thug_script_structure_allocate(uint32_t size, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_structure_pools[thug_script_structure_pool_index];
    return pool ? thug_pool_allocate(pool) : memory->allocate(memory->context, size, 1);
}
/* 0x00409070. Search selected then alternate pool before generic disposal. */
void thug_script_structure_free(void *structure, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_structure_pools[thug_script_structure_pool_index];
    if (pool && thug_pool_contains(pool, structure)) { thug_pool_release(pool, structure); return; }
    pool = thug_script_structure_pools[thug_script_structure_pool_index ^ 1];
    if (pool && thug_pool_contains(pool, structure)) thug_pool_release(pool, structure);
    else memory->release(memory->context, structure);
}

uint32_t thug_script_string_pool, thug_script_string_pool_size;

/* 0x00476410. Constructor fields only; other header bytes are preserved. */
ThugScriptStructure *thug_script_structure_initialize(ThugScriptStructure *s) {
    s->first = NULL;
    ((uint8_t *)&s->unknown_0)[1] = 0;
    return s;
}
/* 0x0046d140. Byte 1 is deliberately not initialized. */
ThugScriptComponent *thug_script_component_initialize(ThugScriptComponent *c) {
    c->name = 0;
    c->padding[1] = c->padding[2] = 0;
    c->value = 0; c->next = NULL; c->type_and_flags = 0;
    return c;
}
/* 0x0046caa0. Bytes 2 and 3 are preserved. */
ThugScriptArray *thug_script_array_initialize(ThugScriptArray *array) {
    ((uint8_t *)&array->unknown_0)[1] = 0;
    array->value_or_items = 0; array->count = 0;
    ((uint8_t *)&array->unknown_0)[0] = 0;
    return array;
}
/* 0x0046cb00. Return the address of the inline slot, not its value. */
uint32_t *thug_script_array_items(ThugScriptArray *array) {
    return array->count == 1 ? &array->value_or_items : (uint32_t *)(uintptr_t)array->value_or_items;
}

/* 0x00476340. Unsigned bounds with the original 32-bit end-address wrap. */
void thug_script_string_release(void *string, const ThugMemory *memory) {
    uint32_t address = (uint32_t)(uintptr_t)string;
    if (address >= thug_script_string_pool && address < thug_script_string_pool + thug_script_string_pool_size) return;
    /* The tail-called 0x005bbb60 also treats a null pointer as a no-op. */
    if (string) memory->release(memory->context, string);
}

/* 0x0046cab0. A single item occupies the object itself. This function frees
 * only a separate item buffer, not the items' payloads or the array object. */
void thug_script_array_clear_storage(ThugScriptArray *array, const ThugMemory *memory) {
    if (array->count == 1) {
        array->count = 0;
        ((uint8_t *)&array->unknown_0)[1] = 0;
        if (array->value_or_items) array->value_or_items = 0;
    } else {
        if (array->value_or_items) {
            memory->release(memory->context, (void *)(uintptr_t)array->value_or_items);
            array->value_or_items = 0;
        }
        ((uint8_t *)&array->unknown_0)[1] = 0;
        array->count = 0;
    }
}

/* 0x00477140. Payload ownership is determined by the array's raw type byte.
 * Valid owned graphs are acyclic, with exclusive ownership of heap payloads. */
void thug_script_array_clear(ThugScriptArray *array, const ThugMemory *memory) {
    uint32_t count = array->count;
    uint8_t type = ((uint8_t *)&array->unknown_0)[1];
    uint32_t *items = thug_script_array_items(array);
    if (type == 3 || type == 4 || type == 5 || type == 6 || type == 10 || type == 12) {
        for (uint32_t i = 0; i < count; ++i) {
            if (!items[i]) continue;
            void *value = (void *)(uintptr_t)items[i];
            if (type == 3 || type == 4) thug_script_string_release(value, memory);
            else if (type == 10) {
                thug_script_structure_clear(value, memory);
                thug_script_structure_free(value, memory);
            } else if (type == 12) {
                thug_script_array_clear(value, memory);
                value = (void *)(uintptr_t)items[i];
                if (value) {
                    thug_script_array_clear_storage(value, memory);
                    memory->release(memory->context, value);
                }
            } else memory->release(memory->context, value);
            items[i] = 0;
        }
    }
    thug_script_array_clear_storage(array, memory);
}

/* 0x004772a0. Release the payload but preserve name, next, padding and bit 0.
 * Type 7 additionally clears its 16-bit length. Types 20/21 are borrowed. */
void thug_script_component_clear(ThugScriptComponent *c, const ThugMemory *memory) {
    uint8_t type = c->type_and_flags >> 1;
    void *value = (void *)(uintptr_t)c->value;
    if (value) {
        switch (type) {
        case 3: case 4:
            thug_script_string_release(value, memory); break;
        case 5: case 6: case 7:
            memory->release(memory->context, value); break;
        case 10:
            thug_script_structure_clear(value, memory);
            thug_script_structure_free(value, memory); break;
        case 12:
            thug_script_array_clear(value, memory);
            value = (void *)(uintptr_t)c->value;
            if (value) {
                thug_script_array_clear_storage(value, memory);
                memory->release(memory->context, value);
            }
            break;
        default: break;
        }
    }
    if (type == 7) c->padding[1] = c->padding[2] = 0;
    c->value = 0;
    c->type_and_flags &= 1;
}

/* 0x00477090. Snapshot next before disposing the current member. */
void thug_script_structure_clear(ThugScriptStructure *s, const ThugMemory *memory) {
    ThugScriptComponent *c = s->first;
    while (c) {
        ThugScriptComponent *next = c->next;
        thug_script_component_clear(c, memory);
        memory->release(memory->context, c);
        c = next;
    }
    s->first = NULL;
}
/* 0x00477130 is a tail-jump alias of the same clear operation. */
void thug_script_structure_destroy(ThugScriptStructure *s, const ThugMemory *memory) {
    thug_script_structure_clear(s, memory);
}

/* 0x00477920. Remove every matching member, then append the incoming member.
 * Int and float types replace each other; other differing types coexist.
 * Unnamed checksum flags replace only the same literal checksum. */
void thug_script_structure_insert(ThugScriptStructure *s, ThugScriptComponent *incoming, const ThugMemory *memory) {
    ThugScriptComponent *previous = NULL, *c = s->first;
    while (c) {
        uint8_t old_type = c->type_and_flags >> 1, new_type = incoming->type_and_flags >> 1;
        uint8_t same = old_type == new_type || (old_type == 1 && new_type == 2) || (old_type == 2 && new_type == 1);
        if (old_type == 13 && new_type == 13 && !c->name && c->value != incoming->value) same = 0;
        if (c->name == incoming->name && same) {
            if (previous) previous->next = c->next;
            else s->first = c->next;
            thug_script_component_clear(c, memory);
            memory->release(memory->context, c);
            c = previous ? previous->next : s->first;
        } else { previous = c; c = c->next; }
    }
    if (previous) previous->next = incoming;
    else s->first = incoming;
    incoming->next = NULL;
}

/* 0x00476bc0. Identity and owned nested structures participate; arrays and
 * borrowed structures do not. The original assumes an acyclic graph. */
uint8_t thug_script_structure_contains(const ThugScriptStructure *s, const ThugScriptStructure *target) {
    if (s == target) return 1;
    for (const ThugScriptComponent *c = s->first; c; c = c->next)
        if ((c->type_and_flags & 0xfe) == 0x14 && thug_script_structure_contains(
                (const ThugScriptStructure *)(uintptr_t)c->value, target)) return 1;
    return 0;
}
