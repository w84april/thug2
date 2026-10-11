#include "load.h"
#include "tokens.h"
#include "../core/checksum.h"
#include <stddef.h>

uint8_t thug_script_debug_enabled;
ThugScriptDebugName *thug_script_debug_names;
char *thug_script_debug_cursor;
ThugScriptLocalName *thug_script_local_names;
uint32_t thug_script_loading_file;
ThugScriptJournalEntry thug_script_journal[500];
uint32_t thug_script_journal_count;
_Static_assert(sizeof(ThugScriptJournalEntry) == 8, "Original journal entry");

/* 0x0046cf60. Retain the first text for a checksum, even when later text
 * differs. The original duplicate tail-call compares strings via the Windows
 * CRT; its result is discarded by game callers and it changes no game state.
 * CRT locale/TLS bookkeeping is not part of this platform-independent map. */
void thug_script_add_debug_name(uint32_t name, const char *text) {
    if (!thug_script_debug_enabled) return;
    ThugScriptDebugName *entry = thug_script_debug_names + (name & 0xffff) * 10;
    while (entry->text) { if (entry->name == name) return; ++entry; }
    entry->name = name; entry->text = thug_script_debug_cursor;
    while (*text) *thug_script_debug_cursor++ = *text++;
    *thug_script_debug_cursor++ = 0;
}
/* 0x00470010. Only the low argument byte selects the debug heap. The caller
 * clears any previous table; this routine itself overwrites the global. */
void thug_script_local_names_initialize(uint32_t debug_heap, const ThugMemory *memory) {
    memory->temp_scope(memory->context, (uint8_t)debug_heap ? 3 : 1);
    thug_script_local_names = memory->allocate(memory->context, 4096 * 12, 0);
    memory->temp_scope(memory->context, 0);
    for (uint32_t i = 0; i < 4096; ++i) {
        thug_script_local_names[i].name = 0;
        thug_script_local_names[i].text = NULL;
        thug_script_local_names[i].next = NULL;
    }
}
/* 0x0046f9f0. Free collision nodes/text before the inline text of each bucket. */
void thug_script_local_names_clear(const ThugMemory *memory) {
    if (!thug_script_local_names) return;
    for (uint32_t i = 0; i < 4096; ++i) {
        ThugScriptLocalName *entry = thug_script_local_names[i].next;
        while (entry) {
            ThugScriptLocalName *next = entry->next;
            if (entry->text) memory->release(memory->context, entry->text);
            memory->release(memory->context, entry); entry = next;
        }
        if (thug_script_local_names[i].text)
            memory->release(memory->context, thug_script_local_names[i].text);
    }
    memory->release(memory->context, thug_script_local_names);
    thug_script_local_names = NULL;
}
/* 0x0046fa60. Duplicates are separate local entries. New collisions prepend
 * after the inline bucket, and are also offered to the global debug map. */
void thug_script_add_local_name(uint32_t name, const char *text, const ThugMemory *memory) {
    ThugScriptLocalName *bucket = thug_script_local_names + (name & 0xfff);
    ThugScriptLocalName *entry = bucket->text ? memory->allocate(memory->context, 12, 0) : bucket;
    entry->name = name;
    uint32_t size = 1; while (text[size - 1]) ++size;
    entry->text = memory->allocate(memory->context, size, 0);
    for (uint32_t i = 0; i < size; ++i) entry->text[i] = text[i];
    if (entry != bucket) { entry->next = bucket->next; bucket->next = entry; }
    else entry->next = NULL;
    thug_script_add_debug_name(name, text);
}
/* 0x004727b0 and 0x004727f0. Preserve each journal slot's three padding bytes. */
void thug_script_journal_created(ThugScriptSymbol *symbol, const ThugMemory *memory) {
    thug_script_journal[thug_script_journal_count].symbol = symbol;
    thug_script_journal[thug_script_journal_count].created = 1;
    ++thug_script_journal_count;
    if (symbol->type == 7 && thug_script_cache) thug_script_cache_reload(thug_script_cache, symbol->name, memory);
}
void thug_script_journal_replaced(ThugScriptSymbol *symbol, const ThugMemory *memory) {
    thug_script_journal[thug_script_journal_count].symbol = symbol;
    thug_script_journal[thug_script_journal_count].created = 0;
    ++thug_script_journal_count;
    if (symbol->type == 7 && thug_script_cache) thug_script_cache_reload(thug_script_cache, symbol->name, memory);
}
/* 0x00472830. Undo in forward order, not reverse. The original inspects the
 * entry's type/name after destruction, so release must retain those bytes until
 * the next allocation. Cache reload also requires a valid replacement symbol. */
void thug_script_journal_undo(const ThugMemory *memory) {
    for (uint32_t i = 0; (int32_t)i < (int32_t)thug_script_journal_count; ++i) {
        ThugScriptSymbol *symbol = thug_script_journal[i].symbol;
        if (thug_script_journal[i].created) thug_script_symbol_destroy(symbol, memory);
        else {
            thug_script_symbol_destroy(thug_script_symbol_find(symbol->name), memory);
            thug_script_symbol_insert(symbol);
        }
        symbol = thug_script_journal[i].symbol;
        if (symbol->type == 7 && thug_script_cache) thug_script_cache_reload(thug_script_cache, symbol->name, memory);
    }
    thug_script_journal_count = 0;
}
static void replace(ThugScriptSymbol *symbol, uint32_t journal, const ThugMemory *memory) {
    if (journal) { thug_script_journal_replaced(symbol, memory); thug_script_symbol_unlink(symbol); }
    else thug_script_symbol_destroy(symbol, memory);
}
/* 0x00472420. Two passes: readable names, then global definitions/scripts.
 * The line-number option reaches identical token traversal in this build.
 * Unknown top-level tokens intentionally make no progress, matching the
 * original internal contract rather than inventing malformed-input recovery. */
void thug_script_load_qb(const char *filename, const uint8_t *p,
    uint32_t line_number_option, uint32_t local_names, uint32_t journal, const ThugMemory *memory) {
    (void)line_number_option;
    thug_script_local_names_clear(memory);
    if (local_names) thug_script_local_names_initialize(0, memory);
    const uint8_t *scan = p;
    while (*scan) {
        if (*scan == 0x2b) {
            uint32_t name = thug_script_read_word(scan + 1); scan += 5;
            if (local_names) thug_script_add_local_name(name, (const char *)scan, memory);
            else thug_script_add_debug_name(name, (const char *)scan);
            while (*scan) ++scan;
            ++scan;
        } else scan = thug_script_next_token(scan);
    }
    thug_script_add_debug_name(thug_crc32_string(filename), filename);
    thug_script_loading_file = thug_crc32_string(filename);
    memory->temp_scope(memory->context, 1);
    for (;;) {
        p = thug_script_skip_lines(p);
        switch (*p) {
        case 0:
            memory->temp_scope(memory->context, 0); thug_script_loading_file = 0; return;
        case 0x16: {
            uint32_t name = thug_script_read_word(p + 1);
            p = thug_script_skip_lines(p + 5); p = thug_script_skip_lines(p + 1);
            ThugScriptSymbol *old = thug_script_symbol_find(name);
            if (old) replace(old, journal, memory);
            p = thug_script_register_value(p, name, filename, memory);
            if (!old && journal) thug_script_journal_created(thug_script_symbol_find(name), memory);
            break;
        }
        case 0x23: {
            uint32_t name = thug_script_read_word(p + 2);
            const uint8_t *body = p + 6;
            p = thug_script_skip_script(body);
            uint32_t checksum = thug_script_body_checksum(body);
            ThugScriptSymbol *old = thug_script_symbol_find(name);
            if (old && old->type == 7 && *(const uint32_t *)(uintptr_t)old->value == checksum) break;
            if (old) replace(old, journal, memory);
            ThugScriptSymbol *symbol = thug_script_register_script(body, (uintptr_t)p - (uintptr_t)body, name, checksum, filename, memory);
            if (!old && journal) thug_script_journal_created(symbol, memory);
            break;
        }
        case 0x2b: p = thug_script_next_token(p); break;
        case 0x45: {
            uint32_t name = thug_script_read_word(p + 2); p += 6;
            if (name == 0x0fa33d9b) { memory->temp_scope(memory->context, 0); memory->temp_scope(memory->context, 1); }
            else if (name == 0x70cb0238) {
                if (thug_script_debug_enabled) { memory->temp_scope(memory->context, 0); memory->temp_scope(memory->context, 3); }
                else while (*p != 0 && *p != 0x45) p = thug_script_next_token(p);
            }
            break;
        }
        default: break;
        }
    }
}
