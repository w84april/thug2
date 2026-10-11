#include "../../src/game/assets.h"
#include "../../src/game/components.h"
#include "../../src/game/animation_controllers.h"
#include "../../src/script/delivery.h"
#include "../../src/collision/moving.h"
#include "../../src/core/matrix.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((uint8_t *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static void copy(void *to,const void *from,unsigned n){for(unsigned i=0;i<n;i+=4)put(to,i,word(from,i));}
static const ThugMemory *memory(void){return thug_component_services?thug_component_services->memory:thug_event_services->memory;}
static const ThugDiagnostics *diagnostics(void){return thug_component_services?thug_component_services->diagnostics:thug_event_services->diagnostics;}
/* Unrecovered lifecycle/update virtuals remain unavailable. These identities
 * allow real initialization without pretending the callback body is supplied. */
const uintptr_t thug_asset_manager_methods_draft[3]={0};
const uintptr_t thug_module_base_methods_draft[3]={0},thug_module_node_methods_draft[1]={0};
const uintptr_t thug_task_base_methods_draft[3]={0},thug_task_node_methods_draft[1]={0};
const uintptr_t thug_asset_task_methods_draft[3]={0};
void thug_asset_task_pending_draft(void){__builtin_trap();}
uint32_t thug_asset_manager_references_draft;
/* 0044f7e0. */
void *thug_module_base_construct_draft(void *p,const ThugMemory *m){
 put(p,0,(uintptr_t)thug_module_base_methods_draft);put(p,4,0);((uint8_t *)p)[12]=0;
 void *n=thug_allocate_zeroed(20,m);if(n){put(n,4,(uintptr_t)p);put(n,0,(uintptr_t)thug_module_node_methods_draft);put(n,8,0);put(n,12,(uintptr_t)n);put(n,16,(uintptr_t)n);}put(p,16,(uintptr_t)n);return p;
}
/* 00406890. */
void *thug_task_base_construct_draft(void *p,uint32_t priority,const ThugMemory *m){
 put(p,4,0);put(p,0,(uintptr_t)thug_task_base_methods_draft);put(p,12,0);put(p,16,0);put(p,20,0);
 void *n=thug_allocate_zeroed(20,m);if(n){put(n,4,(uintptr_t)p);put(n,0,(uintptr_t)thug_task_node_methods_draft);put(n,8,priority);put(n,12,(uintptr_t)n);put(n,16,(uintptr_t)n);}put(p,8,(uintptr_t)n);return p;
}
/* 00407f80. Table and update task use their actual constructors. */
void *thug_asset_manager_construct_draft(void *p,const ThugMemory *m){
 thug_module_base_construct_draft(p,m);put(p,0,(uintptr_t)thug_asset_manager_methods_draft);
 ThugObjectLookupTable *table=m->allocate(m->context,24,1);if(table)thug_object_table_initialize(table,10,m);put(p,0x1c,(uintptr_t)table);
 put(p,0x28,0);((uint8_t *)p)[0x34]=0;put(p,0x24,0);put(p,0x20,0);((uint8_t *)p)[0x15]=0;
 void *task=thug_allocate_zeroed(32,m);if(task){thug_task_base_construct_draft(task,0,m);put(task,28,(uintptr_t)p);put(task,0,(uintptr_t)thug_asset_task_methods_draft);put(task,24,(uintptr_t)thug_asset_task_pending_draft);}put(p,0x38,(uintptr_t)task);return p;
}
/* 004088e0. Low byte create flag; references always increment, including wrap. */
void thug_asset_manager_acquire_draft(uint32_t create,const ThugMemory *m){
 if(!thug_asset_manager&&(uint8_t)create){void *p=thug_allocate_zeroed(0x3c,m);thug_asset_manager=p?thug_asset_manager_construct_draft(p,m):0;}
 ++thug_asset_manager_references_draft;
}
const uintptr_t thug_collision_node_methods_draft[1]={0},thug_collision_sentinel_methods_draft[1]={0};
uint32_t thug_moving_collision_sentinel_draft[5]; /* 00691978; +12 aliases main head */
static void *collision_node(void *value,const uintptr_t *methods,const ThugMemory *m){
 void *n=thug_allocate_zeroed(20,m);if(n){put(n,0,(uintptr_t)methods);put(n,4,(uintptr_t)value);put(n,8,0);put(n,12,(uintptr_t)n);put(n,16,(uintptr_t)n);}return n;
}
/* 004177b0. Second original argument is unused. Preserve the head alias. */
void thug_moving_collision_register_draft(void *object,void *owner,const ThugMemory *m){
 (void)owner;void *n=collision_node(object,thug_collision_node_methods_draft,m);
 put(n,16,thug_moving_collision_sentinel_draft[4]);put(n,12,(uintptr_t)thug_moving_collision_sentinel_draft);
 put(pointer(thug_moving_collision_sentinel_draft,16),12,(uintptr_t)n);thug_moving_collision_sentinel_draft[4]=(uintptr_t)n;
 thug_moving_collision_list=pointer(thug_moving_collision_sentinel_draft,12);
}
/* The remaining box and compound query/lifetime methods are unrecovered. */
static void owner_rigid(void *p,void *owner){thug_moving_collision_set_owner(p,owner);}
/* 0040ae10. */
void thug_compound_collision_set_owner_draft(void *p,void *owner){put(p,0x38,(uintptr_t)owner);}
const uintptr_t thug_rigid_collision_base_methods_draft[22]={[11]=(uintptr_t)owner_rigid};
const uintptr_t thug_box_collision_methods_draft[22]={[11]=(uintptr_t)owner_rigid};
const uintptr_t thug_compound_collision_methods_draft[22]={[11]=(uintptr_t)thug_compound_collision_set_owner_draft};
/* 00411fa0. Known common prefix, already inlined in maintained413000. */
void *thug_rigid_collision_base_construct_draft(void *p){
 put(p,0,(uintptr_t)thug_rigid_collision_base_methods_draft);((uint16_t *)p)[4]=0;put(p,12,0);
 for(unsigned i=0;i<4;i++)put(p,16+i*4,i==3?0x3f800000:0);put(p,0xa0,0);
 for(unsigned i=0;i<32;i++)put(p,0x20+i*4,(i%16)%5==0?0x3f800000:0);
 return p;
}
/* 00412550. */
void *thug_box_collision_construct_draft(void *p){
 thug_rigid_collision_base_construct_draft(p);put(p,0,(uintptr_t)thug_box_collision_methods_draft);
 thug_bounds_reset((void *)((uint8_t *)p+0xa4));put(p,0xc4,0);((uint16_t *)p)[0x64]=0;
 const uint32_t b[]={0xc2480000,0xc1a00000,0xc2b40000,0x3f800000,0x41f00000,0x42100000,0x42b40000,0x3f800000};copy((uint8_t *)p+0xa4,b,32);return p;
}
/* 004133e0. */
void *thug_compound_collision_construct_draft(void *p,const ThugMemory *m){
 ((uint16_t *)p)[4]=0;put(p,12,0);put(p,0,(uintptr_t)thug_compound_collision_methods_draft);
 thug_bounds_reset((void *)((uint8_t *)p+0x14));void *n=collision_node((void *)UINTPTR_MAX,thug_collision_sentinel_methods_draft,m);
 put(p,0x38,0);put(p,0x10,(uintptr_t)n);((uint8_t *)p)[0x34]=1;return p;
}
/* 00411be0. */
void thug_compound_collision_append_draft(void *p,void *object,const ThugMemory *m){
 void *n=collision_node(object,thug_collision_node_methods_draft,m),*head=pointer(p,16);
 put(n,16,word(head,16));put(n,12,(uintptr_t)head);put(pointer(head,16),12,(uintptr_t)n);put(head,16,(uintptr_t)n);
}
/* 00414990. Valid relocated geometry and initialized successful heap/list. */
void *thug_moving_collision_create_draft(uint32_t kind,ThugCollisionObject *data,int32_t count,void *owner,const ThugMemory *m){
 void *p=0;
 if(kind==1){
  p=m->allocate(m->context,0xd0,1);if(p)thug_box_collision_construct_draft(p);
  if(count>0){ThugBounds b;thug_bounds_reset(&b);for(int32_t i=0;i<count;i++){thug_bounds_expand(&b,data[i].bounds.min);thug_bounds_expand(&b,data[i].bounds.max);}copy((uint8_t *)p+0xa4,&b,32);}
 }else if(kind==4){
  if(count==1){p=m->allocate(m->context,0xd4,1);if(p)thug_moving_collision_initialize(p,data);}
  else if(count>1){p=thug_allocate_array_storage(0x3c,m);if(p)thug_compound_collision_construct_draft(p,m);for(int32_t i=0;i<count;i++){void *child=m->allocate(m->context,0xd4,1);if(child)thug_moving_collision_initialize(child,&data[i]);thug_compound_collision_append_draft(p,child,m);}}
  else return 0;
 }else return 0;
 if(p){void (*set_owner)(void *,void *)=(void *)(uintptr_t)word(pointer(p,0),0x2c);set_owner(p,owner);thug_moving_collision_register_draft(p,owner,m);}return p;
}
/* 0040add0. */
uint32_t thug_collision_kind_draft(uint32_t name){switch(name){case 0xdd42aa66:case 0x2ba71070:case 0xe460abde:return 1;case 0x6aadf154:return 4;default:return 0;}}
typedef struct {ThugComponentMethods base;void (*bind)(void *,uint32_t,void *);uintptr_t missing[2];} CollisionComponentMethods;
extern const CollisionComponentMethods thug_collision_component_methods_draft;
/* 0041c920. */
void *thug_collision_component_create_draft(const ThugMemory *m){void *p=thug_allocate_zeroed(0x1c,m);if(p){thug_component_construct(p);put(p,0,(uintptr_t)&thug_collision_component_methods_draft);put(p,4,0xa432dc41);}return p;}
/* 0041c890. Always perform the actual manager lookup on the fallback path. */
void thug_collision_component_bind_draft(void *p,uint32_t kind,void *data){
 int32_t count=1;
 if(!data){void *model=thug_object_find_component(pointer(p,12),0x286a8d26),*renderer=pointer(model,0x208);
  void *asset=thug_asset_find(thug_asset_manager,word(renderer,0x30),0,diagnostics());
  if(asset){data=pointer(asset,0x8c);count=(int32_t)word(asset,0x88);}else count=0;
 }
 put(p,0x18,(uintptr_t)thug_moving_collision_create_draft(kind,data,count,pointer(p,12),memory()));
}
/* 0041c7b0. LevelObject implies an existing named scene sector. */
void thug_collision_component_initialize_draft(void *p,const ThugScriptStructure *s){
 uint32_t name=0;thug_script_get_checksum(s,0x2d7e583b,&name,0);uint32_t kind=thug_collision_kind_draft(name);if(!kind)return;
 uint32_t cls=0;thug_script_get_checksum(s,0x12b4e660,&cls,0);void *data=0;
 if(cls==0xb7b3bd86){uint32_t key;thug_script_get_checksum(s,0xa1dc81f9,&key,1);void *sector=thug_scenes_find_object(key);void *instance=pointer(sector,0x18);if(instance)data=pointer(instance,12);}
 ((const CollisionComponentMethods *)pointer(p,0))->bind(p,kind,data);
}
/* 00490ab0. */
void *thug_model_asset_geometry_draft(const void *p){return pointer(p,0xb4);}
/* 00493040. Requires the original valid one-part list when count==1. */
void *thug_model_renderer_collision_geometry_draft(const void *p){
 uint16_t n;__builtin_memcpy(&n,(const uint8_t *)p+0x4a,2);if(n!=1)return 0;
 void *head=pointer(p,0x10),*part=pointer(pointer(head,4),0);
 void *data=thug_asset_find(thug_asset_manager,word(part,0x10),1,diagnostics());return thug_model_asset_geometry_draft(data);
}
/* 0041c980; +4 frame context is passed explicitly only by the host ABI. */
void thug_collision_component_update_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 (void)q;(void)d;(void)m;void *collision=pointer(p,0x18);if(!collision)return;
 void *model=thug_object_find_component(pointer(p,12),0x286a8d26);void *geometry=model?thug_model_renderer_collision_geometry_draft(pointer(model,0x208)):0;
 void *owner=pointer(p,12);void (*set_position)(void *,const float *)=(void *)(uintptr_t)word(pointer(collision,0),0x14);
 void (*set_orientation)(void *,const float *)=(void *)(uintptr_t)word(pointer(collision,0),0x18);
 if(geometry){float v[4],matrix[16];for(unsigned i=0;i<3;i++){float a,b;__builtin_memcpy(&a,(uint8_t *)geometry+0x40+i*4,4);__builtin_memcpy(&b,(uint8_t *)owner+0x4c+i*4,4);v[i]=a+b;}put(v,12,word(owner,0x58));set_position(collision,v);thug_matrix_multiply(matrix,(float *)((uint8_t *)geometry+16),(float *)((uint8_t *)owner+0xc0));set_orientation(collision,matrix);}
 else{set_position(collision,(float *)((uint8_t *)owner+0x4c));set_orientation(collision,(float *)((uint8_t *)owner+0xc0));}
}
static void moved(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){((const CollisionComponentMethods *)pointer(p,0))->base.update(p,q,d,m);}
static void empty(void *p){(void)p;}
static void *dispose_pending(void *p,uint32_t flags,const ThugMemory *m){(void)p;(void)flags;(void)m;__builtin_trap();}
static uint32_t unhandled(void *p,uint32_t key,ThugScriptStructure *s,ThugScriptInstance *i){return thug_animation_unhandled_command(p,key,s,i,0,0);}
const CollisionComponentMethods thug_collision_component_methods_draft={
 .base={.dispose=dispose_pending,.update=thug_collision_component_update_draft,.initialize=thug_collision_component_initialize_draft,.finalize=empty,.unknown_10=empty,.refresh=thug_component_refresh,.unknown_18=thug_component_empty_two,.suspend=thug_component_suspend,.unknown_20=thug_component_empty_one,.moved=moved,.unknown_28=thug_component_empty_one,.descriptor=thug_component_descriptor_base,.checksum=unhandled},.bind=thug_collision_component_bind_draft
};
/* Typed no-result bridge for original412ff0/412070 virtual+18. */
void thug_moving_collision_orientation_set_bridge_draft(void *p,const float *v){thug_moving_collision_set_orientation(p,v);}
void thug_collision_component_update_entry_draft(void *p){thug_collision_component_update_draft(p,0,diagnostics(),memory());}
