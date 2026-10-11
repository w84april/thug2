#ifndef THUG_GAME_COMPONENT_REGISTRATION_H
#define THUG_GAME_COMPONENT_REGISTRATION_H
#include <stdint.h>
typedef void (*ThugRegistrationInitialize)(void);
void thug_component_register_factory(void *,uint32_t,uint32_t,ThugRegistrationInitialize);
#endif
