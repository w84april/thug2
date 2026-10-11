#include "../../src/game/components.h"
#include "../../src/core/number.h"
#include "../../src/script/params.h"
#include "../../src/script/lifetime.h"
#include "../../src/script/values.h"
#include <stddef.h>
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* 00497790 / 00497900. The two script slots share their retained parameter
 * structure. Setting a checksum prepares a script without advancing it;
 * clearing a checksum destroys that script but retains shared parameters. */
static void set_script(void *p,unsigned slot,uint32_t name,const ThugScriptStructure *arguments,ThugReferencedObject *owner,const ThugDiagnostics *d,const ThugMemory *m){
 ThugScriptInstance *script=ptr(p,slot);
 if(name){
  if(!script){script=thug_script_allocate(0xf4,m);if(script)thug_script_initialize(script);put(p,slot,(uintptr_t)script);}
  ThugScriptStructure *parameters=ptr(p,0x104);
  if(!parameters){parameters=thug_script_structure_allocate(8,m);if(parameters)thug_script_structure_initialize(parameters);put(p,0x104,(uintptr_t)parameters);}
  thug_script_structure_merge_optional(parameters,arguments,m);thug_script_setup_named(script,name,parameters,owner,d,m);
 }else{if(script){thug_script_destroy(script,d,m);thug_script_free(script,m);}put(p,slot,0);}
}
void thug_particle_setup_script_draft(void *p,uint32_t name,const ThugScriptStructure *arguments,ThugReferencedObject *owner,const ThugDiagnostics *d,const ThugMemory *m){set_script(p,0xfc,name,arguments,owner,d,m);}
void thug_particle_update_script_draft(void *p,uint32_t name,const ThugScriptStructure *arguments,ThugReferencedObject *owner,const ThugDiagnostics *d,const ThugMemory *m){set_script(p,0x100,name,arguments,owner,d,m);}
extern void *thug_cutscene_context_draft;
void *thug_particle_find_draft(const void *,uint32_t);
void *thug_particle_manager_create_draft(void *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,const ThugMemory *);
uint32_t thug_script_get_text_legacy_draft(const ThugScriptStructure *,uint32_t,const char **,uint32_t);
void *thug_flexparticle_construct_draft(void *);
void thug_flexparticle_finalize_draft(void *);
void thug_flexparticle_visibility_draft(void *,uint32_t);
float thug_particle_parameter_scale_draft; /* Original global0067d6d0. */
/* 0041db00. Complete initializer control flow; creation still inherits the
 * recovered point-sprite factory contract. Other particle classes trap. */
void thug_flexparticle_setup_initialize_draft(void *p,const ThugScriptStructure *s,const ThugDiagnostics *d,const ThugMemory *m){
 thug_script_get_checksum(s,0xa1dc81f9,(void *)((char *)p+0x24),0);
 float capacity=1;thug_script_get_float(s,0x6289dd76,&capacity,0);uint32_t count=thug_truncate_double_low_word(capacity);
 uint32_t segments=2,texture=0,blend=0x515e298e,type=0xaab555bb,alpha=0,a=8,c=1,reuse=0,local_count=0;
 float b=.5f,local_float=0;const char *model=0;
 thug_script_get_integer(s,0x9e52a20f,&segments,0);thug_script_get_checksum(s,0x7d99f28d,&texture,0);
 thug_script_get_checksum(s,0xdd6bb3d5,&blend,0);thug_script_get_checksum(s,0x7321a8d6,&type,0);
 thug_script_get_checksum(s,0x184197d5,(void *)((char *)p+0x28),0);thug_script_get_integer(s,0xa605b89f,&alpha,0);
 thug_script_get_integer(s,0xd93124d6,&a,0);thug_script_get_float(s,0x4e0a65ee,&b,0);thug_script_get_integer(s,0xd8458fb4,&c,0);
 thug_script_get_integer(s,0xd5928f25,&reuse,0);thug_script_get_integer(s,0x03d4e483,&local_count,0);
 thug_script_get_float(s,0x8e9a640e,&local_float,0);thug_script_get_text_legacy_draft(s,0x286a8d26,&model,0);
 uint8_t inherit=thug_script_has_flag(s,0xa0e585b0);ThugObjectReference *reference=(void *)((char *)p+0x18);
 if(reuse){void *effect=thug_particle_find_draft(thug_cutscene_context_draft,word(p,0x24));thug_object_reference_assign(reference,effect);if(reference->object)goto configure;}
 put(p,0x24,(uintptr_t)p);void *effect=thug_particle_manager_create_draft(thug_cutscene_context_draft,(uintptr_t)p,type,count,segments,texture,blend,alpha,a,word(&b,0),c,reuse,inherit,(uintptr_t)model,m);
 thug_object_reference_assign(reference,effect);if(!reference->object)return;
configure:
 effect=reference->object;
 uint32_t checksum=0;if(thug_script_get_checksum(s,0x87fa53ed,&checksum,0))put(effect,0xf4,checksum);
 ((uint8_t *)effect)[0x126]=(int32_t)local_count>0;put(effect,0x78,word(p,0x28));put(effect,0x70,word(&local_float,0));
 ThugScriptStructure *arguments=0;thug_script_get_structure(s,0x7031f10c,&arguments,0);
 uint32_t setup=0,update=0;
 if(thug_script_get_checksum(s,0xfc57577f,&setup,0))thug_particle_setup_script_draft(effect,setup,arguments,ptr(p,12),d,m);
 if(thug_script_get_checksum(s,0x092276db,&update,0))thug_particle_update_script_draft(effect,update,arguments,ptr(p,12),d,m);
 if(thug_script_has_flag(s,0xa2487cc3))((uint8_t *)p)[0x38]=1;
 uint8_t attach=thug_script_has_flag(s,0xbbfa4b06);((uint8_t *)effect)[0x132]=0;
 if(attach){uint32_t target=word(p,0x28);thug_script_get_checksum(s,0x0830ecaf,&target,0);
  if(target)put(p,0x34,(uintptr_t)thug_object_find_component(thug_script_find_object(target),0x286a8d26));}
 if(thug_script_has_flag(s,0x47580c70))put(effect,0x120,word(effect,0x120)|0x4000);
 if(thug_script_has_flag(s,0x5446af14))put(effect,0x120,word(effect,0x120)|0x8000);
 if(thug_script_has_flag(s,0x9b9381e2))((uint8_t *)effect)[0x131]=1;
 if(thug_script_has_flag(s,0xde45a90d))((uint8_t *)effect)[0x133]=0;
 uint32_t value=0;thug_script_get_integer(s,0x9d5923d8,&value,0);((uint8_t *)effect)[0x124]=value;
 float vector[4];if(thug_script_get_vector(s,0xe4247a6b,vector,0)){__builtin_memcpy((char *)effect+0x40,vector,16);((uint8_t *)effect)[0x127]=1;}
 thug_particle_parameter_scale_draft=(float)(int32_t)thug_script_get_global_integer(0x0cf3cba1,1);
}
static void initialize_entry(void *p,const ThugScriptStructure *s){thug_flexparticle_setup_initialize_draft(p,s,thug_component_services->diagnostics,thug_component_services->memory);}
static void visibility_entry(void *p,void *v){thug_flexparticle_visibility_draft(p,(uintptr_t)v);}
const ThugComponentMethods thug_flexparticle_setup_methods_draft={.initialize=initialize_entry,.finalize=thug_flexparticle_finalize_draft,.unknown_20=visibility_entry,.moved=thug_component_empty_frame_bridge};
/* Versioned factory preserves the earlier checkpoints' explicit boundaries. */
void *thug_flexparticle_setup_versioned_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x3c,m);if(p){thug_flexparticle_construct_draft(p);put(p,0,(uintptr_t)&thug_flexparticle_setup_methods_draft);}return p;}

/* Explicit frontier of the actual barrel frame after its startup script has
 * returned. This is a comparison stop, NOT recovered Motion behavior. */
uint32_t *thug_particle_setup_motion_boundary_draft;
void thug_particle_setup_motion_boundary_frame_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;uint32_t *b=thug_particle_setup_motion_boundary_draft;
 if(b){b[0]=0x4270e0;b[1]=(uintptr_t)p;b[2]=word(p,12);b[3]=1;}__builtin_trap();
}
