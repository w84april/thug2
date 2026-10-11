/* Original SkaterGap startup, state masks, per-frame cancellation and cleanup.
 * Gap start/end scoring and script commands remain explicitly unrecovered. */
#include "../../src/game/components.h"
#include "../../src/game/grind.h"
#include "../../src/game/stats.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
extern const ThugComponentMethods thug_skater_gap_pending_methods_draft;
extern const ThugTrickNodeMethods thug_gap_primary_sentinel_methods_draft,thug_gap_secondary_sentinel_methods_draft;
/* 00512240 and00512270. These wrappers call the original base unlinks before
 * testing the low flag byte; their concrete table identities remain distinct. */
ThugTrickNode *thug_gap_primary_sentinel_delete_draft(ThugTrickNode *p,uint32_t flags,const ThugMemory *m){
 thug_trick_primary_destroy(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
ThugTrickNode *thug_gap_secondary_sentinel_delete_draft(ThugTrickNode *p,uint32_t flags,const ThugMemory *m){
 thug_trick_secondary_destroy(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
const ThugTrickNodeMethods thug_gap_primary_sentinel_methods_draft={thug_gap_primary_sentinel_delete_draft};
const ThugTrickNodeMethods thug_gap_secondary_sentinel_methods_draft={thug_gap_secondary_sentinel_delete_draft};
/* 005122a0. Only the two first dependency links are cleared here. */
void *thug_skater_gap_construct_draft(void *p){
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_skater_gap_pending_methods_draft);
 void *s=(char *)p+0x18;put(s,0,(uintptr_t)&thug_gap_primary_sentinel_methods_draft);
 put(s,12,(uintptr_t)s);put(s,16,(uintptr_t)s);put(s,8,0);put(s,4,UINT32_MAX);
 s=(char *)p+0x2c;put(s,4,UINT32_MAX);put(s,8,0);put(s,12,(uintptr_t)s);put(s,16,(uintptr_t)s);
 put(s,0,(uintptr_t)&thug_gap_secondary_sentinel_methods_draft);put(p,4,0x11b4c67f);put(p,0x48,0);put(p,0x4c,0);return p;
}
/* 00512c60 and00511bb0. */
void *thug_skater_gap_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x58,m);return p?thug_skater_gap_construct_draft(p):0;}
void thug_skater_gap_initialize_draft(void *p,const ThugScriptStructure *s){(void)s;put(p,0x40,0);}
/* 00511bc0. Load the next owner before storing the preceding component link. */
void thug_skater_gap_finalize_draft(void *p){
 const uint32_t types[]={0x5bd63b29,0x589e5fb3,0xd9151d4d,0x726e85aa};
 void *owner=ptr(p,12),*found=thug_object_find_component(owner,types[0]);
 for(unsigned i=1;i<4;i++){owner=ptr(p,12);put(p,0x44+i*4,(uintptr_t)found);found=thug_object_find_component(owner,types[i]);}
 put(p,0x54,(uintptr_t)found);
}
/* 00511f10. Detach the two sentinels; this does not recursively free their nodes. */
void thug_skater_gap_destroy_draft(void *p){
 put(p,0,(uintptr_t)&thug_skater_gap_pending_methods_draft);
 thug_trick_secondary_destroy((void *)((char *)p+0x2c));
 thug_trick_primary_destroy((void *)((char *)p+0x18));thug_component_destroy(p);
}
/* 005122f0. */
void *thug_skater_gap_delete_draft(void *p,uint32_t flags,const ThugMemory *m){
 thug_skater_gap_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 00511c80. Clear-before-select writes and subsequent reloads also apply when
 * output slots alias each other or fields of the input graph. */
void thug_skater_gap_state_masks_draft(void *p,uint32_t *select,uint32_t *clear){
 put(clear,0,0);put(select,0,0);void *state=ptr(ptr(p,0x50),0x2c);uint32_t flag=0;
 if(!byte(state,0x118)){
  if(byte(state,0x118)||word(state,0x1c)){
   put(select,0,0x400);put(clear,0,word(clear,0)|0x4000000);
   switch(word(ptr(p,0x54),0x18)){case 0:flag=1;break;case 1:flag=2;break;case 2:flag=0x80;break;case 3:flag=0x100;break;}
  }else{
   put(select,0,0x200);put(clear,0,word(clear,0)|0x2000000);state=ptr(ptr(p,0x48),0x1528);
   switch(word(state,0x18)){
    case 0:{
     if(!byte(state,0x90)){
      void *balance=ptr(p,0x4c);
      if(!word(balance,0x18)&&!byte(balance,0x1c)){put(select,0,word(select,0)|1);put(clear,0,word(clear,0)|0x10000);}
     }
     void *balance=ptr(p,0x4c);if(word(balance,0x18)||byte(balance,0x1c))flag=0x40;break;
    }
    case 1:flag=2;break;case 2:flag=8;break;case 3:flag=0x10;break;case 4:flag=4;break;case 5:flag=0x20;break;
   }
  }
 }else{
  put(select,0,0x800);put(clear,0,word(clear,0)|0x8000000);
  void *owner=thug_object_find_global(0,0x824c6a24);
  void *vehicle=thug_object_find_component(owner,0xe47f1b79);flag=word(vehicle,0x114)?1:2;
 }
 if(flag){put(select,0,word(select,0)|flag);put(clear,0,word(clear,0)|(flag<<16));}
}
/* 00512320. Counter wraps before deriving state masks and cancelling gaps. */
void thug_skater_gap_update_draft(void *p,const ThugMemory *m){
 put(p,0x40,word(p,0x40)+1);uint32_t select,clear;
 thug_skater_gap_state_masks_draft(p,&select,&clear);thug_tricks_cancel(p,select,clear,m);
}
static void *first(void *node){return word(node,4)==UINT32_MAX?0:node;}
/* 005121a0. Capture next before disposal; the current-frame counter is reloaded
 * on each iteration when the preserve-current flag is present. */
void thug_skater_gap_clear_secondary_draft(void *p,const ThugScriptStructure *s,const ThugMemory *m){
 uint8_t preserve=thug_script_has_flag(s,0x97975226);void *node=first(ptr(p,0x38));
 while(node){void *next=first(ptr(node,12));
  if(!preserve||word(node,0x30)!=word(p,0x40))((const ThugTrickNodeMethods *)ptr(node,0))->dispose(node,1,m);
  node=next;
 }
}
static void frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;thug_skater_gap_update_draft(p,m);}
static uint32_t pending_command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){(void)p;(void)n;(void)s;(void)i;__builtin_trap();}
static void empty(void *p){(void)p;}
const ThugComponentMethods thug_skater_gap_pending_methods_draft={
 .dispose=thug_skater_gap_delete_draft,.update=frame,.initialize=thug_skater_gap_initialize_draft,.finalize=thug_skater_gap_finalize_draft,
 .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=pending_command};
