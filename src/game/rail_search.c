#include "rail.h"
#include "../core/vector.h"
#include "../core/line.h"
#include "../script/params.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
_Static_assert(sizeof(ThugRailNode)==0x54,"Original rail node stride");
_Static_assert(offsetof(ThugRailNode,next)==0x40,"Original rail node link");
_Static_assert(offsetof(ThugObjectTransform,rail_nodes)==0x40,"Rail array offset");
_Static_assert(offsetof(ThugObjectTransform,rail_count)==0x48,"Rail count offset");
_Static_assert(offsetof(ThugObjectTransform,changed)==0x50,"Transform state offset");
/* Shared arithmetic in 57c600/57cc30; preserve the original x87 spill points. */
static void quarter(float out[4],const float a[4],const float b[4],double raise) {
    double sum[4],mean[4],delta[4],part[4];
    for(unsigned i=0;i<4;++i)sum[i]=R((double)b[i]+a[i]);
    sum[0]=(float)sum[0];sum[1]=(float)sum[1];
    for(unsigned i=0;i<4;++i)mean[i]=R(sum[i]*.5);
    mean[0]=(float)mean[0];mean[3]=(float)mean[3];
    for(unsigned i=0;i<4;++i)delta[i]=R(mean[i]-a[i]);
    delta[2]=(float)delta[2];delta[3]=(float)delta[3];
    for(unsigned i=0;i<4;++i)part[i]=R(delta[i]*.5);
    for(unsigned i=1;i<4;++i)part[i]=(float)part[i];
    for(unsigned i=0;i<4;++i) {
        double v=R((double)a[i]+part[i]);
        out[i]=(float)(i==1?R(v+raise):v);
    }
}
static uint8_t vertical(ThugCollisionProbe *p,const float start[4],ThugCollisionQuery *query) {
    float end[4]={start[0],(float)R((double)start[1]-12),start[2],(float)R((double)start[3]+1)};
    thug_collision_probe_set_points(p,start,end);
    return thug_collision_probe_query(p,1,0,query);
}
/* 0057c600: rail cross sweep and two support-height probes. */
uint8_t thug_rail_clearance(float ax,float ay,float az,float aw,float bx,float by,float bz,float bw,ThugCollisionQuery *query) {
    if(thug_skater_orientation_context->identifier==0xd443a2bc)return 1;
    const float a[4]={ax,ay,az,aw},b[4]={bx,by,bz,bw};
    ThugCollisionProbe p;thug_collision_probe_initialize(&p);
    float base[4],d[4],start[4],end[4];quarter(base,a,b,6);
    for(unsigned i=0;i<4;++i)d[i]=i==1?0:(float)R((double)b[i]-a[i]);
    thug_vector_set_length(d,7);
    float x=d[0];d[0]=d[2];d[2]=-x;
    for(unsigned i=0;i<4;++i){end[i]=(float)R((double)base[i]-d[i]);start[i]=(float)R((double)d[i]+base[i]);}
    uint8_t result=0;
    thug_collision_probe_set_points(&p,start,end);
    if(thug_collision_probe_query(&p,1,0,query))goto finish;
    thug_collision_probe_reverse(&p);
    if(thug_collision_probe_query(&p,1,0,query))goto finish;
    result=1;
    if(!vertical(&p,start,query))goto finish;
    float baseline=(float)R((double)base[1]-6),first=(float)R((double)p.point[1]-baseline);
    if(!vertical(&p,end,query))goto finish;
    double second=R((double)p.point[1]-baseline);
    if(first>-1&&second>-1)result=0;
    else {
        float high=first;double low=second;
        if(first<second){high=(float)second;low=first;}
        if(high>1&&low>-2)result=0;
    }
finish:
    thug_collision_probe_release(&p);return result;
}
/* 0057cc30: classify the collidable side of a connected rail. */
int32_t thug_rail_side(const ThugRailNode *node,const float direction[4],ThugCollisionQuery *query) {
    float a[4],b[4];__builtin_memcpy(a,node->position,16);__builtin_memcpy(b,node->next->position,16);
    ThugCollisionProbe p;thug_collision_probe_initialize(&p);
    float base[4],start[4],end[4];quarter(base,a,b,-6);
    double dw=R((double)b[3]-a[3]),dx=R((double)b[0]-a[0]);
    float dx_copy=(float)dx,dz=(float)R((double)b[2]-a[2]),y=0,z=dz;
    double length=R(__builtin_sqrt(R(R(dx*dx)+R((double)dz*dz))));
    if(length>0) {double inverse=R(4/length);dx=R(dx*inverse);y=(float)R(0*inverse);z=(float)R((double)dz*inverse);}
    float perp[3]={z,y,(float)-dx};
    for(unsigned i=0;i<3;++i){end[i]=(float)R((double)base[i]-perp[i]);start[i]=(float)R((double)perp[i]+base[i]);}
    end[3]=(float)R((double)base[3]-dw);start[3]=(float)R(dw+base[3]);
    thug_collision_probe_set_points(&p,start,end);
    uint8_t forward=thug_collision_probe_query(&p,1,0,query);
    thug_collision_probe_reverse(&p);
    uint8_t reverse=thug_collision_probe_query(&p,1,0,query);
    int32_t side=forward==reverse?0:forward?-1:1;
    if(side) {
        double dot=R(R(R(R((double)b[1]-a[1])*direction[1])+R((double)dz*direction[2]))+R((double)dx_copy*direction[0]));
        if(dot<0)side=-side;
    }
    thug_collision_probe_release(&p);return side;
}


static uint8_t overlaps(const float lo[4],const float hi[4],const ThugRailNode *n) {
    return !(lo[0]>n->maximum[0]||hi[0]<n->minimum[0]||lo[2]>n->maximum[2]||hi[2]<n->minimum[2]||lo[1]>n->maximum[1]||hi[1]<n->minimum[1]);
}
static double dot(const float a[4],const float b[4]) {
    return R(R(R((double)a[0]*b[0])+R((double)a[2]*b[2]))+R((double)a[1]*b[1]));
}
/* 0057e2d0: point/segment candidate ranking and output commit. */
uint8_t thug_rail_search(ThugObjectTransform *world,const float from[4],const float to[4],float out[4],ThugRailNode **out_node,const ThugRailNode *skip,float minimum_alignment,int32_t requested_side,ThugCollisionQuery *query) {
    float line[8];thug_segment_initialize(line);
    __builtin_memcpy(line,from,16);__builtin_memcpy(line+4,to,16);
    float lo[4],hi[4];thug_segment_bounds(line,line+4,lo,hi);
    float radius=(float)thug_script_get_global_number(0xf840753e,0);
    for(unsigned j=0;j<3;++j){lo[j]=(float)R((double)lo[j]-radius);hi[j]=(float)R((double)hi[j]+radius);}
    float best=10000000,selected[4];ThugRailNode *selected_node=0;uint8_t found=0;
    for(int32_t i=0;i<world->rail_count;++i) {
        ThugRailNode *n=world->rail_nodes+i;
        if((n->flags&0x10)||n==skip||!(n->flags&4))continue;
        if(!n->next) {
            if(n->previous||!overlaps(lo,hi,n))continue;
            float relative[4],direction[4],projection[4];
            thug_vector_difference(relative,n->position,from);thug_vector_difference(direction,to,from);
            thug_vector_normalize(direction);
            thug_vector_scaled(projection,(float)dot(relative,direction),direction);
            thug_vector_subtract(relative,projection);
            double distance=thug_vector_length(relative);
            if(distance>radius)continue;
            double weighted=R(distance+distance);
            if(best<weighted)continue;
            best=(float)weighted;__builtin_memcpy(selected,n->position,16);selected_node=n;found=1;
        } else {
            if(!overlaps(lo,hi,n))continue;
            float rail[8];thug_segment_initialize(rail);
            __builtin_memcpy(rail,n->position,16);__builtin_memcpy(rail+4,n->next->position,16);
            if(!thug_rail_clearance(n->position[0],n->position[1],n->position[2],n->position[3],n->next->position[0],n->next->position[1],n->next->position[2],n->next->position[3],query))continue;
            float on_line[4],on_rail[4],ta,tb;
            if(!thug_segment_closest_points(line,rail,on_line,on_rail,&ta,&tb,1))continue;
            float difference[4],rail_direction[4],motion[4];
            thug_vector_difference(difference,on_rail,on_line);float distance=(float)thug_vector_length(difference);
            thug_vector_difference(rail_direction,rail+4,rail);thug_vector_difference(motion,to,from);
            rail_direction[1]=motion[1]=0;thug_vector_normalize(rail_direction);thug_vector_normalize(motion);
            float alignment=(float)__builtin_fabs(dot(motion,rail_direction));
            if(motion[0]==0&&motion[2]==0&&alignment==0)alignment=1;
            float weighted=(float)R(R(1.121999979019165-alignment)*distance);
            float effective=(float)R(R(2.-alignment)*distance);
            if(requested_side) {
                float direction[4];thug_vector_difference(direction,to,from);
                if(thug_rail_side(n,direction,query)!=requested_side)weighted=(float)R((double)weighted+weighted);
            }
            if(!(weighted<best))continue;
            if(minimum_alignment!=1&&__builtin_fabsf(alignment)<minimum_alignment)continue;
            best=weighted;
            if(effective>radius)found=0;
            else {__builtin_memcpy(selected,on_rail,16);selected_node=n;found=1;}
        }
    }
    if(found) {
        uint32_t x;__builtin_memcpy(&x,selected,4);
        if((x&0x7f800000)==0x7f800000&&(x&0x7fffff))x|=0x400000;
        __builtin_memcpy(out,&x,4);for(unsigned j=1;j<4;++j)__builtin_memcpy(out+j,selected+j,4);
        *out_node=selected_node;
    }
    return found;
}
#undef R
