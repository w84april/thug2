#include "../../src/core/memory.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
#include <stddef.h>

typedef struct ThugSkeletonDraft ThugSkeletonDraft;
typedef struct {
    ThugSkeletonDraft *(*destroy)(ThugSkeletonDraft *, uint32_t, const ThugMemory *);
} ThugSkeletonMethodsDraft;
struct ThugSkeletonDraft {
    const ThugSkeletonMethodsDraft *methods;
    int32_t count;
    uint32_t names[64], parents[64], mirrors[64];
    int32_t mirror_indices[64];
    uint8_t unknown_408[0x100];
    uint32_t unknown_508;
    uint8_t unknown_50c[0x7c];
    uint32_t unknown_588;
    float (*matrices)[16], (*translations)[4];
    uint32_t flags;
};
_Static_assert(sizeof(ThugSkeletonDraft)==0x598, "skeleton layout");
_Static_assert(offsetof(ThugSkeletonDraft,matrices)==0x58c, "matrix pointer");

ThugSkeletonDraft *thug_skeleton_destroy_draft(ThugSkeletonDraft *, uint32_t, const ThugMemory *);
const ThugSkeletonMethodsDraft thug_skeleton_methods_draft = {thug_skeleton_destroy_draft};

static uint32_t word(const void *p) { uint32_t v; __builtin_memcpy(&v,p,4); return v; }
static void store(void *p,uint32_t v) { __builtin_memcpy(p,&v,4); }
static uint32_t quiet(uint32_t v) {
    if ((v&0x7f800000)==0x7f800000 && (v&0x7fffff)) v|=0x400000;
    return v;
}
static void copy_words(void *to,const void *from,uint32_t count) {
    for(uint32_t i=0;i<count;i++)store((uint8_t *)to+4*i,word((const uint8_t *)from+4*i));
}

/* 00463aa0. Conjugates the supplied quaternion IN PLACE. Keep the two
 * float32 product spills and the PC24 register products' wider exponent.
 * Translation is read word-by-word after the basis stores, including overlap. */
float *thug_quaternion_translation_matrix_draft(float q[4],const float t[4],float out[16]) {
    for(unsigned i=0;i<3;i++)store(q+i,quiet(word(q+i))^0x80000000u);
    #define R thug_platform_round_x87_single
    double x=q[0], y=q[1], z=q[2], w=q[3];
    double xx=R(x*x), yy=R(y*y), zz=R(z*z);
    double yz=R(z*y), xz=R(z*x), xy=R(y*x);
    float wx=(float)R(w*x), wy=(float)R(w*y);
    double wz=R(w*z);
    out[0]=(float)R(1.0-R(2.0*R(zz+yy)));
    out[1]=(float)R(2.0*R(wz+xy));
    out[2]=(float)R(2.0*R(xz-wy)); out[3]=0;
    out[4]=(float)R(2.0*R(xy-wz));
    out[5]=(float)R(1.0-R(2.0*R(zz+xx)));
    out[6]=(float)R(2.0*R((double)wx+yz)); out[7]=0;
    out[8]=(float)R(2.0*R((double)wy+xz));
    out[9]=(float)R(2.0*R(yz-wx));
    out[10]=(float)R(1.0-R(2.0*R(yy+xx))); out[11]=0;
    #undef R
    copy_words(out+12,t,4);out[15]=1;
    return out;
}

/* 004a2c20. The translation pointer and all unspecified fields are untouched;
 * the asset caller obtains zeroed storage before constructing this object. */
ThugSkeletonDraft *thug_skeleton_initialize_draft(ThugSkeletonDraft *s) {
    s->methods=&thug_skeleton_methods_draft;s->count=0;s->flags=0;
    s->unknown_588=0;s->matrices=0;s->unknown_508=0x7f7fc99e;
    return s;
}

/* 004a3950. Both buffers are cleared after release, before optional object
 * deletion. Constructor-only storage must have a valid translation pointer. */
ThugSkeletonDraft *thug_skeleton_destroy_draft(ThugSkeletonDraft *s,uint32_t flags,const ThugMemory *m) {
    s->methods=&thug_skeleton_methods_draft;
    if(s->matrices){m->release(m->context,s->matrices);s->matrices=0;}
    if(s->translations){m->release(m->context,s->translations);s->translations=0;}
    if(flags&1)m->release(m->context,s);
    return s;
}

/* Inlined search in 004a39c0, not another recovered routine. Missing and
 * duplicate names retain the original index-zero / first-match behavior. */
static int32_t find_bone(const ThugSkeletonDraft *s,uint32_t name) {
    for(int32_t i=0;i<s->count;i++)if(s->names[i]==name)return i;
    return 0;
}

/* 004a39c0. Internal parser: readable complete data, at most 64 bones and
 * successful allocations are required, as in the original. The supplied
 * length and flag are ignored by the original, not a file-validation layer.
 * Keep this behind a validated file boundary when integrating the loader. */
uint8_t thug_skeleton_parse_draft(ThugSkeletonDraft *s,const uint8_t *input,
    uint32_t length,uint32_t option,const ThugMemory *m) {
    (void)length;(void)option;
    s->flags=word(input+4);s->count=(int32_t)word(input+8);
    const uint8_t *p=input+12;
    copy_words(s->names,p,(uint32_t)s->count&0x3fffffff);p+=(uint32_t)s->count*4;
    copy_words(s->parents,p,(uint32_t)s->count&0x3fffffff);p+=(uint32_t)s->count*4;
    copy_words(s->mirrors,p,(uint32_t)s->count&0x3fffffff);p+=(uint32_t)s->count*4;
    s->matrices=m->allocate(m->context,(uint32_t)s->count*64,1);
    s->translations=m->allocate(m->context,(uint32_t)s->count*16,1);
    for(int32_t i=0;i<s->count;i++,p+=32) {
        float q[4],t[4],matrix[16];
        copy_words(q,p,4);copy_words(t,p+16,4);
        store(t,quiet(word(t)));store(t+1,quiet(word(t+1)));
        store(s->translations[i],word(t));store(s->translations[i]+2,word(t+2));
        store(s->translations[i]+3,word(t+3));store(s->translations[i]+1,word(t+1));
        thug_quaternion_translation_matrix_draft(q,t,matrix);
        if(i) {
            float parent[16];copy_words(parent,s->matrices[find_bone(s,s->parents[i])],16);
            thug_matrix_rigid_inverse(parent);
            thug_matrix_multiply(matrix,matrix,parent);
            matrix[3]=matrix[7]=matrix[11]=0;matrix[15]=1;
        }
        thug_matrix_rigid_inverse(matrix);copy_words(s->matrices[i],matrix,16);
    }
    for(int32_t i=0;i<s->count;i++) {
        uint32_t name=s->mirrors[i];
        if(!name)s->mirror_indices[i]=-1;
        else {int32_t other=find_bone(s,name);s->mirror_indices[i]=other;s->mirror_indices[other]=i;}
    }
    return 1;
}
