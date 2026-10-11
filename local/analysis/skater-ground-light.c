/* Original surface-dependent model/global light adjustment, with x87 spills. */
#include "../../src/collision/probe.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float f(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void pf(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static double r(double v){return thug_platform_round_x87_single(v);}
extern uint32_t thug_model_light_factor_count_draft;
float thug_light_current_draft,thug_light_target_draft,thug_light_ambient_factor_draft;
uint32_t thug_light_ambient_color_draft,*thug_light_direction_colors_draft;
float thug_light_lower_ambient_draft,thug_light_upper_ambient_draft;
float *thug_light_lower_factors_draft,*thug_light_upper_factors_draft;
float thug_light_minimum_draft,*thug_light_factors_draft;
float thug_light_ambient_rgb_draft[3],thug_light_direction_rows_draft[31][8];
/* 005b9760 /00417120. Static and moving mesh classes share the true method. */
uint8_t thug_collision_accepts_light_draft(const void *p){(void)p;return 1;}
uint8_t thug_collision_probe_accepts_light_draft(const ThugCollisionProbe *p){
 if(!p->result.hit)return 1;
 typedef uint8_t (*Predicate)(const void *);return ((Predicate *)(uintptr_t)p->result.instance->methods)[1](p->result.instance);
}
static double factor(float current,float scale){return r(r(r(r((double)current+current)-1)*scale)+1);}
/* 0048e660. Live count, factor arrays and current value are reloaded each turn. */
void thug_model_light_recalculate_draft(void *p){
 float current=f(p,8);pf(p,16,(float)factor(current,current<=.5f?thug_light_lower_ambient_draft:thug_light_upper_ambient_draft));
 if(f(p,16)<0)put(p,16,0);
 for(uint32_t i=0;i<thug_model_light_factor_count_draft;i++){
  current=f(p,8);void *out=ptr(p,20);float *scales=current<=.5f?thug_light_lower_factors_draft:thug_light_upper_factors_draft;
  pf(out,4*i,(float)factor(current,scales[i]));out=ptr(p,20);if(f(out,4*i)<0)put(out,4*i,0);
 }
 typedef void (*Refresh)(void *,uint32_t,uint32_t);((Refresh *)ptr(p,0))[8](p,1,1);
}
/* 0048e830. Compare overshoot before the float spill is reloaded. */
uint8_t thug_model_light_approach_draft(void *p,float target,float rate){
 float current=f(p,8);pf(p,12,target);
 if(current<target){double v=r((double)rate+f(p,8));pf(p,8,(float)v);if(v>target)pf(p,8,target);}
 else if(f(p,8)>target){double v=r((double)f(p,8)-rate);pf(p,8,(float)v);if(v<target)pf(p,8,target);}
 thug_model_light_recalculate_draft(p);return 1;
}
/* 0048e8a0. Raw float parameter copies preserve their bits. */
uint8_t thug_model_light_set_draft(void *p,float target){pf(p,12,target);pf(p,8,target);thug_model_light_recalculate_draft(p);return 1;}
/* 004b67e0. Capture the three color bytes before writing any channel. */
uint8_t thug_light_write_ambient_draft(void){
 uint32_t color=thug_light_ambient_color_draft;unsigned red=color&255,green=(color>>8)&255,blue=(color>>16)&255;
 thug_light_ambient_rgb_draft[0]=(float)r(r(red*(double)thug_light_ambient_factor_draft)*0x1p-7f);
 thug_light_ambient_rgb_draft[1]=(float)r(r(green*(double)thug_light_ambient_factor_draft)*0x1p-7f);
 thug_light_ambient_rgb_draft[2]=(float)r(r(blue*(double)thug_light_ambient_factor_draft)*0x1p-7f);return 1;
}
/* 004b6860. RGB source bytes and factors are reloaded after each store. */
uint8_t thug_light_write_direction_draft(uint32_t index){
 uint8_t *colors=(void *)thug_light_direction_colors_draft;float *factors=thug_light_factors_draft;
 for(unsigned j=0;j<3;j++)thug_light_direction_rows_draft[index][4+j]=(float)r(r(colors[index*4+j]*(double)factors[index])*0x1p-7f);return 1;
}
/* 004b6900. Fixed31 physical color records, independent of the factor count. */
void thug_light_write_all_draft(void){thug_light_write_ambient_draft();for(uint32_t i=0;i<31;i++)thug_light_write_direction_draft(i);}
/* 0048edb0. Global approach uses the original fixed .02 step and floor. */
uint8_t thug_light_approach_draft(float target){
 float current=thug_light_current_draft;thug_light_target_draft=target;
 if(current<target){double v=r((double)thug_light_current_draft+0x1.47ae14p-6f);thug_light_current_draft=(float)v;if(v>target)thug_light_current_draft=target;}
 else if(current>target){double v=r((double)thug_light_current_draft-0x1.47ae14p-6f);thug_light_current_draft=(float)v;if(v<target)thug_light_current_draft=target;}
 current=thug_light_current_draft;thug_light_ambient_factor_draft=(float)factor(current,current<=.5f?thug_light_lower_ambient_draft:thug_light_upper_ambient_draft);
 if(thug_light_ambient_factor_draft<thug_light_minimum_draft)thug_light_ambient_factor_draft=thug_light_minimum_draft;
 float *out=thug_light_factors_draft;
 for(uint32_t i=0;i<thug_model_light_factor_count_draft;i++){
  current=thug_light_current_draft;float *scale=current<=.5f?thug_light_lower_factors_draft:thug_light_upper_factors_draft;
  out[i]=(float)factor(current,scale[i]);out=thug_light_factors_draft;
  if(out[i]<thug_light_minimum_draft){out[i]=thug_light_minimum_draft;out=thug_light_factors_draft;}
 }
 thug_light_write_all_draft();return 1;
}
double thug_collision_probe_light_draft(const ThugCollisionProbe *);
void *thug_model_renderer_lights_draft(const void *);
/* 00420670. Keep the doubled interpolated value wide across the model store. */
void thug_model_surface_light_draft(void *p,const ThugCollisionProbe *probe,uint32_t smooth,float rate){
 if(!thug_collision_probe_accepts_light_draft(probe))return;
 void *light=thug_model_renderer_lights_draft(ptr(p,0x208));double value=thug_collision_probe_light_draft(probe);
 if(light){value=r(value+value);pf(p,0x22c,(float)value);
  if((uint8_t)smooth)thug_model_light_approach_draft(light,(float)r(value*.5f),(float)r((double)rate*0x1.47ae14p-6f));
  else thug_model_light_set_draft(light,(float)r(value*.5f));
 }else thug_light_approach_draft((float)value);
}
