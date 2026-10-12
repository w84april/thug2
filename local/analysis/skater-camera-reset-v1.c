/* Original 00485b20 and 004f9ae0 camera settings/reset candidates.
 * Finite projection service contract remains the already verified PC24 path. */
#include "../../src/game/skater.h"
#include "../../src/script/params.h"
#include "../../src/platform/math.h"
#define R thug_platform_round_x87_single
extern uint32_t thug_score_get_split_layout_draft(void);
extern void thug_camera_projection_v2(void *);
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static void *ptr(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void real(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static float bits(uint32_t v){float f;__builtin_memcpy(&f,&v,4);return f;}
/* 00485b20 */
void thug_camera_set_fov_v1(void *p,float fov){real(p,0xac,fov);thug_camera_projection_v2(p);}
/* 004f9ae0: optional getters preserve caller bytes; required locals must exist.
 * Array storage and both component payloads must be valid caller-owned data. */
void thug_skater_camera_reset_v1(void *p,uint32_t mode,float duration){
 ThugObjectComponent *component=thug_object_find_component(ptr(p,12),0xc4e311fa);
 uint32_t layout=thug_score_get_split_layout_draft();
 ThugScriptArray *array=thug_script_get_global_array_text(layout==1?"Skater_Camera_2P_Vert_Array":layout==2?"Skater_Camera_2P_Horiz_Array":"Skater_Camera_Array",0);
 const ThugScriptStructure *s=thug_script_get_global_structure((uintptr_t)thug_script_array_structure(array,(int32_t)mode),0);
 put(p,0x24,mode);put(p,0x134,0);
 float fov,behind,above,tilt,origin,wallride;
 thug_script_get_float(s,0x94df1603,&fov,0);thug_script_get_float(s,0x52e6c41b,&behind,0);thug_script_get_float(s,0x0b96ae2d,&above,0);
 thug_script_get_float(s,0xe3c07609,&tilt,0);thug_script_get_float(s,0x012f6992,&origin,0);
 static const uint32_t fields[][2]={{0x7f0032ac,0x134},{0xadb6390e,0x138},{0xf54fb9c5,0x140},{0x2fa11029,0x144},{0x042fd4a0,0x148},{0xae47899b,0xe4},{0xe1e4e104,0xe8},{0xf386f4d9,0xec},{0x4882a1fe,0xf0},{0xbef0d195,0xf4},{0x3396be2a,0x124}};
 for(unsigned i=0;i<sizeof fields/sizeof fields[0];i++)thug_script_get_float(s,fields[i][0],(float *)((char *)p+fields[i][1]),0);
 put(p,0x118,0x3f800000);put(p,0x11c,0x3f800000);put(p,0x114,0x3f800000);
 thug_script_get_float(s,0x748743a7,&wallride,0);thug_script_get_float(s,0x5a7f5cc5,(float *)((char *)p+0x118),0);
 thug_script_get_float(s,0xd790b83d,(float *)((char *)p+0x114),0);thug_script_get_float(s,0xd414c22e,(float *)((char *)p+0x11c),0);
 real(p,0x110,wallride);uint32_t unused;thug_script_get_checksum_legacy(s,0xa1dc81f9,&unused,0);
 real(p,0xe0,fov);real(p,0x14c,(float)R((double)origin*12));real(p,0x12c,tilt);
 float b=(float)R((double)behind*12),a=(float)R((double)above*12);
 if(duration<=0){real(p,0xc4,b);put(p,0xc8,0);put(p,0xd4,0);real(p,0xd0,a);}
 else {real(p,0xc8,duration);real(p,0xd4,duration);double inverse=R((double)bits(0x3c888889)/duration);real(p,0xcc,(float)R(R((double)b-number(p,0xc4))*inverse));real(p,0xd8,(float)R(R((double)a-number(p,0xd0))*inverse));}
 thug_camera_set_fov_v1(ptr(component,0x18),layout==1?(float)R((double)fov*.5):fov);
 uint32_t angle=(mode==5||mode==6)?0x40490fdb:(mode==7||mode==8)?0x3fc90fdb:(mode==11||mode==12)?0xbfc90fdb:0;
 put(ptr(p,0x168),0x28,angle);
}
