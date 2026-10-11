/* Test-only virtual dispatch witness. This observes the command ABI and live
 * links; it is never bound to a game component in scene construction. */
#include <stdint.h>
static uint32_t *const c=(void *)0x19e0000,*const log=(void *)0x19e1000;
static uint32_t observe(uint32_t kind,void *p,uint32_t name,void *s,void *script){
 uint32_t i=c[0]++,*o=log+i*5;o[0]=kind;o[1]=(uintptr_t)p;o[2]=name;o[3]=(uintptr_t)s;o[4]=(uintptr_t)script;
 uint32_t result=c[32+i];
 if(c[1]==kind&&c[2]==i){if(c[3])*(uint32_t *)(uintptr_t)c[3]=c[4];if(c[5])*(uint32_t *)(uintptr_t)c[5]=c[6];}
 return result;
}
uint32_t fixture_prop_checksum(void *p,uint32_t n,void *s,void *script){return observe(1,p,n,s,script);}
uint32_t fixture_prop_member(void *p,void *s,void *script){return observe(2,p,0,s,script);}
