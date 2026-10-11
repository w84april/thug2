#include "../../src/game/assets.h"
#include <stddef.h>

typedef struct ThugSkeletonDraft ThugSkeletonDraft;
extern ThugSkeletonDraft *thug_skeleton_initialize_draft(ThugSkeletonDraft *);
extern uint8_t thug_skeleton_parse_draft(ThugSkeletonDraft *,const uint8_t *,uint32_t,uint32_t,const ThugMemory *);

/* Port interface, not recovered Windows file-handle/worker-thread code.
 * A provider must resolve the engine's mounted archives before loose files,
 * use PC path casing rules, and arrange asynchronous read completion separately.
 * The current comparison provider supplies complete, bounded resident files. */
typedef struct {
    void *context;
    ThugAsyncFile *(*open)(void *,const char *,uint32_t,uint32_t);
    uint32_t (*size)(void *,ThugAsyncFile *);
    uint32_t (*read)(void *,ThugAsyncFile *,void *,uint32_t,uint32_t);
    uint8_t (*close)(void *,ThugAsyncFile *);
} ThugAssetIoDraft;
const ThugAssetIoDraft *thug_asset_io_draft;

typedef struct {
    uint32_t unavailable_0;
    void *(*data)(const ThugAsset *);
    uint32_t unavailable_8,unavailable_c;
    uint32_t (*load_buffer)(ThugAsset *,const void *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
    int32_t (*load_file)(ThugAsset *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
    uint32_t (*unload)(ThugAsset *,const ThugMemory *);
    uint32_t unavailable_1c;
    uint8_t (*ready)(const ThugAsset *);
    uint32_t unavailable_24;
    void *(*set_data)(ThugAsset *,void *);
    uint32_t unavailable_2c;
    void (*process_loaded)(ThugAsset *,const ThugMemory *);
    void (*parse)(ThugAsset *,const void *,uint32_t,const ThugMemory *);
    uint32_t unavailable_38;
    void (*release_buffer)(ThugAsset *,const ThugMemory *);
    uint32_t (*loading)(ThugAsset *);
    uint8_t (*read_finished)(ThugAsset *);
    uint32_t unavailable_48;
    uint8_t (*mark_ready)(ThugAsset *);
    uint8_t (*unloaded)(ThugAsset *);
    uint32_t unavailable_54;
} ThugAssetMethodsDraft;
_Static_assert(offsetof(ThugAssetMethodsDraft,parse)==0x34,"asset parser virtual");
_Static_assert(sizeof(ThugAssetMethodsDraft)==0x58,"asset virtual layout");
static const ThugAssetMethodsDraft *methods(const ThugAsset *a){return (const ThugAssetMethodsDraft *)a->methods;}

/* 00407670 and 004076b0. */
uint32_t thug_asset_loading_draft(ThugAsset *a){a->state=1;return 1;}
uint8_t thug_asset_unloaded_draft(ThugAsset *a){a->state=0;return 1;}
/* 004076e0. */
void *thug_asset_set_data_draft(ThugAsset *a,void *data){a->data=data;return data;}
/* 004075f0. Five arguments are consumed but ignored. */
uint32_t thug_asset_begin_load_draft(ThugAsset *a,const void *p,uint32_t n,uint32_t x,uint32_t y,uint32_t z){
    (void)p;(void)n;(void)x;(void)y;(void)z;methods(a)->loading(a);return 0;
}
/* 00407600 and 00407630. */
uint32_t thug_asset_finish_unload_draft(ThugAsset *a){methods(a)->unloaded(a);return 0;}
uint8_t thug_asset_finish_parse_draft(ThugAsset *a,const void *p,uint32_t n){
    (void)p;(void)n;methods(a)->mark_ready(a);return 1;
}
/* 00407620. Read buffer/size before the virtual may clear them. */
void thug_asset_process_loaded_draft(ThugAsset *a,const ThugMemory *m){methods(a)->parse(a,a->buffer,a->size,m);}

/* 00409a10. */
void thug_skeleton_asset_release_buffer_draft(ThugAsset *a,const ThugMemory *m){
    if(a->buffer){m->release(m->context,a->buffer);a->buffer=0;}
}
/* 00409b80. Only complete readable skeleton buffers with successful allocation
 * enter this original parser. A failed parse retains the original early return. */
void thug_skeleton_asset_parse_draft(ThugAsset *a,const void *p,uint32_t n,const ThugMemory *m){
    ThugSkeletonDraft *s=thug_allocate_zeroed(0x598,m);
    if(s)s=thug_skeleton_initialize_draft(s);
    if(!thug_skeleton_parse_draft(s,p,n,1,m))return;
    methods(a)->set_data(a,s);
    if(a->file){thug_asset_io_draft->close(thug_asset_io_draft->context,a->file);a->file=0;}
    methods(a)->release_buffer(a,m);
    thug_asset_finish_parse_draft(a,p,n);
}
/* 00409990. Both 5480a0 diagnostic calls in the original are actual no-ops. */
uint32_t thug_skeleton_asset_load_buffer_draft(ThugAsset *a,const void *p,uint32_t n,uint32_t x,uint32_t y,uint32_t z,const ThugMemory *m){
    thug_asset_begin_load_draft(a,p,n,x,y,z);methods(a)->parse(a,p,n,m);return 0;
}
/* 004099e0. The virtual destructor's result is ignored. Buffer cleanup only
 * runs when a data object existed; resetting the state always runs. */
uint32_t thug_skeleton_asset_unload_draft(ThugAsset *a,const ThugMemory *m){
    void *data=methods(a)->data(a);
    if(data){
        typedef struct {void *(*destroy)(void *,uint32_t,const ThugMemory *);} DataMethods;
        const DataMethods *v=*(const DataMethods **)data;
        v->destroy(data,1,m);methods(a)->set_data(a,0);methods(a)->release_buffer(a,m);
    }
    return thug_asset_finish_unload_draft(a);
}
/* 00409a50. The port caller bounds the filename to <=251 bytes, matching the
 * original 256-byte stack buffer. Only its low async byte controls the branch.
 * The original fixed extension comes from 48c0c0 -> 4b2320: exactly "Xbx". */
int32_t thug_skeleton_asset_load_file_draft(ThugAsset *a,const char *name,uint32_t async,uint32_t x,uint32_t y,uint32_t z,const ThugMemory *m){
    thug_asset_begin_load_draft(a,name,async,x,y,z);
    char path[256];uint32_t i=0;
    while(name[i]){path[i]=name[i];i++;}
    path[i++]='.';path[i++]='X';path[i++]='b';path[i++]='x';path[i]=0;
    a->file=thug_asset_io_draft->open(thug_asset_io_draft->context,path,!(uint8_t)async,100);
    if(!a->file)return -1;
    uint32_t size=thug_asset_io_draft->size(thug_asset_io_draft->context,a->file);
    m->temp_scope(m->context,2);
    a->buffer=m->allocate(m->context,size,0);
    m->temp_scope(m->context,0);
    if((uint8_t)async){
        a->file->flags=8;
        a->file->callback=thug_asset_read_callback;a->file->context=a;a->file->argument=0;
    }
    thug_asset_io_draft->read(thug_asset_io_draft->context,a->file,a->buffer,1,size);
    if(!(uint8_t)async){a->size=size;methods(a)->process_loaded(a,m);}
    return 0;
}
const ThugAssetMethodsDraft thug_skeleton_asset_methods_draft={
    .data=thug_asset_data,.load_buffer=thug_skeleton_asset_load_buffer_draft,
    .load_file=thug_skeleton_asset_load_file_draft,.unload=thug_skeleton_asset_unload_draft,
    .ready=thug_asset_ready,.set_data=thug_asset_set_data_draft,
    .process_loaded=thug_asset_process_loaded_draft,.parse=thug_skeleton_asset_parse_draft,
    .release_buffer=thug_skeleton_asset_release_buffer_draft,.loading=thug_asset_loading_draft,
    .read_finished=thug_asset_read_finished,.mark_ready=thug_asset_mark_ready,.unloaded=thug_asset_unloaded_draft
};
/* 00409970. This class uses only the base 0x4c bytes. */
ThugAsset *thug_skeleton_asset_initialize_draft(ThugAsset *a){
    thug_asset_initialize(a);a->methods=(const ThugAssetMethods *)&thug_skeleton_asset_methods_draft;return a;
}
