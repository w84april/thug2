#include "../../src/core/memory.h"
#include "../../src/core/sort.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* 004b7af0: unsigned upper-half, then lower-half order is unsigned word order. */
int32_t thug_model_companion_compare_draft(const void *a,const void *b){
    uint32_t x=word(a,4),y=word(b,4);return x>y?1:x<y?-1:0;
}
/* 004b7c60. Complete resident companion data and successful initialized heap
 * are the original internal contract. Zero count retains the old array. */
uint32_t thug_model_companion_parse_draft(void *model,const uint8_t **input,const ThugMemory *m){
    const uint8_t *p=*input;uint32_t version=word(p,0);p+=4;
    if(version>=2){put(model,0xb0,word(p,0));p+=4;}
    uint32_t count=word(p,0);p+=4;put(model,0xc0,count);
    if(count){
        put(model,0xbc,(uintptr_t)m->allocate(m->context,count*16,1));
        for(uint32_t i=0;i<word(model,0xc0);i++){
            void *record=(uint8_t *)pointer(model,0xbc)+i*16;
            put(record,0,word(p,0));put(record,4,word(p,4));put(record,8,word(p,8));p+=12;
            put(pointer(model,0xbc),i*16+12,0);
        }
        thug_crt_qsort(pointer(model,0xbc),word(model,0xc0),16,thug_model_companion_compare_draft);
    }
    *input=p;return word(model,0xc0)!=0;
}
/* 004b7eb0. The cursor is local and a NULL companion leaves the model alone. */
void thug_model_companion_load_draft(void *model,const uint8_t *data,const ThugMemory *m){
    if(data)thug_model_companion_parse_draft(model,&data,m);
}
