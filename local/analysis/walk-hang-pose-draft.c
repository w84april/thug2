/* Ledge-hanging input and pose prerequisites. */
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
/* 0043da20: the down-input gate reads the original pad fields directly. */
uint32_t thug_walk_hang_drop_input_draft(const void *pad){
 if(word(pad,0x234)||number(pad,0x22c)==0)return 0;
 return R(3.1415927410125732f-__builtin_fabs((double)number(pad,0x228)))<.7853981852531433f;
}
/* 0043fc70: interpolate the ledge, apply offsets, then follow a rotating contact. */
void thug_walk_hang_pose_draft(void *p,const ThugMemory *m){
 float from[4],to[4],position[4];float fraction=number(p,0x18cc);
 thug_rail_point(ptr(p,0x176c),to,ptr(p,0x1768));thug_rail_point(ptr(p,0x176c),from,ptr(p,0x1764));
 thug_vector_lerp(position,from,to,fraction);for(unsigned i=0;i<4;i++)put(p,0x24+i*4,word(position,i*4));
 fp(p,0x28,R((double)number(p,0x18d0)+number(p,0x28)));
 for(unsigned i=0;i<4;i++){double delta=R((double)number(p,0x18d4)*number(p,0x48+i*4));if(i)delta=(float)delta;fp(p,0x24+i*4,R(delta+number(p,0x24+i*4)));}
 ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *contact=gate->contact;if(!contact)return;
 if(!contact->reference.object){thug_skater_moving_contact_release(gate,m);return;}
 if(!contact->orientation_changed)return;
 thug_rail_point(ptr(p,0x176c),to,ptr(p,0x1768));thug_rail_point(ptr(p,0x176c),from,ptr(p,0x1764));
 float direction[4]={(float)R((double)from[0]-to[0]),0,(float)R((double)from[2]-to[2]),(float)R((double)from[3]-to[3])};thug_vector_normalize(direction);
 double x=-(double)direction[2],dot=R(R(R((double)direction[0]*number(p,0x50))+R(x*number(p,0x48)))+R((double)number(p,0x4c)*0));put(p,0x4c,0);
 if(dot>0){fp(p,0x48,x);fp(p,0x50,direction[0]);put(p,0x54,0x3f800000);}
 else{fp(p,0x48,-x);fp(p,0x50,-(double)direction[0]);put(p,0x54,0xbf800000);}
}
