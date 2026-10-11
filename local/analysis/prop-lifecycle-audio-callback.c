/* Platform stop-call witness. It records the original call and may apply an
 * explicit fixture mutation; it does not supply sound playback/game logic. */
#include <stdint.h>
uint32_t fixture_prop_audio_stop(void *buffer){
    uint32_t *control=(void *)0x19b0000,*log=(void *)0x19b1000,n=log[0]++;
    uint32_t *row=log+8+n*4;row[0]=(uintptr_t)buffer;
    row[1]=control[0]?*(uint32_t *)(uintptr_t)control[0]:0;
    row[2]=control[1]?*(uint32_t *)(uintptr_t)control[1]:0;row[3]=0;
    if(control[2])*(uint32_t *)(uintptr_t)control[2]=control[3];
    if(control[4])*(uint32_t *)(uintptr_t)control[4]=control[5];
    return control[6];
}
