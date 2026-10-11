#ifndef THUG_CORE_RANDOM_H
#define THUG_CORE_RANDOM_H
#include <stdint.h>
typedef struct { uint32_t increment, multiplier, value; } ThugRandomState;
/* Original blocks 690fd4 and 690fc8. Initialization/seeding is separate work. */
extern ThugRandomState thug_random_state, thug_random_alternate_state;
/* Single browser-thread replacement for CRT TLS access at 629be5. Startup
 * seed 1 is supplied by the port; Windows TLS allocation is not recovered. */
extern uint32_t thug_crt_random_state;
uint32_t thug_crt_random(void);
int32_t thug_random_range(uint32_t limit);
int32_t thug_random_alternate_range(uint32_t limit);
#endif
