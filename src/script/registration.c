#include "registration.h"
/* 0046f060. The first argument is unused. Each nonzero leading name creates a
 * fresh symbol, including duplicates; stride and descriptor storage are borrowed.
 * Store the descriptor before tagging the symbol, then reload the next name. */
void thug_script_register_commands(uint32_t unused,const void *descriptors,
    uint32_t stride,const ThugMemory *memory) {
    (void)unused;
    const uint8_t *entry=descriptors;
    uint32_t name;__builtin_memcpy(&name,entry,4);
    while(name){
        ThugScriptSymbol *symbol=thug_script_symbol_create(name,memory);
        symbol->value=(uintptr_t)entry;
        entry+=stride;
        symbol->type=9;
        __builtin_memcpy(&name,entry,4);
    }
}
