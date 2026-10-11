/* Test-only: terminal debug print, with no format arguments here. */
#include <stdint.h>
void fixture_wall_contact_print(uint32_t *context,const char *format,...) {
 uint32_t *record=(uint32_t *)(uintptr_t)(context[3]+context[2]++*48);
 record[0]=4;record[1]=(uintptr_t)format;record[2]=record[3]=0;
 for(unsigned i=4;i<9;++i)record[i]=0;
 record[9]=context[6];record[10]=context[6]?*(uint32_t *)(uintptr_t)context[6]:0;record[11]=0;
}
