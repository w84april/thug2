/* Test-only dispatch observation. These callbacks are not recovered game code. */
#include <stdint.h>
#define LOG ((uint32_t *)(uintptr_t)0x16dc900)
static uint32_t record(uint32_t self,uint32_t name,uint32_t parameters,uint32_t script){
    uint32_t *row=LOG+8+LOG[0]++*4;row[0]=self;row[1]=name;row[2]=parameters;row[3]=script;return LOG[1];
}
uint32_t fixture_component_checksum(uint32_t self,uint32_t name,uint32_t parameters,uint32_t script){return record(self,name,parameters,script);}
uint32_t fixture_component_member(uint32_t self,uint32_t parameters,uint32_t script){return record(self,0,parameters,script);}
