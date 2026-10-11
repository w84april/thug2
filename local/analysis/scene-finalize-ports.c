#include "vertex-upload-ports.c"
uint32_t fixture_shared_add_ref(uint32_t device){uint32_t *log=event(4);log[1]=device;log[2]=word(device+4);put(device+4,word(device+4)+1);log[3]=word(device+4);return log[3];}
