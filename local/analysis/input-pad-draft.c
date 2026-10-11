/* Recovered controller packet -> original button/axis state, PC executable. */
#include "../../src/game/skater.h"
#include "../../src/core/checksum.h"
#include "../../src/core/timing.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static float flt(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void set(void *p,unsigned o,float v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static double unsigned_x87(uint32_t v){return (int32_t)v<0?R((double)(int32_t)v+0x1p32):(int32_t)v;}
/* 0046b800. Naming does not initialize the button's other fields. */
void thug_input_button_name_draft(void *p,const char *name){put(p,0x18,thug_crc32_string(name));}
/* 0057b620. The suppression deadline is copied as raw float bits. */
void thug_input_button_deadline_draft(void *p,uint32_t bits){put(p,0x1c,bits);}
/* 0046b820. Strict signed pressure threshold; suppression consumes no edge. */
void thug_input_button_pressure_draft(void *p,int32_t pressure){
    uint8_t *b=p;float deadline=flt(p,0x1c);
    if(deadline!=0){
        if(pressure>64 && !(unsigned_x87(thug_frame_time())>deadline))return;
        put(p,0x1c,0);
    }
    uint8_t prior=b[0];put(p,0xc,(uint32_t)pressure);
    if(pressure>64){
        if(!prior){put(p,4,thug_elapsed_time()+thug_timer_offset);b[0x10]=1;}
        b[0]=1;
    }else{
        if(prior){put(p,8,thug_elapsed_time()+thug_timer_offset);put(p,0x14,1);}
        b[0]=0;
    }
}
/* 0046b8b0. Forced release sets its latch but leaves release time untouched. */
void thug_input_button_force_draft(void *p,uint32_t value){
    uint8_t *b=p,v=(uint8_t)value;
    if(v){if(!b[0]){put(p,4,thug_elapsed_time()+thug_timer_offset);b[0x10]=1;}}
    else if(b[0])put(p,0x14,1);
    b[0]=v;
}
/* 0046b940. Preserve original non-address-order naming and untouched storage. */
void *thug_input_pad_construct_draft(void *p){
    static const uint16_t offsets[]={0,0x20,0x40,0x60,0x160,0x140,0x180,0x1a0,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x1c0,0x1e0};
    static const char *const names[]={"UP","DOWN","LEFT","RIGHT","SQUARE","CIRCLE","TRIANGLE","X","L1","L2","L3","R1","R2","R3","START","SELECT"};
    for(unsigned i=0;i<16;i++)thug_input_button_name_draft((uint8_t *)p+offsets[i],names[i]);
    put(p,0x230,0);put(p,0x234,0);return p;
}
/* 0046bb50. Release buttons, clear axes, retain edges and direction deadlines. */
void thug_input_pad_clear_draft(void *p){
    static const uint16_t order[]={0,0x20,0x40,0x60,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x160,0x140,0x1a0,0x180,0x1c0,0x1e0};
    for(unsigned i=0;i<16;i++)thug_input_button_pressure_draft((uint8_t *)p+order[i],0);
    for(unsigned o=0x200;o<=0x22c;o+=4)put(p,o,0);
}
/* 0046bc60. Original L/R stick edge-clearing asymmetry is intentional here. */
void thug_input_pad_reset_draft(void *p){
    thug_input_pad_clear_draft(p);
    static const uint16_t order[]={0,0x20,0x40,0x60,0x80,0xa0,0xc0,0xe0,0x100,0x120,0x160,0x140,0x1a0,0x180,0x1c0,0x1e0};
    for(unsigned i=0;i<16;i++){
        ThugInputButton *button=(void *)((uint8_t *)p+order[i]);
        if(order[i]==0x100){thug_input_button_clear_latch(button);thug_input_button_clear_latch(button);}
        else if(order[i]==0x120){thug_input_button_clear_pending(button);thug_input_button_clear_pending(button);}
        else{thug_input_button_clear_latch(button);thug_input_button_clear_pending(button);}
    }
}
uint32_t thug_input_direction_initialized_draft; /* 006f22b0 */
float thug_input_direction_angles_draft[16]; /* 006f2270 */
/* 0046ba80. Low-byte booleans form the original four-bit table index. */
double thug_input_pad_direction_draft(uint32_t up,uint32_t down,uint32_t left,uint32_t right){
    unsigned i=(uint8_t)up+2*((uint8_t)down+2*((uint8_t)left+2*(uint8_t)right));
    if(!(thug_input_direction_initialized_draft&1)){
        static const uint32_t values[]={0x40490fdb,0x40490fdb,0xbfc90fdb,0xbf490fdb,0xc016cbe4,0xc016cbe4,0x3fc90fdb,0x3f490fdb,0x4016cbe4,0x4016cbe4,0x3fc90fdb,0x3f490fdb,0x4016cbe4,0x4016cbe4};
        thug_input_direction_initialized_draft|=1;
        for(unsigned j=0;j<14;j++)__builtin_memcpy(thug_input_direction_angles_draft+j+2,values+j,4);
    }
    return thug_input_direction_angles_draft[i];
}
/* 0046bda0. Consume the original 32-byte packet without reinterpreting bindings. */
void thug_input_pad_update_draft(void *p,const uint8_t *packet){
    static const uint16_t destinations[]={0,0x20,0x40,0x60,0x160,0x140,0x1a0,0x180,0x80,0xe0,0xa0,0x100};
    static const uint8_t bytes[]={6,7,5,4,11,9,10,8,12,13,14,15};
    for(unsigned i=0;i<12;i++)thug_input_button_pressure_draft((uint8_t *)p+destinations[i],packet[bytes[i]]?255:0);
    thug_input_button_pressure_draft((uint8_t *)p+0xc0,(word(packet,0x1c)&0x200)?255:0);
    thug_input_button_pressure_draft((uint8_t *)p+0x120,(word(packet,0x1c)&0x400)?255:0);
    thug_input_button_pressure_draft((uint8_t *)p+0x1e0,(word(packet,0x1c)&0x100)?255:0);
    for(unsigned i=0;i<4;i++){
        int32_t a=(int32_t)packet[i]-128;
        if(!a)put(p,0x210+4*i,0);
        else{if(a==-128)a=-127;set(p,0x210+4*i,(float)R((double)(a+(a>0?-50:50))*0.012987012974917889f));}
    }
    for(unsigned i=0;i<4;i++)set(p,0x200+4*i,(int32_t)packet[0x12+i]-128);
    double x=flt(p,0x200),y=flt(p,0x204);
    set(p,0x224,(float)R(__builtin_sqrt(R(R(x*x)+R(y*y)))));
    set(p,0x220,(float)thug_platform_atan2(x,-y));
    x=flt(p,0x208);y=flt(p,0x20c);
    double magnitude=R(__builtin_sqrt(R(R(y*y)+R(x*x))));
    set(p,0x22c,(float)magnitude);
    if(magnitude>0.0010000000474974513f)set(p,0x228,(float)thug_platform_atan2(x,-y));
    else{
        unsigned up=packet[6]!=0,down=packet[7]!=0,left=packet[5]!=0,right=packet[4]!=0;
        if(up||down||left||right){set(p,0x228,(float)thug_input_pad_direction_draft(up,down,left,right));set(p,0x22c,127);}
        else{put(p,0x228,0);put(p,0x22c,0);}
    }
    if(word(p,0x230)){
        if(!(flt(p,0x22c)!=0 && __builtin_fabs((double)flt(p,0x228))<0.7853981852531433f
          && unsigned_x87(thug_frame_time())<=unsigned_x87(word(p,0x230))))put(p,0x230,0);
    }
    if(word(p,0x234)){
        if(!(flt(p,0x22c)!=0 && R(3.1415927410125732f-__builtin_fabs((double)flt(p,0x228)))<0.7853981852531433f
          && unsigned_x87(thug_frame_time())<=unsigned_x87(word(p,0x234))))put(p,0x234,0);
    }
}
