/* SkaterAdjustPhysics startup and real moving-geometry escape prerequisites.
 * Full frame/ground/light integration is still unavailable and traps. */
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/collision/probe.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float f(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void pf(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static double r(double v){return thug_platform_round_x87_single(v);}
extern const ThugComponentMethods thug_skater_adjust_pending_methods_draft;
/* 004f80e0. Allocation zeroes storage before the selective constructor writes. */
void *thug_skater_adjust_create_draft(const ThugMemory *m){
 void *p=thug_allocate_zeroed(0x34,m);if(!p)return 0;thug_component_construct(p);
 put(p,0x20,0);put(p,0x24,0);put(p,0x28,0);put(p,0x2c,0);((uint8_t *)p)[0x1c]=0;
 put(p,0,(uintptr_t)&thug_skater_adjust_pending_methods_draft);put(p,4,0x9f9cc949);return p;
}
/* 004f8040/004f8050. */
void thug_skater_adjust_destroy_draft(void *p){put(p,0,(uintptr_t)&thug_skater_adjust_pending_methods_draft);thug_component_destroy(p);}
void *thug_skater_adjust_delete_draft(void *p,uint32_t flags,const ThugMemory *m){thug_skater_adjust_destroy_draft(p);if((uint8_t)flags&1)m->release(m->context,p);return p;}
/* 004f8080. The next owner is loaded before the preceding link is stored. */
void thug_skater_adjust_finalize_draft(void *p){
 const uint32_t types[]={0x5bd63b29,0x286a8d26,0x8a897dd2,0x408d2aa9,0x43686585};
 void *owner=ptr(p,12),*found=thug_object_find_component(owner,types[0]);
 for(unsigned i=1;i<5;i++){owner=ptr(p,12);put(p,0x1c+i*4,(uintptr_t)found);found=thug_object_find_component(owner,types[i]);}put(p,0x30,(uintptr_t)found);
}
/* 00417190/004171b0. Forward word copies, including overlapping storage. */
void thug_collision_probe_start_draft(void *p,const void *start){for(unsigned i=0;i<4;i++)put(p,i*4,word(start,i*4));}
void thug_collision_probe_end_draft(void *p,const void *end){for(unsigned i=0;i<4;i++)put(p,16+i*4,word(end,i*4));}
/* 00427700. Up to nine successive surface tests; both stack-owned probe
 * references are released on every exit. The receiver is unused. */
void *thug_moving_contact_enclosing_draft(void *p,const void *position,void *out,ThugCollisionQuery *query){
 (void)p;ThugCollisionProbe down,up;thug_collision_probe_initialize(&down);
 thug_collision_probe_start_draft(&down,position);thug_collision_probe_end_draft(&down,position);
 down.segment[1]=(float)r((double)f(position,4)+400.0f);
 down.segment[5]=(float)r((double)f(position,4)+6.0f);
 thug_collision_probe_initialize(&up);void *owner=0;
 for(unsigned attempt=1;;attempt++){
  if(!thug_collision_probe_query(&down,1,0,query))break;
  if(!thug_collision_probe_has_moving_object(&down))break;
  thug_collision_probe_start_draft(&up,position);thug_collision_probe_end_draft(&up,down.point);
  up.segment[5]=(float)r((double)down.point[1]+0.1f);
  if(!thug_collision_probe_query(&up,1,0,query)){
   pf(out,0,down.point[0]);put(out,4,word(down.point,4));put(out,12,word(down.point,12));put(out,8,word(down.point,8));
   owner=thug_collision_probe_moving_object(&down);break;
  }
  thug_collision_probe_start_draft(&down,down.point);down.segment[1]=(float)r((double)down.point[1]-0.1f);
  if(attempt+1==10)break;
 }
 thug_collision_probe_release(&up);thug_collision_probe_release(&down);return owner;
}
/* 00427b30. X retains its x87 exponent through doubling; Y spills before
 * doubling; Z/W spill both before doubling and before addition. */
void *thug_moving_contact_escape_draft(void *p,void *position,const void *previous,ThugCollisionQuery *query){
 float surface[4],unused[4],candidate[4];void *owner=thug_moving_contact_enclosing_draft(p,position,surface,query);
 if(!owner)return 0;
 if(!thug_moving_contact_enclosing_draft(p,previous,unused,query)){thug_collision_probe_start_draft(position,previous);return owner;}
 double dt=thug_frame_duration(),x=r(dt*f(owner,0xac));
 float y=(float)r(dt*f(owner,0xb0)),z=(float)r(dt*f(owner,0xb4)),w=(float)r(dt*f(owner,0xb8));
 x=r(x+x);double yy=r((double)y+y);z=(float)r((double)z+z);w=(float)r((double)w+w);
 candidate[0]=(float)r(x+f(position,0));candidate[1]=(float)r(yy+f(position,4));
 candidate[2]=(float)r((double)z+f(position,8));candidate[3]=(float)r((double)w+f(position,12));
 if(!thug_moving_contact_enclosing_draft(p,candidate,unused,query))thug_collision_probe_start_draft(position,candidate);
 else {put(position,0,word(surface,0));put(position,12,word(surface,12));put(position,4,word(surface,4));put(position,8,word(surface,8));pf(position,4,(float)r((double)f(position,4)+1));}
 return owner;
}
void thug_skater_adjust_update_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
static void pending_frame(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){thug_skater_adjust_update_draft(p,q,d,m);}
static uint32_t command(void *p,uint32_t n,ThugScriptStructure *s,ThugScriptInstance *i){return thug_animation_unhandled_command(p,n,s,i,0,0);}
static void empty(void *p){(void)p;}
static void initialize(void *p,const ThugScriptStructure *s){thug_component_empty_one(p,(void *)s);}
const ThugComponentMethods thug_skater_adjust_pending_methods_draft={
 .dispose=thug_skater_adjust_delete_draft,.update=pending_frame,.initialize=initialize,.finalize=thug_skater_adjust_finalize_draft,
 .unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,
 .unknown_20=thug_component_empty_one,.moved=thug_component_empty_frame_bridge,.unknown_28=thug_component_empty_one,
 .descriptor=thug_component_descriptor_base,.checksum=command};
