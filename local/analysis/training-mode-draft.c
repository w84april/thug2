#include "../../src/game/stats.h"
#include "../../src/script/operators.h"
/* 005a11d0. Only unnamed checksum components are candidates. Iterate the
 * actual parameter list, with first-truthy short circuit and settings lookup. */
uint8_t thug_game_mode_equals_draft(const ThugScriptStructure *params,void *script){
    (void)script;
    for(ThugScriptComponent *c=thug_script_next_component(params,0);c;c=thug_script_next_component(params,c))
        if(!c->name&&(c->type_and_flags&0xfe)==0x1a&&thug_settings_flag(thug_game_settings,c->value))return 1;
    return 0;
}

/* 0045be90 / 0045bf90. Prefix lookup traverses already populated per-array
 * indexes. Building those indexes remains part of node-loader recovery. */
typedef struct {uint16_t count,padding;const uint16_t *indices;} PrefixIndicesDraft;
typedef struct PrefixArrayDraft {
    const ThugObjectLookupTable *table;
    uint32_t array_name;
    struct PrefixArrayDraft *next;
} PrefixArrayDraft;
typedef struct {PrefixArrayDraft *first;} PrefixManagerDraft;
PrefixManagerDraft *thug_node_prefix_manager_draft; /* 006f0d80 */
uint32_t thug_node_prefix_results_draft[1000]; /* 006efde0..006f0d80 */
uint32_t *thug_node_prefix_find_draft(const PrefixManagerDraft *manager,uint32_t prefix,uint16_t *count){
    uint32_t n=0;
    for(const PrefixArrayDraft *entry=manager->first;entry;entry=entry->next){
        const ThugObjectLookupTable *t=entry->table;
        const ThugObjectLookupNode *p=(void *)((uintptr_t)t->buckets+(prefix&((1u<<(t->shift&31))-1))*12);
        while(p&&(p->key!=prefix||!p->value))p=p->next;
        const PrefixIndicesDraft *found=p?p->value:0;
        if(found&&found->count){
            uint32_t size=found->count;const uint16_t *indices=found->indices;
            const ThugScriptArray *array=thug_script_get_global_array(entry->array_name,1);
            for(uint32_t i=0;i<size;i++){
                const ThugScriptStructure *node=thug_script_array_structure(array,indices[i]);
                uint32_t name=0;thug_script_get_checksum(node,0xa1dc81f9,&name,0);
                thug_node_prefix_results_draft[n++]=name;
            }
        }
    }
    *count=(uint16_t)n;return thug_node_prefix_results_draft;
}
uint32_t *thug_node_prefix_find_global_draft(uint32_t prefix,uint16_t *count){
    return thug_node_prefix_find_draft(thug_node_prefix_manager_draft,prefix,count);
}

#include "../../src/core/checksum.h"
/* 00476a30. Scene commands accept literal checksums or names supplied as text.
 * Checksum lookup has priority; both failures preserve the caller's output. */
uint8_t thug_script_get_scene_name_draft(const ThugScriptStructure *s,uint32_t name,uint32_t *out,uint32_t required){
    if(!thug_script_get_checksum(s,name,out,required)){
        const char *text=0;
        if(!thug_script_get_text(s,name,&text,required))return 0;
        *out=thug_crc32_string(text);
    }
    return 1;
}
