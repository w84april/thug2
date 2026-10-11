/* Comparison-only bounded file stream; original read grouping is observable. */
#include "vertex-upload-ports.c"
#define BASE 0x1800000u
#define IO_CONTROL (BASE+0x1a000)
#define IO_LOG (BASE+0x30000)
static void file_event(uint32_t kind,uint32_t file,uint32_t width,uint32_t count,uint32_t start){
    uint32_t n=word(IO_CONTROL);if(n>=2000)__builtin_trap();put(IO_CONTROL,n+1);
    uint32_t *log=(void *)(uintptr_t)(IO_LOG+n*24);log[0]=kind;log[1]=file;log[2]=width;log[3]=count;log[4]=start;log[5]=word(file);
}
uint32_t fixture_scene_read(uint32_t out,uint32_t width,uint32_t count,uint32_t file){
    uint32_t start=word(file),n=width*count;if(start<BASE||start+n>BASE+0x100000||start+n<start)__builtin_trap();
    __builtin_memcpy((void *)(uintptr_t)out,(void *)(uintptr_t)start,n);put(file,start+n);file_event(1,file,width,count,start);return n;
}
uint32_t fixture_scene_seek(uint32_t file,int32_t offset,uint32_t origin){
    uint32_t start=word(file);if(origin!=1)__builtin_trap();put(file,start+offset);file_event(2,file,(uint32_t)offset,origin,start);return word(file);
}
