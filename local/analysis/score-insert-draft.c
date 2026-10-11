/* Original score insertion and bounded history compression. */
#include "../../src/game/score.h"
#include "../../src/game/balance.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
#include "../../src/core/checksum.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void store_number(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static void *last(const void *score){return ptr(ptr(score,0x4c),word(score,0x54)*4-4);}
extern uint32_t thug_score_range_value_draft(const void *,int32_t,int32_t);
extern void thug_score_entries_append_draft(void *,void *,const ThugMemory *);
extern uint8_t thug_score_map_append_draft(void *,const uint32_t *,void *,const ThugMemory *);
extern void thug_score_escape_spaces_draft(char *,const char *);
extern void thug_timed_tricks_record_name_draft(void *,const char *,uint32_t,uint32_t);
extern void thug_score_notify_trick_draft(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
#define R thug_platform_round_x87_single
/* 005629d0. The original automatic record only initializes seven words and
 * both string prefixes through NUL. Trailing string-storage bytes are
 * indeterminate, including in this reconstruction; they are not score state.
 * Valid callers retain an entry zero and enough later entries to remove. */
void thug_score_compress_history_draft(void *score,const ThugMemory *m){
 uint8_t record[0x9c];for(unsigned o=0;o<0x1c;o+=4)put(record,o,0);
 __builtin_memcpy(record+0x1c,"... + ",7);__builtin_memcpy(record+0x5c,"...\\_+\\_",9);
 int32_t count=(int32_t)word(score,0x54),remove=count;
 for(int32_t i=0;i<(int32_t)word(score,0x54);i++){
  if(i&&!((uint8_t *)ptr(ptr(score,0x4c),(uint32_t)i*4))[0x1c]){remove=i;break;}
 }
 if(remove>(int32_t)word(score,0x6c)||remove>(int32_t)word(score,0x68))return;
 put(record,0,thug_score_range_value_draft(score,0,remove));
 for(int32_t n=remove;n>0;n--){
  m->release(m->context,ptr(ptr(score,0x4c),4));
  for(int32_t i=1;i<(int32_t)(word(score,0x54)-1);i++){
   void *items=ptr(score,0x4c);put(items,(uint32_t)i*4,word(items,(uint32_t)i*4+4));
  }
  put(ptr(score,0x4c),word(score,0x54)*4-4,0);put(score,0x54,word(score,0x54)-1);
  uint32_t total=word(score,0x5c),spin=word(score,0x6c),start=word(score,0x68);
  put(score,0x5c,total-1);put(score,0x6c,spin-1);put(score,0x68,start-1);
 }
 __builtin_memcpy(ptr(ptr(score,0x4c),0),record,sizeof(record));
 void *entry=ptr(ptr(score,0x4c),0);put(entry,0x18,word(entry,0x18)|2);
}
static char *copy_text(char *out,const char *in){while((*out=*in++))out++;return out;}
/* 00563990. Required skater/components/widgets and fitting strings are original
 * internal contracts. All UI/event notifications execute their real callees;
 * subsequent reads retain callback-visible mutation order. */
void thug_score_insert_draft(void *score,const char *name,uint32_t points,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m){
 uint8_t empty=!name[0];int16_t id;__builtin_memcpy(&id,(char *)score+8,2);
 ThugSkaterBody *body=thug_game_skater_by_id(thug_game_context,(uint32_t)(int32_t)id);if(!body)return;
 void *trick=thug_object_find_component(body,0x270f56e1),*timed=thug_object_find_component(body,0x4ff8dac6);
 if(name[0])((uint8_t *)trick)[0x13a8]=1;
 void *physics=thug_object_find_component(body,0x5bd63b29);
 uint32_t orientation=((uint8_t *)ptr(physics,0x1528))[0x28];if(!((uint8_t *)ptr(physics,12))[0x110])orientation=!orientation;
 thug_timed_tricks_record_name_draft(timed,name,points,orientation);
 if((int32_t)word(score,0x5c)>249){
  thug_score_compress_history_draft(score,m);
  if((int32_t)word(score,0x5c)>249){
   if(empty)return;if(d&&d->print)d->print(d->context,"Trick Limit (%d) Reached\n",250);
   void *entry=last(score);put(entry,0,word(entry,0)+points);
   if(!(flags&0x200))store_number(score,0x60,(float)R((double)number(score,0x60)+1));
   thug_score_recalculate(score,d,m);return;
  }
 }
 m->temp_scope(m->context,6);uint32_t checksum=thug_crc32_string(name),variant=(flags>>1)&(flags&0x400?4:6);
 if((int32_t)word(score,0x54)<250){void *entry=m->allocate(m->context,0x9c,1);thug_score_entries_append_draft((char *)score+0x4c,entry,m);put(last(score),0,0);}
 void *entry=last(score);put(entry,0,word(entry,0)+points);
 put(last(score),0x10,checksum);put(last(score),0x14,variant);put(last(score),0x18,flags);put(last(score),8,0);
 ((uint8_t *)last(score))[0x1c]=0;((uint8_t *)last(score))[0x5c]=0;put(last(score),12,0);
 if(!empty){
  thug_score_escape_spaces_draft((char *)last(score)+0x1c,name);
  entry=last(score);char *out=(char *)entry+0x5c;
  if(flags&0x80)out=copy_text(out,"\\c3");else if(flags&0x20)out=copy_text(out,"\\c2");
  out=copy_text(out,(char *)entry+0x1c);if(flags&0xa0)out=copy_text(out,"\\c0");copy_text(out," ");
  int32_t i=(int32_t)(word(score,0x54)-2);void *items=ptr(score,0x4c);
  for(;i>=0;i--){char *text=(char *)ptr(items,(uint32_t)i*4)+0x5c;uint32_t len=0;while(text[len])len++;
   if(text[0]=='.'||!len)continue;if(text[len-1]==' ')text[len-1]=0;
   char *end=text;while(*end)end++;__builtin_memcpy(end,"\\_+ ",5);break;
  }
 }
 uint32_t total=word(score,0x5c);if(word(score,0x68)==total-1)put(score,0x6c,total);if(flags&2)put(score,0x68,total);
 void *map=(char *)score+0x38,*repeat=thug_objective_find(map,&checksum);uint8_t bypass=!!(flags&0x50);
 if(bypass)put(last(score),4,0);
 else{
  if(!repeat){repeat=thug_allocate_array_storage(0x24,m);thug_score_map_append_draft(map,&checksum,repeat,m);
   for(unsigned i=0;i<4;i++){put(repeat,4+i*4,0);put(repeat,0x14+i*4,0);}}
  uint32_t current=word(repeat,variant*4+0x14);put(last(score),4,word(repeat,variant*4+4)+current);put(repeat,variant*4+0x14,word(repeat,variant*4+0x14)+1);
 }
 put(score,0x5c,word(score,0x5c)+1);
 if(!empty){
  uint32_t old_multiplier=word(score,0x60),threshold=thug_script_get_global_integer(0xfd4625cd,1);put(score,0x64,word(score,0x64)+1);
  if(number(score,0x60)==0||bypass)store_number(score,0x60,(float)R((double)number(score,0x60)+1));
  else{
   uint32_t current=word(repeat,variant*4+0x14);
   if((int32_t)current<(int32_t)threshold){if(!(flags&0x200))store_number(score,0x60,(float)R((double)number(score,0x60)+1));}
   else{double delta=R(1-R((double)(int32_t)(current-threshold+1)*.5));float stored=(float)delta;
    if(delta>0&&!(flags&0x200))store_number(score,0x60,(float)R((double)stored+number(score,0x60)));}
  }
  if(word(score,0x60)==0x3f800000){
   void *component=thug_object_find_component(body,0x8bce7e66);
   store_number(component,0x1c,(float)thug_skater_stat_parameter(ptr(component,12),0x0b84f532));
   uint16_t zero=0;__builtin_memcpy((char *)component+0x20,&zero,2);put(component,0x18,2);
   store_number(score,0,(float)thug_script_get_global_number(0x59b9a85e,1));put(score,4,thug_script_get_global_integer(0xb33d71c0,1));
   thug_object_broadcast_event((void *)body,0x670fda8c,0,0,d,m);
  }
  int32_t i=(int32_t)(word(score,0x5c)-1),consecutive=0;void *items=ptr(score,0x4c);
  for(;i>0;i--){if(word(ptr(items,(uint32_t)i*4),0x18)&2)break;consecutive++;}
  if(consecutive>10){put(last(score),0,0);if(number(score,0x60)>1)store_number(score,0x60,(float)R((double)number(score,0x60)-1));}
  void *adjust=thug_object_find_component(body,0x9f9cc949);
  if(adjust&&((uint8_t *)adjust)[0x1c]){put(last(score),0,0);put(score,0x60,old_multiplier);}
 }
 thug_score_recalculate(score,d,m);thug_score_update_combo_text(score,0,d,m);
 thug_score_notify_trick_draft(score,thug_skater_screen_id(body),d,m);
 uint32_t points_now=word(score,0x14);float multiplier=number(score,0x60);put(score,0x10,0);
 thug_score_update_numeric_text(score,(int32_t)points_now,multiplier,d,m);m->temp_scope(m->context,0);
}
