/* Original ledge-jump collision scan and callback-aware state transition.
 * The surrounding complete ground/Walk update remains unfinished. */
#include "../../src/game/collision_events.h"
#include "../../src/game/moving_contact.h"
#include "../../src/game/stats.h"
#include "../../src/script/delivery.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void pb(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
extern double thug_walk_gravity_draft(void);
extern void thug_walk_change_state_draft(void *,uint32_t);
extern void thug_walk_leave_platform_draft(void *,float[4],float *,const ThugMemory *);
extern float *thug_walk_probe_direction_draft(const void *,float[4],uint32_t);
/* 0052bc70,1545 bytes. First find clear high rays, then lower them to estimate
 * ledge height. Script callbacks may cancel the jump or change its live owner. */
uint8_t thug_walk_ledge_jump_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 if(byte(ptr(ptr(p,0x178c),0x1528),0x70))return 0;
 const unsigned directions[3]={0,1,6};
 float high=parameter(0xda85f5ae),radius=(float)R((double)parameter(0x99978d2b)*3);
 float step=(float)R(R((double)high-parameter(0x6da7f696))*.1111111119389534f);
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 float extent=(float)R((double)radius+1),upper=(float)R((double)high+1),lo[4],hi[4];
 hi[0]=(float)R((double)extent+number(p,0x24));hi[1]=(float)R((double)upper+number(p,0x28));hi[2]=(float)R((double)extent+number(p,0x2c));hi[3]=(float)R((double)number(p,0x30)+1);
 lo[0]=(float)R((double)number(p,0x24)-extent);lo[1]=number(p,0x28);lo[2]=(float)R((double)number(p,0x2c)-extent);lo[3]=(float)R((double)number(p,0x30)-1);
 ThugBounds bounds;thug_collision_segment_copy(bounds.min,lo,hi);
 ThugCollisionCache cache;thug_collision_cache_initialize(&cache);thug_collision_cache_build(&cache,&bounds);probe.cache=&cache;
 uint8_t found=0;
 for(unsigned i=0;i<3;i++){
  unsigned offset=directions[i]*0xcc;
  if(!byte(p,0xa0+offset)||(byte(p,0x10c+offset)&2))continue;
  double cosine=thug_platform_cos(R((double)parameter(0x78e6a5ec)*.01745329238474369f));
  double dot=R(R(R((double)number(p,0x8c)*number(p,0xac+offset))+R((double)number(p,0x88)*number(p,0xa8+offset)))+R((double)number(p,0x84)*number(p,0xa4+offset)));
  if(dot<=-cosine){
   copy4(probe.segment,(char *)p+0x24);probe.segment[1]=(float)R((double)number(p,0x28)+high);
   float ray[4];thug_walk_probe_direction_draft(p,ray,directions[i]);double delta[4];
   for(unsigned k=0;k<4;k++){delta[k]=R((double)radius*ray[k]);if(k<3)delta[k]=(float)delta[k];}
   for(unsigned k=0;k<4;k++)probe.segment[4+k]=(float)R(delta[k]+probe.segment[k]);
   uint8_t clear=!thug_collision_probe_query(&probe,1,0,query);pb(p,0xb4+offset,clear);if(clear)found=1;
  }else pb(p,0xb4+offset,0);
 }
 if(found){
  float lowest=(float)R((double)high+number(p,0x28));
  for(unsigned i=0;i<3;i++){
   unsigned index=directions[i],offset=index*0xcc;
   if(!byte(p,0xa0+offset)||!byte(p,0xb4+offset))continue;
   copy4(probe.segment,(char *)p+0x24);probe.segment[1]=(float)R((double)number(p,0x28)+high);
   /* This inline path keeps the cosine wide, unlike the high-ray helper. */
   double angle=R((double)index*.8975979089736938f),cosine=thug_platform_cos(angle),sine=thug_platform_sin(angle);
   float x=(float)R(R(cosine*number(p,0x48))-R(sine*number(p,0x50)));
   float dz=(float)R(R(R(cosine*number(p,0x50))+R(sine*number(p,0x48)))*radius);
   float dy=(float)R((double)radius*0.0),dx=(float)R((double)x*radius);
   probe.segment[4]=(float)R((double)dx+probe.segment[0]);probe.segment[5]=(float)R((double)probe.segment[1]+dy);
   probe.segment[6]=(float)R((double)probe.segment[2]+dz);probe.segment[7]=(float)R((double)probe.segment[3]+radius);
   for(unsigned n=8;n;--n){
    probe.segment[1]=(float)R((double)probe.segment[1]-step);probe.segment[5]=(float)R((double)probe.segment[5]-step);
    if(thug_collision_probe_query(&probe,1,0,query))break;
   }
   if(probe.segment[1]<lowest)lowest=probe.segment[1];
  }
  float rise=(float)R(R(R((double)parameter(0x72660978)+lowest)+step)-number(p,0x28));
  double half=R(thug_walk_gravity_draft()*rise);float speed=(float)R(__builtin_sqrt(R(half+half)));
  uint8_t cancelled=0;
  if(byte(p,0x1864)){
   const uint32_t events[3]={2,4,0};
   thug_collision_event_from_probe(ptr(p,0x177c),events,(void *)((char *)p+0x17b4),diagnostics,memory);
   cancelled=byte(ptr(p,0x1780),0x26);
  }
  if(!cancelled){
   fp(p,0x44,speed);thug_walk_change_state_draft(p,1);copy4((char *)p+0x1878,(char *)p+0x48);
   thug_walk_leave_platform_draft(p,(void *)((char *)p+0x34),(void *)((char *)p+0x44),memory);
   put(p,0x78,0x584cf9e9);thug_object_broadcast_event(ptr(p,12),0x8687163a,0,0,diagnostics,memory);
   thug_object_remove_event(ptr(p,12),0x6b9ca247,memory);
  }
 }
 thug_collision_cache_destroy(&cache);
 if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
 return found;
}
#include "../../src/core/timing.h"
extern uint8_t thug_walk_try_rail_draft(void *,uint32_t,ThugCollisionQuery *,const ThugMemory *);
static double xyz_squared(double x,double y,double z){return R(R(R(x*x)+R(y*y))+R(z*z));}
static double zyx_dot(const float a[4],const float b[4]){return R(R(R((double)a[2]*b[2])+R((double)a[1]*b[1]))+R((double)a[0]*b[0]));}
static void push_position(void *p,const float normal[4],double distance){
 double delta[4];for(unsigned i=0;i<4;i++)delta[i]=R(distance*normal[i]);
 for(unsigned i=0;i<4;i++)fp(p,0x24+i*4,R(delta[i]+number(p,0x24+i*4)));
}
static void stop_horizontal(void *p){
 put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);
 float limit=parameter(0x0bd6a05d);if(limit<number(p,0x704))fp(p,0x704,limit);pb(p,0x186c,1);
}
/* 0052c2c0,3107 bytes. Seven radial rays and an airborne sweep produce retained
 * contacts. Resolve ledge/rail gates, penetration and ordered velocity constraints. */
uint8_t thug_walk_resolve_contacts_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 float radius=parameter(0x99978d2b),height=parameter(0x6da7f696);uint8_t any=0,result=0;
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 for(unsigned i=0;i<8;i++){
  void *contact=(char *)p+0xa0+i*0xcc;
  if(i==7){
   if(word(p,0x18)!=1){pb(contact,0,0);continue;}
   float dt=number(p,0x80);
   for(unsigned k=0;k<4;k++)probe.segment[k]=(float)R((double)number(p,0x24+k*4)+number(p,0x71c+k*4));
   for(unsigned k=0;k<4;k++){float d=(float)R((double)number(p,0x80)*number(p,0x34+k*4));probe.segment[4+k]=(float)R((double)d+probe.segment[k]);}
   float rise=(float)R((double)number(p,0x44)*number(p,0x80));double gravity=thug_walk_gravity_draft();
   probe.segment[5]=(float)R(R((double)rise-R(R(R((double)dt*dt)*gravity)*.5f))+probe.segment[5]);
  }else{
   copy4(probe.segment,(char *)p+0x24);probe.segment[1]=(float)R((double)number(p,0x28)+height);
   double angle=R((double)i*.8975979089736938f),cosine=thug_platform_cos(angle),sine=thug_platform_sin(angle);
   float x=(float)R(R(cosine*number(p,0x48))-R(sine*number(p,0x50)));
   float dz=(float)R(R(R(sine*number(p,0x48))+R(cosine*number(p,0x50)))*radius);
   float dy=(float)R((double)radius*0),dx=(float)R((double)x*radius);
   probe.segment[4]=(float)R((double)dx+number(p,0x24));probe.segment[5]=(float)R((double)(float)R((double)dy+number(p,0x28))+height);
   probe.segment[6]=(float)R((double)dz+number(p,0x2c));probe.segment[7]=(float)R((double)radius+number(p,0x30));
  }
  uint8_t hit=thug_collision_probe_query(&probe,1,0,query);pb(contact,0,hit);if(!hit)continue;
  if(i==7&&probe.normal[1]>.7070000171661377f){pb(contact,0,0);continue;}
  thug_collision_probe_assign((void *)((char *)contact+0x1c),&probe);
  copy4((char *)contact+4,probe.normal);put(contact,8,0);any=1;
  double length=R(__builtin_sqrt(xyz_squared(number(contact,4),number(contact,8),number(contact,12))));
  if(length>0){double inverse=R(1/length);for(unsigned k=0;k<3;k++)fp(contact,4+k*4,R(inverse*number(contact,4+k*4)));}
  uint8_t same=0;
  if(thug_collision_probe_has_moving_object(&probe)){
   ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *platform=gate->contact;
   if(platform){
    if(!platform->reference.object)thug_skater_moving_contact_release(gate,memory);
    else same=platform->reference.object==thug_collision_probe_moving_object(&probe);
   }
   if(!same){void *owner=thug_collision_probe_moving_object(&probe);fp(contact,0x18,zyx_dot((void *)((char *)owner+0xac),(void *)((char *)contact+4)));}
   else put(contact,0x18,0);
  }else put(contact,0x18,0);
 }
 if(word(p,0x18)==0){
  if((byte(p,0xa0)||byte(p,0x16c)||byte(p,0x568))&&byte(p,0x98)){
   if(!byte(p,0x17a8)){put(p,0x17ac,thug_elapsed_time()+thug_timer_offset);pb(p,0x17a8,1);}
   uint32_t start=word(p,0x17ac);float delay=parameter(0x38d36700);uint32_t elapsed=thug_elapsed_time()+thug_timer_offset-start;
   double time=(int32_t)elapsed;if((int32_t)elapsed<0)time=R(time+4294967296.0f);
   if(time>delay&&(thug_walk_try_rail_draft(p,0,query,memory)||thug_walk_ledge_jump_draft(p,query,diagnostics,memory)))goto done;
  }else pb(p,0x17a8,0);
  if(byte(ptr(p,0x1770),0x100)&&!byte(p,0x9a)&&thug_walk_try_rail_draft(p,1,query,memory))goto done;
  if(byte(ptr(p,0x1780),0x26))goto done;
  if(word(p,0x18)==0&&number(p,0x1798)<.5f){
   float normal[4]={number(p,0x1794),0,number(p,0x179c),number(p,0x17a0)};
   double length=R(__builtin_sqrt(R(R((double)normal[0]*normal[0])+R((double)normal[2]*normal[2]))));
   if(length>0){double inverse=R(1/length);for(unsigned k=0;k<3;k++)normal[k]=(float)R((double)normal[k]*inverse);}
   double distance=R((double)parameter(0x4d16f37d)*number(p,0x80));push_position(p,normal,distance);
  }
 }
 if(!any)goto done;
 for(unsigned i=0;i<8;i++){
  void *contact=(char *)p+0xa0+i*0xcc;if(!byte(contact,0))continue;
  float fraction=number(contact,0x90);double minimum=R((double)parameter(0xa20c43b7)/radius);
  if(fraction<minimum){double distance=R((double)parameter(0x4d16f37d)*number(p,0x80));push_position(p,(void *)((char *)contact+4),distance);}
 }
 uint8_t constrained=0;
 for(unsigned i=0;i<8;i++){
  void *contact=(char *)p+0xa0+i*0xcc;if(!byte(contact,0))continue;
  double dot=R(R(R((double)number(p,0x3c)*number(contact,12))+R((double)number(contact,4)*number(p,0x34)))+R((double)number(p,0x38)*number(contact,8)));
  if(dot<number(contact,0x18))constrained=1;else pb(contact,0,0);
 }
 if(!constrained)goto done;
 result=1;
 for(unsigned i=0;i<8;i++)if(byte(p,0xa0+i*0xcc)){
  for(unsigned j=i+1;j<8;j++)if(byte(p,0xa0+j*0xcc)&&zyx_dot((void *)((char *)p+0xa4+i*0xcc),(void *)((char *)p+0xa4+j*0xcc))<=0){stop_horizontal(p);goto done;}
 }
 double x=number(p,0x34),w=number(p,0x40);float y=number(p,0x38),z=number(p,0x3c);
 const unsigned order[8]={7,4,3,5,2,6,1,0};
 for(unsigned i=0;i<8;i++){
  void *contact=(char *)p+0xa0+order[i]*0xcc;if(!byte(contact,0))continue;
  double dot=R(R(R((double)z*number(contact,12))+R((double)y*number(contact,8)))+R(x*number(contact,4)));
  if(dot<number(contact,0x18)){
   double amount=R(dot-number(contact,0x18));float dw=(float)R(amount*number(contact,16)),dz=(float)R(amount*number(contact,12)),dy=(float)R(amount*number(contact,8));
   x=R(x-R(amount*number(contact,4)));y=(float)R((double)y-dy);z=(float)R((double)z-dz);w=R(w-dw);
   double alignment=R(R(R((double)z*number(p,0x3c))+R((double)y*number(p,0x38)))+R(x*number(p,0x34)));
   if(alignment<=0){stop_horizontal(p);goto done;}
  }
 }
 float stored_w=(float)w;
 double length=R(__builtin_sqrt(R(R(R(x*x)+R((double)z*z))+R((double)y*y))));float stored_length=(float)length;
 if(length>=.0001){
  double inverse=R(1/(double)stored_length);float direction[4]={(float)R(inverse*x),(float)R((double)y*inverse),(float)R((double)z*inverse),(float)R(w*inverse)};
  float projection=(float)zyx_dot(direction,(void *)((char *)p+0x34));
  if(stored_length>projection){stored_w=(float)R((double)direction[3]*projection);z=(float)R((double)direction[2]*projection);y=(float)R((double)direction[1]*projection);x=R((double)direction[0]*projection);}
 }else{x=0;y=0;z=0;stored_w=1;}
 double original_squared=xyz_squared(number(p,0x34),number(p,0x38),number(p,0x3c));
 if(original_squared>=1e-8){double new_squared=R(R(R(x*x)+R((double)z*z))+R((double)y*y));pb(p,0x186c,R(new_squared/original_squared)<.25f);}else pb(p,0x186c,0);
 fp(p,0x34,x);fp(p,0x38,y);fp(p,0x3c,z);fp(p,0x40,stored_w);
 float speed=(float)R(__builtin_sqrt(xyz_squared(number(p,0x34),number(p,0x38),number(p,0x3c))));
 float limit=parameter(0x0bd6a05d);
 if(number(p,0x704)>limit){fp(p,0x704,speed);limit=parameter(0x0bd6a05d);if(limit>number(p,0x704))fp(p,0x704,limit);}
 done:
 if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
 return result;
}
extern void thug_walk_follow_platform_draft(void *,const ThugMemory *);
extern void thug_walk_prepare_cache_draft(void *);
extern void thug_walk_accelerate_draft(void *,float[4],ThugCollisionQuery *);
extern void thug_walk_face_velocity_draft(void *);
extern uint32_t *thug_skater_construction_boundary_draft;
/* PREFIX ONLY of0052d300. Preserve genuine state-change returns; continuing
 * ground movement stops explicitly before the unrecovered floor handler. */
void thug_walk_ground_contacts_prefix_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 thug_walk_follow_platform_draft(p,memory);thug_walk_prepare_cache_draft(p);thug_walk_accelerate_draft(p,(void *)((char *)p+0x34),query);
 if(word(p,0x78)==0x1d537eff&&number(p,0x1870)<parameter(0x8e1cf27a))put(p,0x78,0x9b46e749);
 if(thug_walk_resolve_contacts_draft(p,query,diagnostics,memory))thug_walk_face_velocity_draft(p);else pb(p,0x186c,0);
 pb(p,0x1958,0);
 if(word(p,0x18)||byte(ptr(p,0x1780),0x26)){thug_collision_default_cache=0;return;}
 double dx=R((double)number(p,0x80)*number(p,0x34));float dy=(float)R((double)number(p,0x80)*number(p,0x38)),dz=(float)R((double)number(p,0x80)*number(p,0x3c)),dw=(float)R((double)number(p,0x80)*number(p,0x40));
 fp(p,0x24,R(dx+number(p,0x24)));fp(p,0x28,R((double)dy+number(p,0x28)));fp(p,0x2c,R((double)dz+number(p,0x2c)));fp(p,0x30,R((double)dw+number(p,0x30)));
 uint32_t *boundary=thug_skater_construction_boundary_draft;
 if(boundary){boundary[0]=0x52b370;boundary[1]=0;boundary[2]=(uintptr_t)p;boundary[3]=1;}__builtin_trap();
}
