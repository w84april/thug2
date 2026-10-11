#ifndef THUG_GAME_NODES_H
#define THUG_GAME_NODES_H
#include "../script/params.h"

typedef struct { uint16_t array_index; int16_t node_index; } ThugNodeSlot;
typedef struct {
    uint32_t unknown_0, unknown_4;
    ThugScriptArray *nodes;
} ThugNodeArrayEntry;
typedef struct {
    ThugNodeSlot slots[16384];
    uint32_t unknown_10000;
    ThugNodeArrayEntry arrays[];
} ThugNodeTable;

/* Original 0x006f0d84. Table population remains part of the unrecovered loader. */
extern ThugNodeTable *thug_node_table;
uint32_t thug_node_name(const ThugScriptStructure *);
ThugScriptStructure *thug_node_table_find(const ThugNodeTable *, uint32_t name, uint32_t unused);
ThugScriptStructure *thug_node_find(uint32_t name, uint32_t unused);
void thug_node_position(const ThugScriptStructure *,float[4]);
void thug_node_position_by_name(uint32_t,float[4]);
void thug_node_angles(const ThugScriptStructure *,float[4]);
#endif
