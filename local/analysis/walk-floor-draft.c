/* Original transitions used when walking leaves the floor.
 * Floor handling and ledge selection are still being recovered. */
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
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static uint8_t byte(const void *p,unsigned o){return ((const uint8_t *)p)[o];}
static void pb(void *p,unsigned o,uint8_t v){((uint8_t *)p)[o]=v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void copy4(void *p,const void *s){for(unsigned i=0;i<4;i++)put(p,i*4,word(s,i*4));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
extern void thug_walk_change_state_draft(void *,uint32_t);
extern void thug_walk_prepare_facing_draft(void *,const float[4],uint32_t);
extern uint8_t thug_walk_find_rail_draft(const ThugObjectTransform *,const float[4],float,float,uint32_t,void *,float[8],void **,ThugCollisionQuery *);
/* 00441190,194 bytes. Callback target for a top-side rail entry. */
void thug_walk_enter_rail_top_draft(void *p){
 void *node=ptr(p,0x1764),*next=ptr(node,0x40);if(!next)next=ptr(node,0x44);
 float from[4],to[4];thug_rail_point(ptr(p,0x176c),from,node);thug_rail_point(ptr(p,0x176c),to,next);
 double x=R((double)to[0]-from[0]),y=R((double)to[1]-from[1]),z=R((double)to[2]-from[2]);
 float length=(float)R(__builtin_sqrt(R(R(R(z*z)+R(y*y))+R(x*x))));
 float offset=parameter(0x76bf49e0);fp(p,0x18cc,R(R((double)length-offset)/length));
 thug_walk_change_state_draft(p,3);if(word(p,0x1764))put(ptr(p,0x178c),0x22c,word(p,0x1764));
}
/* 00441fc0,420 bytes. Select a near-vertical rail from its upper end. */
uint8_t thug_walk_try_rail_top_draft(void *p,ThugCollisionQuery *query,const ThugMemory *memory){
 if(byte(ptr(ptr(p,0x178c),0x1528),0x70))return 0;
 float height=parameter(0xc4c164e8),radius=parameter(0xa2735dd9),target[8];
 if(!thug_walk_find_rail_draft(thug_game_context->rail_transform,(void *)((char *)p+0x24),radius,height,0,p,target,(void **)((char *)p+0x1764),query))return 0;
 put(p,0x176c,(uintptr_t)thug_game_context->rail_transform);thug_skater_moving_contact_release(ptr(p,0x1784),memory);
 put(p,0x44,0);put(p,0x34,0);put(p,0x38,0);put(p,0x3c,0);put(p,0x40,0x3f800000);
 copy4((char *)p+0x18e4,(char *)p+0x24);copy4((char *)p+0x1904,target);
 put(p,0x1948,(uintptr_t)thug_walk_enter_rail_top_draft);put(p,0x194c,0);put(p,0x1950,0);put(p,0x1954,0);
 put(p,0x1914,word(p,0x9c));put(p,0x1918,0);thug_walk_prepare_facing_draft(p,target+4,0x3f800000);
 put(p,0x1944,1);copy4((char *)p+0x18b4,target+4);put(p,0x18c8,word(p,0x28));
 thug_walk_change_state_draft(p,4);put(p,0x78,0xd63adcad);return 1;
}
/* 0043dc00,91 bytes. Remaining model animation blend supplies the grab height. */
double thug_walk_ledge_blend_height_draft(const void *p){
 void *model=ptr(ptr(p,0x1778),0x208);if(!(byte(model,0x44)&8))return 0;
 float progress=number(model,0x20),height=parameter(0xa8c13e74);return R(R(1.0-progress)*height);
}
/* 0043dc60,136 bytes. Required hang height minus scaled model height. */
double thug_walk_hang_height_draft(void){
 float height=parameter(0xde86132e),scale=parameter(0x7201ad48),model=parameter(0xa8c13e74);
 return R((double)height-R((double)model*scale));
}
/* 0043dcf0,214 bytes. Enter hanging state and deliver the actual rail script. */
void thug_walk_enter_hang_draft(void *p,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 float offset=parameter(0xc3263e6e);for(unsigned i=0;i<4;i++)fp(p,0x71c+i*4,R((double)offset*number(p,0x48+i*4)));
 fp(p,0x720,thug_walk_hang_height_draft());thug_walk_change_state_draft(p,2);
 if(word(p,0x1764))put(ptr(p,0x178c),0x22c,word(p,0x1764));
 if(word(p,0x176c))put(ptr(p,0x178c),0x230,word(p,0x176c));
 const uint32_t events[3]={10,3,0};
 thug_skater_rail_event(ptr(p,0x178c),events,diagnostics,memory);
 pb(thug_object_find_component(ptr(p,12),0x380d909a),0x1d,0);
}
/* 0057cb20,62 bytes. Arbitrary rail-space vector, with forward-copy overlap. */
float *thug_rail_transform_vector_draft(const ThugObjectTransform *rail,float out[4],const float in[4]){
 if(!rail->changed){copy4(out,in);return out;}thug_matrix_transform_vector(rail->matrix,out,in);return out;
}
/* 0057c540,original forward thirteen-word assignment, including overlap. */
void thug_ledge_target_copy_draft(void *out,const void *in){for(unsigned i=0;i<13;i++)put(out,i*4,word(in,i*4));}
/* 005299f0,750 bytes. Fixed/moving grind selection and final collision clearance. */
uint8_t thug_walk_try_grind_draft(void *p,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 if(byte(ptr(p,0x1780),0x24))return 0;
 float *point=(void *)((char *)p+0x74c);ThugRailNode **selected=(void *)((char *)p+0x760);
 uint8_t found=thug_rail_search(thug_game_context->rail_transform,(void *)((char *)p+0x68),(void *)((char *)p+0x24),point,selected,0,1,0,query);
 if(found){put(p,0x75c,(uintptr_t)thug_game_context->rail_transform);put(p,0x764,0);}
 else{
  put(p,0x74,0x3f800000);put(p,0x30,0x3f800000);
  ThugTransformComponent *component=thug_component_type_head(thug_component_type_registry,0x1cdfb2a3);
  if(!component)return 0;
  for(;component;component=(void *)(uintptr_t)component->unknown_14){
   if(found)break;
   float world[16],inverse[16],from[4],to[4];thug_component_world_transform(component,world);thug_matrix_copy(inverse,world);thug_matrix_inverse(inverse);
   thug_matrix_transform_vector(inverse,from,(void *)((char *)p+0x68));thug_matrix_transform_vector(inverse,to,(void *)((char *)p+0x24));
   ThugAttachmentProvider *provider=(void *)component;ThugObjectTransform *rail=(void *)provider->methods->points(provider);
   found=thug_rail_search(rail,from,to,point,selected,0,1,0,query);
   if(found){
    put(p,0x75c,(uintptr_t)provider->methods->points(provider));float transformed[4];thug_matrix_transform_vector(world,transformed,point);copy4(point,transformed);put(p,0x764,(uintptr_t)component->base.owner);
   }
  }
 }
 if(!found||!thug_skater_rail_eligible(ptr(p,0x178c),*selected,word(p,0x75c),1))return 0;
 ThugCollisionProbe probe;thug_collision_probe_from_points(&probe,(void *)((char *)p+0x24),point);
 uint8_t result=0;
 if(thug_collision_probe_query(&probe,1,0,query)){
  double z=R((double)point[2]-probe.point[2]),y=R((double)point[1]-probe.point[1]),x=R((double)point[0]-probe.point[0]);
  if(R(R(R(x*x)+R(y*y))+R(z*z))>36.0f)goto done;
 }
 thug_skater_track_movement(2,(void *)((char *)p+0x68),(void *)((char *)p+0x24),diagnostics);
 put(p,0x748,1);put(p,0x78,0xa6a3147e);result=1;
 done:thug_collision_probe_release(&probe);return result;
}
/* 0043ddd0,490 bytes. Check both directions of the vertical hang clearance. */
uint8_t thug_walk_hang_vertical_clear_draft(void *p,ThugCollisionProbe *probe,const float target[13],const float side[4],ThugCollisionQuery *query){
 (void)p;float lateral=parameter(0xafbf7687),offset[4];for(unsigned i=0;i<4;i++)offset[i]=(float)R((double)lateral*side[i]);
 float forward=parameter(0xc3263e6e);
 float x=(float)R(R((double)forward*target[4])+target[0]);
 double y=R(R((double)forward*target[5])+target[1]);
 float z=(float)R((double)forward*target[6]),w=(float)R((double)forward*target[7]);
 z=(float)R((double)z+target[2]);w=(float)R((double)w+target[3]);
 probe->segment[0]=(float)R((double)x+offset[0]);probe->segment[1]=(float)R(y+offset[1]);probe->segment[2]=(float)R((double)z+offset[2]);probe->segment[3]=(float)R((double)w+offset[3]);
 copy4((probe->segment+4),probe->segment);float height=parameter(0xa8c13e74);double hang=thug_walk_hang_height_draft();
 probe->segment[1]=(float)R(R((double)probe->segment[1]-height)+hang);float above=parameter(0x8f35f29f);(probe->segment+4)[1]=(float)R((double)above+(probe->segment+4)[1]);
 if(thug_collision_probe_query(probe,1,0,query))return 0;
 float from[4];copy4(from,probe->segment);copy4(probe->segment,(probe->segment+4));copy4((probe->segment+4),from);
 return !thug_collision_probe_query(probe,1,0,query);
}
/* 0057c5a0,81 bytes. Coordinate-wise one-unit coincidence, low-byte result. */
uint8_t thug_rail_nodes_coincident_draft(const void *rail,const ThugRailNode *a,const ThugRailNode *b){
 (void)rail;for(unsigned i=0;i<3;i++)if(__builtin_fabs(R((double)a->position[i]-b->position[i]))>1.0)return 0;return 1;
}
static uint8_t clear_nodes(const ThugObjectTransform *rail,const ThugRailNode *a,const ThugRailNode *b,ThugCollisionQuery *query){
 float from[4],to[4];thug_rail_point(rail,to,b);thug_rail_point(rail,from,a);
 return thug_rail_clearance(from[0],from[1],from[2],from[3],to[0],to[1],to[2],to[3],query);
}
/* 0057e170,341 bytes. First clear outgoing/incoming rail at a coincident node. */
uint8_t thug_rail_find_coincident_draft(const ThugObjectTransform *rail,const ThugRailNode *source,uint32_t skip_flags,ThugRailNode **out,ThugCollisionQuery *query){
 for(int32_t i=0;i<(int32_t)word(rail,0x48);i++){
  ThugRailNode *node=(void *)((char *)ptr(rail,0x40)+(uint32_t)i*0x54);
  if(!thug_rail_nodes_coincident_draft(rail,node,source)||(!node->next&&!node->previous)||node==source)continue;
  if(node->next&&(node->flags&4)&&!(node->flags&skip_flags)&&clear_nodes(rail,node,node->next,query)){*out=node;return 1;}
  if(node->previous&&(node->previous->flags&4)&&!(node->previous->flags&skip_flags)&&clear_nodes(rail,node->previous,node,query)){*out=node->previous;return 1;}
 }
 return 0;
}
/* 0043e230,753 bytes. Follow connected ledges, or an angle-compatible duplicate. */
uint8_t thug_walk_follow_ledge_draft(void *p,float *fraction,ThugRailNode *start,ThugRailNode *end,ThugRailNode **out_start,ThugRailNode **out_end,ThugCollisionQuery *query,const ThugDiagnostics *diagnostics){
 ThugRailNode *found=0;
 if(*fraction<0){
  ThugRailNode *previous=start->previous;
  if(previous&&(previous->flags&4)&&!(previous->flags&8)&&clear_nodes(ptr(p,0x176c),previous,start,query)){*out_end=start;*out_start=start->previous;return 1;}
  if(!thug_rail_find_coincident_draft(ptr(p,0x176c),start,0x28,&found,query))return 0;
 }else{
  if(end->next&&(end->flags&4)&&!(end->flags&8)&&clear_nodes(ptr(p,0x176c),end,end->next,query)){*out_start=end;*out_end=end->next;return 1;}
  if(!thug_rail_find_coincident_draft(ptr(p,0x176c),end,0x28,&found,query))return 0;
 }
 uint8_t same=thug_rail_nodes_coincident_draft(ptr(p,0x176c),found,end)||thug_rail_nodes_coincident_draft(ptr(p,0x176c),found->next,start);
 float from[4],to[4],direction[4],candidate[4];thug_rail_point(ptr(p,0x176c),from,start);thug_rail_point(ptr(p,0x176c),to,end);
 thug_vector_difference(direction,to,from);thug_vector_normalize(direction);
 ThugRailNode *next=found->next;thug_rail_point(ptr(p,0x176c),from,found);thug_rail_point(ptr(p,0x176c),to,next);
 thug_vector_difference(candidate,to,from);thug_vector_normalize(candidate);
 double x=candidate[0],y=candidate[1],z=candidate[2];if(!same){x=R(x*-1.0);y=R(y*-1.0);z=R(z*-1.0);}
 double dot=R(R(R((double)direction[2]*z)+R(y*direction[1]))+R(x*direction[0]));
 if(dot<-0.8659999966621399){diagnostics->print(diagnostics->context,"M:%s:%i: %s\n","omponents\\WalkHangUtil.cpp",0x4f2,"BAD ANGLE ON COINCIDENT RAIL");return 0;}
 if(!same)*fraction=(float)R(1.0-*fraction);
 *out_start=found;*out_end=found->next;
 diagnostics->print(diagnostics->context,"M:%s:%i: %s\n","omponents\\WalkHangUtil.cpp",0x4fc,"FOUND COINCIDENT RAIL");return 1;
}
