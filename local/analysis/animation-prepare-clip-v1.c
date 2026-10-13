/* Unverified original Animation startup parameter preparation. */
#include "../../src/game/animation_controllers.h"
#include "../../src/game/ui.h"
#include "../../src/script/params.h"
#include "../../src/script/values.h"
extern void thug_ui_object_merge_parameters_v1(ThugUiObjectBase *,const ThugScriptStructure *,const ThugMemory *);
static ThugScriptStructure *temporary(const ThugMemory *m){
    ThugScriptStructure *s=thug_script_structure_allocate(8,m);
    return s?thug_script_structure_initialize(s):0;
}
/* 0047f000. Required temporary allocation, valid owner and stable pools. */
void thug_animation_state_prepare_clip_v1(ThugAnimationState *state,uint32_t name,const ThugMemory *m){
    ThugScriptStructure *definitions=thug_script_get_global_structure(0x95807202,1),*source=0;
    if(definitions&&thug_script_get_structure(definitions,name,&source,0)){
        ThugScriptStructure *outer=temporary(m),*copy=temporary(m);
        thug_script_structure_merge_optional(copy,source,m);
        thug_script_set_structure(outer,0x5db4115f,copy,m);
        thug_ui_object_merge_parameters_v1((ThugUiObjectBase *)state->body,outer,m);
        if(outer){thug_script_structure_destroy(outer,m);thug_script_structure_free(outer,m);}
    }
}
