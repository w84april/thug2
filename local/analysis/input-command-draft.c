/* Original Input script commands and their complete descriptor registration. */
#include "../../src/game/components.h"
#include "../../src/script/delivery.h"
#include "../../src/script/registration.h"
#include "../../src/core/timing.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static float flt(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static uint32_t bits(float f){uint32_t v;__builtin_memcpy(&v,&f,4);return v;}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
void thug_input_button_deadline_draft(void *,uint32_t);
void thug_input_button_force_draft(void *,uint32_t);
uint32_t thug_input_enable_events_draft(void *,ThugScriptStructure *,ThugScriptInstance *);
uint32_t thug_input_disable_events_draft(void *,ThugScriptStructure *,ThugScriptInstance *);
/* 0041e7e0. The deadline is truncated to a signed low word before float storage. */
void thug_input_suppress_button_draft(void *p,uint32_t name,float seconds,uint32_t clear){
    ThugInputButton *button=thug_input_find_button((void *)((uint8_t *)p+0x20),name);
    uint32_t now=thug_frame_time();double time=(int32_t)now;
    if((int32_t)now<0)time=R(time+0x1p32);
    uint32_t deadline=thug_truncate_double_low_word(R(time+R((double)seconds*1000)));
    thug_input_button_deadline_draft(button,bits((float)(int32_t)deadline));
    if((uint8_t)clear){thug_input_button_force_draft(button,0);thug_input_button_clear_latch(button);thug_input_button_clear_pending(button);}
}
const char thug_input_suppression_format_draft[]="D:%s:%i: time = %g\n";
const char thug_input_source_file_draft[]="omponents\\InputComponent.cpp";
/* 0041e8f0. 00401c30 is the existing host formatted-debug-output boundary. */
uint32_t thug_input_command_suppress_draft(void *p,const ThugScriptStructure *s,ThugScriptInstance *script,const ThugDiagnostics *d){
    (void)script;uint32_t name=0;
    if(thug_script_get_checksum(s,0,&name,0)){
        float seconds=1;thug_script_get_float(s,0x906b67ba,&seconds,0);
        if(d&&d->print)d->print(d->context,thug_input_suppression_format_draft,thug_input_source_file_draft,0x94,(double)seconds);
        uint32_t clear=0;thug_script_get_integer(s,0x1a4e0ef9,&clear,0);
        thug_input_suppress_button_draft(p,name,seconds,clear!=0);
    }
    return 1;
}
/* 0041e9a0 /0041e9b0 /0041e9c0 /0041e9d0. */
uint32_t thug_input_disable_player_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;((uint8_t *)p)[0x498]=1;return 1;}
uint32_t thug_input_enable_player_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;((uint8_t *)p)[0x498]=0;return 1;}
uint32_t thug_input_disable_network_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;((uint8_t *)p)[0x499]=1;return 1;}
uint32_t thug_input_enable_network_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;((uint8_t *)p)[0x499]=0;return 1;}
/* 0041e9e0. */
uint32_t thug_input_player_disabled_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return ((uint8_t *)p)[0x498]||((uint8_t *)p)[0x499];}
/* 0041ea20 /0041ea30 /0041ea40 /0041ea50 inspect held, not the edge latch. */
uint32_t thug_input_left_pressed_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return ((uint8_t *)p)[0x60]!=0;}
uint32_t thug_input_right_pressed_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return ((uint8_t *)p)[0x80]!=0;}
uint32_t thug_input_up_pressed_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return ((uint8_t *)p)[0x20]!=0;}
uint32_t thug_input_down_pressed_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){(void)s;(void)script;return ((uint8_t *)p)[0x40]!=0;}
/* 0046c370. Asymmetric positive/negative scales and original quadrant folding. */
double thug_input_stick_magnitude_draft(void *unused,float x,float y,float angle){
    (void)unused;double a=R((double)x/(x>0?127:128)),b=R((double)y/(y>0?127:128));
    double folded;
    if(angle>-.7853981852531433f&&angle<.7853981852531433f)folded=angle;
    else if(angle>.7853981852531433f&&angle<2.356194496154785f)folded=R((double)angle-1.5707963705062866f);
    else if(__builtin_fabs((double)angle)>2.356194496154785f)folded=R(__builtin_fabs((double)angle)-3.1415927410125732f);
    else folded=R((double)angle+1.5707963705062866f);
    double cosine=__builtin_fabs(thug_platform_cos(folded));
    double value=R(R(R(__builtin_sqrt(R(R(b*b)+R(a*a))))*cosine)*1.1764705181121826f);
    return value>1?1:value;
}
/* 0041ea60. Reload output structures and pad words between inserting fields. */
uint32_t thug_input_read_sticks_draft(void *p,ThugScriptStructure *parameters,ThugScriptInstance *script,const ThugMemory *m){
    (void)parameters;
    thug_script_set_float_bits(ptr(script,0x14),0x737f15cf,bits((float)R((double)flt(p,0x248)*57.2957763671875f)),m);
    void *out=ptr(script,0x14),*pad=(uint8_t *)p+0x20;
    float magnitude=(float)thug_input_stick_magnitude_draft(pad,flt(p,0x228),flt(p,0x22c),flt(p,0x248));
    thug_script_set_float_bits(out,0x686ad1c2,bits(magnitude),m);
    thug_script_set_float_bits(ptr(script,0x14),0xd6030cea,bits((float)R((double)flt(p,0x240)*57.2957763671875f)),m);
    out=ptr(script,0x14);magnitude=(float)thug_input_stick_magnitude_draft(pad,flt(pad,0x200),flt(pad,0x204),flt(pad,0x220));
    thug_script_set_float_bits(out,0xc94777ac,bits(magnitude),m);return 1;
}
/* 0041eb20. Duration units: seconds first, then frames, otherwise milliseconds.
 * Missing required arguments read original uninitialized stack storage; trap
 * explicitly outside the valid script contract rather than inventing a value. */
uint32_t thug_input_held_longer_draft(void *p,const ThugScriptStructure *s,ThugScriptInstance *script){
    (void)script;uint32_t name;float duration;
    if(!thug_script_get_checksum(s,0xc5f953c2,&name,1))__builtin_trap();
    if(!thug_script_get_float(s,0,&duration,1))__builtin_trap();
    double threshold=duration;
    if(thug_script_has_flag(s,0xd029f619)||thug_script_has_flag(s,0x49e0ee96))threshold=R(threshold*1000);
    else if(thug_script_has_flag(s,0x019176c5)||thug_script_has_flag(s,0x4a07c332))threshold=R(threshold*16.66666603088379f);
    uint32_t ticks=thug_truncate_double_low_word(threshold);
    ThugInputButton *button=thug_input_find_button((void *)((uint8_t *)p+0x20),name);
    return button&&*(uint8_t *)button&&thug_input_button_elapsed(button)>ticks;
}
/* Host adapters retain each original three-argument component-member ABI. */
static const ThugDiagnostics *diagnostics(void){return thug_event_services?thug_event_services->diagnostics:thug_component_services->diagnostics;}
static const ThugMemory *memory(void){return thug_event_services?thug_event_services->memory:thug_component_services->memory;}
uint32_t thug_input_suppress_command_bridge_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){return thug_input_command_suppress_draft(p,s,script,diagnostics());}
uint32_t thug_input_read_sticks_bridge_draft(void *p,ThugScriptStructure *s,ThugScriptInstance *script){return thug_input_read_sticks_draft(p,s,script,memory());}
typedef uint32_t (*Member)(void *,ThugScriptStructure *,ThugScriptInstance *);
typedef struct{uint32_t name,type;Member member;uint32_t offset,reserved,terminator;} InputCommand;
_Static_assert(sizeof(InputCommand)==24,"Original Input descriptor stride");
/* 00684c78, fourteen descriptors established by original initializer6445b0. */
const InputCommand thug_input_commands_draft[]={
 {0xbf7d6c46,0x27d7cd28,thug_input_suppress_command_bridge_draft,0,0,0},
 {0x6e24f5fd,0x27d7cd28,thug_input_disable_player_draft,0,0,0},
 {0x56c6c0cd,0x27d7cd28,thug_input_enable_player_draft,0,0,0},
 {0x6df51774,0x27d7cd28,thug_input_disable_network_draft,0,0,0},
 {0x31c6454f,0x27d7cd28,thug_input_enable_network_draft,0,0,0},
 {0x0660746a,0x27d7cd28,thug_input_player_disabled_draft,0,0,0},
 {0x78238598,0x27d7cd28,thug_input_left_pressed_draft,0,0,0},
 {0x1d604a9d,0x27d7cd28,thug_input_right_pressed_draft,0,0,0},
 {0x89aa9b5f,0x27d7cd28,thug_input_up_pressed_draft,0,0,0},
 {0x83028fc5,0x27d7cd28,thug_input_down_pressed_draft,0,0,0},
 {0xb2a022de,0x27d7cd28,thug_input_read_sticks_bridge_draft,0,0,0},
 {0x2366469c,0x27d7cd28,(Member)thug_input_held_longer_draft,0,0,0},
 {0x1090a150,0x27d7cd28,thug_input_enable_events_draft,0,0,0},
 {0x28729460,0x27d7cd28,thug_input_disable_events_draft,0,0,0},
 {0,0x27d7cd28,0,0,0,UINT32_MAX}
};
/* 0041e6f0. */
void thug_input_register_commands_draft(const ThugMemory *m){thug_script_register_commands(0x27d7cd28,thug_input_commands_draft,24,m);}
