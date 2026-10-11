#ifndef THUG_CORE_SORT_H
#define THUG_CORE_SORT_H
#include <stdint.h>
typedef int32_t (*ThugCompare)(const void *, const void *);
void thug_crt_shortsort(void *low, void *high, uint32_t width, ThugCompare);
void thug_crt_qsort(void *base, uint32_t count, uint32_t width, ThugCompare);
#endif
