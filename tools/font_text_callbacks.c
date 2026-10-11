/* Test-only Windows services. Encoding is configurable fixture behavior,
 * not an implementation of a browser keyboard or Windows code page. */
#include <stdint.h>
#define C ((uint32_t *)(uintptr_t)0x1801000)
static uint32_t *record(uint32_t kind) {
    uint32_t *r=(uint32_t *)(uintptr_t)(0x1802000+C[0]++*64);
    for(unsigned i=0;i<16;++i)r[i]=0;
    r[0]=kind; return r;
}
int32_t fixture_text_wide(uint32_t cp,uint32_t flags,const uint16_t *in,int32_t count,char *out,int32_t capacity,const char *fallback,int32_t *used) {
    uint32_t *r=record(0),n=0,hash=0,needed=0;
    while(count<0 || n<(uint32_t)count) { uint16_t c=in[n++];hash=hash*33+c; if(count<0 && !c)break; }
    r[1]=cp;r[2]=flags;r[3]=(uint32_t)count;r[4]=out!=0;r[5]=(uint32_t)capacity;r[6]=fallback!=0;r[7]=used!=0;r[8]=hash;r[9]=n;
    int32_t substituted=0;
    for(uint32_t i=0;i<n;++i) {
        uint16_t c=in[i];
        if(C[1]==1 && c>=128)needed+=2;
        else {++needed;if(c>255)substituted=1;}
    }
    *used=substituted;
    int32_t result=(int32_t)needed;
    if(C[3]) {result=0;C[2]=87;}
    else if(out && (capacity<0 || (uint32_t)capacity<needed)) {result=0;C[2]=122;}
    else if(out) {
        uint32_t k=0;
        for(uint32_t i=0;i<n;++i) {
            uint16_t c=in[i];
            if(C[1]==1 && c>=128) {out[k++]=(char)(0xc0|(c>>6));out[k++]=(char)(0x80|(c&63));}
            else out[k++]=(char)(c>255?'?':c);
        }
    }
    r[10]=(uint32_t)result;r[11]=(uint32_t)*used;r[12]=C[2];
    return result;
}
uint32_t fixture_text_last_error(void) {
    uint32_t *r=record(1);r[1]=C[2];return C[2];
}
uint32_t fixture_text_map(uint32_t code,uint32_t mode) {
    uint32_t *r=record(2);r[1]=code;r[2]=mode;
    uint32_t result=mode==1?code+0x100:((code*7+C[4])&255)|0x80000000u;
    r[3]=result;return result;
}
