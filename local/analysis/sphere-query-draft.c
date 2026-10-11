#include "sphere-query-draft.h"
#include "../../src/platform/math.h"
#include <stddef.h>
_Static_assert(sizeof(ThugSphereHitDraft)==44,"Sphere hit stride");
_Static_assert(offsetof(ThugSphereResultDraft,direction)==0x584,"Sphere direction offset");
_Static_assert(offsetof(ThugSphereResultDraft,count)==0x598,"Sphere hit count offset");
_Static_assert(offsetof(ThugSphereResultDraft,mode)==0x5a0,"Sphere mode offset");
extern uint32_t thug_sphere_triangle_draft(const float *,const float *,const float *,const float *,float *,float *);
extern uint32_t thug_swept_sphere_triangle_draft(const float *,const float *,const float *,const float *,float *,float,const float *,float *,float *);
/* 00691990 is separate from the segment probe's default cache at00691974. */
ThugCollisionCache *thug_sphere_default_cache_draft;
/* Comparison ABI only: fixtures map the three original BSP globals to this
 * storage. Recovered callers continue to pass an explicit query context. */
ThugCollisionQuery thug_sphere_query_fixture_state;
static double r(double x){return __builtin_isnan(x)?-__builtin_nan(""):thug_platform_round_x87_single(x);}
static double add(double a,double b){return r(a+b);}
static double mul(double a,double b){return r(a*b);}
/* 0048c940. First nonnull grid in the sentinel-terminated scene list. The
 * sphere argument pushed by410240 is never read by the original function. */
ThugCollisionGrid *thug_collision_first_grid_draft(void){
    ThugCollisionSceneNode *node=thug_collision_scene_list;
    if(node->scene==(ThugCollisionScene *)(uintptr_t)UINT32_MAX)return NULL;
    while(node){
        ThugCollisionSceneNode *next=node->next;
        if(next->scene==(ThugCollisionScene *)(uintptr_t)UINT32_MAX)next=NULL;
        ThugCollisionGrid *grid=node->scene->collision;
        if(grid)return grid;
        node=next;
    }
    return NULL;
}
/* 004110b0. Static sphere virtual: real BSP candidates, face flags, vertex
 * decoding, stationary/swept contacts and ordered writes to the 32-hit array. */
uint8_t thug_static_collision_sphere_draft(const ThugCollisionInstance *instance,const float *sphere,
    const ThugBounds *bounds,ThugSphereResultDraft *result,ThugCollisionQuery *query_state){
    uint16_t storage[2048];uint32_t count;
    const uint16_t *faces=thug_collision_query(instance->geometry,bounds,&count,storage,0x800,query_state);
    for(uint32_t i=0;i<count;i++){
        const ThugCollisionObject *object=instance->geometry;
        const uint8_t *face=(const uint8_t *)object->faces+faces[i]*(object->small_faces?8:10);
        uint16_t flags=*(const uint16_t *)face;
        if((flags&result->excluded_flags)||((uint16_t)~flags&result->required_flags))continue;
        float a[4],b[4],c[4],point[4],normal[4],time=0;
        float *vertices[3]={a,b,c};
        for(unsigned corner=0;corner<3;corner++){
            uint32_t vertex=object->small_faces?face[4+corner]:((const uint16_t *)(face+4))[corner];
            thug_collision_vertex_into(object,vertex,vertices[corner]);
        }
        uint32_t hit=result->travel==0
            ?thug_sphere_triangle_draft(sphere,a,b,c,point,normal)
            :thug_swept_sphere_triangle_draft(sphere,a,b,c,&time,result->travel,result->direction,point,normal);
        if(!(uint8_t)hit)continue;
        if(result->count==32)return 1;
        ThugSphereHitDraft *out=result->hits+result->count;
        for(unsigned j=0;j<4;j++)out->normal[j]=normal[j];
        out->flag_40=(uint8_t)(flags&0x40);out->checksum=instance->checksum;
        for(unsigned j=0;j<4;j++)out->point[j]=point[j];
        if(result->travel>0)out->time=time;
        ++result->count;
        if(result->mode==2)return 1;
    }
    return (int32_t)result->count>0;
}
/* 00410240. Complete scene sphere query. An invalid/missing cache first runs
 * grid_bounds for its original stamp/output side effects, then performs the
 * selected-scene traversal. Virtual return values do not stop traversal. */
uint8_t thug_collision_scene_sphere_draft(const float sphere[5],ThugSphereResultDraft *result,
    const ThugCollisionCache *cache,ThugCollisionQuery *query_state){
    ThugBounds bounds;float point[4];double negative=mul(sphere[4],-1);
    for(unsigned i=0;i<4;i++)point[i]=(float)add(sphere[i],i==3?sphere[4]:negative);
    thug_bounds_from_point(&bounds,point);
    for(unsigned i=0;i<4;i++)point[i]=(float)add(sphere[i],sphere[4]);
    thug_bounds_expand(&bounds,point);
    if(result->travel!=0){
        for(unsigned i=0;i<4;i++){
            double motion=mul(result->travel,result->direction[i]);if(i)motion=(float)motion;
            double position=add(motion,sphere[i]);if(i>=2)position=(float)position;
            point[i]=(float)add(position,i==3?sphere[4]:negative);
        }
        thug_bounds_expand(&bounds,point);
        for(unsigned i=0;i<4;i++){
            double motion=mul(result->travel,result->direction[i]);if(i)motion=(float)motion;
            double position=add(motion,sphere[i]);if(i)position=(float)position;
            point[i]=(float)add(position,sphere[4]);
        }
        thug_bounds_expand(&bounds,point);
    }
    uint8_t valid=cache&&thug_bounds_contains(&cache->bounds,&bounds);
    if(!valid){
        ThugCollisionGrid *grid=thug_collision_first_grid_draft();if(!grid)return 0;
        thug_collision_grid_bounds(grid,&bounds);
    }
    result->count=0;
    for(unsigned i=0;i<4;i++){
        double pad=i==3?1:0.5;
        bounds.max[i]=(float)add(bounds.max[i],pad);bounds.min[i]=(float)add(bounds.min[i],-pad);
    }
    if(valid){
        for(uint32_t i=0;i!=(uint32_t)cache->static_count;i++){
            const ThugCachedCollision *entry=cache->objects+i;
            if(thug_bounds_overlap(&bounds,entry->bounds)){
                ThugSphereMethodDraft method=(ThugSphereMethodDraft)(uintptr_t)entry->object->methods->unknown_3c_to_4c[1];
                method(entry->object,sphere,&bounds,result,query_state);
            }
        }
    }else{
        float segment[8];__builtin_memcpy(segment,&bounds,32);
        ThugCollisionGrid **selected=thug_collision_select_scenes(segment);if(!selected)return 0;
        for(;*selected;selected++){
            int32_t count;ThugCollisionInstance **objects=thug_collision_grid_query(*selected,segment,&count);
            for(;*objects;objects++){
                ThugCollisionInstance *instance=*objects;
                if(instance->methods->intersects(instance,&bounds)){
                    ThugSphereMethodDraft method=(ThugSphereMethodDraft)(uintptr_t)instance->methods->unknown_3c_to_4c[1];
                    method(instance,sphere,&bounds,result,query_state);
                }
            }
        }
    }
    return (int32_t)result->count>0;
}
/* 00418300. The original consumes one unused argument with ret4. */
uint8_t thug_sphere_probe_query_draft(void *probe,uint32_t unused,ThugCollisionQuery *query_state){
    (void)unused;ThugSphereResultDraft *result=(void *)((uint8_t *)probe+0x14);
    ThugCollisionCache *cache;__builtin_memcpy(&cache,(uint8_t *)probe+0xb5c,4);
    result->mode=1;if(!cache)cache=thug_sphere_default_cache_draft;
    return thug_collision_scene_sphere_draft(probe,result,cache,query_state);
}
