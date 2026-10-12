/* Original ledge-selection graph; surrounding floor/Walk work remains incomplete. */
#include "../../src/game/stats.h"
#include "../../src/game/rail.h"
#include "../../src/game/attachment.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
extern void thug_walk_change_state_draft(void *,uint32_t);
extern void thug_walk_prepare_facing_draft(void *,const float[4],uint32_t);
extern uint8_t thug_walk_find_rail_draft(const ThugObjectTransform *,const float[4],float,float,uint32_t,void *,float[8],void **,ThugCollisionQuery *);
#include "../../src/game/grind.h"
extern double thug_walk_hang_height_draft(void);
extern uint8_t thug_walk_follow_ledge_draft(void *,float *,ThugRailNode *,ThugRailNode *,ThugRailNode **,ThugRailNode **,ThugCollisionQuery *,const ThugDiagnostics *);
extern uint8_t thug_walk_hang_vertical_clear_draft(void *,ThugCollisionProbe *,const float[13],const float[4],ThugCollisionQuery *);
static void add_scaled(float out[4],const float direction[4],float scale){for(unsigned i=0;i<4;i++)out[i]=(float)R(R((double)scale*direction[i])+out[i]);}
/* 0043f3a0,2243 bytes. Five successive side-clearance probes; one hit blocks. */
uint8_t thug_walk_hang_side_blocked_draft(void *p,const float normal[4],float fraction,const float position[4],uint32_t side_flag,const float perpendicular[4],float dx,float dy,float dz,float dw,ThugRailNode *node,ThugRailNode *next,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 uint8_t side=(uint8_t)side_flag;double dot=R(R(R((double)dy*perpendicular[1])+R((double)dx*perpendicular[0]))+R((double)dz*perpendicular[2]));
 uint8_t endpoint=dot<0?side:!side;float lateral[4],facing[4];
 for(unsigned i=0;i<4;i++)lateral[i]=side?perpendicular[i]:-perpendicular[i];copy4(facing,normal);
 double factor=endpoint?R(1.0-fraction):fraction;
 double length=R(__builtin_sqrt(R(R(R((double)dz*dz)+R((double)dy*dy))+R((double)dx*dx))));
 float distance=(float)R(length*factor),reach=parameter(0x3344a6d0);
 if(distance<R((double)reach+1)){
  fraction=(float)R((endpoint?2.0:-2.0)+fraction);ThugRailNode *start,*end;
  if(thug_walk_follow_ledge_draft(p,&fraction,node,next,&start,&end,query,diagnostics)){
   float sign=fraction<=.5?1:-1,from[4],to[4],tangent[4];thug_rail_point(ptr(p,0x176c),from,end);thug_rail_point(ptr(p,0x176c),to,start);
   float x=(float)R((double)to[0]-from[0]),z=(float)R((double)to[2]-from[2]);double w=R((double)to[3]-from[3]);
   tangent[0]=(float)R((double)x*sign);tangent[1]=0;tangent[2]=(float)R((double)z*sign);tangent[3]=(float)R(w*sign);thug_vector_normalize(tangent);
   double facing_dot=R(R(R((double)tangent[1]*normal[1])+R((double)tangent[2]*normal[2]))+R((double)tangent[0]*normal[0]));
   if(facing_dot<0&&facing_dot>-.8700000047683716){copy4(lateral,tangent);facing[0]=side?tangent[2]:-tangent[2];facing[2]=side?-tangent[0]:tangent[0];}
  }
 }
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);copy4(probe.segment,position);
 float above=parameter(0x84ff931c);probe.segment[1]=(float)R((double)probe.segment[1]+above);
 float behind=parameter(0xcbeb3d89);for(unsigned i=0;i<4;i++)probe.segment[i]=(float)R((double)probe.segment[i]-R((double)behind*normal[i]));
 copy4(probe.segment+4,probe.segment);reach=parameter(0x3344a6d0);add_scaled(probe.segment+4,lateral,reach);
 uint8_t result=1;if(thug_collision_probe_query(&probe,1,0,query))goto done;
 copy4(probe.segment+4,probe.segment);above=parameter(0xc774dd6d);probe.segment[5]=(float)R((double)probe.segment[5]+above);
 reach=parameter(0x3344a6d0);add_scaled(probe.segment+4,lateral,reach);if(thug_collision_probe_query(&probe,1,0,query))goto done;
 copy4(probe.segment+4,probe.segment);above=parameter(0xc774dd6d);probe.segment[5]=(float)R(R((double)above*.5)+probe.segment[5]);
 reach=parameter(0x3344a6d0);add_scaled(probe.segment+4,lateral,reach);if(thug_collision_probe_query(&probe,1,0,query))goto done;
 copy4(probe.segment+4,probe.segment);above=parameter(0x84ff931c);double hang=thug_walk_hang_height_draft();probe.segment[5]=(float)R(R(R(hang-above)-1)+probe.segment[5]);
 float forward=parameter(0xc3263e6e);add_scaled(probe.segment+4,facing,forward);reach=parameter(0x3344a6d0);add_scaled(probe.segment+4,lateral,reach);
 float edge[4]={dx,dy,dz,dw};thug_vector_normalize(edge);for(unsigned i=0;i<4;i++){float offset=endpoint?-edge[i]:edge[i];probe.segment[4+i]=(float)R((double)probe.segment[4+i]+offset);}
 if(thug_collision_probe_query(&probe,1,0,query))goto done;
 copy4(probe.segment+4,probe.segment);probe.segment[5]=(float)R((double)probe.segment[5]-R(thug_walk_parameter(0,0xc774dd6d)*.5));
 float scaled[4];thug_vector_scaled(scaled,(float)thug_walk_parameter(0,0xc3263e6e),facing);thug_vector_add(probe.segment+4,scaled);
 thug_vector_scaled(scaled,(float)thug_walk_parameter(0,0x3344a6d0),lateral);thug_vector_add(probe.segment+4,scaled);
 result=thug_collision_probe_query(&probe,1,0,query)!=0;
 done:thug_collision_probe_release(&probe);return result;
}
/* 0043fe30,754 bytes. Clearance on each side and a reachable hanging target. */
uint8_t thug_walk_hang_target_draft(void *p,ThugCollisionProbe *probe,const float point[4],float target[13],ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 copy4(target,point);float nx=target[4],side[4]={-target[6],0,nx,1};float start[4],end[4],delta[4];
 ThugRailNode *node=ptr(target,0x30);thug_rail_point(ptr(p,0x176c),end,node->next);thug_rail_point(ptr(p,0x176c),start,node);thug_vector_difference(delta,start,end);
 if(!thug_walk_hang_vertical_clear_draft(p,probe,target,side,query))return 0;
 float opposite[4]={-side[0],0,-nx,-1};if(!thug_walk_hang_vertical_clear_draft(p,probe,target,opposite,query))return 0;
 float height=parameter(0xa8c13e74);target[1]=(float)R((double)target[1]-height);float offset=parameter(0x262a9467);add_scaled(target,target+4,offset);
 node=ptr(target,0x30);
 if(thug_walk_hang_side_blocked_draft(p,target+4,target[8],target,1,side,delta[0],delta[1],delta[2],delta[3],node,node->next,query,diagnostics))return 0;
 node=ptr(target,0x30);
 if(thug_walk_hang_side_blocked_draft(p,target+4,target[8],target,0,side,delta[0],delta[1],delta[2],delta[3],node,node->next,query,diagnostics))return 0;
 float scaled[4],destination[4];thug_vector_scaled(scaled,(float)thug_walk_parameter(0,0xc3263e6e),target+4);thug_vector_sum(destination,target,scaled);
 destination[1]=(float)R(thug_walk_hang_height_draft()+destination[1]);copy4(probe->segment,(char *)p+0x24);copy4(probe->segment+4,destination);
 if(!thug_collision_probe_query(probe,1,0,query))return 1;
 if(word(p,0x18)==0){
  copy4(probe->segment+4,(char *)p+0x24);probe->segment[5]=(float)R(thug_walk_parameter(0,0xa85ec070)+probe->segment[5]);
  if(!thug_collision_probe_query(probe,1,0,query)){copy4(probe->segment,probe->segment+4);copy4(probe->segment+4,destination);if(!thug_collision_probe_query(probe,1,0,query))return 1;}
 }
 return 0;
}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void flip_normal(float n[4]){for(unsigned i=0;i<3;i++)n[i]=-n[i];}
/* 00440690,1372 bytes. Choose a usable side, with a real automatic collision cache. */
uint8_t thug_walk_choose_ledge_draft(void *p,const float from[4],const float to[4],const float point[4],const float other[4],float fraction,float target[13],uint32_t side_flag,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 float height=parameter(0xa8c13e74);
 if(word(p,0x18)==1){if(other[1]<point[1]||__builtin_fabs(R((double)point[1]-other[1]))>12)return 0;}
 float delta[4];thug_vector_difference(delta,to,from);float dx=delta[0],dz=delta[2];thug_vector_normalize(delta);
 float slope=parameter(0x98724ebc);if(__builtin_fabs((double)delta[1])>thug_platform_sin(R((double)slope*.01745329238474369f)))return 0;
 float *normal=target+4;normal[0]=-dz;normal[1]=0;normal[2]=dx;normal[3]=1;thug_vector_normalize(normal);
 uint8_t side=(uint8_t)side_flag;
 double dot=R(R(R((double)number(p,0x50)*normal[2])+R((double)number(p,0x4c)*normal[1]))+R((double)number(p,0x48)*normal[0]));
 if((!side&&dot<0)||(side&&dot>0))flip_normal(normal);
 uint8_t left=R(R((double)delta[0]*normal[2])-R((double)delta[2]*normal[0]))>0;
 uint32_t flags=word(ptr(target,0x30),0x48);if(((flags&0x80)&&left)||((flags&0x40)&&!left)){left=!left;flip_normal(normal);}
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);ThugCollisionCache cache;thug_collision_cache_initialize(&cache);
 float lo[4],hi[4],upper=(float)R((double)height+12);
 hi[0]=(float)R((double)point[0]+24);hi[1]=(float)R((double)upper+point[1]);hi[2]=(float)R((double)point[2]+24);hi[3]=(float)R((double)point[3]+1);
 for(unsigned i=0;i<4;i++)lo[i]=(float)R((double)point[i]-(i==3?1:24));
 ThugBounds bounds;thug_collision_segment_copy(bounds.min,lo,hi);thug_collision_cache_build(&cache,&bounds);probe.cache=&cache;target[8]=fraction;
 uint8_t result=thug_walk_hang_target_draft(p,&probe,point,target,query,diagnostics);
 if(!result){
  flags=word(ptr(target,0x30),0x48);
  if((word(p,0x18)==1||!side)&&(!(flags&0x80)||left)&&(!(flags&0x40)||!left)){
   flip_normal(normal);result=thug_walk_hang_target_draft(p,&probe,point,target,query,diagnostics);
  }
 }
 if(result){
  target[10]=(float)R((double)target[1]-point[1]);
  double z=R((double)target[2]-point[2]),y=R((double)target[1]-point[1]),x=R((double)target[0]-point[0]);
  target[9]=(float)R(R(R(y*normal[1])+R(z*normal[2]))+R(x*normal[0]));
  float offset=parameter(0xc3263e6e);
  for(unsigned i=0;i<4;i++){double product=R((double)offset*normal[i]);if(i<3)product=(float)product;probe.segment[i]=(float)R(product+target[i]);}
  float above=parameter(0xdbb3d53e);probe.segment[1]=(float)R((double)probe.segment[1]+above);copy4(probe.segment+4,probe.segment);
  offset=parameter(0x2f83ae83);add_scaled(probe.segment+4,normal,offset);
  uint32_t hit=thug_collision_probe_query(&probe,1,0,query)!=0;put(target,44,((0u-hit)&0xcd20c764u)+0x1ee948a5u);
 }
 thug_collision_cache_destroy(&cache);thug_collision_probe_release(&probe);return result;
}
#include "../../src/core/line.h"
extern float *thug_rail_transform_vector_draft(const ThugObjectTransform *,float[4],const float[4]);
extern void thug_ledge_target_copy_draft(void *,const void *);
extern double thug_walk_ledge_blend_height_draft(const void *);
extern void thug_walk_enter_hang_draft(void *,const ThugDiagnostics *,const ThugMemory *);
/* 0057dda0,969 bytes. Rank eligible segments and verify the full hanging target. */
uint8_t thug_walk_scan_ledge_draft(const ThugObjectTransform *world,const float from[4],const float to[4],const float direction[4],void *p,float out[13],float radius,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 float line[8],lo[4],hi[4];thug_segment_initialize(line);copy4(line,from);copy4(line+4,to);thug_segment_bounds(line,line+4,lo,hi);
 for(unsigned j=0;j<3;j++){lo[j]=(float)R((double)lo[j]-radius);hi[j]=(float)R((double)hi[j]+radius);}
 float best;uint32_t initial=0x56b5e621;__builtin_memcpy(&best,&initial,4);float radius_squared=(float)R((double)radius*radius);uint8_t found=0;
 for(int32_t i=0;i<world->rail_count;i++){
  ThugRailNode *node=world->rail_nodes+i;
  if((node->flags&0x28)||!(node->flags&4)||!node->next)continue;
  if(lo[0]>node->maximum[0]||hi[0]<node->minimum[0]||lo[2]>node->maximum[2]||hi[2]<node->minimum[2]||lo[1]>node->maximum[1]||hi[1]<node->minimum[1])continue;
  float rail[8],linepoint[4],railpoint[4],ta,tb;thug_segment_initialize(rail);copy4(rail,node->position);copy4(rail+4,node->next->position);
  if(!thug_segment_closest_points(line,rail,linepoint,railpoint,&ta,&tb,1))continue;
  float delta[4];thug_vector_difference(delta,railpoint,linepoint);if(thug_vector_length_squared(delta)>radius_squared)continue;
  double dot=R(R(R((double)delta[2]*direction[2])+R((double)delta[1]*direction[1]))+R((double)delta[0]*direction[0]));
  if(dot>0){float offset[4];thug_vector_scaled(offset,(float)R(dot*.6666666865348816f),direction);thug_vector_add(delta,offset);}
  double weighted=thug_vector_length_squared(delta);float stored=(float)weighted;if(weighted>best)continue;
  float start[4],end[4];thug_rail_point(world,end,node->next);thug_rail_point(world,start,node);
  if(!thug_rail_clearance(start[0],start[1],start[2],start[3],end[0],end[1],end[2],end[3],query))continue;
  float target[13],point[4],other[4];put(target,48,(uintptr_t)node);
  thug_rail_transform_vector_draft(world,other,linepoint);thug_rail_transform_vector_draft(world,point,railpoint);
  thug_rail_point(world,end,node->next);thug_rail_point(world,start,node);
  if(thug_walk_choose_ledge_draft(p,start,end,point,other,tb,target,0,query,diagnostics)){best=stored;thug_ledge_target_copy_draft(out,target);found=1;}
 }
 return found;
}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
/* 0043ec40,1007 bytes. Fixed/moving ledge grab and transition into its animation. */
uint8_t thug_walk_try_hang_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 if(byte(ptr(ptr(p,0x178c),0x1528),0x70))return 0;
 float scale=parameter(0x01d1e6af);double limit=R(thug_skater_transfer_speed(p)*scale);
 double x=number(p,0x34),y=number(p,0x38),z=number(p,0x3c);
 if(R(limit*limit)<R(R(R(x*x)+R(y*y))+R(z*z)))return 0;
 void *hang=thug_object_find_component(ptr(p,12),0x380d909a);if(byte(hang,0x1c))return 0;
 put(p,0x74,0x3f800000);put(p,0x30,0x3f800000);put(p,0x176c,(uintptr_t)thug_game_context->rail_transform);
 float direction[4],target[13];for(unsigned j=0;j<4;j++)direction[j]=-number(p,0x48+j*4);
 float radius=(float)thug_script_get_global_number(0xa8276303,0);
 uint8_t found=thug_walk_scan_ledge_draft(ptr(p,0x176c),(void *)((char *)p+0x68),(void *)((char *)p+0x24),direction,p,target,radius,query,diagnostics);
 if(found)thug_skater_moving_contact_release(ptr(p,0x1784),memory);
 else{
  ThugTransformComponent *component=thug_component_type_head(thug_component_type_registry,0x1cdfb2a3);
  if(!component)return 0;
  for(;component;component=(void *)(uintptr_t)component->unknown_14){
   if(found)break;
   float inverse[16],from[4],to[4];thug_component_world_transform(component,inverse);thug_matrix_inverse(inverse);
   thug_matrix_transform_vector(inverse,from,(void *)((char *)p+0x68));thug_matrix_transform_vector(inverse,to,(void *)((char *)p+0x24));
   ThugAttachmentProvider *provider=(void *)component;put(p,0x176c,(uintptr_t)provider->methods->points(provider));
   for(unsigned j=0;j<4;j++)direction[j]=-number(p,0x48+j*4);radius=(float)thug_script_get_global_number(0xa8276303,0);
   found=thug_walk_scan_ledge_draft(ptr(p,0x176c),from,to,direction,p,target,radius,query,diagnostics);
   if(found)thug_skater_moving_contact_set_owner(ptr(p,0x1784),component->base.owner,memory);
  }
 }
 if(!found)return 0;
 put(p,0x1764,word(target,48));put(p,0x1768,word(ptr(target,48),0x40));put(p,0x44,0);put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);
 put(p,0x18cc,word(target,32));put(p,0x18d4,word(target,36));put(p,0x18d0,word(target,40));((uint8_t *)hang)[0x1d]=1;
 copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);put(p,0x1948,(uintptr_t)thug_walk_enter_hang_draft);put(p,0x194c,0);put(p,0x1950,0);put(p,0x1954,0);
 float speed=parameter(0xfdc8aec0);uint32_t speed_bits;__builtin_memcpy(&speed_bits,&speed,4);thug_walk_prepare_facing_draft(p,target+4,speed_bits);put(p,0x1944,1);
 float offset=parameter(0xc3263e6e);for(unsigned j=0;j<4;j++)fp(p,0x71c+j*4,R((double)offset*target[4+j]));
 copy4((char *)p+0x18b4,target+4);put(p,0x18c8,word(p,0x28));put(p,0x1914,word(p,0x9c));fp(p,0x1918,thug_walk_ledge_blend_height_draft(p));
 thug_walk_change_state_draft(p,4);put(p,0x78,0xeb71d98e);return 1;
}
