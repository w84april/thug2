/* Included by a new derivation of the pinned asset factory. */
#include "../../src/script/delivery.h"
static uint32_t texture_word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void texture_put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
_Alignas(4) uint8_t thug_asset_options_storage_draft[4*96]; /*691758*/
uint32_t thug_asset_options_mask_draft; /*6918d8*/
/* 00407730 /00407770: four fixed slots. The size argument is ignored, unused
 * bytes retained, and release accepts only exact slot starts. */
void *thug_asset_options_allocate_draft(uint32_t ignored){
    (void)ignored;uint32_t mask=thug_asset_options_mask_draft;
    for(unsigned i=0;i<4;i++)if(!(mask&(1u<<i))){thug_asset_options_mask_draft=mask|(1u<<i);return thug_asset_options_storage_draft+i*96;}
    return 0;
}
void thug_asset_options_release_draft(void *p){
    for(unsigned i=0;i<4;i++)if(p==thug_asset_options_storage_draft+i*96){thug_asset_options_mask_draft&=~(1u<<i);return;}
}
/* 0040a620: explicit options precede script overrides; the 19 word copy is
 * forward and retains original overlap ordering. A free slot is required. */
void thug_texture_asset_options_draft(ThugAsset *a,const void *options,const ThugScriptStructure *params){
    a->animation_name=(uintptr_t)thug_asset_options_allocate_draft(0x4c);
    uint8_t *p=(void *)(uintptr_t)a->animation_name;p[0]=1;texture_put(p,4,0);p[8]=0;p[9]=0;
    if(options)for(unsigned i=0;i<19;i++)texture_put(p,i*4,texture_word(options,i*4));
    if(params){
        thug_script_get_integer(params,0xbf34d221,(uint32_t *)(p+4),0);
        p[0]=thug_script_has_flag(params,0xe6237329);
        p[8]=thug_script_has_flag(params,0x6875b9c0);
        p[9]=thug_script_has_flag(params,0x86b52462);
    }
}
/* 0049ef90: actual PC4b2320 extension is Xbx. Sufficient non-overlapping
 * destination capacity is the original internal formatting contract. */
void thug_texture_filename_draft(char *out,const char *name){
    while(*name)*out++=*name++;*out++='.';*out++='X';*out++='b';*out++='x';*out=0;
}
extern void *thug_texture_dictionary_get_buffer_draft(uint32_t,const uint8_t *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
/* 0040a5a0: real5480c0 is the asset key getter. The completed parse owns its
 * dictionary; the source buffer is retained for the original unload path. */
void thug_texture_asset_parse_draft(ThugAsset *a,const void *data,uint32_t size,const ThugMemory *m){
    const uint8_t *p=(void *)(uintptr_t)a->animation_name;
    void *dictionary=thug_texture_dictionary_get_buffer_draft(a->unknown_4,data,size,p[0],texture_word(p,4),p[8],p[9],m);
    methods(a)->set_data(a,dictionary);
    thug_asset_options_release_draft((void *)(uintptr_t)a->animation_name);a->animation_name=0;
    if(a->file){thug_asset_io_draft->close(thug_asset_io_draft->context,a->file);a->file=0;}
    thug_asset_finish_parse_draft(a,data,size);
}
/* 0040a840. Copy is selected solely by its low byte. Original diagnostics are
 * bare RETs; the fixed diagnostic formatting has no externally visible result. */
uint32_t thug_texture_asset_load_buffer_draft(ThugAsset *a,const void *data,uint32_t size,uint32_t copy,uint32_t options,uint32_t params,const ThugMemory *m){
    thug_asset_begin_load_draft(a,data,size,copy,options,params);
    thug_texture_asset_options_draft(a,(void *)(uintptr_t)options,(void *)(uintptr_t)params);
    if((uint8_t)copy){a->buffer=m->allocate(m->context,size,0);__builtin_memcpy(a->buffer,data,size);data=a->buffer;}
    methods(a)->parse(a,data,size,m);return 0;
}
/* 0040a720. Names must fit the original options payload (65 bytes plus NUL).
 * Open failure retains options/loading state, exactly as the PC routine does. */
int32_t thug_texture_asset_load_file_draft(ThugAsset *a,const char *name,uint32_t async,uint32_t x,uint32_t options,uint32_t params,const ThugMemory *m){
    thug_asset_begin_load_draft(a,name,async,x,options,params);
    thug_texture_asset_options_draft(a,(void *)(uintptr_t)options,(void *)(uintptr_t)params);
    char *dest=(char *)(uintptr_t)a->animation_name+10;const char *src=name;
    do{*dest++=*src;}while(*src++);
    char path[256];thug_texture_filename_draft(path,name);
    a->file=thug_asset_io_draft->open(thug_asset_io_draft->context,path,!(uint8_t)async,100);
    if(!a->file)return -1;
    uint32_t size=thug_asset_io_draft->size(thug_asset_io_draft->context,a->file);
    a->buffer=m->allocate(m->context,size,0);
    if((uint8_t)async){a->file->flags=8;a->file->callback=thug_asset_read_callback;a->file->context=a;a->file->argument=0;}
    thug_asset_io_draft->read(thug_asset_io_draft->context,a->file,a->buffer,1,size);
    if(!(uint8_t)async){a->size=size;methods(a)->process_loaded(a,m);}
    return 0;
}
const ThugAssetMethodsDraft thug_texture_asset_methods_draft={
    .dispose=thug_asset_delete_draft,.data=thug_asset_data,.ready=thug_asset_ready,
    .load_buffer=thug_texture_asset_load_buffer_draft,.load_file=thug_texture_asset_load_file_draft,
    .set_data=thug_asset_set_data_draft,.process_loaded=thug_asset_process_loaded_draft,.parse=thug_texture_asset_parse_draft,
    .loading=thug_asset_loading_draft,.read_finished=thug_asset_read_finished,.mark_ready=thug_asset_mark_ready,
    .unloaded=thug_asset_unloaded_draft
    /* Texture dictionary destruction/unload remains unavailable. */
};
/* Explicit missing model-file boundary. The manager still executes its real
 * factory/dependency work before arriving here; no result is manufactured. */
int32_t (*thug_model_asset_file_pending_draft)(ThugAsset *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
int32_t thug_model_asset_file_unavailable_draft(ThugAsset *a,const char *name,uint32_t async,uint32_t x,uint32_t options,uint32_t params,const ThugMemory *m){
    if(thug_model_asset_file_pending_draft)thug_model_asset_file_pending_draft(a,name,async,x,options,params,m);
    __builtin_trap();
}
/* 0048bfe0: strip first .skin, then first .mdl; return whether .skin existed.
 * The original copy is forward, including the terminator. */
uint32_t thug_model_base_path_draft(const char *name,char *out){
    char *d=out;do{*d++=*name;}while(*name++);
    uint32_t skin=0;
    for(char *p=out;*p;p++)if(p[0]=='.'&&p[1]=='s'&&p[2]=='k'&&p[3]=='i'&&p[4]=='n'){*p=0;skin=1;break;}
    for(char *p=out;*p;p++)if(p[0]=='.'&&p[1]=='m'&&p[2]=='d'&&p[3]=='l'){*p=0;break;}
    return skin;
}
/* 00409e90: retain padding and the word at+c. */
void *thug_model_asset_options_initialize_draft(void *p){
    ((uint8_t *)p)[0]=0;texture_put(p,4,0);texture_put(p,8,0);((uint8_t *)p)[16]=0;((uint8_t *)p)[17]=0;return p;
}

#include "model-asset-extension.c"
