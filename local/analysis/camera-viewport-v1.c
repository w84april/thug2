/* Original viewport ownership/reference updates and player-camera registration.
 * Complete profile/camera-specific QB initialization is still separate. */
#include "../../src/game/camera.h"
#include "../../src/game/components.h"
#include "../../src/game/stats.h"
#include "../../src/game/ui.h"
#include "../../src/core/matrix.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
/* 004a0d70. The current reference is reread after the real virtual destructor. */
void thug_viewport_clear_owned_camera_v1(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 if(!(word(p,0x14)&1))return;
 void *camera=ptr(p,0x18);
 if(camera)(*(const ThugUiObjectMethods **)camera)->dispose(camera,1,d,m);
 camera=ptr(p,0x18);
 if(camera){thug_object_reference_unlink(camera,(ThugObjectReference *)((char *)p+0x18));put(p,0x18,0);}
 put(p,0x18,0);put(p,0x14,word(p,0x14)&~1u);
}
/* 004a0970. Cache the mapped viewport before releasing its old ownership. */
void thug_viewport_assign_camera_v1(uint32_t index,ThugCamera *camera,const ThugDiagnostics *d,const ThugMemory *m){
 int32_t mapped=thug_viewport_mapping[index];if(mapped==-1)return;
 void *viewport=thug_viewports[mapped];thug_viewport_clear_owned_camera_v1(viewport,d,m);
 ThugObjectReference *reference=(void *)((char *)viewport+0x18);void *old=reference->object;
 if(old){thug_object_reference_unlink(old,reference);reference->object=0;}
 reference->object=(void *)camera;if(camera)thug_object_reference_link((void *)camera,reference);
}
ThugCamera *thug_particle_camera_draft(uint32_t);
/* 0059f890. Separate object key and viewport index precede a low-byte force.
 * Copy/update occurs
 * before replacing the viewport's reference, including a repeated live lookup. */
uint8_t thug_player_register_camera_v1(uint32_t key,uint32_t index,uint32_t force,const ThugDiagnostics *d,const ThugMemory *m){
 void *owner=thug_object_find_global(0,key);if(!owner)return 0;
 ThugObjectComponent *component=thug_object_find_component(owner,0xc4e311fa);
 if(component){
  if((uint8_t)force){
   thug_matrix_copy((float *)((char *)owner+0x6c),thug_camera_orientation(thug_particle_camera_draft(index)));
   const void *position=thug_camera_position(thug_particle_camera_draft(index));
   for(unsigned i=0;i<4;i++)put(owner,0x4c+4*i,word(position,4*i));
   (*(const ThugComponentMethods **)component)->update(component,0,d,m);
  }
  thug_viewport_assign_camera_v1(index,ptr(component,0x18),d,m);
 }
 return 1;
}
