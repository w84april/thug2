#include "decal_scene.h"
#include "../collision/scene.h"
#include "../core/timing.h"
#include "../core/checksum.h"
#include "../core/number.h"
#include "../script/params.h"
#include "../game/stats.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
static void copy(void *out,const void *in,unsigned n) {
    for(unsigned i=0;i<n;++i){uint32_t w;__builtin_memcpy(&w,(const uint8_t *)in+i*4,4);__builtin_memcpy((uint8_t *)out+i*4,&w,4);}
}
ThugObjectLookupTable *thug_decal_previous_points; /*7004b4*/
ThugTextureDictionary *thug_decal_texture_dictionary; /*700f20*/
ThugRenderGeometry *thug_decal_selected_geometry[128]; /*700510*/
ThugCollisionInstance *thug_decal_selected_collision[128]; /*700710*/
static ThugDecalPrevious *next_previous(void) {
    ThugObjectLookupTable *table=thug_decal_previous_points;
    return thug_object_table_next(table)&&table->iteration_node?table->iteration_node->value:NULL;
}
/* 0x004928a0. Tracking keys and projection types are separate arguments.
 * The first tracked point is recorded without projection; later calls reuse
 * a recent nearby point. Scene selection precedes expanded object filtering.
 * Original fixed candidate arrays require room for their null terminator. */
uint8_t thug_decal_project_scene(const float from[4],const float to[4],float width,float height,
    float rotation,float angle,float lifetime,const char *texture_name,uint32_t type,
    uint32_t tracking_id,uint8_t flag,void *texture,const ThugMemory *memory) {
    thug_decal_reserved_slots=thug_script_get_global_integer(0x26fcb7be,1);
    ThugDecalPrevious *previous=NULL;
    if(tracking_id) {
        uint32_t now=thug_frame_time();
        thug_decal_previous_points->iteration_bucket=UINT32_MAX;
        thug_decal_previous_points->iteration_node=NULL;
        previous=next_previous();
        while(previous) {
            ThugDecalPrevious *expired=NULL;
            if(now<previous->timestamp||now-previous->timestamp>500)expired=previous;
            else if(previous->type==tracking_id) {
                double x=R24((double)from[0]-previous->position[0]);
                double y=R24((double)from[1]-previous->position[1]);
                double z=R24((double)from[2]-previous->position[2]);
                double squared=R24(R24(R24(z*z)+R24(y*y))+R24(x*x));
                if(squared<4356.0f)break;
            }
            previous=next_previous();
            if(expired){uint32_t key=(uintptr_t)expired;thug_object_table_remove(thug_decal_previous_points,&key,memory);memory->release(memory->context,expired);}
        }
        if(!previous) {
            ThugDecalPrevious *point=memory->allocate(memory->context,24,1);
            point->type=tracking_id;copy(point->position,from,4);point->timestamp=now;
            uint32_t key=(uintptr_t)point;thug_object_table_insert(thug_decal_previous_points,&key,point,memory);return 1;
        }
    }
    if(!texture)texture=thug_texture_dictionary_find(thug_decal_texture_dictionary,thug_crc32_string(texture_name));
    float segment[8];thug_collision_segment_copy(segment,from,to);
    ThugBounds bounds,expanded;thug_bounds_from_point(&bounds,segment);thug_bounds_expand(&bounds,segment+4);
    for(unsigned i=0;i<3;++i){expanded.min[i]=(float)R24((double)bounds.min[i]-width);expanded.max[i]=(float)R24((double)bounds.max[i]+width);}
    expanded.min[3]=expanded.max[3]=1;
    ThugCollisionGrid **grids=thug_collision_select_scenes(segment);
    if(!grids||!*grids)return 0;
    int32_t count=0;
    do {
        ThugCollisionInstance **objects=thug_collision_grid_bounds(*grids++,&expanded);
        if(!objects)continue;
        for(;*objects;++objects) {
            ThugCollisionInstance *object=*objects;const ThugBounds *b=object->methods->bounds(object);
            if(b->min[0]>expanded.max[0]||expanded.min[0]>b->max[0]||
               b->min[2]>expanded.max[2]||expanded.min[2]>b->max[2]||
               b->min[1]>expanded.max[1]||expanded.min[1]>b->max[1])continue;
            thug_decal_selected_geometry[count]=thug_scenes_find_object(object->checksum);
            thug_decal_selected_collision[count++]=object;
        }
    } while(*grids);
    if(count<=0)return 0;
    thug_decal_selected_geometry[count]=NULL;thug_decal_selected_collision[count]=NULL;
    uint8_t result=0;
    if(!tracking_id||previous->position[0]!=from[0]||previous->position[2]!=from[2]) {
        ThugDecalProjection projection;thug_decal_projection_initialize(&projection);
        copy(projection.from,from,4);copy(projection.to,to,4);
        projection.width=width;projection.height=height;projection.rotation=rotation;
        projection.angle=angle;projection.lifetime=lifetime;projection.texture=texture;
        projection.type=type;projection.previous=previous?previous->position:NULL;projection.flag=flag;
        ThugDecalBuffer *buffer=thug_decal_project(thug_decal_selected_geometry,thug_decal_selected_collision,&projection,memory);
        result=buffer!=NULL;
        if(!tracking_id&&buffer) {
            uint32_t elapsed=thug_truncate_double_low_word(R24(thug_frame_duration()*1000));
            thug_decal_advance_lifetime(elapsed,buffer);thug_decal_refresh_colors(buffer);
            /* 5480c0 is the shared +4 accessor, also used on network objects.
             * Here its receiver is the texture wrapper, exactly as in the PC. */
            uint32_t connection=(uintptr_t)thug_network_first_connection((const ThugNetworkState *)texture);__builtin_memcpy((uint8_t *)buffer+0x1c04,&connection,4);
        }
    }
    if(previous){copy(previous->position,from,4);previous->timestamp=thug_frame_time();}
    return result;
}

#undef R24
