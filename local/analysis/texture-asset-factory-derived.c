/* Derived from pinned asset factory; bind actual texture loading virtuals. */
/* Extends the pinned skeleton-asset source with factory integration. */
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
    uint32_t unavailable_8;
    ThugAsset *(*dispose)(ThugAsset *,uint32_t,const ThugMemory *);
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
ThugAsset *thug_asset_delete_draft(ThugAsset *,uint32_t,const ThugMemory *);
const ThugAssetMethodsDraft thug_skeleton_asset_methods_draft={
    .dispose=thug_asset_delete_draft,
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

#include "../../src/core/checksum.h"
#include "../../src/game/nodes.h"
#include "../../src/script/delivery.h"

/* These classes' loading virtuals remain unavailable. Their constructors and
 * factory dispatch are recovered here; no replacement load success is supplied. */
#define OTHER_METHODS(name) const ThugAssetMethodsDraft name={.data=thug_asset_data,.ready=thug_asset_ready,.read_finished=thug_asset_read_finished}
OTHER_METHODS(thug_scene_asset_methods_draft);
#include "texture-asset-extension.c"
OTHER_METHODS(thug_collision_asset_methods_draft);
/* Model file virtual is an explicit unavailable boundary in texture-asset-extension.c. */
OTHER_METHODS(thug_animation2_asset_methods_draft);
OTHER_METHODS(thug_cutscene_asset_methods_draft);
OTHER_METHODS(thug_qb_asset_methods_draft);
#undef OTHER_METHODS
/* 00409220,0040a580,004095f0,0040a210,00408bb0. */
#define EXTRA_CTOR(name,table) ThugAsset *name(ThugAsset *a){thug_asset_initialize(a);a->methods=(const ThugAssetMethods *)&table;a->animation_name=0;return a;}
EXTRA_CTOR(thug_scene_asset_initialize_draft,thug_scene_asset_methods_draft)
EXTRA_CTOR(thug_texture_asset_initialize_draft,thug_texture_asset_methods_draft)
EXTRA_CTOR(thug_collision_asset_initialize_draft,thug_collision_asset_methods_draft)
EXTRA_CTOR(thug_animation2_asset_initialize_draft,thug_animation2_asset_methods_draft)
EXTRA_CTOR(thug_qb_asset_initialize_draft,thug_qb_asset_methods_draft)
#undef EXTRA_CTOR
/* 00409c40 and 00407a30. Model +4c remains untouched. */
ThugAsset *thug_model_asset_initialize_draft(ThugAsset *a){
    thug_asset_initialize(a);uint32_t *p=(uint32_t *)a;
    p[20]=p[21]=p[22]=p[23]=0;a->methods=(const ThugAssetMethods *)&thug_model_asset_methods_draft;return a;
}
ThugAsset *thug_cutscene_asset_initialize_draft(ThugAsset *a){
    thug_asset_initialize(a);a->methods=(const ThugAssetMethods *)&thug_cutscene_asset_methods_draft;return a;
}
/* 0045d140 and 00408bf0. The node table includes this loader-owned field beyond
 * its public lookup prefix; preserve exact offset without inventing a new table. */
void thug_node_table_set_asset_draft(ThugNodeTable *t,ThugAsset *a){
    __builtin_memcpy((uint8_t *)t+0x100f8,&a,4);
}
void thug_qb_asset_register_draft(ThugAsset *a){
    ((uint8_t *)a)[0x60]=1;thug_node_table_set_asset_draft(thug_node_table,a);
}
typedef struct AssetLinkDraft {
    const uint32_t *methods;
    uint32_t key,value;
    struct AssetLinkDraft *previous,*next;
} AssetLinkDraft;
const uint32_t thug_asset_detached_link_methods_draft[1]; /* 645564; deletion not yet called here. */
/* 00407810 and forwarding entry004093e0. */
void thug_asset_destroy_base_draft(ThugAsset *a){
    AssetLinkDraft *link=(AssetLinkDraft *)&a->link_methods;
    a->methods=&thug_asset_base_methods;link->methods=thug_asset_detached_link_methods_draft;
    link->next->previous=link->previous;link->previous->next=link->next;
    link->previous=link;link->next=link;
}
void thug_asset_destroy_forward_draft(ThugAsset *a){thug_asset_destroy_base_draft(a);}
/* 00407af0. Failure disposal does not implicitly unload a partially loaded file. */
ThugAsset *thug_asset_delete_draft(ThugAsset *a,uint32_t flags,const ThugMemory *m){
    thug_asset_destroy_forward_draft(a);if(flags&1)m->release(m->context,a);return a;
}
/* 004075d0,004076f0,00407700. */
void thug_asset_set_metadata_draft(ThugAsset *a,uint32_t x,uint32_t y,uint32_t z){a->unknown_14=x;a->unknown_18=y;a->unknown_1c=z;}
void *thug_asset_set_dependency_draft(ThugAsset *a,void *p){a->unknown_34=(uintptr_t)p;return p;}
uint32_t thug_asset_set_key_draft(ThugAsset *a,uint32_t key){a->unknown_4=key;return key;}
/* 00407840. Insert after the sentinel in its original next/previous convention. */
void thug_asset_add_dependent_draft(ThugAsset *a,ThugAsset *dependent,const ThugMemory *m){
    AssetLinkDraft *link=thug_allocate_zeroed(0x14,m);
    if(link){link->methods=thug_asset_detached_link_methods_draft;link->key=(uintptr_t)dependent;link->value=0;link->previous=link;link->next=link;}
    AssetLinkDraft *head=(AssetLinkDraft *)&a->link_methods;
    link->next=head->next;link->previous=head;head->next->previous=link;head->next=link;
}
/* 004079c0. Original static extension table67c650, with the game's C-locale
 * case-insensitive comparisons. This method does not inspect path separators. */
uint32_t thug_asset_type_draft(ThugAssetManager *manager,const char *name){
    (void)manager;const char *p=name;while(*p)p++;
    while(p>name&&*p!='.')p--;
    if(*p!='.')return 0;p++;
    static const struct {const char *extension;uint32_t kind;} types[]={
        {"BIN",1},{"COL",4},{"SCN",2},{"GEOM",2},{"MDL",7},{"SKA",5},
        {"FAM",5},{"SKE",6},{"SKIN",7},{"TEX",3},{"CUT",9},{"QB",10}
    };
    for(unsigned i=0;i<12;i++){
        const char *a=types[i].extension,*b=p;
        for(;;a++,b++){
            uint8_t x=(uint8_t)*a,y=(uint8_t)*b;
            if(y>='a'&&y<='z')y-=32;
            if(x!=y)break;if(!x)return types[i].kind;
        }
    }
    return 0;
}
/* 00407a60. */
uint8_t thug_asset_manager_flags_draft(const ThugAssetManager *m){return ((const uint8_t *)m)[0x14];}
static ThugAsset *find_asset(const ThugAssetManager *m,uint32_t key){
    ThugObjectLookupTable *t=m->table;
    ThugObjectLookupNode *p=t->buckets+(key&((1u<<(t->shift&31))-1));
    while(p&&(p->key!=key||!p->value))p=p->next;
    return p?p->value:0;
}
/* 00407b90. Preserve the extra ready call before the first wait. */
ThugAsset *thug_asset_find_object_draft(ThugAssetManager *m,uint32_t key,uint32_t required,const ThugDiagnostics *d){
    (void)required;ThugAsset *a=find_asset(m,key);
    if(a&&!a->methods->ready(a)&&!a->methods->ready(a))do{thug_async_wait(0,d);}while(!a->methods->ready(a));
    return a;
}
typedef struct {
    uint8_t unknown_0[0x1c];ThugObjectLookupTable *table;
    ThugAsset *sync,*async;uint32_t metadata[3];uint8_t once,padding[3];
} AssetManagerDraft;
_Static_assert(offsetof(AssetManagerDraft,once)==0x34,"manager pending metadata");
/* 00408440. All original type branches and failure/list/dependency paths.
 * Valid type2..11, initialized manager/lists and successful allocations are the
 * original internal contract. Missing class loading virtuals remain unavailable. */
void *thug_asset_create_draft(ThugAssetManager *manager,const char *name,uint32_t type,uint32_t key,uint32_t dependency,
    uint32_t async,uint32_t x,uint32_t flags,uint32_t y,uint32_t z,const ThugDiagnostics *d,const ThugMemory *m){
    AssetManagerDraft *manager_full=(AssetManagerDraft *)manager;
    if(!key)key=thug_crc32_string(name);if(!type)type=thug_asset_type_draft(manager,name);
    ThugAsset *a=0;
    #define CREATE(bytes,constructor) do{a=thug_allocate_zeroed(bytes,m);if(a)a=constructor(a);}while(0)
    switch(type){
    case 2:CREATE(0x50,thug_scene_asset_initialize_draft);break;
    case 3:CREATE(0x50,thug_texture_asset_initialize_draft);break;
    case 4:CREATE(0x50,thug_collision_asset_initialize_draft);break;
    case 5:CREATE(0x50,thug_animation_asset_initialize);break;
    case 6:CREATE(0x4c,thug_skeleton_asset_initialize_draft);break;
    case 7:CREATE(0x60,thug_model_asset_initialize_draft);break;
    case 8:CREATE(0x50,thug_animation2_asset_initialize_draft);break;
    case 9:CREATE(0x4c,thug_cutscene_asset_initialize_draft);break;
    case 10:case 11:CREATE(0x64,thug_qb_asset_initialize_draft);if(type==11)thug_qb_asset_register_draft(a);break;
    }
    #undef CREATE
    ((uint8_t *)a)[12]=(uint8_t)flags;a->state=0;
    thug_asset_set_metadata_draft(a,manager_full->metadata[0],manager_full->metadata[1],manager_full->metadata[2]);
    if(manager_full->once){manager_full->metadata[0]=0;manager_full->once=0;}
    thug_asset_set_key_draft(a,key);
    if(dependency){ThugAsset *parent=thug_asset_find_object_draft(manager,dependency,1,d);thug_asset_set_dependency_draft(a,parent);thug_asset_add_dependent_draft(parent,a,m);}
    if(methods(a)->load_file(a,name,async,x,y,z,m)){
        if(!thug_script_get_global_integer(0x25dc7904,0))methods(a)->dispose(a,1,m);
        return 0;
    }
    thug_object_table_insert(manager_full->table,&key,a,m);
    ThugAsset **head=(uint8_t)async?&manager_full->async:&manager_full->sync;
    if(*head){
        a->unknown_30=(uintptr_t)*head;a->unknown_2c=(*head)->unknown_2c;
        ((ThugAsset *)(uintptr_t)(*head)->unknown_2c)->unknown_30=(uintptr_t)a;
        (*head)->unknown_2c=(uintptr_t)a;
    }else{*head=a;a->unknown_30=(uintptr_t)a;a->unknown_2c=(uintptr_t)a;}
    return a->methods->data(a);
}
/* 004087b0. Capture existing data before waiting; preserve the discarded debug
 * symbol lookup on both paths. */
void *thug_asset_get_or_load_draft(ThugAssetManager *manager,const char *name,uint32_t type,uint32_t key,uint32_t dependency,
    uint32_t async,uint32_t x,uint32_t flags,uint32_t y,uint32_t z,const ThugDiagnostics *d,const ThugMemory *m){
    if(!key)key=thug_crc32_string(name);ThugAsset *a=find_asset(manager,key);void *data;
    if(!a)data=thug_asset_create_draft(manager,name,type,key,dependency,async,x,flags,y,z,d,m);
    else{data=a->methods->data(a);while(!a->methods->ready(a))thug_async_wait(0,d);}
    thug_script_get_global_integer(0x25dc7904,0);return data;
}
/* 00445640. Name and unnamed checksum are required by the original script ABI. */
uint8_t thug_load_skeleton_draft(ThugScriptStructure *params,ThugScriptInstance *script,const ThugDiagnostics *d,const ThugMemory *m){
    (void)script;ThugAssetManager *manager=thug_asset_manager;
    const char *name;uint32_t key;
    thug_script_get_text(params,0xa1dc81f9,&name,1);thug_script_get_checksum(params,0,&key,1);
    thug_asset_get_or_load_draft(manager,name,0,key,0,0,0,thug_asset_manager_flags_draft(manager),0,0,d,m);return 1;
}
/* Host ABI bridge, not an additional original routine. */
uint8_t thug_load_skeleton_native_draft(ThugScriptStructure *params,ThugScriptInstance *script){
    return thug_load_skeleton_draft(params,script,thug_event_services->diagnostics,thug_event_services->memory);
}
