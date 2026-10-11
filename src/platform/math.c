#include "math.h"
#include <stdint.h>
extern double sin(double);
extern double cos(double);
extern double tan(double);
extern double atan2(double, double);
extern double log2(double);
int thug_math_errno;
float thug_platform_reciprocal_seed(float value) { return 1.0f / value; }
float thug_platform_rsqrt_seed(float value) { return 1.0f / __builtin_sqrtf(value); }
double thug_platform_tan(double angle) { return tan(angle); }
double thug_platform_atan2(double y, double x) { return atan2(y,x); }
double thug_platform_log2(double value) { return log2(value); }

double thug_platform_acos_x87_single(float value) {
    if (!(value >= -1 && value <= 1)) {
        thug_math_errno = 33; /* MSVC CRT domain error, with default matherr. */
        return __builtin_nan("");
    }
    if (value == 1) return 0;
    if (value == -1) return 0x1.921fb54442d18p+1;
    double plus = thug_platform_round_x87_single(1 + (double)value);
    double minus = thug_platform_round_x87_single(1 - (double)value);
    double product = thug_platform_round_x87_single(plus * minus);
    double y = thug_platform_round_x87_single(__builtin_sqrt(product));
    /* FPATAN itself is a transcendental operation, not a PC=24 multiply.
     * The SDK atan2 replaces that instruction; physical x87 accuracy is not
     * claimed. Preserve the PC=24 arithmetic preceding it. */
    return atan2(y, value);
}

double thug_platform_round_x87_single(double value) {
    if (!__builtin_isfinite(value) || value == 0) return value;
    union { double value; uint64_t bits; } n = { .value = value };
    uint64_t tail = n.bits & UINT64_C(0x1fffffff);
    uint64_t kept = n.bits & ~UINT64_C(0x1fffffff);
    if (tail > UINT64_C(0x10000000) || (tail == UINT64_C(0x10000000) && (kept & UINT64_C(0x20000000))))
        kept += UINT64_C(0x20000000);
    n.bits = kept; return n.value;
}

double thug_platform_sin(double angle) {
    /* Finite out-of-range FSIN inputs are left unchanged. Infinities produce NaN. */
    if (__builtin_isfinite(angle) && __builtin_fabs(angle) >= 0x1p63) return angle;
    return sin(angle);
}
double thug_platform_cos(double angle) {
    if (__builtin_isfinite(angle) && __builtin_fabs(angle) >= 0x1p63) return angle;
    return cos(angle);
}

double thug_platform_multiply_x87_single(double value, double factor) {
    /* PC=24 rounds the significand but retains x87's wider exponent. Using a
     * float cast would underflow tiny script angles. Split the exact integer
     * case as well: its 31x24-bit product can exceed double's 53-bit precision.
     * Both partial products are exact and the residual resolves halfway ties. */
    double high = (double)(float)value;
    double high_product = high * (double)factor;
    double low_product = (value - high) * (double)factor;
    double product = high_product + low_product;
    if (!__builtin_isfinite(product) || product == 0) return value * (double)factor;
    double residual = low_product - (product - high_product);
    union { double value; uint64_t bits; } number = { .value = product };
    uint64_t tail = number.bits & UINT64_C(0x1fffffff);
    uint64_t retained = number.bits & ~UINT64_C(0x1fffffff);
    if (product < 0) residual = -residual;
    if (tail > UINT64_C(0x10000000) || (tail == UINT64_C(0x10000000)
        && (residual > 0 || (residual == 0 && (retained & UINT64_C(0x20000000))))))
        retained += UINT64_C(0x20000000);
    number.bits = retained;
    return number.value;
}
