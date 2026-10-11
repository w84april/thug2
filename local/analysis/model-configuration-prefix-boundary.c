/* Test-only loader breakpoint, no result supplied. */
#include <stdint.h>
void fixture_model_load(void *component,void *parameters,void *renderer,const char *path,
 unsigned key,unsigned assets,unsigned option,unsigned flag,unsigned skin,unsigned route,unsigned loaded){
 volatile uint32_t *p=(void *)0x19f0000;p[0]=0x4935e0;p[1]=(uintptr_t)parameters;p[2]=(uintptr_t)component;p[3]=1;
 p[4]=(uintptr_t)renderer;p[5]=key;p[6]=assets&255;p[7]=option;p[8]=flag&255;p[9]=skin;p[10]=route&255;p[11]=loaded&255;
 unsigned n=0;volatile char *out=(void *)0x19f0040;do{out[n]=path[n];}while(path[n++]);p[12]=n-1;
 __builtin_trap();
}
