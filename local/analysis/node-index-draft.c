#include "../../src/game/nodes.h"
#include "../../src/core/lookup.h"
#include "../../src/core/checksum.h"
#include "../../src/script/load.h"
#include "../../src/script/values.h"
#include <stddef.h>

typedef struct {uint32_t name;ThugScriptArray *nodes;uint8_t flag,padding[3];} NodeArrayBuildDraft;
typedef struct {
    ThugNodeSlot slots[16384];
    uint16_t unknown_10000,current_array;
    uint32_t array_count;
    NodeArrayBuildDraft arrays[20];
    uint32_t unknown_100f8;
} NodeTableBuildDraft;
_Static_assert(offsetof(NodeTableBuildDraft,arrays[0].nodes)==0x1000c,"Original array pointer");
_Static_assert(sizeof(NodeTableBuildDraft)==0x100fc,"Original node-table allocation");
/* 0045d370. Preserve all uninitialized metadata and array entries. */
NodeTableBuildDraft *thug_node_table_initialize_draft(NodeTableBuildDraft *table) {
    table->array_count=0;
    for(uint32_t i=0;i<16384;++i){table->slots[i].array_index=0;table->slots[i].node_index=-1;}
    table->current_array=UINT16_MAX;
    return table;
}
/* 0045ce60. Duplicate names still occupy another slot. Both indices are
 * truncated to sixteen bits; the hash table must contain a terminating hole. */
void thug_node_table_insert_draft(NodeTableBuildDraft *table,uint32_t array_index,
                                 uint32_t node_index,const ThugScriptStructure *node) {
    uint32_t kind=0,name=0;
    thug_script_get_checksum(node,0x12b4e660,&kind,0);
    if(kind==0xc953660e||!thug_script_get_checksum(node,0xa1dc81f9,&name,0))return;
    uint32_t slot=name&0x3fff;
    while(table->slots[slot].node_index!=-1)slot=(slot+1)&0x3fff;
    table->slots[slot].node_index=(int16_t)node_index;
    table->slots[slot].array_index=(uint16_t)array_index;
}
/* 0045d3a0. The caller has already bound this array entry. */
void thug_node_table_index_array_draft(NodeTableBuildDraft *table,uint32_t array_index) {
    ThugScriptArray *array=table->arrays[array_index].nodes;
    for(uint32_t i=0;i<array->count;++i)
        thug_node_table_insert_draft(table,array_index,i,thug_script_array_structure(array,i));
}
/* 0046f9b0. First equal key wins, even when its readable text is null. */
const char *thug_script_local_name_draft(uint32_t name) {
    if(!thug_script_local_names)return 0;
    for(ThugScriptLocalName *p=thug_script_local_names+(name&4095);p;p=p->next)
        if(p->name==name)return p->text;
    return 0;
}

typedef struct {int32_t count;uint16_t *indices;uint32_t key;} PrefixBuildIndicesDraft;
/* Keep the existing prefix lookup's external layout and type qualifiers. */
typedef struct PrefixArrayDraft {
    const ThugObjectLookupTable *table;
    uint32_t array_name;
    struct PrefixArrayDraft *next;
} PrefixArrayDraft;
typedef struct {PrefixArrayDraft *first;} PrefixManagerDraft;
extern PrefixManagerDraft *thug_node_prefix_manager_draft;
/* 0045bda0. Grow by one hundred entries AFTER storing the hundredth value.
 * Reload live count and storage after allocator calls, preserving mutation order. */
void thug_node_prefix_append_draft(PrefixBuildIndicesDraft *list,uint32_t index,const ThugMemory *m) {
    list->indices[list->count]=(uint16_t)index;
    int32_t count=(int32_t)((uint32_t)list->count+1);
    list->count=count;
    if(count%100==0) {
        uint16_t *old=list->indices;
        list->indices=m->allocate(m->context,(uint32_t)count*2+200,0);
        for(int32_t i=0;i<list->count;++i)list->indices[i]=old[i];
        if(old)m->release(m->context,old);
    }
}
/* 0045c650. Add to the first live matching lookup value, or create its list. */
void thug_node_prefix_add_draft(PrefixArrayDraft *entry,uint32_t key,uint32_t index,const ThugMemory *m) {
    const ThugObjectLookupTable *table=entry->table;
    ThugObjectLookupNode *p=(void *)((uintptr_t)table->buckets+(key&((1u<<(table->shift&31))-1))*12);
    while(p&&(p->key!=key||!p->value))p=p->next;
    if(p&&p->value){thug_node_prefix_append_draft(p->value,index,m);return;}
    PrefixBuildIndicesDraft *list=thug_allocate_zeroed(12,m);
    if(list){list->key=0;list->count=0;list->indices=m->allocate(m->context,200,0);}
    list->key=key;
    thug_node_prefix_append_draft(list,index,m);
    thug_object_table_insert((void *)entry->table,&key,list,m);
}
/* 0045c240. Iteration terminates at a null value. The old buffer is captured
 * before allocating its exact replacement; the live list count governs copying. */
void thug_node_prefix_compact_draft(PrefixArrayDraft *entry,const ThugMemory *m) {
    ThugObjectLookupTable *table=(void *)entry->table;
    table->iteration_bucket=UINT32_MAX;table->iteration_node=0;
    for(;;) {
        table=(void *)entry->table;
        if(!thug_object_table_next(table)||!table->iteration_node)return;
        PrefixBuildIndicesDraft *list=table->iteration_node->value;
        if(!list)return;
        uint16_t *old=list->indices;
        list->indices=m->allocate(m->context,(uint32_t)list->count*2,0);
        for(int32_t i=0;i<list->count;++i)list->indices[i]=old[i];
        if(old)m->release(m->context,old);
    }
}
/* 0045c5d0. Initialized allocator and successful allocations are the engine's
 * live-object contract; Windows exception unwinding is outside normal returns. */
PrefixArrayDraft *thug_node_prefix_array_initialize_draft(PrefixArrayDraft *entry,const ThugMemory *m) {
    ThugObjectLookupTable *table=m->allocate(m->context,24,1);
    if(table)table=thug_object_table_initialize(table,8,m);
    entry->table=table;entry->array_name=0;entry->next=0;
    return entry;
}
static uint32_t prefix_is_trg(const char *s) {
    /* The original C-locale case-insensitive comparison is only against TRG. */
    return (s[0]=='t'||s[0]=='T')&&(s[1]=='r'||s[1]=='R')&&
           (s[2]=='g'||s[2]=='G')&&!s[3];
}
/* 0045c700. Build prefixes from the loaded QB's local readable-name table.
 * Underscores add the preceding prefix, except TRG. A trailing run of digits
 * adds its preceding prefix as well. Preserve insertion and debug-name order.
 * Original names must fit the 1000-byte temporary buffer. */
void thug_node_prefix_build_draft(PrefixManagerDraft *manager,uint32_t array_name,const ThugMemory *m) {
    PrefixArrayDraft *entry=thug_allocate_zeroed(12,m);
    if(entry)entry=thug_node_prefix_array_initialize_draft(entry,m);
    entry->next=manager->first;manager->first=entry;entry->array_name=array_name;
    ThugScriptArray *array=thug_script_get_global_array(array_name,1);
    uint32_t count=array->count;
    for(uint32_t i=0;i<count;++i) {
        uint32_t name=0;
        thug_script_get_checksum(thug_script_array_structure(array,i),0xa1dc81f9,&name,0);
        const char *text=thug_script_local_name_draft(name);
        if(!text||!*text)continue;
        char buffer[1000],*digits=0;
        for(uint32_t j=0;;++j) {
            char c=text[j];buffer[j]=c;
            if(c>='0'&&c<='9'){if(!digits)digits=&buffer[j];}else digits=0;
            if(c=='_') {
                buffer[j]=0;
                if(!prefix_is_trg(buffer))thug_node_prefix_add_draft(entry,thug_crc32_string(buffer),i,m);
                thug_script_add_debug_name(thug_crc32_string(buffer),buffer);
                buffer[j]='_';buffer[j+1]=0;
                thug_script_add_debug_name(thug_crc32_string(buffer),buffer);
            }
            if(!text[j+1])break;
        }
        if(digits) {
            *digits=0;uint32_t prefix=thug_crc32_string(buffer);
            thug_node_prefix_add_draft(entry,prefix,i,m);
            thug_script_add_debug_name(prefix,buffer);
        }
    }
    thug_node_prefix_compact_draft(entry,m);
}
/* 0045c900. The same initialized scope is used by nested zeroed allocations. */
void thug_node_prefix_build_global_draft(uint32_t array_name,const ThugMemory *m) {
    m->temp_scope(m->context,1);
    if(!thug_node_prefix_manager_draft) {
        PrefixManagerDraft *manager=thug_allocate_zeroed(4,m);
        if(manager)manager->first=0;
        thug_node_prefix_manager_draft=manager;
    }
    thug_node_prefix_build_draft(thug_node_prefix_manager_draft,array_name,m);
    m->temp_scope(m->context,0);
}
/* 0046caf0. Only the low byte is stored; the other header bytes are untouched. */
void thug_script_array_set_type_draft(ThugScriptArray *array,uint32_t type) {
    ((uint8_t *)array)[1]=(uint8_t)type;
}
/* 0045d480. Links start as node-array indices. Resolve to node names and change
 * the link array type only when it was nonempty. Both loop counts are captured. */
void thug_node_links_resolve_draft(ThugScriptArray *array) {
    uint32_t count=array->count;
    for(uint32_t i=0;i<count;++i) {
        ThugScriptArray *links=0;
        if(!thug_script_get_array(thug_script_array_structure(array,i),0x2e7d5ee7,&links,0)||!links->count)continue;
        uint32_t link_count=links->count;
        for(uint32_t j=0;j<link_count;++j) {
            uint32_t index=(uintptr_t)thug_script_array_structure(links,j);
            uint32_t name=thug_node_name(thug_script_array_structure(array,index));
            thug_script_array_set_word(links,j,name);
        }
        thug_script_array_set_type_draft(links,13);
    }
}
