/* Complete original SkaterAdjustPhysics frame and its three helpers. */
#include "../../src/game/components.h"
#include "../../src/game/moving_contact.h"
#include "../../src/script/delivery.h"
#include "../../src/script/params.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float f(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void pf(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void *at(void *p,unsigned o){return (char *)p+o;}
static double r(double v){return thug_platform_round_x87_single(v);}
void thug_collision_probe_start_draft(void *,const void *);
void thug_collision_probe_end_draft(void *,const void *);
void *thug_moving_contact_escape_draft(void *,void *,const void *,ThugCollisionQuery *);
void thug_model_surface_light_draft(void *,const ThugCollisionProbe *,uint32_t,float);
uint32_t thug_adjust_initialized_draft; /* 007ccdb0 */
float thug_adjust_offsets_draft[5][4]; /* 007ccd60 */
/* 007ce5d8 is the existing thug_skater_orientation_context. */
const char thug_adjust_escape_format_draft[]="M:%s:%i: %s\n";
const char thug_adjust_escape_source_draft[]="mponents\\SkaterAdjustPhysicsComponent.cpp";
const char thug_adjust_escape_message_draft[]="found to be inside a moving object";
/* 004f82f0. Static-only secondary surface query, preserving the real probe. */
void thug_skater_adjust_light_draft(void *p,ThugCollisionProbe *probe,ThugCollisionQuery *q){
 uint8_t hit=thug_collision_probe_query(probe,0,0,q);ThugCollisionProbe copy;
 thug_collision_probe_copy_initialize(&copy,probe);thug_collision_probe_set_flags(&copy,0,0x20);
 copy.segment[1]=(float)r((double)copy.segment[1]+12);
 if(hit){thug_collision_probe_end_draft(&copy,probe->point);copy.segment[5]=(float)r((double)probe->point[1]-1);}
 else thug_collision_probe_end_draft(&copy,copy.segment);
 uint8_t second=thug_collision_probe_query(&copy,0,0,q);
 if(second||hit)thug_model_surface_light_draft(ptr(p,0x24),second?&copy:probe,1,1);
 thug_collision_probe_release(&copy);
}
/* 004f8aa0. Reacquire contact after escape, then publish the original event. */
void thug_skater_adjust_escape_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(!thug_moving_contact_escape_draft(ptr(p,0x2c),at(ptr(p,12),0x4c),at(ptr(p,0x20),0x98),q))return;
 if(d&&d->print)d->print(d->context,thug_adjust_escape_format_draft,thug_adjust_escape_source_draft,0x182,thug_adjust_escape_message_draft);
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);float point[4];void *body=ptr(p,12);
 thug_vector_copy(point,at(body,0x4c));point[1]=(float)r((double)point[1]+30);thug_collision_probe_start_draft(&probe,point);
 body=ptr(p,12);thug_vector_copy(point,at(body,0x4c));point[1]=(float)r((double)point[1]-30);thug_collision_probe_end_draft(&probe,point);
 if(thug_collision_probe_query(&probe,1,0,q)&&thug_collision_probe_has_moving_object(&probe))
  thug_skater_moving_contact_set_owner(ptr(p,0x2c),(void *)thug_collision_probe_moving_object(&probe),m);
 if(word(ptr(ptr(p,0x20),0x1528),0x18)==4){
  thug_skater_change_state(ptr(p,0x20),1,d,m);thug_object_emit_event(ptr(p,12),0xafaa46ba,0,d,m);
 }else{
  body=ptr(p,12);if(thug_vector_equal(at(body,0x4c),at(ptr(p,0x20),0x98))){put(body,0xac,0);put(body,0xb0,0);put(body,0xb4,0);put(body,0xb8,0x3f800000);}
 }
 thug_collision_probe_release(&probe);
}
/* 004f8420. Full grounded fallback/correction, shadows, contact and lighting. */
void thug_skater_adjust_ground_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 void *physics=ptr(p,0x20),*body=ptr(p,12);((uint8_t *)p)[0x1c]=0;
 if(!thug_vector_not_equal(at(body,0x4c),at(physics,0x98)))return;
 thug_vector_copy(at(physics,0x208),at(body,0x4c));body=ptr(p,12);physics=ptr(p,0x20);
 thug_vector_copy(at(physics,0x218),at(body,0x4c));body=ptr(p,12);
 double w=r((double)f(body,0x88)*.01f),z=r((double)f(body,0x84)*.01f),y=r((double)f(body,0x80)*.01f),x=f(body,0x7c);
 physics=ptr(p,0x20);x=r(x*.01f);pf(physics,0x208,(float)r(x+f(physics,0x208)));pf(physics,0x20c,(float)r(y+f(physics,0x20c)));
 pf(physics,0x210,(float)r(z+f(physics,0x210)));pf(physics,0x214,(float)r(w+f(physics,0x214)));
 physics=ptr(p,0x20);pf(physics,0x20c,(float)r((double)f(physics,0x20c)+8));void *end=at(ptr(p,0x20),0x21c);
 double length=r(thug_script_get_global_number(0x801c9cb6,0)*12);pf(end,0,(float)r((double)f(end,0)-length));
 if(thug_skater_query_surface(ptr(p,0x20),0x10,0,q)){
  physics=ptr(p,0x20);void *state=ptr(physics,0x1528);
  if(!byte(state,0x88)&&!byte(state,0x78)){
   void *contact=ptr(ptr(p,0x2c),0x18);
   if(contact){
    uint8_t release=!word(contact,0);
    if(!release&&(word(state,0x18)==0||word(state,0x18)==1)){
     if(!thug_collision_probe_has_moving_object(at(physics,0xa8)))release=1;
     else {void *old=ptr(ptr(ptr(p,0x2c),0x18),0);release=thug_collision_probe_moving_object(at(ptr(p,0x20),0xa8))!=old;}
     if(release)thug_vector_add(at(ptr(p,12),0xac),at(ptr(ptr(ptr(p,0x2c),0x18),0),0xac));
    }
    if(release)thug_skater_moving_contact_release(ptr(p,0x2c),m);
   }
  }
  uint32_t flags=thug_adjust_initialized_draft;
  if(!(flags&1))thug_adjust_initialized_draft=flags|=1;
  if(!(flags&2))thug_adjust_initialized_draft=flags|=2;
  if(!(flags&4))thug_adjust_initialized_draft=flags|=4;
  double height=r((double)f(ptr(p,12),0x50)-f(ptr(p,0x20),0x124));pf(ptr(p,0x30),0x11c,(float)height);
  if(height<.001f)pf(ptr(p,12),0x50,(float)r((double)f(ptr(p,0x20),0x124)+.001f));
  thug_shadow_set_position(ptr(p,0x28),at(ptr(p,0x20),0x120));thug_shadow_set_up(ptr(p,0x28),at(ptr(p,0x20),0x130));
  if(word(ptr(ptr(p,0x20),0x1528),0x18)!=4)thug_skater_adjust_light_draft(p,at(ptr(p,0x20),0xa8),q);
  if(word(thug_skater_orientation_context,0x40)!=0xd443a2bc){
   ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);thug_collision_probe_set_flags(&probe,0x810,0);
   float v[4],delta[4];body=ptr(p,12);thug_vector_copy(v,at(body,0x4c));v[1]=(float)r((double)v[1]+3000);thug_collision_probe_start_draft(&probe,v);
   body=ptr(p,12);for(unsigned i=0;i<4;i++)v[i]=(float)r((double)f(body,0x4c+4*i)+f(body,0x7c+4*i));thug_collision_probe_end_draft(&probe,v);
   if(thug_collision_probe_query(&probe,1,0,q)){
    body=ptr(p,12);thug_vector_difference(delta,at(body,0x4c),probe.point);
    double squared=r(r(r((double)delta[0]*delta[0])+r((double)delta[1]*delta[1]))+r((double)delta[2]*delta[2]));
    if(squared<36)thug_vector_copy(at(body,0x4c),probe.point);
    else{
     void *previous=at(ptr(p,0x20),0x98);thug_vector_difference(delta,at(body,0x4c),previous);
     thug_vector_copy(at(body,0x4c),thug_vector_length(delta)<1?probe.point:previous);
     body=ptr(p,12);thug_vector_scaled_copy(delta,at(body,0xac),-.5f);thug_vector_copy(at(body,0xac),delta);
     if(word(ptr(ptr(p,0x20),0x1528),0x18)==4){
      thug_skater_change_state(ptr(p,0x20),1,d,m);thug_object_emit_event(ptr(p,12),0xafaa46ba,0,d,m);
      body=ptr(p,12);pf(body,0x50,(float)r((double)f(body,0x50)+2));
     }
    }
   }
   thug_collision_probe_release(&probe);
  }
  body=ptr(p,12);put(p,0x18,0);thug_vector_copy(at(ptr(p,0x20),0x98),at(body,0x4c));return;
 }
 uint32_t state=word(ptr(ptr(p,0x20),0x1528),0x18);
 if((state!=4&&state!=3)||word(thug_skater_orientation_context,0x40)!=0xd443a2bc){
  ((uint8_t *)p)[0x1c]=1;
  if(!(thug_adjust_initialized_draft&8)){
   thug_adjust_initialized_draft|=8;const float offsets[5][4]={{0,0,0,1},{.1f,.1f,.1f,1},{-.2f,0,0,1},{0,0,-.2f,1},{.2f,0,0,1}};
   __builtin_memcpy(thug_adjust_offsets_draft,offsets,sizeof(offsets));
  }
  int32_t index=(int32_t)word(p,0x18);
  if(index<5){
   const float *offset=thug_adjust_offsets_draft[index];put(p,0x18,(uint32_t)index+1);physics=ptr(p,0x20);
   x=r((double)offset[0]+f(physics,0x98));y=r((double)f(physics,0x9c)+offset[1]);z=r((double)f(physics,0xa0)+offset[2]);w=r((double)f(physics,0xa4)+offset[3]);
   body=ptr(p,12);pf(body,0x54,(float)z);pf(body,0x58,(float)w);pf(body,0x4c,(float)x);pf(body,0x50,(float)y);
  }else put(p,0x18,0);
  body=ptr(p,12);x=-f(body,0xac);y=-f(body,0xb0);z=-f(body,0xb4);w=-f(body,0xb8);
  x=r(x+.101f);y=r(y+.101f);z=r(z+0x1.9a0276p-4f);pf(body,0xb4,(float)z);w=r(w+1);pf(body,0xb8,(float)w);pf(body,0xac,(float)x);pf(body,0xb0,(float)y);
  state=word(ptr(ptr(p,0x20),0x1528),0x18);if(state!=0&&state!=1)thug_skater_change_state(ptr(p,0x20),1,d,m);
 }
 put(ptr(p,0x30),0x11c,0);
}
/* 004f8c40. Transition byte is compared with exactly1, not merely nonzero. */
void thug_skater_adjust_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 void *state=ptr(ptr(p,0x20),0x1528);
 if((word(state,0x18)==0||f(ptr(p,12),0xb0)<0)&&byte(state,0x60)!=1){((uint8_t *)state)[0x60]=1;put(state,0x64,thug_elapsed_time()+thug_timer_offset);}
 if(!byte(ptr(ptr(p,0x20),0x1528),0x88))thug_skater_adjust_escape_draft(p,q,d,m);
 thug_skater_adjust_ground_draft(p,q,d,m);void *body=ptr(p,12);thug_vector_copy(at(body,0x5c),at(body,0x4c));
}
