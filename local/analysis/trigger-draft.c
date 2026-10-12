/* Original Trigger component, collision callbacks and event-mask command. */
#include "../../src/game/components.h"
#include "../../src/game/collision_events.h"
#include "../../src/script/params.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
extern const ThugComponentMethods thug_trigger_methods_draft;
/* 00434b90. The allocator clears the whole object; the inlined constructor
 * only installs the base flags, method table and component checksum. */
void *thug_trigger_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x2c,m);if(!p)return 0;
 thug_component_construct(p);put(p,0,(uintptr_t)&thug_trigger_methods_draft);put(p,4,0xe594f0a2);return p;
}
/* 00434900 / 00434910. */
void thug_trigger_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_trigger_methods_draft);thug_component_destroy(p);}
void *thug_trigger_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_trigger_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 00434940. Ordered word copies retain raw payloads and overlapping reads. */
void thug_trigger_initialize_draft(void *p,const ThugScriptStructure *s){
 (void)s;const void *owner=ptr(p,12);for(unsigned i=0;i<4;i++)put(p,0x18+i*4,word(owner,0x4c+i*4));
}
/* 00434970. Required unnamed array; either integer events or alternatives of
 * integer arrays. Duplicate events are added, and x86 shifts mask by31. */
uint32_t thug_trigger_command_draft(void *p,uint32_t name,ThugScriptStructure *params,ThugScriptInstance *script){
 (void)script;if(name!=0x3a717382)return 2;
 ThugScriptArray *a=0,*alternatives=0;thug_script_get_array(params,0,&a,0);uint32_t count=1;
 if(((const uint8_t *)a)[1]==12){alternatives=a;count=a->count;}
 for(uint32_t i=0;i<count;i++){
  if(alternatives)a=(void *)thug_script_array_structure(alternatives,(int32_t)i);
  if(((const uint8_t *)a)[1]!=1)return 0;
  uint32_t mask=0;
  for(int32_t j=0;j<(int32_t)a->count;j++){
   int32_t event=(int32_t)(uintptr_t)thug_script_array_structure(a,j);
   if(event>=0)mask+=UINT32_C(1)<<((uintptr_t)thug_script_array_structure(a,j)&31);
  }
  uint32_t current=word(p,0x28);if((current|mask)==current)return 1;
 }
 return 0;
}
/* 00434ce0. Traverse saved collision records backward. Later records suppress
 * duplicate names regardless of their flag; callback changes remain visible. */
void thug_trigger_from_records_draft(void *p,const uint32_t events[3],void *records,const ThugDiagnostics *d,const ThugMemory *m){
 uint32_t remaining=word(records,0xc30);if(!remaining)return;
 uint32_t index=remaining+1;uint8_t *entry=(uint8_t *)records+0x8c+remaining*0x60;
 do{
  uint8_t active=entry[-0x60];entry-=0x60;index--;
  if(active){
   int32_t count=(int32_t)word(records,0xc30),j=(int32_t)index;
   const uint8_t *later=entry+0x5c;
   while(j<count){if(word(entry-4,0)==word(later,0))break;j++;later+=0x60;}
   if(j==count)thug_collision_event_start(p,events,word(entry-4,0),0,0,d,m);
  }
 }while(--remaining);
}
/* 00434d70. The original event tuple at0064663c contains three zero words. */
void thug_trigger_probe_callback_draft(ThugCollisionProbe *probe){
 static const uint32_t events[3]={0,0,0};const ThugComponentServices *s=thug_component_services;
 thug_collision_event_from_probe((void *)(uintptr_t)probe->unknown_a8,events,probe,s->diagnostics,s->memory);
}
/* 00434d90. Compare all four coordinates; NaNs count as changed. A teleported
 * owner only updates the saved position. Ordinary motion executes real static
 * and moving collision queries, then rereads the owner after script callbacks. */
void thug_trigger_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 void *owner=ptr(p,12);unsigned i=0;
 for(;i<4;i++)if(!(number(owner,0x4c+i*4)==number(p,0x18+i*4)))break;
 if(i==4)return;
 if(word(owner,0x104)&8){for(i=0;i<4;i++)put(p,0x18+i*4,word(owner,0x4c+i*4));return;}
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 for(i=0;i<4;i++)put(probe.segment,i*4,word(p,0x18+i*4));
 owner=ptr(p,12);for(i=0;i<4;i++)put(probe.segment,16+i*4,word(owner,0x4c+i*4));
 thug_collision_probe_set_flags(&probe,0,0x50);probe.callback=thug_trigger_probe_callback_draft;probe.unknown_a8=(uintptr_t)p;
 const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
 thug_collision_probe_query(&probe,1,0,q);thug_component_services=previous;
 owner=ptr(p,12);for(i=0;i<4;i++)put(p,0x18+i*4,word(owner,0x4c+i*4));
 thug_collision_probe_release(&probe);
}
static void empty(void *p){(void)p;}
const ThugComponentMethods thug_trigger_methods_draft={
 .dispose=thug_trigger_delete_draft,.update=thug_trigger_update_draft,.initialize=thug_trigger_initialize_draft,.finalize=empty,
 .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=thug_trigger_command_draft};
