/* 00528280: floor target shared by ledge and vertical-rail exits. */
#include "../../src/collision/probe.h"
#include "../../src/script/values.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
static void copy4(float *out,const float *in){for(unsigned i=0;i<4;i++){uint32_t v;__builtin_memcpy(&v,in+i,4);__builtin_memcpy(out+i,&v,4);}}
static float parameter(uint32_t key){float v;thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),key,&v,1);return v;}
uint8_t thug_walk_exit_floor_draft(void *p,const float from[4],float out[4],ThugCollisionProbe *probe,ThugCollisionQuery *q){
 (void)p;double height=parameter(0x6da7f696);height=R(height+height);
 copy4(probe->segment,from);probe->segment[1]=(float)R((double)probe->segment[1]+height);
 copy4(probe->segment+4,from);float depth=parameter(0xaebfa9cd);probe->segment[5]=(float)R((double)probe->segment[5]-depth);
 uint8_t hit=thug_collision_probe_query(probe,1,0,q);copy4(out,hit?probe->point:from);return hit?1:0;
}
