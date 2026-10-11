#ifndef THUG_GAME_SKATER_H
#define THUG_GAME_SKATER_H
#include "../collision/probe.h"
#include "../script/params.h"
#include "../platform/diagnostics.h"
#include "../core/matrix.h"
extern const void *thug_input_manager;
uint32_t thug_input_device_id(const void *, uint32_t);

/* Recovered prefixes. Unknown fields retain their original byte positions. */
typedef struct ThugObjectComponent {
    uint32_t unknown_0, type, unknown_8;
    void *owner;
    struct ThugObjectComponent *next;
} ThugObjectComponent;
typedef struct { uint32_t type, factory; } ThugComponentTypeEntry;
typedef struct {
    uint8_t unknown_0_to_43[0x44];
    uint32_t count;
    ThugComponentTypeEntry entries[];
} ThugComponentTypeRegistry;
extern ThugComponentTypeRegistry *thug_component_type_registry;
extern void *thug_component_type_heads[128];
void *thug_component_type_head(const ThugComponentTypeRegistry *, uint32_t);
typedef struct {
    uint8_t unknown_0_to_13[0x14];
    uint32_t object_id;
    uint8_t unknown_18_to_4b[0x34];
    float position[4], previous_position[4], orientation[16], velocity[4];
    uint8_t parameter_sets_enabled;
    uint8_t unknown_bd_to_bf[3];
    float orientation_c0[16];
    ThugObjectComponent *components;
    uint8_t unknown_104_to_10f[12], stat_modifier_selector;
    uint8_t unknown_111_to_277[0x167];
    struct ThugStatModifierOwner *modifier_owner;
    uint32_t unknown_27c;
    struct ThugSkaterPhysics *physics;
    uint8_t unknown_284_to_28f[12];
    float values[];
} ThugSkaterBody;
typedef struct {
    float matrix[16];
    struct ThugRailNode *rail_nodes;
    uint32_t unknown_44;
    int32_t rail_count;
    uint32_t unknown_4c;
    uint8_t changed;
} ThugObjectTransform;
typedef struct {
    ThugObjectComponent base;
    uint32_t unknown_14;
    ThugObjectTransform *transform;
} ThugTransformComponent;
float *thug_transform_set(ThugObjectTransform *, const float source[16]);
float *thug_component_world_transform(ThugTransformComponent *, float out[16]);
typedef struct {
    ThugObjectComponent base;
    uint32_t unknown_14, mode, unknown_1c;
    uint8_t drag_coefficient_selector;
    uint8_t unknown_21_to_23[3];
    uint32_t drag_selector_time;
    uint8_t stat_modifier_selector;
    uint8_t unknown_29_to_2b[3];
    uint32_t stat_modifier_time;
    uint8_t ground_transition_flag, unknown_31_to_33[3];
    uint32_t ground_transition_time;
    uint8_t transition_flag_38, unknown_39_to_3b[3];
    uint32_t transition_time_3c;
    uint8_t surface_flag_8, unknown_41_to_43[3];
    uint32_t surface_flag_time;
    uint8_t transition_flag_48, unknown_49_to_4b[3];
    uint32_t transition_time_4c;
    uint8_t rail_separated, unknown_51_to_53[3];
    uint32_t rail_separated_time;
    uint8_t state_flag_58, unknown_59_to_5b[3];
    uint32_t state_time_5c;
    uint8_t unknown_60_to_67[8];
    uint8_t transition_flag_68, unknown_69_to_6b[3];
    uint32_t transition_time_6c;
    uint8_t resistance_requested, unknown_71_to_77[7];
    uint8_t skip_ground_probe, unknown_79_to_7b[3];
    uint32_t skip_ground_probe_time;
    uint8_t ground_contact_flag, unknown_81_to_83[3];
    uint32_t ground_contact_time;
    uint8_t moving_contact_locked, unknown_89_to_97[15], landing_flag_98, unknown_99_to_9b[3];
    uint32_t landing_time_9c;
    uint8_t wallplant_flag_a0, unknown_a1_to_a3[3];
    uint32_t wallplant_time_a4;
    uint8_t transfer_flag_a8, unknown_a9_to_ab[3];
    uint32_t transfer_time_ac;
    uint8_t transfer_flag_b0, unknown_b1_to_b3[3];
    uint32_t transfer_time_b4;
    uint8_t rebound_cancel_requested, unknown_b9_to_bb[3];
    uint32_t rebound_cancel_time;
    uint8_t state_flag_c0, unknown_c1_to_c3[3];
    uint32_t state_time_c4;
    uint8_t rail_node_changed, unknown_c9_to_cb[3];
    uint32_t rail_node_changed_time;
    uint8_t state_flag_d0, unknown_d1_to_d3[3];
    uint32_t state_time_d4;
    uint8_t state_flag_d8, unknown_d9_to_db[3];
    uint32_t state_time_dc;
    uint8_t unknown_e0, material;
    uint8_t unknown_e2_to_e3[2];
    float transfer_velocity[4];
    uint8_t unknown_f4_to_11b[0x28];
    float wallplant_height;
} ThugSkaterState;
void thug_skater_state_set_mode(ThugSkaterState *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_state_set_material(ThugSkaterState *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
typedef struct {
    uint8_t unknown_0_to_b[12];
    ThugSkaterBody *body;
    uint8_t unknown_10_to_17[8];
    struct ThugMovingContact *contact;
    float relative_position[4];
    uint8_t unknown_2c_to_6b[0x40];
    ThugReferencedObject *released_owner;
    uint32_t release_time;
} ThugSkaterGroundGate;
typedef struct {
    uint8_t unknown[0x1c];
    uint32_t mode;
    uint8_t unknown_20_to_117[0xf8], alternate;
} ThugSkaterMovementMode;
typedef struct {
    uint8_t unknown[0x24], wallplant_blocked, unknown_25, wall_response_suppressed, unknown_27_to_2b[5];
    ThugSkaterMovementMode *movement_mode;
} ThugSkaterWallGate;
typedef struct {
    ThugObjectComponent base;
    uint32_t unknown_14, mode;
    uint8_t unknown_1c_to_47[0x2c];
    float direction[4];
    uint8_t unknown_58_to_1867[0x1810];
    float speed_factor;
} ThugSkaterTransferMotion;
typedef struct {
    float position[4], normal[4], original_height;
    uint8_t moving, untouched[3];
} ThugSkaterTransferResult;
/* Button meanings are not yet established; keep their observed offsets. */
typedef struct {
    uint8_t pressed, unknown_1_to_3[3];
    uint32_t timestamp;
    uint32_t timestamp_8, unknown_c;
    uint8_t pending_10, unknown_11_to_13[3];
    uint32_t pending_14;
} ThugInputButton;
typedef struct {
    uint8_t unknown_0_to_1f[0x20];
    ThugInputButton button_20;
    uint8_t unknown_38_to_3f[8];
    ThugInputButton button_40;
    uint8_t unknown_58_to_5f[8];
    ThugInputButton button_60;
    uint8_t unknown_78_to_7f[8];
    ThugInputButton button_80;
    uint8_t unknown_98_to_9f[8];
    ThugInputButton button_a0;
    uint8_t unknown_b8_to_bf[8];
    ThugInputButton button_c0;
    uint8_t unknown_d8_to_df[8];
    ThugInputButton button_e0;
    uint8_t unknown_f8_to_ff[8];
    ThugInputButton button_100;
    uint8_t unknown_118_to_11f[8];
    ThugInputButton button_120;
    uint8_t unknown_138_to_15f[0x28];
    ThugInputButton button_160;
    uint8_t unknown_178_to_17f[8];
    ThugInputButton button_180;
    uint8_t unknown_198_to_19f[8];
    ThugInputButton button_1a0;
    uint8_t unknown_1b8_to_1bf[8];
    ThugInputButton button_1c0;
    uint8_t unknown_1d8_to_1ff[0x28];
} ThugSkaterInput;
ThugInputButton *thug_input_find_button(ThugSkaterInput *, uint32_t name);
uint32_t thug_input_button_elapsed(const ThugInputButton *);
uint32_t thug_input_button_elapsed_8(const ThugInputButton *);
void thug_input_button_clear_pending(ThugInputButton *);
void thug_input_button_clear_latch(ThugInputButton *);
typedef struct {
    uint32_t time, type, key, unknown_c;
    uint8_t consumed, unknown_11_to_13[3];
    uint32_t mask;
} ThugInputHistoryEntry;
typedef struct {
    uint8_t unknown_0_to_497[0x498], blocked_498, blocked_499;
} ThugInputTriggerGate;
typedef struct {
    uint8_t unknown_0_to_2e7[0x2e8];
    float window_scale;
} ThugInputTriggerScale;
typedef struct {
    uint8_t unknown_0_to_1f[0x20];
    const ThugInputTriggerGate *trigger_gate;
    uint32_t unknown_24;
    const ThugInputTriggerScale *trigger_scale;
    uint8_t unknown_2c_to_37[12];
    ThugInputHistoryEntry history[100];
    uint16_t history_count, history_head;
    uint32_t matched_input[3];
    uint8_t unknown_9a8_to_9ff[0x58], button_state[22];
    uint8_t unknown_a16_to_1330[0x91b];
    char name[0x73];
    float spin_angle;
    uint8_t unknown_13a8_to_13af[8], notification_flag;
} ThugSkaterNameContext;
extern uint32_t thug_input_button_names[22];
uint32_t thug_input_button_index(uint32_t name);
uint8_t thug_skater_named_button(const ThugSkaterNameContext *, uint32_t name);
uint8_t thug_skater_consume_recent_input(ThugSkaterNameContext *, uint32_t name, uint32_t window, uint32_t mask);
void thug_skater_commit_input_marks(ThugSkaterNameContext *, uint32_t mask);
uint8_t thug_skater_match_rotation_input(ThugSkaterNameContext *, const uint32_t keys[3], uint32_t override);
uint8_t thug_skater_match_release_input(ThugSkaterNameContext *, uint32_t key, uint32_t alternate, uint32_t commit);
uint8_t thug_input_is_direction(uint32_t name);
void thug_skater_clear_input_marks(ThugSkaterNameContext *);
uint32_t thug_skater_read_trigger_arguments(const ThugSkaterNameContext *, const ThugScriptComponent *, int32_t count, uint32_t *output);
void thug_skater_set_matched_input(ThugSkaterNameContext *, const uint32_t keys[3]);
uint8_t thug_skater_match_two_inputs(ThugSkaterNameContext *, uint32_t first, uint32_t second, uint32_t window, uint32_t mask);
uint8_t thug_skater_match_trick_input(ThugSkaterNameContext *, const ThugScriptStructure *, uint32_t commit_mask, uint32_t ignore_mask, uint32_t scale_window);
typedef struct {
    uint32_t duration_bits, time, start_bits, delta_bits, mode;
    uint8_t flags, unknown_15_to_17[3];
} ThugAxisRotation;
typedef struct {
    ThugAxisRotation entries[6];
    uint8_t active, unknown_91_to_93[3];
} ThugAxisRotationQueue;
typedef struct {
    ThugObjectComponent base;
    uint8_t unknown_14_to_27[0x14];
    float pivot[4];
    ThugAxisRotationQueue axes[3];
} ThugRotationComponent;
void thug_rotation_queue_add(ThugAxisRotationQueue *, uint32_t duration_bits, uint32_t time,
    uint32_t start_bits, uint32_t delta_bits, uint32_t mode, uint32_t flag, uint32_t secondary);
void thug_rotation_schedule(ThugRotationComponent *, float duration, float start, float endpoint,
    uint32_t mode, uint32_t flag, uint32_t x, uint32_t y, uint32_t z,
    const ThugDiagnostics *, const ThugMemory *);
void thug_rotation_clear(ThugRotationComponent *, const ThugDiagnostics *, const ThugMemory *);
typedef struct { uint8_t unknown[0x18]; uint32_t identifier; } ThugSkaterModeContext;
typedef struct {
    uint8_t unknown_0_to_27[0x28], blocked_28, unknown_29_to_4f[0x27], blocked_50;
} ThugSkaterOrientationGate;
typedef struct ThugSkaterPhysics {
    uint8_t unknown_0_to_b[12];
    ThugSkaterBody *body;
    uint8_t unknown_10_to_17[8];
    float cached_orientation[16];
    float orientation_source[4], orientation_target[4], orientation_previous[4], orientation_blend;
    float time_step;
    uint32_t state_change_time, previous_state;
    float side_previous_position[4];
    ThugCollisionProbe surface_probe;
    ThugCollisionProbe saved_probe;
    float surface_segment[8];
    uint8_t surface_skatable, surface_flag_8, surface_flag_4;
    uint8_t unknown_22b;
    union { uint32_t ground_value_22c; struct ThugRailNode *rail_node; };
    ThugObjectTransform *rail_transform;
    uint32_t rail_reentry_time, rail_update_time, rail_retry_delay, rail_name;
    uint32_t ground_value_244;
    uint8_t unknown_248_to_249[2], attachment_moving, unknown_24b;
    int32_t attachment_index;
    float attachment_direction;
    uint8_t unknown_254, previous_skip_ground_probe, unknown_256_to_257[2];
    float state_saved_position[4];
    float transition_previous_position[4], transition_orientation[4], transition_forward[4], transition_height;
    uint8_t unknown_29c_to_2ab[0x10];
    float repulsion_direction[4], repulsion_fraction, repulsion_distance, repulsion_strength, repulsion_turn_rate;
    uint8_t unknown_2cc_to_2cf[4], ground_transition_flag, unknown_2d1_to_2d3[3];
    uint32_t nearby_obstacle_direction;
    uint8_t unknown_2d8, acceleration_requested, tap_turn_mode, rotation_input_used, rotation_half_turn;
    uint8_t unknown_2dd_to_2df[3];
    float rotation_duration;
    uint8_t ground_flag_2e4, unknown_2e5_to_2e7[3];
    float rotation_step;
    uint8_t airborne_flag_2ec;
    uint8_t parameter_mode_active, unknown_2ee_to_2ef[2];
    uint32_t parameter_mode;
    uint8_t projectile_enabled, unknown_2f5_to_2f7[3];
    int32_t projectile_count;
    uint8_t unknown_2fc_to_300[5], special_timer_active;
    uint8_t parameter_mode_fallback, alternate_acceleration, reverse_script_requested, unknown_305_to_307[3];
    uint32_t projectile_input_value;
    union { uint32_t state_value_30c; float tap_turn_remaining; };
    uint8_t acceleration_blocked, brake_input_enabled, unknown_312_to_313[2];
    float friction;
    uint32_t revert_count, revert_recovery_time;
    float airborne_friction_gate;
    uint8_t braking, unknown_325_to_327[3];
    uint32_t repulsion_times[4];
    uint8_t unknown_338_to_347[0x10];
    float heading;
    uint8_t unknown_34c_to_34f[4];
    float drag_override_active;
    float speed_soft_limit, speed_hard_limit;
    float drag_override;
    float ground_gravity_override;
    ThugObjectReference attachment_reference;
    uint8_t spin_input_blocked, unknown_371;
    uint8_t landed_from_transfer, landing_flag_373, landing_flag_374, unknown_375_to_377[3];
    uint32_t input_release_elapsed;
    float transfer_height;
    uint32_t state_enter_time, state_exit_time;
    uint8_t accelerate_along_velocity;
    uint8_t unknown_389_to_38b[3];
    float wall_transition_normal[4];
    uint32_t wall_transition_time, wall_transition_time_3a0;
    uint8_t rotation_requested, turn_positive, unknown_3a6_to_3ab[6];
    float transfer_speed_multiplier;
    float transfer_surface[16];
    ThugMatrixInterpolation transfer_interpolation;
    float transfer_progress, transfer_duration, transfer_direction[4], transfer_previous_orientation[16];
    uint32_t rebound_gate_time, last_rebound_time;
    uint8_t ground_flag_4e8, unknown_4e9_to_4eb[3];
    uint32_t transfer_gate_time;
    uint8_t vert_air_event_active, unknown_4f1_to_4f3[3];
    ThugCollisionCache collision_cache;
    uint8_t transfer_moving, focus_input_latched, unknown_14c2_to_14c3[2];
    uint32_t projectile_cooldown;
    uint8_t projectile_blocked, unknown_14c9_to_14cb[3];
    uint32_t wall_transition_value;
    float wallplant_saved_velocity[4], wallplant_saved_position[4], wallplant_saved_normal[4];
    uint8_t unknown_1500_to_150b[12];
    ThugSkaterInput *input;
    struct ThugCollisionEventComponent *collision_events;
    struct ThugSoundComponent *sound;
    ThugSkaterNameContext *name_context;
    ThugSkaterOrientationGate *orientation_gate;
    struct ThugBalanceScoreComponent *score_component;
    ThugSkaterModeContext *mode_context;
    ThugSkaterState *state;
    ThugSkaterGroundGate *ground_gate;
    ThugSkaterWallGate *wall_gate;
    ThugSkaterTransferMotion *transfer_motion;
    struct ThugWallContactMark *wall_mark;
} ThugSkaterPhysics;
void thug_skater_update_lip(ThugSkaterPhysics *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_skater_wall_overhang(ThugSkaterPhysics *,ThugCollisionQuery *);
void thug_skater_update_wallplant_state(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_airborne(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_build_collision_cache(ThugSkaterPhysics *);
void thug_skater_update_speed_limits(ThugSkaterPhysics *);
extern int32_t thug_transfer_speed_diagnostic_counter;
extern const char thug_transfer_speed_format[];
void thug_skater_update_transfer_speed(ThugSkaterPhysics *, const ThugDiagnostics *);
void thug_skater_update_revert_count(ThugSkaterPhysics *,const ThugDiagnostics *);
void thug_skater_update_focus_input(ThugSkaterPhysics *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_skater_check_projectile_input(ThugSkaterPhysics *);
uint32_t thug_skater_is_walking(const ThugSkaterWallGate *);
void thug_skater_update_projectile(ThugSkaterPhysics *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_rotation(ThugSkaterPhysics *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_special_timer(ThugSkaterPhysics *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_skater_try_vert_wallplant(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_skater_try_wallplant(ThugSkaterPhysics *, uint32_t late, uint32_t check_only, uint32_t forced,
    ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_set_material(ThugSkaterPhysics *, uint32_t, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_pitch_input(ThugSkaterPhysics *);
void thug_skater_spin_input(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_transfer_orientation(ThugSkaterPhysics *);
void thug_skater_upright_orientation(ThugSkaterPhysics *);
uint8_t thug_skater_try_raised_path(ThugSkaterPhysics *, const float previous[4], ThugCollisionQuery *);
void thug_skater_check_rotation_input(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_skater_resolve_overhead(ThugSkaterPhysics *, ThugCollisionQuery *);
uint8_t thug_skater_resolve_air_wall(ThugSkaterPhysics *, const float previous[4],
    ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);

typedef struct {
    uint8_t unknown_0_to_3f[0x40];
    uint32_t identifier;
} ThugSkaterOrientationContext;
/* Original global 0x007ce5d8. Only the field used by 0x004fe860 is recovered. */
extern const ThugSkaterOrientationContext *thug_skater_orientation_context;

void thug_skater_apply_quadratic_drag(ThugSkaterPhysics *, float coefficient);
ThugObjectComponent *thug_object_find_component(const ThugSkaterBody *, uint32_t type);
/* Enabled objects must have their core-physics component; selected structures
 * must be loaded before requesting a numeric parameter, as in the original. */
ThugScriptStructure *thug_skater_parameter_set(const ThugSkaterBody *);
double thug_skater_get_parameter(uint32_t name, uint32_t assert_missing, const ThugSkaterBody *);
uint32_t thug_skater_get_integer_parameter(uint32_t name, uint32_t assert_missing, const ThugSkaterBody *);
void thug_skater_apply_drag(ThugSkaterPhysics *);
void thug_skater_change_state(ThugSkaterPhysics *, uint32_t mode, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_save_surface(ThugSkaterPhysics *, const ThugCollisionProbe *);
uint8_t thug_skater_try_wall_transition(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_skater_correct_side(ThugSkaterPhysics *, float direction, float distance, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_correct_sides(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_apply_friction(ThugSkaterPhysics *);
uint8_t thug_skater_should_brake(const ThugSkaterPhysics *);
uint8_t thug_skater_braking_inhibited(const ThugSkaterPhysics *);
uint8_t thug_skater_can_accelerate(const ThugSkaterPhysics *);
void thug_skater_accelerate(ThugSkaterPhysics *);
void thug_skater_brake(ThugSkaterPhysics *);
void thug_skater_align_velocity(const ThugSkaterPhysics *, float velocity[4]);
double thug_skater_gravity(const ThugSkaterPhysics *);
double thug_skater_transfer_speed(const ThugSkaterTransferMotion *);
extern float thug_skater_transfer_velocity[4];
void thug_skater_apply_transfer(ThugSkaterPhysics *, const ThugSkaterTransferResult *,
    const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_skater_find_alternate_transfer(ThugSkaterPhysics *, const float direction[4], const float normal[4],
    uint8_t *opposed, float point[4], float contact_normal[4], uint8_t *moving, ThugCollisionQuery *);
uint8_t thug_skater_try_alternate_transfer(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_leave_transition(ThugSkaterPhysics *, uint8_t force, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_handle_floor(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_skater_find_transfer(ThugSkaterPhysics *, uint8_t force_vertical,
    const float from[4], const float scan_origin[4], float velocity[4],
    ThugSkaterTransferResult *, ThugCollisionQuery *);
uint8_t thug_skater_slope_turn(ThugSkaterPhysics *);
void thug_skater_apply_resistance(ThugSkaterPhysics *);
/* Direction index must be 0..3, as supplied by the four-way caller. */
void thug_skater_repulsion_probe(ThugSkaterPhysics *, const float start[4], const float end[4], uint32_t direction,
    ThugCollisionQuery *);
void thug_skater_apply_repulsion(ThugSkaterPhysics *, ThugCollisionQuery *);
void thug_skater_correct_low_speed_collision(ThugSkaterPhysics *, ThugCollisionQuery *);
double thug_skater_wall_turn(ThugSkaterPhysics *, const float normal[4], float *turn, float fraction);
uint8_t thug_skater_try_rebound(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_wall_response(ThugSkaterPhysics *, const float normal[4], ThugCollisionQuery *,
    const ThugDiagnostics *, const ThugMemory *);
void thug_skater_movement_sweep(ThugSkaterPhysics *, ThugCollisionQuery *,
    const ThugDiagnostics *, const ThugMemory *);
void thug_skater_ground_update(ThugSkaterPhysics *, ThugCollisionQuery *);
void thug_skater_update_grounded(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_set_up_vector(ThugSkaterPhysics *, float x, float y, float z, float w,
    ThugCollisionQuery *);
void thug_skater_blend_orientation(ThugSkaterPhysics *);
extern const char thug_skater_tracking_format[];
void thug_skater_track_movement(uint32_t type, const float from[4], const float to[4], const ThugDiagnostics *);
void thug_skater_prepare_floor_transition(ThugSkaterPhysics *, ThugCollisionQuery *, const ThugDiagnostics *);
void thug_skater_steer(ThugSkaterPhysics *);
void thug_skater_handle_backward_motion(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_skater_handle_input_release(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_nearby_obstacle(ThugSkaterPhysics *, ThugCollisionQuery *);
uint8_t thug_skater_forward_obstruction(ThugSkaterPhysics *, const ThugScriptStructure *,
    uint32_t unused, ThugCollisionQuery *);
uint8_t thug_skater_query_surface(ThugSkaterPhysics *, uint16_t excluded, uint16_t required,
    ThugCollisionQuery *);
/* Extracted suffix of 0x005003a0 for numeric verification, not a separate original function. */
void thug_skater_classify_surface(ThugSkaterPhysics *);
void thug_skater_update_wallride(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_movement(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_initialize_physics(ThugSkaterPhysics *,const ThugScriptStructure *);
void thug_skater_link_physics(ThugSkaterPhysics *);
void thug_shadow_set_position(void *,const float[4]);
void thug_shadow_set_up(void *,const float[4]);
void *thug_skater_camera_object(const ThugSkaterBody *);
#endif
