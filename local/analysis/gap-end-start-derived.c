/* Original gap creation, concrete list ownership and owned strings. */
#include "../../src/game/grind.h"
#include "../../src/game/stats.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/core/checksum.h"
#include "../../src/core/memory_state.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void *first(void *p){return word(p,4)==UINT32_MAX?0:p;}
static void dispose(void *p,const ThugMemory *m){((const ThugTrickNodeMethods *)ptr(p,0))->dispose(p,1,m);}
extern uint32_t thug_skater_serial_draft;
extern void *thug_skater_handle_construct_draft(void *);
extern void thug_skater_gap_state_masks_draft(void *,uint32_t *,uint32_t *);
extern uint32_t thug_score_preceding_named_draft(const void *,uint32_t,uint32_t,int32_t);
extern uint32_t thug_score_preceding_bound_draft(const void *,uint32_t,uint32_t,uint32_t);
/* 006f22b4/006f22bc. Other script-value pool contracts are unchanged. */
uint32_t thug_gap_array_pool_index_draft;
ThugFixedPool *thug_gap_array_pools_draft[2];
/* 00408fd0. Reload the selected index after a failed membership test. */
void thug_gap_array_free_draft(void *p,const ThugMemory *m){
 ThugFixedPool *pool=thug_gap_array_pools_draft[thug_gap_array_pool_index_draft];
 if(pool&&thug_pool_contains(pool,p)){thug_pool_release(pool,p);return;}
 pool=thug_gap_array_pools_draft[thug_gap_array_pool_index_draft^1];
 if(pool&&thug_pool_contains(pool,p))thug_pool_release(pool,p);else m->release(m->context,p);
}
/* 00401da0. The serial/live counter is decremented even for an empty string. */
void thug_owned_string_destroy_draft(void *p,const ThugMemory *m){
 void *s=ptr(p,4);if(s){m->release(m->context,s);put(p,4,0);}--thug_skater_serial_draft;
}
/* 00401dd0. Inclusive range and forward copy, with a freshly loaded destination
 * pointer each byte. Null/invalid ranges retain capacity; empty strings allocate
 * one byte but record capacity two. Heap initialization is a platform service. */
void thug_owned_string_range_draft(void *p,const char *text,int32_t start,int32_t end,const ThugMemory *m){
 if(!text||end<start){void *old=ptr(p,4);if(old){m->release(m->context,old);put(p,4,0);}return;}
 if(!text[start]){void *old=ptr(p,4);if(old)m->release(m->context,old);
  char *s=m->allocate(m->context,1,1);put(p,4,(uintptr_t)s);s[0]=0;put(p,8,2);return;}
 uint32_t capacity=(uint32_t)end-(uint32_t)start+2;if((int32_t)capacity<4)capacity=4;
 void *old=ptr(p,4);if(old&&(int32_t)capacity>(int32_t)word(p,8)){m->release(m->context,old);put(p,4,0);}
 if(!ptr(p,4)){put(p,8,capacity);put(p,4,(uintptr_t)thug_allocate_array_storage(capacity,m));}
 uint32_t written=0,i=(uint32_t)start;
 for(;;){char c=text[(int32_t)i];((char *)ptr(p,4))[written++]=c;i++;if((int32_t)i>end)break;}
 ((char *)ptr(p,4))[written]=0;
}
/* 00401ed0. Scan before modifying the receiver; return the receiver itself. */
void *thug_owned_string_assign_draft(void *p,const char *text,const ThugMemory *m){
 uint32_t end=0;if(text){while(text[end])end++;end--;if((int32_t)end<0)end=0;}
 thug_owned_string_range_draft(p,text,0,(int32_t)end,m);return p;
}
extern const ThugTrickNodeMethods thug_gap_primary_node_methods_draft,thug_gap_secondary_node_methods_draft;
/* 00578740. Only the documented fields are initialized; array padding survives. */
void *thug_gap_primary_node_construct_draft(void *p,const ThugMemory *m){
 put(p,4,(uintptr_t)p);put(p,8,0);put(p,12,(uintptr_t)p);put(p,16,(uintptr_t)p);
 put(p,0,(uintptr_t)&thug_gap_primary_node_methods_draft);put(p,0x20,0);put(p,0x24,0);put(p,0x30,0);((uint8_t *)p)[0x34]=0;
 ThugFixedPool *pool=thug_gap_array_pools_draft[thug_gap_array_pool_index_draft];
 ThugScriptArray *a=pool?thug_pool_allocate(pool):m->allocate(m->context,12,1);
 if(a)thug_script_array_initialize(a);put(p,0x60,(uintptr_t)a);put(p,0x38,0);put(p,0x3c,0);return p;
}
/* 005787f0. */
void *thug_gap_secondary_node_construct_draft(void *p){
 put(p,4,(uintptr_t)p);put(p,8,0);put(p,12,(uintptr_t)p);put(p,16,(uintptr_t)p);
 put(p,0,(uintptr_t)&thug_gap_secondary_node_methods_draft);thug_skater_handle_construct_draft((char *)p+0x14);return p;
}
/* 00579570/00579630. Destroy owned payloads before base list unlinking. */
void thug_gap_primary_node_destroy_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)&thug_gap_primary_node_methods_draft);ThugScriptArray *a=ptr(p,0x60);
 if(a)thug_script_array_clear(a,m);a=ptr(p,0x60);
 if(a){thug_script_array_clear_storage(a,m);thug_gap_array_free_draft(a,m);}thug_trick_primary_destroy(p);
}
void thug_gap_secondary_node_destroy_draft(void *p,const ThugMemory *m){
 thug_owned_string_destroy_draft((char *)p+0x14,m);thug_trick_secondary_destroy(p);
}
/* 00579820/00579600. */
ThugTrickNode *thug_gap_primary_node_delete_draft(ThugTrickNode *p,uint32_t flags,const ThugMemory *m){
 thug_gap_primary_node_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
ThugTrickNode *thug_gap_secondary_node_delete_draft(ThugTrickNode *p,uint32_t flags,const ThugMemory *m){
 thug_gap_secondary_node_destroy_draft(p,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
const ThugTrickNodeMethods thug_gap_primary_node_methods_draft={thug_gap_primary_node_delete_draft};
const ThugTrickNodeMethods thug_gap_secondary_node_methods_draft={thug_gap_secondary_node_delete_draft};
/* 0057a2f0/00512030. Snapshot each successor before deleting its predecessor. */
void thug_gap_list_clear_draft(void *sentinel,const ThugMemory *m){
 void *p=first(ptr(sentinel,12));while(p){void *next=first(ptr(p,12));dispose(p,m);p=next;}
}
void thug_skater_gap_clear_draft(void *p,const ThugMemory *m){
 thug_gap_list_clear_draft((char *)p+0x18,m);thug_gap_list_clear_draft((char *)p+0x2c,m);
}
static void prepend(void *p,void *sentinel){
 put(p,16,(uintptr_t)sentinel);put(p,12,word(sentinel,12));put(ptr(sentinel,12),16,(uintptr_t)p);put(sentinel,12,(uintptr_t)p);
}
/* 00512050. Successful node allocation and a valid script instance are required. */
void thug_skater_gap_register_trick_draft(void *p,const ThugScriptStructure *params,const ThugScriptInstance *script,const ThugMemory *m){
 void *node=thug_allocate_zeroed(0x34,m);if(node)thug_gap_secondary_node_construct_draft(node);
 prepend(node,(char *)p+0x2c);put(node,0x24,word(script,0xb8));((uint8_t *)node)[0x2c]=0;put(node,0x30,word(p,0x40));
 uint32_t key=0;thug_script_get_checksum(params,0x3b442e26,&key,0);put(node,0x20,key);
 const char *text=0;thug_script_get_text(params,0x3eafa520,&text,0);thug_owned_string_assign_draft((char *)node+0x14,text,m);
 put(node,0x28,0);thug_script_get_checksum(params,0xa26994e6,(void *)((char *)node+0x28),1);
}
/* 00512140. The next node is captured before spawning/executing the real script. */
void thug_skater_gap_check_tricks_draft(void *p,const ThugScriptStructure *unused,const ThugDiagnostics *d,const ThugMemory *m){
 (void)unused;void *node=first(ptr(p,0x38));while(node){void *next=first(ptr(node,12));
  if(((uint8_t *)node)[0x2c])thug_object_spawn_script(ptr(p,12),word(node,0x28),word(node,0x24),0,0,0,d,m);
  node=next;
 }
}
/* Preserve the original-instruction oracle's FCHS sign/payload bits, including
 * signaling encodings. This comparison does not establish physical-x87 behavior
 * for signaling NaNs; ordinary finite game vectors do not reach that boundary. */
static uint32_t negate_word(uint32_t v){return v^0x80000000;}
/* 00512360. Full StartGap, including duplicate disposal, real score queries,
 * array copy, secondary registration and state-derived immediate cancellation. */
void thug_skater_gap_start_draft(void *p,const ThugScriptStructure *params,const ThugScriptInstance *script,const ThugMemory *m){
 if(((uint8_t *)ptr(ptr(p,0x48),0x1528))[0x70])return;
 uint32_t key=0;thug_script_get_checksum(params,0x3b442e26,&key,0);
 void *sentinel=(char *)p+0x18,*node=first(ptr(p,0x24));
 while(node){void *next=first(ptr(node,12));if(word(node,0x14)==key&&word(node,0x1c)==word(script,0xb8))dispose(node,m);node=next;}
 node=thug_allocate_zeroed(0x64,m);if(node)thug_gap_primary_node_construct_draft(node,m);
 prepend(node,sentinel);put(node,0x14,key);put(node,0x1c,word(script,0xb8));put(node,0x2c,0);
 void *reference=thug_skater_camera_object(ptr(p,12));for(unsigned i=0;i<4;i++)put(node,0x40+4*i,word(reference,0x4c+4*i));
 reference=thug_skater_camera_object(ptr(p,12));uint32_t neg[4];for(unsigned i=0;i<4;i++)neg[i]=negate_word(word(reference,0x8c+4*i));
 put(node,0x58,neg[2]);put(node,0x50,neg[0]);put(node,0x54,neg[1]);put(node,0x5c,neg[3]);
 uint32_t related,binding,angle;const char *name;ThugScriptArray *a;
 if(thug_script_get_checksum(params,0xa26994e6,&related,0)){
  put(node,0x28,related);
  if(thug_script_get_checksum(params,0x95e16467,&binding,0)){
   put(node,0x20,binding);
   if(thug_script_get_integer(params,0xedf5db70,&angle,0)){((uint8_t *)node)[0x34]=thug_script_has_flag(params,0x1c39f1b9);put(node,0x30,(uint32_t)((int32_t)angle/180));}
   thug_script_get_integer(params,0xa4bee6a1,(void *)((char *)node+0x3c),0);
   put(node,0x24,thug_score_preceding_bound_draft(ptr(p,0x44),binding,word(node,0x30),word(node,0x3c)));
  }else if(thug_script_get_text(params,0x3eafa520,&name,0)){
   put(node,0x2c,thug_crc32_string(name));
   if(thug_script_get_integer(params,0xedf5db70,&angle,0)){((uint8_t *)node)[0x34]=thug_script_has_flag(params,0x1c39f1b9);put(node,0x30,(uint32_t)((int32_t)angle/180));}
   thug_script_get_integer(params,0xa4bee6a1,(void *)((char *)node+0x3c),0);
   put(node,0x24,thug_score_preceding_named_draft(ptr(p,0x44),word(node,0x2c),word(node,0x30),(int32_t)word(node,0x3c)));
  }else if(thug_script_get_array(params,0x1e26fd3e,&a,0)){
   thug_script_array_copy(ptr(node,0x60),a,m);put(node,0x38,word(ptr(p,0x44),0x5c));
  }
  thug_skater_gap_register_trick_draft(p,params,script,m);
 }
 put(node,0x18,0);a=0;thug_script_get_array(params,0xf4fabe45,&a,0);
 if(a){for(uint32_t i=0;i<a->count;i++)put(node,0x18,word(node,0x18)|thug_script_get_global_integer((uintptr_t)thug_script_array_structure(a,(int32_t)i),0));}
 else {uint32_t mask;if(thug_script_get_checksum_legacy(params,0xf4fabe45,&mask,0))put(node,0x18,word(node,0x18)|thug_script_get_global_integer(mask,0));}
 uint32_t raw=0;if(thug_script_get_checksum(params,0x2760de9e,&raw,0))put(node,0x18,word(node,0x18)|raw);
 if(thug_script_has_flag(params,0xc442e33d))put(node,0x18,word(node,0x18)|0x600);
 else if(!thug_script_has_flag(params,0xe3ed4ade)&&!(word(node,0x18)&0x600))put(node,0x18,word(node,0x18)|0x800);
 if(!(((uint8_t *)ptr(ptr(p,0x50),0x2c))[0x118]&&(word(node,0x18)&0x800))&&thug_skater_orientation_context->identifier==0xd443a2bc)return;
 uint32_t select,clear;thug_skater_gap_state_masks_draft(p,&select,&clear);thug_tricks_cancel(p,select,clear,m);
}
/* 00512cc0: full dispatcher; exported name retained for descriptor ABI. */
extern void thug_skater_gap_end_draft(void *,ThugScriptStructure *,ThugScriptInstance *,const ThugDiagnostics *,const ThugMemory *);
extern uint32_t thug_node_named_link_count_draft(uint32_t);
extern ThugScriptStructure *thug_node_link_at_draft(uint32_t,int32_t);
#include "../../src/game/components.h"
#include "../../src/script/delivery.h"
extern void thug_skater_gap_clear_secondary_draft(void *,const ThugScriptStructure *,const ThugMemory *);
uint32_t thug_skater_gap_command_prefix_draft(void *p,uint32_t name,ThugScriptStructure *params,ThugScriptInstance *script){
 switch(name){case 0x65b9ec39:case 0x0196772b:case 0x42f80e5e:case 0xfc4f2009:break;
 case 0x4562e4a6:case 0xe5399fb2:break;default:return 2;}
 const ThugMemory *m=thug_event_services?thug_event_services->memory:thug_component_services->memory;
 switch(name){
 case 0x4562e4a6:{
  uint32_t owner=word(script,0xb8);if(!owner)break;
  int32_t count=(int32_t)thug_node_named_link_count_draft(owner);
  for(int32_t i=0;i<count;i++){
   ThugScriptStructure *node=thug_node_link_at_draft(owner,i);uint32_t name=0;
   if(thug_script_get_checksum_legacy(node,0x2ca8a299,&name,0)){
    thug_object_spawn_script(ptr(p,12),name,word(script,0xb8),0,0,0,
      thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics,m);break;
   }
  }break;
 }
 case 0xe5399fb2:thug_skater_gap_end_draft(p,params,script,thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics,m);break;
 case 0x65b9ec39:thug_skater_gap_start_draft(p,params,script,m);break;
 case 0x0196772b:thug_skater_gap_clear_secondary_draft(p,params,m);break;
 case 0xfc4f2009:thug_skater_gap_register_trick_draft(p,params,script,m);break;
 case 0x42f80e5e:thug_skater_gap_check_tricks_draft(p,params,thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics,m);break;
 }
 return 1;
}
