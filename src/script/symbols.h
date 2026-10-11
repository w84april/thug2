#ifndef THUG_SCRIPT_SYMBOLS_H
#define THUG_SCRIPT_SYMBOLS_H
#include "parser.h"

/* Original iteration globals 6f363c/6f3640. Iteration is shared and cannot be
 * nested. The original reads one slot beyond the 4096 buckets when finishing;
 * provide a readable trailing slot as well as valid acyclic bucket chains. */
extern ThugScriptSymbol *thug_script_symbol_iteration_entry;
extern uint32_t thug_script_symbol_iteration_bucket;
ThugScriptSymbol *thug_script_symbol_find(uint32_t name);
void thug_script_symbol_insert(ThugScriptSymbol *);
void thug_script_symbol_unlink(ThugScriptSymbol *);
ThugScriptSymbol *thug_script_symbol_iterate(const ThugScriptSymbol *previous);
ThugScriptSymbol *thug_script_symbol_create(uint32_t name, const ThugMemory *);
void thug_script_symbol_destroy(ThugScriptSymbol *, const ThugMemory *);
/* Creates a new symbol even for unsupported tokens, which leave the cursor
 * unchanged. Existing same-name entries are not removed by this routine. */
const uint8_t *thug_script_register_value(const uint8_t *, uint32_t name, const char *filename, const ThugMemory *);
uint32_t thug_script_body_checksum(const uint8_t *);
#endif
