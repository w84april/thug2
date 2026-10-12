/* Camera QB initialization and bounded component links; no frame behavior. */
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/script/params.h"
#include "../../src/core/matrix.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *component(void *owner,uint32_t type){return thug_object_find_component(owner,type);}
/* 004fa3c0: null binding preserves the earlier mode word. */
void thug_skater_camera_bind_target_v1(void *p,void *target){
 put(p,0x170,(uintptr_t)target);put(p,0x174,target?(uintptr_t)component(target,0x43686585):0);put(p,0x178,target?(uintptr_t)component(target,0xd9151d4d):0);if(target)put(p,0x28,3);
}
/* 00524c50 */
void thug_skater_camera_roll_bind_target_v1(void *p,void *target){
 put(p,0x9c,(uintptr_t)target);put(p,0xa0,target?(uintptr_t)component(target,0x726e85aa):0);put(p,0xa4,target?(uintptr_t)component(target,0xd9151d4d):0);
}
/* 004e3f70: QB parameter is unused; retain the two adjacent bytes. */
void thug_skater_camera_object_initialize_v1(void *p,const ThugScriptStructure *params){
 (void)params;put(p,0x20,0);put(p,0x24,0);put(p,0x1c,0x3f800000);((unsigned char *)p)[0x18]=0;((unsigned char *)p)[0x19]=0;
}
/* 004e4040 */
void thug_skater_camera_object_finalize_v1(void *p){put(p,0x40,(uintptr_t)component((void *)(uintptr_t)word(p,12),0x27d7cd28));}
/* 00524fb0 */
void thug_skater_camera_roll_finalize_v1(void *p){
 void *owner=(void *)(uintptr_t)word(p,12);put(p,0x90,(uintptr_t)component(owner,0x81c7122d));put(p,0x94,(uintptr_t)component(owner,0xc4e311fa));put(p,0x98,(uintptr_t)component(owner,0x5e43a604));
}
/* 004fa5c0: required checksum getter retains its initial zero on failure. */
void thug_skater_camera_initialize_v1(void *p,const ThugScriptStructure *params){
 void *owner=(void *)(uintptr_t)word(p,12);for(unsigned i=0;i<16;i++)put(owner,0x6c+4*i,i%5==0?0x3f800000:0);
 for(unsigned i=0;i<12;i++)put(p,0x40+4*i,word(owner,0x6c+4*i));
 uint32_t id=0;thug_script_get_checksum_legacy(params,0x4c48da58,&id,1);thug_skater_camera_bind_target_v1(p,thug_object_find_global(0,id));
}
/* 00524f50: required checksum getter, then exact forward 16-word matrix copy. */
void thug_skater_camera_roll_initialize_v1(void *p,const ThugScriptStructure *params){
 uint32_t id=0;thug_script_get_checksum(params,0x4c48da58,&id,1);thug_skater_camera_roll_bind_target_v1(p,thug_object_find_global(0,id));
 put(p,0x74,0x3f800000);put(p,0x20,0x3f800000);thug_matrix_copy((float *)((char *)p+0x34),(float *)((char *)(uintptr_t)word(p,12)+0x6c));
}
