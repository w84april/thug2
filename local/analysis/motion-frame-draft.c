#include "../../src/game/components.h"
#include "../../src/core/timing.h"
#include "../../src/core/matrix.h"
#include "../../src/platform/math.h"
static uint32_t word(const void *p,unsigned o){uint32_t v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){__builtin_memcpy((char *)p+o,&v,4);}
static float number(const void *p,unsigned o){float v;__builtin_memcpy(&v,(const char *)p+o,4);return v;}
static void set(void *p,unsigned o,float v){__builtin_memcpy((char *)p+o,&v,4);}
static void *pointer(const void *p,unsigned o){return (void *)(uintptr_t)word(p,o);}
static double r(double v){return thug_platform_round_x87_single(v);}
/* 004258b0. Pre-multiply the owner's basis, then repair the other two axes. */
void thug_motion_rotate_axis_draft(void *p,uint32_t axis,float angle){
 if(axis>2)return;float rotation[16],*matrix=(void *)((char *)pointer(p,12)+0x6c);
 if(axis==0)thug_matrix_rotation_x(rotation,angle);else if(axis==1)thug_matrix_rotation_y(rotation,angle);else thug_matrix_rotation_z(rotation,angle);
 thug_matrix_multiply(matrix,rotation,matrix);thug_matrix_orthogonalize(matrix,axis);
}
/* 00425a80. Axis is an internal0..2 index; retain each original float spill. */
uint8_t thug_motion_rotate_step_draft(void *p,uint32_t axis){
 unsigned o=axis*4;uint8_t done=0;
 if(number(p,0x16c+o)!=0){
  set(p,0x15c+o,(float)r(r((double)number(p,0x1e0)*number(p,0x16c+o))+number(p,0x15c+o)));
  if(__builtin_fabsf(number(p,0x14c+o))<__builtin_fabsf(number(p,0x15c+o))&&(number(p,0x15c+o)>0)==(number(p,0x14c+o)>0))put(p,0x15c+o,word(p,0x14c+o));
 }
 if(number(p,0x17c+o)!=0){
  double delta=r((double)number(p,0x1e0)*number(p,0x17c+o));
  if(__builtin_fabs(r((double)number(p,0x15c+o)-number(p,0x14c+o)))<__builtin_fabs(delta)){
   put(p,0x15c+o,word(p,0x14c+o));put(p,0x17c+o,0);return number(p,0x14c+o)==0;
  }
  set(p,0x15c+o,(float)r((double)number(p,0x15c+o)-delta));
 }
 float angle=(float)r((double)number(p,0x15c+o)*number(p,0x1e0));
 if(!(word(p,0x1c)&(0x20u<<axis))){
  int before=number(p,0x12c+o)>number(p,0x13c+o);
  set(p,0x13c+o,(float)r((double)angle+number(p,0x13c+o)));
  if(before!=(number(p,0x12c+o)>number(p,0x13c+o))){done=1;angle=(float)r((double)angle-r((double)number(p,0x13c+o)-number(p,0x12c+o)));}
 }
 thug_motion_rotate_axis_draft(p,axis,angle);return done;
}
/* 00425c70. The flags are reread between axes; completed axes clear in order. */
void thug_motion_rotate_axes_draft(void *p){for(uint32_t axis=0;axis<3;axis++){uint32_t flag=1u<<axis;if((word(p,0x18)&flag)&&thug_motion_rotate_step_draft(p,axis))put(p,0x18,word(p,0x18)&~flag);}}
/* 00424440. Advance interpolation time and preserve its separately stored sum. */
void thug_motion_interpolate_draft(void *p){
 float t=(float)r((double)number(p,0x1e0)+number(p,0x1c8));set(p,0x1c8,t);
 if(number(p,0x1c4)==0||t>=number(p,0x1c4)){t=1;put(p,0x18,word(p,0x18)&~0x20u);}else t=(float)r((double)t/number(p,0x1c4));
 thug_matrix_interpolate(pointer(p,0x1cc),(void *)((char *)pointer(p,12)+0x6c),t);
}
/* 00423740. Period is nonzero. Modulo and doubled numerator wrap as uint32;
 * the divisor is loaded with FIDIV as signed, independently of the modulo. */
void thug_motion_bob_draft(void *p){
 uint32_t period=word(p,0x1dc),n=((thug_elapsed_time()+thug_timer_offset)%period)*2;
 double phase=(int32_t)n;if((int32_t)n<0)phase=r(phase+0x1p32);
 phase=r(r(phase*0x1.921fb6p+1)/(int32_t)period);
 float displacement=(float)r(thug_platform_sin(phase)*number(p,0x1d8));set(p,0x1d4,displacement);
 void *owner=pointer(p,12);put(p,0x1d0,word(owner,0x50));set(owner,0x50,(float)r((double)displacement+number(owner,0x50)));
}
/* 00424200. Destination interpolation and velocity use the original ordered
 * PC24 intermediates and float stores; node arrival uses the real script path. */
uint8_t thug_motion_translate_draft(void *p,const ThugDiagnostics *d,const ThugMemory *m){
 void *owner=pointer(p,12);float negative[4];for(unsigned i=0;i<4;i++)negative[i]=-number(owner,0x4c+4*i);
 if(number(p,0x124)!=0){double speed=r(r(r(thug_frame_duration()*60.0)*number(p,0x124))+number(p,0x20));set(p,0x20,(float)speed);
  if(speed>=number(p,0x120)){put(p,0x20,word(p,0x120));put(p,0x124,0);}}
 double progress=r(r((double)number(p,0x20)*number(p,0x1e0))+number(p,0x11c));set(p,0x11c,(float)progress);
 if(progress>=number(p,0x118)){
  owner=pointer(p,12);for(unsigned i=0;i<4;i++)put(owner,0x4c+4*i,word(p,0x108+4*i));
  if(word(p,0x128))thug_motion_arrive_at_node(p,word(p,0x128),d,m);
  owner=pointer(p,12);for(unsigned i=0;i<4;i++)put(owner,0xac+4*i,i==3?0x3f800000:0);return 1;
 }
 double delta[4];for(unsigned i=0;i<4;i++){delta[i]=r((double)number(p,0x108+4*i)-number(p,0x18c+4*i));if(i>=2)delta[i]=(float)delta[i];}
 float factor=(float)r(progress/number(p,0x118));double product[4];for(unsigned i=0;i<4;i++){product[i]=r(delta[i]*factor);if(i!=2)product[i]=(float)product[i];}
 owner=pointer(p,12);for(unsigned j=0;j<4;j++){unsigned i=(j+2)&3;set(owner,0x4c+4*i,(float)r(product[i]+number(p,0x18c+4*i)));}
 owner=pointer(p,12);double velocity[4];for(unsigned i=0;i<4;i++){velocity[i]=r((double)negative[i]+number(owner,0x4c+4*i));if(i)velocity[i]=(float)velocity[i];}
 double inverse=r(1.0/number(p,0x1e0));for(unsigned j=0;j<4;j++){unsigned i=(j+2)&3;set(owner,0xac+4*i,(float)r(velocity[i]*(i?(float)inverse:inverse)));}return 0;
}
/* Frame integration frontier. Unsupported path-following, rail motion and
 * collision-aware ballistic routines still trap at their real entry points. */
uint32_t *thug_motion_frame_boundary_draft;
extern uint32_t *thug_particle_setup_motion_boundary_draft;
void thug_particle_setup_motion_boundary_frame_draft(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
static void unavailable(uint32_t address,void *p){uint32_t *b=thug_motion_frame_boundary_draft;if(b){b[0]=address;b[1]=(uintptr_t)p;b[2]=word(p,12);b[3]=1;}__builtin_trap();}
void thug_motion_frame_prefix_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
 if(thug_particle_setup_motion_boundary_draft)thug_particle_setup_motion_boundary_frame_draft(p,q,d,m);
 set(p,0x1e0,(float)thug_frame_duration());
 if(word(p,0x18)){
  if(word(p,0x18)&0x80){put(pointer(p,12),0x50,word(p,0x1d0));thug_motion_bob_draft(p);}
  if(word(p,0x18)&7)thug_motion_rotate_axes_draft(p);
  if(word(p,0x18)&0x20)thug_motion_interpolate_draft(p);
  if(word(p,0x18)&8){if(thug_motion_translate_draft(p,d,m))put(p,0x18,word(p,0x18)&~8u);}
  else if(word(p,0x18)&0x10)unavailable(0x426e70,p);
  else if(word(p,0x18)&0x200)unavailable(0x4246a0,p);
  if(word(p,0x18)&0x100)unavailable(0x424870,p);
 }
 if(__builtin_fabsf(number(p,0x1a0))>0){
  double acceleration=number(p,0x1a0)>0?384.0:-384.0;
  if((number(p,0x1a0)>0)!=(number(p,0x19c)>0))put(p,0x19c,0);
  double change=r(acceleration*number(p,0x1e0));float delta=(float)r(r(r(.5*change)+number(p,0x19c))*number(p,0x1e0));
  set(p,0x19c,(float)r(change+number(p,0x19c)));
  if(number(p,0x1a0)>0?delta>number(p,0x1a0):delta<number(p,0x1a0)){put(p,0x19c,0);delta=number(p,0x1a0);}
  void *owner=pointer(p,12);set(owner,0x50,(float)r((double)delta+number(owner,0x50)));set(p,0x1a0,(float)r((double)number(p,0x1a0)-delta));
 }else put(p,0x19c,0);
 void *owner=pointer(p,12);if(word(owner,0x14)>15)thug_matrix_copy((void *)((char *)owner+0xc0),(void *)((char *)owner+0x6c));
}
void thug_motion_frame_proximity_boundary_draft(void *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)q;(void)d;(void)m;unavailable(0x4ec560,p);}
