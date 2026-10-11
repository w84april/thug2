#ifndef THUG_GAME_ATTACHMENT_H
#define THUG_GAME_ATTACHMENT_H
#include "skater.h"
typedef struct ThugAttachmentPoint {
    float position[4];
    struct ThugAttachmentPoint *next;
} ThugAttachmentPoint;
typedef struct {
    ThugAttachmentPoint *head;
    uint8_t transformed, unknown_5_to_7[3];
    float transform[16];
} ThugAttachmentPoints;
typedef struct ThugAttachmentProvider ThugAttachmentProvider;
typedef struct {
    uint32_t unknown[13];
    ThugAttachmentPoints *(*points)(ThugAttachmentProvider *);
} ThugAttachmentProviderMethods;
struct ThugAttachmentProvider {
    const ThugAttachmentProviderMethods *methods;
    uint8_t unknown_4_to_17[0x14];
    ThugAttachmentPoints *points;
};
typedef struct ThugAttachmentComponent {
    ThugObjectComponent base;
    struct ThugAttachmentComponent *next_of_type;
    uint8_t enabled, unknown_19_to_1b[3];
    ThugAttachmentProvider *provider;
} ThugAttachmentComponent;
extern const ThugAttachmentProviderMethods thug_attachment_provider_methods;
ThugAttachmentPoints *thug_attachment_provider_points(ThugAttachmentProvider *);
void thug_attachment_set_transform(ThugAttachmentPoints *, const float matrix[16]);
void thug_attachment_point_position(const ThugAttachmentPoints *, float out[4], const float point[4]);
int32_t thug_attachment_nearest(ThugAttachmentComponent *, float out[4], const float target[4]);
/* A valid provider with a missing index returns one and leaves out untouched. */
uint8_t thug_attachment_indexed(ThugAttachmentComponent *, float out[4], int32_t index);
/* Active contacts must provide their attachment component and a valid selected
 * point when movement is enabled, as required by the original caller. */
void thug_skater_update_attachment(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
void thug_skater_find_attachment(ThugSkaterPhysics *, const ThugDiagnostics *, const ThugMemory *);
#endif
