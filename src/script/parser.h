#ifndef THUG_SCRIPT_PARSER_H
#define THUG_SCRIPT_PARSER_H
#include "expression.h"
#include "branches.h"
#include "../platform/diagnostics.h"

/* Original shared parser state at 0x006f2370 and 0x006f2568. Recursive parsing
 * uses these same objects; introducing a separate evaluator per call changes
 * observable original behavior. */
extern ThugScriptExpression thug_script_parser_expression;
extern ThugScriptComponent thug_script_parser_value;
typedef uint32_t (*ThugScriptNativePredicate)(ThugScriptStructure *, ThugScriptInstance *);
/* Port ABI adapter, not an additional recovered function. A null diagnostics
 * argument inherits the enclosing dispatcher binding for parsed predicates. */
uint32_t thug_script_call_native(ThugScriptNativePredicate, ThugScriptStructure *, ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);

/* Internal parsers require valid, terminating QB grammar and successful memory
 * allocation. The outer file loader must validate untrusted bytecode first.
 * Native symbol values must already be relocated to callable function pointers. */
const uint8_t *thug_script_parse_named_value(const uint8_t *, uint32_t name, ThugScriptStructure *, const ThugScriptStructure *arguments, const ThugMemory *);
const uint8_t *thug_script_parse_component_value(const uint8_t *, const ThugScriptStructure *arguments, ThugScriptComponent *, const ThugMemory *);
const uint8_t *thug_script_parse_parameters(ThugScriptStructure *, const uint8_t *, const ThugScriptStructure *arguments, const ThugMemory *);
const uint8_t *thug_script_parse_structure(ThugScriptStructure *, const uint8_t *, const ThugScriptStructure *arguments, const ThugMemory *);
const uint8_t *thug_script_parse_array(ThugScriptArray *, const uint8_t *, const ThugScriptStructure *arguments, const ThugMemory *);
const uint8_t *thug_script_parse_expression(const uint8_t *, const ThugScriptStructure *arguments, ThugScriptComponent *, const ThugMemory *);
#endif
