/* Test-only configured native/virtual handlers. Deletion and nested delivery
 * call the actual recovered runtime through explicit imports. */
#include <stdint.h>
#define C ((uint32_t *)(uintptr_t)0x1830000)
#define WORD(at) (*(uint32_t *)(uintptr_t)(at))
extern void thug_script_delete_spawned(uint32_t,uint32_t,uint32_t);
extern void thug_script_events_deliver(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t thug_event_emit(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,float,uint32_t,uint32_t);
static void observe(uint32_t kind,uint32_t owner,uint32_t *parameters,uint32_t *script,uint32_t *event) {
    uint32_t *first=parameters?(uint32_t *)(uintptr_t)parameters[1]:0;
    uint32_t *log=C+32+C[0]++*24;
    log[0]=kind;log[1]=owner;log[2]=(uintptr_t)script;log[3]=(uintptr_t)parameters;
    log[4]=(uintptr_t)first;log[5]=first?first[1]:0;log[6]=first?first[2]:0;
    log[7]=script?script[50]:0;log[8]=script?script[41]:0;log[9]=script?script[12]:0;
    log[10]=script?((uint8_t *)script)[0xcc]:0;
    log[11]=WORD(C[8]+12);log[12]=WORD(C[9]+0x1c);
    for(unsigned i=0;i<5;++i)log[13+i]=event?event[i]:0;
    log[18]=owner&&kind==1?WORD(owner+0x18):0;
    log[19]=WORD(C[9]+0xb034);log[20]=WORD(C[9]+0x20+0xb00c);
    log[21]=WORD(C[9]+0x20+0x7000);log[22]=WORD(C[9]+0x20+0xb010);log[23]=C[1];
}
uint32_t fixture_delivery_native(uint32_t *parameters,uint32_t *script) {
    observe(0,0,parameters,script,0);
    uint32_t mode=C[2],arg=C[3],value=C[4];
    if(mode==1){script[41]=1;script[38]=value;}
    if(mode==2)((uint8_t *)(uintptr_t)arg)[9]=(uint8_t)value;
    if(mode==3)((uint8_t *)(uintptr_t)arg)[8]=(uint8_t)value;
    if(mode==4)WORD(arg)=value;
    if(mode==5){C[2]=0;thug_script_delete_spawned(arg,C[10],C[11]);}
    if(mode==6){C[2]=0;thug_script_events_deliver(arg,C[12],(uintptr_t)script,C[10],C[11]);}
    if(mode==7){C[2]=0;thug_event_emit(C[9],arg,value,C[5],C[6],C[7],-1,C[10],C[11]);}
    return C[1];
}
static void receive(uint32_t kind,uint32_t owner,uint32_t *event) {
    observe(kind,owner,0,0,event);
    uint32_t mode=C[13];
    if(mode==1)event[3]|=C[14];
    if(mode==2)event[2]=C[14];
    if(mode==3){WORD(owner+0x10)=C[14];C[13]=0;}
    if(mode==4){event[0]=C[14];event[1]=C[15];event[2]=C[16];event[4]=C[17];}
    if(mode==5){event[4]=C[14];event[3]|=4;}
    if(mode==6){C[13]=0;thug_event_emit(C[9],C[14],C[15],C[16],0,0,-1,C[10],C[11]);}
}
void fixture_delivery_receiver(uint32_t owner,uint32_t *event){receive(1,owner,event);}
void fixture_delivery_object(uint32_t owner,uint32_t *event){receive(2,owner,event);}
void fixture_delivery_print(uint32_t *context,const char *format,...) {
    uint32_t *record=context+1+context[0]++*2;record[0]=(uintptr_t)format;record[1]=0;
}
