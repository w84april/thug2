#include "animation_cache.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>

ThugAnimationCacheManager *thug_animation_cache_manager;
uint32_t thug_animation_cache_pool_index;
ThugFixedPool *thug_animation_cache_pools[2];
uint16_t thug_animation_rotation_table[256][4],thug_animation_translation_table[256][4];
uint32_t thug_animation_tick_counter[2],thug_animation_cache_tick[2],thug_animation_cache_build_count;
_Static_assert(sizeof(ThugAnimationCacheReader)==0x1e4,"Cache reader layout");
_Static_assert(sizeof(ThugAnimationCacheManager)==0xe0,"Cache manager layout");
_Static_assert(offsetof(ThugAnimationCacheBlock,flags)==0x164,"Cache block flags");
_Static_assert(offsetof(ThugKeyframeAnimation,references)==0x3a,"Animation references");
static void zero_bytes(void *p,uint32_t size) { uint8_t *bytes=p;for(uint32_t i=0;i<size;i++)bytes[i]=0; }
static void copy_bytes(uint8_t *out,const uint8_t *in,uint32_t size) { for(uint32_t i=0;i<size;i++)out[i]=in[i]; }
static uint16_t half(const void *p) { uint16_t n;__builtin_memcpy(&n,p,2);return n; }
static void set_half(void *p,uint16_t n) { __builtin_memcpy(p,&n,2); }
static void set_float(void *p,float n) { __builtin_memcpy(p,&n,4); }
static double rounded(double n) { return thug_platform_round_x87_single(n); }

/* 0x005be8e0. This tick is distinct from the frame-rate timer counter. */
uint64_t thug_animation_tick(void) { return (uint64_t)thug_animation_tick_counter[1]<<32|thug_animation_tick_counter[0]; }
/* 0x00482c20. The byte loads and halfword stores deliberately remain ordered:
 * packed input, dictionary and output may overlap. */
const uint8_t *thug_animation_decode_rotation(const uint8_t *p,void *output,uint32_t flags,const uint8_t *table) {
    uint8_t *out=output;uint16_t first=0,header;
    if(flags&0x100) { first=half(p);header=half(p+2);p+=4; }
    else { header=half(p);p+=2; }
    set_half(out,flags&0x100?(header&0x8000)|(first&0x7fff):header);
    if(header&0x4000) {
        if(!(header&0x3800)) {
            uint32_t index=*p++;
            const uint8_t *entry=flags&0x2000?table+index*6:(const uint8_t *)thug_animation_rotation_table+index*8;
            for(uint32_t i=0;i<3;i++)set_half(out+2+i*2,half(entry+i*2));
        } else {
            for(uint32_t i=0;i<3;i++) {
                uint16_t value;
                if(header&(0x2000u>>i)) {
                    uint32_t index=*p++;
                    value=flags&0x10000?half((const uint8_t *)thug_animation_rotation_table+index*8+6):(uint16_t)index;
                } else if(flags&0x8000) value=(uint16_t)*p++<<8;
                else { value=half(p);p+=2; }
                set_half(out+2+i*2,value);
            }
        }
        set_half(out,half(out)&0x87ff);
    } else for(uint32_t i=0;i<3;i++) {
        uint16_t value;
        if(flags&0x8000)value=(uint16_t)*p++<<8;
        else { value=half(p);p+=2; }
        set_half(out+2+i*2,value);
    }
    if(flags&0x100)set_half(out,(half(out)&0x8000)|(first&0x7fff));
    return p;
}
/* 0x00482e70. The third argument is unused. */
const uint8_t *thug_animation_decode_translation(const uint8_t *p,void *output,uint32_t unused) {
    (void)unused;uint8_t *out=output,header=*p++;
    if(header&0x40)set_half(out,header&0x3f);
    else { set_half(out,half(p));p+=2; }
    if(header&0x80) {
        const uint8_t *entry=(const uint8_t *)thug_animation_translation_table+*p*8;
        for(uint32_t i=0;i<3;i++)set_half(out+2+i*2,half(entry+i*2));
        ++p;
    } else {
        for(uint32_t i=0;i<3;i++)set_half(out+2+i*2,half(p+i*2));
        p+=6;
    }
    return p;
}
static void copy_header(uint8_t *out,const uint8_t *in) {
    uint16_t v=(half(out)&0x7fff)|(half(in)&0x8000);
    set_half(out,v);
    set_half(out,(v&0x8000)|(half(in)&0x7fff));
}
/* 0x00482a70. Padding at output+2 is not initialized. */
void thug_animation_expand_rotation(void *output,const void *input) {
    uint8_t *out=output;const uint8_t *in=input;copy_header(out,in);
    for(uint32_t i=0;i<3;i++)set_float(out+4+i*4,(float)(int16_t)half(in+2+i*2)*0x1p-14f);
}
/* 0x00483d00. Capture XYZ before writing; read the sign after XYZ stores. */
void thug_animation_expand_quaternion(void *output,const void *input) {
    uint8_t *out=output;const uint8_t *in=input;copy_header(out,in);
    int32_t a=(int16_t)half(in+2),b=(int16_t)half(in+4),c=(int16_t)half(in+6);
    if(!a&&!b&&!c) { set_float(out+12,0);set_float(out+8,0);set_float(out+4,0);set_float(out+16,1);return; }
    float x=(float)a*0x1p-14f,y=(float)b*0x1p-14f,z=(float)c*0x1p-14f;
    double w=rounded(1-rounded((double)x*x));
    w=rounded(w-rounded((double)y*y));w=rounded(w-rounded((double)z*z));
    if(w<0)w=0;
    w=rounded(__builtin_sqrt(w));
    set_float(out+4,x);set_float(out+8,y);set_float(out+12,z);
    if(half(in)&0x8000)w=-w;
    set_float(out+16,(float)w);
}
/* 0x00480660, 0x00480800, 0x004805e0..0x00480640. */
ThugAnimationCacheManager *thug_animation_cache_instance(void) { return thug_animation_cache_manager; }
uint32_t thug_animation_cache_format(const ThugAnimationCacheManager *m) { return m->format; }
uint8_t thug_animation_cache_rotation_stride(const ThugAnimationCacheBlock *b) { return b->rotation_stride; }
uint8_t thug_animation_cache_translation_stride(const ThugAnimationCacheBlock *b) { return b->translation_stride; }
uint8_t *thug_animation_cache_rotations(const ThugAnimationCacheBlock *b,uint32_t unused) { (void)unused;return b->rotations; }
uint8_t *thug_animation_cache_translations(const ThugAnimationCacheBlock *b,uint32_t unused) { (void)unused;return b->translations; }
uint16_t *thug_animation_cache_rotation_offsets(ThugAnimationCacheBlock *b) { return b->rotation_offsets; }
uint16_t *thug_animation_cache_translation_offsets(ThugAnimationCacheBlock *b) { return b->translation_offsets; }
void thug_animation_cache_set_cleanup(ThugAnimationCacheBlock *b,void (*fn)(void *),void *context) { b->cleanup=fn;b->context=context; }
static uint32_t rotation_size(uint32_t format) { return format==2?8:format==3?16:format==4?20:0; }
static uint32_t translation_size(uint32_t format) { return format==2?8:format==3||format==4?16:0; }
/* 0x00480670. Even an exact multiple receives another alignment unit. */
uint32_t thug_animation_cache_allocation_size(const ThugAnimationCacheManager *m,uint32_t unused,uint32_t rotations,uint32_t translations,uint32_t format) {
    (void)unused;uint32_t bytes=rotation_size(format)*rotations+translation_size(format)*translations;
    return (bytes/m->alignment+1)*m->alignment;
}
/* 0x00480a70. */
void thug_animation_cache_reader_free(ThugAnimationCacheReader *reader,const ThugMemory *memory) {
    ThugFixedPool *pool=thug_animation_cache_pools[thug_animation_cache_pool_index];
    if(pool&&thug_pool_contains(pool,reader)) { thug_pool_release(pool,reader);return; }
    pool=thug_animation_cache_pools[thug_animation_cache_pool_index^1];
    if(pool&&thug_pool_contains(pool,reader))thug_pool_release(pool,reader);
    else memory->release(memory->context,reader);
}
static void clear_reader(ThugAnimationCacheReader *reader) {
    zero_bytes(reader->first,sizeof(reader->first));zero_bytes(reader->second,sizeof(reader->second));reader->flags=0x8000;
}
/* 0x00480ad0. Bit 14 must be clear on entry: the original spin loop caches
 * that bit in a register, so another thread cannot release it. */
uint32_t thug_animation_cache_clear(ThugAnimationCacheBlock *b,const ThugMemory *memory) {
    uint16_t busy=b->flags&0x4000;while(busy) { }
    b->flags|=0x8000;
    if(b->cleanup) { b->cleanup(b->context);b->cleanup=0; }
    uint32_t size=b->allocated;
    b->flags&=0x8000;b->rotations=0;b->translations=0;b->animation=0;b->bone_count=0;
    b->rotation_stride=0;b->translation_stride=0;b->payload=0;b->allocated=0;
    if(b->storage) { memory->temp_scope(memory->context,7);memory->release(memory->context,b->storage);memory->temp_scope(memory->context,0);b->storage=0; }
    for(uint32_t i=0;i<18;i++)if(b->readers[i]) {
        clear_reader(b->readers[i]);
        if(b->readers[i])thug_animation_cache_reader_free(b->readers[i],memory);
        b->readers[i]=0;
    }
    b->format=0;return size;
}
/* 0x00480bf0. Allocation success is an original internal contract. */
uint32_t thug_animation_cache_pin_block(ThugAnimationCacheBlock *b,const ThugMemory *memory) {
    uint32_t i=0;while(i<18&&b->readers[i])++i;
    if(i==18)return UINT32_MAX;
    ThugFixedPool *pool=thug_animation_cache_pools[thug_animation_cache_pool_index];
    ThugAnimationCacheReader *reader=pool?thug_pool_allocate(pool):memory->allocate(memory->context,0x1e4,1);
    if(reader)reader->flags=0x8000;
    b->readers[i]=reader;reader->flags&=0x7fff;
    zero_bytes(b->readers[i]->first,sizeof(reader->first));zero_bytes(b->readers[i]->second,sizeof(reader->second));return i;
}
/* 0x00480c90. Reader zero stays resident when its reference is released. */
void thug_animation_cache_unpin_block(ThugAnimationCacheBlock *b,int32_t i,const ThugMemory *memory) {
    if(!(b->flags&0x1fff))return;
    if(b->readers[i]&&i>0) {
        clear_reader(b->readers[i]);if(b->readers[i])thug_animation_cache_reader_free(b->readers[i],memory);b->readers[i]=0;
    }
    b->flags=(b->flags&0xe000)|((b->flags-1)&0x1fff);
}
/* 0x00480df0. */
void thug_animation_cache_remove(ThugAnimationCacheManager *m,ThugKeyframeAnimation *animation,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++)if(m->blocks[i]->animation==animation) { --m->count;m->bytes-=thug_animation_cache_clear(m->blocks[i],memory); }
}
/* 0x00480db0. The original does not decrement the manager count here. */
void thug_animation_cache_flush(ThugAnimationCacheManager *m,uint32_t only_unpinned,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++) {
        ThugAnimationCacheBlock *b=m->blocks[i];
        if(b->format&&(!(uint8_t)only_unpinned||!(b->flags&0x1fff)))m->bytes-=thug_animation_cache_clear(b,memory);
    }
}
/* 0x00480e30. */
uint32_t thug_animation_cache_pin(ThugAnimationCacheManager *m,ThugKeyframeAnimation *animation,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++)if(m->blocks[i]->animation==animation) {
        ThugAnimationCacheBlock *b=m->blocks[i];uint32_t result=thug_animation_cache_pin_block(b,memory);
        if(result!=UINT32_MAX)b->flags=(b->flags&0xe000)|((b->flags+1)&0x1fff);
        return result;
    }
    return UINT32_MAX;
}
/* 0x00480e80. */
void thug_animation_cache_unpin(ThugAnimationCacheManager *m,ThugKeyframeAnimation *animation,int32_t index,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++)if(m->blocks[i]->animation==animation) {
        thug_animation_cache_unpin_block(m->blocks[i],index,memory);
        if(!(m->blocks[i]->flags&0x1fff)&&m->evict_on_unpin)thug_animation_cache_remove(m,animation,memory);
    }
}
/* 0x00480940. The port's scope and availability callbacks replace heap services. */
uint32_t thug_animation_cache_available(ThugAnimationCacheManager *m,const ThugMemory *memory) {
    (void)m;memory->temp_scope(memory->context,7);uint32_t n=memory->available(memory->context);memory->temp_scope(memory->context,0);return n;
}
/* 0x00480810. Failure retains the already-written sizes and busy flag. */
uint32_t thug_animation_cache_allocate(ThugAnimationCacheBlock *b,ThugKeyframeAnimation *animation,uint32_t bones,uint32_t rotations,uint32_t translations,uint32_t format,const ThugMemory *memory) {
    b->flags|=0x8000;b->bone_count=(uint16_t)bones;b->format=format;
    b->rotation_stride=(uint8_t)rotation_size(format);b->translation_stride=(uint8_t)translation_size(format);
    uint32_t bytes=b->rotation_stride*rotations+b->translation_stride*translations;
    b->payload=bytes;b->allocated=(bytes/thug_animation_cache_manager->alignment+1)*thug_animation_cache_manager->alignment;
    memory->temp_scope(memory->context,7);uint32_t size=b->allocated;
    if(memory->available(memory->context)<size) { b->format=0;memory->temp_scope(memory->context,0);return 0; }
    b->animation=animation;b->storage=memory->allocate(memory->context,size,1);zero_bytes(b->storage,b->allocated);
    b->rotations=b->storage;b->translations=b->storage+b->rotation_stride*rotations;
    memory->temp_scope(memory->context,0);b->flags&=0x3fff;b->timestamp=0;return b->allocated;
}
/* 0x00480980. Search stops at the first matching asset OR free slot. */
ThugAnimationCacheBlock *thug_animation_cache_add(ThugAnimationCacheManager *m,ThugKeyframeAnimation *animation,uint32_t bones,uint32_t rotations,uint32_t translations,uint32_t format,const ThugMemory *memory) {
    for(uint32_t i=0;i<50;i++) {
        ThugAnimationCacheBlock *b=m->blocks[i];if(b->animation==animation)return 0;
        if(!b->format) {
            uint32_t size=thug_animation_cache_allocate(b,animation,bones,rotations,translations,format,memory);m->bytes+=size;
            if(!size)return 0;
            ++m->count;return m->blocks[i];
        }
    }
    return 0;
}
/* 0x004806c0. Strict unsigned timestamps select the first oldest eligible slot. */
ThugKeyframeAnimation *thug_animation_cache_oldest(ThugAnimationCacheManager *m,uint32_t minimum,uint32_t *references) {
    uint32_t oldest=thug_frame_time();ThugKeyframeAnimation *result=0;
    for(uint32_t i=0;i<50;i++) {
        ThugAnimationCacheBlock *b=m->blocks[i];
        if(b->allocated>=minimum&&b->timestamp<oldest&&!(b->flags&0x2000)) {
            *references=b->flags&0x1fff;oldest=b->timestamp;result=b->animation;
        }
    }
    return result;
}
/* 0x00480ed0. */
uint8_t thug_animation_cache_evict(ThugAnimationCacheManager *m,uint32_t priority,uint32_t minimum,const ThugMemory *memory) {
    uint32_t references=999;ThugKeyframeAnimation *a=thug_animation_cache_oldest(m,minimum,&references);
    if(priority>references&&a) { thug_animation_cache_remove(m,a,memory);return 1; }return 0;
}
/* 0x00482ba0, 0x00482bd0. Packed count occupies bits 1..8. */
uint32_t thug_keyframe_animation_pin(ThugKeyframeAnimation *a,const ThugMemory *memory) {
    a->references=(a->references&~0x1fe)|((a->references+2)&0x1fe);
    return thug_animation_cache_pin(thug_animation_cache_instance(),a,memory);
}
void thug_keyframe_animation_unpin(ThugKeyframeAnimation *a,int32_t index,const ThugMemory *memory) {
    if((int16_t)((a->references&~1u)<<7)>0) {
        a->references=(a->references&~0x1fe)|(((a->references&~1u)-1)&0x1fe);
        thug_animation_cache_unpin(thug_animation_cache_instance(),a,index,memory);
    }
}
/* 0x00482b90. Actual callback registered by the cache builder. */
void thug_keyframe_animation_cache_cleared(void *p) { if(p)((ThugKeyframeAnimation *)p)->cache=0; }

/* 0x00485270. Decode both packed streams into per-bone contiguous records.
 * Original internal contracts: valid length tables and output buffers, successful
 * allocation, and matching stream boundaries. Offset tables intentionally wrap. */
void thug_keyframe_animation_build_cache(ThugKeyframeAnimation *a,uint32_t format,const ThugMemory *memory) {
    uint64_t previous=(uint64_t)thug_animation_cache_tick[1]<<32|thug_animation_cache_tick[0];
    uint64_t now=thug_animation_tick();if(thug_animation_cache_build_count>=10&&now==previous)return;
    if(now!=previous) { thug_animation_cache_build_count=0;now=thug_animation_tick();thug_animation_cache_tick[0]=(uint32_t)now;thug_animation_cache_tick[1]=(uint32_t)(now>>32); }
    ThugAnimationCacheManager *m=thug_animation_cache_instance();
    uint32_t needed=thug_animation_cache_allocation_size(m,a->bone_count,(uint32_t)(int32_t)a->rotation_count,(uint32_t)(int32_t)a->translation_count,format);
    if(m->count==50||thug_animation_cache_available(m,memory)<needed) {
        uint32_t priority=(uint32_t)((int16_t)(a->references<<7)>>8);
        if(thug_animation_cache_evict(m,priority,needed,memory))a->cache=0;
    }
    ThugAnimationCacheBlock *b=thug_animation_cache_add(m,a,a->bone_count,(uint32_t)(int32_t)a->rotation_count,(uint32_t)(int32_t)a->translation_count,format,memory);
    if(!b)return;
    uint16_t *rotation_offsets=thug_animation_cache_rotation_offsets(b),*translation_offsets=thug_animation_cache_translation_offsets(b);
    uint32_t rotation_stride=thug_animation_cache_rotation_stride(b),translation_stride=thug_animation_cache_translation_stride(b),bones=a->bone_count;
    const uint16_t *lengths=a->rotation_lengths;const uint8_t *p=a->rotation_keys,*end=p+*lengths;
    uint8_t *rotations=thug_animation_cache_rotations(b,0),*translations=thug_animation_cache_translations(b,0);
    uint32_t index=0,offset=0;rotation_offsets[0]=0;translation_offsets[0]=0;
    /* The packed rotation key and expanded translation record reuse one
     * original stack slot. Its last X halfword survives as translation padding.
     * Truly unwritten automatic padding is explicitly initialized to zero. */
    uint8_t shared[16]={0};
    while(index<bones) {
        while(!*lengths) { end=p+*++lengths;rotation_offsets[(uint16_t)++index]=(uint16_t)offset;if((uint16_t)index==bones)break; }
        if((uint16_t)index==bones)break;
        uint8_t expanded[20]={0};p=thug_animation_decode_rotation(p,shared,a->flags,a->rotation_table);
        const uint8_t *record=shared;
        if(format==3) { thug_animation_expand_rotation(expanded,shared);record=expanded; }
        else if(format==4) { thug_animation_expand_quaternion(expanded,shared);record=expanded; }
        copy_bytes(rotations+(uint16_t)offset,record,rotation_stride);offset+=rotation_stride;
        if(p==end) { end=p+*++lengths;rotation_offsets[(uint16_t)++index]=(uint16_t)offset; }
    }
    lengths=a->translation_lengths;p=a->translation_keys;end=p+*lengths;index=0;offset=0;
    while(index<bones) {
        while(!*lengths) { end=p+*++lengths;translation_offsets[(uint16_t)++index]=(uint16_t)offset;if((uint16_t)index==bones)break; }
        if((uint16_t)index==bones)break;
        uint8_t key[8];p=thug_animation_decode_translation(p,key,a->flags);
        const uint8_t *record=key;
        if(format>=3&&format<=4) {
            set_half(shared,half(key));for(uint32_t i=0;i<3;i++)set_float(shared+4+i*4,(float)(int16_t)half(key+2+i*2)*0.03125f);record=shared;
        }
        copy_bytes(translations+(uint16_t)offset,record,translation_stride);offset+=translation_stride;
        if(p==end) { end=p+*++lengths;translation_offsets[(uint16_t)++index]=(uint16_t)offset; }
    }
    a->cache=b;thug_animation_cache_set_cleanup(b,thug_keyframe_animation_cache_cleared,a);
    a->cache->flags=(a->cache->flags&~0x2000)|((a->flags>>11&1)<<13);
    ++thug_animation_cache_build_count;now=thug_animation_tick();thug_animation_cache_tick[0]=(uint32_t)now;thug_animation_cache_tick[1]=(uint32_t)(now>>32);
}
