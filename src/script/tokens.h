#ifndef THUG_SCRIPT_TOKENS_H
#define THUG_SCRIPT_TOKENS_H
#include <stdint.h>
#include "params.h"
/* Internal unchecked bytecode helpers. The loader must establish valid lengths,
 * terminated strings and balanced blocks before exposing external input. */
uint32_t thug_script_read_word(const uint8_t *);
uint16_t thug_script_read_half(const uint8_t *);
uint8_t *thug_script_write_word(uint8_t *, uint32_t);
uint8_t *thug_script_write_half(uint8_t *, uint32_t);
const uint8_t *thug_script_skip_lines(const uint8_t *);
const uint8_t *thug_script_next_token(const uint8_t *);
const uint8_t *thug_script_skip_value(const uint8_t *);
const uint8_t *thug_script_skip_script(const uint8_t *);
const uint8_t *thug_script_skip_line(const uint8_t *);
void thug_script_prepare_bytecode(uint8_t *);
const uint8_t *thug_script_random_value(const uint8_t *, ThugScriptComponent *, uint32_t alternate);
#endif
