#ifndef THUG_PLATFORM_DIAGNOSTICS_H
#define THUG_PLATFORM_DIAGNOSTICS_H
/* New platform boundary for the original formatted debug-output service.
 * Formatting and OS output are supplied by the host; callers retain their
 * original format strings, argument values and call order. */
typedef struct {
    void *context;
    void (*print)(void *context, const char *format, ...);
} ThugDiagnostics;
#endif
