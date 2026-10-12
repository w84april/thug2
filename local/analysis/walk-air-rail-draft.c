/* Airborne near-vertical rail catch: target, nearest candidate and transition. */
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/line.h"
#include "../../src/core/vector.h"
#include "../../src/core/timing.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
extern float *thug_rail_orientation_draft(const ThugObjectTransform *,float[16],const void *);
extern void thug_walk_change_state_draft(void *,uint32_t);
/* 0057c500: ordered word copies also preserve forward-overlap behavior. */
void *thug_rail_catch_copy_draft(void *out,const void *in){for(unsigned i=0;i<9;i++)put(out,4*i,word(in,4*i));return out;}
/* 004413e0: a catch between the lower/upper margins needs a clear segment. */
uint8_t thug_walk_air_rail_target_draft(void *p,const float lower[4],const float upper[4],const float matrix[16],const float point[4],float fraction,float out[9],ThugCollisionQuery *query){
 double z=R((double)upper[2]-lower[2]),x=R((double)upper[0]-lower[0]);
 float y=(float)R((double)upper[1]-lower[1]),normalized=y;
 double length=R(__builtin_sqrt(R(R(R(x*x)+R((double)y*y))+R(z*z))));
 if(length>0)normalized=(float)R((double)y*R(1.0/length));
 if(normalized<.9950000047683716f)return 0;
 if(R(R((double)normalized*parameter(0x5296e3fd))+lower[1])>point[1])return 0;
 if(R((double)upper[1]-R((double)normalized*parameter(0x76bf49e0)))<point[1])return 0;
 float offset=parameter(0x35b3bbda);double delta[4];
 for(unsigned i=0;i<4;i++){delta[i]=R((double)offset*matrix[8+i]);if(i<3)delta[i]=(float)delta[i];}
 /* The original loads all point lanes before writing the destination. */
 float position[4];for(unsigned i=0;i<4;i++)position[i]=(float)R((double)point[i]-delta[i]);
 thug_vector_copy(out,position);
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);
 thug_vector_copy(probe.segment,(void *)((char *)p+0x24));thug_vector_copy(probe.segment+4,out);
 uint8_t hit=thug_collision_probe_query(&probe,1,0,query);
 if(!hit){
  for(unsigned i=0;i<4;i++)put(out,16+4*i,word(matrix,32+4*i));put(out,32,word(&fraction,0));
  uint8_t *state=ptr(ptr(p,0x178c),0x1528);
  if(state[0xa0]!=1){state[0xa0]=1;put(state,0xa4,thug_elapsed_time()+thug_timer_offset);}
 }
 if(probe.moving_object.object)thug_object_reference_unlink(probe.moving_object.object,&probe.moving_object);
 return !hit;
}
/* 0057da20: scan forward; an equal-distance later candidate replaces the first. */
uint8_t thug_walk_air_rail_search_draft(const ThugObjectTransform *world,const float from[4],const float to[4],void *p,float out[9],ThugRailNode **selected,ThugCollisionQuery *query){
 *selected=0;float line[8],minimum[4],maximum[4];thug_segment_initialize(line);
 thug_vector_copy(line,from);thug_vector_copy(line+4,to);thug_segment_bounds(line,line+4,minimum,maximum);
 double radius=thug_script_get_global_number(0x30ce7f2c,0);
 for(unsigned i=0;i<3;i++){minimum[i]=(float)R((double)minimum[i]-radius);maximum[i]=(float)R((double)maximum[i]+radius);}
 float radius_squared=(float)R(radius*radius),best;uint32_t best_bits=0x56b5e621;__builtin_memcpy(&best,&best_bits,4);
 for(int32_t i=0;i<world->rail_count;i++){
  ThugRailNode *node=(ThugRailNode *)world->rail_nodes+i;
  if(!(node->flags&0x20)||!(node->flags&4)||!node->next)continue;
  if(minimum[0]>node->maximum[0]||maximum[0]<node->minimum[0]||minimum[2]>node->maximum[2]||maximum[2]<node->minimum[2]||minimum[1]>node->maximum[1]||maximum[1]<node->minimum[1])continue;
  float rail[8],line_point[4],rail_point[4],line_fraction,fraction;thug_segment_initialize(rail);
  thug_vector_copy(rail,node->position);thug_vector_copy(rail+4,node->next->position);
  if(!thug_segment_closest_points(line,rail,line_point,rail_point,&line_fraction,&fraction,1))continue;
  float difference[4];thug_vector_difference(difference,rail_point,line_point);float distance=(float)thug_vector_length_squared(difference);
  if(node->name==0xf5b17b09||node->next->name==0xf5b17b09)distance=(float)R((double)distance*4.0);
  if(distance>radius_squared||distance>best)continue;
  float matrix[16],target[9];ThugRailNode *lower,*upper;
  if(node->position[1]<node->next->position[1]){lower=node;upper=node->next;}
  else{lower=node->next;upper=node;fraction=(float)R(1.0-fraction);}
  thug_rail_orientation_draft(world,matrix,lower);
  if(!thug_walk_air_rail_target_draft(p,lower->position,upper->position,matrix,rail_point,fraction,target,query))continue;
  *selected=node->position[1]<node->next->position[1]?node:node->next;
  best=distance;thug_rail_catch_copy_draft(out,target);
 }
 return *selected!=0;
}
/* 00442170: catch directly into state3, with no intermediate animation. */
uint8_t thug_walk_air_rail_draft(void *p,const float from[4],const float to[4],ThugCollisionQuery *query,const ThugMemory *memory){
 float target[9];
 if(!thug_walk_air_rail_search_draft(thug_game_context->rail_transform,from,to,p,target,(ThugRailNode **)((char *)p+0x1764),query))return 0;
 put(p,0x176c,(uintptr_t)thug_game_context->rail_transform);thug_skater_moving_contact_release(ptr(p,0x1784),memory);
 thug_vector_copy((void *)((char *)p+0x24),target);thug_vector_copy((void *)((char *)p+0x48),target+4);put(p,0x18cc,word(target,32));
 put(p,0x44,0);put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);thug_walk_change_state_draft(p,3);
 if(word(p,0x1764))put(ptr(p,0x178c),0x22c,word(p,0x1764));put(p,0x78,0xc84243da);return 1;
}
