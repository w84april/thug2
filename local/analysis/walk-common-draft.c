/* Candidates for the shared Walk frame tail. Full frame dispatch is unfinished. */
#include "../../src/game/stats.h"
#include "../../src/core/timing.h"
#include "../../src/core/vector.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void fp(void *p,unsigned o,double v){float f=(float)v;__builtin_memcpy((char *)p+o,&f,4);}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
#define R thug_platform_round_x87_single
/* 00527be0,99 bytes. Height offset decays outside hang and animation states. */
void thug_walk_decay_model_offset_draft(void *p){
 if(word(p,0x18)==2||word(p,0x18)==4)return;
 float rate=parameter(0xb32c972b);double factor=R(thug_frame_duration()*rate),value=number(p,0x9c);
 fp(p,0x9c,R(R(-value*factor)+value));
}
/* 00527420,231 bytes. Tilt recovery preserves the original snap and blend gates. */
void thug_walk_restore_up_draft(void *p){
 if(word(p,0x5c)==0x3f800000)return;
 if(number(p,0x5c)>.9990000128746033f){put(p,0x58,0);put(p,0x5c,0x3f800000);put(p,0x60,0);put(p,0x64,0x3f800000);put(p,0x72c,0);return;}
 if(number(p,0x72c)!=0)return;
 float rate=parameter(0x0f22c135),target[4]={0,1,0,1},result[4];
 thug_vector_lerp(result,(float *)((char *)p+0x58),target,(float)R(thug_frame_duration()*rate));
 __builtin_memcpy((char *)p+0x58,result,16);thug_vector_normalize((float *)((char *)p+0x58));
}
/* 00528400,191 bytes. Keep the smaller current/previous speed after100ms. */
void thug_walk_filter_speed_event_draft(void *p,uint32_t previous){
 if(word(p,0x18))return;
 uint32_t timestamp=word(p,0x1c);if(thug_elapsed_time()+thug_timer_offset-timestamp<100){put(p,0x708,word(p,0x704));return;}
 float prior=number(p,0x708),current=number(p,0x704);if(current<prior)prior=current;
 fp(p,0x704,prior);fp(p,0x708,current);
 if(word(p,0x78)==0xaf895b3f&&prior==0)put(p,0x78,previous==0x1d537eff?0x1d537eff:0x9b46e749);
}
static void cross(float out[4],const float left[4],const float right[4]){
 for(unsigned i=0;i<3;i++){unsigned j=(i+1)%3,k=(i+2)%3;out[i]=(float)R(R((double)left[j]*right[k])-R((double)left[k]*right[j]));}out[3]=0;
}
/* 00529ce0,642 bytes. Publish position, orientation, velocity and model offset. */
void thug_walk_write_owner_draft(void *p){
 double y=number(p,0x744),remaining=R(1-R(y*y));double scale=remaining>0?R(__builtin_sqrt(remaining)):.00009999999747378752f;
 for(unsigned i=0;i<4;i++)fp(p,0x48+4*i,R(scale*number(p,0x48+4*i)));put(p,0x4c,word(p,0x744));
 float basis[16]={0};basis[15]=1;
 cross(basis,(float *)((char *)p+0x58),(float *)((char *)p+0x48));thug_vector_normalize(basis);
 for(unsigned i=0;i<4;i++)put(basis,16+4*i,word(p,0x58+4*i));cross(basis+8,basis,basis+4);
 for(unsigned i=0;i<4;i++)put(ptr(p,12),0x4c+4*i,word(p,0x24+4*i));
 thug_matrix_copy((float *)((char *)ptr(p,12)+0x6c),basis);thug_matrix_copy((float *)((char *)ptr(p,12)+0xc0),basis);
 uint32_t state=word(p,0x18);void *owner=ptr(p,12);
 if(state<2){for(unsigned i=0;i<4;i++)put(owner,0xac+4*i,word(p,0x34+4*i));put(ptr(p,12),0xb0,word(p,0x44));}
 else if(state==2){fp(owner,0xac,-(double)number(p,0x50));put(owner,0xb0,0);put(owner,0xb8,0x3f800000);fp(owner,0xb4,number(p,0x48));owner=ptr(p,12);double speed=number(p,0x18dc);for(unsigned i=0;i<4;i++)fp(owner,0xac+4*i,R(speed*number(owner,0xac+4*i)));}
 else{if(state==3)fp(owner,0xb0,number(p,0x704));else put(owner,0xb0,0);put(owner,0xac,0);put(owner,0xb4,0);put(owner,0xb8,0x3f800000);}
 float offset=number(p,0x9c);void *model=ptr(p,0x1778);for(unsigned i=0;i<4;i++)fp(model,0x1f8+4*i,R((double)basis[4+i]*offset));
}
/* 00529800,198 bytes. Continue the original temporary axis-angle rotation. */
void thug_walk_rotate_owner_draft(void *p){
 if(number(p,0x72c)==0)return;
 float duration=parameter(0xb0675803),rotation[16];float *matrix=(float *)((char *)ptr(p,12)+0x6c);
 float angle=(float)R(R((double)number(p,0x80)/duration)*number(p,0x730));
 thug_matrix_axis_angle(rotation,(float *)((char *)p+0x734),angle);thug_matrix_multiply(matrix,matrix,rotation);
 thug_matrix_copy((float *)((char *)ptr(p,12)+0xc0),(float *)((char *)ptr(p,12)+0x6c));
 double remaining=R((double)number(p,0x72c)-number(p,0x80));fp(p,0x72c,remaining);if(remaining<0)remaining=0;fp(p,0x72c,remaining);
}
