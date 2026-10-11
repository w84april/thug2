/* Original level links and the storage/history dependencies of EndGap. */
#include "../../src/game/nodes.h"
#include "../../src/game/balance.h"
#include "../../src/script/values.h"
#include "../../src/script/schedule.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* 0045c3a0. An absent Links member has zero entries. */
uint32_t thug_node_named_link_count_draft(uint32_t name){
 ThugScriptStructure *node=thug_node_table_find(thug_node_table,name,1);ThugScriptArray *links=0;
 thug_script_get_array(node,0x2e7d5ee7,&links,0);return links?links->count:0;
}
/* 0045c460. The caller supplies a valid link index. Reload the global table. */
ThugScriptStructure *thug_node_link_at_draft(uint32_t name,int32_t index){
 ThugScriptStructure *node=thug_node_table_find(thug_node_table,name,1);ThugScriptArray *links=0;
 thug_script_get_array(node,0x2e7d5ee7,&links,0);
 uint32_t target=(uintptr_t)thug_script_array_structure(links,index);
 return thug_node_table_find(thug_node_table,target,1);
}
/* 0045c4b0/0045c520. Compare resolved node identity, with a captured count. */
uint8_t thug_node_links_to_draft(const ThugScriptStructure *node,const ThugScriptStructure *target){
 ThugScriptArray *links=0;thug_script_get_array(node,0x2e7d5ee7,&links,0);if(!links)return 0;
 int32_t count=(int32_t)links->count;
 for(int32_t i=0;i<count;i++){
  uint32_t name=(uintptr_t)thug_script_array_structure(links,i);
  if(thug_node_table_find(thug_node_table,name,1)==target)return 1;
 }return 0;
}
uint8_t thug_node_names_linked_draft(uint32_t source,uint32_t target){
 const ThugNodeTable *table=thug_node_table;
 ThugScriptStructure *a=thug_node_table_find(table,source,1),*b=thug_node_table_find(table,target,1);
 return thug_node_links_to_draft(a,b);
}
/* 005612a0. Forward writes precede reading the next input byte. */
void thug_score_escape_spaces_draft(char *out,const char *in){
 unsigned char c=*in;
 while(c){if(c==' '){*out++='\\';*out='_';}else *out=(char)c;c=*++in;out++;}*out=0;
}
/* 005614d0. Signed capacity checks, live source reloads, route-zero storage.
 * Capacity/count are nonnegative and growth must make room when exhausted. */
void thug_score_entries_append_draft(void *p,void *entry,const ThugMemory *m){
 if((int32_t)word(p,4)<=(int32_t)word(p,8)){
  uint32_t capacity=word(p,4)+word(p,12);void *items=m->allocate(m->context,capacity*4,0);
  for(int32_t i=0;i<(int32_t)word(p,4);i++)put(items,(uint32_t)i*4,word(ptr(p,0),(uint32_t)i*4));
  for(int32_t i=(int32_t)word(p,4);i<(int32_t)capacity;i++)put(items,(uint32_t)i*4,0);
  void *old=ptr(p,0);if(old)m->release(m->context,old);put(p,0,(uintptr_t)items);put(p,4,capacity);
 }
 put(ptr(p,0),word(p,8)*4,(uintptr_t)entry);put(p,8,word(p,8)+1);
}
/* 005628b0. Shared indexed-list layout. Allocation succeeds before use. */
uint8_t thug_score_map_append_draft(void *p,const uint32_t *key,void *value,const ThugMemory *m){
 void *node=m->allocate(m->context,12,1);if(node){put(node,4,0);put(node,8,0);}
 put(node,4,(uintptr_t)value);put(node,0,word(key,0));
 if(!ptr(p,4))put(p,4,(uintptr_t)node);else put(ptr(p,8),8,(uintptr_t)node);
 put(p,8,(uintptr_t)node);put(p,0,word(p,0)+1);put(p,12,0);return 1;
}
/* 00561550. Half-open history range, captured item storage, wrapping products.
 * Valid entries have nonnegative repeat/spin indices. Unlike 562e40 this body
 * does not special-case flag 0x100 when selecting the spin multiplier. */
uint32_t thug_score_range_value_draft(const void *score,int32_t start,int32_t end){
 static const uint32_t spins[]={2,3,4,5,6,7},repetitions[]={100,75,50,25,10};
 uint32_t result=0,multiplier=2;if(start>=end)return 0;const void *items=ptr(score,0x4c);
 for(int32_t i=start;i<end;i++){
  const void *entry=ptr(items,(uint32_t)i*4);
  if(word(entry,0x18)&2)multiplier=2;
  else if(!i||(word(ptr(items,(uint32_t)(i-1)*4),0x18)&2)){
   int32_t spin=(int32_t)word(entry,8);multiplier=spin<6?spins[spin]:7;
  }
  int32_t repeat=(int32_t)word(entry,4);uint32_t reduction=repeat<5?repetitions[repeat]:10;
  int32_t value=(int32_t)(word(entry,0)*reduction*multiplier)/200;
  if(word(entry,0x14))value=(int32_t)((uint32_t)value*120)/100;
  result+=(uint32_t)value;
 }return result;
}
/* 0051c9d0. Reuse the recovered live career/profile/availability predicate. */
void thug_timed_tricks_record_name_draft(void *p,const char *name,uint32_t points,uint32_t unused){
 (void)unused;if(thug_timed_tricks_enabled(p)&&points!=word(p,0xa14))put(p,0xa10,(uintptr_t)name);
}
/* 005638a0. Actual synchronous QB dispatch, with owned UI identifiers. */
void thug_score_notify_trick_draft(void *unused,uint32_t screen,const ThugDiagnostics *d,const ThugMemory *m){
 (void)unused;ThugScriptStructure *s=thug_script_structure_allocate(8,m);if(s)thug_script_structure_initialize(s);
 thug_script_set_checksum(s,0x33124d2e,screen+0x1e55886e,m);
 thug_script_set_checksum(s,0x6e7c7ba7,screen+0x44727dae,m);
 thug_script_set_checksum(s,0x6d02989c,screen+0xf4d3a70e,m);
 thug_script_run_sync(0x3bd51fe5,s,0,0,d,m);
 if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
}
/* 00584110/005656c0. Explicit -1 selects the stored current level. */
void *thug_level_gap_state_draft(const void *p,uint32_t level){
 if(level==UINT32_MAX)level=word(p,0x630);return ptr(p,0x63c+level*4);
}
void *thug_game_gap_state_draft(const void *p){return thug_level_gap_state_draft(ptr(p,0x20),UINT32_MAX);}
static void *first(void *p){return word(p,4)==UINT32_MAX?0:p;}
static int same_text(const char *a,const char *b){while(*a==*b){if(!*a)return 1;a++;b++;}return 0;}
/* 00578bc0/00578c70. First exact string match wins; sentinel nodes end traversal.
 * The shared 5480c0 accessor reads the owned string at node+0x44+4. */
void thug_gap_history_record_draft(void *p,const char *name,uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){
 for(void *node=first(ptr(p,0x10));node;node=first(ptr(node,12))){
  if(same_text(ptr(node,0x48),name)){
   put(node,0x14,a);put(node,0x18,b);put(node,0x1c,c);put(node,0x20,d);
   put(node,0x24,e);put(node,0x28,f);put(node,0x2c,g);put(node,0x30,h);return;
  }
 }
}
void thug_gap_history_increment_draft(void *p,const char *name){
 for(void *node=first(ptr(p,0x10));node;node=first(ptr(node,12))){
  if(same_text(ptr(node,0x48),name)){put(node,0x34,word(node,0x34)+1);return;}
 }
}
/* 00578670. */
void thug_gap_secondary_mark_draft(void *p){((uint8_t *)p)[0x2c]=1;}
/* 0049f4c0 is literally XOR EAX,EAX; RET 8 in this specimen. This reproduces
 * that original body; it does not stand in for any other missing routine. */
uint32_t thug_gap_array_score_count_draft(void *p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;return 0;}
