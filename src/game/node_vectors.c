#include "nodes.h"
/* 0045c050. Prefer the PC position field; legacy position negates Z. */
void thug_node_position(const ThugScriptStructure *node,float out[4]) {
    if(thug_script_get_vector(node,0x7f261953,out,0))return;
    if(thug_script_get_vector(node,0xb9d31b0a,out,0)){out[2]=-out[2];return;}
    out[0]=0;out[1]=0;out[2]=0;out[3]=1;
}
/* 0045c560. The original requires the named node to exist. */
void thug_node_position_by_name(uint32_t name,float out[4]) {
    thug_node_position(thug_node_table_find(thug_node_table,name,1),out);
}
/* 0045c180. Clear output before lookup, retaining the aliased-input order. */
void thug_node_angles(const ThugScriptStructure *node,float out[4]) {
    out[0]=0;out[1]=0;out[2]=0;out[3]=1;
    thug_script_get_vector(node,0x9d2d0915,out,0);
}
