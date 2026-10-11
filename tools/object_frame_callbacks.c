/* Test instrumentation for virtual call ordering/mutations, not game code. */
#include <stdint.h>
static uint32_t word(uint32_t p) {uint32_t v;__builtin_memcpy(&v,(const void *)(uintptr_t)p,4);return v;}
static void put(uint32_t p,uint32_t v) {__builtin_memcpy((void *)(uintptr_t)p,&v,4);}
void fixture_object_step(uint32_t self,uint32_t query,uint32_t diagnostics,uint32_t memory) {
    (void)query;(void)diagnostics;(void)memory;
    uint32_t context=word(self+0x1c),log=word(context),owner=word(context+4),n=word(log);
    put(log,n+1);uint32_t row=log+4+n*28;
    put(row,self);put(row+4,word(owner+8));put(row+8,word(owner+0x104));
    put(row+12,word(owner+0x100));put(row+16,word(self+8));put(row+20,word(owner+0x58));put(row+24,word(context+0x14));
    uint32_t target=word(context+8);
    if(target){uint32_t value=word(context+12);if(word(context+16)==1)*(uint8_t *)(uintptr_t)target=(uint8_t)value;else put(target,value);}
}
