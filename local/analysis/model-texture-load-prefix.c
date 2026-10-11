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
void thug_model_texture_load_prefix_draft(void *component,const ThugScriptStructure *params,void *renderer,const char *path,
    uint32_t key,uint32_t assets,uint32_t option,uint32_t flag,uint32_t skin,uint32_t route,uint32_t loaded){
    (void)component;(void)params;(void)key;(void)skin;
    const ThugMemory *m=thug_component_services?thug_component_services->memory:thug_event_services->memory;
    const ThugDiagnostics *d=thug_component_services?thug_component_services->diagnostics:thug_event_services->diagnostics;
    ((uint8_t *)renderer)[0x44]&=0xfe;ThugAssetManager *manager=thug_asset_manager;
    if(!(uint8_t)route)__builtin_trap();
    m->allocate(m->context,24,1); /* part retained by the suspended original call */
    if(!(uint8_t)assets||(uint8_t)loaded)__builtin_trap();
    uint8_t texture_options[76]={0};char texture_path[256];
    __builtin_memcpy(texture_options+4,&option,4);texture_options[9]=flag;
    texture_options[8]=thug_model_base_path_draft(path,texture_path);
    char *end=texture_path;while(*end)end++;__builtin_memcpy(end,".tex",5);
    thug_asset_get_or_load_draft(manager,texture_path,0,0,0,0,0,thug_asset_manager_flags_draft(manager),(uintptr_t)texture_options,0,d,m);
    uint8_t model_options[20]={0};thug_model_asset_options_initialize_draft(model_options);
    model_options[0]=((uint8_t *)renderer)[0x44]>>5&1;__builtin_memcpy(model_options+4,&option,4);
    uint32_t flags=thug_asset_manager_flags_draft(manager),dependency=thug_crc32_string(texture_path);
    thug_asset_get_or_load_draft(manager,path,0,0,dependency,0,0,flags,(uintptr_t)model_options,0,d,m);
    __builtin_trap();
}
