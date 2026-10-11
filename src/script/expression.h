#ifndef THUG_SCRIPT_EXPRESSION_H
#define THUG_SCRIPT_EXPRESSION_H
#include "operators.h"

typedef struct { uint32_t opcode, parentheses; } ThugScriptExpressionOperator;
typedef struct {
    ThugScriptComponent values[20];
    uint32_t value_index;
    ThugScriptExpressionOperator operators[20];
    uint32_t operator_index;
    uint8_t has_operator, padding_1e9[3];
    const uint8_t *origin;
    const char *error;
    uint8_t initialized, padding_1f5[3];
} ThugScriptExpression;

extern const char thug_expression_error_operator_overflow[], thug_expression_error_value_overflow[];
ThugScriptExpression *thug_script_expression_initialize(ThugScriptExpression *, const ThugMemory *);
void thug_script_expression_clear(ThugScriptExpression *, const ThugMemory *);
void thug_script_expression_clear_if_needed(ThugScriptExpression *, const ThugMemory *);
void thug_script_expression_destroy(ThugScriptExpression *, const ThugMemory *);
void thug_script_expression_set_origin(ThugScriptExpression *, const uint8_t *);
void thug_script_expression_set_error(ThugScriptExpression *, const char *, const ThugMemory *);
void thug_script_expression_push_operator(ThugScriptExpression *, uint32_t opcode, const ThugMemory *);
void thug_script_expression_push_value(ThugScriptExpression *, const ThugScriptComponent *, const ThugMemory *);
void thug_script_expression_open_parenthesis(ThugScriptExpression *);
extern ThugScriptComponent thug_expression_temporary;
extern const int32_t thug_expression_precedence[64];
void thug_script_expression_execute(ThugScriptExpression *, const ThugMemory *);
/* Operator tokens must be in the original precedence-table range [0, 63]. */
void thug_script_expression_accept_operator(ThugScriptExpression *, uint32_t opcode, const ThugMemory *);
void thug_script_expression_close_parenthesis(ThugScriptExpression *, const ThugMemory *);
uint8_t thug_script_expression_finish(ThugScriptExpression *, ThugScriptComponent *, const ThugMemory *);
#endif
