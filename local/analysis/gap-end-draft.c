/* Original EndGap award and callback-visible list lifecycle. */
#include "../../src/game/grind.h"
#include "../../src/game/stats.h"
#include "../../src/script/schedule.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
#include "../../src/core/checksum.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void *first(void *p){return word(p,4)==UINT32_MAX?0:p;}
static void dispose(void *p,const ThugMemory *m){((const ThugTrickNodeMethods *)ptr(p,0))->dispose(p,1,m);}
extern uint8_t thug_node_names_linked_draft(uint32_t,uint32_t);
extern uint32_t thug_score_count_named_draft(const void *,uint32_t,uint32_t,uint32_t,int32_t);
extern uint32_t thug_score_count_bound_draft(const void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t thug_gap_array_score_count_draft(const void *,const void *,uint32_t);
extern void thug_gap_secondary_mark_draft(void *);
extern void *thug_game_gap_state_draft(const void *);
extern void thug_gap_history_record_draft(void *,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void thug_gap_history_increment_draft(void *,const char *);
extern void thug_score_insert_draft(void *,const char *,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
extern void thug_skater_gap_start_draft(void *,const ThugScriptStructure *,const ThugScriptInstance *,const ThugMemory *);
/* 00512770. Required initialized graphs, fitting text and successful allocations
 * are the original internal contracts. In particular, predicate scripts must
 * supply their required boolean output. The rejected-predicate path deliberately
 * retains the original missing output-structure cleanup. */
void thug_skater_gap_end_draft(void *p,ThugScriptStructure *params,ThugScriptInstance *script,const ThugDiagnostics *d,const ThugMemory *m){
 if(((uint8_t *)ptr(ptr(p,0x48),0x1528))[0x70])return;
 uint32_t key=0;thug_script_get_checksum(params,0x3b442e26,&key,0);
 void *node=first(ptr(p,0x24));
 while(node){
  void *next=first(ptr(node,12));
  if(word(node,0x14)!=key||(!key&&!thug_node_names_linked_draft(word(node,0x1c),word(script,0xb8)))){node=next;continue;}
  if(word(node,0x18)&0xffff0000){dispose(node,m);node=next;continue;}
  if(thug_script_has_name_or_flag(params,0x687e2c25)){
   ThugScriptStructure *result=thug_script_structure_allocate(8,m);if(result)thug_script_structure_initialize(result);
   thug_script_run_collect(0x35b75889,0,ptr(p,12),result,d,m);
   uint32_t accepted;thug_script_get_boolean(result,0x1c39f1b9,&accepted,1);
   if(accepted!=1){dispose(node,m);node=next;continue;}
   if(result){thug_script_structure_destroy(result,m);thug_script_structure_free(result,m);}
  }
  const char *name;if(!thug_script_get_text(params,0xc4745838,&name,0))name="Unnamed Gap";
  char label[256];char *out=label;*out++='\\';*out++='c';*out++='1';
  for(const char *in=name;*in;) *out++=*in++;
  *out++='\\';*out++='c';*out++='0';*out=0;
  if(word(node,0x28)){
   uint32_t bound=word(node,0x20);uint8_t match=!bound&&!word(node,0x2c)&&!word(ptr(node,0x60),4);
   if(bound)match=(int32_t)word(node,0x24)<(int32_t)thug_score_count_bound_draft(ptr(p,0x44),bound,word(node,0x30),((uint8_t *)node)[0x34],word(node,0x3c));
   if(!match&&word(node,0x2c))match=(int32_t)word(node,0x24)<(int32_t)thug_score_count_named_draft(ptr(p,0x44),word(node,0x2c),word(node,0x30),((uint8_t *)node)[0x34],(int32_t)word(node,0x3c));
   if(!match&&word(ptr(node,0x60),4))match=(int32_t)thug_gap_array_score_count_draft(ptr(p,0x44),ptr(node,0x60),word(node,0x38))>0;
   if(match){uint32_t id=word(node,0x14);void *other=first(ptr(p,0x38));
    while(other){void *following=first(ptr(other,12));if(word(other,0x20)==id){thug_gap_secondary_mark_draft(other);break;}other=following;}
   }
  }
  uint32_t a[8];for(unsigned i=0;i<8;i++)a[i]=word(node,0x40+i*4);
  thug_gap_history_record_draft(thug_game_gap_state_draft(thug_game_context),name,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]);
  uint32_t points=0;
  if(thug_script_get_integer(params,0xcd66c8ae,&points,0)&&((uint8_t *)ptr(p,12))[0xbc]){
   thug_score_insert_draft(ptr(p,0x44),label,points,0x10,d,m);
   ((uint8_t *)thug_object_find_component(ptr(p,12),0x270f56e1))[0x13a8]=1;
   thug_gap_history_increment_draft(thug_game_gap_state_draft(thug_game_context),name);
   thug_object_spawn_script(ptr(p,12),0x541a2485,0,0,0,0,d,m);
  }
  uint32_t success;
  if(thug_script_get_checksum(params,0x7c9e51ab,&success,0)){
   void *owner=ptr(p,12);uint32_t network_argument=thug_script_has_flag(params,0x23627fd7);
   uint32_t network=thug_script_has_flag(params,0x20209c31);
   thug_object_spawn_script(owner,success,word(script,0xb8),network,network_argument,0,d,m);
  }
  ThugScriptStructure *start=0;
  if(thug_script_get_structure(params,0xec1cd520,&start,0))thug_skater_gap_start_draft(p,start,script,m);
  uint32_t event=thug_crc32_extend_string(key,"_Success");
  thug_event_emit((ThugEventManager *)thug_object_lookup_manager,event,UINT32_MAX,word(ptr(p,12),0x14),params,1,-1,d,m);
  void *live=first(ptr(p,0x24));while(live&&live!=node)live=first(ptr(live,12));
  if(live==node)dispose(node,m);
  node=first(ptr(p,0x24));
 }
}
