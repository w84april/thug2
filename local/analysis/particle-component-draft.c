#include "../../src/game/components.h"
#include "../../src/game/object_registry.h"
#include "../../src/game/nodes.h"
#include "../../src/game/drawing.h"
#include "../../src/core/random.h"
#include "../../src/core/timing.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void set_number(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
/* 00476770. Unlike 476df0, missing values retain both outputs. Ordered raw
 * reads preserve NaN payloads and aliases where the first write changes y. */
uint8_t thug_script_get_pair_outputs_draft(const ThugScriptStructure *s,uint32_t name,float *x,float *y,uint32_t required){
 uint32_t at;if(!thug_script_get_typed(s,name,5,&at)){if(required)thug_draw_style_noop((void *)s);return 0;}
 const void *p=(void *)(uintptr_t)at;put(x,0,word(p,4));put(y,0,word(p,8));return 1;
}
float *thug_matrix_euler_draft(float out[16],const float angles[4]);
/* 0041f520. Live target priority, parameter precedence, wrapped random phase,
 * PC24 sine envelope and optional local rotation match the original order. */
void thug_lockobj_initialize_draft(void *p,const ThugScriptStructure *s,const ThugMemory *m){
 put(p,0x18,0);put(p,0x20,0);put(p,0x1c,thug_object_default_id);
 put(p,0x24,0);put(p,0x28,0);put(p,0x2c,0);put(p,0x30,0x3f800000);
 uint8_t *flags=(uint8_t *)p+0x8c;*flags&=~2u;
 if(thug_script_has_flag(s,0xd443a2bc)){*flags&=~4u;return;}
 *flags|=4;thug_script_get_checksum(s,0x2bfc2486,(void *)((char *)p+0x18),0);
 if(!thug_script_get_vector(s,0,(void *)((char *)p+0x24),0))thug_script_get_vector(s,0xbe9ab709,(void *)((char *)p+0x24),0);
 thug_script_get_checksum(s,0x40c698af,(void *)((char *)p+0x1c),0);thug_script_get_checksum(s,0xcab94088,(void *)((char *)p+0x20),0);
 ThugUiObjectBase *target=(void *)thug_object_find_global(thug_component_type_registry,word(p,0x1c));if(!target)target=(void *)thug_object_find_global(thug_component_type_registry,word(p,0x18));
 if(target){ThugObjectManager *manager=(void *)thug_component_type_registry;const ThugObjectManagerMethods *methods=manager->methods;
  uint32_t priority=thug_truncate_double_low_word(R((double)(int32_t)target->queue_node.priority-1));methods->set_priority(manager,pointer(p,12),priority,m);}
 *flags&=~1u;set_number(p,0x78,1);set_number(p,0x7c,1);
 if(thug_script_get_pair_outputs_draft(s,0x700c4085,(void *)((char *)p+0x78),(void *)((char *)p+0x7c),0))*flags|=1;
 put(p,0x84,0);put(p,0x80,0);
 if(thug_script_get_pair_outputs_draft(s,0xd25807f0,(void *)((char *)p+0x80),(void *)((char *)p+0x84),0))*flags|=1;
 put(p,0x88,(uint32_t)thug_random_range(1024));double phase=(thug_frame_time()+word(p,0x88))&1023;
 double b=thug_platform_sin(R(R(phase*number(p,0x84))*0.006135922856628895));
 double a=thug_platform_sin(R(R(phase*number(p,0x80))*0.006135922856628895));
 double value=R(R(a*b)+1);value=R(R((double)number(p,0x7c)-number(p,0x78))*value);value=R(value*.5);value=R(value+number(p,0x78));set_number(p,0x74,(float)value);
 *flags=(*flags&~2u)|((thug_script_has_name_or_flag(s,0x9d2d0915)<<1)&2u);
 if(*flags&2){float angles[4];thug_node_angles(s,angles);thug_matrix_euler_draft((void *)((char *)p+0x34),angles);}
}
void thug_lockobj_initialize_entry_draft(void *p,const ThugScriptStructure *s){thug_lockobj_initialize_draft(p,s,thug_component_services->memory);}
extern const ThugComponentMethods thug_flexparticle_methods_draft;
/* 0041da00/0041e1e0. The reference is initialized empty and spare bytes retain
 * their input value. Allocation's exact zero fill is the existing 401cc0. */
void *thug_flexparticle_construct_draft(void *p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_flexparticle_methods_draft);
 put(p,0x18,0);put(p,0x1c,0);put(p,0x20,0);put(p,4,0xc5bceb9e);
 for(unsigned o=0x24;o<=0x34;o+=4)put(p,o,0);((uint8_t *)p)[0x38]=0;return p;}
void *thug_flexparticle_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x3c,m);return p?thug_flexparticle_construct_draft(p):0;}
/* 00433e70. Assign the original four suspension-distance thresholds. */
void thug_suspend_force_distance_draft(void *p){for(unsigned i=0;i<4;i++)put(p,0x34+4*i,0x49742400+16*i);}
/* 0041d740. The optional owner Suspend component gets those thresholds. */
void thug_flexparticle_finalize_draft(void *p){void *s=thug_object_find_component(pointer(p,12),0xce0ca665);put(p,0x30,(uintptr_t)s);if(s)thug_suspend_force_distance_draft(s);}
/* 0041d760. The low byte propagates exactly, not a normalized boolean. */
void thug_flexparticle_visibility_draft(void *p,uint32_t value){void *o=pointer(p,0x18);if(o)((uint8_t *)o)[0x12f]=(uint8_t)value;}
static void visibility_entry(void *p,void *value){thug_flexparticle_visibility_draft(p,(uintptr_t)value);}
/* Explicit boundary: particle-engine allocation/initialization and frame update
 * are not recovered. No synthetic successful effect is returned. */
uint32_t *thug_particle_component_boundary_draft; /* Optional comparison breakpoint record. */
void thug_flexparticle_initialize_unavailable_draft(void *p,const ThugScriptStructure *s){
 if(thug_particle_component_boundary_draft){uint32_t *b=thug_particle_component_boundary_draft;b[0]=0x41db00;b[1]=(uintptr_t)s;b[2]=(uintptr_t)p;b[3]=1;}
 __builtin_trap();
}
const ThugComponentMethods thug_flexparticle_methods_draft={.initialize=thug_flexparticle_initialize_unavailable_draft,.finalize=thug_flexparticle_finalize_draft,.unknown_20=visibility_entry};
