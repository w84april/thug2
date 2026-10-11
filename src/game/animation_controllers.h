#ifndef THUG_GAME_ANIMATION_CONTROLLERS_H
#define THUG_GAME_ANIMATION_CONTROLLERS_H
#include "animation.h"
#include "animation_cache.h"
#include "stats.h"
#include "../script/runtime.h"
typedef struct { ThugAnimationController base; uint32_t unknown_14; ThugKeyframeAnimation *animation; ThugAnimationReader *reader; uint32_t animation_namespace; int32_t cache_index; } ThugStandardAnimationController;
typedef struct { ThugAnimationController base; ThugAnimationChannel *timeline; ThugAnimationReader *reader; void *animation; uint32_t animation_namespace; } ThugTimedAnimationController;
typedef struct { ThugAnimationController base; void *animation; ThugAnimationReader *reader; uint32_t animation_namespace; float weight; } ThugWeightedAnimationController;
typedef struct { ThugAnimationController base; uint8_t first,second,padding[2]; } ThugFlagAnimationController;
typedef struct { ThugAnimationController base; float vectors[64][4]; uint8_t unknown_414[0x440]; } ThugPoseAnimationController;
typedef struct {
    uint32_t name,target; float scale; uint32_t index;
    float rotation[4],velocity[4],vector[4],offset[4],quaternion[4];
    uint8_t enabled,use_vector,flag,padding;
} ThugBoneAnimationRecord;
typedef struct { ThugAnimationController base; ThugBoneAnimationRecord records[4]; } ThugBoneAnimationController;
extern const ThugAnimationControllerMethods thug_timed_animation_methods,thug_weighted_animation_methods,thug_flag_animation_methods,thug_pose_animation_methods,thug_bone_animation_methods;
double thug_animation_state_duration(const ThugAnimationState *,uint32_t,const ThugDiagnostics *);
double thug_animation_component_duration(const ThugAnimationComponent *,uint32_t,const ThugDiagnostics *);
uint8_t thug_animation_parse_range(float *,float *,float current,float duration,const ThugScriptStructure *,uint32_t unused);
uint8_t thug_animation_parse_loop(uint32_t *,const ThugScriptStructure *);
ThugAnimationController *thug_timed_animation_initialize(ThugAnimationController *,ThugAnimationChannel *,const ThugDiagnostics *,const ThugMemory *);
void thug_timed_animation_destroy(ThugAnimationController *,const ThugMemory *);
ThugAnimationController *thug_timed_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
void thug_timed_animation_configure(ThugAnimationController *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_timed_animation_command(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
ThugAnimationController *thug_weighted_animation_initialize(ThugAnimationController *,ThugAnimationChannel *,ThugSkaterBody *,const ThugDiagnostics *,const ThugMemory *);
void thug_weighted_animation_destroy(ThugAnimationController *,const ThugMemory *);
ThugAnimationController *thug_weighted_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
uint32_t thug_weighted_animation_command(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
ThugAnimationController *thug_flag_animation_initialize(ThugAnimationController *,ThugAnimationChannel *);
void thug_flag_animation_destroy(ThugAnimationController *);
ThugAnimationController *thug_flag_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
void thug_flag_animation_configure(ThugAnimationController *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
ThugAnimationController *thug_pose_animation_initialize(ThugAnimationController *,ThugAnimationChannel *);
void thug_pose_animation_destroy(ThugAnimationController *);
ThugAnimationController *thug_pose_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
uint32_t thug_animation_unhandled_command(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
ThugAnimationController *thug_bone_animation_initialize(ThugAnimationController *,ThugAnimationChannel *,ThugSkaterBody *);
void thug_bone_animation_destroy(ThugAnimationController *);
ThugAnimationController *thug_bone_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
uint32_t thug_bone_animation_find(const ThugBoneAnimationController *,uint32_t);
uint8_t thug_bone_animation_all_enabled(const ThugBoneAnimationController *);
void thug_bone_animation_enable_all(ThugBoneAnimationController *);
void thug_bone_animation_disable_all(ThugBoneAnimationController *);
void thug_bone_animation_set_rotation(ThugBoneAnimationController *,const float *);
void thug_bone_animation_set_velocity(ThugBoneAnimationController *,const float *);
void thug_bone_animation_setup(ThugBoneAnimationController *,uint32_t all,uint32_t index,const ThugScriptStructure *);
void thug_bone_animation_configure(ThugAnimationController *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_bone_animation_command(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
extern const ThugAnimationControllerMethods thug_standard_animation_methods;
extern uint32_t thug_standard_animation_pool_index,thug_animation_channel_pool_index;
extern ThugFixedPool *thug_standard_animation_pools[2],*thug_animation_channel_pools[2];
extern ThugObjectLookupManager *thug_animation_objects;
ThugAnimationController *thug_standard_animation_initialize(ThugAnimationController *,ThugAnimationChannel *,const ThugDiagnostics *,const ThugMemory *);
void thug_standard_animation_destroy(ThugAnimationController *,const ThugMemory *);
void *thug_standard_animation_allocate(uint32_t,uint32_t,const ThugMemory *);
void thug_standard_animation_free(ThugAnimationController *,const ThugMemory *);
ThugAnimationController *thug_standard_animation_delete(ThugAnimationController *,uint32_t,const ThugMemory *);
uint32_t thug_standard_animation_command(ThugAnimationController *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
ThugAnimationController *thug_animation_create_controller(ThugAnimationChannel *,const ThugScriptStructure *,const ThugDiagnostics *,const ThugMemory *);
void thug_animation_clear_controllers(ThugAnimationChannel *,const ThugMemory *);
void thug_animation_channel_destroy(ThugAnimationChannel *,const ThugMemory *);
void thug_animation_channel_free(ThugAnimationChannel *,const ThugMemory *);
ThugAnimationChannel *thug_animation_channel_delete(ThugAnimationChannel *,uint32_t,const ThugMemory *);
uint32_t thug_animation_channel_command(ThugAnimationChannel *,uint32_t,const ThugScriptStructure *,void *,const ThugDiagnostics *,const ThugMemory *);
void thug_animation_channel_update(ThugAnimationChannel *,const ThugDiagnostics *,const ThugMemory *);
void thug_standard_animation_update(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
void thug_timed_animation_update(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
double thug_balance_animation_position(ThugAnimationController *);
void thug_balance_animation_update(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
void thug_bone_animation_update(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
void thug_animation_controller_idle(ThugAnimationController *,const ThugDiagnostics *,const ThugMemory *);
#endif
