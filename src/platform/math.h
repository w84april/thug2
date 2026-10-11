#ifndef THUG_PLATFORM_MATH_H
#define THUG_PLATFORM_MATH_H
/* Port adapter, not recovered game code. Uses the SDK's static double-precision
 * libm. FSIN/FCOS hardware accuracy is not reproduced. */
double thug_platform_sin(double angle);
double thug_platform_cos(double angle);
/* SDK replacement for FPTAN after the floor handler's clamped acos. */
double thug_platform_tan(double angle);
/* SDK replacement for FPATAN, with no physical x87 accuracy claim. */
double thug_platform_atan2(double y, double x);
/* SDK replacement for the logarithm part of FYL2X. This does not claim
 * physical x87 transcendental accuracy or exception-status emulation. */
double thug_platform_log2(double value);
/* Numeric adapter for the single-precision-control CRT acos path at 623630.
 * Error state is shared with recovered CRT text conversion in this
 * single-threaded port, not host libc errno. */
extern int thug_math_errno;
double thug_platform_acos_x87_single(float value);
/* Input value must be an exact int32 or float32, as returned by the QB getter.
 * Factor has at most 24 significant bits; its exponent may exceed float32. */
double thug_platform_multiply_x87_single(double value, double factor);
/* Round a normal double result to a 24-bit significand, preserving exponent.
 * Used for bounded stat, rotation and timer arithmetic, not arbitrary x87. */
double thug_platform_round_x87_single(double value);
/* SSE seed adapters follow the pinned Unicorn 2.1.4 float32 division/sqrt
 * model. Physical Intel/AMD reciprocal approximation tables are not emulated.
 * Recovered callers retain their original Newton refinement operations. */
float thug_platform_reciprocal_seed(float value);
float thug_platform_rsqrt_seed(float value);
#endif
