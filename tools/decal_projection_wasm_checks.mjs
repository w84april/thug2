import {verifyScriptState} from './script_state_wasm_checks.mjs';
export async function verifyDecalProjection(wasm,fixture,load) {
  const lifecycle=await verifyScriptState(wasm,fixture.lifecycle,load);
  const projection=await verifyScriptState(wasm,fixture.projection,load);
  return {result:'pass',cases:lifecycle.cases+projection.cases,calls:lifecycle.calls+projection.calls,
    functions:lifecycle.functions+projection.functions,counts:{...lifecycle.counts,...projection.counts},lifecycle,projection};
}
