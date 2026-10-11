/* Test-only DirectInput COM observation, not a browser haptics implementation. */
#include <stdint.h>
static uint32_t record(uint32_t *effect,uint32_t kind,const uint32_t *parameters,uint32_t flags){
    uint32_t *context=(void *)(uintptr_t)effect[1];
    uint32_t *row=context+4+24*context[0]++;
    for(unsigned i=0;i<24;i++)row[i]=0;
    row[0]=kind;row[1]=(uintptr_t)effect;row[2]=flags;
    if(parameters){
        for(unsigned i=0;i<14;i++)row[3+i]=(i==9||i==12)?0:parameters[i];
        const uint32_t *direction=(void *)(uintptr_t)parameters[9];
        row[17]=direction[0];row[18]=direction[1];
        row[19]=*(const uint32_t *)(uintptr_t)parameters[12];
    }
    return 0x80004005;
}
uint32_t fixture_input_effect_stop(uint32_t *effect){return record(effect,1,0,0);}
uint32_t fixture_input_effect_set(uint32_t *effect,const uint32_t *parameters,uint32_t flags){return record(effect,2,parameters,flags);}
