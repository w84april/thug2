#include "assets.h"
#include <stddef.h>
_Static_assert(offsetof(ThugAsyncFile, pending)==0x38,"Async pending operations");
_Static_assert(offsetof(ThugAssetMethods, ready)==0x20,"Asset ready virtual");
_Static_assert(offsetof(ThugAssetMethods, read_finished)==0x44,"Asset completion virtual");
_Static_assert(sizeof(ThugAsset)==0x50,"Animation asset allocation");
_Static_assert(sizeof(ThugAnimationReader)==0x214,"Animation reader allocation");
ThugAsyncCompletion thug_async_completions[2][16];
ThugAsyncFile *thug_async_files[16];
uint32_t thug_async_pending, thug_async_completion_counts[2], thug_async_write_buffer;
volatile uint8_t thug_async_completed;
ThugAssetManager *thug_asset_manager;
uint32_t thug_animation_reader_pool_index;
ThugFixedPool *thug_animation_reader_pools[2];
const uint32_t thug_asset_link_methods[1];
const ThugAnimationReaderMethods thug_animation_reader_methods={.dispose=thug_animation_reader_delete};
const ThugAssetMethods thug_asset_base_methods = {
    .data=thug_asset_data,.ready=thug_asset_ready,.read_finished=thug_asset_read_finished
};
const ThugAssetMethods thug_animation_asset_methods = {
    .data=thug_asset_data,.ready=thug_asset_ready,.read_finished=thug_asset_read_finished
};
/* 0x005b9770. The completed buffer is the one just switched away from. */
void thug_async_swap_completions(void) { thug_async_write_buffer ^= 1; thug_async_completed = 0; }
/* 0x005b68c0. Capture the batch size, but read each record and file state at
 * dispatch time. Completion callbacks can change later records or counters. */
void thug_async_process_completions(void) {
    thug_async_swap_completions();
    uint32_t index = thug_async_write_buffer ^ 1;
    int32_t count = (int32_t)thug_async_completion_counts[index];
    for (int32_t i=0;i<count;++i) {
        ThugAsyncCompletion *record = &thug_async_completions[index][i];
        ThugAsyncFile *file = record->file;
        file->callback(file,record->operation,record->result,file->context,file->argument);
        --thug_async_pending;
        if (!--file->pending) file->active = 0;
    }
    thug_async_completion_counts[index] = 0;
}
/* 0x005b6a50. The original completion flag is supplied by the I/O producer;
 * pumping callbacks does not itself imply that an asset is parsed and ready. */
void thug_async_wait(uint32_t all_files, const ThugDiagnostics *diagnostics) {
    for (;;) {
        if (diagnostics && diagnostics->print) diagnostics->print(diagnostics->context,
            "CAsyncFileLoader waiting for io completion: busy count %d completion %d\n",
            thug_async_pending,(uint32_t)thug_async_completed);
        while (!thug_async_completed) {}
        if (diagnostics && diagnostics->print) diagnostics->print(diagnostics->context,
            "CAsyncFileLoader got completion: busy count %d completion %d\n",
            thug_async_pending,(uint32_t)thug_async_completed);
        thug_async_process_completions();
        if (!(uint8_t)all_files) return;
        uint32_t i=0;
        while (i<16 && (int32_t)thug_async_files[i]->pending<=0) ++i;
        if (i==16) return;
        if (diagnostics && diagnostics->print) diagnostics->print(diagnostics->context,
            "CAsyncFileLoader still needs to wait for file handle %d\n",i);
    }
}
/* 0x00407910 and 0x004071a0. Unwritten bytes retain their incoming values. */
ThugAsset *thug_asset_initialize(ThugAsset *asset) {
    asset->methods=&thug_asset_base_methods;
    asset->link_id=UINT32_MAX; asset->link_value=0;
    asset->previous=asset->next=&asset->link_methods;
    asset->link_methods=thug_asset_link_methods;
    asset->unknown_34=asset->state=asset->size=asset->unknown_14=0;
    asset->file=NULL; asset->buffer=NULL;
    return asset;
}
ThugAsset *thug_animation_asset_initialize(ThugAsset *asset) {
    thug_asset_initialize(asset); asset->methods=&thug_animation_asset_methods;
    asset->animation_name=0; return asset;
}
/* 0x00590250, 0x00407610, 0x00407680 and 0x004076a0. */
void *thug_asset_data(const ThugAsset *asset) { return asset->data; }
uint8_t thug_asset_ready(const ThugAsset *asset) { return asset->state==4; }
uint8_t thug_asset_read_finished(ThugAsset *asset) { asset->state=2; return 1; }
uint8_t thug_asset_mark_ready(ThugAsset *asset) { asset->state=4; return 1; }
/* 0x00407710. This is the actual file callback registered by the animation
 * loader. It marks reading finished (state 2), not asset readiness (state 4). */
void thug_asset_read_callback(ThugAsyncFile *file, uint32_t operation, uint32_t result, void *context, uint32_t argument) {
    (void)file; (void)operation;
    if (!argument) {
        ThugAsset *asset=context; asset->size=result;
        asset->methods->read_finished(asset);
    }
}
/* 0x00407c00. Match the inline lookup, including null-value collisions. */
void *thug_asset_find(ThugAssetManager *manager, uint32_t key, uint32_t required, const ThugDiagnostics *diagnostics) {
    (void)required;
    ThugObjectLookupTable *table=manager->table;
    uint32_t bucket=key & ((UINT32_C(1)<<(table->shift&31))-1);
    ThugObjectLookupNode *node=(ThugObjectLookupNode *)((uintptr_t)table->buckets+bucket*12);
    while (node && (node->key!=key || !node->value)) node=node->next;
    ThugAsset *asset=node ? node->value : NULL;
    if (!asset) return NULL;
    while (!asset->methods->ready(asset)) thug_async_wait(0,diagnostics);
    return asset->methods->data(asset);
}
/* 0x0048cf50. Zero names deliberately bypass the global manager. */
void *thug_animation_find(uint32_t key, uint32_t required, const ThugDiagnostics *diagnostics) {
    return key ? thug_asset_find(thug_asset_manager,key,required,diagnostics) : NULL;
}
/* 0x0048cf70. The original clears exactly 131 words after the key. */
ThugAnimationReader *thug_animation_reader_initialize(ThugAnimationReader *reader) {
    reader->methods=&thug_animation_reader_methods;
    __builtin_memset((uint8_t *)reader+8,0,0x20c); reader->name=0;
    return reader;
}
/* 0x004b3990 and forwarding entry 0x0048bfc0. */
ThugAnimationReader *thug_animation_reader_allocate(const ThugMemory *memory) {
    ThugFixedPool *pool=thug_animation_reader_pools[thug_animation_reader_pool_index];
    ThugAnimationReader *reader=pool ? thug_pool_allocate(pool) : memory->allocate(memory->context,0x214,1);
    return reader ? thug_animation_reader_initialize(reader) : NULL;
}
ThugAnimationReader *thug_create_animation_reader(const ThugMemory *memory) { return thug_animation_reader_allocate(memory); }
/* 0x0048cfa0 and 0x0048cfd0. Retain both lookups in selection. */
void *thug_animation_reader_set_mode(ThugAnimationReader *reader, uint32_t mode, const ThugDiagnostics *diagnostics) {
    reader->mode=(uint8_t)mode;
    return reader->mode ? NULL : thug_animation_find(reader->name,1,diagnostics);
}
void *thug_animation_reader_select(ThugAnimationReader *reader, uint32_t name, const ThugDiagnostics *diagnostics) {
    reader->name=name; reader->mode=0;
    thug_animation_find(name,1,diagnostics);
    return thug_animation_find(reader->name,1,diagnostics);
}
/* 0x004645e0. A reader can belong to either of the two configured pools. */
void thug_animation_reader_free(ThugAnimationReader *reader,const ThugMemory *memory) {
    ThugFixedPool *pool=thug_animation_reader_pools[thug_animation_reader_pool_index];
    if (pool && thug_pool_contains(pool,reader)) { thug_pool_release(pool,reader); return; }
    pool=thug_animation_reader_pools[thug_animation_reader_pool_index^1];
    if (pool && thug_pool_contains(pool,reader)) thug_pool_release(pool,reader);
    else memory->release(memory->context,reader);
}
/* 0x0048d000. */
ThugAnimationReader *thug_animation_reader_delete(ThugAnimationReader *reader,uint32_t flags,const ThugMemory *memory) {
    reader->methods=&thug_animation_reader_methods;
    if ((uint8_t)flags&1) thug_animation_reader_free(reader,memory);
    return reader;
}
/* 0x004b22a0, instantiated for the reader's virtual ABI, and 0x0048bfd0. */
void thug_animation_reader_release(ThugAnimationReader *reader,const ThugMemory *memory) {
    if (reader) reader->methods->dispose(reader,1,memory);
}
void thug_release_animation_reader(ThugAnimationReader *reader,const ThugMemory *memory) {
    thug_animation_reader_release(reader,memory);
}
