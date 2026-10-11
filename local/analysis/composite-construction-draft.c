#include "../../src/game/components.h"
#include "../../src/game/object_registry.h"
#include "../../src/game/nodes.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#include <stddef.h>

typedef struct CompositeDraft CompositeDraft;
typedef struct {
    CompositeDraft *(*dispose)(CompositeDraft *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
    uint32_t unavailable_4[4];
    void (*receive_event)(void *,ThugEvent *);
    void (*defer)(CompositeDraft *,const ThugDiagnostics *,const ThugMemory *);
    uint32_t (*active)(const CompositeDraft *);
    void (*finalize)(CompositeDraft *,const ThugDiagnostics *,const ThugMemory *);
    void (*add_from_parameters)(CompositeDraft *,ThugScriptStructure *,ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
    ThugObjectFrameStep frame_notification;
} CompositeMethodsDraft;
struct CompositeDraft {
    ThugUiObjectBase base;
    float position[4],previous_position[4],orientation[16],velocity[4];
    uint8_t parameter_sets_enabled,padding_bd[3];
    float orientation_c0[16];
    ThugObjectComponent *components;
    uint32_t flags;
};
_Static_assert(sizeof(CompositeDraft)==0x108,"Composite allocation");
_Static_assert(offsetof(CompositeDraft,components)==0x100,"Component head");
_Static_assert(offsetof(CompositeMethodsDraft,finalize)==0x20,"Finalize slot");
extern const CompositeMethodsDraft thug_composite_methods_draft;
extern void thug_object_defer_delete_draft(ThugUiObjectBase *,const ThugDiagnostics *,const ThugMemory *);
static const CompositeMethodsDraft *object_methods(const CompositeDraft *p){return (const void *)(uintptr_t)p->base.object.unknown_0;}
static const ThugComponentMethods *component_methods(const ThugObjectComponent *p){return (const void *)(uintptr_t)p->unknown_0;}
static ThugObjectComponent **type_next(ThugObjectComponent *p){return (void *)((uint8_t *)p+0x14);}
static double r24(double n){return thug_platform_round_x87_single(n);}
static void identity(float out[16]) {for(unsigned i=0;i<16;i++)out[i]=(i%5==0)?1:0;}

/* 0042bc40. Writes only the nine basis words. The three off-diagonal products
 * retained on the x87 stack keep a wider exponent; specified temporaries spill
 * to float32. All source reads precede the first output store. */
void thug_quaternion_basis_draft(const float q[4],float out[16]) {
    double x=q[0],y=q[1],z=q[2],w=q[3];
    double length=r24(r24(r24(r24(x*x)+r24(y*y))+r24(z*z))+r24(w*w));
    double scale=length>0?r24(2.0/length):0;
    double sx=r24(scale*x);
    float sy=(float)r24(scale*y),sz=(float)r24(scale*z);
    float wx=(float)r24(sx*w),wy=(float)r24((double)sy*w),wz=(float)r24((double)sz*w);
    double xx=r24(sx*x),xy=r24((double)sy*x),xz=r24((double)sz*x);
    float yy=(float)r24((double)sy*y),yz=(float)r24((double)sz*y);
    double zz=r24((double)sz*z);
    out[0]=(float)r24(1.0-r24((double)yy+zz));
    out[4]=(float)r24(xy+wz);out[8]=(float)r24(xz-wy);
    out[1]=(float)r24(xy-wz);out[5]=(float)r24(1.0-r24(zz+xx));
    out[9]=(float)r24((double)yz+wx);out[2]=(float)r24(xz+wy);
    out[6]=(float)r24((double)yz-wx);out[10]=(float)r24(1.0-r24((double)yy+xx));
}
/* 0045c0b0. The stored quaternion supplies XYZ; reconstruct nonnegative W.
 * Missing quaternion initializes the entire matrix, present quaternion only
 * replaces the nine basis words through the original converter. */
void thug_node_orientation_draft(const ThugScriptStructure *node,float out[16]) {
    float v[4];
    if(!thug_script_get_vector(node,0xc97f3aa9,v,0)){identity(out);return;}
    double squared=r24(r24(r24((double)v[2]*v[2])+r24((double)v[1]*v[1]))+r24((double)v[0]*v[0]));
    if(squared>1)squared=1;
    float q[4]={v[0],v[1],v[2],(float)r24(__builtin_sqrt(r24(1.0-squared)))};
    thug_quaternion_basis_draft(q,out);
}
/* 0045e510. Previous position and byte padding remain untouched. */
CompositeDraft *thug_composite_initialize_draft(CompositeDraft *p) {
    thug_ui_object_initialize(&p->base);p->base.object.unknown_0=(uintptr_t)&thug_composite_methods_draft;
    p->flags=0;
    for(unsigned i=0;i<4;i++)p->velocity[i]=(i==3)?1:0;
    for(unsigned i=0;i<4;i++)p->position[i]=(i==3)?1:0;
    identity(p->orientation);identity(p->orientation_c0);
    p->components=0;p->flags=0;p->parameter_sets_enabled=0;p->base.object.unknown_8_to_10[0]|=0x20;
    return p;
}
/* 0045f2a0. Capture the unsigned registry length, take the first matching factory.
 * The memory argument is a host ABI extension to registered zero-argument
 * factories, as already used by thug_physics_create. */
void *thug_component_create_registered_draft(const ThugComponentTypeRegistry *registry,uint32_t type,const ThugMemory *m) {
    uint32_t count=registry->count;
    for(uint32_t i=0;i<count;i++)if(registry->entries[i].type==type) {
        typedef void *(*Factory)(const ThugMemory *);
        return ((Factory)(uintptr_t)registry->entries[i].factory)(m);
    }
    return 0;
}
/* 0045f3e0. First registered type wins; an unknown type retains its old link. */
void thug_component_track_draft(const ThugComponentTypeRegistry *registry,ThugObjectComponent *component) {
    uint32_t count=registry->count,type=component->type;
    for(uint32_t i=0;i<count;i++)if(registry->entries[i].type==type) {
        *type_next(component)=thug_component_type_heads[i];thug_component_type_heads[i]=component;return;
    }
}
/* 0045f420. If a duplicate type entry does not contain the component, continue
 * into later entries. Clear its type-next only when it was actually removed. */
void thug_component_untrack_draft(const ThugComponentTypeRegistry *registry,ThugObjectComponent *component) {
    uint32_t count=registry->count,type=component->type;
    for(uint32_t i=0;i<count;i++)if(registry->entries[i].type==type) {
        ThugObjectComponent *p=thug_component_type_heads[i];
        if(p==component){thug_component_type_heads[i]=*type_next(component);*type_next(component)=0;return;}
        for(;p;p=*type_next(p))if(*type_next(p)==component) {
            *type_next(p)=*type_next(component);*type_next(component)=0;return;
        }
    }
}
/* 0045da30. Preserve the incoming component's own next pointer. */
void thug_composite_add_component_draft(CompositeDraft *p,ThugObjectComponent *component) {
    if(!p->components)p->components=component;
    else {ThugObjectComponent *last=p->components;while(last->next)last=last->next;last->next=component;}
    component->owner=p;thug_component_track_draft(thug_component_type_registry,component);
}
/* Host scope for original fixed-argument component virtuals, not an additional
 * recovered function. Preserve a caller's query and restore nested services. */
static ThugComponentServices component_scope(const ThugDiagnostics *d,const ThugMemory *m) {
    ThugComponentServices s={thug_component_services?thug_component_services->query:0,d,m};return s;
}
/* 0045db30. First pass finalizes using live next links. Reload the head for moved
 * notifications, after setting flags20 then40 in their original order. */
void thug_composite_finalize_draft(CompositeDraft *p,const ThugDiagnostics *d,const ThugMemory *m) {
    const ThugComponentServices *previous=thug_component_services,services=component_scope(d,m);thug_component_services=&services;
    for(ThugObjectComponent *c=p->components;c;c=c->next)component_methods(c)->finalize(c);
    p->flags|=0x20;p->flags|=0x40;
    for(ThugObjectComponent *c=p->components;c;c=c->next)component_methods(c)->moved(c,services.query,d,m);
    thug_component_services=previous;
}
/* 0045ee20. Descriptor type is required. With overrides, merge descriptor then
 * node parameters into a real temporary owned structure before initialization. */
void thug_composite_add_parameters_draft(CompositeDraft *p,ThugScriptStructure *descriptor,ThugScriptStructure *overrides,const ThugDiagnostics *d,const ThugMemory *m) {
    uint32_t type;thug_script_get_checksum(descriptor,0xb6015ea8,&type,1);
    ThugObjectComponent *component=thug_component_create_registered_draft(thug_component_type_registry,type,m);
    thug_composite_add_component_draft(p,component);
    const ThugComponentServices *previous=thug_component_services,services=component_scope(d,m);thug_component_services=&services;
    if(overrides) {
        ThugScriptStructure *s=thug_script_structure_allocate(8,m);
        if(s)s=thug_script_structure_initialize(s);
        thug_script_structure_merge(s,descriptor,m);thug_script_structure_merge(s,overrides,m);
        component_methods(component)->initialize(component,s);
        if(s){thug_script_structure_destroy(s,m);thug_script_structure_free(s,m);}
    } else component_methods(component)->initialize(component,descriptor);
    thug_component_services=previous;
}
/* 0045da90. Capture item storage and signed length before the first virtual call;
 * re-read the object's method table for each descriptor. */
void thug_composite_add_array_draft(CompositeDraft *p,ThugScriptArray *array,ThugScriptStructure *overrides,const ThugDiagnostics *d,const ThugMemory *m) {
    uint32_t *items=thug_script_array_items(array);int32_t count=(int32_t)array->count;
    for(int32_t i=0;i<count;i++)object_methods(p)->add_from_parameters(p,(void *)(uintptr_t)items[i],overrides,d,m);
}
/* 0045dad0. Rename through the real registry, then position/orientation and flag. */
void thug_composite_apply_node_draft(CompositeDraft *p,const ThugScriptStructure *node,const ThugMemory *m) {
    uint32_t name;
    if(thug_script_get_checksum(node,0xa1dc81f9,&name,0))thug_ui_object_set_id(&p->base,name,m);
    thug_node_position(node,p->position);thug_node_orientation_draft(node,p->orientation);
    if(thug_script_has_flag(node,0x23627fd7))p->base.object.unknown_8_to_10[0]|=2;
}
/* 0045f330. Zero allocation, concrete constructor, type metadata and real manager
 * registration. Failed storage cannot satisfy the original live-object contract. */
CompositeDraft *thug_composite_create_draft(ThugObjectManager *manager,const ThugMemory *m) {
    CompositeDraft *p=thug_allocate_zeroed(0x108,m);if(p)p=thug_composite_initialize_draft(p);
    thug_ui_object_set_type(&p->base,0xcdeb9229,m);manager->methods->add(manager,&p->base,m);return p;
}
/* 0045f3a0. Optional finalization tests only the low flag byte. */
CompositeDraft *thug_composite_create_from_array_draft(ThugObjectManager *manager,ThugScriptArray *array,ThugScriptStructure *node,uint32_t finalize,const ThugDiagnostics *d,const ThugMemory *m) {
    CompositeDraft *p=thug_composite_create_draft(manager,m);thug_composite_apply_node_draft(p,node,m);
    thug_composite_add_array_draft(p,array,node,d,m);
    if((uint8_t)finalize)object_methods(p)->finalize(p,d,m);
    return p;
}
/* 0045d890/0045e620. Unlink each component from both chains before real virtual
 * deletion, reloading the object head after each callback. Base destruction
 * unregisters the object and releases its owned scripts/references/parameters. */
void thug_composite_destroy_draft(CompositeDraft *p,const ThugDiagnostics *d,const ThugMemory *m) {
    p->base.object.unknown_0=(uintptr_t)&thug_composite_methods_draft;p->flags|=0x80;
    while(p->components) {
        ThugObjectComponent *c=p->components;p->components=c->next;
        thug_component_untrack_draft(thug_component_type_registry,c);component_methods(c)->dispose(c,1,m);
    }
    thug_ui_object_destroy(&p->base,d,m);
}
CompositeDraft *thug_composite_delete_draft(CompositeDraft *p,uint32_t flags,const ThugDiagnostics *d,const ThugMemory *m) {
    thug_composite_destroy_draft(p,d,m);if((uint8_t)flags&1)m->release(m->context,p);return p;
}
/* 0045d7c0/0045e500. Notify every component before deferred base deletion;
 * the active predicate is the complement of just bit zero. */
void thug_composite_defer_draft(CompositeDraft *p,const ThugDiagnostics *d,const ThugMemory *m) {
    for(ThugObjectComponent *c=p->components;c;c=c->next)component_methods(c)->unknown_10(c);
    thug_object_defer_delete_draft(&p->base,d,m);
}
uint32_t thug_composite_active_draft(const CompositeDraft *p){return (~p->flags)&1;}
/* The command/descriptor virtuals remain unavailable, not success replacements.
 * These recovered slots support construction/finalization/lifetime only. */
const CompositeMethodsDraft thug_composite_methods_draft={
    .dispose=thug_composite_delete_draft,.receive_event=thug_ui_object_event_bridge,
    .defer=thug_composite_defer_draft,.active=thug_composite_active_draft,
    .finalize=thug_composite_finalize_draft,.add_from_parameters=thug_composite_add_parameters_draft,
    .frame_notification=thug_component_empty_frame_bridge
};
