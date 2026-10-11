/* Test-only node-provider boundary, sharing the already verified event log. */
#include "rebound_callbacks.c"
uint32_t fixture_sweep_nodes(uint32_t owner) {
    observe(3, owner, 0, 0);
    return C[10];
}
