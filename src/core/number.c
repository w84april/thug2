#include "number.h"
#include "../platform/math.h"

/* 0x00403ef0. The game's polynomial approximation, used for the grounded
 * heading. Inputs are not clamped. Preserve PC24 operations, including the
 * negative-input branch and its final subtraction from the stored float pi. */
double thug_acos_approximate(float value) {
    double x = value < 0 ? -(double)value : value;
    double root = thug_platform_round_x87_single(__builtin_sqrt(thug_platform_round_x87_single(1-x)));
    double p = thug_platform_round_x87_single(x * (double)-0.018729299306869507f);
    p = thug_platform_round_x87_single(p + (double)0.07426100224256516f);
    p = thug_platform_round_x87_single(p*x);
    p = thug_platform_round_x87_single(p - (double)0.2121143937110901f);
    p = thug_platform_round_x87_single(p*x);
    p = thug_platform_round_x87_single(p + (double)1.5707287788391113f);
    p = thug_platform_round_x87_single(p*root);
    return value < 0 ? thug_platform_round_x87_single((double)3.1415927410125732f-p) : p;
}
/* 0x00405fd0. Zero (including -0) and unordered inputs select positive one. */
double thug_sign_nonnegative(float value) { return value < 0 ? -1 : 1; }
/* 0x004196b0. Equality or an unordered comparison selects the right operand,
 * including its signed zero or NaN; this is not the standard fmax operation. */
double thug_max_number(float left, float right) { return left > right ? left : right; }
/* 0x00487ad0. Ordered minima choose the right operand for equality or NaNs. */
double thug_min_three(float first,float second,float third) {
    double selected=second<third?second:third;
    return first<selected?first:selected;
}
/* 0x004022c0. Ordered comparisons: an unordered bound does not replace the
 * current value. Apply the maximum before the minimum, including reversed bounds. */
double thug_clamp_number(float value,float minimum,float maximum) {
    double result=value>maximum?maximum:value;
    return result<minimum?minimum:result;
}
