#ifndef THUG_SCRIPT_OPERATORS_H
#define THUG_SCRIPT_OPERATORS_H
#include "values.h"
ThugScriptComponent *thug_script_next_component(const ThugScriptStructure *, const ThugScriptComponent *);
void thug_script_remove_name(ThugScriptStructure *, uint32_t name, const ThugMemory *);
void thug_script_remove_typed(ThugScriptStructure *, uint32_t name, uint32_t type, const ThugMemory *);
void thug_script_remove_unnamed_value(ThugScriptStructure *, uint32_t value, const ThugMemory *);
uint8_t thug_script_component_equal(const ThugScriptComponent *, const ThugScriptComponent *);
uint8_t thug_script_component_less(const ThugScriptComponent *, const ThugScriptComponent *);
uint8_t thug_script_component_greater(const ThugScriptComponent *, const ThugScriptComponent *);
uint8_t thug_script_structure_is_subset(const ThugScriptStructure *, const ThugScriptStructure *);
uint8_t thug_script_array_equal_fallback(const ThugScriptArray *, const ThugScriptArray *);
const char *thug_script_array_text(const ThugScriptArray *, int32_t index);
double thug_script_array_number(const ThugScriptArray *, int32_t index);
void thug_script_array_component(const ThugScriptArray *, uint32_t index, ThugScriptComponent *, uint32_t borrow, const ThugMemory *);
uint8_t thug_script_component_is_borrowed(const ThugScriptComponent *);
void thug_script_component_borrow(ThugScriptComponent *);
void thug_script_component_own(ThugScriptComponent *);
uint32_t thug_script_component_truth(const ThugScriptComponent *);
void thug_script_component_resolve(ThugScriptComponent *);
#endif
