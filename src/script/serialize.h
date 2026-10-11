#ifndef THUG_SCRIPT_SERIALIZE_H
#define THUG_SCRIPT_SERIALIZE_H
#include "params.h"
/* Compact parameter format used by script dispatch. Internal input contract:
 * initialized name-table symbols, valid acyclic value graphs, terminated strings
 * and representable array storage. Failure returns 0 and retains partial writes.
 * reserved is propagated recursively but does not alter this specimen's output. */
typedef void (*ThugScriptSerializeCallback)(void);
uint8_t *thug_script_write_named_header(uint8_t *, uint32_t type, uint32_t name);
uint32_t thug_script_serialize_integer(uint32_t name, uint32_t value, uint8_t *, uint32_t capacity);
uint32_t thug_script_serialize_float(uint8_t *, uint32_t name, uint32_t bits, uint32_t capacity);
uint32_t thug_script_serialize_string(const char *, uint8_t *, uint32_t name, uint32_t capacity);
uint32_t thug_script_serialize_local_string(const char *, uint8_t *, uint32_t name, uint32_t capacity);
uint32_t thug_script_serialize_array(const ThugScriptArray *, uint8_t *, uint32_t capacity, uint32_t reserved);
uint32_t thug_script_serialize_structure(const ThugScriptStructure *, uint8_t *, uint32_t capacity,
    uint32_t reserved, ThugScriptSerializeCallback);
#endif
