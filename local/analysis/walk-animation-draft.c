/* Original animation-backed Walk transition and QB completion command. */
#include "../../src/game/animation.h"
#include "../../src/game/moving_contact.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
#include "../../src/script/delivery.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
#define R thug_platform_round_x87_single
/* 004813b0,58 bytes. Preserve the original order when output pointers alias. */
void thug_animation_channel_times_draft(void *p,float *start,float *current,float *end){
 put(current,0,word(p,0x18));
 if(!word(p,0x24)){put(start,0,word(p,0x14));put(end,0,word(p,0x1c));}
 else{put(start,0,word(p,0x1c));put(end,0,word(p,0x14));}
}
/* 0041a0e0,129 bytes. Intrusive-list sentinels are live objects with id=-1. */
void thug_animation_component_times_draft(void *p,float *start,float *current,float *end){
 void *state=ptr(p,0x34);if(word(state,4)==0xffffffff)return;
 float first=0,now=0,last=0;void *channel=ptr(state,0x20);
 if(word(channel,4)!=0xffffffff)thug_animation_channel_times_draft(channel,&first,&now,&last);
 fp(start,0,first);fp(current,0,now);fp(end,0,last);
}
/* 0052ad10,550 bytes. The real transition frame reads the animation timeline;
 * completing the transition still depends on its script/callback lifecycle. */
void thug_walk_transition_frame_draft(void *p,const ThugMemory *memory){
 ThugSkaterGroundGate *gate=ptr(p,0x1784);ThugMovingContact *contact=gate->contact;
 if(contact){
  if(!contact->reference.object||!thug_moving_contact_update(contact,(float *)((char *)p+0x24)))thug_skater_moving_contact_release(gate,memory);
  else{
   contact=((ThugSkaterGroundGate *)ptr(p,0x1784))->contact;
   for(unsigned i=0;i<4;i++)fp(p,0x1934+4*i,R((double)number(p,0x1934+4*i)+contact->displacement[i]));
   contact=((ThugSkaterGroundGate *)ptr(p,0x1784))->contact;
   if(contact->orientation_changed){
    float facing[4];thug_matrix_rotate_vector(contact->rotation,facing,(float *)((char *)p+0x191c));
    __builtin_memcpy((char *)p+0x191c,facing,16);
    if(number(p,0x1920)!=0){put(p,0x1920,0);thug_vector_normalize((float *)((char *)p+0x191c));}
   }
  }
 }
 float start,current,end;thug_animation_component_times_draft(ptr(p,0x1774),&start,&current,&end);
 float progress=(float)R(R((double)current-start)/R((double)end-start));
 float position[4];thug_vector_lerp(position,(float *)((char *)p+0x18e4),(float *)((char *)p+0x1904),progress);
 for(unsigned i=0;i<4;i++)fp(p,0x24+4*i,R((double)position[i]+number(p,0x1934+4*i)));
 double turn=R((double)progress/number(p,0x192c));if(turn>1)turn=1;
 double angle=number(p,0x1930);angle=R(R(angle*turn)-angle);
 __builtin_memcpy((char *)p+0x48,(char *)p+0x191c,16);
 double sine=thug_platform_sin(angle),cosine=thug_platform_cos(angle),x=number(p,0x48),z=number(p,0x50);
 fp(p,0x48,R(R(cosine*x)+R(sine*z)));fp(p,0x50,R(-R(sine*x)+R(cosine*z)));
 put(p,0x78,0x4fe6069c);fp(p,0x9c,R(R(R((double)number(p,0x1918)-number(p,0x1914))*progress)+number(p,0x1914)));
}
extern void thug_walk_enter_hang_draft(void *,const ThugDiagnostics *,const ThugMemory *);
/* 005298d0,280 bytes. Commit the destination to the owner before the callback,
 * retaining the receiver adjustment in the original member-function record. */
void thug_walk_finish_transition_draft(void *p,const ThugDiagnostics *diagnostics,const ThugMemory *memory){
 float position[4];for(unsigned i=0;i<4;i++)position[i]=(float)R((double)number(p,0x1904+4*i)+number(p,0x1934+4*i));
 __builtin_memcpy((char *)ptr(p,12)+0x4c,position,16);
 float basis[16]={number(p,0x1924),0,-number(p,0x191c),1,0,1,0,1,0,0,0,0,0,0,0,1};
 for(unsigned i=0;i<4;i++)put(basis,32+4*i,word(p,0x191c+4*i));
 thug_matrix_copy((float *)((char *)ptr(p,12)+0x6c),basis);put(p,0x9c,word(p,0x1918));
 uintptr_t callback=word(p,0x1948);if(!callback)return;
 void *receiver=(void *)((uintptr_t)p+word(p,0x194c));
 /* Port ABI bridge: hanging requires scoped host services; the rail entries
  * retain the original single-receiver ABI. No callback behavior is replaced. */
 if(callback==(uintptr_t)thug_walk_enter_hang_draft)thug_walk_enter_hang_draft(receiver,diagnostics,memory);
 else ((void (*)(void *))callback)(receiver);
}
/* 0052a180,13 bytes. Fixed QB member ABI; services come from the interpreter's
 * existing nested event scope, as for other recovered native commands. */
uint32_t thug_walk_finish_command_draft(void *p,ThugScriptStructure *parameters,ThugScriptInstance *script){
 (void)parameters;(void)script;const ThugEventServices *services=thug_event_services;
 thug_walk_finish_transition_draft(p,services?services->diagnostics:0,services?services->memory:0);return 1;
}
