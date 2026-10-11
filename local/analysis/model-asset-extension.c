/* Included after the recovered texture asset code; original PC model assets. */
typedef struct {
    void *context;
    void *(*acquire)(void *,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
    uint32_t (*size)(void *,const char *);
    void (*release)(void *,uint32_t);
} ThugModelFileCacheDraft;
/* Platform file-cache boundary, distinct from model parsing. */
const ThugModelFileCacheDraft *thug_model_file_cache_draft;
static void *model_pointer(const ThugAsset *a,unsigned offset){return (void *)(uintptr_t)texture_word(a,offset);}
static void model_set_pointer(ThugAsset *a,unsigned offset,const void *p){texture_put(a,offset,(uintptr_t)p);}
/* 00409e10: defaults then explicit five-word copy, then script overrides. */
void thug_model_asset_options_draft(ThugAsset *a,const void *options,const ThugScriptStructure *params){
    uint8_t *p=thug_asset_options_allocate_draft(20);model_set_pointer(a,0x50,p);
    thug_model_asset_options_initialize_draft(p);
    if(options)for(unsigned i=0;i<5;i++)texture_put(p,i*4,texture_word(options,i*4));
    if(params){thug_script_get_integer(params,0xbf34d221,(uint32_t *)(p+4),0);p[0]=thug_script_has_flag(params,0x01a1482e);}
}
/* 00409c60: unsigned decrement/wrap, mark read-complete only on zero. */
uint8_t thug_model_asset_read_finished_draft(ThugAsset *a){
    uint32_t count=texture_word(a,0x5c)-1;texture_put(a,0x5c,count);
    if(count)return 0;return thug_asset_read_finished(a);
}
/* 00409da0: companion buffer first; cached primary data releases by checksum. */
void thug_model_asset_release_buffer_draft(ThugAsset *a,const ThugMemory *m){
    void *companion=model_pointer(a,0x58);
    if(companion){m->release(m->context,companion);model_set_pointer(a,0x58,0);}
    if(a->animation_name){thug_model_file_cache_draft->release(thug_model_file_cache_draft->context,a->animation_name);a->animation_name=0;a->buffer=0;return;}
    if(a->buffer)m->release(m->context,a->buffer);a->animation_name=0;a->buffer=0;
}
/* Partial00409c70: real dependency lookup, data virtual, and all eight model
 * parser arguments. No parsed model, cleanup or success is fabricated. */
void (*thug_model_buffer_pending_draft)(uint32_t,const void *,uint32_t,const void *,void *,uint32_t,uint32_t,uint32_t,const ThugMemory *);
void thug_model_asset_parse_prefix_draft(ThugAsset *a,const void *data,uint32_t size,const ThugMemory *m){
    ThugAsset *dependency=(void *)(uintptr_t)a->unknown_34;
    void *dictionary=methods(dependency)->data(dependency);
    const uint8_t *options=model_pointer(a,0x50);
    if(thug_model_buffer_pending_draft)thug_model_buffer_pending_draft(a->unknown_4,data,size,
        (void *)(uintptr_t)texture_word(options,8),dictionary,texture_word(options,4),options[16],options[0],m);
    __builtin_trap();
}
/* 0040a140: copy only when both low-byte copy and !options[17]. */
uint32_t thug_model_asset_load_buffer_draft(ThugAsset *a,const void *data,uint32_t size,uint32_t copy,uint32_t options,uint32_t params,const ThugMemory *m){
    thug_asset_begin_load_draft(a,data,size,copy,options,params);
    thug_model_asset_options_draft(a,(void *)(uintptr_t)options,(void *)(uintptr_t)params);
    if((uint8_t)copy&&!((uint8_t *)model_pointer(a,0x50))[17]){
        a->buffer=m->allocate(m->context,size,0);__builtin_memcpy(a->buffer,data,size);data=a->buffer;
    }
    methods(a)->parse(a,data,size,m);return 0;
}
extern void thug_model_path_lower_draft(char *);
static void model_filename(char *out,const char *base,const char *suffix){
    while(*base)*out++=*base++;while((*out++=*suffix++));
}
static void model_read_callback(ThugAsyncFile *file,ThugAsset *a){
    file->flags=8;file->callback=thug_asset_read_callback;file->context=a;file->argument=0;
}
/* 00409eb0: complete file orchestration. Names must fit the original512-byte
 * stack buffers. Cache and ordinary-file providers return bounded resident data
 * and arrange async completion separately, as required by the asset interface. */
int32_t thug_model_asset_load_file_draft(ThugAsset *a,const char *name,uint32_t async,uint32_t x,uint32_t options,uint32_t params,const ThugMemory *m){
    thug_asset_begin_load_draft(a,name,async,x,options,params);
    thug_model_asset_options_draft(a,(void *)(uintptr_t)options,(void *)(uintptr_t)params);
    char base[512],path[512],companion_path[512];uint32_t skin=thug_model_base_path_draft(name,base);
    thug_model_path_lower_draft(base);((uint8_t *)model_pointer(a,0x50))[17]=0;
    model_filename(path,base,skin?".skin.Xbx":".mdl.Xbx");
    ((uint8_t *)model_pointer(a,0x50))[16]=skin;texture_put(a,0x5c,texture_word(a,0x5c)+1);
    uint32_t size;
    if(skin&&!(uint8_t)async){
        a->animation_name=thug_crc32_string(path);
        a->buffer=thug_model_file_cache_draft->acquire(thug_model_file_cache_draft->context,path,0,0,0,0);
        size=thug_model_file_cache_draft->size(thug_model_file_cache_draft->context,path);
    }else{
        a->file=thug_asset_io_draft->open(thug_asset_io_draft->context,path,!(uint8_t)async,100);
        if(!a->file)return -1;
        size=thug_asset_io_draft->size(thug_asset_io_draft->context,a->file);a->buffer=m->allocate(m->context,size,0);
        if((uint8_t)async)model_read_callback(a->file,a);
        thug_asset_io_draft->read(thug_asset_io_draft->context,a->file,a->buffer,1,size);
    }
    if(skin){
        model_filename(companion_path,base,".cas.Xbx");texture_put(a,0x5c,texture_word(a,0x5c)+1);
        ThugAsyncFile *file=thug_asset_io_draft->open(thug_asset_io_draft->context,companion_path,!(uint8_t)async,100);
        model_set_pointer(a,0x54,file);if(!file)return -1;
        uint32_t count=thug_asset_io_draft->size(thug_asset_io_draft->context,file);
        void *buffer=m->allocate(m->context,count,0);model_set_pointer(a,0x58,buffer);texture_put(model_pointer(a,0x50),8,(uintptr_t)buffer);
        if((uint8_t)async)model_read_callback(file,a);
        thug_asset_io_draft->read(thug_asset_io_draft->context,file,buffer,1,count);
    }
    if(((uint8_t *)model_pointer(a,0x50))[17])m->temp_scope(m->context,0);
    if(!(uint8_t)async){
        if(model_pointer(a,0x58))texture_put(a,0x5c,texture_word(a,0x5c)-1);
        texture_put(a,0x5c,texture_word(a,0x5c)-1);a->size=size;methods(a)->process_loaded(a,m);
    }
    return 0;
}
/* Retain the previous checkpoint's explicit409eb0 test breakpoint. Normally the
 * pointer is NULL and execution enters the newly recovered file loader. */
static int32_t model_file_dispatch(ThugAsset *a,const char *name,uint32_t async,uint32_t x,uint32_t options,uint32_t params,const ThugMemory *m){
    if(thug_model_asset_file_pending_draft)return thug_model_asset_file_unavailable_draft(a,name,async,x,options,params,m);
    return thug_model_asset_load_file_draft(a,name,async,x,options,params,m);
}
const ThugAssetMethodsDraft thug_model_asset_methods_draft={
    .data=thug_asset_data,.ready=thug_asset_ready,.loading=thug_asset_loading_draft,
    .read_finished=thug_model_asset_read_finished_draft,.mark_ready=thug_asset_mark_ready,
    .load_file=model_file_dispatch,.load_buffer=thug_model_asset_load_buffer_draft,
    .process_loaded=thug_asset_process_loaded_draft,.parse=thug_model_asset_parse_prefix_draft,
    .release_buffer=thug_model_asset_release_buffer_draft
};
