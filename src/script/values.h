#ifndef THUG_SCRIPT_VALUES_H
#define THUG_SCRIPT_VALUES_H
#include "params.h"
#include "../core/memory.h"
#include "../core/memory_state.h"
extern uint32_t thug_script_structure_pool_index;
extern ThugFixedPool *thug_script_structure_pools[2];
void *thug_script_structure_allocate(uint32_t, const ThugMemory *);
void thug_script_structure_free(void *, const ThugMemory *);
/* Original shared string storage bounds: 6f3574 and 6f357c.
 * Pooled string addresses must not be freed. */
extern uint32_t thug_script_string_pool, thug_script_string_pool_size;
typedef struct { uint32_t checksum; char *text; } ThugScriptStringEntry;
typedef struct { uint8_t tag, padding[3]; float x, y, z; } ThugScriptVector;
/* 6f3570, 6f3578, 6f3580, 6f3584. The caller provides enough pool/table space. */
extern uint8_t thug_script_string_interning;
extern char *thug_script_string_cursor;
extern ThugScriptStringEntry *thug_script_string_entries;
extern uint32_t thug_script_string_count;
ThugScriptStructure *thug_script_structure_initialize(ThugScriptStructure *);
ThugScriptComponent *thug_script_component_initialize(ThugScriptComponent *);
ThugScriptArray *thug_script_array_initialize(ThugScriptArray *);
uint32_t *thug_script_array_items(ThugScriptArray *);
void thug_script_string_release(void *, const ThugMemory *);
void thug_script_array_clear_storage(ThugScriptArray *, const ThugMemory *);
void thug_script_array_clear(ThugScriptArray *, const ThugMemory *);
void thug_script_component_clear(ThugScriptComponent *, const ThugMemory *);
void thug_script_structure_clear(ThugScriptStructure *, const ThugMemory *);
void thug_script_structure_destroy(ThugScriptStructure *, const ThugMemory *);
void thug_script_structure_insert(ThugScriptStructure *, ThugScriptComponent *, const ThugMemory *);
uint8_t thug_script_structure_contains(const ThugScriptStructure *, const ThugScriptStructure *);
ThugScriptVector *thug_script_vector_initialize(ThugScriptVector *);
char *thug_script_string_intern(const char *);
char *thug_script_string_copy(const char *, const ThugMemory *);
void thug_script_array_set_size(ThugScriptArray *, uint32_t count, uint8_t type, const ThugMemory *);
void thug_script_array_copy_items(uint32_t *destination, const uint32_t *source, uint32_t count, uint32_t type, const ThugMemory *);
void thug_script_array_copy(ThugScriptArray *destination, ThugScriptArray *source, const ThugMemory *);
void thug_script_component_copy(ThugScriptComponent *destination, const ThugScriptComponent *source, uint32_t borrow_nested, const ThugMemory *);
/* Source/destination lists must be separate and owned graphs must be acyclic. */
ThugScriptStructure *thug_script_structure_merge(ThugScriptStructure *, const ThugScriptStructure *, const ThugMemory *);
ThugScriptStructure *thug_script_structure_merge_optional(ThugScriptStructure *, const ThugScriptStructure *, const ThugMemory *);
void thug_script_set_string(ThugScriptStructure *, uint32_t name, const char *, const ThugMemory *);
void thug_script_set_local_string(ThugScriptStructure *, uint32_t name, const char *, const ThugMemory *);
void thug_script_set_integer(ThugScriptStructure *, uint32_t name, uint32_t value, const ThugMemory *);
/* Float arguments remain raw words, as loaded by the original MOV instructions. */
void thug_script_set_float_bits(ThugScriptStructure *, uint32_t name, uint32_t bits, const ThugMemory *);
void thug_script_set_checksum(ThugScriptStructure *, uint32_t name, uint32_t value, const ThugMemory *);
void thug_script_set_scalar(ThugScriptStructure *, uint32_t name, uint32_t type, uint32_t value, const ThugMemory *);
void thug_script_set_vector_bits(ThugScriptStructure *, uint32_t name, uint32_t x, uint32_t y, uint32_t z, const ThugMemory *);
void thug_script_set_pair_bits(ThugScriptStructure *, uint32_t name, uint32_t x, uint32_t y, const ThugMemory *);
void thug_script_set_array(ThugScriptStructure *, uint32_t name, ThugScriptArray *, const ThugMemory *);
void thug_script_set_array_copy(ThugScriptStructure *, uint32_t name, ThugScriptArray *, const ThugMemory *);
void thug_script_array_set_word(ThugScriptArray *, int32_t index, uint32_t value);
void thug_script_set_structure(ThugScriptStructure *, uint32_t name, ThugScriptStructure *, const ThugMemory *);
void thug_script_set_structure_copy(ThugScriptStructure *, uint32_t name, const ThugScriptStructure *, const ThugMemory *);
void thug_script_set_blob(ThugScriptStructure *, uint32_t name, const uint8_t *, uint32_t length, const ThugMemory *);
ThugScriptStructure *thug_script_structure_assign(ThugScriptStructure *, const ThugScriptStructure *, const ThugMemory *);
ThugScriptComponent *thug_script_find_component(const ThugScriptStructure *, uint32_t name);
#endif
