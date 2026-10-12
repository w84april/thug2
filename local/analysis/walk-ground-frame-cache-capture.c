/* Test-only observation at the cache lifetime boundary. Disabled by default.
 * The real destructor always executes. This does not implement game behavior. */
#include "../../src/collision/scene.h"
uint32_t thug_walk_cache_capture_enabled,thug_walk_cache_capture_count;
uint32_t thug_walk_cache_capture_rows[16][1014];
void __real_thug_collision_cache_destroy(ThugCollisionCache *);
void __wrap_thug_collision_cache_destroy(ThugCollisionCache *cache){
 if(thug_walk_cache_capture_enabled){
  uint32_t n=thug_walk_cache_capture_count++;if(n>=16)__builtin_trap();
  uint32_t *row=thug_walk_cache_capture_rows[n];row[0]=(uintptr_t)cache;row[1]=thug_collision_cache_mask;row[2]=UINT32_MAX;
  for(unsigned i=0;i<8;i++)if((row[1]&(1u<<i))&&thug_collision_cache_registry[i]==cache){row[2]=i;break;}
  __builtin_memcpy(row+3,cache,sizeof *cache);
 }
 __real_thug_collision_cache_destroy(cache);
}
