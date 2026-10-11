/* Test-only command and object-activity boundaries. No gameplay handlers are
 * substituted in the recovered runtime itself. Context stores relocated global
 * addresses so the callback can observe scheduling and request deferred stops. */
#include <stdint.h>
#define C ((uint32_t *)(uintptr_t)0x1830000)
static uint32_t command(uint32_t kind,void *owner,uint32_t name,uint32_t *parameters,uint32_t *script) {
    uint32_t *log=C+32+C[0]++*16;
    uint32_t *first=parameters?(uint32_t *)(uintptr_t)parameters[1]:0;
    log[0]=kind;log[1]=(uintptr_t)owner;log[2]=name;log[3]=(uintptr_t)parameters;log[4]=(uintptr_t)script;
    log[5]=(uintptr_t)first;log[6]=first?first[1]:0;log[7]=first?first[2]:0;log[8]=script?script[3]:0;log[9]=script?script[50]:0;
    log[10]=script?((uint8_t *)script)[0xcc]:0;
    log[11]=*(uint8_t *)(uintptr_t)C[4];log[12]=*(uint8_t *)(uintptr_t)C[5];log[13]=*(uint8_t *)(uintptr_t)C[6];
    log[14]=*(uint32_t *)(uintptr_t)C[7];log[15]=*(uint32_t *)(uintptr_t)C[8];
    if(C[2]==1&&script){script[41]=1;script[38]=C[3];}
    if(C[2]==2&&script)script[3]=0;
    if(C[2]==3&&first)first[2]^=C[3];
    if(C[2]==4&&script)script[58]=C[3];
    if(C[2]==5&&script)script[3]=C[3];
    if(C[2]==6)*(uint8_t *)(uintptr_t)C[6]=1;
    if(C[2]==7&&script){
        uint32_t *added=(uint32_t *)(uintptr_t)C[3],*next=(uint32_t *)(uintptr_t)script[0];
        added[0]=(uintptr_t)next;added[1]=(uintptr_t)script;if(next)next[1]=(uintptr_t)added;script[0]=(uintptr_t)added;
        ++*(uint32_t *)(uintptr_t)C[9];C[2]=0;
    }
    if(C[2]==8)((uint8_t *)(uintptr_t)C[3])[0xcc]=(uint8_t)C[10];
    if(C[2]==9&&script){script[41]=11;script[38]=0;}
    if(C[2]==10&&kind==5){
        uint32_t *probe=(uint32_t *)(uintptr_t)C[12];probe[0x68/4]=C[13];probe[0x58/4]=C[14];
    }
    return C[1];
}
uint32_t fixture_schedule_native(uint32_t *p,uint32_t *s){return command(0,0,0,p,s);}
uint32_t fixture_schedule_object(void *o,uint32_t n,uint32_t *p,uint32_t *s){return command(1,o,n,p,s);}
uint32_t fixture_schedule_member(void *o,uint32_t n,uint32_t *p,uint32_t *s){return command(2,o,n,p,s);}
uint32_t fixture_schedule_component(void *o,uint32_t n,uint32_t *p,uint32_t *s){return command(3,o,n,p,s);}
uint32_t fixture_schedule_active(void *o){return command(4,o,0,0,0);}
uint32_t fixture_schedule_nodes(void *o){command(5,o,0,0,0);return C[11];}
