/* Comparison-only alternate scene virtual; no game behavior is replaced. */
#include "texture-buffer-ports.c"
void *fixture_alternate_sector(void *scene,void *memory){
 (void)memory;uint32_t s=(uintptr_t)scene;put(s+0x84,word(s+0x84)+1);return (void *)(uintptr_t)word(s+0x80);
}
