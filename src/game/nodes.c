#include "nodes.h"
#include <stddef.h>

_Static_assert(sizeof(ThugNodeSlot) == 4, "Node slot layout");
_Static_assert(sizeof(ThugNodeArrayEntry) == 12, "Node array entry layout");
_Static_assert(offsetof(ThugNodeTable, arrays) == 0x10004, "Node array offset");
ThugNodeTable *thug_node_table;

/* 0x0045be40. Missing names return the initialized zero. */
uint32_t thug_node_name(const ThugScriptStructure *node) {
    uint32_t name = 0;
    thug_script_get_checksum(node, 0xa1dc81f9, &name, 0);
    return name;
}

/* 0x0045cfc0. Open addressing wraps at 16384 slots. Each occupied slot names
 * an array and a signed node index. Valid tables contain a terminating -1 slot. */
ThugScriptStructure *thug_node_table_find(const ThugNodeTable *table, uint32_t name, uint32_t unused) {
    (void)unused;
    uint32_t slot = name & 0x3fff;
    while (table->slots[slot].node_index != -1) {
        const ThugNodeSlot *entry = &table->slots[slot];
        ThugScriptStructure *node = thug_script_array_structure(
            table->arrays[entry->array_index].nodes, entry->node_index);
        uint32_t actual = 0;
        thug_script_get_checksum(node, 0xa1dc81f9, &actual, 1);
        if (actual == name) return node;
        slot = (slot + 1) & 0x3fff;
    }
    return NULL;
}

/* 0x0045c1b0. */
ThugScriptStructure *thug_node_find(uint32_t name, uint32_t unused) {
    return thug_node_table_find(thug_node_table, name, unused);
}
