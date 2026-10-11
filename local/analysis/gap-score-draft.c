/* Original score-history queries used by StartGap and EndGap.
 * Required script/profile structures retain the original valid-data contract. */
#include "../../src/game/score.h"
#include "../../src/game/profile.h"
#include "../../src/core/checksum.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* 00586130. PUSH ECX seeds the output with the original profile pointer. */
ThugScriptStructure *thug_profile_specials_draft(const ThugProfile *p){
 ThugScriptStructure *s=(void *)p;thug_script_get_structure(&p->parameters,0xddbee809,&s,1);return s;
}
/* 00561360. Each extra tap follows the first next-trick array entry. */
uint32_t thug_score_trick_checksum_draft(uint32_t key,int32_t taps){
 ThugScriptStructure *s=thug_script_get_global_structure(key,1),*params=0;
 thug_script_get_structure(s,0x7031f10c,&params,1);
 uint32_t next=(uint32_t)taps;
 for(int32_t i=1;i<taps;i++){
  thug_script_get_checksum(params,0x6e855102,&next,0);
  ThugScriptArray *a=thug_script_get_global_array(next,1);
  s=thug_script_array_structure(a,0);thug_script_get_structure(s,0x7031f10c,&params,1);
 }
 const char *name=0;thug_script_get_text_forward(params,0xa1dc81f9,&name,1);return thug_crc32_string(name);
}
/* 00562080. A direct binding takes precedence, including checksum zero. */
uint32_t thug_score_profile_checksum_draft(uint32_t key,int32_t taps){
 ThugProfile *profile=thug_game_profile(thug_game_context,0);
 ThugScriptStructure *bindings=thug_profile_parameters(profile,0xd544aa2d);uint32_t trick=0;
 if(!thug_script_get_checksum(bindings,key,&trick,0)){
  ThugScriptArray *a=0;thug_script_get_array(thug_profile_specials_draft(profile),0,&a,1);
  int32_t count=(int32_t)a->count;
  for(int32_t i=0;i<count;i++){
   ThugScriptStructure *s=thug_script_array_structure(a,i);uint32_t combo=0;
   thug_script_get_checksum(s,0xa92a2280,&combo,1);
   if(combo==key){thug_script_get_checksum(s,0x5b077ce1,&trick,1);break;}
  }
 }
 return trick?thug_score_trick_checksum_draft(trick,taps):0;
}
/* 00562150. Integer bindings identify created tricks; special entries use
 * their checksum-valued index. The first matching enabled entry wins. */
uint32_t thug_score_profile_special_draft(uint32_t key){
 ThugProfile *profile=thug_game_profile(thug_game_context,0);
 ThugScriptStructure *bindings=thug_profile_parameters(profile,0xd544aa2d);uint32_t slot=UINT32_MAX;
 if(thug_script_get_integer(bindings,key,&slot,0))return slot;
 ThugScriptArray *a=0;thug_script_get_array(thug_profile_specials_draft(profile),0,&a,1);
 int32_t count=(int32_t)a->count;
 for(int32_t i=0;i<count;i++){
  ThugScriptStructure *s=thug_script_array_structure(a,i);uint32_t enabled=0,combo=0;
  thug_script_get_integer(s,0xb56a8816,&enabled,0);
  if(enabled){thug_script_get_checksum(s,0xa92a2280,&combo,1);if(combo==key){thug_script_get_checksum(s,0x5b077ce1,&slot,1);return slot;}}
 }
 return slot;
}
/* 005622c0. Gap entries reset spin context. Signed arithmetic wraps like x86,
 * including INT_MIN absolute values and the low-byte exact-spin option. */
uint32_t thug_score_count_history_draft(const void *p,uint32_t key,uint32_t spin,uint32_t exact){
 uint32_t count=0,context=1;
 for(uint32_t i=0;(int32_t)i<(int32_t)word(p,0x5c);i++){
  void **items=ptr(p,0x4c);void *entry=items[i];
  if(word(entry,0x18)&2)context=1;
  else if(!i||(word(items[i-1],0x18)&2))context=word(entry,8);
  if(word(entry,0x10)!=key)continue;
  if(spin){
   if(spin!=context)continue;
   if((uint8_t)exact){
    uint32_t delta=word(entry,12);if((int32_t)delta<0)delta=0u-delta;
    delta-=spin*180u;if((int32_t)delta<0)delta=0u-delta;
    if((int32_t)delta>=(int32_t)thug_script_get_global_integer(0xfcfacab8,0))continue;
   }
  }
  count++;
 }
 return count;
}
/* Shared body of005625a0/00562620: capture the count and storage once, retain
 * the trailing match across flag0x10 entries and same-key wrong-spin entries. */
static uint32_t preceding(const void *p,uint32_t key,uint32_t spin){
 int32_t remaining=(int32_t)word(p,0x5c);uint32_t count=0;uint8_t trailing=0;
 if(remaining>0){void **items=ptr(p,0x4c);
  do{void *entry=*items++;
   if(word(entry,0x10)==key){if(!spin||spin==word(entry,8)){count++;trailing=1;}}
   else if(!(word(entry,0x18)&0x10)||!trailing)trailing=0;
  }while(--remaining);
  if(trailing)count--;
 }
 return count;
}
static uint32_t resolve_created(uint32_t key,uint32_t taps,uint8_t *found){
 uint32_t name=thug_score_profile_checksum_draft(key,(int32_t)taps);*found=1;
 if(!name){
  uint32_t slot=thug_score_profile_special_draft(key);if(slot==UINT32_MAX){*found=0;return 0;}
  ThugSkaterBody *body=thug_game_local_skater(thug_game_context);
  if(body){const char *text=0;void *created=ptr(body,0x17c+slot*4);
   thug_script_get_text(ptr(created,4),0xa1dc81f9,&text,1);name=thug_crc32_string(text);}
 }
 return name;
}
/* 005624c0,00562510,005625a0,00562620: distinct argument orders preserved. */
uint32_t thug_score_count_named_draft(const void *p,uint32_t key,uint32_t spin,uint32_t exact,int32_t taps){
 if(taps>1)key=thug_score_trick_checksum_draft(key,taps);
 return thug_score_count_history_draft(p,key,spin,exact);
}
uint32_t thug_score_count_bound_draft(const void *p,uint32_t key,uint32_t spin,uint32_t exact,uint32_t taps){
 uint8_t found;uint32_t name=resolve_created(key,taps,&found);return found?thug_score_count_history_draft(p,name,spin,exact):0;
}
uint32_t thug_score_preceding_named_draft(const void *p,uint32_t key,uint32_t spin,int32_t taps){
 if(taps>1)key=thug_score_trick_checksum_draft(key,taps);return preceding(p,key,spin);
}
uint32_t thug_score_preceding_bound_draft(const void *p,uint32_t key,uint32_t spin,uint32_t taps){
 uint8_t found;uint32_t name=resolve_created(key,taps,&found);return found?preceding(p,name,spin):0;
}
