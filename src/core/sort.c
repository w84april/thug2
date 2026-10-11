#include "sort.h"

static void swap(uintptr_t left, uintptr_t right, uint32_t width) {
    if (left == right) return;
    uint8_t *a=(uint8_t *)left, *b=(uint8_t *)right;
    for (uint32_t i=0;i<width;++i) { uint8_t value=b[i];b[i]=a[i];a[i]=value; }
}
/* 00624230. Original private ABI passes high in EAX. Selection sort preserves
 * the first maximum on ties; swapping it to the end is deliberately unstable. */
void thug_crt_shortsort(void *first, void *last, uint32_t width, ThugCompare compare) {
    uintptr_t low=(uintptr_t)first, high=(uintptr_t)last;
    while (high>low) {
        uintptr_t greatest=low;
        for (uintptr_t p=low+width;p<=high;p+=width)
            if (compare((const void *)p,(const void *)greatest)>0) greatest=p;
        swap(greatest,high,width);high-=width;
    }
}
/* 006242a0. Median-of-three partitioning, exact comparison order, and original
 * equal-key partition trimming. Work on the smaller partition first. Valid
 * storage, non-mutating comparison, and representable byte ranges are the
 * same internal contracts as the original CRT routine. */
void thug_crt_qsort(void *base, uint32_t count, uint32_t width, ThugCompare compare) {
    if (count<2 || !width) return;
    uintptr_t low=(uintptr_t)base, high=low+(count-1)*width;
    uintptr_t saved_low[30],saved_high[30];uint32_t depth=0;
    for (;;) {
        uint32_t size=(high-low)/width+1;
        if (size<=8) thug_crt_shortsort((void *)low,(void *)high,width,compare);
        else {
            uintptr_t middle=low+(size/2)*width, left=low, right=high;
            if (compare((const void *)low,(const void *)middle)>0) swap(low,middle,width);
            if (compare((const void *)low,(const void *)high)>0) swap(low,high,width);
            if (compare((const void *)middle,(const void *)high)>0) swap(middle,high,width);
            for (;;) {
                if (middle>left) {
                    do {left+=width;} while (left<middle && compare((const void *)left,(const void *)middle)<=0);
                }
                if (middle<=left) {
                    do {left+=width;} while (left<=high && compare((const void *)left,(const void *)middle)<=0);
                }
                do {right-=width;} while (right>middle && compare((const void *)right,(const void *)middle)>0);
                if (left>right) break;
                swap(left,right,width);
                if (middle==right) middle=left;
            }
            right+=width;
            if (middle<right) {
                do {right-=width;} while (right>middle && compare((const void *)right,(const void *)middle)==0);
            }
            if (middle>=right) {
                do {right-=width;} while (right>low && compare((const void *)right,(const void *)middle)==0);
            }
            if ((int32_t)(right-low)>=(int32_t)(high-left)) {
                if (low<right) {saved_low[depth]=low;saved_high[depth++]=right;}
                if (left<high) {low=left;continue;}
            } else {
                if (left<high) {saved_low[depth]=left;saved_high[depth++]=high;}
                if (low<right) {high=right;continue;}
            }
        }
        if (!depth) return;
        --depth;low=saved_low[depth];high=saved_high[depth];
    }
}
