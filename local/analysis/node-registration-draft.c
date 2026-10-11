#include "../../src/game/nodes.h"
#include "../../src/script/values.h"
#include "../../src/script/operators.h"
#include "../../src/collision/probe.h"
#include <stddef.h>

typedef struct {uint32_t name;ThugScriptArray *nodes;uint8_t flag,padding[3];} RegisteredArrayDraft;
typedef struct {
    ThugNodeSlot slots[16384];
    uint16_t current_array,current_node;
    uint32_t array_count;
    RegisteredArrayDraft arrays[20];
    uint32_t unknown_100f8;
} NodeRegistrationDraft;
_Static_assert(offsetof(NodeRegistrationDraft,arrays)==0x10008,"Original entries");
_Static_assert(sizeof(NodeRegistrationDraft)==0x100fc,"Original allocation");
extern void thug_node_table_index_array_draft(NodeRegistrationDraft *,uint32_t);
extern void thug_node_prefix_build_global_draft(uint32_t,const ThugMemory *);
extern void thug_node_links_resolve_draft(ThugScriptArray *);

/* 0045d050. A nonzero name must exist in the table. Unlike find, this internal
 * iterator positioning routine has no missing-name termination test. */
void thug_node_iteration_start_draft(NodeRegistrationDraft *table,uint32_t name) {
    table->current_array=0;table->current_node=0;
    if(!name)return;
    uint32_t slot=name&0x3fff;
    for(;;slot=(slot+1)&0x3fff) {
        ThugNodeSlot entry=table->slots[slot];
        ThugScriptStructure *node=thug_script_array_structure(table->arrays[entry.array_index].nodes,entry.node_index);
        uint32_t actual=0;thug_script_get_checksum(node,0xa1dc81f9,&actual,1);
        if(actual==name) {
            /* Copy both halfwords together, after the getter. */
            __builtin_memcpy(&table->current_array,&table->slots[slot],4);return;
        }
    }
}
/* 0045d3f0. Preserve sixteen-bit wrapping and the signed node/count comparison.
 * The caller supplies valid current-array storage; empty arrays are not skipped. */
ThugScriptStructure *thug_node_iteration_next_draft(NodeRegistrationDraft *table) {
    if((int16_t)table->current_node==-1)return 0;
    ThugScriptArray *array=table->arrays[table->current_array].nodes;
    ThugScriptStructure *node=thug_script_array_structure(array,(int16_t)table->current_node);
    int32_t count=(int32_t)array->count;
    table->current_node++;
    if((int16_t)table->current_node>=count) {
        table->current_array++;
        uint32_t index=table->current_array;
        table->current_node=0;
        if(index>=table->array_count)table->current_node=UINT16_MAX;
    }
    return node;
}
/* 0045d110 and the three global wrappers 0045c1d0/0045c1f0/0045c200. */
void thug_node_iteration_end_draft(NodeRegistrationDraft *table) {table->current_node=UINT16_MAX;}
void thug_node_iteration_start_global_draft(uint32_t name) {thug_node_iteration_start_draft((void *)thug_node_table,name);}
ThugScriptStructure *thug_node_iteration_next_global_draft(void) {return thug_node_iteration_next_draft((void *)thug_node_table);}
void thug_node_iteration_end_global_draft(void) {thug_node_iteration_end_draft((void *)thug_node_table);}

/* 0045c020 / 0045c420. The link target requires a valid link array/index. */
uint32_t thug_node_link_count_draft(const ThugScriptStructure *node) {
    ThugScriptArray *links=0;thug_script_get_array(node,0x2e7d5ee7,&links,0);
    return links?links->count:0;
}
ThugScriptStructure *thug_node_link_target_draft(const ThugScriptStructure *node,int32_t index) {
    ThugScriptArray *links=0;thug_script_get_array(node,0x2e7d5ee7,&links,0);
    uint32_t name=(uintptr_t)thug_script_array_structure(links,index);
    return thug_node_table_find(thug_node_table,name,1);
}

typedef struct {ThugObjectReference *references;int32_t count;} NodeReferenceListDraft;
typedef struct {NodeReferenceListDraft *lists;uint32_t unknown_4,group_count;int32_t list_count;} NodeLinkGroupsDraft;
NodeLinkGroupsDraft *thug_node_link_groups_draft; /* 006f2264 */
/* 004694e0. The process allocator is initialized before this normal path. */
NodeLinkGroupsDraft *thug_node_link_groups_get_draft(const ThugMemory *m) {
    if(!thug_node_link_groups_draft) {
        NodeLinkGroupsDraft *groups=m->allocate(m->context,16,1);
        if(groups){groups->group_count=0;groups->list_count=0;groups->lists=0;groups->unknown_4=0;}
        thug_node_link_groups_draft=groups;
    }
    return thug_node_link_groups_draft;
}
/* 00469540. Reference unlinking mutates actual referenced objects and neighbors.
 * Reload the live array pointer and signed length for each iteration. */
void thug_node_reference_list_clear_draft(NodeReferenceListDraft *list) {
    for(int32_t i=0;i<list->count;++i) {
        ThugObjectReference *ref=&list->references[i];
        if(ref->object){thug_object_reference_unlink(ref->object,ref);ref->object=0;}
        ref->object=0;
    }
}
/* 004696c0. Clear references, then label connected first-link chains. A chain
 * merging with an existing group restarts at its first node with that group ID.
 * Rails, climbing nodes and PedAI waypoints are skipped by the outer traversal. */
void thug_node_link_groups_rebuild_draft(NodeLinkGroupsDraft *groups,const ThugMemory *m) {
    if(!groups->lists)return;
    for(int32_t i=0;i<groups->list_count;++i)thug_node_reference_list_clear_draft(&groups->lists[i]);
    groups->group_count=0;
    thug_node_iteration_start_global_draft(0);
    for(ThugScriptStructure *node=thug_node_iteration_next_global_draft();node;node=thug_node_iteration_next_global_draft()) {
        uint32_t kind=0;thug_script_get_checksum(node,0x12b4e660,&kind,0);
        if(kind==0x8e6b02ad||kind==0x30c19600)continue;
        if(kind==0x4c23a77e) {
            uint32_t type;
            if(thug_script_get_checksum(node,0x7321a8d6,&type,0)&&type==0xcba10ffa)continue;
        }
        uint32_t links=thug_node_link_count_draft(node),registered=0;
        if((!links&&kind!=0x4c23a77e)||thug_script_has_name_or_flag(node,0x9c91c3ca))continue;
        ThugScriptStructure *current=node;uint32_t candidate=groups->group_count;
        for(;;) {
            if(thug_script_get_integer(current,0x9c91c3ca,&registered,0)) {
                if((uint32_t)registered==candidate)break;
                candidate=(uint32_t)registered;current=node;
            }
            thug_script_set_integer(current,0x9c91c3ca,candidate,m);
            if(!thug_node_link_count_draft(current))break;
            current=thug_node_link_target_draft(current,0);
        }
        if(candidate==groups->group_count)groups->group_count++;
    }
    thug_node_iteration_end_global_draft();
}
/* 0045d520. Register once, construct real indexes, convert coordinates and links,
 * then optionally rebuild link groups. All original callees now execute. */
uint8_t thug_node_register_array_draft(NodeRegistrationDraft *table,uint32_t name,uint32_t postprocess,const ThugMemory *m) {
    for(uint32_t i=0;i<table->array_count;++i)if(table->arrays[i].name==name)return 0;
    ThugScriptArray *array=thug_script_get_global_array(name,1);
    table->arrays[table->array_count].name=name;
    table->arrays[table->array_count].nodes=array;
    table->arrays[table->array_count].flag=(uint8_t)postprocess;
    uint32_t index=table->array_count;table->array_count=index+1;
    thug_node_table_index_array_draft(table,index);
    thug_node_prefix_build_global_draft(name,m);
    int32_t count=(int32_t)array->count;
    for(int32_t i=0;i<count;++i) {
        ThugScriptStructure *node=thug_script_array_structure(array,i);
        float position[4]={0,0,0,1};
        if(thug_script_get_vector(node,0xb9d31b0a,position,0)) {
            thug_script_remove_name(node,0xb9d31b0a,m);
            uint32_t bits[4];__builtin_memcpy(bits,position,16);
            /* The vector getter already quieted Z's x87 load. FCHS flips its
             * sign including zeros, infinities and NaN payloads. X stays raw. */
            thug_script_set_vector_bits(node,0x7f261953,bits[0],bits[1],bits[2]^0x80000000u,m);
        }
    }
    thug_node_links_resolve_draft(array);
    if((uint8_t)postprocess)thug_node_link_groups_rebuild_draft(thug_node_link_groups_get_draft(m),m);
    return 1;
}
