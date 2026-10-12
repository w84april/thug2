/* Test-only heap/file/GPU storage. These are platform ports, not recovered game. */
#include "../../tools/script_values_memory.c"
#define BASE 0x1800000u
#define CONTROL (BASE+0x12000)
#define GPU_LOG (BASE+0x14000)
#define TEXTURES (BASE+0x100000)
#define TEXTURE_METHODS (BASE+0x11200)
#define IO_CONTROL (BASE+0x32000)
#define IO_LOG (BASE+0x33000)
#define FILE_HANDLE (BASE+0x1000)
#define FILE_NAME (BASE+0x2000)
#define INPUT_DATA (BASE+0xa000)
static uint32_t *at(uint32_t p){return (uint32_t *)(uintptr_t)p;}
static void put(uint32_t p,uint32_t v){__builtin_memcpy((void *)(uintptr_t)p,&v,4);}
void *fixture_tag_allocate(uint32_t *c,uint32_t size,uint32_t route){
 if(c[12]&&!--c[12]){record(c,1,size,route,0);return 0;}
 void *p=fixture_values_allocate(c,size,route);put((uintptr_t)p-16,BASE+0x600);
 if(c[9]&&c[10]==size){put(c[9],c[11]);c[9]=0;}return p;
}
uint32_t fixture_tag_scope(const void *p){if(word((uintptr_t)p-16)!=BASE+0x600)__builtin_trap();return 1;}
static uint32_t *event(uint32_t op){
 uint32_t *c=at(CONTROL);if(c[0]>=200)__builtin_trap();uint32_t *log=at(GPU_LOG+c[0]++*64);
 for(unsigned i=0;i<16;i++)log[i]=0;log[0]=op;log[15]=word(BASE+0x208);return log;
}
uint32_t fixture_tag_create(uint32_t device,uint32_t w,uint32_t h,uint32_t mips,uint32_t usage,uint32_t format,uint32_t pool,uint32_t output,uint32_t shared){
 uint32_t *c=at(CONTROL);if(c[1]>=6)__builtin_trap();uint32_t p=TEXTURES+c[1]++*0x20000;
 uint32_t *log=event(1);uint32_t args[]={device,w,h,mips,usage,format,pool,output,shared,p};for(unsigned i=0;i<10;i++)log[1+i]=args[i];put(p,TEXTURE_METHODS);put(p+4,mips);put(p+8,word(CONTROL+12));put(p+12,0);
 for(unsigned level=0;level<4;level++){uint32_t *d=at(p+0x20+level*32);for(unsigned k=0;k<8;k++)d[k]=0;d[0]=format;d[6]=w>>level;d[7]=h>>level;}
 put(output,p);return 0;
}
uint32_t fixture_tag_lock(uint32_t p,uint32_t level,uint32_t output,uint32_t rect,uint32_t flags){
 if(level>=4)__builtin_trap();uint32_t bytes=p+0x100+level*0x4000,pitch=word(p+8);if(!pitch)pitch=word(CONTROL+8);
 uint32_t *log=event(2);uint32_t args[]={p,level,rect,flags,pitch,bytes};for(unsigned i=0;i<6;i++)log[1+i]=args[i];put(output,pitch);put(output+4,bytes);return 0;
}
uint32_t fixture_tag_unlock(uint32_t p,uint32_t level){uint32_t *log=event(3);log[1]=p;log[2]=level;return 0;}
uint32_t fixture_tag_levels(uint32_t p){uint32_t n=word(p+4),*log=event(4);log[1]=p;log[2]=n;return n;}
uint32_t fixture_tag_description(uint32_t p,uint32_t level,uint32_t output){
 if(level>=4)__builtin_trap();uint32_t *log=event(5);log[1]=p;log[2]=level;for(unsigned i=0;i<8;i++){uint32_t v=word(p+0x20+level*32+i*4);put(output+i*4,v);log[3+i]=v;}return 0;
}
uint32_t fixture_tag_release(uint32_t p){uint32_t *log=event(6);log[1]=p;put(p+12,word(p+12)+1);return 0;}
uint32_t fixture_tag_bind(uint32_t device,uint32_t stage,uint32_t texture){uint32_t *log=event(7);log[1]=device;log[2]=stage;log[3]=texture;return 0;}
static void io_record(uint32_t op,uint32_t a,uint32_t b,uint32_t c,uint32_t d){
 uint32_t *ctl=at(IO_CONTROL);if(ctl[0]>=100)__builtin_trap();uint32_t *log=at(IO_LOG+ctl[0]++*20);log[0]=op;log[1]=a;log[2]=b;log[3]=c;log[4]=d;
}
uint32_t fixture_tag_open(const char *name,const char *mode){
 const char *expected=(const char *)(uintptr_t)FILE_NAME;unsigned i=0;do{if(name[i]!=expected[i]||i>=255)__builtin_trap();}while(expected[i++]);
 if(mode[0]!='r'||mode[1]!='b'||mode[2])__builtin_trap();uint32_t present=word(IO_CONTROL+4);put(FILE_HANDLE,INPUT_DATA);io_record(1,present,0,0,0);return present?FILE_HANDLE:0;
}
uint32_t fixture_tag_read(void *out,uint32_t width,uint32_t count,uint32_t file){
 if(file!=FILE_HANDLE)__builtin_trap();uint32_t start=word(file),size=width*count,end=word(file+4);if(start<INPUT_DATA||size>end-start)__builtin_trap();uint32_t dest=(uintptr_t)out;
 io_record(2,width,count,start,dest>=BASE&&dest<BASE+0x400000?dest:0);__builtin_memcpy(out,(void *)(uintptr_t)start,size);put(file,start+size);return count;
}
uint32_t fixture_tag_close(uint32_t file){if(file!=FILE_HANDLE)__builtin_trap();io_record(3,file,0,0,0);return 1;}
