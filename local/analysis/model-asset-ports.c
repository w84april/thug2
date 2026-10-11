/* Comparison-only file/cache boundaries and an instrumented parse virtual. */
#include <stdint.h>
static uint32_t word(uint32_t a){return *(uint32_t *)(uintptr_t)a;}
static void log_event(uint32_t *c,uint32_t op,uint32_t a,uint32_t b,uint32_t d,const char *name){
 if(c[3]>=32)__builtin_trap();uint32_t *r=(void *)(uintptr_t)(c[4]+c[3]++*544);
 r[0]=op;r[1]=a;r[2]=b;r[3]=d;r[4]=word(c[5]+8);r[5]=c[9];r[6]=c[0];r[7]=c[1];
 char *s=(void *)(r+8);unsigned i=0;if(name){while(name[i]){if(i>=511)__builtin_trap();s[i]=name[i];i++;}}while(i<512)s[i++]=0;
}
static unsigned companion(const char *s){unsigned n=0;while(s[n])n++;return n>=8&&s[n-8]=='.'&&s[n-7]=='c'&&s[n-6]=='a'&&s[n-5]=='s';}
void *fixture_model_open(uint32_t *c,const char *s,uint32_t sync,uint32_t priority){unsigned second=companion(s);log_event(c,1,sync,priority,second,s);return (void *)(uintptr_t)((c[9]&(1u<<second))?0:c[second?8:2]);}
uint32_t fixture_model_size(uint32_t *c,void *f){unsigned second=(uintptr_t)f==c[8];if(!second&&(uintptr_t)f!=c[2])__builtin_trap();log_event(c,2,(uintptr_t)f,0,0,0);return c[second?7:1];}
uint32_t fixture_model_read(uint32_t *c,void *f,void *b,uint32_t width,uint32_t n){unsigned second=(uintptr_t)f==c[8];if((!second&&(uintptr_t)f!=c[2])||width!=1||n!=c[second?7:1])__builtin_trap();log_event(c,3,(uintptr_t)b,(uintptr_t)f,n,0);const uint8_t *d=(void *)(uintptr_t)c[second?6:0];for(unsigned i=0;i<n;i++)((uint8_t *)b)[i]=d[i];return n;}
uint8_t fixture_model_close(uint32_t *c,void *f){log_event(c,4,(uintptr_t)f,0,0,0);return 1;}
void *fixture_model_acquire(uint32_t *c,const char *name,unsigned a,unsigned b,unsigned d,unsigned e){if(a||b||d||e)__builtin_trap();log_event(c,5,0,0,0,name);return (void *)(uintptr_t)c[0];}
uint32_t fixture_model_cached_size(uint32_t *c,const char *name){log_event(c,6,0,0,0,name);return c[1];}
void fixture_model_cached_release(uint32_t *c,unsigned key){log_event(c,7,key,0,0,0);}
void fixture_model_parse(void *asset,const void *data,unsigned size,void *memory){(void)memory;uint32_t *p=(void *)0x1824000;p[0]++;p[1]=(uintptr_t)asset;p[2]=(uintptr_t)data;p[3]=size;p[4]=word((uintptr_t)asset+8);p[5]=word((uintptr_t)asset+0x5c);}
