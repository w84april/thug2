#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/core/matrix.h"
#include "../../src/core/timing.h"
#include "../../src/script/registration.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void set_number(void *p,unsigned o,double v){float f=v;put(p,o,word(&f,0));}
static uint32_t quiet(uint32_t v){return (v&0x7f800000)==0x7f800000&&(v&0x7fffff)?v|0x400000:v;}
static double r(double x){return thug_platform_round_x87_single(x);}
extern void *thug_cutscene_context_draft;
extern float thug_particle_parameter_scale_draft;
ThugNetworkState *thug_particle_network_state_draft; /* Original006fa7d0, distinct from7cce14. */
uint8_t thug_particle_command_draft(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *,ThugCollisionQuery *);
void thug_particle_manager_delete_draft(void *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
void thug_particle_manager_expire_draft(void *,uint32_t);
void thug_particle_setup_script_draft(void *,uint32_t,const ThugScriptStructure *,ThugReferencedObject *,const ThugDiagnostics *,const ThugMemory *);
void thug_particle_update_script_draft(void *,uint32_t,const ThugScriptStructure *,ThugReferencedObject *,const ThugDiagnostics *,const ThugMemory *);
void thug_particle_update_draft(void *,float,uint32_t,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_particle_suspend_ready_draft(void *,float *);
uint8_t thug_particle_suspend_far_draft(const void *);
float *thug_particle_orientation_draft(void *,float *);
void thug_particle_advance_setup_draft(void *,const ThugDiagnostics *,const ThugMemory *);
static void delete_owner(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 void *o=ptr(p,12);typedef void (*Delete)(void *,const ThugDiagnostics *,const ThugMemory *);((Delete *)ptr(o,0))[6](o,d,m);
}
/* 0041d7f0. The component forwards all three original command arguments. */
uint32_t thug_flexparticle_forward_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 void *effect=ptr(p,0x18);return effect?thug_particle_command_draft(effect,name,s,script,thug_component_services->query):0;
}
/* 0041d780. Its running query requires a live effect, unlike41d8f0. */
uint32_t thug_flexparticle_checksum_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 if(name==0x2299a9f2){void *e=ptr(p,0x18);return ((uint8_t *)e)[0x12b]||number(e,0x70)>0;}
 if(name==0x96896315)return thug_flexparticle_forward_draft(p,name,s,script);return 2;
}
/* 0041d700. Direct members receive name, parameters AND script. */
uint32_t thug_flexparticle_descriptor_draft(void *p,const ThugScriptCommand *entry,ThugScriptStructure *s,ThugScriptInstance *script){
 ThugComponentChecksum member;__builtin_memcpy(&member,(const char *)entry+8,4);
 if(member)return member((char *)p+word(entry,12),entry->name,s,script);
 return ((const ThugComponentMethods *)ptr(p,0))->checksum(p,entry->name,s,script);
}
/* 0041d820 /0041d8f0 /0041d920 /0041d940. */
uint32_t thug_flexparticle_clear_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)s;(void)script;void *e=ptr(p,0x18);if(e)put(e,0x8c,0);return 1;
}
uint32_t thug_flexparticle_running_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)s;(void)script;void *e=ptr(p,0x18);return e&&(((uint8_t *)e)[0x12b]||number(e,0x70)>0);
}
uint32_t thug_flexparticle_start_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)s;(void)script;void *e=ptr(p,0x18);if(e)((uint8_t *)e)[0x12b]=1;return 1;
}
uint32_t thug_flexparticle_stop_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)s;(void)script;void *e=ptr(p,0x18);if(e)((uint8_t *)e)[0x12b]=0;return 1;
}
/* 0041d840. Both named commands perform the same optional slot updates. */
uint32_t thug_flexparticle_scripts_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)script;ThugScriptStructure *parameters=0;thug_script_get_structure(s,0x7031f10c,&parameters,0);
 if(word(p,0x18)){
  uint32_t setup=0,update=0;
  if(thug_script_get_checksum(s,0xfc57577f,&setup,0))thug_particle_setup_script_draft(ptr(p,0x18),setup,parameters,ptr(p,12),thug_component_services->diagnostics,thug_component_services->memory);
  if(thug_script_get_checksum(s,0x092276db,&update,0))thug_particle_update_script_draft(ptr(p,0x18),update,parameters,ptr(p,12),thug_component_services->diagnostics,thug_component_services->memory);
 }return 1;
}
/* 0041d960. Any nonzero integer chooses delayed particle expiry. */
uint32_t thug_flexparticle_remove_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)script;uint32_t delayed=0;thug_script_get_integer(s,0x0cf50f29,&delayed,0);
 if(delayed)thug_particle_manager_expire_draft(thug_cutscene_context_draft,word(p,0x24));
 else thug_particle_manager_delete_draft(thug_cutscene_context_draft,word(p,0x24),thug_component_services->diagnostics,thug_component_services->memory);return 1;
}
/* 0041e190. Deletion may already clear the reference; otherwise unlink it. */
uint32_t thug_flexparticle_destroy_owner_draft(void *p,uint32_t name,ThugScriptStructure *s,ThugScriptInstance *script){
 (void)name;(void)s;(void)script;ThugObjectReference *reference=(void *)((char *)p+0x18);
 if(reference->object){
  thug_particle_manager_delete_draft(thug_cutscene_context_draft,word(p,0x24),thug_component_services->diagnostics,thug_component_services->memory);
  if(reference->object){thug_object_reference_unlink(reference->object,reference);reference->object=0;}reference->object=0;
 }delete_owner(p,thug_component_services->diagnostics,thug_component_services->memory);return 1;
}
typedef struct {uint32_t name,type;ThugComponentChecksum member;uint32_t adjustment,reserved,flags;} ParticleCommand;
#define ROW(n) {n,0xc5bceb9e,0,0,0,0}
ParticleCommand thug_particle_descriptors_draft[26]={
 ROW(0x63274395),ROW(0x8ffdef38),ROW(0x7911855b),ROW(0xdb8621f7),ROW(0xe985a9a6),ROW(0xe3309ab5),ROW(0xfbb6720d),ROW(0xa075ee45),ROW(0x2a479569),ROW(0x2e66815e),ROW(0xd3f1d333),ROW(0xb373fb6e),ROW(0x1cfbf078),ROW(0x514b2584),ROW(0x711b1a6a),ROW(0x35b65bd4),ROW(0x099cd17b),ROW(0x4893f05d),ROW(0x482482c6),ROW(0x7f97bad3),ROW(0xe99d53a8),ROW(0xed0fe310),ROW(0x2a1f307b),ROW(0xabf5f9e1),ROW(0x83b57984),ROW(0)};
/* 00642fe0. Only the last four words of each static descriptor are written. */
void thug_particle_descriptors_initialize_draft(void){
 const ThugComponentChecksum members[]={thug_flexparticle_destroy_owner_draft,thug_flexparticle_clear_draft,thug_flexparticle_scripts_draft,thug_flexparticle_scripts_draft,thug_flexparticle_running_draft,thug_flexparticle_start_draft,thug_flexparticle_stop_draft,thug_flexparticle_remove_draft,0};
 for(unsigned i=0;i<26;i++){ParticleCommand *p=&thug_particle_descriptors_draft[i];p->member=i<17?thug_flexparticle_forward_draft:members[i-17];p->adjustment=0;p->reserved=0;p->flags=i==25?0xffffffff:0;}
}
/* 0041d6e0. Descriptor storage is retained by the original symbol registry. */
void thug_particle_descriptors_register_draft(const ThugMemory *m){thug_script_register_commands(0xc5bceb9e,thug_particle_descriptors_draft,24,m);}
/* 0041df80. Full component update; scope the host services around real scripts. */
static void flex_update(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(!word(p,0x18)){delete_owner(p,d,m);return;}
 set_number(p,0x2c,r(thug_frame_duration()+number(p,0x2c)));
 void *suspend=ptr(p,0x30);uint8_t ready=!suspend||thug_particle_suspend_ready_draft(suspend,0);
 suspend=ptr(p,0x30);
 if(suspend&&thug_particle_suspend_far_draft(suspend)&&!thug_network_is_active(thug_particle_network_state_draft)){
  if(number(p,0x2c)>=thug_particle_parameter_scale_draft){
   void *effect=ptr(p,0x18);put(effect,0x120,word(effect,0x120)|1);((uint8_t *)ptr(p,0x18))[0x12f]=1;
   effect=ptr(p,0x18);if(((uint8_t *)effect)[0x12a]){thug_particle_update_draft(effect,number(p,0x2c),0,q,d,m);put(p,0x2c,0);}
   effect=ptr(p,0x18);if(effect){put(effect,0x120,word(effect,0x120)&~1u);((uint8_t *)ptr(p,0x18))[0x12f]=0;}
  }
 }else{
  void *effect=ptr(p,0x18);put(effect,0x120,word(effect,0x120)|1);((uint8_t *)ptr(p,0x18))[0x12f]=1;
  if(ready){
   if(((uint8_t *)p)[0x38]){
    float owner[16],rotation[16];thug_matrix_copy(owner,(float *)((char *)ptr(p,12)+0xc0));owner[12]=owner[13]=owner[14]=0;owner[15]=1;
    thug_particle_orientation_draft(ptr(p,0x18),rotation);float *target=(float *)((char *)ptr(p,12)+0xc0);thug_matrix_multiply(target,rotation,owner);
    put(ptr(p,0x18),0xdc,(uintptr_t)((char *)ptr(p,12)+0xc0));
   }
   void *owner=ptr(p,12);uint32_t z=word(owner,0x54),x=quiet(word(owner,0x4c)),y=quiet(word(owner,0x50)),w=word(owner,0x58);
   effect=ptr(p,0x18);put(effect,0x20,x);put(effect,0x24,y);put(effect,0x28,z);put(effect,0x2c,w);
   effect=ptr(p,0x18);if(((uint8_t *)effect)[0x12a]){
    if(word(p,0x34))put(effect,0xec,word(ptr(p,0x34),0x22c));
    thug_particle_update_draft(ptr(p,0x18),number(p,0x2c),0,q,d,m);put(p,0x2c,0);
   }
  }else thug_particle_advance_setup_draft(ptr(p,0x18),d,m);
 }
 if(word(ptr(p,12),0x104)&4){((uint8_t *)ptr(p,0x18))[0x12f]=0;((uint8_t *)ptr(p,0x18))[0x130]=0;}
}
void thug_flexparticle_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;flex_update(p,q,d,m);thug_component_services=previous;
}
uint32_t thug_flexparticle_descriptor_scoped_draft(void *p,const ThugScriptCommand *entry,ThugScriptStructure *s,ThugScriptInstance *script,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
 uint32_t result=thug_flexparticle_descriptor_draft(p,entry,s,script);thug_component_services=previous;return result;
}
void *thug_flexparticle_construct_draft(void *);
void thug_flexparticle_setup_initialize_draft(void *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
void thug_flexparticle_finalize_draft(void *);
void thug_flexparticle_visibility_draft(void *,uint32_t);
static void initialize_entry(void *p,const ThugScriptStructure *s){thug_flexparticle_setup_initialize_draft(p,s,thug_component_services->diagnostics,thug_component_services->memory);}
static void visibility_entry(void *p,void *v){thug_flexparticle_visibility_draft(p,(uintptr_t)v);}
const ThugComponentMethods thug_flexparticle_dispatch_methods_draft={.update=thug_flexparticle_update_draft,.initialize=initialize_entry,.finalize=thug_flexparticle_finalize_draft,.unknown_20=visibility_entry,.moved=thug_component_empty_frame_bridge,.descriptor=thug_flexparticle_descriptor_draft,.checksum=thug_flexparticle_checksum_draft};
/* Versioned factory keeps earlier checkpoints and their explicit stops intact. */
void *thug_flexparticle_dispatch_versioned_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x3c,m);if(p){thug_flexparticle_construct_draft(p);put(p,0,(uintptr_t)&thug_flexparticle_dispatch_methods_draft);}return p;}
