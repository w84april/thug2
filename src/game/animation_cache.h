#ifndef THUG_GAME_ANIMATION_CACHE_H
#define THUG_GAME_ANIMATION_CACHE_H
#include "../core/memory.h"
#include "../core/memory_state.h"
struct ThugAnimationEvent;
typedef struct ThugAnimationCacheBlock ThugAnimationCacheBlock;
typedef struct {
    float duration;
    uint32_t flags,bone_count;
    const uint8_t *rotation_table,*rotation_keys,*translation_keys;
    const uint8_t *bone_keys,*bone_map,*bone_mask;
    ThugAnimationCacheBlock *cache;
    struct ThugAnimationEvent **events;
    const uint16_t *rotation_lengths,*translation_lengths;
    int16_t rotation_count,translation_count;
    int16_t event_count;
    uint16_t references;
} ThugKeyframeAnimation;
typedef struct {
    uint32_t first[60],second[60];
    uint16_t flags,padding;
} ThugAnimationCacheReader;
struct ThugAnimationCacheBlock {
    ThugKeyframeAnimation *animation;
    uint32_t timestamp,format;
    uint8_t *storage;
    uint32_t allocated,payload;
    uint8_t *rotations,*translations;
    void (*cleanup)(void *);
    void *context;
    ThugAnimationCacheReader *readers[18];
    uint8_t rotation_stride,translation_stride;
    uint16_t rotation_offsets[60],translation_offsets[60],bone_count,flags;
    uint16_t padding;
};
typedef struct {
    ThugAnimationCacheBlock *blocks[50];
    uint32_t count,bytes,alignment,format,unknown_d8;
    uint8_t evict_on_unpin,padding[3];
} ThugAnimationCacheManager;
extern ThugAnimationCacheManager *thug_animation_cache_manager;
extern uint32_t thug_animation_cache_pool_index;
extern ThugFixedPool *thug_animation_cache_pools[2];
extern uint16_t thug_animation_rotation_table[256][4],thug_animation_translation_table[256][4];
extern uint32_t thug_animation_tick_counter[2],thug_animation_cache_tick[2],thug_animation_cache_build_count;
uint64_t thug_animation_tick(void);
const uint8_t *thug_animation_decode_rotation(const uint8_t *,void *,uint32_t,const uint8_t *);
const uint8_t *thug_animation_decode_translation(const uint8_t *,void *,uint32_t);
void thug_animation_expand_rotation(void *,const void *);
void thug_animation_expand_quaternion(void *,const void *);
ThugAnimationCacheManager *thug_animation_cache_instance(void);
uint32_t thug_animation_cache_format(const ThugAnimationCacheManager *);
uint8_t thug_animation_cache_rotation_stride(const ThugAnimationCacheBlock *);
uint8_t thug_animation_cache_translation_stride(const ThugAnimationCacheBlock *);
uint8_t *thug_animation_cache_rotations(const ThugAnimationCacheBlock *,uint32_t);
uint8_t *thug_animation_cache_translations(const ThugAnimationCacheBlock *,uint32_t);
uint16_t *thug_animation_cache_rotation_offsets(ThugAnimationCacheBlock *);
uint16_t *thug_animation_cache_translation_offsets(ThugAnimationCacheBlock *);
void thug_animation_cache_set_cleanup(ThugAnimationCacheBlock *,void (*)(void *),void *);
uint32_t thug_animation_cache_allocation_size(const ThugAnimationCacheManager *,uint32_t,uint32_t,uint32_t,uint32_t);
void thug_animation_cache_reader_free(ThugAnimationCacheReader *,const ThugMemory *);
uint32_t thug_animation_cache_clear(ThugAnimationCacheBlock *,const ThugMemory *);
uint32_t thug_animation_cache_pin_block(ThugAnimationCacheBlock *,const ThugMemory *);
void thug_animation_cache_unpin_block(ThugAnimationCacheBlock *,int32_t,const ThugMemory *);
void thug_animation_cache_remove(ThugAnimationCacheManager *,ThugKeyframeAnimation *,const ThugMemory *);
void thug_animation_cache_flush(ThugAnimationCacheManager *,uint32_t,const ThugMemory *);
uint32_t thug_animation_cache_pin(ThugAnimationCacheManager *,ThugKeyframeAnimation *,const ThugMemory *);
void thug_animation_cache_unpin(ThugAnimationCacheManager *,ThugKeyframeAnimation *,int32_t,const ThugMemory *);
uint32_t thug_animation_cache_available(ThugAnimationCacheManager *,const ThugMemory *);
uint32_t thug_animation_cache_allocate(ThugAnimationCacheBlock *,ThugKeyframeAnimation *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
ThugAnimationCacheBlock *thug_animation_cache_add(ThugAnimationCacheManager *,ThugKeyframeAnimation *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
ThugKeyframeAnimation *thug_animation_cache_oldest(ThugAnimationCacheManager *,uint32_t,uint32_t *);
uint8_t thug_animation_cache_evict(ThugAnimationCacheManager *,uint32_t,uint32_t,const ThugMemory *);
uint32_t thug_keyframe_animation_pin(ThugKeyframeAnimation *,const ThugMemory *);
void thug_keyframe_animation_unpin(ThugKeyframeAnimation *,int32_t,const ThugMemory *);
void thug_keyframe_animation_cache_cleared(void *);
void thug_keyframe_animation_build_cache(ThugKeyframeAnimation *,uint32_t,const ThugMemory *);
void thug_animation_cache_initialize(ThugAnimationCacheManager *,uint32_t,uint32_t,const ThugMemory *);
ThugKeyframeAnimation *thug_keyframe_animation_initialize(ThugKeyframeAnimation *);
void thug_keyframe_animation_destroy(ThugKeyframeAnimation *,const ThugMemory *);
uint8_t thug_keyframe_animation_parse_compressed(ThugKeyframeAnimation *,const void *,const ThugMemory *);
uint8_t thug_keyframe_animation_parse_fixed(ThugKeyframeAnimation *,const void *,const ThugMemory *);
uint8_t thug_keyframe_animation_load_buffer(ThugKeyframeAnimation *,const void *,uint32_t,uint32_t,const ThugMemory *);
#endif
