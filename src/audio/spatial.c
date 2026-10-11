#include "sound.h"
#include "../core/vector.h"
#include "../platform/math.h"
#define R24 thug_platform_round_x87_single
_Static_assert(sizeof(ThugSpatialSoundVolume) == 44, "Spatial volume layout");
uint8_t thug_sound_suppressed_a, thug_sound_suppressed_b;
/* 0x0047b080. Keep the signed value of the first largest magnitude channel.
 * Equal magnitudes and unordered comparisons do not replace it. */
double thug_sound_volume_peak(const ThugSoundVolume *volume) {
    double peak = volume->channels[0];
    unsigned count = volume->format == 2 ? 5 : 2;
    for (unsigned i = 1; i < count; ++i) if (__builtin_fabs(peak) < __builtin_fabs((double)volume->channels[i])) peak = volume->channels[i];
    return peak;
}
/* 0x0047be10. Complete listener selection, distance attenuation and stereo
 * panning. Playback and Windows device operations are separate routines.
 * Suppressed/absent-listener/range exits preserve the original unwritten bytes. */
uint8_t thug_sound_spatialize(const ThugSoundConfiguration *configuration, ThugSpatialSoundVolume *out, const float position[4], float range, uint32_t curve, const ThugCamera *camera, const float *range_origin) {
    if (thug_sound_disabled()) return 1;
    for (unsigned i = 0; i < 5; ++i) out->volume.channels[i] = 0;
    if (!(configuration->unknown_0 & 255) && (thug_sound_suppressed_a || thug_sound_suppressed_b)) return 1;
    if (!camera) { camera = thug_camera_nearest(position, 0); if (!camera) return 1; }
    const float *p = thug_camera_position(camera);
    double x = R24((double)p[0] - position[0]), y = R24((double)p[1] - position[1]), z = R24((double)p[2] - position[2]);
    float distance = (float)R24(__builtin_sqrt(R24(R24(R24(z*z) + R24(y*y)) + R24(x*x))));
    if (range_origin) range = (float)R24(thug_vector_distance(range_origin, thug_camera_position(camera)) + distance);
    else if (range == 0) range = thug_sound_default_distance;
    if (distance >= range) return !(R24((double)distance * (double)1.05f) > range);
    float ratio = (float)R24((double)distance / range), amplitude = 0;
    double remaining = R24(1 - (double)ratio), value;
    switch (curve) {
        case 0:
            value = R24(R24(R24(remaining * 3) + R24(1 - R24((double)ratio * ratio))) * .25);
            amplitude = (float)R24(value * 100); break;
        case 1: amplitude = (float)R24(remaining * 100); break;
        case 2: amplitude = (float)R24(R24(remaining * remaining) * 100); break;
        case 3: amplitude = (float)R24(R24(__builtin_sqrt(remaining)) * 100); break;
        default: break;
    }
    out->volume.format = 3;
    if (__builtin_fabs(thug_sound_volume_peak(&out->volume)) < __builtin_fabs((double)amplitude)) {
        float direction[4], axis[4];
        thug_vector_difference(direction, position, thug_camera_position(camera));
        thug_vector_normalize(direction);
        thug_vector_negated(axis, thug_camera_orientation(camera));
        double mix = R24(R24(thug_vector_dot(axis, direction) + 1) * .5);
        float right = (float)R24(R24(1 - R24(mix * mix)) * amplitude);
        double opposite = R24(1 - mix);
        double left = R24(R24(1 - R24(opposite * opposite)) * amplitude);
        uint32_t format = out->volume.format;
        uint8_t changed = 0;
        if (left > out->volume.channels[0]) { out->volume.channels[0] = (float)left; changed = 1; }
        if (right > out->volume.channels[1]) { out->volume.channels[1] = right; changed = 1; }
        if (format == 1 && changed) {
            thug_vector_negated(axis, thug_camera_orientation(camera) + 8);
            if (thug_vector_dot(axis, direction) < 0) out->volume.channels[0] = (float)R24(-(double)out->volume.channels[0]);
        }
    }
    out->distance = range;
    thug_vector_copy(out->position, position);
    return 1;
}
