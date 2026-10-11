#include <stdint.h>
void fixture_configure(void *component,void *parameters){volatile uint32_t *p=(void *)0x19f0000;p[0]=0x420d10;p[1]=(uintptr_t)parameters;p[2]=(uintptr_t)component;p[3]=1;__builtin_trap();}
