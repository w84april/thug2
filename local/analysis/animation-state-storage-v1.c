/* 0047f150/0047ea80: initialized Animation state storage and channel flag.
 * Identity tables do not establish configuration, clip loading or dispatch. */
#include "../../src/core/memory.h"
#include "../../src/script/runtime.h"
extern void thug_gap_list_clear_draft(void *,const ThugMemory *);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
const uint32_t thug_animation_state_pending_methods_v1[7]={0};
const uint32_t thug_animation_state_links_pending_methods_v1[1]={0};
void *thug_animation_state_construct_storage_v1(void *p,void *owner,void *component,uint32_t flag,const ThugMemory *m){
 void *list=(char *)p+0x14;
 put(p,4,(uintptr_t)p);put(p,8,0);put(p,12,(uintptr_t)p);put(p,16,(uintptr_t)p);
 put(p,0,(uintptr_t)thug_animation_state_pending_methods_v1);
 put(p,0x18,0xffffffff);put(p,0x1c,0);put(p,0x20,(uintptr_t)list);put(p,0x24,(uintptr_t)list);
 put(list,0,(uintptr_t)thug_animation_state_links_pending_methods_v1);
 ((uint8_t *)p)[0x4d]=1;put(p,0x68,(uintptr_t)owner);put(p,0x6c,(uintptr_t)component);
 put(p,0x50,0);put(p,0x58,0);put(p,0x28,0);put(p,0x2c,0);((uint8_t *)p)[0x4c]=0;put(p,0x40,0);put(p,0x3c,0);
 for(unsigned at=0x30;at<=0x38;at+=4)put(p,at,(uint8_t)flag?0x3f800000:0);
 thug_gap_list_clear_draft(list,m);((uint8_t *)p)[0x44]=0;put(p,0x48,0);
 if(((uint8_t *)p)[0x60]){((uint8_t *)p)[0x60]=0;ThugScriptInstance *script=(void *)(uintptr_t)word(owner,0x10);if(script)thug_script_clear_wait(script);}
 put(p,0x64,0);put(p,0x5c,0);((uint8_t *)p)[0x4e]=0;return p;
}
/* The original dereferences the head's marker before checking for null.
 * A valid mapped nonnull list head is required by this scoped routine. */
void thug_animation_state_enable_channel_events_v1(void *p,uint32_t flag){
 void *head=(void *)(uintptr_t)word(p,0x20);
 if(word(head,4)!=0xffffffff&&head){((uint8_t *)p)[0x4d]=(uint8_t)flag;((uint8_t *)head)[0x70]=(uint8_t)flag;}
}
