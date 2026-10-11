#include "../../src/game/components.h"
#include "../../src/game/assets.h"
#include "../../src/script/delivery.h"
#include "../../src/core/checksum.h"
extern uint32_t thug_model_base_path_draft(const char *,char *);
extern void *thug_model_asset_options_initialize_draft(void *);
extern uint8_t thug_asset_manager_flags_draft(const ThugAssetManager *);
extern void *thug_asset_get_or_load_draft(ThugAssetManager *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
/* Partial004935e0: the actual asset-manager route through texture load and
 * model-asset request. Alternate allocation/direct/already-loaded routes and
 * the post-model-load tail remain unavailable. Not a complete recovered routine.
 * Original texture options initialize only bytes0,4..9. Zeroing the other
 * automatic bytes gives portable deterministic padding; comparisons distinguish
 * these originally indeterminate bytes from every defined engine field. */
void (*thug_model_asset_ready_pending_draft)(void *,void *,void *);
void *thug_model_geometry_create_draft(const ThugMemory *);
uint8_t thug_model_geometry_bind_draft(void *,void *,void *,uint32_t,const ThugMemory *);
uint8_t thug_model_geometry_flag16_draft(void *,uint32_t);
void thug_model_geometry_set_lights_draft(void *,void *);
void thug_model_part_insert_draft(void *,void *,void *const *,const ThugMemory *);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint16_t half(const void *p,unsigned o){uint16_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,2);return v;}
static void put_half(void *p,unsigned o,uint16_t v){__builtin_memcpy((uint8_t *)p+o,&v,2);}
void thug_model_texture_load_prefix_draft(void *component,const ThugScriptStructure *params,void *renderer,const char *path,
    uint32_t key,uint32_t assets,uint32_t option,uint32_t flag,uint32_t skin,uint32_t route,uint32_t loaded){
    (void)component;(void)params;(void)key;(void)skin;
    const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
    const ThugDiagnostics *d=thug_component_services?thug_component_services->diagnostics:thug_event_services->diagnostics;
    ((uint8_t *)renderer)[0x44]&=0xfe;ThugAssetManager *manager=thug_asset_manager;
    if(!(uint8_t)route)__builtin_trap();
    void *part=m->allocate(m->context,24,1); /* part retained by the suspended original call */
    if(!(uint8_t)assets||(uint8_t)loaded)__builtin_trap();
    uint8_t texture_options[76]={0};char texture_path[256];
    __builtin_memcpy(texture_options+4,&option,4);texture_options[9]=flag;
    texture_options[8]=thug_model_base_path_draft(path,texture_path);
    char *end=texture_path;while(*end)end++;__builtin_memcpy(end,".tex",5);
    thug_asset_get_or_load_draft(manager,texture_path,0,0,0,0,0,thug_asset_manager_flags_draft(manager),(uintptr_t)texture_options,0,d,m);
    uint8_t model_options[20]={0};thug_model_asset_options_initialize_draft(model_options);
    model_options[0]=((uint8_t *)renderer)[0x44]>>5&1;__builtin_memcpy(model_options+4,&option,4);
    uint32_t flags=thug_asset_manager_flags_draft(manager),dependency=thug_crc32_string(texture_path);
    void *model=thug_asset_get_or_load_draft(manager,path,0,0,dependency,0,0,flags,(uintptr_t)model_options,0,d,m);
    if(thug_model_asset_ready_pending_draft){thug_model_asset_ready_pending_draft(renderer,part,model);__builtin_trap();}
    put(part,16,thug_crc32_string(path));put_half(renderer,0x4a,half(renderer,0x4a)+1);put(part,12,0);
    void *geometry=thug_model_geometry_create_draft(m);put(part,0,(uintptr_t)geometry);
    if(!(uint8_t)route&&!geometry)return; /* original AL0; current public prefix has no result */
    thug_model_geometry_bind_draft(geometry,model,renderer,skin,m);put(part,4,word(model,4));
    thug_model_geometry_flag16_draft(pointer(part,0),((uint8_t *)renderer)[0x44]>>4&1);put(part,8,key);
    put(renderer,0x18,word(renderer,0x18)|(1u<<(((uint8_t *)renderer)[0x46]&31)));
    if(word(renderer,0x2c))thug_model_geometry_set_lights_draft(pointer(part,0),pointer(renderer,0x2c));
    put_half(renderer,0x46,half(renderer,0x46)+1);
    if(word(renderer,4)){
        typedef struct{uintptr_t unused[3];uint32_t (*set)(void *,uint32_t);} Methods;
        if((uint8_t)((const Methods *)pointer(renderer,0))->set(renderer,0))put(renderer,4,0);
    }
    put(part,20,0);thug_model_part_insert_draft((uint8_t *)renderer+0x10,pointer(renderer,0x10),&part,m);
    if(half(renderer,0x46)==1)put(renderer,0x30,thug_crc32_string(path));
    /* The actual standard branch returns AL1. Other loading routes remain
     * explicit traps above; this contextual prefix still has a void ABI. */
}
