/* Native matching trial. Recovered behavior remains in src/core; this file
 * restores 32-bit MSVC types and member calling conventions. No assembly. */
typedef unsigned int u32;
typedef signed int s32;
extern const u32 crc_table[256];

extern "C" u32 crc_buffer(const unsigned char *bytes, s32 length) {
    if (!bytes || length <= 0) return 0;
    u32 crc = ~0u;
    for (s32 i = 0; i < length; ++i)
        crc = (crc >> 8) ^ crc_table[(bytes[i] ^ crc) & 255];
    return crc;
}
extern "C" u32 crc_extend(const unsigned char *bytes, s32 length, u32 crc) {
    for (s32 i = 0; i < length; ++i)
        crc = (crc >> 8) ^ crc_table[(bytes[i] ^ crc) & 255];
    return crc;
}
extern "C" u32 crc_normalized(const char *bytes, s32 length) {
    if (!bytes || length <= 0) return 0;
    u32 crc = ~0u;
    for (s32 i = 0; i < length; ++i) {
        char c = bytes[i];
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}
extern "C" u32 crc_string(const char *text) {
    if (!text) return 0;
    u32 crc = ~0u;
    char c;
    while ((c = *text++) != 0) {
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}
extern "C" u32 crc_extend_string(u32 crc, const char *text) {
    if (!text) return crc;
    char c;
    while ((c = *text++) != 0) {
        if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
        if (c == '/') c = '\\';
        crc = (crc >> 8) ^ crc_table[(c ^ crc) & 255];
    }
    return crc;
}

struct Vector {
    float x, y, z, w;
    Vector &copy(const Vector &source);
    Vector &add(const Vector &source);
    Vector &subtract(const Vector &source);
    Vector &scale(float factor);
    float length_squared() const;
};
Vector &Vector::copy(const Vector &source) {
    x = source.x; y = source.y; z = source.z; w = source.w;
    return *this;
}
Vector &Vector::add(const Vector &source) {
    x += source.x; y += source.y; z += source.z; w += source.w;
    return *this;
}
Vector &Vector::subtract(const Vector &source) {
    x -= source.x; y -= source.y; z -= source.z; w -= source.w;
    return *this;
}
Vector &Vector::scale(float factor) {
    x *= factor; y *= factor; z *= factor; w *= factor;
    return *this;
}
float Vector::length_squared() const { return x*x + y*y + z*z; }
