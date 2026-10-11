#include "runtime.h"

/* 00472d20: clear only wait type bits owned by this component. Current and
 * saved owner pointers themselves remain unchanged, including null owners. */
void thug_script_clear_component_wait(ThugScriptInstance *script,const ThugScriptWaitOwner *owner) {
    if(script->wait_owner&&script->wait_owner==owner)script->wait_type=0;
    for(uint32_t i=0;(int32_t)i<(int32_t)script->call_depth;++i) {
        ThugScriptCallFrame *frame=(void *)(script->call_storage+i*48);
        if(frame->wait_owner&&frame->wait_owner==owner)frame->wait_type_bits&=0xfffffff0;
    }
}
/* 00472e70: the component destructor invalidates waits throughout the live
 * script list, preserving the original next-pointer read after each update. */
void thug_script_clear_component_waits(const ThugScriptWaitOwner *owner) {
    for(ThugScriptInstance *script=thug_script_list;script;script=script->next)
        thug_script_clear_component_wait(script,owner);
}
