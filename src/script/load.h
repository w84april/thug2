#ifndef THUG_SCRIPT_LOAD_H
#define THUG_SCRIPT_LOAD_H
#include "cache.h"
typedef struct { uint32_t name; char *text; } ThugScriptDebugName;
typedef struct ThugScriptLocalName {
    uint32_t name; char *text; struct ThugScriptLocalName *next;
} ThugScriptLocalName;
typedef struct {
    ThugScriptSymbol *symbol;
    uint8_t created, padding[3];
} ThugScriptJournalEntry;
/* Original globals: 7cefac, 6f232c, 6f2334, 6f2368, 6f2364,
 * 6f2588..6f3527 and 6f3528. The debug table uses 65536 groups of ten
 * entries; internal routines do not check bucket, string or journal capacity. */
extern uint8_t thug_script_debug_enabled;
extern ThugScriptDebugName *thug_script_debug_names;
extern char *thug_script_debug_cursor;
extern ThugScriptLocalName *thug_script_local_names;
extern uint32_t thug_script_loading_file;
extern ThugScriptJournalEntry thug_script_journal[500];
extern uint32_t thug_script_journal_count;
void thug_script_add_debug_name(uint32_t name, const char *text);
void thug_script_local_names_initialize(uint32_t debug_heap, const ThugMemory *);
void thug_script_local_names_clear(const ThugMemory *);
void thug_script_add_local_name(uint32_t name, const char *text, const ThugMemory *);
void thug_script_journal_created(ThugScriptSymbol *, const ThugMemory *);
void thug_script_journal_replaced(ThugScriptSymbol *, const ThugMemory *);
void thug_script_journal_undo(const ThugMemory *);
/* 472420 consumes an already loaded QB buffer. File I/O and script-runtime
 * initialization are separate. This is an unchecked internal grammar loader;
 * callers must provide terminating bytecode and enough allocator/table space. */
void thug_script_load_qb(const char *filename, const uint8_t *bytecode,
    uint32_t line_number_option, uint32_t local_names, uint32_t journal,
    const ThugMemory *);
#endif
