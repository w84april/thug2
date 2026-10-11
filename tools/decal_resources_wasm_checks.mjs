import {verifyScriptState} from './script_state_wasm_checks.mjs';
export async function verifyDecalResources(wasm,fixture,load) {
  {
    const {instance:{exports:e}}=await WebAssembly.instantiate(wasm),v=new DataView(e.memory.buffer);
    for(const [slot,implementation] of [['thug_d3dx_normalize3','thug_d3dx_normalize3_sse'],
      ['thug_d3dx_transform_coordinate','thug_d3dx_transform_coordinate_sse']]) {
      if(e.__indirect_function_table.get(v.getUint32(e[slot].value,true))!==e[implementation])
        throw new Error('D3DX startup dispatch '+slot);
    }
    if(v.getUint32(e.thug_crt_random_state.value,true)!==1)throw new Error('Port CRT startup seed');
  }
  const math=await verifyScriptState(wasm,fixture.math,load);
  const resources=await verifyScriptState(wasm,fixture.resources,load);
  const counts={...math.counts,...resources.counts};
  return {result:'pass',cases:math.cases+resources.cases,calls:math.calls+resources.calls,
    functions:Object.keys(counts).length,counts,nan_fields_classification_only:math.nan_fields_classification_only+resources.nan_fields_classification_only,
    startup_dispatch:'selected SSE backends',math,resources};
}
