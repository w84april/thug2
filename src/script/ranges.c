#include "tokens.h"
#include "params.h"
#include "../core/number.h"
#include "../core/random.h"
#include "../platform/math.h"

static double round24(double value) { return thug_platform_round_x87_single(value); }

/* 0x0046fbd0: bytecode in EAX, stream selector in BL, output on the stack.
 * Both endpoints are read before writing the component. Values within 1e-5 of
 * the original signed-integer candidates produce an inclusive integer range.
 * The conversion bias is 0.1, not ordinary round-to-nearest's 0.5. Unordered
 * tolerance comparisons take the integer branch, matching the x87 status tests. */
const uint8_t *thug_script_random_value(const uint8_t *p, ThugScriptComponent *out, uint32_t alternate) {
    alternate &= 0xff;
    union { uint32_t bits; float value; } first = { .bits = thug_script_read_word(p + 1) };
    union { uint32_t bits; float value; } second = { .bits = thug_script_read_word(p + 5) };
    double a = first.value, b = second.value;
    int32_t ia = (int32_t)thug_truncate_double_low_word(round24(a + (a < 0 ? -(double)0.1f : (double)0.1f)));
    int32_t ib = (int32_t)thug_truncate_double_low_word(round24(b + (b < 0 ? -(double)0.1f : (double)0.1f)));
    double da = __builtin_fabs(round24(a - (double)ia));
    double db = __builtin_fabs(round24(b - (double)ib));
    if (!(da > (double)0.00001f) && !(db > (double)0.00001f)) {
        if (ia > ib) { int32_t swap = ia; ia = ib; ib = swap; }
        uint32_t limit = (uint32_t)ib - (uint32_t)ia + 1;
        int32_t choice = alternate ? thug_random_alternate_range(limit) : thug_random_range(limit);
        out->value = (uint32_t)choice + (uint32_t)ia;
        out->type_and_flags = (out->type_and_flags & 1) | 2;
    } else {
        if (a > b) { double swap = a; a = b; b = swap; }
        int32_t choice = alternate ? thug_random_alternate_range(0x7ff9) : thug_random_range(0x7ff9);
        double value = round24(round24(b - a) * (double)choice);
        value = round24(value * (double)3.052503234357573e-05f);
        union { float value; uint32_t bits; } result = { .value = (float)round24(value + a) };
        out->type_and_flags = (out->type_and_flags & 1) | 4;
        out->value = result.bits;
    }
    return p + 9;
}
