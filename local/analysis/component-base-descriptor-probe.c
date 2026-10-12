/* Test adapter: invoke the concrete descriptor virtual. No routine credit. */
#include "../../src/game/components.h"
uint32_t thug_component_descriptor_virtual_probe_draft(void *p,const ThugScriptCommand *c,ThugScriptStructure *s,ThugScriptInstance *i){return (*(const ThugComponentMethods **)p)->descriptor(p,c,s,i);}
