/* Comparison-only file port: original Letter S texture bytes are resident before
 * startup. This implements actual byte reads, not an asset/command success stub. */
#include <stdint.h>
static uint32_t word(uint32_t at){uint32_t v;__builtin_memcpy(&v,(void *)(uintptr_t)at,4);return v;}
static void log_io(uint32_t *c,uint32_t op,uint32_t a,uint32_t b,uint32_t d){
    if(c[3]>=8)__builtin_trap();uint32_t *r=(void *)(uintptr_t)(c[4]+c[3]++*32);
    r[0]=op;r[1]=a;r[2]=b;r[3]=d;r[4]=c[2];r[5]=c[1];r[6]=word(c[5]+8);r[7]=c[0];
}
void *fixture_training_open(uint32_t *c,const char *name,uint32_t sync,uint32_t priority){
    const char wanted[]="models\\gameobjects\\skate\\letter_s\\letter_s.tex.Xbx";
    for(unsigned i=0;i<sizeof(wanted);i++)if(name[i]!=wanted[i])__builtin_trap();
    log_io(c,1,sync,priority,0);return (void *)(uintptr_t)c[2];
}
uint32_t fixture_training_size(uint32_t *c,void *file){log_io(c,2,(uintptr_t)file,0,0);return c[1];}
uint32_t fixture_training_read(uint32_t *c,void *file,void *buffer,uint32_t width,uint32_t count){
    if((uintptr_t)file!=c[2]||width!=1||count!=c[1])__builtin_trap();
    log_io(c,3,(uintptr_t)buffer,width,count);
    for(uint32_t i=0;i<count;i++)((uint8_t *)buffer)[i]=((const uint8_t *)(uintptr_t)c[0])[i];return count;
}
uint8_t fixture_training_close(uint32_t *c,void *file){log_io(c,4,(uintptr_t)file,0,0);return 1;}
