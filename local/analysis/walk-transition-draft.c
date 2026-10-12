/* Original Walk state transitions and vertical-rail entry helpers.
 * Full ground/Walk updates and playable integration remain unfinished. */
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/timing.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void pb(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
/* 005284c0,149 bytes. The enabled gameplay flag also records its use. */
double thug_walk_gravity_draft(void){
 if(!thug_gameplay_flag(thug_game_context->gameplay_flags,0x9c8c6df1))return parameter(0xa5e2da58);
 thug_gameplay_flag_set(thug_game_context->gameplay_flags,thug_script_get_global_integer(0x9c8c6df1,0));
 thug_last_gameplay_flag=1;return R((double)parameter(0xa5e2da58)*.5f);
}
/* 005260e0,384 bytes. Preserve unchanged states and reset only original fields. */
void thug_walk_change_state_draft(void *p,uint32_t state){
 uint32_t previous=word(p,0x18);if(state==previous)return;
 put(p,0x20,previous);put(p,0x18,state);put(p,0x1c,thug_elapsed_time()+thug_timer_offset);
 if(previous==0||previous==1){pb(p,0x17a8,0);pb(p,0x17a4,0);}
 if(previous==1){put(p,0x1898,0);put(p,0x189c,0);put(p,0x18a0,0);put(p,0x18a4,0);put(p,0x18a8,0x3f800000);pb(p,0x9b,0);}
 state=word(p,0x18);
 if(state==0){put(p,0x1870,0x461c4000);pb(p,0x1874,1);}
 if(state==4){put(p,0x1934,0);put(p,0x1938,0);put(p,0x193c,0);put(p,0x1940,0x3f800000);}
 state=word(p,0x18);if(state!=1)pb(p,0x18b0,0);
 if(state==0||word(p,0x20)!=1)pb(p,0x186c,0);
 if(state==2){
  put(p,0x18dc,0);
  if(word(p,0x20)==1){
   void *input=(char *)ptr(p,0x1770)+0x20;
   float seconds=parameter(0xac96d24b);uint32_t now=thug_frame_time();put(input,0x230,now-thug_truncate_double_low_word(R((double)seconds*-1000.0f)));
   seconds=parameter(0xac96d24b);now=thug_frame_time();put(input,0x234,now-thug_truncate_double_low_word(R((double)seconds*-1000.0f)));
  }
 }
}
/* 0052ab90,376 bytes. Carry platform velocity into the separate horizontal and
 * vertical outputs, move away when aligned, then release the retained contact. */
void thug_walk_leave_platform_draft(void *p,float velocity[4],float *vertical,const ThugMemory *memory){
 ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *contact=gate->contact;
 if(contact&&!contact->reference.object){thug_skater_moving_contact_release(gate,memory);contact=0;}
 if(!contact){put(p,0x1888,0);put(p,0x188c,0);put(p,0x1890,0);put(p,0x1894,0x3f800000);}
 else{
  copy4((char *)p+0x1888,(char *)contact->reference.object+0xac);
  double dot=R(R(R((double)number(p,0x1890)*velocity[2])+R((double)number(p,0x188c)*velocity[1]))+R((double)number(p,0x1888)*velocity[0]));
  if(dot>0){
   float frame=number(p,0x80);double x=R((double)frame*number(p,0x1888));float y=(float)R((double)frame*number(p,0x188c)),z=(float)R((double)frame*number(p,0x1890)),w=(float)R((double)frame*number(p,0x1894));
   fp(p,0x24,R(x+number(p,0x24)));fp(p,0x28,R((double)y+number(p,0x28)));fp(p,0x2c,R((double)z+number(p,0x2c)));fp(p,0x30,R((double)w+number(p,0x30)));
  }
  *vertical=(float)R((double)number(p,0x188c)+*vertical);put(p,0x188c,0);
  for(unsigned i=0;i<4;i++)velocity[i]=(float)R((double)number(p,0x1888+i*4)+velocity[i]);
 }
 thug_skater_moving_contact_release(ptr(p,0x1784),memory);
}
#include "../../src/core/matrix.h"
/* 00527720,139 bytes. Keep the wide angle through wrap selection, then store
 * the original forward copy and the raw interpolation weight. */
void thug_walk_prepare_facing_draft(void *p,const float direction[4],uint32_t weight){
 double to=thug_platform_atan2(direction[0],direction[2]),from=thug_platform_atan2(number(p,0x48),number(p,0x50));
 double delta=R(to-from);fp(p,0x1930,delta);
 if(__builtin_fabs(delta)>3.1415927410125732f)fp(p,0x1930,R(delta-R((delta<0?-1.0:1.0)*6.2831854820251465f)));
 copy4((char *)p+0x191c,direction);put(p,0x192c,weight);
}
/* 00528220,84 bytes. Probe rays use the signed integer direction index and preserve
 * the cosine spill before multiplying the current facing direction. */
float *thug_walk_probe_direction_draft(const void *p,float out[4],uint32_t direction_index){
 double angle=R((double)(int32_t)direction_index*.8975979089736938f);float cosine=(float)thug_platform_cos(angle);double sine=thug_platform_sin(angle);
 float x=(float)R(R((double)cosine*number(p,0x48))-R(sine*number(p,0x50)));
 double z=R(R(sine*number(p,0x48))+R((double)cosine*number(p,0x50)));
 out[1]=0;out[3]=1;out[0]=x;out[2]=(float)z;return out;
}
extern void thug_quaternion_basis_draft(const float q[4],float out[16]);
/* 0057cfb0,212 bytes. Rail-node quaternion orientation, optionally transformed
 * by its owning rail graph; the original affine lanes are initialized explicitly. */
float *thug_rail_orientation_draft(const ThugObjectTransform *transform,float out[16],const void *node){
 float basis[16],world[16];thug_quaternion_basis_draft((const float *)((const char *)node+0x30),basis);
 basis[3]=basis[7]=basis[11]=basis[12]=basis[13]=basis[14]=0;basis[15]=1;
 if(transform->changed){thug_matrix_multiply(world,transform->matrix,basis);return thug_matrix_copy(out,world);}
 return thug_matrix_copy(out,basis);
}
/* 004410c0,200 bytes. Establish rail traversal speed from the world-space
 * segment, enter state3 and retain the original rail node in the physics owner. */
void thug_walk_enter_rail_draft(void *p){
 void *node=ptr(p,0x1764),*next=ptr(node,0x40);if(!next)next=ptr(node,0x44);
 float from[4],to[4];thug_rail_point(ptr(p,0x176c),from,node);thug_rail_point(ptr(p,0x176c),to,next);
 float x=(float)R((double)to[0]-from[0]),y=(float)R((double)to[1]-from[1]),z=(float)R((double)to[2]-from[2]);
 float speed=parameter(0x5296e3fd);double length=R(__builtin_sqrt(R(R(R((double)z*z)+R((double)y*y))+R((double)x*x))));
 fp(p,0x18cc,R((double)speed/length));thug_walk_change_state_draft(p,3);
 if(word(p,0x1764))put(ptr(p,0x178c),0x22c,word(p,0x1764));
}
#include "../../src/core/vector.h"
#include "../../src/collision/moving.h"
/* 00441260,369 bytes. The upper end of a near-vertical rail supplies an exit
 * position offset along its segment and away from its orientation normal. */
uint8_t thug_walk_rail_exit_target_draft(const float start[4],const float end[4],const float matrix[16],float out[8]){
 if(start[1]>end[1])return 0;
 float direction[4];for(unsigned i=0;i<4;i++)direction[i]=(float)R((double)end[i]-start[i]);thug_vector_normalize(direction);
 if(direction[1]<.9950000047683716f)return 0;
 float distance=parameter(0x76bf49e0);double target[4];
 for(unsigned i=0;i<4;i++){double delta=R((double)direction[i]*distance);if(i)delta=(float)delta;target[i]=R((double)end[i]-delta);}
 out[3]=(float)target[3];for(unsigned i=0;i<3;i++)out[i]=(float)target[i];
 distance=parameter(0x35b3bbda);double delta[4];for(unsigned i=0;i<4;i++){delta[i]=R((double)distance*matrix[8+i]);if(i>=2)delta[i]=(float)delta[i];}
 for(unsigned i=0;i<4;i++)out[i]=(float)R((double)out[i]-delta[i]);copy4(out+4,matrix+8);return 1;
}
/* 004418b0,706 bytes. Ground-side rail entry checks slope, facing and a real
 * collision segment. Failed clearance retains the already computed position. */
uint8_t thug_walk_rail_entry_target_draft(const void *p,const float start[4],const float end[4],const float matrix[16],float out[8],ThugCollisionQuery *query){
 if(start[1]>end[1])return 0;
 float direction[4];for(unsigned i=0;i<4;i++)direction[i]=(float)R((double)end[i]-start[i]);thug_vector_normalize(direction);
 if(direction[1]<.9950000047683716f)return 0;
 double threshold=thug_platform_cos(R((double)parameter(0x456f216d)*.01745329238474369f));
 double dot=R(R(R((double)matrix[10]*number(p,0x50))+R((double)matrix[9]*number(p,0x4c)))+R((double)matrix[8]*number(p,0x48)));
 if(dot<threshold)return 0;
 float distance=parameter(0x5296e3fd);double target[4];
 for(unsigned i=0;i<4;i++){double delta=R((double)direction[i]*distance);if(i<3)delta=(float)delta;target[i]=R(delta+start[i]);}
 for(unsigned i=0;i<4;i++)out[i]=(float)target[i];
 distance=parameter(0x35b3bbda);double delta[4];for(unsigned i=0;i<4;i++)delta[i]=R((double)distance*matrix[8+i]);
 for(unsigned i=0;i<4;i++)out[i]=(float)R((double)out[i]-delta[i]);
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);copy4(probe.segment,(const char *)p+0x24);
 for(unsigned i=0;i<4;i++){double offset=R((double)matrix[8+i]*6.0f);if(i<3)offset=(float)offset;probe.segment[4+i]=(float)R((double)out[i]-offset);}
 uint8_t hit=thug_collision_probe_query(&probe,1,0,query);
 if(!hit)copy4(out+4,matrix+8);
 if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
 return !hit;
}
/* 0057d880,407 bytes. Walk rail selection scans nodes in reverse, preserves
 * original radius/height gates and uses real entry/exit target calculations. */
uint8_t thug_walk_find_rail_draft(const ThugObjectTransform *rail,const float origin[4],float radius,float height,uint32_t entering,void *walk,float out[8],void **selected,ThugCollisionQuery *query){
 float squared=(float)R((double)radius*radius);uint32_t count=(uint32_t)rail->rail_count;
 for(uint32_t i=count;i;){
  void *node=(char *)rail->rail_nodes+(--i)*0x54;uint32_t flags=word(node,0x48);if(!(flags&0x20)||!(flags&4))continue;
  float *position=(void *)((char *)node+0x20);
  if(__builtin_fabs(R((double)position[0]-origin[0]))>radius||__builtin_fabs(R((double)position[2]-origin[2]))>radius||__builtin_fabs(R((double)position[1]-origin[1]))>height)continue;
  double x=R((double)position[0]-origin[0]),z=R((double)position[2]-origin[2]);if(R(R(z*z)+R(x*x))>squared)continue;
  void *next=ptr(node,0x40);if(!next)next=ptr(node,0x44);float matrix[16];
  if((uint8_t)entering){thug_rail_orientation_draft(rail,matrix,node);if(thug_walk_rail_entry_target_draft(walk,position,(float *)((char *)next+0x20),matrix,out,query)){*selected=node;return 1;}}
  else{thug_rail_orientation_draft(rail,matrix,next);if(thug_walk_rail_exit_target_draft((float *)((char *)next+0x20),position,matrix,out)){*selected=next;return 1;}}
 }
 return 0;
}
/* 00441de0,479 bytes. A successful rail search releases the moving contact,
 * initializes the interpolation/callback record and enters the original state4. */
uint8_t thug_walk_try_rail_draft(void *p,uint32_t forced,ThugCollisionQuery *query,const ThugMemory *memory){
 if(((uint8_t *)ptr(ptr(p,0x178c),0x1528))[0x70])return 0;
 float radius=parameter((uint8_t)forced?0x0eecd255:0xa2735dd9),height=parameter(0xc4c164e8),target[8];
 if(!thug_walk_find_rail_draft(thug_game_context->rail_transform,(float *)((char *)p+0x24),radius,height,1,p,target,(void **)((char *)p+0x1764),query))return 0;
 put(p,0x176c,(uintptr_t)thug_game_context->rail_transform);thug_skater_moving_contact_release(ptr(p,0x1784),memory);
 put(p,0x44,0);put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);
 put(p,0x1948,(uintptr_t)thug_walk_enter_rail_draft);put(p,0x194c,0);put(p,0x1950,0);put(p,0x1954,0);put(p,0x1914,word(p,0x9c));put(p,0x1918,0);
 thug_walk_prepare_facing_draft(p,target+4,0x3f800000);put(p,0x1944,1);copy4((char *)p+0x18b4,target+4);put(p,0x18c8,word(target,4));
 thug_walk_change_state_draft(p,4);put(p,0x78,0xe2524194);return 1;
}
