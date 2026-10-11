import {verifyScriptState} from './script_state_wasm_checks.mjs';
export async function verifyPhysicsStateActionsContext(wasm,fixture,load){
const empty=await verifyScriptState(wasm,fixture,load);
const nested=await verifyScriptState(wasm,{...fixture,scoped_event_services:{...fixture.scoped_event_services,pointer:fixture.outer_scope}},load);
const result={result:'pass',original_cases:empty.cases,cases:empty.cases+nested.cases,calls:empty.calls+nested.calls,native_qb_callbacks:empty.native_qb_callbacks+nested.native_qb_callbacks,nan_fields_classification_only:empty.nan_fields_classification_only+nested.nan_fields_classification_only,null_scope:empty,outer_scope:nested};
return result;
}
