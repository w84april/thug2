#include "skater.h"
#include "../core/vector.h"
#include "../platform/math.h"
#define R24 thug_platform_round_x87_single

/* 0x00503b30. At low speed, probe along the requested side axis. A hit
 * proposes a correction along its normal; a second probe must clear that move.
 * The speed comparison admits unordered values, as TEST AH,5 / JNP does. */
void thug_skater_correct_low_speed_collision(ThugSkaterPhysics *p, ThugCollisionQuery *query) {
    const float *velocity = p->body->velocity;
    double sum = R24(R24((double)velocity[0]*velocity[0]) + R24((double)velocity[1]*velocity[1]));
    float speed = (float)R24(__builtin_sqrt(R24(sum + R24((double)velocity[2]*velocity[2]))));
    if (thug_script_get_global_number(0xbc33d268,1) < speed) return;
    const ThugSkaterInput *input = p->input;
    const ThugInputButton *button;
    if (input->button_60.pressed) button = &input->button_60;
    else if (input->button_80.pressed) button = &input->button_80;
    else return;
    uint32_t elapsed = thug_input_button_elapsed(button);
    double milliseconds = (int32_t)elapsed;
    if ((int32_t)elapsed < 0) milliseconds = R24(milliseconds + 0x1p32);
    float duration = (float)thug_platform_multiply_x87_single(milliseconds,0.001f);
    float limit = (float)thug_script_get_global_number(0x435f0653,1);
    if (duration > limit) duration = limit;
    if (input->button_80.pressed) duration = -duration;
    double distance = thug_script_get_global_number(0x4b8bab12,1);
    float side_step = (float)thug_platform_multiply_x87_single(distance,R24((double)duration/limit));
    const ThugSkaterBody *source = p->body;
    double height = thug_script_get_global_number(0xbfbbd0af,1);
    float lifted[3];
    for (unsigned i = 0; i < 3; ++i) lifted[i] = (float)thug_platform_multiply_x87_single(height,source->orientation[i+4]);
    double lifted_w = thug_platform_multiply_x87_single(height,source->orientation[7]);
    for (unsigned i = 0; i < 3; ++i) p->surface_segment[i] = lifted[i] + p->body->position[i];
    p->surface_segment[3] = (float)R24(lifted_w + p->body->position[3]);
    const float *side = p->body->orientation;
    double delta_x = R24((double)side_step*side[0]);
    float delta[3];
    for (unsigned i = 0; i < 3; ++i) delta[i] = (float)R24((double)side_step*side[i+1]);
    p->surface_segment[4] = (float)R24(delta_x+p->surface_segment[0]);
    for (unsigned i = 1; i < 4; ++i) p->surface_segment[i+4] = delta[i-1]+p->surface_segment[i];
    if (!thug_skater_query_surface(p,0x10,0,query)) return;
    float correction[4], normal[4];
    for (unsigned i = 0; i < 4; ++i) {
        correction[i] = p->surface_probe.point[i]-p->surface_segment[i+4];
        normal[i] = p->surface_probe.normal[i];
    }
    thug_vector_project_axis(correction,normal);
    ThugSkaterBody *body = p->body;
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i] = body->position[i]+body->orientation[i+4];
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i+4] = correction[i]+p->surface_segment[i];
    if (!thug_skater_query_surface(p,0x10,0,query)) {
        body = p->body;
        for (unsigned i = 0; i < 4; ++i) body->position[i] = p->surface_segment[i+4]-body->orientation[i+4];
    }
}
