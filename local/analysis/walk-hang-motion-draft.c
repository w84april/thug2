/* Ledge traversal and corner-facing updates from the original walking engine. */
#include "../../src/game/rail.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/vector.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static void copy4(void *out,const void *in){for(unsigned i=0;i<4;i++)put(out,4*i,word(in,4*i));}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
extern double thug_walk_hang_height_draft(void);
extern uint8_t thug_walk_follow_ledge_draft(void *,float *,ThugRailNode *,ThugRailNode *,ThugRailNode **,ThugRailNode **,ThugCollisionQuery *,const ThugDiagnostics *);
extern uint8_t thug_walk_hang_side_blocked_draft(void *,const float[4],float,const float[4],uint32_t,const float[4],float,float,float,float,ThugRailNode *,ThugRailNode *,ThugCollisionQuery *,const ThugDiagnostics *);
/* 005250a0: invalidate interpolation after a sharp ledge corner. */
void thug_walk_hang_reset_orientation_draft(void *p){
 void *walk=ptr(p,0xa0);*((uint8_t *)p+0x1c)=1;*((uint8_t *)walk+0x70c)=1;
 put(ptr(p,0x90),0x24,0);put(ptr(p,0x90),0x20,0);put(ptr(p,0x90),0x1c,0x3f800000);*((uint8_t *)ptr(p,0x90)+0x18)=0;
}
/* 0043dfc0: carry remaining travel onto a new ledge and choose its facing. */
void thug_walk_hang_corner_draft(void *p,float distance,uint32_t reverse,const float previous[4]){
 float from[4],to[4],delta[4];thug_rail_point(ptr(p,0x176c),to,ptr(p,0x1768));thug_rail_point(ptr(p,0x176c),from,ptr(p,0x1764));
 for(unsigned i=0;i<4;i++)delta[i]=(float)R((double)from[i]-to[i]);
 float xx=(float)R((double)delta[0]*delta[0]);double length=R(__builtin_sqrt(R(R(R((double)delta[2]*delta[2])+R((double)delta[1]*delta[1]))+xx)));
 if(distance>length)distance=(float)length;double fraction=R((double)distance/length);fp(p,0x18cc,fraction);if((uint8_t)reverse)fp(p,0x18cc,R(1-fraction));
 float normal[3]={-delta[2],0,delta[0]};length=R(__builtin_sqrt(R(R((double)normal[0]*normal[0])+xx)));
 if(length>0){double inverse=R(1/length);for(unsigned i=0;i<3;i++)normal[i]=(float)R((double)normal[i]*inverse);}
 double z=(uint8_t)reverse?-(double)delta[2]:delta[2],x=(uint8_t)reverse?-(double)delta[0]:delta[0];
 double old_cross=R(R((double)previous[2]*number(p,0x48))-R((double)number(p,0x50)*previous[0]));
 double new_cross=R(R((double)normal[0]*z)-R((double)normal[2]*x));
 if(R(new_cross*old_cross)<0)for(unsigned i=0;i<3;i++)normal[i]=-normal[i];
 double dot=R(R(R((double)normal[2]*number(p,0x50))+R((double)normal[1]*number(p,0x4c)))+R((double)normal[0]*number(p,0x48)));
 if(thug_platform_cos(1.0471975803375244)>dot)thug_walk_hang_reset_orientation_draft(ptr(p,0x1760));
 for(unsigned i=0;i<3;i++)fp(p,0x48+i*4,normal[i]);put(p,0x54,0x3f800000);
 float offset=parameter(0xc3263e6e);for(unsigned i=0;i<4;i++)fp(p,0x71c+i*4,R((double)offset*number(p,0x48+i*4)));fp(p,0x720,thug_walk_hang_height_draft());
}
/* 00440130: side clearance, connected-ledge traversal and collision rollback. */
void thug_walk_hang_traverse_draft(void *p,float step,ThugCollisionQuery *q,const ThugDiagnostics *d){
 float saved_position[4],saved_offset[4],saved_facing[4],start[4],from[4],to[4],delta[4];
 copy4(saved_position,(char *)p+0x24);copy4(saved_offset,(char *)p+0x71c);copy4(saved_facing,(char *)p+0x48);
 for(unsigned i=0;i<4;i++)start[i]=(float)R((double)number(p,0x24+i*4)+number(p,0x71c+i*4));
 uint32_t old_fraction=word(p,0x18cc),old_start=word(p,0x1764),old_end=word(p,0x1768);float side[4]={-saved_facing[2],0,saved_facing[0],1};
 thug_rail_point(ptr(p,0x176c),to,ptr(p,0x1768));thug_rail_point(ptr(p,0x176c),from,ptr(p,0x1764));
 double wide[4];for(unsigned i=0;i<4;i++){wide[i]=R((double)from[i]-to[i]);delta[i]=(float)wide[i];}
 uint8_t positive=step>0;double dot=R(R(R((double)side[0]*wide[0])+R(wide[2]*saved_facing[0]))+R(wide[1]*0));uint8_t advancing=dot<0?positive:!positive;
 if(thug_walk_hang_side_blocked_draft(p,saved_facing,number(p,0x18cc),saved_position,positive,side,delta[0],delta[1],delta[2],delta[3],ptr(p,0x1764),ptr(p,0x1768),q,d)){
  put(p,0x18dc,0);put(p,0x78,0x4194ecca);return;
 }
 double squared=R(R(R((double)delta[0]*delta[0])+R((double)delta[1]*delta[1]))+R((double)delta[2]*delta[2]));float stored_squared=(float)squared;
 double change=R(__builtin_fabs((double)step)/R(__builtin_sqrt(squared)));if(!advancing)change=-change;
 double fraction=R(change+number(p,0x18cc));fp(p,0x18cc,fraction);uint8_t stopped=0;
 if(fraction<0||fraction>1){
  if(!thug_walk_follow_ledge_draft(p,(float *)((char *)p+0x18cc),ptr(p,0x1764),ptr(p,0x1768),(void *)((char *)p+0x1764),(void *)((char *)p+0x1768),q,d)){
   float value=number(p,0x18cc);if(value>1)value=1;else if(value<0)value=0;fp(p,0x18cc,value);put(p,0x18dc,0);put(p,0x78,0x4194ecca);stopped=1;
  }else{
   float value=number(p,0x18cc),clamped=value;if(clamped>1)clamped=1;else if(clamped<0)clamped=0;
   float remaining=(float)R(__builtin_fabs(R((double)value-clamped))*R(__builtin_sqrt((double)stored_squared)));
   float direction[4];for(unsigned i=0;i<4;i++)direction[i]=advancing?delta[i]:-delta[i];
   thug_walk_hang_corner_draft(p,remaining,number(p,0x18cc)<0,direction);
  }
 }
 if(!stopped)put(p,0x78,0x279b1f0b+(positive?0x05fcf6b8:0));
 ThugCollisionProbe probe;thug_collision_probe_initialize(&probe);copy4(probe.segment,start);
 for(unsigned i=0;i<4;i++)probe.segment[4+i]=(float)R((double)number(p,0x71c+i*4)+number(p,0x24+i*4));
 if(thug_collision_probe_query(&probe,1,0,q)){
  copy4((char *)p+0x24,saved_position);put(p,0x18cc,old_fraction);put(p,0x1764,old_start);put(p,0x1768,old_end);
  copy4((char *)p+0x71c,saved_offset);copy4((char *)p+0x48,saved_facing);put(p,0x18dc,0);put(p,0x78,0x4194ecca);
 }
 thug_collision_probe_release(&probe);
}
