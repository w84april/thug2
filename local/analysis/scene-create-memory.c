/* Comparison-only allocator failure, never a recovered game routine. */
#include "texture-buffer-ports.c"
void *fixture_scene_allocate(uint32_t *context,uint32_t size,uint32_t route){
    if(context[8]){context[8]=0;record(context,1,size,route,0);return 0;}
    return fixture_texture_allocate(context,size,route);
}
