#include "profile.h"
#include <stddef.h>
_Static_assert(offsetof(ThugProfile, parameters) == 0x5c, "Profile parameter structure");
_Static_assert(offsetof(ThugProfileManager, selected) == 0x1c, "Selected profile");
ThugProfileManager *thug_profile_manager;
static uint32_t word(const void *p) { uint32_t v; __builtin_memcpy(&v,p,4); return v; }
/* 0x0057b640 and0x0057b630. Indexing uses original wrapping word offsets. */
ThugProfile *thug_profile_at(const ThugProfileManager *m, uint32_t index) {
    return (ThugProfile *)(uintptr_t)word((const void *)((uintptr_t)m + 0x14 + index*4));
}
ThugProfile *thug_profile_current(const ThugProfileManager *m) { return thug_profile_at(m,m->selected); }
/* 0x00564fc0. The game receiver is unused; the profile manager is global. */
ThugProfile *thug_game_profile_at(const ThugGameContext *game, uint32_t index) {
    (void)game; return thug_profile_at(thug_profile_manager,index);
}
/* 0x00564f80. This pointer is unused; the selected profile manager is global. */
ThugProfile *thug_game_profile(const ThugGameContext *game, const ThugScriptStructure *parameters) {
    (void)game;
    uint32_t index;
    if (parameters && thug_script_get_integer(parameters,0x5b8ab877,&index,0))
        return thug_profile_at(thug_profile_manager,index);
    return thug_profile_current(thug_profile_manager);
}
/* 0x00586110. A missing result retains the incoming name as a pointer word. */
ThugScriptStructure *thug_profile_parameters(const ThugProfile *profile, uint32_t name) {
    ThugScriptStructure *result = (ThugScriptStructure *)(uintptr_t)name;
    thug_script_get_structure(&profile->parameters,name,&result,1); return result;
}
/* 0x005860a0. PUSH ECX seeds the optional output with the original this word. */
uint32_t thug_profile_binding_count(const ThugProfile *profile) {
    uint32_t count = (uint32_t)(uintptr_t)profile;
    thug_script_get_boolean(&profile->parameters,0xac9b9eda,&count,1); return count;
}
/* 0x00587100. Both checksum words and all padding remain untouched. */
ThugProfileBinding *thug_profile_binding_initialize(ThugProfileBinding *binding) { binding->special = 0; return binding; }
/* 0x00586630. Disabled diagnostics do not change the unchecked array access. */
void thug_profile_binding(const ThugProfile *profile, ThugProfileBinding *out, int32_t index) {
    ThugProfileBinding binding;
    thug_profile_binding_initialize(&binding);
    ThugScriptStructure *structure;
    ThugScriptArray *array;
    thug_script_get_structure(&profile->parameters,0xddbee809,&structure,1);
    thug_script_get_array_legacy(structure,0,&array,1);
    ThugScriptStructure *entry = thug_script_array_structure(array,index);
    thug_script_get_checksum_legacy(entry,0x5b077ce1,&binding.trick,1);
    thug_script_get_checksum_legacy(entry,0xa92a2280,&binding.combo,1);
    uint32_t special = 0;
    thug_script_get_boolean(entry,0xb56a8816,&special,0);
    if (special) binding.special = 1;
    binding.padding[0] = binding.padding[1] = binding.padding[2] = 0;
    *out = binding;
}
