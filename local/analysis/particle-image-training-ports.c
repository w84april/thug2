/* Comparison-only resident files and texture storage, not a graphics renderer. */
#include "../../tools/script_loader_memory.c"
#define BASE 0x800000u
#define CONTROL (BASE+0xf1300)
#define IO_CONTROL (BASE+0xf2200)
#define IO_LOG (BASE+0x1700000)
#define GPU_LOG (BASE+0x1a00000)
#define TEXTURE_METHODS (BASE+0xf1200)
static void put(uint32_t p,uint32_t v){__builtin_memcpy((void *)(uintptr_t)p,&v,4);}
uint32_t fixture_training_scope(const void *p){uint32_t a=(uintptr_t)p;if(a<0x2400000||a>=0x4000000)__builtin_trap();put(CONTROL+12,word(CONTROL+12)+1);return 1;}
static uint32_t *event(uint32_t op){uint32_t n=word(CONTROL+8);if(n>=7000)__builtin_trap();put(CONTROL+8,n+1);uint32_t *p=(void *)(uintptr_t)(GPU_LOG+n*64);for(unsigned i=0;i<16;i++)p[i]=0;p[0]=op;return p;}
uint32_t fixture_training_create(uint32_t dev,uint32_t w,uint32_t h,uint32_t levels,uint32_t usage,uint32_t fmt,uint32_t pool,uint32_t out,uint32_t shared){
    if(!levels||levels>16)__builtin_trap();uint32_t p=word(CONTROL),next=p+256;put(p,TEXTURE_METHODS);put(p+4,levels);
    for(uint32_t l=0;l<levels;l++){
        uint32_t a=w>>l,b=h>>l;if(!a)a=1;if(!b)b=1;uint32_t pitch,n;
        if(fmt==0x31545844||fmt==0x35545844){pitch=((a+3)/4)*(fmt==0x31545844?8:16);n=pitch*((b+3)/4);}
        else{uint32_t depth=fmt==0x29?1:fmt==0x19?2:fmt==0x15?4:0;if(!depth)__builtin_trap();pitch=a*depth;n=pitch*b;}
        put(p+16+l*12,next);put(p+20+l*12,n);put(p+24+l*12,pitch);next=(next+n+15)&~15u;
    }
    if(next>=BASE+0x5800000)__builtin_trap();put(CONTROL,next);put(CONTROL+4,word(CONTROL+4)+1);put(out,p);
    uint32_t values[]={dev,w,h,levels,usage,fmt,pool,out,shared,p};uint32_t *log=event(1);for(unsigned i=0;i<10;i++)log[1+i]=values[i];return 0;
}
uint32_t fixture_training_lock(uint32_t p,uint32_t level,uint32_t out,uint32_t rect,uint32_t flags){
    if(level>=word(p+4))__builtin_trap();uint32_t data=word(p+16+level*12),n=word(p+20+level*12),pitch=word(p+24+level*12);
    put(out,pitch);put(out+4,data);uint32_t values[]={p,level,rect,flags,data,n,pitch};uint32_t *log=event(2);for(unsigned i=0;i<7;i++)log[1+i]=values[i];return 0;
}
uint32_t fixture_training_unlock(uint32_t p,uint32_t level){uint32_t *log=event(3);log[1]=p;log[2]=level;return 0;}
static void file_event(uint32_t kind,uint32_t file,uint32_t width,uint32_t count,uint32_t start){
    uint32_t n=word(IO_CONTROL);if(n>=125000)__builtin_trap();put(IO_CONTROL,n+1);uint32_t *log=(void *)(uintptr_t)(IO_LOG+n*24);
    log[0]=kind;log[1]=file;log[2]=width;log[3]=count;log[4]=start;log[5]=word(file);
}
uint32_t fixture_training_read(uint32_t out,uint32_t width,uint32_t count,uint32_t file){
    uint32_t start=word(file),n=width*count;if(start<BASE+0x1400000||start+n>word(file+4)||start+n<start)__builtin_trap();
    __builtin_memcpy((void *)(uintptr_t)out,(void *)(uintptr_t)start,n);put(file,start+n);file_event(1,file,width,count,start);return n;
}
uint32_t fixture_training_seek(uint32_t file,int32_t offset,uint32_t origin){uint32_t start=word(file);if(origin!=1)__builtin_trap();put(file,start+offset);file_event(2,file,offset,origin,start);return word(file);}

/* Bounded, distinct CRT and GPU-buffer regions; these are comparison ports. */
#define MESH_CONTROL (BASE+0xf2300)
#define BUFFER_METHODS (BASE+0xf2400)
void *fixture_training_crt(uint32_t size){
 uint32_t p=word(MESH_CONTROL),next=(p+size+19)&~3u;if(next>0x4800000u)__builtin_trap();
 put(MESH_CONTROL,next);put(MESH_CONTROL+8,word(MESH_CONTROL+8)+1);__builtin_memset((void *)(uintptr_t)p,0xa5,size);return (void *)(uintptr_t)p;
}
uint32_t fixture_training_buffer_create(uint32_t dev,uint32_t n,uint32_t usage,uint32_t format,uint32_t pool,uint32_t out,uint32_t shared){
 if(dev!=BASE+0xf1000||pool||shared)__builtin_trap();uint32_t p=word(MESH_CONTROL+4),next=(p+256+n+15)&~15u;
 if(next>0x5000000u)__builtin_trap();put(MESH_CONTROL+4,next);put(MESH_CONTROL+12,word(MESH_CONTROL+12)+1);
 put(p,BUFFER_METHODS);put(p+4,n);put(p+8,usage);put(p+12,format);put(out,p);return 0;
}
uint32_t fixture_training_buffer_lock(uint32_t p,uint32_t offset,uint32_t n,uint32_t out,uint32_t flags){
 if(offset+n>word(p+4)||flags)__builtin_trap();put(out,p+256+offset);put(MESH_CONTROL+16,word(MESH_CONTROL+16)+1);return 0;
}
uint32_t fixture_training_buffer_unlock(uint32_t p){if(word(p)!=BUFFER_METHODS)__builtin_trap();put(MESH_CONTROL+20,word(MESH_CONTROL+20)+1);return 0;}

static int same_name(const char *a,const char *b){for(unsigned i=0;i<256;i++){if(a[i]!=b[i])return 0;if(!b[i])return 1;}return 0;}
uint32_t fixture_training_open(uint32_t name,uint32_t mode){
 const char *a=(void *)(uintptr_t)name,*m=(void *)(uintptr_t)mode;uint32_t file,start;
 if(same_name(a,(void *)(BASE+0xf2100))){file=BASE+0xf2000;start=BASE+0x1400000;}
 else if(same_name(a,(void *)0x5f41100)){file=0x5f41000;start=0x5f40000;}else __builtin_trap();
 if(m[0]!='r'||m[1]!='b'||m[2])__builtin_trap();put(file,start);put(MESH_CONTROL+24,word(MESH_CONTROL+24)+1);return file;
}
uint32_t fixture_training_close(uint32_t file){if(file!=BASE+0xf2000&&file!=0x5f41000)__builtin_trap();put(MESH_CONTROL+28,word(MESH_CONTROL+28)+1);return 1;}

uint32_t fixture_training_buffer_add_ref(uint32_t p){if(word(p)!=BUFFER_METHODS)__builtin_trap();uint32_t n=word(p+16)+1;put(p+16,n);put(MESH_CONTROL+32,word(MESH_CONTROL+32)+1);return n;}

void *fixture_collision_factory_boundary(void *m){(void)m;volatile uint32_t *p=(void *)0x80e000;p[0]=0x41c920;p[1]=*(uint32_t *)0x80c010;p[2]=0x80c000;p[3]=1;__builtin_trap();}
