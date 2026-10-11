#include "../../src/game/components.h"
#include "../../src/game/objectives.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static double r(double v){return thug_platform_round_x87_single(v);}
/* 0055d990. Valid sentinel list: the original reads body before testing node. */
ThugSkaterNode *thug_proximity_list_at_draft(const void *list,uint32_t index){
 for(ThugSkaterNode *n=pointer(list,12);(uintptr_t)n->body!=UINT32_MAX;n=n->next)if(index--==0)return n;
 return 0;
}
/* 005665c0. Count first, then repeat the original indexed traversal. */
ThugSkaterBody *thug_proximity_skater_at_draft(const ThugGameContext *game,uint32_t index){
 uint32_t count=0;for(ThugSkaterNode *n=game->skaters;(uintptr_t)n->body!=UINT32_MAX;n=n->next)count++;
 return index<count?thug_proximity_list_at_draft((const char *)game+0x28,index)->body:0;
}
/* 004ec3c0. Output remains untouched on no local skater or self. Retain the
 * wide exponent until the caller spills the PC24 squared distance. */
double thug_proximity_local_distance_draft(const void *p,uint32_t *id){
 ThugSkaterBody *body=thug_game_local_skater(thug_game_context);
 if(!body||body==pointer(p,12))return 0x1.9c4498p+44;
 *id=word(body,0x14);void *owner=pointer(p,12);
 double x=r((double)number(body,0x4c)-number(owner,0x4c));
 double y=r((double)number(body,0x50)-number(owner,0x50));
 double z=r((double)number(body,0x54)-number(owner,0x54));
 return r(r(r(x*x)+r(z*z))+r(y*y));
}
/* 004ec4b0. The best distance spills to float after each strictly closer body;
 * index lookup and owner reads repeat, including observable output aliases. */
double thug_proximity_nearest_distance_draft(const void *p,uint32_t *id){
 uint32_t count=0;for(ThugSkaterNode *n=thug_game_context->skaters;(uintptr_t)n->body!=UINT32_MAX;n=n->next)count++;
 float best=0x1.9c4498p+44f;
 for(uint32_t i=0;i<count;i++){
  ThugSkaterBody *body=thug_proximity_skater_at_draft(thug_game_context,i);void *owner=pointer(p,12);
  if(!body||body==owner)continue;
  double x=r((double)number(body,0x4c)-number(owner,0x4c));
  double y=r((double)number(body,0x50)-number(owner,0x50));
  double z=r((double)number(body,0x54)-number(owner,0x54));
  double distance=r(r(r(z*z)+r(x*x))+r(y*y));
  if(distance<best){uint32_t key=word(body,0x14);best=(float)distance;*id=key;}
 }
 return best;
}
static ThugScriptStructure *parameters(uint32_t key,uint32_t integer,uint32_t id,const ThugMemory *m){
 ThugScriptStructure *s=thug_script_structure_allocate(8,m);if(s)thug_script_structure_initialize(s);
 thug_script_set_checksum(s,key,id,m);if(integer)thug_script_set_integer(s,integer,id,m);return s;
}
static void release(ThugScriptStructure *s,const ThugMemory *m){if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}}
static int enabled(const void *p){return !(word(pointer(p,12),8)&1);}
static void emit(const void *p,uint32_t event,ThugScriptStructure *s,const ThugDiagnostics *d,const ThugMemory *m){thug_object_emit_event(pointer(p,12),event,s,d,m);}
/* 004ec560. A parameter-bearing event requires a distance helper to have
 * supplied an ID, as in a live player scene. Original missing-ID stack contents
 * are undefined; callers must not request those events with no eligible body. */
void thug_proximity_update_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 float distance=0;uint32_t id=0;ThugScriptStructure *s;
 if(number(p,0x18)!=0){
  double local=thug_proximity_local_distance_draft(p,&id);distance=(float)local;
  if(local<=number(p,0x18)){
   s=parameters(0xf79c90ae,0xdb1e28cd,id,m);emit(p,0x7048029a,s,d,m);
   if(enabled(p))emit(p,0xf5b2a042,s,d,m);release(s,m);
  }else{
   if(thug_proximity_nearest_distance_draft(p,&id)<=number(p,0x18)){
    s=parameters(0xf79c90ae,0xdb1e28cd,id,m);emit(p,0xf5b2a042,s,d,m);release(s,m);
   }
   distance=0;
  }
 }
 if(number(p,0x1c)!=0){
  if(distance==0)distance=(float)thug_proximity_nearest_distance_draft(p,&id);
  if(distance>=number(p,0x1c)&&enabled(p)){
   s=parameters(0x873a40d0,0x5f3602f5,id,m);emit(p,0x91bcad1d,s,d,m);release(s,m);
  }
 }
 if(number(p,0x20)!=0){
  if(distance==0)distance=(float)thug_proximity_local_distance_draft(p,&id);
  if(distance<=number(p,0x20)){
   s=parameters(0xf79c90ae,0,id,m);if(enabled(p))emit(p,0xd69bd3de,s,d,m);release(s,m);
  }
 }
 if(number(p,0x24)!=0){
  if(distance==0)distance=(float)thug_proximity_local_distance_draft(p,&id);
  if(distance>=number(p,0x24)&&enabled(p))emit(p,0x35fdafae,0,d,m);
 }
 if(number(p,0x28)!=0){
  if(distance==0)distance=(float)thug_proximity_local_distance_draft(p,&id);
  if(enabled(p))emit(p,distance<=number(p,0x28)?0xa06c9031:0x9c1cde7a,0,d,m);
 }
}
extern uint32_t *thug_motion_frame_boundary_draft;
void thug_motion_frame_proximity_boundary_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_proximity_update_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(thug_motion_frame_boundary_draft)thug_motion_frame_proximity_boundary_draft(p,q,d,m);
 thug_proximity_update_draft(p,d,m);
}
uint32_t *thug_proximity_frame_boundary_draft;
void thug_proximity_lock_boundary_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;uint32_t *b=thug_proximity_frame_boundary_draft;
 if(b){b[0]=0x41ff90;b[1]=(uintptr_t)p;b[2]=word(p,12);b[3]=1;}__builtin_trap();
}
