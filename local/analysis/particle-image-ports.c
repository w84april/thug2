/* Comparison-only bounded heap, resident-file and GPU storage ports. */
#include "particle-image-gpu-ports.c"
#define IO_CONTROL (BASE+0x32000)
#define IO_LOG (BASE+0x33000)
#define FILE_HANDLE (BASE+0x1000)
#define FILE_NAME (BASE+0x2000)
#define INPUT_DATA (BASE+0xa000)
static void io_record(uint32_t op,uint32_t a,uint32_t b,uint32_t c,uint32_t d){
 uint32_t *ctl=at(IO_CONTROL);if(ctl[0]>=100)__builtin_trap();uint32_t *log=at(IO_LOG+ctl[0]++*20);log[0]=op;log[1]=a;log[2]=b;log[3]=c;log[4]=d;
}
uint32_t fixture_image_open(const char *name,const char *mode){
 const char *expected=(const char *)(uintptr_t)FILE_NAME;unsigned i=0;do{if(name[i]!=expected[i]||i>=255)__builtin_trap();}while(expected[i++]);
 if(mode[0]!='r'||mode[1]!='b'||mode[2])__builtin_trap();uint32_t present=word(IO_CONTROL+4);put(FILE_HANDLE,INPUT_DATA);
 io_record(1,present,0,0,0);return present?FILE_HANDLE:0;
}
uint32_t fixture_image_read(void *out,uint32_t width,uint32_t count,uint32_t file){
 if(file!=FILE_HANDLE)__builtin_trap();uint32_t start=word(file),size=width*count,end=word(file+4);
 if(start<INPUT_DATA||size>end-start)__builtin_trap();uint32_t dest=(uintptr_t)out;
 io_record(2,width,count,start,dest>=BASE&&dest<BASE+0x200000?dest:0);
 __builtin_memcpy(out,(void *)(uintptr_t)start,size);put(file,start+size);return count;
}
uint32_t fixture_image_close(uint32_t file){if(file!=FILE_HANDLE)__builtin_trap();io_record(3,file,0,0,0);return 1;}
