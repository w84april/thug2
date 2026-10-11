#ifndef THUG_GAME_ASSETS_H
#define THUG_GAME_ASSETS_H
#include "../core/lookup.h"
#include "../platform/diagnostics.h"
typedef struct ThugAsyncFile ThugAsyncFile;
typedef void (*ThugAsyncCompletionCallback)(ThugAsyncFile *, uint32_t, uint32_t, void *, uint32_t);
struct ThugAsyncFile {
    const void *methods;
    uint32_t result;
    ThugAsyncCompletionCallback callback;
    void *context;
    uint32_t argument, flags, active, unknown_1c;
    uint8_t unknown_20[0x18];
    uint32_t pending;
};
typedef struct { ThugAsyncFile *file; uint32_t operation, result; } ThugAsyncCompletion;
extern ThugAsyncCompletion thug_async_completions[2][16];
extern ThugAsyncFile *thug_async_files[16];
extern uint32_t thug_async_pending, thug_async_completion_counts[2], thug_async_write_buffer;
extern volatile uint8_t thug_async_completed;
void thug_async_swap_completions(void);
void thug_async_process_completions(void);
/* Like the original, this waits for an external I/O producer. A browser host
 * must arrange completion before calling synchronous engine paths. */
void thug_async_wait(uint32_t all_files, const ThugDiagnostics *);

typedef struct ThugAsset ThugAsset;
typedef struct {
    uint32_t unavailable_0;
    void *(*data)(const ThugAsset *);
    uint32_t unavailable_8[6];
    uint8_t (*ready)(const ThugAsset *);
    uint32_t unavailable_24[8];
    uint8_t (*read_finished)(ThugAsset *);
    uint32_t unavailable_48[4];
} ThugAssetMethods;
struct ThugAsset {
    const ThugAssetMethods *methods;
    uint32_t unknown_4, state, unknown_c;
    void *data;
    uint32_t unknown_14, unknown_18, unknown_1c;
    ThugAsyncFile *file;
    void *buffer;
    uint32_t size, unknown_2c, unknown_30, unknown_34;
    const uint32_t *link_methods;
    uint32_t link_id, link_value;
    void *previous, *next;
    uint32_t animation_name;
};
typedef struct { uint8_t unknown_0[0x1c]; ThugObjectLookupTable *table; } ThugAssetManager;
extern ThugAssetManager *thug_asset_manager;
/* Only the methods called by the recovered asset/controller paths are wired.
 * Loading, parsing, updating and destruction are still unavailable. */
extern const ThugAssetMethods thug_asset_base_methods, thug_animation_asset_methods;
extern const uint32_t thug_asset_link_methods[1];
ThugAsset *thug_asset_initialize(ThugAsset *);
ThugAsset *thug_animation_asset_initialize(ThugAsset *);
void *thug_asset_data(const ThugAsset *);
uint8_t thug_asset_ready(const ThugAsset *);
uint8_t thug_asset_read_finished(ThugAsset *);
uint8_t thug_asset_mark_ready(ThugAsset *);
void thug_asset_read_callback(ThugAsyncFile *, uint32_t operation, uint32_t result, void *asset, uint32_t argument);
void *thug_asset_find(ThugAssetManager *, uint32_t key, uint32_t required, const ThugDiagnostics *);
void *thug_animation_find(uint32_t key, uint32_t required, const ThugDiagnostics *);
typedef struct ThugAnimationReader ThugAnimationReader;
typedef struct {
    ThugAnimationReader *(*dispose)(ThugAnimationReader *,uint32_t,const ThugMemory *);
    uint32_t unavailable_4[5];
} ThugAnimationReaderMethods;
struct ThugAnimationReader {
    const ThugAnimationReaderMethods *methods;
    uint32_t name;
    uint8_t unknown_8[0x200], mode, unknown_209[0xb];
};
extern const ThugAnimationReaderMethods thug_animation_reader_methods;
extern uint32_t thug_animation_reader_pool_index;
extern ThugFixedPool *thug_animation_reader_pools[2];
ThugAnimationReader *thug_animation_reader_initialize(ThugAnimationReader *);
ThugAnimationReader *thug_animation_reader_allocate(const ThugMemory *);
ThugAnimationReader *thug_create_animation_reader(const ThugMemory *);
void *thug_animation_reader_set_mode(ThugAnimationReader *, uint32_t mode, const ThugDiagnostics *);
void *thug_animation_reader_select(ThugAnimationReader *, uint32_t name, const ThugDiagnostics *);
void thug_animation_reader_free(ThugAnimationReader *,const ThugMemory *);
ThugAnimationReader *thug_animation_reader_delete(ThugAnimationReader *,uint32_t flags,const ThugMemory *);
void thug_animation_reader_release(ThugAnimationReader *,const ThugMemory *);
void thug_release_animation_reader(ThugAnimationReader *,const ThugMemory *);
#endif
